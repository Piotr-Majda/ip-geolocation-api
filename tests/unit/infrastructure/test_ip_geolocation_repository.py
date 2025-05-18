from unittest.mock import AsyncMock, MagicMock

import pytest

from sqlalchemy.exc import OperationalError

from app.domain.models.ip_data import IpGeolocationData
from app.infrastructure.ip_geolocation_repository import (
    DatabaseUnavailableError,
    IpGeolocationRepositoryImpl,
)
from app.infrastructure.models import IpGeolocation


# Dummy ORM class for model_validate
class DummyORM:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
            

class AsyncSessionContextManager:
    def __init__(self, session):
        self.session = session
    async def __aenter__(self):
        return self.session
    async def __aexit__(self, exc_type, exc, tb):
        pass


@pytest.mark.asyncio
class TestIpGeolocationRepositoryImpl:
    @pytest.fixture
    def mock_session(self):
        session = MagicMock()
        session.commit = AsyncMock()
        session.refresh = AsyncMock()
        session.rollback = AsyncMock()
        session.add = MagicMock()
        session.execute = AsyncMock(return_value=MagicMock())
        return session

    @pytest.fixture
    def mock_db_client(self, mock_session):
        db_client = MagicMock()
        db_client.get_session.return_value = AsyncSessionContextManager(mock_session)
        return db_client

    @pytest.fixture
    def repo(self, mock_db_client):
        return IpGeolocationRepositoryImpl(database_client=mock_db_client)

    @pytest.fixture
    def ip_data(self):
        return IpGeolocationData(
            ip="1.1.1.1",
            url="example.com",
            city="Sydney",
            country="Australia",
            # Add other required fields as needed
        )

    async def test_add_success(self, repo, mock_session, ip_data):
        # Given
        mock_session.commit.return_value = None
        mock_session.refresh.return_value = None

        # When
        result = await repo.add(ip_data)

        # Then
        assert isinstance(result, IpGeolocationData)
        assert result.ip == ip_data.ip

    async def test_add_operational_error(self, repo, mock_session, ip_data):
        # Given

        mock_session.commit.side_effect = OperationalError("stmt", {}, Exception())
        mock_session.rollback.return_value = None

        # When / Then
        with pytest.raises(DatabaseUnavailableError):
            await repo.add(ip_data)

    async def test_get_by_ip_found(self, repo, mock_session, ip_data):
        # Given
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = DummyORM(**ip_data.model_dump())
        mock_session.execute.return_value = mock_result

        # When
        result = await repo.get_by_ip(ip_data.ip)

        # Then
        assert isinstance(result, IpGeolocationData)
        assert result.ip == ip_data.ip

    async def test_get_by_ip_not_found(self, repo, mock_session):
        # Given
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        # When
        result = await repo.get_by_ip("1.1.1.1")

        # Then
        assert result is None

    async def test_get_by_ip_operational_error(self, repo, mock_session):
        # Given
        mock_session.execute.side_effect = OperationalError("stmt", {}, Exception())

        # When / Then
        with pytest.raises(DatabaseUnavailableError):
            await repo.get_by_ip("1.1.1.1")

    async def test_get_by_url_found(self, repo, mock_session, ip_data):
        # Given
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = DummyORM(**ip_data.model_dump())
        mock_session.execute.return_value = mock_result

        # When
        result = await repo.get_by_url(ip_data.url)

        # Then
        assert isinstance(result, IpGeolocationData)
        assert result.url == ip_data.url

    async def test_get_by_url_not_found(self, repo, mock_session):
        # Given
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        # When
        result = await repo.get_by_url("example.com")

        # Then
        assert result is None

    async def test_get_by_url_operational_error(self, repo, mock_session):
        # Given
        mock_session.execute.side_effect = OperationalError("stmt", {}, Exception())

        # When / Then
        with pytest.raises(DatabaseUnavailableError):
            await repo.get_by_url("example.com")

    async def test_delete_by_ip_success(self, repo, mock_session):
        # Given
        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit.return_value = None

        # When
        result = await repo.delete_by_ip("1.1.1.1")

        # Then
        assert result is True

    async def test_delete_by_ip_not_found(self, repo, mock_session):
        # Given
        mock_result = MagicMock()
        mock_result.rowcount = 0
        mock_session.execute = AsyncMock(return_value=mock_result)

        # When
        result = await repo.delete_by_ip("1.1.1.1")

        # Then
        assert result is False

    async def test_delete_by_ip_operational_error(self, repo, mock_session):
        # Given
        

        mock_session.execute.side_effect = OperationalError("stmt", {}, Exception())
        mock_session.rollback.return_value = None

        # When / Then
        with pytest.raises(DatabaseUnavailableError):
            await repo.delete_by_ip("1.1.1.1")

    async def test_delete_by_url_success(self, repo, mock_session):
        # Given
        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_session.execute.return_value = mock_result
        mock_session.commit.return_value = None

        # When
        result = await repo.delete_by_url("example.com")

        # Then
        assert result is True

    async def test_delete_by_url_not_found(self, repo, mock_session): 
        # Given
        mock_result = MagicMock()
        mock_result.rowcount = 0
        mock_session.execute.return_value = mock_result
        mock_session.commit.return_value = None

        # When
        result = await repo.delete_by_url("example.com")

        # Then
        assert result is False

    async def test_delete_by_url_operational_error(self, repo, mock_session):
        # Given
        mock_session.execute.side_effect = OperationalError("stmt", {}, Exception())
        mock_session.rollback.return_value = None

        # When / Then
        with pytest.raises(DatabaseUnavailableError):
            await repo.delete_by_url("example.com")

    async def test_is_available_true(self, repo, mock_session):
        # Given
        mock_session.execute.return_value = None

        # When
        result = await repo.is_available()

        # Then
        assert result is True

    async def test_is_available_operational_error(self, repo, mock_session):
        # Given
        mock_session.execute.side_effect = OperationalError("stmt", {}, Exception())

        # When
        result = await repo.is_available()

        # Then
        assert result is False

    async def test_is_available_unexpected_error(self, repo, mock_session):
        # Given
        mock_session.execute.side_effect = Exception("unexpected")

        # When
        result = await repo.is_available()

        # Then
        assert result is False
