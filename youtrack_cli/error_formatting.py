"""Centralized error formatting module for YouTrack CLI.

This module provides standardized error message formatting across all CLI commands,
with support for quiet mode and programmatic error handling.
"""

from enum import Enum
from typing import Any, Dict, Optional

from rich.console import Console

from .console import is_quiet_mode


class ErrorCode(Enum):
    """Standardized error codes for programmatic handling."""

    # Authentication errors (AUTH_xxx)
    AUTH_FAILED = "AUTH_001"
    AUTH_EXPIRED = "AUTH_002"
    AUTH_INVALID_TOKEN = "AUTH_003"
    AUTH_NO_CREDENTIALS = "AUTH_004"

    # Network errors (NET_xxx)
    NET_CONNECTION_FAILED = "NET_001"
    NET_TIMEOUT = "NET_002"
    NET_SSL_ERROR = "NET_003"
    NET_DNS_ERROR = "NET_004"

    # Validation errors (VAL_xxx)
    VAL_INVALID_INPUT = "VAL_001"
    VAL_MISSING_REQUIRED = "VAL_002"
    VAL_FORMAT_ERROR = "VAL_003"
    VAL_OUT_OF_RANGE = "VAL_004"

    # Permission errors (PERM_xxx)
    PERM_ACCESS_DENIED = "PERM_001"
    PERM_INSUFFICIENT_RIGHTS = "PERM_002"
    PERM_RESOURCE_FORBIDDEN = "PERM_003"

    # Configuration errors (CFG_xxx)
    CFG_NOT_FOUND = "CFG_001"
    CFG_INVALID_FORMAT = "CFG_002"
    CFG_SAVE_FAILED = "CFG_003"
    CFG_LOAD_FAILED = "CFG_004"

    # Resource errors (RES_xxx)
    RES_NOT_FOUND = "RES_001"
    RES_ALREADY_EXISTS = "RES_002"
    RES_OPERATION_FAILED = "RES_003"

    # System errors (SYS_xxx)
    SYS_INTERNAL_ERROR = "SYS_001"
    SYS_UNSUPPORTED_OPERATION = "SYS_002"
    SYS_FILESYSTEM_ERROR = "SYS_003"

    # Generic errors (GEN_xxx)
    GEN_UNKNOWN_ERROR = "GEN_001"
    GEN_OPERATION_CANCELLED = "GEN_002"


