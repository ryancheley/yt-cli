"""Tests for common command utilities."""

from unittest.mock import MagicMock, patch

import click

from youtrack_cli.commands.common import confirm_action, format_output, handle_api_error


class TestHandleApiError:
    """Test handle_api_error function."""

    def test_handle_api_error_basic(self):
        """Test basic error handling."""
        ctx = MagicMock(spec=click.Context)
        error = Exception("Test error")

        with patch("youtrack_cli.commands.common.console") as mock_console:
            handle_api_error(error, ctx)

            mock_console.print.assert_called_once_with("[red]Error: Test error[/red]")
            ctx.exit.assert_called_once_with(1)

    def test_handle_api_error_with_different_error_types(self):
        """Test handling different error types."""
        ctx = MagicMock(spec=click.Context)
        errors = [
            ValueError("Value error"),
            RuntimeError("Runtime error"),
            Exception("Generic error"),
        ]

        with patch("youtrack_cli.commands.common.console") as mock_console:
            for error in errors:
                ctx.reset_mock()
                mock_console.reset_mock()

                handle_api_error(error, ctx)

                mock_console.print.assert_called_once_with(f"[red]Error: {error}[/red]")
                ctx.exit.assert_called_once_with(1)


class TestFormatOutput:
    """Test format_output function."""

    def test_format_output_no_data(self):
        """Test formatting with no data."""
        with patch("youtrack_cli.commands.common.console") as mock_console:
            format_output(None)
            mock_console.print.assert_called_once_with("[yellow]No data found[/yellow]")

    def test_format_output_empty_dict(self):
        """Test formatting with empty dict."""
        with patch("youtrack_cli.commands.common.console") as mock_console:
            format_output({})
            mock_console.print.assert_called_once_with("[yellow]No data found[/yellow]")

    def test_format_output_json(self):
        """Test JSON output formatting."""
        data = {"key": "value", "number": 42}

        with patch("youtrack_cli.commands.common.console") as mock_console:
            format_output(data, format_type="json")
            mock_console.print_json.assert_called_once_with(data=data)

    def test_format_output_table_default(self):
        """Test default table output formatting."""
        data = {"key": "value", "number": 42}

        with patch("youtrack_cli.commands.common.console") as mock_console:
            format_output(data)
            mock_console.print.assert_called_once_with(data)

    def test_format_output_table_explicit(self):
        """Test explicit table output formatting."""
        data = {"key": "value", "number": 42}

        with patch("youtrack_cli.commands.common.console") as mock_console:
            format_output(data, format_type="table")
            mock_console.print.assert_called_once_with(data)

    def test_format_output_unknown_format(self):
        """Test unknown format type defaults to table."""
        data = {"key": "value", "number": 42}

        with patch("youtrack_cli.commands.common.console") as mock_console:
            format_output(data, format_type="unknown")
            mock_console.print.assert_called_once_with(data)


class TestConfirmAction:
    """Test confirm_action function."""

    @patch("click.confirm")
    def test_confirm_action_default_false(self, mock_confirm):
        """Test confirmation with default False."""
        mock_confirm.return_value = True

        result = confirm_action("Are you sure?")

        assert result is True
        mock_confirm.assert_called_once_with("Are you sure?", default=False)

    @patch("click.confirm")
    def test_confirm_action_default_true(self, mock_confirm):
        """Test confirmation with default True."""
        mock_confirm.return_value = False

        result = confirm_action("Are you sure?", default=True)

        assert result is False
        mock_confirm.assert_called_once_with("Are you sure?", default=True)

    @patch("click.confirm")
    def test_confirm_action_user_accepts(self, mock_confirm):
        """Test when user accepts."""
        mock_confirm.return_value = True

        result = confirm_action("Delete item?")

        assert result is True

    @patch("click.confirm")
    def test_confirm_action_user_declines(self, mock_confirm):
        """Test when user declines."""
        mock_confirm.return_value = False

        result = confirm_action("Delete item?")

        assert result is False
