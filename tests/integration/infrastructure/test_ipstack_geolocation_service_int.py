import pytest

from app.core.config import settings
from app.domain.services import IpGeolocationServiceError
from app.infrastructure.ipstack_geolocation_service import IpStackGeolocationService


@pytest.fixture
def ipstack_service(use_real_api, api_key) -> IpStackGeolocationService:
    if not use_real_api:
        pytest.skip("Skipping test: --use-real-api flag not set")

    key = api_key or settings.IPSTACK_API_KEY
    if not key:
        pytest.skip("No API key provided. Use --api-key or set IPSTACK_API_KEY in settings")

    return IpStackGeolocationService(api_key=key)


@pytest.mark.asyncio
async def test_is_available(ipstack_service: IpStackGeolocationService):
    """Test if IpStack service is available."""
    is_available = await ipstack_service.is_available()
    assert is_available is True, "Service should be available"


@pytest.mark.asyncio
async def test_get_geolocation_by_ip(ipstack_service: IpStackGeolocationService):
    """Test geolocation lookup with IP."""
    result = await ipstack_service.get_geolocation_by_ip("8.8.8.8")
    assert result is not None, "Result should not be None"
    assert result.ip == "8.8.8.8"
    assert result.country is not None
    assert result.city is not None
    assert result.latitude is not None
    assert result.longitude is not None
    assert result.region is not None
    assert result.continent is not None
    assert result.postal_code is not None


@pytest.mark.asyncio
async def test_get_geolocation_by_url(ipstack_service: IpStackGeolocationService):
    """Test geolocation lookup with URL."""
    result = await ipstack_service.get_geolocation_by_url("www.google.com")
    assert result is not None, "Result should not be None"
    assert result.ip is not None
    assert result.country is not None
    assert result.city is not None
    assert result.latitude is not None
    assert result.longitude is not None
    assert result.region is not None
    assert result.continent is not None
    assert result.postal_code is not None


@pytest.mark.asyncio
async def test_get_geolocation_invalid_ip(ipstack_service: IpStackGeolocationService):
    """Test handling of invalid IP."""
    with pytest.raises(IpGeolocationServiceError) as exc_info:
        await ipstack_service.get_geolocation_by_ip("999.999.999.999")
    assert "The IP Address supplied is invalid." in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_geolocation_invalid_url(ipstack_service: IpStackGeolocationService):
    """Test handling of invalid URL."""
    with pytest.raises(IpGeolocationServiceError) as exc_info:
        await ipstack_service.get_geolocation_by_url("thisisnotarealwebsite123456789.com")
    assert "The IP Address supplied is invalid." in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_geolocation_with_invalid_api_key():
    """Test handling of invalid API key."""
    service = IpStackGeolocationService(api_key="invalid_key")
    with pytest.raises(IpGeolocationServiceError) as exc_info:
        await service.get_geolocation_by_ip("8.8.8.8")
    assert "You have not supplied a valid API Access Key" in str(exc_info.value)
