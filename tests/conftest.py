"""
Global pytest fixtures for the IP Geolocation API tests.
"""

from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest
from sqlalchemy import delete

from app.domain.models.ip_data import Geolocation
from app.domain.services import IpGeolocationService, IpGeolocationServiceError
from app.infrastructure.database import DatabaseClient
from app.infrastructure.models import IpGeolocation
from app.interfaces.api.routes.dependencies import get_database_client, get_ip_geolocation_service

# Import the FastAPI app
from app.main import app


# pytest options
def pytest_addoption(parser):
    parser.addoption(
        "--use-real-api",
        action="store_true",
        default=False,
        help="Run tests against real IpStack API",
    )
    parser.addoption(
        "--api-key",
        action="store",
        default=None,
        help="API key for IpStack service",
    )


# Database client


@pytest.fixture
async def database_client():
    """
    Database client that is up.
    """
    # test_database_url = "sqlite+aiosqlite:///:memory:"
    test_database_url = "postgresql+asyncpg://postgres:postgres@localhost:5433/geolocation-test"
    db_client = DatabaseClient(url=test_database_url)
    try:
        db_client.connect()
        await db_client.reset_schema()
        yield db_client
    finally:
        await db_client.close()


@pytest.fixture
async def database_client_down(database_client: DatabaseClient):
    """
    Database client that is down.
    """
    try:
        await database_client.close()
        yield database_client
    finally:
        database_client.connect()


@pytest.fixture
async def populate_db_with_ip_geolocation_data(
    database_client: DatabaseClient, ip_geolocation_data: Geolocation
):
    """
    Populate the database with IP geolocation data.
    """
    async with database_client.get_session() as session:
        # Create your test data
        test_entry = IpGeolocation(**ip_geolocation_data.model_dump())
        session.add(test_entry)
        await session.commit()
    yield
    # Optionally, clean up after test
    async with database_client.get_session() as session:
        await session.execute(delete(IpGeolocation))
        await session.commit()


@pytest.fixture
def ip_geolocation_data(request) -> Geolocation | None:
    """
    IP geolocation data that is up.
    """
    if getattr(request, "param", None) and isinstance(request.param, Geolocation):
        geolocation_data = request.param
    else:
        geolocation_data = None
    return geolocation_data


@pytest.fixture
def ip_geolocation_service(
    request, ip_geolocation_data: Geolocation | None
) -> IpGeolocationService:
    """
    IP geolocation service
    param: bool, if False, the service is unavailable, otherwise it is up
    """
    if getattr(request, "param", None) is False:
        print("IP geolocation service is unavailable (mocked)")
        return MagicMock(
            spec=IpGeolocationService,
            is_available=AsyncMock(return_value=False),
            get_geolocation_by_ip=AsyncMock(
                side_effect=IpGeolocationServiceError("Service unavailable")
            ),
            get_geolocation_by_url=AsyncMock(
                side_effect=IpGeolocationServiceError("Service unavailable")
            ),
        )
    else:
        print("IP geolocation service is available (mocked)")
        return MagicMock(
            spec=IpGeolocationService,
            is_available=AsyncMock(return_value=True),
            get_geolocation_by_ip=AsyncMock(return_value=ip_geolocation_data),
            get_geolocation_by_url=AsyncMock(return_value=ip_geolocation_data),
        )


# Test client
@pytest.fixture
async def test_client(
    database_client: DatabaseClient, ip_geolocation_service: IpGeolocationService
):
    """
    Create a TestClient for making API requests without running a server.

    This is useful for unit tests or when you don't want to start a real server.
    """

    async def get_database_client_override():
        return database_client

    async def get_ip_geolocation_service_override():
        return ip_geolocation_service

    app.dependency_overrides[get_database_client] = get_database_client_override
    app.dependency_overrides[get_ip_geolocation_service] = get_ip_geolocation_service_override

    async with httpx.AsyncClient(app=app, base_url="http://localhost:8000/") as client:
        yield client

    app.dependency_overrides = {}


@pytest.fixture
async def test_client_v1(
    database_client: DatabaseClient, ip_geolocation_service: IpGeolocationService
):
    """
    Create a TestClient for making API requests without running a server.

    This is useful for unit tests or when you don't want to start a real server.
    """

    async def get_database_client_override():
        return database_client

    async def get_ip_geolocation_service_override():
        return ip_geolocation_service

    app.dependency_overrides[get_database_client] = get_database_client_override
    app.dependency_overrides[get_ip_geolocation_service] = get_ip_geolocation_service_override

    async with httpx.AsyncClient(app=app, base_url="http://localhost:8000/api/v1") as client:
        yield client

    app.dependency_overrides = {}
