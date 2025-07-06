"""Comprehensive logging infrastructure for YouTrack CLI using structlog."""

import logging
import logging.handlers
import os
import re
import sys
from pathlib import Path
from typing import Any, Optional

import structlog
from rich.logging import RichHandler

__all__ = [
    "SensitiveDataFilter",
    "setup_logging",
    "get_logger",
    "log_operation",
    "log_api_call",
    "get_log_file_path",
]


class SensitiveDataFilter(logging.Filter):
    """Filter to mask sensitive data in log records."""

    SENSITIVE_PATTERNS = [
        # More specific patterns first
        (
            re.compile(r"(Authorization:\s*Bearer\s+)([^\s]+)", re.IGNORECASE),
            r"\1***MASKED***",
        ),
        (re.compile(r"(Bearer\s+)([^\s]+)", re.IGNORECASE), r"\1***MASKED***"),
        (
            re.compile(r"(token[\s]*[=:][\s]*)([^\s]+)", re.IGNORECASE),
            r"\1***MASKED***",
        ),
        (
            re.compile(r"(password[\s]*[=:][\s]*)([^\s]+)", re.IGNORECASE),
            r"\1***MASKED***",
        ),
        (
            re.compile(r"(api[_-]?key[\s]*[=:][\s]*)([^\s]+)", re.IGNORECASE),
            r"\1***MASKED***",
        ),
        (
            re.compile(r"(authorization[\s]*[=:][\s]*)([^\s]+)", re.IGNORECASE),
            r"\1***MASKED***",
        ),
    ]

    def filter(self, record: logging.LogRecord) -> bool:
        """Filter and mask sensitive data in log records."""
        if hasattr(record, "msg") and isinstance(record.msg, str):
            message = record.msg
            for pattern, replacement in self.SENSITIVE_PATTERNS:
                message = pattern.sub(replacement, message)
            record.msg = message

        # Also filter args if present
        if hasattr(record, "args") and record.args:
            filtered_args = []
            for arg in record.args:
                if isinstance(arg, str):
                    filtered_arg = arg
                    for pattern, replacement in self.SENSITIVE_PATTERNS:
                        filtered_arg = pattern.sub(replacement, filtered_arg)
                    filtered_args.append(filtered_arg)
                else:
                    filtered_args.append(arg)
            record.args = tuple(filtered_args)

        return True


def _get_log_file_path() -> Path:
    """Get the path for log files."""
    # Use XDG_DATA_HOME if available, otherwise use ~/.local/share
    data_home = os.environ.get("XDG_DATA_HOME")
    if data_home:
        log_dir = Path(data_home) / "youtrack-cli"
    else:
        log_dir = Path.home() / ".local" / "share" / "youtrack-cli"

    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir / "youtrack-cli.log"


def _setup_file_logging(log_level: int) -> logging.handlers.RotatingFileHandler:
    """Set up file-based logging with rotation."""
    log_file = _get_log_file_path()

    # Create rotating file handler (10MB max, keep 5 backup files)
    file_handler = logging.handlers.RotatingFileHandler(log_file, maxBytes=10 * 1024 * 1024, backupCount=5)
    file_handler.setLevel(log_level)

    # Use standard formatter for file logs
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(file_formatter)

    # Add sensitive data filter
    file_handler.addFilter(SensitiveDataFilter())

    return file_handler


def _setup_console_logging(log_level: int) -> RichHandler:
    """Set up console-based logging with rich formatting."""
    console_handler = RichHandler(rich_tracebacks=True, show_path=False, show_time=True, show_level=True)
    console_handler.setLevel(log_level)

    # Add sensitive data filter
    console_handler.addFilter(SensitiveDataFilter())

    return console_handler


def _configure_structlog() -> None:
    """Configure structlog for structured logging."""
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def setup_logging(
    verbose: bool = False,
    debug: bool = False,
    log_file: bool = True,
    log_level: Optional[str] = None,
) -> None:
    """Setup comprehensive logging with structlog and rich formatting.

    Args:
        verbose: Enable verbose (INFO) logging
        debug: Enable debug logging (overrides verbose)
        log_file: Enable file-based logging with rotation
        log_level: Override log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # Determine log level
    if log_level:
        level = getattr(logging, log_level.upper(), logging.WARNING)
    elif debug:
        level = logging.DEBUG
    elif verbose:
        level = logging.INFO
    else:
        level = logging.WARNING

    # Remove existing handlers
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Set up handlers
    handlers = []

    # Console handler
    console_handler = _setup_console_logging(level)
    handlers.append(console_handler)

    # File handler (if enabled)
    if log_file:
        file_handler = _setup_file_logging(level)
        handlers.append(file_handler)

    # Configure basic logging
    logging.basicConfig(
        level=level,
        format="%(message)s",
        handlers=handlers,
    )

    # Configure structlog
    _configure_structlog()

    # Set level for YouTrack CLI logger
    logger = logging.getLogger("youtrack_cli")
    logger.setLevel(level)

    # Reduce httpx logging noise unless in debug mode
    if not debug:
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("urllib3").setLevel(logging.WARNING)

    # Log startup message
    if debug:
        logger.debug("Logging system initialized", extra={"level": logging.getLevelName(level)})


def get_logger(name: Optional[str] = None) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance for the YouTrack CLI.

    Args:
        name: Optional name for the logger. If None, uses the caller's module name.

    Returns:
        Structured logger instance configured for YouTrack CLI
    """
    if name is None:
        # Get caller's module name
        frame = sys._getframe(1)
        module_name = frame.f_globals.get("__name__", "youtrack_cli")
        name = module_name

    return structlog.get_logger(name)


def log_operation(operation: str, **kwargs: Any) -> None:
    """Log a high-level operation with structured context.

    Args:
        operation: Name of the operation being performed
        **kwargs: Additional context to include in the log
    """
    logger = get_logger("youtrack_cli.operations")
    logger.info("Operation started", operation=operation, **kwargs)


def log_api_call(
    method: str,
    url: str,
    status_code: Optional[int] = None,
    duration: Optional[float] = None,
    **kwargs: Any,
) -> None:
    """Log API calls with structured context.

    Args:
        method: HTTP method (GET, POST, etc.)
        url: API endpoint URL
        status_code: HTTP status code (if available)
        duration: Request duration in seconds (if available)
        **kwargs: Additional context to include in the log
    """
    logger = get_logger("youtrack_cli.api")

    # Mask sensitive parts of URL
    safe_url = url
    if "token" in safe_url:
        safe_url = re.sub(r"token=[^&]+", "token=***MASKED***", safe_url)

    log_data = {"method": method, "url": safe_url, **kwargs}

    if status_code is not None:
        log_data["status_code"] = status_code

    if duration is not None:
        log_data["duration_ms"] = round(duration * 1000, 2)

    if status_code and status_code >= 400:
        logger.error("API call failed", **log_data)
    else:
        logger.debug("API call completed", **log_data)


def get_log_file_path() -> Path:
    """Get the current log file path.

    Returns:
        Path to the current log file
    """
    return _get_log_file_path()
