"""
API tests for health endpoints to verify the application is running correctly.
"""
import pytest


def test_health_endpoint(test_client):
    """
    Verify that the /health endpoint returns a 200 status code and reports 'ok' status.

    This is a basic test to confirm the API is running and responding.
    """
    # When making a GET request to the health endpoint
    response = test_client.get("/health")

    # Then the response should have a 200 status code
    assert response.status_code == 200

    # And the response should contain a status of 'ok'
    data = response.json()
    assert data["status"] == "ok"

    # And all components should report 'ok' status
    for component_name, component_info in data["components"].items():
        assert component_info["status"] == "ok", f"Component {component_name} is not OK"


def test_root_endpoint(test_client):
    """
    Verify that the root endpoint (/) returns a 200 status code.

    This tests that the base URL of the API is responding.
    """
    # When making a GET request to the root endpoint
    response = test_client.get("/")

    # Then the response should have a 200 status code
    assert response.status_code == 200

    # And the response should contain a welcome message
    data = response.json()
    assert "message" in data
    assert "Welcome" in data["message"]


@pytest.mark.parametrize(
    "endpoint",
    [
        "/docs",
        "/openapi.json",
    ],
)
def test_documentation_endpoints(test_client, endpoint):
    """
    Verify that documentation endpoints are accessible.

    This confirms that Swagger docs and OpenAPI JSON schema are available.
    """
    # When making a GET request to documentation endpoints
    response = test_client.get(endpoint)

    # Then the response should have a 200 status code
    assert response.status_code == 200
