"""Tests for common CLI options and decorators."""

import asyncio
from unittest.mock import MagicMock, patch

import pytest

from youtrack_cli.common import async_command, common_options, handle_exceptions, output_options


class TestCommonOptions:
    """Test common_options decorator."""

    def test_common_options_basic(self):
        """Test basic common options decorator."""

        @common_options
        def test_command(**kwargs):
            return kwargs

        # Create a mock function with the decorator
        with (
            patch("youtrack_cli.common.setup_logging") as mock_setup_logging,
            patch("youtrack_cli.common.get_console") as mock_get_console,
        ):
            mock_console = MagicMock()
            mock_get_console.return_value = mock_console

            result = test_command()

            # Check that setup_logging was called with defaults
            mock_setup_logging.assert_called_once_with(verbose=False, debug=False, log_level=None, log_file=True)

            # Check that default values were passed
            assert result["format"] == "table"
            assert result["verbose"] is False
            assert result["debug"] is False
            assert result["console"] == mock_console

    def test_common_options_with_values(self):
        """Test common options with custom values."""

        @common_options
        def test_command(**kwargs):
            return kwargs

        with (
            patch("youtrack_cli.common.setup_logging") as mock_setup_logging,
            patch("youtrack_cli.common.get_console") as mock_get_console,
        ):
            mock_console = MagicMock()
            mock_get_console.return_value = mock_console

            result = test_command(format="json", verbose=True, debug=True, log_level="DEBUG", no_log_file=True)

            # Check that setup_logging was called with custom values
            mock_setup_logging.assert_called_once_with(verbose=True, debug=True, log_level="DEBUG", log_file=False)

            # Check that values were passed correctly
            assert result["format"] == "json"
            assert result["verbose"] is True
            assert result["debug"] is True

    def test_common_options_no_color(self):
        """Test common options with no color flag."""

        @common_options
        def test_command(**kwargs):
            return kwargs

        with patch("youtrack_cli.common.setup_logging"), patch("rich.console.Console") as mock_console_class:
            mock_console = MagicMock()
            mock_console_class.return_value = mock_console

            result = test_command(no_color=True)

            # Check that Console was created with no color system
            mock_console_class.assert_called_once_with(color_system=None)
            assert result["console"] == mock_console

    def test_common_options_preserves_function_metadata(self):
        """Test that common options preserves function metadata."""

        @common_options
        def test_command():
            """Test command docstring."""
            pass

        assert test_command.__name__ == "test_command"
        assert test_command.__doc__ == "Test command docstring."


class TestOutputOptions:
    """Test output_options decorator."""

    def test_output_options_basic(self):
        """Test basic output options decorator."""

        @output_options
        def test_command(**kwargs):
            return kwargs

        result = test_command()
        assert result == {}

    def test_output_options_with_values(self):
        """Test output options with values."""

        @output_options
        def test_command(**kwargs):
            return kwargs

        result = test_command(output="/tmp/output.txt", limit=10, no_headers=True)

        assert result["output"] == "/tmp/output.txt"
        assert result["limit"] == 10
        assert result["no_headers"] is True

    def test_output_options_preserves_function_metadata(self):
        """Test that output options preserves function metadata."""

        @output_options
        def test_command():
            """Test command docstring."""
            pass

        assert test_command.__name__ == "test_command"
        assert test_command.__doc__ == "Test command docstring."


class TestAsyncCommand:
    """Test async_command decorator."""

    def test_async_command_basic(self):
        """Test basic async command decorator."""

        @async_command
        async def test_command():
            await asyncio.sleep(0)
            return "success"

        result = test_command()
        assert result == "success"

    def test_async_command_with_args(self):
        """Test async command with arguments."""

        @async_command
        async def test_command(arg1, arg2, kwarg1=None):
            await asyncio.sleep(0)
            return {"arg1": arg1, "arg2": arg2, "kwarg1": kwarg1}

        result = test_command("value1", "value2", kwarg1="kwvalue")
        assert result == {"arg1": "value1", "arg2": "value2", "kwarg1": "kwvalue"}

    def test_async_command_preserves_function_metadata(self):
        """Test that async command preserves function metadata."""

        @async_command
        async def test_command():
            """Test async command docstring."""
            pass

        assert test_command.__name__ == "test_command"
        assert test_command.__doc__ == "Test async command docstring."


class TestHandleExceptions:
    """Test handle_exceptions decorator."""

    def test_handle_exceptions_no_error(self):
        """Test handle exceptions when no error occurs."""

        @handle_exceptions
        def test_command():
            return "success"

        result = test_command()
        assert result == "success"

    def test_handle_exceptions_with_error(self):
        """Test handle exceptions when error occurs."""

        @handle_exceptions
        def test_command(**kwargs):
            raise ValueError("Test error")

        with (
            patch("youtrack_cli.utils.handle_error") as mock_handle_error,
            patch("youtrack_cli.utils.display_error") as mock_display_error,
            patch("youtrack_cli.common.get_console"),
            pytest.raises(SystemExit) as exc_info,
        ):
            test_command()

        # Check that error was handled
        mock_handle_error.assert_called_once()
        call_args = mock_handle_error.call_args[0]
        assert isinstance(call_args[0], ValueError)
        assert str(call_args[0]) == "Test error"
        assert call_args[1] == "test_command"

        # Check that error was displayed
        mock_display_error.assert_called_once()

        # Check that it exited with code 1
        assert exc_info.value.code == 1

    def test_handle_exceptions_with_console_kwarg(self):
        """Test handle exceptions with console in kwargs."""

        @handle_exceptions
        def test_command(**kwargs):
            raise RuntimeError("Test runtime error")

        mock_console = MagicMock()

        with (
            patch("youtrack_cli.utils.handle_error"),
            patch("youtrack_cli.utils.display_error"),
            patch("youtrack_cli.common.get_console") as mock_get_console,
            pytest.raises(SystemExit),
        ):
            test_command(console=mock_console)

        # get_console is called but the console from kwargs is used
        mock_get_console.assert_called_once()

    def test_handle_exceptions_preserves_function_metadata(self):
        """Test that handle exceptions preserves function metadata."""

        @handle_exceptions
        def test_command():
            """Test command docstring."""
            pass

        assert test_command.__name__ == "test_command"
        assert test_command.__doc__ == "Test command docstring."
