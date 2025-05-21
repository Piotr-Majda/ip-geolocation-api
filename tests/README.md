# Test Suite Overview

This directory contains all test suites for the project. Use this README as the main entry point for test documentation.

## Test Types

- [Unit Tests](unit/README.md)

  - Test individual components in isolation using mocks. Each test targets a single function, class, or method. See `unit/README.md` for details.

- [Integration Tests](integration/README.md)

  - Verify how multiple components work together, including real database or external API interactions. See `integration/README.md` for details.

- [API Tests](api/README.md)
  - Validate the behavior and robustness of the API endpoints, including input validation, error handling, and end-to-end flows. See `api/README.md` for details.

## Testing Approach

- **Isolation:** External services are mocked, and database integration tests use an in-memory SQLite database for fast, isolated runs
- **Integration with Real API** Some integration tests require access to the real external API and are skipped by default. To run these tests, use the --use-real-api flag
- **Repeatability:** The database is reset between tests to ensure clean state.
- **Coverage:** Both positive and negative scenarios are tested, including error and edge cases.
- **Fixtures:** Common test fixtures are used for setup and teardown.

## Running Tests

Use the Makefile from the project root to run tests
Default coverage report on terminal will be displayed

```bash
make test                        # Run all tests
make unit-test                   # Run only unit tests
make integration-test            # Run only integration tests
make api-test                    # Run only API tests
make integration-real-api-test   # Run only integration tests with real api
```

Or run tests directly with pytest:

```bash
poetry run pytest tests/unit
poetry run pytest tests/integration
poetry run pytest tests/api
poetry run pytest tests/integration --use-real-api --api-key <YOUR_IPSTACK_KEY>
```

## Test Coverage

To run all test with generating coverage report:

```bash
make test-coverage
```

This will run all test suites and produce coverage reports in XML and HTML formats.

---

For more details, see the README files in each test subdirectory:

- [Unit Tests](unit/README.md)
- [Integration Tests](integration/README.md)
- [API Tests](api/README.md)
