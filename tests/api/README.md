# API Tests

This directory contains tests that verify the behavior and robustness of the API endpoints for the IP Geolocation service.

## Testing Strategy

- **In-Memory Database:**

  - All tests run against a fresh, in-memory SQLite database to ensure isolation and repeatability.
  - Database is reset between tests to avoid state leakage.

- **Mocked External Dependencies:**

  - The external IP geolocation service is fully mocked using dependency injection and test fixtures.
  - This allows us to simulate both successful and failure scenarios (e.g., service unavailable, not found).

- **End-to-End Flow Validation:**

  - Tests cover the full flow from HTTP API request, through application and domain logic, to database and external service interactions.
  - Both positive (success) and negative (error, invalid input) cases are validated.

- **Tools and Fixtures:**
  - Uses `pytest` and `httpx.AsyncClient` for async API testing.
  - Common fixtures provide test clients, database setup/teardown, and external service mocks.

## What We Test

- **Status Codes:**
  - Ensure correct HTTP status codes for all scenarios (success, validation error, not found, dependency errors).
- **Response Structure:**
  - Validate that responses match the expected schema and contain the correct data.
- **Input Validation:**
  - Test both valid and invalid inputs, including mutual exclusivity and required fields.
- **Error Handling:**
  - Simulate and verify behavior when the database or external service is down or returns errors.

## Directory Structure

- `test_add_geolocation.py` - Tests for POST (add) endpoints
- `test_get_geolocation.py` - Tests for GET (retrieve) endpoints
- `test_delete_geolocation.py`- Tests for DELETE (remove) endpoints
- `test_health.py` - Tests for health check endpoints

## How to Run

Run all API tests with:

```bash
pytest tests/api/
or
make api-test
or
poetry run pytest test/api
```
---

For more details, see the individual test files and fixtures in this directory.
