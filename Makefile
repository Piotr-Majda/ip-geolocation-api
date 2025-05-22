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

format:
	$(POETRY) run black app tests
	$(POETRY) run isort app tests

security-scan:
	$(POETRY) run bandit -r app/ --exclude app/tests
	$(POETRY) run safety scan $(SAFETY_KEY) --ci

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

test-coverage:
	$(POETRY) run pytest tests --cov=app --cov-report=xml --cov-report=html
	$(POETRY) run coverage report

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

docker-down-fresh:
	$(DOCKER_COMPOSE) down -v --remove-orphans --rmi all

# Clean up commands

ifeq ($(OS),Windows_NT)
clean:
	if exist .pytest_cache rmdir /s /q .pytest_cache
	if exist .coverage del /f /q .coverage
	if exist htmlcov del /f /q htmlcov
	if exist coverage.xml del /f /q coverage.xml
	if exist security-reports rmdir /s /q security-reports
	for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
	for /d /r . %%d in (*.egg-info) do @if exist "%%d" rd /s /q "%%d"
	del /s /q *.pyc
	del /s /q *.pyo
	del /s /q *.pyd
	del /s /q coverage-*.xml
else
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
endif

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

IP ?= 192.168.1.1
URL ?= https://www.google.com
LIMIT ?= 5

# select data from database
select-data-limit:
	$(DOCKER_COMPOSE) exec db psql -U postgres -d geolocation -c "SELECT * FROM ip_geolocation LIMIT $(LIMIT);"

select-data-all:
	$(DOCKER_COMPOSE) exec db psql -U postgres -d geolocation -c "SELECT * FROM ip_geolocation;"

select-data-count:
	$(DOCKER_COMPOSE) exec db psql -U postgres -d geolocation -c "SELECT COUNT(*) FROM ip_geolocation;"

select-data-ip:
	$(DOCKER_COMPOSE) exec db psql -U postgres -d geolocation -c "SELECT * FROM ip_geolocation WHERE ip = '$(IP)';"

# curl commands
curl-get-ip:
	$(DOCKER_COMPOSE) exec api curl -X GET "http://localhost:8000/api/v1/geolocation/?ip_address=$(IP)"

curl-get-url:
	$(DOCKER_COMPOSE) exec api curl -X GET "http://localhost:8000/api/v1/geolocation/?url=$(URL)"

curl-add-ip:
	$(DOCKER_COMPOSE) exec api curl -X POST "http://localhost:8000/api/v1/geolocation/" -H "Content-Type: application/json" -d '{"ip_address": "$(IP)"}'

curl-add-url:
	$(DOCKER_COMPOSE) exec api curl -X POST "http://localhost:8000/api/v1/geolocation/" -H "Content-Type: application/json" -d '{"url": "$(URL)"}'

curl-delete-ip:
	$(DOCKER_COMPOSE) exec api curl -X DELETE "http://localhost:8000/api/v1/geolocation/?ip_address=$(IP)"

curl-delete-url:
	$(DOCKER_COMPOSE) exec api curl -X DELETE "http://localhost:8000/api/v1/geolocation/?url=$(URL)"
