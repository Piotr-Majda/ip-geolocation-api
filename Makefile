.PHONY: setup lint test unit-test api-test integration-test e2e-test docker-build docker-up docker-down docker-test clean coverage security-scan

# Include .env file if it exists
-include .env

# Environment variables
DOCKER_COMPOSE = docker-compose
POETRY = poetry
SAFETY_KEY = $(if $(SAFETY_API_KEY),--key $(SAFETY_API_KEY),)
IPSTACK_KEY = $(if $(IPSTACK_API_KEY),--api-key $(IPSTACK_API_KEY),)

# Main targets
setup:
	$(POETRY) install

lint:
	$(POETRY) run flake8 app tests
	$(POETRY) run black --check app tests
	$(POETRY) run mypy app tests

security-scan:
	$(POETRY) run bandit -r app/ --exclude app/tests
	$(POETRY) run safety scan $(SAFETY_KEY)

lint-all: lint security-scan

test:
	$(POETRY) run pytest tests

unit-test:
	$(POETRY) run pytest tests/unit

integration-test:
	$(POETRY) run pytest tests/integration

# real api test
integration-real-api-test:
	$(POETRY) run pytest tests/integration --use-real-api $(IPSTACK_KEY)

api-test:
	$(POETRY) run pytest tests/api

coverage:
	$(POETRY) run pytest tests/unit --cov=app --cov-report=xml:coverage-unit.xml
	$(POETRY) run pytest tests/api --cov=app --cov-report=xml:coverage-api.xml
	$(POETRY) run pytest tests/integration --cov=app --cov-report=xml:coverage-integration.xml
	$(POETRY) run coverage combine coverage-*.xml
	$(POETRY) run coverage report
	$(POETRY) run coverage xml
	$(POETRY) run coverage html

# Security report generation
security-report:
	mkdir -p security-reports
	$(POETRY) run bandit -r app/ --exclude app/tests -f json -o security-reports/bandit-report.json || true
	$(POETRY) run safety scan --json $(SAFETY_KEY) > security-reports/safety-report.json || true
	@echo "Security reports generated in security-reports directory"

# Docker commands
docker-build:
	$(DOCKER_COMPOSE) build

docker-up:
	$(DOCKER_COMPOSE) up -d

docker-down:
	$(DOCKER_COMPOSE) down

# Clean up commands
clean:
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov
	rm -rf coverage.xml
	rm -rf security-reports
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name "coverage-*.xml" -delete

# migration commands
migrate:
	$(POETRY) run alembic upgrade head

migrate-docker:
	$(DOCKER_COMPOSE) exec -it api alembic upgrade head

# seed commands
seed:
	$(POETRY) run python scripts/seed.py

seed-docker:
	$(DOCKER_COMPOSE) exec -it api python scripts/seed.py

# migrate and seed commands
migrate-seed-docker: migrate-docker seed-docker

migrate-seed: migrate seed
