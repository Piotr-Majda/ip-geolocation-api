"""
Command-line interface for the IP Geolocation API.
"""

import os

import uvicorn
from dotenv import load_dotenv

from app.core.logging import setup_logging


def main():
    """
    CLI entrypoint for running the application.
    """
    # Setup logging
    setup_logging()
    load_dotenv()

    # Get host and port from environment variables or use safe defaults
    host = os.getenv("HOST", "127.0.0.1")  # Default to localhost for safety
    port = int(os.getenv("PORT", 8000))

    # Enable binding to all interfaces only in production environment
    if os.getenv("ENVIRONMENT") == "production":
        host = "0.0.0.0"  # nosec B104 - Intentional for production environments

    print(f"Starting IP Geolocation API on http://{host}:{port}")
    uvicorn.run("app.main:app", host=host, port=port, reload=True)


if __name__ == "__main__":
    main()
