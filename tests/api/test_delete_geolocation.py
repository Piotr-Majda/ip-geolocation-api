"""
API tests for geolocation endpoints to verify the application is running correctly.
"""

import pytest

from app.domain.models.ip_data import IpGeolocationData

test_data = [
    IpGeolocationData(
        ip="127.0.0.1",
        url="https://www.google.com/",
        latitude=123.456,
        longitude=78.910,
        city="Test City",
        region="Test Region",
        country="Test Country",
        continent="Test Continent",
        postal_code="12345",
    )
]


@pytest.mark.asyncio
@pytest.mark.parametrize("ip_geolocation_data", test_data, indirect=True)
async def test_delete_geolocation_by_ip_address(
    test_client_v1, ip_geolocation_data, populate_db_with_ip_geolocation_data
):
    """
    Verify that the /geolocation endpoint returns a 200 status code and reports 'ok' status.
    """
    response = await test_client_v1.delete(
        "/geolocation/", params={"ip_address": ip_geolocation_data.ip}
    )
    assert response.status_code == 200  # OK


@pytest.mark.asyncio
@pytest.mark.parametrize("ip_geolocation_data", test_data, indirect=True)
async def test_delete_geolocation_by_url(
    test_client_v1, ip_geolocation_data, populate_db_with_ip_geolocation_data
):
    """
    Verify that the /geolocation endpoint returns a 200 status code and reports 'ok' status.
    """
    response = await test_client_v1.delete("/geolocation/", params={"url": ip_geolocation_data.url})
    assert response.status_code == 200  # OK


@pytest.mark.asyncio
async def test_delete_geolocation_by_ip_address_not_found(test_client_v1):
    """
    Should return 404 if IP not found.
    """
    response = await test_client_v1.delete("/geolocation/", params={"ip_address": "8.8.8.8"})
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_geolocation_by_url_not_found(test_client_v1):
    """
    Should return 404 if URL not found.
    """
    response = await test_client_v1.delete("/geolocation/", params={"url": "https://notfound.com"})
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_geolocation_by_ip_and_url_422(test_client_v1):
    """
    Should return 422 if both ip_address and url are provided.
    """
    response = await test_client_v1.delete(
        "/geolocation/", params={"ip_address": "127.0.0.1", "url": "https://www.google.com/"}
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_delete_geolocation_by_zero_input_422(test_client_v1):
    """
    Should return 422 if neither ip_address nor url is provided.
    """
    response = await test_client_v1.delete("/geolocation/")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_delete_geolocation_by_ip_address_invalid_input(test_client_v1):
    """
    Should return 422 if ip_address is invalid.
    """
    response = await test_client_v1.delete(
        "/geolocation/", params={"ip_address": "999.999.999.999"}
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_delete_geolocation_by_url_invalid_input(test_client_v1):
    """
    Should return 422 if url is invalid.
    """
    response = await test_client_v1.delete("/geolocation/", params={"url": "not-a-url"})
    assert response.status_code == 422


@pytest.mark.asyncio
@pytest.mark.parametrize("ip_geolocation_data", test_data, indirect=True)
async def test_delete_geolocation_by_ip_address_database_down(
    test_client_v1, ip_geolocation_data, database_client_down
):
    """
    Verify that the /geolocation endpoint returns a 503 status code when the database is down.
    """
    response = await test_client_v1.delete(
        "/geolocation/", params={"ip_address": ip_geolocation_data.ip}
    )
    response_data = response.json()
    assert response.status_code == 503, f"Response: {response_data}"
    assert response_data["error"]["message"] == "Database unavailable", f"Response: {response_data}"
