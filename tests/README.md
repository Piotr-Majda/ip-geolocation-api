# IP Geolocation API Tests

This directory contains tests for the IP Geolocation API.

## Test Structure

- `api/`: API tests (HTTP requests to test endpoints)
- `unit/`: Unit tests (will be added)
- `integration/`: Integration tests (will be added)

## Running Tests

### Test Approaches

There are two ways to test the API:

1. **Using TestClient (recommended for development)**: 
   - Tests run against the API directly in the same process
   - Faster, no need to start a separate server
   - Automatically used when running `pytest`

2. **Against a running server**:
   - Tests run against an actual server
   - Good for deployment verification
   - Requires manually starting the server

### Running Tests with TestClient

To run all API tests without starting a server:

```bash
# Run all tests
poetry run pytest
```

### Running Tests Against a Real Server

To run API tests against a running local instance:

```bash
# Start the API in one terminal
poetry run api

# Run API tests in another terminal using the api_client fixture
poetry run pytest tests/api -k "not test_client"
```

You can specify a different API URL by setting the `TEST_API_BASE_URL` environment variable:

```bash
# Windows PowerShell
$env:TEST_API_BASE_URL="http://localhost:8000"; poetry run pytest tests/api

# Linux/Mac
TEST_API_BASE_URL="http://localhost:8000" poetry run pytest tests/api
```

### Running With Coverage

```bash
poetry run pytest --cov=app
```

## Writing Tests

Follow these guidelines when writing tests:

1. Use descriptive test names that explain what is being tested
2. Use the Given-When-Then pattern in test docstrings and comments
3. Make use of fixtures in `conftest.py` for common setup
4. Keep tests independent and idempotent (can be run multiple times)
5. For API tests, prefer using `test_client` fixture unless you specifically need to test against a running server

# Test Structure for IP Geolocation API

This directory contains test files organized to match the application structure, following TDD and BDD principles.

## Directory Structure

```
tests/
├── unit/                       # Unit tests for individual components
│   ├── domain/                 # Tests for domain entities and logic
│   │   ├── models/             # Tests for domain model classes
│   │   │   ├── test_ip.py
│   │   │   ├── test_geolocation.py
│   │   ├── repositories/       # Tests for repository interfaces
│   │   │   ├── test_geolocation_repository.py
│   │   ├── services/           # Tests for domain services
│   │   │   ├── test_geolocation_service.py
│   │   ├── application/            # Tests for application use cases
│   │   │   ├── use_cases/
│   │   │   │   ├── test_get_geolocation.py
│   │   │   │   ├── test_add_geolocation.py
│   │   │   │   ├── test_delete_geolocation.py
│   │   ├── infrastructure/         # Tests for infrastructure implementations
│   │   │   ├── database/
│   │   │   │   ├── test_models.py
│   │   │   │   ├── repositories/
│   │   │   │       ├── test_sqlalchemy_geolocation_repository.py
│   │   │   ├── external/
│   │   │   │   ├── test_ipstack_client.py
│   │   │   ├── cache/
│   │   │   │   ├── test_redis_cache.py
│   │   ├── interfaces/             # Tests for API routes and controllers
│   │   │   ├── api/
│   │   │   │   ├── routes/
│   │   │   │   │   ├── test_geolocation_routes.py
│   │   │   │   │   ├── test_health_routes.py
│   │   ├── conftest.py             # Global pytest fixtures
├── integration/                # Integration tests between components
│   ├── test_repository_db.py   # Tests repositories with actual DB
│   ├── test_api_external.py    # Tests external API integrations
│   ├── conftest.py             # Integration test fixtures
├── api/                        # API tests (HTTP requests)
│   ├── test_geolocation_api.py # Tests complete API endpoints
│   ├── conftest.py             # API test fixtures
├── features/                   # BDD feature specifications
│   ├── geolocation.feature     # Gherkin feature file
│   ├── steps/                  # Step definitions for BDD tests
│   │   ├── test_geolocation_steps.py
├── performance/                # Performance and load tests
│   ├── test_api_performance.py # Simple load tests
```

## Test Types

### Unit Tests

Unit tests focus on testing individual components in isolation. Dependencies are mocked.

