"""Tests for the progressive help system."""

from unittest.mock import MagicMock, patch

import click
import pytest
from rich.console import Console

from youtrack_cli.help_system import (
    HelpContent,
    ProgressiveHelpFormatter,
    ProgressiveHelpMixin,
    add_help_verbose_option,
    check_help_verbose,
    create_help_content,
    show_verbose_main_help,
)


class TestHelpContent:
    """Test HelpContent class."""

    def test_help_content_basic(self):
        """Test basic HelpContent creation."""
        content = HelpContent("Basic description")

        assert content.basic_description == "Basic description"
        assert content.verbose_description == "Basic description"
        assert content.basic_options == []
        assert content.verbose_options == []
        assert content.basic_examples == []
        assert content.verbose_examples == []

    def test_help_content_with_all_params(self):
        """Test HelpContent with all parameters."""
        content = HelpContent(
            basic_description="Basic desc",
            verbose_description="Verbose desc",
            basic_options=["--option1"],
            verbose_options=["--option1", "--option2"],
            basic_examples=["example1"],
            verbose_examples=["example1", "example2"],
        )

        assert content.basic_description == "Basic desc"
        assert content.verbose_description == "Verbose desc"
        assert content.basic_options == ["--option1"]
        assert content.verbose_options == ["--option1", "--option2"]
        assert content.basic_examples == ["example1"]
        assert content.verbose_examples == ["example1", "example2"]


class TestProgressiveHelpFormatter:
    """Test ProgressiveHelpFormatter class."""

    def test_formatter_initialization(self):
        """Test formatter initialization."""
        formatter = ProgressiveHelpFormatter()
        assert formatter.verbose_mode is False
        assert isinstance(formatter.console, Console)

    def test_formatter_with_custom_console(self):
        """Test formatter with custom console."""
        console = Console()
        formatter = ProgressiveHelpFormatter(console=console)
        assert formatter.console is console

    def test_set_verbose_mode(self):
        """Test setting verbose mode."""
        formatter = ProgressiveHelpFormatter()
        formatter.set_verbose_mode(True)
        assert formatter.verbose_mode is True

        formatter.set_verbose_mode(False)
        assert formatter.verbose_mode is False

    def test_format_command_help_basic(self):
        """Test basic command help formatting."""
        formatter = ProgressiveHelpFormatter()
        ctx = MagicMock(spec=click.Context)
        ctx.info_name = "yt"

        help_content = HelpContent(
            basic_description="Basic command description",
            basic_options=["--option1", "--option2"],
            basic_examples=["yt command example1"],
        )

        result = formatter.format_command_help(ctx, help_content, "test-command")

        assert "Basic command description" in result
        assert "Usage: yt test-command [OPTIONS]" in result
        assert "Options:" in result
        assert "--option1" in result
        assert "--option2" in result
        assert "Examples:" in result
        assert "yt command example1" in result
        assert "For more detailed help, use: yt test-command --help-verbose" in result

    def test_format_command_help_verbose(self):
        """Test verbose command help formatting."""
        formatter = ProgressiveHelpFormatter()
        formatter.set_verbose_mode(True)
        ctx = MagicMock(spec=click.Context)
        ctx.info_name = "yt"

        help_content = HelpContent(
            basic_description="Basic description",
            verbose_description="Detailed description",
            basic_options=["--option1"],
            verbose_options=["--option1", "--option2", "--verbose-option"],
            basic_examples=["basic example"],
            verbose_examples=["basic example", "advanced example"],
        )

        result = formatter.format_command_help(ctx, help_content, "test-command")

        assert "Detailed description" in result
        assert "--verbose-option" in result
        assert "advanced example" in result
        assert "For more detailed help" not in result

    def test_format_group_help_basic(self):
        """Test basic group help formatting."""
        formatter = ProgressiveHelpFormatter()
        ctx = MagicMock(spec=click.Context)
        ctx.info_name = "yt"

        help_content = HelpContent(basic_description="Group description")

        # Mock subcommands
        cmd1 = MagicMock()
        cmd1.get_short_help_str.return_value = "List items"
        cmd2 = MagicMock()
        cmd2.get_short_help_str.return_value = "Create items"
        cmd3 = MagicMock()
        cmd3.get_short_help_str.return_value = "Hidden command"

        subcommands = {
            "list": cmd1,
            "create": cmd2,
            "hidden": cmd3,
        }

        result = formatter.format_group_help(ctx, help_content, subcommands)

        assert "Group description" in result
        assert "Usage: yt [OPTIONS] COMMAND [ARGS]..." in result
        assert "Commands:" in result
        assert "list" in result
        assert "create" in result
        assert "List items" in result
        assert "Create items" in result
        # In basic mode, hidden command should not appear unless it's essential
        assert "... and 1 more commands" in result

    def test_format_group_help_verbose(self):
        """Test verbose group help formatting."""
        formatter = ProgressiveHelpFormatter()
        formatter.set_verbose_mode(True)
        ctx = MagicMock(spec=click.Context)
        ctx.info_name = "yt"

        help_content = HelpContent(basic_description="Group description")

        cmd1 = MagicMock()
        cmd1.get_short_help_str.return_value = "List items"
        cmd2 = MagicMock()
        cmd2.get_short_help_str.return_value = "Hidden command"

        subcommands = {
            "list": cmd1,
            "hidden": cmd2,
        }

        result = formatter.format_group_help(ctx, help_content, subcommands)

        # In verbose mode, all commands should be shown
        assert "list" in result
        assert "hidden" in result
        assert "Hidden command" in result
        assert "more commands" not in result

    def test_create_rich_help_panel(self):
        """Test rich help panel creation."""
        formatter = ProgressiveHelpFormatter()
        panel = formatter.create_rich_help_panel("Test Title", "Test content", "green")

        assert panel.title == "[green]Test Title[/green]"
        assert panel.border_style == "green"


