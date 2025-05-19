from unittest.mock import AsyncMock, patch

import httpx
import pytest

from app.domain.models.ip_data import Geolocation
from app.domain.services import IpGeolocationServiceError, IpGeolocationServiceUnavailableError
from app.infrastructure.ipstack_geolocation_service import IpStackGeolocationService


@pytest.mark.asyncio
class TestIpStackGeolocationService:
    @pytest.fixture
    def service(self) -> IpStackGeolocationService:
        return IpStackGeolocationService(api_key="dummy")

    @pytest.fixture
    def ip_data(self) -> dict:
        return {
            "ip": "1.1.1.1",
            "country_name": "Australia",
            "city": "Sydney",
            # ... add all required fields for IpGeolocationData ...
        }

    @patch("httpx.AsyncClient.get")
    async def test_get_geolocation_by_ip_success(self, mock_get, service, ip_data):
        # Given
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = ip_data
        mock_get.return_value = mock_response

        # When
        result = await service.get_geolocation_by_ip("1.1.1.1")

        # Then
        assert isinstance(result, Geolocation)
        assert result.ip == ip_data["ip"]

    @patch("httpx.AsyncClient.get")
    async def test_get_geolocation_by_ip_failure(self, mock_get, service):
        # Given
        mock_response = AsyncMock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        # When / Then
        with pytest.raises(IpGeolocationServiceError):
            await service.get_geolocation_by_ip("1.1.1.1")

    @patch("httpx.AsyncClient.get")
    async def test_get_geolocation_by_url_success(self, mock_get, service, ip_data):
        # Given
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = ip_data
        mock_get.return_value = mock_response

        # When
        result = await service.get_geolocation_by_url("example.com")

        # Then
        assert isinstance(result, Geolocation)
        assert result.ip == ip_data["ip"]

    @patch("httpx.AsyncClient.get")
    async def test_get_geolocation_by_url_failure(self, mock_get, service):
        # Given
        mock_response = AsyncMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        # When / Then
        with pytest.raises(IpGeolocationServiceError):
            await service.get_geolocation_by_url("example.com")

    @patch("httpx.AsyncClient.get")
    async def test_is_available_success(self, mock_get, service):
        # Given
        mock_response = AsyncMock()
        mock_response.status_code = 101  # Simulate "missing API key" but service is up
        mock_get.return_value = mock_response

        # When
        result = await service.is_available()

        # Then
        assert result is True

    @patch("httpx.AsyncClient.get")
    async def test_is_available_failure(self, mock_get, service):
        # Given
        mock_response = AsyncMock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        # When
        result = await service.is_available()

        # Then
        assert result is False

    @patch("httpx.AsyncClient.get", side_effect=httpx.RequestError("Network error"))
    async def test_is_available_exception(self, mock_get, service):
        # Given/When
        result = await service.is_available()

        # Then
        assert result is False
