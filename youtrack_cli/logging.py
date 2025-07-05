"""Logging infrastructure for YouTrack CLI."""

import logging
import sys
from typing import Optional

from rich.logging import RichHandler


def setup_logging(verbose: bool = False, debug: bool = False) -> None:
    """Setup logging with rich formatting.

    Args:
        verbose: Enable verbose (INFO) logging
        debug: Enable debug logging (overrides verbose)
    """
    if debug:
        level = logging.DEBUG
    elif verbose:
        level = logging.INFO
    else:
        level = logging.WARNING

    # Remove existing handlers
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Configure rich logging
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True, show_path=False)],
    )

    # Set level for YouTrack CLI logger
    logger = logging.getLogger("youtrack_cli")
    logger.setLevel(level)

    # Reduce httpx logging noise unless in debug mode
    if not debug:
        logging.getLogger("httpx").setLevel(logging.WARNING)


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get a logger instance for the YouTrack CLI.

    Args:
        name: Optional name for the logger. If None, uses the caller's module name.

    Returns:
        Logger instance configured for YouTrack CLI
    """
    if name is None:
        # Get caller's module name
        frame = sys._getframe(1)
        module_name = frame.f_globals.get("__name__", "youtrack_cli")
        name = module_name

    return logging.getLogger(name)