class MockCommand(ProgressiveHelpMixin, click.Command):
    """Mock command for testing ProgressiveHelpMixin."""

    pass


class MockGroup(ProgressiveHelpMixin, click.Group):
    """Mock group for testing ProgressiveHelpMixin."""

    pass


class TestProgressiveHelpMixin:
    """Test ProgressiveHelpMixin class."""

    def test_mixin_initialization(self):
        """Test mixin initialization."""
        help_content = HelpContent("Test description")
        cmd = MockCommand("test", help_content=help_content)
        assert cmd.help_content is help_content

    def test_get_help_record_command(self):
        """Test get_help_record for command."""
        help_content = HelpContent("Test command description")
        cmd = MockCommand("test", help_content=help_content)
        ctx = MagicMock(spec=click.Context)
        ctx.obj = {"help_verbose": False}

        with patch.object(ProgressiveHelpFormatter, "format_command_help") as mock_format:
            mock_format.return_value = "formatted help"
            result = cmd.get_help_record(ctx)
            assert result == "formatted help"
            mock_format.assert_called_once()

    def test_get_help_record_group(self):
        """Test get_help_record for group."""
        help_content = HelpContent("Test group description")
        group = MockGroup("test", help_content=help_content)
        ctx = MagicMock(spec=click.Context)
        ctx.obj = {"help_verbose": True}

        group.list_commands = MagicMock(return_value=["cmd1", "cmd2"])
        group.get_command = MagicMock(return_value=MagicMock())

        with patch.object(ProgressiveHelpFormatter, "format_group_help") as mock_format:
            mock_format.return_value = "formatted group help"
            result = group.get_help_record(ctx)
            assert result == "formatted group help"
            mock_format.assert_called_once()


class TestHelperFunctions:
    """Test helper functions."""

    def test_create_help_content(self):
        """Test create_help_content helper function."""
        content = create_help_content(
            basic_desc="Basic",
            verbose_desc="Verbose",
            basic_opts=["--opt1"],
            verbose_opts=["--opt1", "--opt2"],
        )

        assert isinstance(content, HelpContent)
        assert content.basic_description == "Basic"
        assert content.verbose_description == "Verbose"
        assert content.basic_options == ["--opt1"]
        assert content.verbose_options == ["--opt1", "--opt2"]

    def test_add_help_verbose_option(self):
        """Test add_help_verbose_option decorator."""

        @add_help_verbose_option
        def test_command():
            pass

        # Check that the option was added
        assert hasattr(test_command, "__click_params__")
        params = test_command.__click_params__
        assert len(params) > 0

        # Find the help-verbose option
        help_verbose_param = None
        for param in params:
            if hasattr(param, "name") and param.name == "help_verbose":
                help_verbose_param = param
                break

        assert help_verbose_param is not None
        assert help_verbose_param.is_flag is True

    def test_check_help_verbose_false(self):
        """Test check_help_verbose callback with False value."""
        ctx = MagicMock(spec=click.Context)
        param = MagicMock(spec=click.Parameter)

        result = check_help_verbose(ctx, param, False)
        assert result is False

    def test_check_help_verbose_true(self):
        """Test check_help_verbose callback with True value."""
        ctx = MagicMock(spec=click.Context)
        ctx.obj = {}
        param = MagicMock(spec=click.Parameter)

        with patch("youtrack_cli.help_system.show_verbose_main_help") as mock_show_help:
            # Mock ctx.exit to raise SystemExit
            ctx.exit.side_effect = SystemExit(0)

            with pytest.raises(SystemExit):
                check_help_verbose(ctx, param, True)

            mock_show_help.assert_called_once_with(ctx)
            assert ctx.obj["help_verbose"] is True

    def test_show_verbose_main_help(self):
        """Test show_verbose_main_help function."""
        ctx = MagicMock(spec=click.Context)

        # Create a mock command with list_commands and get_command methods
        mock_command = MagicMock()
        mock_command.list_commands.return_value = ["issues", "projects"]

        mock_issues_cmd = MagicMock()
        mock_issues_cmd.get_short_help_str.return_value = "Manage issues"
        mock_projects_cmd = MagicMock()
        mock_projects_cmd.get_short_help_str.return_value = "Manage projects"

        def mock_get_command(ctx, name):
            if name == "issues":
                return mock_issues_cmd
            elif name == "projects":
                return mock_projects_cmd
            return None

        mock_command.get_command = mock_get_command
        ctx.command = mock_command

        with patch("youtrack_cli.help_system.Console") as mock_console_class:
            mock_console = MagicMock()
            mock_console_class.return_value = mock_console

            show_verbose_main_help(ctx)

            # Verify console.print was called multiple times
            assert mock_console.print.call_count > 10

            # Check some key content was printed
            calls = [call[0][0] for call in mock_console.print.call_args_list]
            content = " ".join(str(call) for call in calls)

            assert "YouTrack CLI" in content
            assert "Usage:" in content
            assert "Getting Started:" in content
            assert "Commands:" in content

    def test_show_verbose_main_help_no_commands(self):
        """Test show_verbose_main_help with no commands."""
        ctx = MagicMock(spec=click.Context)
        ctx.command = MagicMock()
        # Make the command not have list_commands or make it not callable
        del ctx.command.list_commands

        with patch("youtrack_cli.help_system.Console") as mock_console_class:
            mock_console = MagicMock()
            mock_console_class.return_value = mock_console

            show_verbose_main_help(ctx)

            # Should still print help content, just without the commands section
            assert mock_console.print.call_count > 5
