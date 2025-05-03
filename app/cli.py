"""
Command-line interface for the IP Geolocation API.
"""
import os
import uvicorn
from dotenv import load_dotenv


def main():
    """Run the FastAPI application using Uvicorn."""
    load_dotenv()  # Load environment variables from .env file

    host = "0.0.0.0"
    port = int(os.getenv("PORT", 8000))
    reload = True  # Enable auto-reload during development

    print(f"Starting IP Geolocation API on http://{host}:{port}")
    uvicorn.run("app.main:app", host=host, port=port, reload=reload)


if __name__ == "__main__":
    main()
