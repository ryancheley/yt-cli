"""Tests for custom exception hierarchy and error handling."""

import pytest

from youtrack_cli.exceptions import (
    AuthenticationError,
    ConnectionError,
    NotFoundError,
    PermissionError,
    RateLimitError,
    ValidationError,
    YouTrackError,
    YouTrackNetworkError,
    YouTrackServerError,
)


class TestYouTrackError:
    """Test base YouTrackError exception."""

    def test_base_exception_creation(self):
        """Test creating base YouTrack exception."""
        error = YouTrackError("Something went wrong")

        assert str(error) == "Something went wrong"
        assert error.message == "Something went wrong"
        assert error.suggestion is None

    def test_base_exception_with_suggestion(self):
        """Test creating base exception with suggestion."""
        error = YouTrackError("Something went wrong", suggestion="Try doing something else")

        assert error.message == "Something went wrong"
        assert error.suggestion == "Try doing something else"

    def test_base_exception_inheritance(self):
        """Test that YouTrackError inherits from Exception."""
        error = YouTrackError("Test error")
        assert isinstance(error, Exception)
        assert isinstance(error, YouTrackError)


class TestAuthenticationError:
    """Test AuthenticationError exception."""

    def test_authentication_error_default(self):
        """Test authentication error with default message."""
        error = AuthenticationError()

        assert str(error) == "Authentication failed"
        assert error.message == "Authentication failed"
        assert error.suggestion == "Run 'yt auth login' to authenticate with YouTrack"

    def test_authentication_error_custom_message(self):
        """Test authentication error with custom message."""
        error = AuthenticationError("Invalid credentials")

        assert str(error) == "Invalid credentials"
        assert error.message == "Invalid credentials"
        assert error.suggestion == "Run 'yt auth login' to authenticate with YouTrack"

    def test_authentication_error_inheritance(self):
        """Test AuthenticationError inheritance."""
        error = AuthenticationError()
        assert isinstance(error, YouTrackError)
        assert isinstance(error, AuthenticationError)


class TestConnectionError:
    """Test ConnectionError exception."""

    def test_connection_error_default(self):
        """Test connection error with default message."""
        error = ConnectionError()

        assert str(error) == "Failed to connect to YouTrack"
        assert error.message == "Failed to connect to YouTrack"
        assert error.suggestion == "Check your internet connection and YouTrack URL"

    def test_connection_error_custom_message(self):
        """Test connection error with custom message."""
        error = ConnectionError("Network timeout")

        assert str(error) == "Network timeout"
        assert error.message == "Network timeout"
        assert error.suggestion == "Check your internet connection and YouTrack URL"

    def test_connection_error_inheritance(self):
        """Test ConnectionError inheritance."""
        error = ConnectionError()
        assert isinstance(error, YouTrackError)
        assert isinstance(error, ConnectionError)


class TestValidationError:
    """Test ValidationError exception."""

    def test_validation_error_without_field(self):
        """Test validation error without field specification."""
        error = ValidationError("Value is required")

        assert str(error) == "Value is required"
        assert error.message == "Value is required"
        assert error.field is None

    def test_validation_error_with_field(self):
        """Test validation error with field specification."""
        error = ValidationError("cannot be empty", field="username")

        assert str(error) == "Invalid username: cannot be empty"
        assert error.message == "Invalid username: cannot be empty"
        assert error.field == "username"

    def test_validation_error_inheritance(self):
        """Test ValidationError inheritance."""
        error = ValidationError("Test error")
        assert isinstance(error, YouTrackError)
        assert isinstance(error, ValidationError)


class TestNotFoundError:
    """Test NotFoundError exception."""

    def test_not_found_error_creation(self):
        """Test creating not found error."""
        error = NotFoundError("Issue", "TEST-123")

        expected_message = "Issue 'TEST-123' not found"
        expected_suggestion = "Check if the issue exists and you have access to it"

        assert str(error) == expected_message
        assert error.message == expected_message
        assert error.suggestion == expected_suggestion

    def test_not_found_error_different_resource(self):
        """Test not found error with different resource type."""
        error = NotFoundError("Project", "MYPROJECT")

        expected_message = "Project 'MYPROJECT' not found"
        expected_suggestion = "Check if the project exists and you have access to it"

        assert str(error) == expected_message
        assert error.message == expected_message
        assert error.suggestion == expected_suggestion

    def test_not_found_error_inheritance(self):
        """Test NotFoundError inheritance."""
        error = NotFoundError("Issue", "TEST-123")
        assert isinstance(error, YouTrackError)
        assert isinstance(error, NotFoundError)


