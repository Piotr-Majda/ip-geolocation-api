"""
Global pytest fixtures for the IP Geolocation API tests.
"""
import os
import pytest
import httpx
from fastapi.testclient import TestClient
from dotenv import load_dotenv

# Import the FastAPI app
from app.main import app

# Load environment variables
load_dotenv()

# Create a TestClient instance


@pytest.fixture
def test_client():
    """
    Create a TestClient for making API requests without running a server.

    This is useful for unit tests or when you don't want to start a real server.
    """
    return TestClient(app)


@pytest.fixture(scope="session")
def api_base_url():
    """
    Get the base URL for API tests.

    This will use the TEST_API_BASE_URL environment variable if set,
    otherwise it defaults to http://localhost:8000
    """
    return os.getenv("TEST_API_BASE_URL", "http://localhost:8000")


@pytest.fixture
def api_client(api_base_url):
    """
    Create an httpx.Client for making API requests.

    This client is configured with a base URL and reasonable timeouts.
    """
    with httpx.Client(base_url=api_base_url, timeout=10.0) as client:
        yield client