class ErrorSeverity(Enum):
    """Error severity levels."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class StandardizedError:
    """Standardized error message container."""

    def __init__(
        self,
        code: ErrorCode,
        message: str,
        details: Optional[str] = None,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        context: Optional[Dict[str, Any]] = None,
    ):
        self.code = code
        self.message = message
        self.details = details
        self.severity = severity
        self.context = context or {}


class ErrorFormatter:
    """Centralized error formatting utility."""

    def __init__(self, console: Optional[Console] = None, quiet: Optional[bool] = None):
        self.console = console or Console()
        # If quiet mode is not explicitly specified, use global console setting
        self.quiet = quiet if quiet is not None else is_quiet_mode()

        # Define styling for different severities
        self.severity_styles = {
            ErrorSeverity.ERROR: {"emoji": "❌", "style": "red", "prefix": "ERROR"},
            ErrorSeverity.WARNING: {"emoji": "⚠️", "style": "yellow", "prefix": "WARNING"},
            ErrorSeverity.INFO: {"emoji": "ℹ️", "style": "blue", "prefix": "INFO"},
        }

    def format_error(self, error: StandardizedError) -> str:
        """Format error message according to current mode (quiet/verbose)."""
        if self.quiet:
            return self._format_quiet(error)
        return self._format_verbose(error)

    def _format_quiet(self, error: StandardizedError) -> str:
        """Format error for quiet mode (automation-friendly)."""
        return f"{error.code.value}: {error.message}"

    def _format_verbose(self, error: StandardizedError) -> str:
        """Format error for verbose mode (user-friendly)."""
        style_config = self.severity_styles[error.severity]

        # Start with emoji and message
        formatted = f"{style_config['emoji']} {error.message}"

        # Add error code in brackets
        formatted += f" [{error.code.value}]"

        return formatted

    def print_error(self, error: StandardizedError) -> None:
        """Print formatted error to console."""
        if self.quiet:
            # In quiet mode, print plain text without styling
            self.console.print(self.format_error(error))
        else:
            # In verbose mode, use rich styling
            style_config = self.severity_styles[error.severity]
            formatted_message = self._format_verbose(error)

            self.console.print(formatted_message, style=style_config["style"])

            # Print details if available and not in quiet mode
            if error.details:
                self.console.print(f"Details: {error.details}", style="dim")


# Common error factory functions for frequently used errors
class CommonErrors:
    """Factory for common error patterns."""

    @staticmethod
    def authentication_failed(details: Optional[str] = None) -> StandardizedError:
        """Create authentication failed error."""
        return StandardizedError(code=ErrorCode.AUTH_FAILED, message="Authentication failed", details=details)

    @staticmethod
    def no_credentials() -> StandardizedError:
        """Create no credentials found error."""
        return StandardizedError(code=ErrorCode.AUTH_NO_CREDENTIALS, message="No authentication credentials found")

    @staticmethod
    def connection_failed(details: Optional[str] = None) -> StandardizedError:
        """Create connection failed error."""
        return StandardizedError(code=ErrorCode.NET_CONNECTION_FAILED, message="Connection failed", details=details)

    @staticmethod
    def resource_not_found(resource_type: str, identifier: str) -> StandardizedError:
        """Create resource not found error."""
        return StandardizedError(code=ErrorCode.RES_NOT_FOUND, message=f"{resource_type} '{identifier}' not found")

    @staticmethod
    def invalid_input(field: str, details: Optional[str] = None) -> StandardizedError:
        """Create invalid input error."""
        return StandardizedError(
            code=ErrorCode.VAL_INVALID_INPUT, message=f"Invalid input for {field}", details=details
        )

    @staticmethod
    def permission_denied(action: str) -> StandardizedError:
        """Create permission denied error."""
        return StandardizedError(code=ErrorCode.PERM_ACCESS_DENIED, message=f"Permission denied: {action}")

    @staticmethod
    def configuration_error(details: Optional[str] = None) -> StandardizedError:
        """Create configuration error."""
        return StandardizedError(code=ErrorCode.CFG_INVALID_FORMAT, message="Configuration error", details=details)

    @staticmethod
    def operation_failed(operation: str, details: Optional[str] = None) -> StandardizedError:
        """Create operation failed error."""
        return StandardizedError(code=ErrorCode.RES_OPERATION_FAILED, message=f"{operation} failed", details=details)


def get_error_formatter(console: Optional[Console] = None, quiet: Optional[bool] = None) -> ErrorFormatter:
    """Get or create error formatter instance."""
    # Auto-detect quiet mode if not specified
    effective_quiet = quiet if quiet is not None else is_quiet_mode()

    # Always create a new formatter to avoid global state issues
    return ErrorFormatter(console=console, quiet=effective_quiet)


def format_and_print_error(
    error: StandardizedError, console: Optional[Console] = None, quiet: Optional[bool] = None
) -> None:
    """Convenience function to format and print an error."""
    formatter = get_error_formatter(console=console, quiet=quiet)
    formatter.print_error(error)


# Legacy compatibility functions for gradual migration
def print_legacy_error(message: str, console: Optional[Console] = None, quiet: Optional[bool] = None) -> None:
    """Print error using legacy format for backward compatibility."""
    error = StandardizedError(code=ErrorCode.GEN_UNKNOWN_ERROR, message=message)
    format_and_print_error(error, console=console, quiet=quiet)
