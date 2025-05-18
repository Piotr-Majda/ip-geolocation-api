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
poetry run pytest             # Run all tests
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
make populate-test-data
```

**With Poetry:**

```bash
poetry run python scripts/populate_test_data.py
```

This will insert sample geolocation records into your database so you can immediately interact with the API.

## Troubleshooting

### Database Connection Issues

- Verify database credentials in `.env` file
- Check if database container is running: `docker-compose ps`
- Check database logs: `docker-compose logs db`
- The application implements retry mechanisms for temporary database outages

### IPStack API Issues

- Verify your API key is valid and has sufficient quota
- The application caches previously fetched data to reduce API calls
- Check network connectivity to IPStack servers
- The application will serve cached data when IPStack is unavailable

### API Error Codes

- `400` - Invalid input (malformed IP/URL)
- `404` - Geolocation data not found
- `429` - Rate limit exceeded for IPStack API
- `500` - Internal server error
- `503` - External service unavailable

## Development

1. Install dependencies locally:

```bash
make setup
# or
poetry install
```

2. Run in development mode:

```bash
poetry run uvicorn app.main:app --reload
```

3. Build for production:

```bash
make docker-build
make docker-up
```

## License

MIT
