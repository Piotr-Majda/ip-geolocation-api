"""Middleware package for FastAPI application."""

from contextvars import ContextVar
from typing import Optional

# Create a context variable for request ID that can be used across the application
request_id_var: ContextVar[Optional[str]] = ContextVar("request_id", default=None)

from app.middleware.logging import add_logging_middleware  # noqa

__all__ = ["add_logging_middleware", "request_id_var"]
