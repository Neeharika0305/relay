from router.rules import Backend
from router.routing_engine import RoutingEngine


def create_backends():

    return [
        Backend(
            id="backend-a",
            url="http://localhost:8001",
            weight=50,
            priority=1,
            active_connections=50,
            latency_ms=40,
        ),
        Backend(
            id="backend-b",
            url="http://localhost:8002",
            weight=30,
            priority=2,
            active_connections=10,
            latency_ms=120,
        ),
        Backend(
            id="backend-c",
            url="http://localhost:8003",
            weight=20,
            priority=3,
            active_connections=30,
            latency_ms=70,
        ),
    ]


def test_priority_routing():

    engine = RoutingEngine()

    backend = engine.select_backend(
        create_backends(),
        "priority",
    )

    assert backend.id == "backend-a"


def test_least_load_routing():

    engine = RoutingEngine()

    backend = engine.select_backend(
        create_backends(),
        "least_load",
    )

    assert backend.id == "backend-b"


def test_latency_routing():

    engine = RoutingEngine()

    backend = engine.select_backend(
        create_backends(),
        "latency",
    )

    assert backend.id == "backend-a"


def test_unhealthy_backend_is_ignored():

    backends = create_backends()

    backends[0].healthy = False

    engine = RoutingEngine()

    backend = engine.select_backend(
        backends,
        "priority",
    )

    assert backend.id == "backend-b"



def test_no_backends_configured():

    engine = RoutingEngine()

    try:
        engine.select_backend([], "priority")
        assert False
    except RuntimeError as error:
        assert str(error) == "No backends configured"


def test_unsupported_strategy():

    engine = RoutingEngine()

    try:
        engine.select_backend(create_backends(), "random")
        assert False
    except ValueError as error:
        assert str(error) == "Unsupported routing strategy: random"


def test_all_backends_unhealthy():

    backends = create_backends()

    for backend in backends:
        backend.healthy = False

    engine = RoutingEngine()

    try:
        engine.select_backend(backends, "priority")
        assert False
    except RuntimeError as error:
        assert str(error) == "No healthy backends available"


def test_invalid_backend_weight():

    try:
        Backend(
            id="backend-x",
            url="http://localhost:8001",
            weight=0,
        )
        assert False
    except ValueError as error:
        assert str(error) == "Backend weight must be greater than 0"


def test_invalid_backend_priority():

    try:
        Backend(
            id="backend-x",
            url="http://localhost:8001",
            priority=0,
        )
        assert False
    except ValueError as error:
        assert str(error) == "Backend priority must be greater than 0"


def test_negative_latency():

    try:
        Backend(
            id="backend-x",
            url="http://localhost:8001",
            latency_ms=-10,
        )
        assert False
    except ValueError as error:
        assert str(error) == "Latency cannot be negative"


def test_invalid_backend_url():

    try:
        Backend(
            id="backend-x",
            url="localhost:8001",
        )
        assert False
    except ValueError as error:
        assert str(error) == "Backend URL must start with http:// or https://"


def test_weighted_routing_ignores_unhealthy_backend():

    backends = create_backends()

    backends[0].healthy = False

    engine = RoutingEngine()

    for _ in range(50):
        backend = engine.select_backend(
            backends,
            "weighted",
        )

        assert backend.id != "backend-a"

def test_weighted_routing_distribution():

    backends = create_backends()

    engine = RoutingEngine()

    counts = {
        "backend-a": 0,
        "backend-b": 0,
        "backend-c": 0,
    }

    iterations = 10000

    for _ in range(iterations):
        backend = engine.select_backend(
            backends,
            "weighted",
        )

        counts[backend.id] += 1

    ratio_a = counts["backend-a"] / iterations
    ratio_b = counts["backend-b"] / iterations
    ratio_c = counts["backend-c"] / iterations

    assert 0.45 <= ratio_a <= 0.55
    assert 0.25 <= ratio_b <= 0.35
    assert 0.15 <= ratio_c <= 0.25