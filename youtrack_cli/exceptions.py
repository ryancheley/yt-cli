"""Custom exceptions and error handling for YouTrack CLI."""

from typing import List, Optional

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
    "CommandValidationError",
    "ParameterError",
    "UsageError",
    "TokenRefreshError",
    "TokenExpiredError",
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


class CommandValidationError(YouTrackError):
    """Errors related to command structure and usage."""

    def __init__(
        self,
        message: str,
        command_path: Optional[str] = None,
        usage_example: Optional[str] = None,
        similar_commands: Optional[List[str]] = None,
    ):
        suggestion_parts = []
        if similar_commands:
            suggestion_parts.append(f"Did you mean: {', '.join(similar_commands)}")
        if usage_example:
            suggestion_parts.append(f"Usage: {usage_example}")

        suggestion = " | ".join(suggestion_parts) if suggestion_parts else None
        super().__init__(message, suggestion)
        self.command_path = command_path
        self.usage_example = usage_example
        self.similar_commands = similar_commands


class ParameterError(YouTrackError):
    """Errors related to command parameters and arguments."""

    def __init__(
        self,
        message: str,
        parameter_name: Optional[str] = None,
        expected_type: Optional[str] = None,
        usage_example: Optional[str] = None,
        valid_choices: Optional[List[str]] = None,
    ):
        suggestion_parts = []
        if expected_type:
            suggestion_parts.append(f"Expected {expected_type}")
        if valid_choices:
            suggestion_parts.append(f"Valid choices: {', '.join(valid_choices)}")
        if usage_example:
            suggestion_parts.append(f"Example: {usage_example}")

        suggestion = " | ".join(suggestion_parts) if suggestion_parts else None
        super().__init__(message, suggestion)
        self.parameter_name = parameter_name
        self.expected_type = expected_type
        self.usage_example = usage_example
        self.valid_choices = valid_choices


class UsageError(YouTrackError):
    """Errors that provide comprehensive usage guidance."""

    def __init__(
        self,
        message: str,
        command_path: str,
        usage_syntax: str,
        examples: Optional[List[str]] = None,
        common_mistakes: Optional[List[str]] = None,
    ):
        suggestion_parts = [f"Usage: {usage_syntax}"]

        if examples:
            suggestion_parts.append("Examples:")
            for i, example in enumerate(examples, 1):
                suggestion_parts.append(f"  {i}. {example}")

        if common_mistakes:
            suggestion_parts.append("Common mistakes to avoid:")
            for mistake in common_mistakes:
                suggestion_parts.append(f"  - {mistake}")

        suggestion = "\n".join(suggestion_parts)
        super().__init__(message, suggestion)
        self.command_path = command_path
        self.usage_syntax = usage_syntax
        self.examples = examples or []
        self.common_mistakes = common_mistakes or []


class TokenRefreshError(AuthenticationError):
    """Token refresh related errors."""

    def __init__(self, message: str = "Token refresh failed"):
        super().__init__(message)
        self.suggestion = "Try 'yt auth login' to re-authenticate or check if your token supports refresh"


class TokenExpiredError(AuthenticationError):
    """Token expiration related errors."""

    def __init__(self, message: str = "Token has expired"):
        super().__init__(message)
        self.suggestion = "Run 'yt auth refresh' to renew your token or 'yt auth login' to re-authenticate"
