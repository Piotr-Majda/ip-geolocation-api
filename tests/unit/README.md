# Unit Tests

This directory contains unit tests that test individual components in isolation.

## Structure

- `domain/` - Tests for domain models, repositories, and services
- `application/` - Tests for application use cases
- `infrastructure/` - Tests for infrastructure implementations
- `interfaces/` - Tests for API routes and controllers

## Writing Unit Tests

- Keep unit tests isolated - dependencies should be mocked
- Test one component at a time
- Follow the Given-When-Then pattern
- Use descriptive test names 