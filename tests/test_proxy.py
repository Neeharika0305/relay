import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import Project, Route, Backend, RoutingRule
import routes.proxy as proxy_module


SQLITE_URL = "sqlite://"

test_engine = create_engine(
    SQLITE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False,
)


@pytest.fixture
def db_session():
    Base.metadata.create_all(bind=test_engine)

    session = TestingSessionLocal()

    try:
        project = Project(
            id=1,
            name="Test Project",
            api_key="test-api-key",
        )

        route = Route(
            id=1,
            name="demo",
            path="/demo",
            strategy="weighted",
        )

        backend = Backend(
            id=1,
            route_id=1,
            url="http://backend.test",
            weight=100,
            priority=3,
            enabled=True,
        )

        rule = RoutingRule(
            id=1,
            route_id=1,
            rule_type="weighted",
            rule_value="default",
            priority=1,
        )

        session.add_all([
            project,
            route,
            backend,
            rule,
        ])

        session.commit()

        yield session

    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client(db_session, monkeypatch):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async def mock_request(
        self,
        method,
        url,
        content=None,
        headers=None,
        params=None,
    ):
        class MockResponse:
            status_code = 200
            content = b'{"message":"backend response"}'

            headers = {
                "content-type": "application/json",
            }

        return MockResponse()

    monkeypatch.setattr(
        proxy_module.httpx.AsyncClient,
        "request",
        mock_request,
    )

    yield TestClient(app)

    app.dependency_overrides.clear()


def test_proxy_forwards_request(client):
    response = client.get("/v1/proxy/demo")

    assert response.status_code == 200
    assert response.json() == {
        "message": "backend response"
    }


def test_proxy_returns_504_on_timeout(client, monkeypatch):

    async def mock_timeout(
        self,
        method,
        url,
        content=None,
        headers=None,
        params=None,
    ):
        raise proxy_module.httpx.TimeoutException(
            "Backend timed out"
        )

    monkeypatch.setattr(
        proxy_module.httpx.AsyncClient,
        "request",
        mock_timeout,
    )

    response = client.get("/v1/proxy/demo")

    assert response.status_code == 504


def test_proxy_returns_502_on_connection_error(
    client,
    monkeypatch,
):

    async def mock_connection_error(
        self,
        method,
        url,
        content=None,
        headers=None,
        params=None,
    ):
        raise proxy_module.httpx.RequestError(
            "Connection failed"
        )

    monkeypatch.setattr(
        proxy_module.httpx.AsyncClient,
        "request",
        mock_connection_error,
    )

    response = client.get("/v1/proxy/demo")

    assert response.status_code == 502


def test_proxy_returns_404_for_missing_route(client):

    response = client.get("/v1/proxy/missing")

    assert response.status_code == 404


def test_proxy_returns_503_when_no_enabled_backends(
    client,
    db_session,
):

    backend = (
        db_session.query(Backend)
        .filter(Backend.route_id == 1)
        .first()
    )

    backend.enabled = False
    db_session.commit()

    response = client.get("/v1/proxy/demo")

    assert response.status_code == 503


def test_proxy_records_latency(client):

    response = client.get("/v1/proxy/demo")

    assert response.status_code == 200
    assert 1 in proxy_module.runtime_latency_ms
    assert proxy_module.runtime_latency_ms[1] >= 0


def test_proxy_releases_active_connection(client):

    response = client.get("/v1/proxy/demo")

    assert response.status_code == 200

    assert proxy_module.runtime_active_connections.get(
        1,
        0,
    ) == 0


def test_proxy_uses_priority_routing(
    client,
    db_session,
    monkeypatch,
):

    backend_1 = Backend(
        id=2,
        route_id=1,
        url="http://backend-2.test",
        weight=100,
        priority=2,
        enabled=True,
    )

    backend_2 = Backend(
        id=3,
        route_id=1,
        url="http://backend-3.test",
        weight=100,
        priority=1,
        enabled=True,
    )

    db_session.add_all([
        backend_1,
        backend_2,
    ])

    rule = (
        db_session.query(RoutingRule)
        .filter(RoutingRule.route_id == 1)
        .first()
    )

    rule.rule_type = "priority"
    db_session.commit()

    selected_url = None

    async def mock_request(
        self,
        method,
        url,
        content=None,
        headers=None,
        params=None,
    ):
        nonlocal selected_url

        selected_url = url

        class MockResponse:
            status_code = 200
            content = b'{"message":"backend response"}'

            headers = {
                "content-type": "application/json",
            }

        return MockResponse()

    monkeypatch.setattr(
        proxy_module.httpx.AsyncClient,
        "request",
        mock_request,
    )

    response = client.get("/v1/proxy/demo")

    assert response.status_code == 200
    assert selected_url == "http://backend-3.test"
