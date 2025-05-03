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
- `GET /api/geolocations/:ip` - Get geolocation data for IP/URL
- `POST /api/geolocations` - Add new geolocation data
- `DELETE /api/geolocations/:ip` - Delete geolocation data

## Technology Stack

### Backend
- **FastAPI**: Modern, high-performance framework with built-in validation
- **SQLAlchemy**: ORM for database interactions 
- **Pydantic**: For data validation (comes integrated with FastAPI)

### Database
- **PostgreSQL**: Robust relational database
- **Redis**: For caching IPStack responses to reduce API calls

### Infrastructure
- **Docker & Docker Compose**: For containerization and easy deployment
- **Gunicorn + Uvicorn**: For production deployment

### Testing
- **Pytest**: For unit and integration tests
- **Pytest-cov**: For test coverage reporting
- **HTTPx**: For testing HTTP requests

### Utilities
- **Requests**: For calling the IPStack API
- **Python-dotenv**: For environment variable management

## Setup Instructions

### Prerequisites
- Docker and Docker Compose
- IPStack API key (https://ipstack.com/)
- Python 3.13+ and Poetry (for local development)

### Environment Variables
Create a `.env` file with the following variables:
```
IPSTACK_API_KEY=your_api_key_here
DATABASE_URL=your_database_url
PORT=8000
```

### Installation

#### Using Docker (Recommended for Production)
1. Clone the repository
```bash
git clone https://github.com/yourusername/ip-geolocation-api.git
cd ip-geolocation-api
```

2. Start the application using Docker Compose
```bash
docker-compose up -d
```

#### Local Development with Poetry
1. Install dependencies using Poetry
```bash
# Windows
make setup
# or
poetry install
```

## Running the Application
The application will be available at http://localhost:8000

## Testing

### Using Makefile Commands
We provide several commands through Makefile (or make.bat on Windows) to simplify development:

```bash
# Run all tests locally
make test

# Run specific test types
make unit-test
make api-test
make integration-test

# Run lint checks
make lint

# Run tests in Docker (API and integration tests)
make docker-test

# Start Docker environment
make docker-up

# Stop Docker environment
make docker-down
```

### Manual Testing Commands

#### Local Testing
```bash
# Run all tests
poetry run pytest tests

# Run specific test directories
poetry run pytest tests/unit
poetry run pytest tests/api
poetry run pytest tests/integration
```

#### Docker Testing
```bash
# Run API and integration tests in a production-like environment
docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit
```

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
pip install -r requirements.txt
```

2. Run in development mode:
```bash
# For FastAPI
uvicorn app.main:app --reload
```

3. Build for production:
```bash
# Install production WSGI/ASGI servers
pip install gunicorn uvicorn

# Run with gunicorn and uvicorn workers
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## License
MIT

