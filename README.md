# IP Geolocation API

## Project Overview

A RESTful API service that stores and manages geolocation data based on IP addresses or URLs. The service fetches geolocation data from IPStack and provides endpoints to add, delete, and retrieve this information.

## Features

- Store IP/URL geolocation data in database
- Fetch geolocation data from external provider (IPStack)
- RESTful API with JSON request/response format
- Fault-tolerant design with proper error handling
- Comprehensive test coverage

## Architecture

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│             │      │             │      │             │
│   Client    │─────▶│ REST API    │─────▶│  Database   │
│             │      │             │      │             │
└─────────────┘      └──────┬──────┘      └─────────────┘
                            │
                            ▼
                     ┌─────────────┐
                     │   IPStack   │
                     │     API     │
                     │             │
                     └─────────────┘
```

## API Endpoints

- `GET /api/v1/geolocation/` - Get geolocation data for IP/URL (query params)
- `POST /api/v1/geolocation/` - Add new geolocation data
- `DELETE /api/v1/geolocation/` - Delete geolocation data
- `GET /health` - Health check
- `GET /api/v1/docs` - API documentation (Swagger UI)
- `GET /api/v1/openapi.json` - OpenAPI spec

## Technology Stack

### Backend

- **FastAPI**: Modern, high-performance framework with built-in validation
- **SQLAlchemy**: ORM for database interactions
- **Pydantic**: For data validation (comes integrated with FastAPI)

### Database

- **PostgreSQL**: Robust relational database

### Infrastructure

- **Docker & Docker Compose**: For containerization and easy deployment
- **Gunicorn + Uvicorn**: For production deployment

### Testing

- **Pytest**: For unit, API, and integration tests
- **HTTPx**: For async HTTP API testing
- **pytest-cov**: For test coverage reporting
- **In-memory DB & Mocked External Services**: All tests use an in-memory database and mock the external IPStack service for isolation and speed

### Utilities

- **Python-dotenv**: For environment variable management

## Setup Instructions

### Prerequisites

- Docker and Docker Compose
- IPStack API key (https://ipstack.com/)
- Python 3.13+ and Poetry (for local development)

### Environment Variables

Create a `.env` file with the following variables:

```
DATABASE_URL=your_database_url
IPSTACK_API_KEY=your_api_key_here
APP_LOG_FORMAT=text|json
```

### Installation & Running

#### Using Docker (Recommended for Production)

1. Clone the repository

```bash
git clone https://github.com/yourusername/ip-geolocation-api.git
cd ip-geolocation-api
```

2. Create a `.env` file as above
3. Build and start the application

```bash
make docker-build
make docker-up
```

4. Access the API:
   - http://localhost:8000
   - Docs: http://localhost:8000/api/v1/docs
   - OpenAPI: http://localhost:8000/api/v1/openapi.json
   - Health: http://localhost:8000/health

#### Local Development with Poetry

1. Install dependencies

```bash
make setup
# or
poetry install
```

2. Start the database (locally or with Docker)

```bash
docker-compose up -d db
```

3. Run the application

```bash
poetry run uvicorn app.main:app --reload
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
poetry run pytest tests       # Run all tests
poetry run pytest tests/api   # Run API tests
poetry run pytest tests/unit  # Run unit tests
poetry run pytest tests/integration # Run integration tests
```

**With Docker:**

```bash
docker-compose exec api pytest
```

- **Note:** All tests use an in-memory database and mock the external IPStack service for fast, isolated, and reliable test runs.

## Populating the Database with Sample Data

To quickly populate the database with sample geolocation data for manual testing or QA, use the provided script or Makefile target:

**With Makefile:**

```bash
make migrate-seed-docker  # Run migrations and seed the database inside Docker
```

**Or, separately:**

```bash
make migrate-docker      # Run migrations inside Docker
make  seed-docker         # Seed the database inside Docker
```

**With Poetry (local development):**

```bash
make migrate-seed        # Run migrations and seed the database locally
# or separately
make migrate             # Run migrations locally
make seed                # Seed the database locally
```

This will insert sample geolocation records into your database so you can immediately interact with the API.

## Validating Seed Data and API

After seeding, you can use Makefile targets to validate the data in your database and test the API endpoints.

### Select Data from the Database

- **Show a sample of records:**
  ```bash
  make select-data-limit LIMIT=5
  ```
- **Show all records:**
  ```bash
  make select-data-all
  ```
- **Count records:**
  ```bash
  make select-data-count
  ```
- **Select by IP:**
  ```bash
  make select-data-ip IP=1.2.3.4
  ```

### Test API Endpoints with curl

- **GET geolocation by IP:**
  ```bash
  make curl-get-ip IP=1.2.3.4
  ```
- **GET geolocation by URL:**
  ```bash
  make curl-get-url URL=https://www.google.com
  ```
- **POST (add) geolocation by IP:**
  ```bash
  make curl-add-ip IP=1.2.3.4
  ```
- **POST (add) geolocation by URL:**
  ```bash
  make curl-add-url URL=https://www.google.com
  ```
- **DELETE geolocation by IP:**
  ```bash
  make curl-delete-ip IP=1.2.3.4
  ```
- **DELETE geolocation by URL:**
  ```bash
  make curl-delete-url URL=https://www.google.com
  ```

These commands allow you to quickly verify that your database is populated and your API is functioning as expected.

## License

MIT