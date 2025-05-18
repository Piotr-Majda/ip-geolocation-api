from unittest.mock import AsyncMock, MagicMock

import pytest

from app.application.geolocation_service import (
    GeolocationApplicationService,
    NotFoundGeolocationData,
)
from app.domain.models.ip_data import IpGeolocationData


@pytest.fixture
def repo():
    return MagicMock()


@pytest.fixture
def service():
    return MagicMock()


@pytest.fixture
def app_service(repo, service):
    return GeolocationApplicationService(repository=repo, external_service=service)


@pytest.mark.asyncio
async def test_get_ip_data_returns_data(app_service, repo):
    # Given
    ip_data = IpGeolocationData(ip="1.1.1.1")
    repo.get_by_ip = AsyncMock(return_value=ip_data)
    # When
    result = await app_service.get_ip_data("1.1.1.1")
    # Then
    assert result == ip_data
    repo.get_by_ip.assert_awaited_once_with("1.1.1.1")


@pytest.mark.asyncio
async def test_get_url_data_returns_data(app_service, repo):
    # Given
    url_data = IpGeolocationData(ip="1.1.1.1", url="example.com")
    repo.get_by_url = AsyncMock(return_value=url_data)
    # When
    result = await app_service.get_url_data("example.com")
    # Then
    assert result == url_data
    repo.get_by_url.assert_awaited_once_with("example.com")


@pytest.mark.asyncio
async def test_add_ip_data_success(app_service, service, repo):
    # Given
    ip_data = IpGeolocationData(ip="1.1.1.1")
    service.get_geolocation_by_ip = AsyncMock(return_value=ip_data)
    repo.add = AsyncMock(return_value=ip_data)
    # When
    result = await app_service.add_ip_data("1.1.1.1")
    # Then
    assert result == ip_data
    service.get_geolocation_by_ip.assert_awaited_once_with("1.1.1.1")
    repo.add.assert_awaited_once_with(ip_data)


@pytest.mark.asyncio
async def test_add_ip_data_not_found(app_service, service):
    # Given
    service.get_geolocation_by_ip = AsyncMock(return_value=None)
    # When/Then
    with pytest.raises(NotFoundGeolocationData):
        await app_service.add_ip_data("1.1.1.1")
    service.get_geolocation_by_ip.assert_awaited_once_with("1.1.1.1")


@pytest.mark.asyncio
async def test_add_url_data_success(app_service, service, repo):
    # Given
    url_data = IpGeolocationData(ip="1.1.1.1", url="example.com")
    service.get_geolocation_by_url = AsyncMock(return_value=url_data)
    repo.add = AsyncMock(return_value=url_data)
    # When
    result = await app_service.add_url_data("example.com")
    # Then
    assert result == url_data
    service.get_geolocation_by_url.assert_awaited_once_with("example.com")
    repo.add.assert_awaited_once_with(url_data)


@pytest.mark.asyncio
async def test_add_url_data_not_found(app_service, service):
    # Given
    service.get_geolocation_by_url = AsyncMock(return_value=None)
    # When/Then
    with pytest.raises(NotFoundGeolocationData):
        await app_service.add_url_data("example.com")
    service.get_geolocation_by_url.assert_awaited_once_with("example.com")


@pytest.mark.asyncio
async def test_delete_ip_data(app_service, repo):
    # Given
    repo.delete_by_ip = AsyncMock(return_value=True)
    # When
    result = await app_service.delete_ip_data("1.1.1.1")
    # Then
    assert result is True
    repo.delete_by_ip.assert_awaited_once_with("1.1.1.1")


@pytest.mark.asyncio
async def test_delete_url_data(app_service, repo):
    # Given
    repo.delete_by_url = AsyncMock(return_value=True)
    # When
    result = await app_service.delete_url_data("example.com")
    # Then
    assert result is True
    repo.delete_by_url.assert_awaited_once_with("example.com")
