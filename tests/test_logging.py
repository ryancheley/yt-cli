"""Tests for the logging infrastructure."""

import logging
import logging.handlers
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from youtrack_cli.logging import (
    SensitiveDataFilter,
    get_log_file_path,
    get_logger,
    log_api_call,
    log_operation,
    setup_logging,
)


class TestSensitiveDataFilter:
    """Test the SensitiveDataFilter class."""

    def test_filter_token_in_message(self):
        """Test that tokens are masked in log messages."""
        log_filter = SensitiveDataFilter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Making request with token=abc123xyz",
            args=(),
            exc_info=None,
        )

        result = log_filter.filter(record)

        assert result is True
        assert "***MASKED***" in record.msg
        assert "abc123xyz" not in record.msg

    def test_filter_password_in_message(self):
        """Test that passwords are masked in log messages."""
        log_filter = SensitiveDataFilter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Login with password=secret123",
            args=(),
            exc_info=None,
        )

        result = log_filter.filter(record)

        assert result is True
        assert "***MASKED***" in record.msg
        assert "secret123" not in record.msg

    def test_filter_api_key_in_message(self):
        """Test that API keys are masked in log messages."""
        log_filter = SensitiveDataFilter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Using api-key=sk-test123",
            args=(),
            exc_info=None,
        )

        result = log_filter.filter(record)

        assert result is True
        assert "***MASKED***" in record.msg
        assert "sk-test123" not in record.msg

    def test_filter_bearer_token_in_message(self):
        """Test that Bearer tokens are masked in log messages."""
        log_filter = SensitiveDataFilter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9",
            args=(),
            exc_info=None,
        )

        result = log_filter.filter(record)

        assert result is True
        assert "***MASKED***" in record.msg
        assert "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" not in record.msg

    def test_filter_sensitive_data_in_args(self):
        """Test that sensitive data is masked in log record args."""
        log_filter = SensitiveDataFilter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Request details: %s",
            args=("token=secret123",),
            exc_info=None,
        )

        result = log_filter.filter(record)

        assert result is True
        assert record.args is not None  # Type guard for ty
        assert "***MASKED***" in record.args[0]
        assert "secret123" not in record.args[0]

    def test_filter_non_string_args(self):
        """Test that non-string args are preserved unchanged."""
        log_filter = SensitiveDataFilter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Status code: %d",
            args=(200,),
            exc_info=None,
        )

        result = log_filter.filter(record)

        assert result is True
        assert record.args is not None  # Type guard for ty
        assert record.args[0] == 200


