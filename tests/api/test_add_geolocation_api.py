"""
API tests for geolocation endpoints to verify the application is running correctly.
"""

import pytest
from datetime import datetime
from app.domain.models.ip_data import Geolocation

test_data = [
    Geolocation(
        ip="127.0.0.1",
        url="https://www.google.com/",
        latitude=123.456,
        longitude=78.910,
        city="Test City",
        region="Test Region",
        country="Test Country",
        continent="Test Continent",
        postal_code="12345",
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
]


# Add geolocation by IP address
@pytest.mark.asyncio
@pytest.mark.parametrize("ip_geolocation_data", test_data, indirect=True)
async def test_add_geolocation_by_ip_address_success(test_client_v1, ip_geolocation_data):
    """
    Verify that the /geolocation endpoint returns a 200 status code and reports 'ok' status.
    """
    response = await test_client_v1.post(
        "/geolocation/", json={"ip_address": ip_geolocation_data.ip}
    )
    assert response.status_code == 201, f"Response: {response.json()}"
    response_data = response.json()
    assert response_data["status"] == "success"
    assert response_data["data"]["geolocation"]["ip"] == ip_geolocation_data.ip
    assert response_data["data"]["geolocation"]["latitude"] == ip_geolocation_data.latitude
    assert response_data["data"]["geolocation"]["longitude"] == ip_geolocation_data.longitude
    assert response_data["data"]["geolocation"]["city"] == ip_geolocation_data.city
    assert response_data["data"]["geolocation"]["region"] == ip_geolocation_data.region
    assert response_data["data"]["geolocation"]["country"] == ip_geolocation_data.country
    assert response_data["data"]["geolocation"]["continent"] == ip_geolocation_data.continent
    assert response_data["data"]["geolocation"]["postal_code"] == ip_geolocation_data.postal_code


@pytest.mark.asyncio
@pytest.mark.parametrize("ip_geolocation_data", test_data, indirect=True)
async def test_add_geolocation_by_ip_address_database_down(
    test_client_v1, ip_geolocation_data, database_client_down
):
    """
    Verify that the /geolocation endpoint returns a 503 status code when the database is down.
    """
    response = await test_client_v1.post(
        "/geolocation/", json={"ip_address": ip_geolocation_data.ip}
    )
    response_data = response.json()
    assert response.status_code == 503, f"Response: {response_data}"
    assert response_data["error"]["message"] == "Database unavailable", f"Response: {response_data}"


@pytest.mark.asyncio
@pytest.mark.parametrize("ip_geolocation_service", [False], indirect=True)
async def test_add_geolocation_by_ip_address_external_api_down(test_client_v1):
    """
    Verify that the /geolocation endpoint returns a 503 status code when the external API is down.
    """
    response = await test_client_v1.post("/geolocation/", json={"ip_address": "127.0.0.1"})
    response_data = response.json()
    assert response.status_code == 503, f"Response: {response_data}"
    assert response_data["error"]["message"] == "External unavailable", f"Response: {response_data}"


@pytest.mark.asyncio
async def test_add_geolocation_by_ip_address_not_found_geolocation_data(test_client_v1):
    """
    Verify that the /geolocation endpoint returns a 404 status code when the geolocation data is not found.
    """
    response = await test_client_v1.post("/geolocation/", json={"ip_address": "127.0.0.1"})
    assert response.status_code == 404
    response_data = response.json()
    assert (
        response_data["error"]["message"] == "IP data not found on external service"
    ), f"Response: {response_data}"


@pytest.mark.asyncio
@pytest.mark.parametrize("ip_geolocation_data", test_data, indirect=True)
async def test_add_geolocation_by_ip_address_and_url_invalid_input(
    test_client_v1, ip_geolocation_data
):
    """
    Verify that the /geolocation endpoint returns a 422 status code when the input is invalid.
    """
    response = await test_client_v1.post(
        "/geolocation/", json={"ip_address": ip_geolocation_data.ip, "url": ip_geolocation_data.url}
    )
    assert response.status_code == 422


@pytest.mark.asyncio
@pytest.mark.parametrize("ip_geolocation_data", test_data, indirect=True)
async def test_add_geolocation_by_ip_address_invalid_input(test_client_v1):
    """
    Verify that the /geolocation endpoint returns a 422 status code when the input is invalid.
    """
    response = await test_client_v1.post("/geolocation/", json={"ip_address": "257.255.255.255"})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_add_geolocation_by_zero_input(test_client_v1):
    """
    Verify that the /geolocation endpoint returns a 422 status code when the input is empty.
    """
    response = await test_client_v1.post("/geolocation/", json={})
    assert response.status_code == 422


# Add geolocation by URL
@pytest.mark.asyncio
@pytest.mark.parametrize("ip_geolocation_data", test_data, indirect=True)
async def test_add_geolocation_by_url_success(test_client_v1, ip_geolocation_data):
    """
    Verify that the /geolocation/url endpoint returns a 201 status code and correct data.
    """
    response = await test_client_v1.post("/geolocation/", json={"url": "https://www.google.com/"})
    assert response.status_code == 201, f"Response: {response.json()}"
    response_data = response.json()
    assert response_data["status"] == "success"
    assert response_data["data"]["geolocation"]["ip"] == ip_geolocation_data.ip
    assert response_data["data"]["geolocation"]["url"] == ip_geolocation_data.url
    assert response_data["data"]["geolocation"]["latitude"] == ip_geolocation_data.latitude
    assert response_data["data"]["geolocation"]["longitude"] == ip_geolocation_data.longitude
    assert response_data["data"]["geolocation"]["city"] == ip_geolocation_data.city
    assert response_data["data"]["geolocation"]["region"] == ip_geolocation_data.region
    assert response_data["data"]["geolocation"]["country"] == ip_geolocation_data.country
    assert response_data["data"]["geolocation"]["continent"] == ip_geolocation_data.continent
    assert response_data["data"]["geolocation"]["postal_code"] == ip_geolocation_data.postal_code


@pytest.mark.asyncio
async def test_add_geolocation_by_url_invalid_input(test_client_v1):
    """
    Verify that the /geolocation endpoint returns a 422 status code when the input is invalid.
    """
    response = await test_client_v1.post("/geolocation/", json={"url": "invalid-url"})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_add_geolocation_by_url_and_ip_address_invalid_input(test_client_v1):
    """
    Verify that the /geolocation endpoint returns a 422 status code when the input is invalid.
    """
    response = await test_client_v1.post(
        "/geolocation/", json={"url": "invalid-url", "ip_address": "127.0.0.1"}
    )
    assert response.status_code == 422
