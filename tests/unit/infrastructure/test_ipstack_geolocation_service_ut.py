import re
from unittest.mock import MagicMock, patch

import httpx
import pytest

from app.domain.models.ip_data import Geolocation
from app.domain.services import IpGeolocationServiceError
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
            "latitude": 1.23,
            "longitude": 4.56,
            "city": "Sydney",
            "region_name": "NSW",
            "country_name": "Australia",
            "continent_name": "Oceania",
            "zip": "2000",
            # ... add all required fields for IpGeolocationData ...
        }

    @pytest.fixture
    def ip_data_missing_fields(self) -> dict:
        return {
            "ip": "1.1.1.1",
            "city": "Sydney",
            "region_name": "NSW",
            "country_name": "Australia",
            "continent_name": "Oceania",
            "zip": "2000",
            "country_code": "AU",
            "region_code": "NSW",
        }

    @pytest.fixture
    def ip_data_wrong_fields(self) -> dict:
        return {
            "ip": "1.1.1.1",
            "latitude": "east",
            "longitude": "west",
            "city": "Sydney",
            "region_name": "NSW",
            "country_name": "Australia",
            "continent_name": "Oceania",
            "zip": "2000",
            "country_code": "AU",
            "region_code": "NSW",
        }

    @patch("httpx.AsyncClient.get")
    async def test_get_geolocation_by_ip_success(self, mock_get, service, ip_data):
        # Given
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = ip_data
        mock_get.return_value = mock_response

        # When
        result = await service.get_geolocation_by_ip("1.1.1.1")

        # Then
        assert isinstance(result, Geolocation)
        assert result.ip == ip_data["ip"]

    @patch("httpx.AsyncClient.get")
    async def test_get_geolocation_by_ip_missing_required_fields(
        self, mock_get, service, ip_data_missing_fields
    ):
        # Given
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = ip_data_missing_fields
        mock_get.return_value = mock_response

        # When/Then
        with pytest.raises(
            IpGeolocationServiceError,
            match=re.compile(r"Invalid response: missing required fields.*"),
        ):
            await service.get_geolocation_by_ip("1.1.1.1")

    @patch("httpx.AsyncClient.get")
    async def test_get_geolocation_by_ip_field_validation_error(
        self, mock_get, service, ip_data_wrong_fields
    ):
        # Given
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = ip_data_wrong_fields
        mock_get.return_value = mock_response

        # When/Then
        with pytest.raises(
            IpGeolocationServiceError, match=re.compile(r"Invalid JSON response:.*")
        ):
            await service.get_geolocation_by_ip("1.1.1.1")

    @patch("httpx.AsyncClient.get")
    async def test_get_geolocation_by_ip_failure(self, mock_get, service):
        # Given
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        # When / Then
        with pytest.raises(IpGeolocationServiceError):
            await service.get_geolocation_by_ip("1.1.1.1")

    @patch("httpx.AsyncClient.get")
    async def test_get_geolocation_by_url_success(self, mock_get, service, ip_data):
        # Given
        mock_response = MagicMock()
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
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        # When / Then
        with pytest.raises(IpGeolocationServiceError):
            await service.get_geolocation_by_url("example.com")

    @patch("httpx.AsyncClient.get")
    async def test_is_available_success(self, mock_get, service):
        # Given
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"error": {"code": 101}}
        mock_get.return_value = mock_response

        # When
        result = await service.is_available()

        # Then
        assert result is True

    @patch("httpx.AsyncClient.get")
    async def test_is_available_failure(self, mock_get, service):
        # Given
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.json.return_value = {}
        mock_get.return_value = mock_response

        # When
        result = await service.is_available()

        # Then
        assert result is False

    @patch("httpx.AsyncClient.get")
    async def test_is_available_unexpected_error_code(self, mock_get, service):
        # Given
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"error": {"code": 999}}
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
