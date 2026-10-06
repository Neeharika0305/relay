import time

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Backend as ORMBackend
from app.models import Route
from app.models import RoutingRule
from app.router.rules import Backend as RoutingBackend
from app.router.routing_engine import RoutingEngine
from reliability.circuit_breaker import CircuitBreaker


router = APIRouter(
    prefix="/v1/proxy",
    tags=["Proxy"],
)

REQUEST_TIMEOUT = 5.0

CIRCUIT_FAILURE_THRESHOLD = 3
CIRCUIT_RECOVERY_TIMEOUT = 10.0

routing_engine = RoutingEngine()

runtime_active_connections: dict[int, int] = {}
runtime_latency_ms: dict[int, float] = {}

circuit_breakers: dict[int, CircuitBreaker] = {}


def get_circuit_breaker(backend_id: int) -> CircuitBreaker:
    breaker = circuit_breakers.get(backend_id)

    if breaker is None:
        breaker = CircuitBreaker(
            failure_threshold=CIRCUIT_FAILURE_THRESHOLD,
            recovery_timeout=CIRCUIT_RECOVERY_TIMEOUT,
        )
        circuit_breakers[backend_id] = breaker

    return breaker


def get_strategy(route: Route, db: Session) -> str:
    rule = (
        db.query(RoutingRule)
        .filter(RoutingRule.route_id == route.id)
        .order_by(RoutingRule.priority.asc())
        .first()
    )

    if rule is None:
        return "weighted"

    strategy = rule.rule_type.lower()

    if strategy not in RoutingEngine.SUPPORTED_STRATEGIES:
        return "weighted"

    return strategy


@router.api_route(
    "/{route}",
    methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
        "OPTIONS",
        "HEAD",
    ],
)
async def proxy_request(
    route: str,
    request: Request,
    db: Session = Depends(get_db),
):
    route_record = (
        db.query(Route)
        .filter(Route.name == route)
        .first()
    )

    if route_record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Route not found",
        )

    backends = (
        db.query(ORMBackend)
        .filter(
            ORMBackend.route_id == route_record.id,
            ORMBackend.enabled.is_(True),
        )
        .all()
    )

    if not backends:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No enabled backends available",
        )

    available_backends = []

    for backend in backends:
        breaker = get_circuit_breaker(backend.id)

        if breaker.allow_request():
            available_backends.append(backend)
        else:
            print(
                f"[Relay Circuit] OPEN: "
                f"backend={backend.url}"
            )

    if not available_backends:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="All backend circuits are open",
        )

    strategy = get_strategy(
        route_record,
        db,
    )

    routing_backends = [
        RoutingBackend(
            id=str(backend.id),
            url=backend.url,
            weight=max(1, int(backend.weight)),
            priority=backend.priority,
            active_connections=runtime_active_connections.get(
                backend.id,
                0,
            ),
            latency_ms=runtime_latency_ms.get(
                backend.id,
                0.0,
            ),
            healthy=True,
        )
        for backend in available_backends
    ]

    try:
        selected = routing_engine.select_backend(
            routing_backends,
            strategy,
        )

    except (RuntimeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        )

    selected_backend = next(
        backend
        for backend in available_backends
        if str(backend.id) == selected.id
    )

    selected_breaker = get_circuit_breaker(
        selected_backend.id
    )

    runtime_active_connections[selected_backend.id] = (
        runtime_active_connections.get(
            selected_backend.id,
            0,
        )
        + 1
    )

    start_time = time.perf_counter()

    try:
        body = await request.body()

        headers = dict(request.headers)
        headers.pop("host", None)

        async with httpx.AsyncClient(
            timeout=REQUEST_TIMEOUT,
            follow_redirects=False,
        ) as client:

            upstream_response = await client.request(
                method=request.method,
                url=selected_backend.url,
                content=body,
                headers=headers,
                params=request.query_params,
            )

        elapsed_ms = (
            time.perf_counter() - start_time
        ) * 1000

        if upstream_response.status_code >= 500:
            selected_breaker.record_failure()

            print(
                f"[Relay Circuit] FAILURE: "
                f"backend={selected_backend.url} "
                f"status={upstream_response.status_code} "
                f"failures={selected_breaker.failure_count} "
                f"state={selected_breaker.state.value}"
            )

        else:
            selected_breaker.record_success()

        print(
            f"[Relay] route={route_record.name} "
            f"strategy={strategy} "
            f"backend={selected_backend.url} "
            f"latency={elapsed_ms:.2f}ms "
            f"circuit={selected_breaker.state.value}"
        )

        excluded_headers = {
            "content-encoding",
            "transfer-encoding",
            "connection",
        }

        response_headers = {
            key: value
            for key, value in upstream_response.headers.items()
            if key.lower() not in excluded_headers
        }

        return Response(
            content=upstream_response.content,
            status_code=upstream_response.status_code,
            headers=response_headers,
            media_type=upstream_response.headers.get(
                "content-type"
            ),
        )

    except httpx.TimeoutException:
        selected_breaker.record_failure()

        print(
            f"[Relay Circuit] TIMEOUT: "
            f"backend={selected_backend.url} "
            f"failures={selected_breaker.failure_count} "
            f"state={selected_breaker.state.value}"
        )

        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Backend request timed out",
        )

    except httpx.RequestError as exc:
        selected_breaker.record_failure()

        print(
            f"[Relay Circuit] REQUEST FAILURE: "
            f"backend={selected_backend.url} "
            f"failures={selected_breaker.failure_count} "
            f"state={selected_breaker.state.value}"
        )

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Backend request failed: {str(exc)}",
        )

    finally:
        runtime_active_connections[selected_backend.id] = max(
            0,
            runtime_active_connections.get(
                selected_backend.id,
                1,
            )
            - 1
        )

        elapsed_ms = (
            time.perf_counter() - start_time
        ) * 1000

        previous_latency = runtime_latency_ms.get(
            selected_backend.id
        )

        if previous_latency is None:
            runtime_latency_ms[selected_backend.id] = elapsed_ms
        else:
            runtime_latency_ms[selected_backend.id] = (
                0.8 * previous_latency
                + 0.2 * elapsed_ms
            )
