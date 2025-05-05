import json
import logging
import os
from typing import Any, Dict, Optional

# Create loggers dictionary to track configured loggers
_loggers: Dict[str, logging.Logger] = {}


class JsonFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""

    def format(self, record: Any) -> str:
        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Try to parse the message as JSON if it's already formatted
        if isinstance(record.msg, str):
            try:
                log_data.update(json.loads(record.msg))
            except json.JSONDecodeError:
                log_data["message"] = record.getMessage()
        else:
            log_data["message"] = record.getMessage()

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add request_id if available
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id  # type: ignore

        return json.dumps(log_data)


# Create a request context logger filter
class RequestContextFilter(logging.Filter):
    """
    Filter that adds request_id to log records if available in the current context.
    """

    def filter(self, record: Any) -> bool:
        try:
            # Import here to avoid circular imports
            from app.middleware import request_id_var

            request_id = request_id_var.get()
            if request_id:
                record.request_id = request_id  # type: ignore
        except (ImportError, LookupError):
            # Handle the case where the middleware isn't initialized yet
            pass

        return True


def get_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """
    Get or create a logger with the given name.

    Args:
        name: The name of the logger
        level: Optional logging level (defaults to APP_LOG_LEVEL env var or INFO)

    Returns:
        A configured logger
    """
    # Check if logger already exists
    if name in _loggers:
        return _loggers[name]

    # Get log level from environment or use default
    if level is None:
        level = os.getenv("APP_LOG_LEVEL", "INFO").upper()

    numeric_level = getattr(logging, level, logging.INFO)

    # Create and configure logger
    logger = logging.getLogger(name)
    logger.setLevel(numeric_level)

    # Clear any existing handlers
    logger.handlers = []

    # Create console handler
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())

    # Add request context filter
    context_filter = RequestContextFilter()
    handler.addFilter(context_filter)

    logger.addHandler(handler)

    # Don't propagate to root logger
    logger.propagate = False

    # Store for future use
    _loggers[name] = logger

    return logger


# Initialize default loggers
app_logger = get_logger("app")
api_logger = get_logger("api")


def setup_logging(level: Optional[str] = None) -> None:
    """
    Configure the global logging system.

    Args:
        level: Optional logging level (defaults to APP_LOG_LEVEL env var or INFO)
    """
    # Get log level from environment or use default
    if level is None:
        level = os.getenv("APP_LOG_LEVEL", "INFO").upper()

    numeric_level = getattr(logging, level, logging.INFO)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Clear any existing handlers
    root_logger.handlers = []

    # Add JSON formatter
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())

    # Add request context filter
    context_filter = RequestContextFilter()
    handler.addFilter(context_filter)

    root_logger.addHandler(handler)

    # Just update the existing loggers' levels
    app_logger.setLevel(numeric_level)
    api_logger.setLevel(numeric_level)

    # Log initial message
    app_logger.info({"message": "Logging system initialized", "log_level": level})