class TestPermissionError:
    """Test PermissionError exception."""

    def test_permission_error_without_resource(self):
        """Test permission error without resource specification."""
        error = PermissionError("create issues")

        expected_message = "Permission denied to create issues"
        expected_suggestion = "Check your user permissions in YouTrack"

        assert str(error) == expected_message
        assert error.message == expected_message
        assert error.suggestion == expected_suggestion

    def test_permission_error_with_resource(self):
        """Test permission error with resource specification."""
        error = PermissionError("update", "issue TEST-123")

        expected_message = "Permission denied to update issue TEST-123"
        expected_suggestion = "Check your user permissions in YouTrack"

        assert str(error) == expected_message
        assert error.message == expected_message
        assert error.suggestion == expected_suggestion

    def test_permission_error_inheritance(self):
        """Test PermissionError inheritance."""
        error = PermissionError("test action")
        assert isinstance(error, YouTrackError)
        assert isinstance(error, PermissionError)


class TestRateLimitError:
    """Test RateLimitError exception."""

    def test_rate_limit_error_without_retry_after(self):
        """Test rate limit error without retry after time."""
        error = RateLimitError()

        expected_message = "Rate limit exceeded"
        expected_suggestion = "Wait a moment and try again, or reduce the frequency of requests"

        assert str(error) == expected_message
        assert error.message == expected_message
        assert error.suggestion == expected_suggestion

    def test_rate_limit_error_with_retry_after(self):
        """Test rate limit error with retry after time."""
        error = RateLimitError(retry_after=60)

        expected_message = "Rate limit exceeded. Retry after 60 seconds"
        expected_suggestion = "Wait a moment and try again, or reduce the frequency of requests"

        assert str(error) == expected_message
        assert error.message == expected_message
        assert error.suggestion == expected_suggestion

    def test_rate_limit_error_inheritance(self):
        """Test RateLimitError inheritance."""
        error = RateLimitError()
        assert isinstance(error, YouTrackError)
        assert isinstance(error, RateLimitError)


class TestYouTrackNetworkError:
    """Test YouTrackNetworkError exception."""

    def test_network_error_default(self):
        """Test network error with default message."""
        error = YouTrackNetworkError()

        expected_message = "Network error occurred"
        expected_suggestion = "Check your internet connection and try again"

        assert str(error) == expected_message
        assert error.message == expected_message
        assert error.suggestion == expected_suggestion

    def test_network_error_custom_message(self):
        """Test network error with custom message."""
        error = YouTrackNetworkError("Connection timed out")

        expected_message = "Connection timed out"
        expected_suggestion = "Check your internet connection and try again"

        assert str(error) == expected_message
        assert error.message == expected_message
        assert error.suggestion == expected_suggestion

    def test_network_error_inheritance(self):
        """Test YouTrackNetworkError inheritance."""
        error = YouTrackNetworkError()
        assert isinstance(error, YouTrackError)
        assert isinstance(error, YouTrackNetworkError)


class TestYouTrackServerError:
    """Test YouTrackServerError exception."""

    def test_server_error_default(self):
        """Test server error with default message."""
        error = YouTrackServerError()

        expected_message = "Server error occurred"
        expected_suggestion = "The server may be temporarily unavailable. Try again later"

        assert str(error) == expected_message
        assert error.message == expected_message
        assert error.suggestion == expected_suggestion
        assert error.status_code is None

    def test_server_error_custom_message(self):
        """Test server error with custom message."""
        error = YouTrackServerError("Internal server error")

        expected_message = "Internal server error"
        expected_suggestion = "The server may be temporarily unavailable. Try again later"

        assert str(error) == expected_message
        assert error.message == expected_message
        assert error.suggestion == expected_suggestion

    def test_server_error_with_status_code(self):
        """Test server error with status code."""
        error = YouTrackServerError("Internal server error", status_code=500)

        expected_message = "Server error (HTTP 500): Internal server error"
        expected_suggestion = "The server may be temporarily unavailable. Try again later"

        assert str(error) == expected_message
        assert error.message == expected_message
        assert error.suggestion == expected_suggestion
        assert error.status_code == 500

    def test_server_error_inheritance(self):
        """Test YouTrackServerError inheritance."""
        error = YouTrackServerError()
        assert isinstance(error, YouTrackError)
        assert isinstance(error, YouTrackServerError)


