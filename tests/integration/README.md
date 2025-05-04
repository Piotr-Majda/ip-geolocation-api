# Integration Tests

This directory contains integration tests that verify how components work together.

## Structure

- `test_repository_db.py` - Tests for repository interactions with a database
- `test_api_external.py` - Tests for interactions with external APIs

## Writing Integration Tests

- Use real instances rather than mocks
- Test multiple components working together
- Use database fixtures with rollback support
- Reset state between tests
- Tests should be idempotent 