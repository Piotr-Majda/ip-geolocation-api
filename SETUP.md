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
   PORT=8000
   DATABASE_URL=postgresql://postgres:postgres@db:5432/geolocation
   REDIS_URL=redis://redis:6379/0
   IPSTACK_API_KEY=your_ipstack_api_key_here
   LOG_LEVEL=INFO
   ```
   Replace `your_ipstack_api_key_here` with your actual IPStack API key.

3. **Build and start the containers**:
   ```bash
   docker-compose up -d
   ```

4. **Access the API**:
   - API will be available at: http://localhost:8000
   - API documentation: http://localhost:8000/docs
   - OpenAPI spec: http://localhost:8000/openapi.json
   - Health check: http://localhost:8000/health

## Running Locally (without Docker)

1. **Set up Python environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Set up PostgreSQL and Redis**:
   Install and configure PostgreSQL and Redis locally, or use Docker just for these services:
   ```bash
   docker-compose up -d db redis
   ```

3. **Create .env file**:
   Create a `.env` file with your local configuration:
   ```
   PORT=8000
   DATABASE_URL=postgresql://postgres:postgres@localhost:5432/geolocation
   REDIS_URL=redis://localhost:6379/0
   IPSTACK_API_KEY=your_ipstack_api_key_here
   LOG_LEVEL=INFO
   ```

4. **Run the application**:
   ```bash
   uvicorn app.main:app --reload
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

To run tests using Docker:
```bash
docker-compose exec api pytest
```

Or locally:
```bash
pytest
``` 