from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.exc import IntegrityError, OperationalError

from app.domain.models.ip_data import Geolocation
from app.infrastructure.ip_geolocation_repository import (
    DatabaseUnavailableError,
    IpGeolocationRepositoryImpl,
)


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
        return Geolocation(
            ip="1.1.1.1",
            url="www.example.com",
            city="Sydney",
            country="Australia",
            latitude=1.1,
            longitude=1.1,
            region="NSW",
            continent="Australia",
            postal_code="2000",
        )  # type: ignore

    @pytest.fixture
    def ip_data_with_invalid_ip(self):
        return Geolocation(
            ip="1.1.1.1",
            url="www.example.com",
            city="Sydney",
            country="Australia",
            latitude=1.1,
            longitude=1.1,
            region="NSW",
            continent="Australia",
            postal_code="2000",
        )  # type: ignore

    async def test_add_success(self, repo, mock_session, ip_data):
        # Given
        mock_session.commit.return_value = None
        mock_session.refresh.return_value = None
        repo.exists_by_ip = AsyncMock(return_value=False)

        # When
        result = await repo.add(ip_data)

        # Then
        assert isinstance(result, Geolocation)
        assert result.ip == ip_data.ip

    async def test_add_operational_error(self, repo, mock_session, ip_data):
        # Given

        mock_session.commit.side_effect = OperationalError("stmt", {}, Exception())
        mock_session.rollback.return_value = None
        repo.exists_by_ip = AsyncMock(return_value=False)

        # When / Then
        with pytest.raises(DatabaseUnavailableError):
            await repo.add(ip_data)

    async def test_add_integrity_error(self, repo, mock_session, ip_data):
        # Given
        mock_session.commit.side_effect = IntegrityError("stmt", {}, Exception())
        mock_session.rollback.return_value = None
        repo.exists_by_ip = AsyncMock(return_value=False)
        # When / Then
        with pytest.raises(DatabaseUnavailableError):
            await repo.add(ip_data)

    async def test_add_unexpected_error(self, repo, mock_session, ip_data):
        # Given
        mock_session.commit.side_effect = Exception("unexpected")
        mock_session.rollback.return_value = None
        repo.exists_by_ip = AsyncMock(return_value=False)

        # When / Then
        with pytest.raises(Exception):
            await repo.add(ip_data)

    async def test_update_success(self, repo, mock_session, ip_data):
        # Given
        mock_session.commit.return_value = None
        mock_session.refresh.return_value = None
        # Simulate existing record
        existing = MagicMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = existing
        mock_session.execute.return_value = mock_result

        # When
        result = await repo.update(ip_data)

        # Then
        assert isinstance(result, Geolocation)
        assert result.ip == ip_data.ip

    async def test_update_operational_error(self, repo, mock_session, ip_data):
        # Given
        mock_session.execute.side_effect = OperationalError("stmt", {}, Exception())
        mock_session.rollback.return_value = None

        # When / Then
        with pytest.raises(DatabaseUnavailableError):
            await repo.update(ip_data)

    async def test_update_integrity_error(self, repo, mock_session, ip_data):
        # Given
        existing = MagicMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = existing
        mock_session.execute.return_value = mock_result
        mock_session.commit.side_effect = IntegrityError("stmt", {}, Exception())
        mock_session.rollback.return_value = None

        # When / Then
        with pytest.raises(DatabaseUnavailableError):
            await repo.update(ip_data)

    async def test_update_unexpected_error(self, repo, mock_session, ip_data):
        # Given
        existing = MagicMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = existing
        mock_session.execute.return_value = mock_result
        mock_session.commit.side_effect = Exception("unexpected")
        mock_session.rollback.return_value = None

        # When / Then
        with pytest.raises(Exception):
            await repo.update(ip_data)

    async def test_get_by_ip_found(self, repo, mock_session, ip_data):
        # Given
        scalar_result = MagicMock(first=MagicMock(return_value=DummyORM(**ip_data.model_dump())))
        mock_execute_result = MagicMock(scalars=MagicMock(return_value=scalar_result))
        mock_session.execute.return_value = mock_execute_result

        # When
        result = await repo.get_by_ip(ip_data.ip)

        # Then
        assert isinstance(result, Geolocation)
        assert result.ip == ip_data.ip

    async def test_get_by_ip_not_found(self, repo, mock_session):
        # Given
        scalar_result = MagicMock(first=MagicMock(return_value=None))
        mock_execute_result = MagicMock(scalars=MagicMock(return_value=scalar_result))
        mock_session.execute.return_value = mock_execute_result

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
        scalar_result = MagicMock(first=MagicMock(return_value=DummyORM(**ip_data.model_dump())))
        mock_execute_result = MagicMock(scalars=MagicMock(return_value=scalar_result))
        mock_session.execute.return_value = mock_execute_result

        # When
        result = await repo.get_by_url(ip_data.url)

        # Then
        assert isinstance(result, Geolocation)
        assert result.url == ip_data.url

    async def test_get_by_url_not_found(self, repo, mock_session):
        # Given
        scalar_result = MagicMock(first=MagicMock(return_value=None))
        mock_execute_result = MagicMock(scalars=MagicMock(return_value=scalar_result))
        mock_session.execute.return_value = mock_execute_result

        # When
        result = await repo.get_by_url("non_existent_example.com")

        # Then
        assert result is None
        mock_session.execute.assert_called_once()

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

    async def test_exists_by_url_true(self, repo, mock_session):
        # Given
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = MagicMock()  # Simulate found
        mock_session.execute.return_value = mock_result

        # When
        result = await repo.exists_by_url("http://example.com")

        # Then
        assert result is True

    async def test_exists_by_url_false(self, repo, mock_session):
        # Given
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None  # Simulate not found
        mock_session.execute.return_value = mock_result

        # When
        result = await repo.exists_by_url("http://example.com")

        # Then
        assert result is False

    async def test_exists_by_url_operational_error(self, repo, mock_session):
        # Given
        mock_session.execute.side_effect = OperationalError("stmt", {}, Exception())

        # When / Then
        with pytest.raises(DatabaseUnavailableError):
            await repo.exists_by_url("http://example.com")
