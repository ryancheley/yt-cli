"""Custom exceptions and error handling for YouTrack CLI."""

from typing import Optional

__all__ = [
    "YouTrackError",
    "AuthenticationError",
    "ConnectionError",
    "ValidationError",
    "NotFoundError",
    "PermissionError",
    "RateLimitError",
    "YouTrackNetworkError",
    "YouTrackServerError",
]


class YouTrackError(Exception):
    """Base exception for YouTrack CLI errors."""

    def __init__(self, message: str, suggestion: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.suggestion = suggestion


class AuthenticationError(YouTrackError):
    """Authentication related errors."""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, suggestion="Run 'yt auth login' to authenticate with YouTrack")


class ConnectionError(YouTrackError):
    """Connection related errors."""

    def __init__(self, message: str = "Failed to connect to YouTrack"):
        super().__init__(message, suggestion="Check your internet connection and YouTrack URL")


class ValidationError(YouTrackError):
    """Input validation errors."""

    def __init__(self, message: str, field: Optional[str] = None):
        if field:
            message = f"Invalid {field}: {message}"
        super().__init__(message)
        self.field = field


class NotFoundError(YouTrackError):
    """Resource not found errors."""

    def __init__(self, resource_type: str, identifier: str):
        super().__init__(
            f"{resource_type} '{identifier}' not found",
            suggestion=(f"Check if the {resource_type.lower()} exists and you have access to it"),
        )


class PermissionError(YouTrackError):
    """Permission denied errors."""

    def __init__(self, action: str, resource: Optional[str] = None):
        if resource:
            message = f"Permission denied to {action} {resource}"
        else:
            message = f"Permission denied to {action}"
        super().__init__(message, suggestion="Check your user permissions in YouTrack")


class RateLimitError(YouTrackError):
    """Rate limit exceeded errors."""

    def __init__(self, retry_after: Optional[int] = None):
        message = "Rate limit exceeded"
        if retry_after:
            message += f". Retry after {retry_after} seconds"
        super().__init__(
            message,
            suggestion=("Wait a moment and try again, or reduce the frequency of requests"),
        )


class YouTrackNetworkError(YouTrackError):
    """Network related errors that may be retryable."""

    def __init__(self, message: str = "Network error occurred"):
        super().__init__(message, suggestion="Check your internet connection and try again")


class YouTrackServerError(YouTrackError):
    """Server-side errors that may be retryable."""

    def __init__(self, message: str = "Server error occurred", status_code: Optional[int] = None):
        if status_code:
            message = f"Server error (HTTP {status_code}): {message}"
        super().__init__(message, suggestion="The server may be temporarily unavailable. Try again later")
        self.status_code = status_code
