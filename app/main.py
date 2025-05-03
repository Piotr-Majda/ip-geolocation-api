import os
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="IP Geolocation API",
    description=("API for storing and retrieving geolocation data " "based on IP addresses"),
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Health check endpoint


@app.get("/health", tags=["Monitoring"])
async def health_check():
    """
    Check the health of the API and its dependencies.
    """
    # Basic health check - will be expanded to check database and external
    # services
    return {
        "status": "ok",
        "components": {
            "api": {"status": "ok"},
            # Will be implemented with actual DB check
            "database": {"status": "ok"},
            # Will be implemented with actual cache check
            "cache": {"status": "ok"},
        },
    }


# Root endpoint


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint, redirects to docs.
    """
    return {"message": ("Welcome to IP Geolocation API. " "See /docs for documentation.")}


# Include routers - to be expanded
# app.include_router(geolocation_router, prefix="/api")

# Error handling


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": exc.status_code, "message": exc.detail}},
    )


# Global exception handler


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": {"code": "INTERNAL_ERROR", "message": "An unexpected error occurred."}},
    )


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
