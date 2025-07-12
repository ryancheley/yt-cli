"""Common CLI options and decorators for YouTrack CLI."""

from functools import wraps
from typing import Callable

import click

from .console import get_console
from .logging import setup_logging

__all__ = ["common_options", "output_options", "async_command", "handle_exceptions"]


def common_options(f: Callable) -> Callable:
    """Common options decorator for CLI commands.

    Adds common options like format, verbose, debug to commands.
    """

    @click.option(
        "--format",
        type=click.Choice(["table", "json", "yaml"], case_sensitive=False),
        default="table",
        help="Output format for results",
    )
    @click.option(
        "--verbose",
        "-v",
        is_flag=True,
        help="Enable verbose output",
    )
    @click.option(
        "--debug",
        is_flag=True,
        help="Enable debug output",
    )
    @click.option(
        "--log-level",
        type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], case_sensitive=False),
        help="Set specific log level (overrides --verbose and --debug)",
    )
    @click.option(
        "--no-log-file",
        is_flag=True,
        help="Disable file-based logging",
    )
    @click.option(
        "--no-color",
        is_flag=True,
        help="Disable colored output",
    )
    @wraps(f)
    def wrapper(*args, **kwargs):
        # Extract common options
        format_type = kwargs.pop("format", "table")
        verbose = kwargs.pop("verbose", False)
        debug = kwargs.pop("debug", False)
        log_level = kwargs.pop("log_level", None)
        no_log_file = kwargs.pop("no_log_file", False)
        no_color = kwargs.pop("no_color", False)

        # Setup logging based on options
        setup_logging(verbose=verbose, debug=debug, log_level=log_level, log_file=not no_log_file)

        # Configure console color
        if no_color:
            from rich.console import Console

            console = Console(color_system=None)
        else:
            console = get_console()

        # Add common options to kwargs for the command
        kwargs["format"] = format_type
        kwargs["verbose"] = verbose
        kwargs["debug"] = debug
        kwargs["console"] = console

        return f(*args, **kwargs)

    return wrapper


def output_options(f: Callable) -> Callable:
    """Output-specific options decorator.

    Adds options for controlling output behavior.
    """

    @click.option(
        "--output",
        "-o",
        type=click.Path(),
        help="Output file path (default: stdout)",
    )
    @click.option(
        "--limit",
        "-l",
        type=int,
        help="Limit number of results",
    )
    @click.option(
        "--no-headers",
        is_flag=True,
        help="Omit headers in table output",
    )
    @wraps(f)
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)

    return wrapper


def async_command(f: Callable) -> Callable:
    """Decorator to handle async commands properly.

    Wraps async functions for use with Click.
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        import asyncio

        return asyncio.run(f(*args, **kwargs))

    return wrapper


def handle_exceptions(f: Callable) -> Callable:
    """Decorator to handle exceptions consistently across commands.

    Catches exceptions and displays user-friendly error messages.
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            from .utils import display_error, handle_error

            kwargs.get("console", get_console())
            error_result = handle_error(e, getattr(f, "__name__", "command"))
            display_error(error_result)

            # Exit with error code
            import sys

            sys.exit(1)

    return wrapper
