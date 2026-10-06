from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Route, Backend as ORMBackend
from app.models import RoutingRule
from schemas.route import RouteCreate, RouteResponse


router = APIRouter(
    prefix="/v1/routes",
    tags=["Routes"],
)


def route_response(route: Route, db: Session) -> dict:
    backends = (
        db.query(ORMBackend)
        .filter(ORMBackend.route_id == route.id)
        .all()
    )

    rules = (
        db.query(RoutingRule)
        .filter(RoutingRule.route_id == route.id)
        .order_by(RoutingRule.priority.asc())
        .all()
    )

    strategy = (
        rules[0].rule_type
        if rules
        else route.strategy
    )

    return {
        "id": route.id,
        "name": route.name,
        "path": route.path,
        "strategy": strategy,
        "backends": [
            {
                "id": backend.id,
                "name": f"backend-{backend.id}",
                "url": backend.url,
                "weight": int(backend.weight),
                "priority": backend.priority,
                "active_connections": 0,
                "latency_ms": 0.0,
                "healthy": backend.enabled,
            }
            for backend in backends
        ],
    }


@router.post(
    "",
    response_model=RouteResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_route(
    route_data: RouteCreate,
    db: Session = Depends(get_db),
):
    existing_route = (
        db.query(Route)
        .filter(Route.name == route_data.name)
        .first()
    )

    if existing_route:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Route name already exists",
        )

    now = datetime.now(timezone.utc)

    route = Route(
        name=route_data.name,
        path=route_data.path,
        strategy=route_data.strategy.value,
        created_at=now,
        updated_at=now,
    )

    db.add(route)
    db.flush()

    rule = RoutingRule(
        route_id=route.id,
        rule_type=route_data.strategy.value,
        rule_value="default",
        priority=1,
    )

    db.add(rule)

    for backend_data in route_data.backends:
        backend = ORMBackend(
            route_id=route.id,
            url=str(backend_data.url),
            weight=float(backend_data.weight),
            priority=backend_data.priority,
            enabled=True,
        )

        db.add(backend)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Route or backend violates a database constraint",
        )

    db.refresh(route)

    return route_response(route, db)


@router.get(
    "",
    response_model=list[RouteResponse],
)
def get_routes(
    db: Session = Depends(get_db),
):
    routes = (
        db.query(Route)
        .order_by(Route.id)
        .all()
    )

    return [
        route_response(route, db)
        for route in routes
    ]


@router.get(
    "/{route_id}",
    response_model=RouteResponse,
)
def get_route(
    route_id: int,
    db: Session = Depends(get_db),
):
    route = (
        db.query(Route)
        .filter(Route.id == route_id)
        .first()
    )

    if route is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Route not found",
        )

    return route_response(route, db)


@router.put(
    "/{route_id}",
    response_model=RouteResponse,
)
def update_route(
    route_id: int,
    route_data: RouteCreate,
    db: Session = Depends(get_db),
):
    route = (
        db.query(Route)
        .filter(Route.id == route_id)
        .first()
    )

    if route is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Route not found",
        )

    duplicate = (
        db.query(Route)
        .filter(
            Route.id != route_id,
            Route.name == route_data.name,
        )
        .first()
    )

    if duplicate:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Route name already exists",
        )

    route.name = route_data.name
    route.path = route_data.path
    route.strategy = route_data.strategy.value
    route.updated_at = datetime.now(timezone.utc)

    db.query(ORMBackend).filter(
        ORMBackend.route_id == route.id
    ).delete()

    db.query(RoutingRule).filter(
        RoutingRule.route_id == route.id
    ).delete()

    rule = RoutingRule(
        route_id=route.id,
        rule_type=route_data.strategy.value,
        rule_value="default",
        priority=1,
    )

    db.add(rule)

    for backend_data in route_data.backends:
        backend = ORMBackend(
            route_id=route.id,
            url=str(backend_data.url),
            weight=float(backend_data.weight),
            priority=backend_data.priority,
            enabled=True,
        )

        db.add(backend)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Route update violates a database constraint",
        )

    db.refresh(route)

    return route_response(route, db)


@router.delete(
    "/{route_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_route(
    route_id: int,
    db: Session = Depends(get_db),
):
    route = (
        db.query(Route)
        .filter(Route.id == route_id)
        .first()
    )

    if route is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Route not found",
        )

    db.query(ORMBackend).filter(
        ORMBackend.route_id == route.id
    ).delete()

    db.query(RoutingRule).filter(
        RoutingRule.route_id == route.id
    ).delete()

    db.delete(route)
    db.commit()

    return None