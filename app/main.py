import os
from typing import Annotated

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.params import Depends
from fastapi.responses import JSONResponse

# Import logging middleware
from app.core.config import settings
from app.domain.repositories import IpGeolocationRepository
from app.domain.services import IpGeolocationService
from app.interfaces.api.routes.dependencies import (
    get_ip_geolocation_service,
    get_ip_geolocation_repository,
)
from app.middleware import add_logging_middleware
from app.interfaces.api.routes.v1.geolocation_router import router as geolocation_router

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
    docs_url=f"/api/{settings.VERSION}/docs",
    redoc_url=f"/api/{settings.VERSION}/redoc",
    openapi_url=f"/api/{settings.VERSION}/openapi.json",
)

# Add logging middleware
add_logging_middleware(app)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


# Include routers - to be expanded
app.include_router(geolocation_router, prefix=f"/api/{settings.VERSION}")


# Health check endpointget_ip_geolocation_service
@app.get("/health", tags=["Monitoring"])
async def health_check(
    ip_geolocation_service: Annotated[IpGeolocationService, Depends(get_ip_geolocation_service)],
    ip_geolocation_repository: Annotated[
        IpGeolocationRepository, Depends(get_ip_geolocation_repository)
    ],
):
    """
    Check the health of the API and its dependencies.
    """
    # Basic health check - will be expanded to check database and external
    # services
    database_status = "ok" if await ip_geolocation_repository.is_available() else "unavailable"
    external_api_status = "ok" if await ip_geolocation_service.is_available() else "unavailable"
    return {
        "status": "ok",
        "components": {
            "api": {"status": "ok"},
            "database": {"status": database_status},
            "external_api": {"status": external_api_status},
        },
    }


# Root endpoint


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint, redirects to docs.
    """
    return {
        "message": (
            "Welcome to IP Geolocation API. " f"See /api/{settings.VERSION}/docs for documentation."
        )
    }


# Unified error handling for HTTP exceptions
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": exc.status_code, "message": exc.detail}},
    )


# Unified exception handler for all exceptions
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": {"code": "INTERNAL_ERROR", "message": "An unexpected error occurred."}},
    )


if __name__ == "__main__":
    import uvicorn

    # Get host and port from environment variables or use safe defaults
    host = os.getenv("HOST", "127.0.0.1")  # Default to localhost for safety
    port = int(os.getenv("PORT", 8000))

    # Enable binding to all interfaces only in production environment
    if os.getenv("ENVIRONMENT") == "production":
        host = "0.0.0.0"  # nosec B104 - Intentional for production environments

    uvicorn.run("app.main:app", host=host, port=port, reload=True)
