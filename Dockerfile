FROM python:3.13-slim

WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc postgresql-client libpq-dev curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - \
    && ln -s /root/.local/bin/poetry /usr/local/bin/

# Copy Poetry configuration files
COPY pyproject.toml poetry.lock* ./

# Configure Poetry to not use virtual environments inside Docker
RUN poetry config virtualenvs.create false

# Install dependencies (only main dependencies, no dev dependencies)
# Use --no-root to avoid issues with missing README.md
RUN poetry install --only main --no-interaction --no-ansi --no-root

# Copy project files
COPY . .

# Run the application
CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000"] 