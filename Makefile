.PHONY: setup lint test unit-test api-test integration-test e2e-test docker-build docker-up docker-down docker-test clean coverage

# Environment variables
DOCKER_COMPOSE = docker-compose
DOCKER_COMPOSE_TEST = docker-compose -f docker-compose.test.yml
POETRY = poetry

# Main targets
setup:
	$(POETRY) install

lint:
	$(POETRY) run flake8 app tests
	$(POETRY) run black --check app tests
	$(POETRY) run mypy app tests
	$(POETRY) run bandit -r app/ --exclude app/tests
	$(POETRY) run safety scan

test:
	$(POETRY) run pytest tests

unit-test:
	$(POETRY) run pytest tests/unit

api-test:
	$(POETRY) run pytest tests/api

integration-test:
	$(POETRY) run pytest tests/integration

coverage:
	$(POETRY) run pytest tests/unit --cov=app --cov-report=xml:coverage-unit.xml
	$(POETRY) run pytest tests/api --cov=app --cov-report=xml:coverage-api.xml
	$(POETRY) run pytest tests/integration --cov=app --cov-report=xml:coverage-integration.xml
	$(POETRY) run coverage combine coverage-*.xml
	$(POETRY) run coverage report
	$(POETRY) run coverage xml
	$(POETRY) run coverage html

# Docker commands
docker-build:
	$(DOCKER_COMPOSE) build

docker-up:
	$(DOCKER_COMPOSE) up -d

docker-down:
	$(DOCKER_COMPOSE) down

# Docker test commands
docker-test:
	$(DOCKER_COMPOSE_TEST) up --build --abort-on-container-exit
	$(DOCKER_COMPOSE_TEST) down

# Clean up commands
clean:
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov
	rm -rf coverage.xml
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name "coverage-*.xml" -delete