Example for IP domain model:
```python
# tests/unit/domain/models/test_ip.py
import pytest
from app.domain.models.ip import IP, InvalidIPError

def test_valid_ipv4_creation():
    ip = IP("192.168.1.1")
    assert ip.value == "192.168.1.1"
    assert ip.is_ipv4 is True

def test_invalid_ip_raises_error():
    with pytest.raises(InvalidIPError):
        IP("999.168.1.1")
```

### Integration Tests

Integration tests verify that components work correctly together.

Example testing repository with actual database:
```python
# tests/integration/test_repository_db.py
import pytest
from app.domain.models.ip import IP
from app.domain.models.geolocation import Geolocation
from app.infrastructure.database.repositories.sqlalchemy_geolocation_repository import SqlAlchemyGeolocationRepository

@pytest.mark.integration
def test_save_and_retrieve_geolocation(db_session):
    # Given
    repository = SqlAlchemyGeolocationRepository(db_session)
    ip = IP("8.8.8.8")
    geo = Geolocation(
        ip=ip,
        country_name="United States",
        country_code="US",
        city="Mountain View",
        latitude=37.4056,
        longitude=-122.0775
    )
    
    # When - save to DB
    repository.save(geo)
    db_session.commit()
    
    # Then - retrieve from DB
    retrieved = repository.get_by_ip(ip)
    assert retrieved is not None
    assert retrieved.country_name == "United States"
    assert retrieved.city == "Mountain View"
```

### API Tests

API tests make actual HTTP requests to the running API.

Example:
```python
# tests/api/test_geolocation_api.py
import pytest
import requests

@pytest.mark.api
def test_get_geolocation_for_valid_ip(api_base_url):
    # Given a running API
    # When requesting geolocation for a valid IP
    response = requests.get(f"{api_base_url}/api/geolocations/8.8.8.8")
    
    # Then response should be successful with correct data
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["ip"] == "8.8.8.8"
    assert "country_name" in data
    assert "city" in data
```

### BDD Tests

BDD tests connect Gherkin feature files with implementation.

Example feature file:
```gherkin
# tests/features/geolocation.feature
Feature: IP Geolocation API
  As an API user
  I want to get geolocation data for IP addresses
  So that I can display location information to my users

  Scenario: Get geolocation for a valid IP address
    Given the API is running
    When I request geolocation data for IP "8.8.8.8"
    Then the response status code should be 200
    And the response should include geolocation data
    And the data should include country and city information
```

With implementation:
```python
# tests/features/steps/test_geolocation_steps.py
from pytest_bdd import given, when, then, parsers
import requests

@given("the API is running")
def api_running(api_base_url):
    response = requests.get(f"{api_base_url}/health")
    assert response.status_code == 200

@when(parsers.parse('I request geolocation data for IP "{ip}"'))
def request_geolocation(api_base_url, ip):
    response = requests.get(f"{api_base_url}/api/geolocations/{ip}")
    return response

@then(parsers.parse('the response status code should be {status:d}'))
def check_status_code(response, status):
    assert response.status_code == status

@then("the response should include geolocation data")
def check_geolocation_data(response):
    data = response.json()["data"]
    assert data is not None
    assert "ip" in data

@then("the data should include country and city information")
def check_country_city_data(response):
    data = response.json()["data"]
    assert "country_name" in data
    assert "city" in data
```

## Fixtures

Shared fixtures are in conftest.py files at appropriate levels:

```python
# tests/conftest.py - Global fixtures
import pytest
from app.domain.models.ip import IP
from app.domain.models.geolocation import Geolocation

@pytest.fixture
def sample_ip():
    return IP("8.8.8.8")

@pytest.fixture
def sample_geolocation(sample_ip):
    return Geolocation(
        ip=sample_ip,
        country_name="United States",
        country_code="US",
        city="Mountain View",
        latitude=37.4056,
        longitude=-122.0775
    )
```

```python
# tests/integration/conftest.py - Database fixtures
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, clear_mappers
from app.infrastructure.database.models import Base

@pytest.fixture
def in_memory_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)

@pytest.fixture
def db_session(in_memory_db):
    session_factory = sessionmaker(bind=in_memory_db)
    session = session_factory()
    yield session
    session.rollback()
    session.close()
```
