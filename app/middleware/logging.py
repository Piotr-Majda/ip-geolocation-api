import json
import time
import uuid
from typing import Any, Callable, Dict, List, Optional, Set, TypedDict, Union

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

# Import centralized logging
from app.core.logging import api_logger, setup_logging

# Import the request_id_var from the package
from app.middleware import request_id_var


# Define typed dictionaries for log data structure
class RequestData(TypedDict, total=False):
    id: str
    method: str
    path: str
    query_params: Dict[str, str]
    client_ip: str
    headers: Dict[str, str]
    body: Union[Dict[str, Any], List[Any], str]
    body_error: str


class ResponseData(TypedDict, total=False):
    status_code: int
    headers: Dict[str, str]
    body: Union[Dict[str, Any], List[Any], str]
    body_error: str


class LogData(TypedDict, total=False):
    request: RequestData
    response: ResponseData
    timestamp: float
    duration_ms: float
    error: str


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging request and response information in JSON format.
    Includes sanitization of sensitive data.
    """

    def __init__(
        self,
        app: ASGIApp,
        *,
        sensitive_headers: Optional[Set[str]] = None,
        sensitive_query_params: Optional[Set[str]] = None,
        log_request_body: bool = False,
        log_response_body: bool = False,
    ):
        super().__init__(app)
        self.sensitive_headers = sensitive_headers or {
            "authorization",
            "x-api-key",
            "api-key",
            "cookie",
        }
        self.sensitive_query_params = sensitive_query_params or {"api_key", "token", "key"}
        self.log_request_body = log_request_body
        self.log_response_body = log_response_body

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = str(uuid.uuid4())
        # Set the request ID in the context
        token = request_id_var.set(request_id)
        # Also add to request.state for other middleware/handlers
        request.state.request_id = request_id

        # Capture request information
        start_time = time.time()
        log_data: LogData = {
            "request": {
                "id": request_id,
                "method": request.method,
                "path": request.url.path,
                "query_params": self._sanitize_query_params(dict(request.query_params)),
                "client_ip": self._get_client_ip(request),
                "headers": self._sanitize_headers(dict(request.headers)),
            },
            "timestamp": start_time,
        }

        # Log request body if enabled
        if self.log_request_body:
            try:
                # Clone the request body
                body = await request.body()
                # Create a new request with the same body
                request = Request(request.scope, request._receive, request._send)
                if body:
                    log_data["request"]["body"] = self._sanitize_body(json.loads(body))
            except Exception as e:
                log_data["request"]["body_error"] = str(e)

        # Process the request
        try:
            response = await call_next(request)
            status_code = response.status_code

            # Add response info to log data
            log_data["response"] = {
                "status_code": status_code,
                "headers": self._sanitize_headers(dict(response.headers)),
            }

            # Log response body if enabled
            if self.log_response_body and status_code != 204:
                try:
                    response_body = b""
                    async for chunk in response.body_iterator:
                        response_body += chunk

                    # Create a new response with the consumed body
                    from starlette.responses import Response as StarletteResponse

                    response = StarletteResponse(
                        content=response_body,
                        status_code=response.status_code,
                        headers=dict(response.headers),
                        media_type=response.media_type,
                    )

                    try:
                        log_data["response"]["body"] = self._sanitize_body(
                            json.loads(response_body)
                        )
                    except Exception:
                        log_data["response"]["body"] = response_body.decode(
                            "utf-8", errors="replace"
                        )

                except Exception as e:
                    log_data["response"]["body_error"] = str(e)

        except Exception as e:
            log_data["error"] = str(e)
            log_data["response"] = {"status_code": 500}
            raise e from None
        finally:
            # Calculate duration
            duration = time.time() - start_time
            log_data["duration_ms"] = round(duration * 1000, 2)

            # Log the data
            self._log_request(log_data)

            # Reset the context variable
            request_id_var.reset(token)

        return response

    def _sanitize_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """Sanitize sensitive header values."""
        sanitized = {}
        for key, value in headers.items():
            lower_key = key.lower()
            if lower_key in self.sensitive_headers:
                sanitized[key] = "***REDACTED***"
            else:
                sanitized[key] = value
        return sanitized

    def _sanitize_query_params(self, params: Dict[str, str]) -> Dict[str, str]:
        """Sanitize sensitive query parameters."""
        sanitized = {}
        for key, value in params.items():
            lower_key = key.lower()
            if lower_key in self.sensitive_query_params:
                sanitized[key] = "***REDACTED***"
            else:
                sanitized[key] = value
        return sanitized

    def _sanitize_body(
        self, body: Union[Dict[str, Any], List[Any], str]
    ) -> Union[Dict[str, Any], List[Any], str]:
        """Sanitize sensitive data in request/response body."""
        if isinstance(body, dict):
            sanitized: Dict[str, Any] = {}
            for key, value in body.items():
                lower_key = key.lower()
                if any(
                    sensitive in lower_key
                    for sensitive in {"token", "key", "password", "secret", "credential"}
                ):
                    sanitized[key] = "***REDACTED***"
                elif isinstance(value, (dict, list)):
                    sanitized[key] = self._sanitize_body(value)
                else:
                    sanitized[key] = value
            return sanitized
        elif isinstance(body, list):
            return [
                self._sanitize_body(item) if isinstance(item, (dict, list)) else item
                for item in body
            ]
        return body

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request headers or direct connection."""
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        client_host = request.client.host if request.client else None
        return client_host or "unknown"

    def _log_request(self, log_data: LogData) -> None:
        """Log the request data as JSON."""
        # Get status code safely
        response_data = log_data.get("response")
        status_code = 500
        if response_data and "status_code" in response_data:
            status_code = response_data["status_code"]

        if status_code >= 500:
            api_logger.error(json.dumps(log_data))
        elif status_code >= 400:
            api_logger.warning(json.dumps(log_data))
        else:
            api_logger.info(json.dumps(log_data))


def add_logging_middleware(app: FastAPI) -> None:
    """
    Add the logging middleware to the FastAPI application.

    Args:
        app: The FastAPI application
    """
    # Setup logging system
    log_level = "INFO"  # Could be configurable from environment
    setup_logging(log_level)

    # Add middleware
    app.add_middleware(
        RequestLoggingMiddleware,
        sensitive_headers={"authorization", "x-api-key", "api-key", "cookie"},
        sensitive_query_params={"api_key", "token", "key"},
        log_request_body=False,  # Set to True if you want to log request bodies
        log_response_body=False,  # Set to True if you want to log response bodies
    )

    api_logger.info({"message": "Logging middleware initialized", "log_level": log_level})
