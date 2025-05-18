# Setting Up the IP Geolocation API

This guide explains how to set up and run the IP Geolocation API on your local machine.

## Prerequisites

1. **Docker and Docker Compose**: Required for containerization
2. **Python 3.13**: Required if running locally without Docker
3. **IPStack API Key**: Register at https://ipstack.com/ to get a free API key

## Quick Start with Docker

1. **Clone the repository**:

   ```bash
   git clone https://github.com/yourusername/ip-geolocation-api.git
   cd ip-geolocation-api
   ```

2. **Create .env file**:
   Create a `.env` file in the root directory with the following content:

   ```
   DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/geolocation
   IPSTACK_API_KEY=your_ipstack_api_key_here
   APP_LOG_FORMAT=text|json
   ```

   Replace `your_ipstack_api_key_here` with your actual IPStack API key.

3. **Build and start the containers**:

   ```bash
   make docker-build
   make docker-up
   ```

   Or, using Docker Compose directly:

   ```bash
   docker-compose up -d
   ```

4. **Access the API**:
   - API will be available at: http://localhost:8000
   - API documentation: http://localhost:8000/api/v1/docs
   - OpenAPI spec: http://localhost:8000/api/v1/openapi.json
   - Health check: http://localhost:8000/health

## Running Locally (without Docker)

1. **Set up Python environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install poetry
   poetry install
   ```

2. **Set up PostgreSQL**:
   Install and configure PostgreSQL locally, or use Docker just for the database:

   ```bash
   docker-compose up -d db
   ```

3. **Create .env file**:
   Create a `.env` file with your local configuration:

   ```
   DATABASE_URL=postgresql://postgres:postgres@localhost:5432/geolocation
   IPSTACK_API_KEY=your_ipstack_api_key_here
   LOG_LEVEL=INFO
   ```

4. **Run the application**:
   ```bash
   poetry run uvicorn app.main:app --reload
   ```

## Project Structure

The project follows the Domain-Driven Design (DDD) architecture:

```
app/
├── domain/           # Domain models and business logic
├── application/      # Use cases and application services
├── infrastructure/   # External interfaces implementations
├── interfaces/       # API routes and controllers
└── main.py           # Application entry point
```

## Running Tests

You can run tests using the Makefile or Poetry:

**With Makefile:**

```bash
make test           # Run all tests
make unit-test      # Run unit tests
make api-test       # Run API tests
make integration-test # Run integration tests
```

**With Poetry:**

```bash
poetry run pytest             # Run all tests
poetry run pytest tests/api   # Run API tests
poetry run pytest tests/unit  # Run unit tests
poetry run pytest tests/integration # Run integration tests
```

**With Docker:**

```bash
docker-compose exec api pytest
```