class TestExceptionHierarchy:
    """Test exception hierarchy and relationships."""

    def test_all_exceptions_inherit_from_youtrack_error(self):
        """Test that all custom exceptions inherit from YouTrackError."""
        exceptions = [
            AuthenticationError(),
            ConnectionError(),
            ValidationError("test"),
            NotFoundError("Resource", "ID"),
            PermissionError("action"),
            RateLimitError(),
            YouTrackNetworkError(),
            YouTrackServerError(),
        ]

        for exception in exceptions:
            assert isinstance(exception, YouTrackError)
            assert isinstance(exception, Exception)

    def test_exception_types_are_distinct(self):
        """Test that different exception types are distinguishable."""
        auth_error = AuthenticationError()
        connection_error = ConnectionError()
        validation_error = ValidationError("test")

        assert type(auth_error) is not type(connection_error)
        assert type(auth_error) is not type(validation_error)
        assert type(connection_error) is not type(validation_error)

    def test_exception_catching_by_base_class(self):
        """Test that exceptions can be caught by base class."""
        try:
            raise AuthenticationError("Test error")
        except YouTrackError as e:
            assert isinstance(e, AuthenticationError)
            assert e.message == "Test error"
        except Exception:
            pytest.fail("Should have been caught as YouTrackError")

    def test_exception_catching_by_specific_type(self):
        """Test that exceptions can be caught by specific type."""
        try:
            raise ValidationError("Invalid input", field="username")
        except ValidationError as e:
            assert e.field == "username"
            assert e.message == "Invalid username: Invalid input"
        except YouTrackError:
            pytest.fail("Should have been caught as ValidationError")


class TestExceptionMessages:
    """Test exception message formatting and suggestions."""

    def test_all_exceptions_have_messages(self):
        """Test that all exceptions have meaningful messages."""
        exceptions = [
            (AuthenticationError(), "Authentication failed"),
            (ConnectionError(), "Failed to connect to YouTrack"),
            (ValidationError("required"), "required"),
            (NotFoundError("Issue", "TEST-123"), "Issue 'TEST-123' not found"),
            (PermissionError("read"), "Permission denied to read"),
            (RateLimitError(), "Rate limit exceeded"),
            (YouTrackNetworkError(), "Network error occurred"),
            (YouTrackServerError(), "Server error occurred"),
        ]

        for exception, expected_message in exceptions:
            assert expected_message in str(exception)
            assert expected_message in exception.message

    def test_all_exceptions_have_suggestions(self):
        """Test that all exceptions have helpful suggestions."""
        exceptions = [
            AuthenticationError(),
            ConnectionError(),
            NotFoundError("Issue", "TEST-123"),
            PermissionError("read"),
            RateLimitError(),
            YouTrackNetworkError(),
            YouTrackServerError(),
        ]

        for exception in exceptions:
            assert exception.suggestion is not None
            assert len(exception.suggestion) > 0
            assert isinstance(exception.suggestion, str)

    def test_exception_string_representations(self):
        """Test exception string representations."""
        error = YouTrackError("Test message", suggestion="Test suggestion")
        assert str(error) == "Test message"

        # The suggestion is not included in __str__ but is available as attribute
        assert error.suggestion == "Test suggestion"


class TestExceptionUsagePatterns:
    """Test common exception usage patterns."""

    def test_raising_and_catching_specific_exceptions(self):
        """Test raising and catching specific exception types."""
        with pytest.raises(AuthenticationError) as exc_info:
            raise AuthenticationError("Invalid token")

        assert exc_info.value.message == "Invalid token"
        assert "yt auth login" in exc_info.value.suggestion

    def test_re_raising_with_additional_context(self):
        """Test re-raising exceptions with additional context."""
        try:
            try:
                raise ConnectionError("Network timeout")
            except ConnectionError as e:
                # Re-raise with additional context
                raise YouTrackNetworkError(f"Failed during operation: {e.message}") from e
        except YouTrackNetworkError as final_error:
            assert "Failed during operation: Network timeout" in final_error.message

    def test_exception_chaining(self):
        """Test exception chaining for debugging."""
        original_error = ConnectionError("Original network error")

        try:
            try:
                raise original_error
            except ConnectionError as e:
                raise YouTrackServerError("Server unavailable") from e
        except YouTrackServerError as chained_error:
            assert chained_error.__cause__ == original_error