class TestLoggingSetup:
    """Test the logging setup functionality."""

    def setup_method(self):
        """Reset logging configuration before each test."""
        # Clear all existing handlers
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

    def test_setup_logging_default(self):
        """Test default logging setup."""
        setup_logging()

        root_logger = logging.getLogger()
        assert root_logger.level == logging.WARNING
        assert len(root_logger.handlers) >= 1

    def test_setup_logging_verbose(self):
        """Test verbose logging setup."""
        setup_logging(verbose=True)

        root_logger = logging.getLogger()
        assert root_logger.level == logging.INFO

    def test_setup_logging_debug(self):
        """Test debug logging setup."""
        setup_logging(debug=True)

        root_logger = logging.getLogger()
        assert root_logger.level == logging.DEBUG

    def test_setup_logging_specific_level(self):
        """Test setup with specific log level."""
        setup_logging(log_level="ERROR")

        root_logger = logging.getLogger()
        assert root_logger.level == logging.ERROR

    def test_setup_logging_no_file(self):
        """Test setup without file logging."""
        setup_logging(log_file=False)

        root_logger = logging.getLogger()
        # Should only have console handler
        rotating_handlers = [h for h in root_logger.handlers if isinstance(h, logging.handlers.RotatingFileHandler)]
        assert len(rotating_handlers) == 0

    @patch("youtrack_cli.logging._get_log_file_path")
    def test_setup_logging_with_file(self, mock_get_path):
        """Test setup with file logging."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            log_file = Path(tmp_dir) / "test.log"
            mock_get_path.return_value = log_file

            setup_logging(log_file=True)

            root_logger = logging.getLogger()
            # Should have both console and file handlers
            rotating_handlers = [h for h in root_logger.handlers if isinstance(h, logging.handlers.RotatingFileHandler)]
            assert len(rotating_handlers) >= 1


class TestLoggerRetrieval:
    """Test logger retrieval functionality."""

    def test_get_logger_with_name(self):
        """Test getting a logger with a specific name."""
        logger = get_logger("test.module")

        # Check that we get a logger instance
        assert hasattr(logger, "info")
        assert hasattr(logger, "debug")
        assert hasattr(logger, "error")
        assert "test.module" in str(logger)

    def test_get_logger_without_name(self):
        """Test getting a logger without specifying a name."""
        logger = get_logger()

        # Check that we get a logger instance
        assert hasattr(logger, "info")
        assert hasattr(logger, "debug")
        assert hasattr(logger, "error")
        # Should use the module name of the caller
        assert "test_logging" in str(logger)


class TestStructuredLogging:
    """Test structured logging functions."""

    def setup_method(self):
        """Set up logging for each test."""
        setup_logging(debug=True, log_file=False)

    def test_log_operation(self):
        """Test logging operations with structured context."""
        with patch("youtrack_cli.logging.get_logger") as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger

            log_operation("test_operation", user="test_user", project="test_project")

            mock_logger.info.assert_called_once_with(
                "Operation started",
                operation="test_operation",
                user="test_user",
                project="test_project",
            )

    def test_log_api_call_success(self):
        """Test logging successful API calls."""
        with patch("youtrack_cli.logging.get_logger") as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger

            log_api_call(
                method="GET",
                url="https://api.example.com/issues",
                status_code=200,
                duration=0.5,
            )

            mock_logger.debug.assert_called_once()
            args, kwargs = mock_logger.debug.call_args
            assert args[0] == "API call completed"
            assert kwargs["method"] == "GET"
            assert kwargs["status_code"] == 200
            assert kwargs["duration_ms"] == 500.0

    def test_log_api_call_error(self):
        """Test logging failed API calls."""
        with patch("youtrack_cli.logging.get_logger") as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger

            log_api_call(
                method="POST",
                url="https://api.example.com/issues",
                status_code=500,
                duration=1.2,
            )

            mock_logger.error.assert_called_once()
            args, kwargs = mock_logger.error.call_args
            assert args[0] == "API call failed"
            assert kwargs["method"] == "POST"
            assert kwargs["status_code"] == 500
            assert kwargs["duration_ms"] == 1200.0

    def test_log_api_call_masks_token_in_url(self):
        """Test that tokens in URLs are masked in logs."""
        with patch("youtrack_cli.logging.get_logger") as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger

            log_api_call(
                method="GET",
                url="https://api.example.com/issues?token=secret123&other=value",
                status_code=200,
            )

            mock_logger.debug.assert_called_once()
            args, kwargs = mock_logger.debug.call_args
            assert "secret123" not in kwargs["url"]
            assert "***MASKED***" in kwargs["url"]
            assert "other=value" in kwargs["url"]


class TestLogFilePath:
    """Test log file path functionality."""

    @patch.dict(os.environ, {"XDG_DATA_HOME": "/custom/data"})
    @patch("youtrack_cli.logging.Path.mkdir")
    def test_get_log_file_path_with_xdg(self, mock_mkdir):
        """Test log file path when XDG_DATA_HOME is set."""
        path = get_log_file_path()

        assert str(path).startswith("/custom/data/youtrack-cli")
        assert path.name == "youtrack-cli.log"
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

    @patch.dict(os.environ, {}, clear=True)
    @patch("youtrack_cli.logging.Path.home")
    @patch("youtrack_cli.logging.Path.mkdir")
    def test_get_log_file_path_without_xdg(self, mock_mkdir, mock_home):
        """Test log file path when XDG_DATA_HOME is not set."""
        mock_home.return_value = Path("/home/user")

        path = get_log_file_path()

        assert str(path).startswith("/home/user/.local/share/youtrack-cli")
        assert path.name == "youtrack-cli.log"
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

    @patch("youtrack_cli.logging.Path.mkdir")
    def test_get_log_file_path_creates_directory(self, mock_mkdir):
        """Test that log directory is created if it doesn't exist."""
        get_log_file_path()

        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)


class TestLoggingIntegration:
    """Integration tests for the logging system."""

    def test_sensitive_data_filter_integration(self):
        """Test that sensitive data filtering works end-to-end."""
        with tempfile.NamedTemporaryFile(mode="w+", delete=False) as temp_file:
            # Set up logging with a temporary file
            file_handler = logging.FileHandler(temp_file.name)
            file_handler.addFilter(SensitiveDataFilter())

            logger = logging.getLogger("test_integration")
            logger.addHandler(file_handler)
            logger.setLevel(logging.DEBUG)

            # Log a message with sensitive data
            logger.info("API request with token=secret123 and password=mypass")

            # Read the log file and verify sensitive data is masked
            temp_file.seek(0)
            log_content = temp_file.read()

            assert "***MASKED***" in log_content
            assert "secret123" not in log_content
            assert "mypass" not in log_content

            # Clean up
            os.unlink(temp_file.name)

    def test_structlog_configuration(self):
        """Test that structlog is configured correctly."""
        setup_logging(debug=True)

        # Test that structured logging works
        with patch("structlog.get_logger") as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger

            # Create a new logger to trigger the mock
            get_logger("test.new.module")

            mock_get_logger.assert_called_with("test.new.module")
