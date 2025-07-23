"""Progressive help system for YouTrack CLI.

This module provides a progressive help system that supports both basic and verbose help modes
to reduce cognitive load for new users while maintaining comprehensive help for advanced users.
"""

from __future__ import annotations

from typing import Any

import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text


class HelpContent:
    """Container for help content at different verbosity levels."""

    def __init__(
        self,
        basic_description: str,
        verbose_description: str | None = None,
        basic_options: list[str] | None = None,
        verbose_options: list[str] | None = None,
        basic_examples: list[str] | None = None,
        verbose_examples: list[str] | None = None,
    ):
        self.basic_description = basic_description
        self.verbose_description = verbose_description or basic_description
        self.basic_options = basic_options or []
        self.verbose_options = verbose_options or []
        self.basic_examples = basic_examples or []
        self.verbose_examples = verbose_examples or []


class ProgressiveHelpFormatter:
    """Enhanced help formatter that supports progressive help disclosure."""

    def __init__(self, console: Console | None = None):
        self.console = console or Console()
        self.verbose_mode = False

    def set_verbose_mode(self, verbose: bool):
        """Set the verbosity level for help output."""
        self.verbose_mode = verbose

    def format_command_help(
        self,
        ctx: click.Context,
        help_content: HelpContent,
        command_name: str,
    ) -> str:
        """Format help text for a command based on verbosity level."""
        # Get the appropriate description
        description = help_content.verbose_description if self.verbose_mode else help_content.basic_description

        # Get the appropriate options
        options = help_content.verbose_options if self.verbose_mode else help_content.basic_options

        # Get the appropriate examples
        examples = help_content.verbose_examples if self.verbose_mode else help_content.basic_examples

        # Build help text
        help_sections = []

        # Add description
        if description:
            help_sections.append(description)

        # Add usage information
        if ctx.info_name:
            usage = f"Usage: {ctx.info_name} {command_name} [OPTIONS]"
            help_sections.append(f"\n{usage}")

        # Add options
        if options:
            help_sections.append("\nOptions:")
            for option in options:
                help_sections.append(f"  {option}")

        # Add examples
        if examples:
            help_sections.append("\nExamples:")
            for example in examples:
                help_sections.append(f"  {example}")

        # Add verbosity hint if in basic mode
        if not self.verbose_mode:
            help_sections.append(f"\nFor more detailed help, use: {ctx.info_name} {command_name} --help-verbose")

        return "\n".join(help_sections)

    def format_group_help(
        self,
        ctx: click.Context,
        help_content: HelpContent,
        subcommands: dict[str, Any],
    ) -> str:
        """Format help text for a command group based on verbosity level."""
        # Get the appropriate description
        description = help_content.verbose_description if self.verbose_mode else help_content.basic_description

        help_sections = []

        # Add description
        if description:
            help_sections.append(description)

        # Add usage
        if ctx.info_name:
            usage = f"Usage: {ctx.info_name} [OPTIONS] COMMAND [ARGS]..."
            help_sections.append(f"\n{usage}")

        # Add commands section
        if subcommands:
            help_sections.append("\nCommands:")

            # In basic mode, show only essential commands
            # In verbose mode, show all commands
            if self.verbose_mode:
                for cmd_name, cmd in subcommands.items():
                    help_line = f"  {cmd_name:<15} {cmd.get_short_help_str(limit=60)}"
                    help_sections.append(help_line)
            else:
                # Show only the most commonly used commands in basic mode
                essential_commands = ["list", "create", "show", "update", "delete", "search", "status", "login", "help"]

                for cmd_name in essential_commands:
                    if cmd_name in subcommands:
                        cmd = subcommands[cmd_name]
                        help_line = f"  {cmd_name:<15} {cmd.get_short_help_str(limit=60)}"
                        help_sections.append(help_line)

                # Add hint about more commands
                hidden_count = len(subcommands) - len([cmd for cmd in essential_commands if cmd in subcommands])
                if hidden_count > 0:
                    help_sections.append(f"\n  ... and {hidden_count} more commands")

        # Add verbosity hint if in basic mode
        if not self.verbose_mode:
            help_sections.append(f"\nFor complete command list and details, use: {ctx.info_name} --help-verbose")

        return "\n".join(help_sections)

    def create_rich_help_panel(self, title: str, content: str, style: str = "blue") -> Panel:
        """Create a rich panel for help content."""
        return Panel(
            Text(content, style="white"),
            title=f"[{style}]{title}[/{style}]",
            border_style=style,
            padding=(1, 2),
        )


class ProgressiveHelpMixin:
    """Mixin class to add progressive help capabilities to Click commands."""

    def __init__(self, *args, **kwargs):
        self.help_content: HelpContent | None = kwargs.pop("help_content", None)
        super().__init__(*args, **kwargs)

    def get_help_record(self, ctx: click.Context) -> str | None:
        """Get help record with progressive disclosure."""
        if not hasattr(ctx, "obj") or not ctx.obj:
            return super().get_help_record(ctx)

        verbose_mode = ctx.obj.get("help_verbose", False)

        if self.help_content:
            formatter = ProgressiveHelpFormatter()
            formatter.set_verbose_mode(verbose_mode)

            if isinstance(self, click.Group):
                subcommands = {name: self.get_command(ctx, name) for name in self.list_commands(ctx)}
                return formatter.format_group_help(ctx, self.help_content, subcommands)
            return formatter.format_command_help(ctx, self.help_content, self.name or "command")

        return super().get_help_record(ctx)


def create_help_content(
    basic_desc: str,
    verbose_desc: str | None = None,
    basic_opts: list[str] | None = None,
    verbose_opts: list[str] | None = None,
    basic_examples: list[str] | None = None,
    verbose_examples: list[str] | None = None,
) -> HelpContent:
    """Helper function to create HelpContent instances."""
    return HelpContent(
        basic_description=basic_desc,
        verbose_description=verbose_desc,
        basic_options=basic_opts,
        verbose_options=verbose_opts,
        basic_examples=basic_examples,
        verbose_examples=verbose_examples,
    )


def add_help_verbose_option(func):
    """Decorator to add --help-verbose option to commands."""

    def callback(ctx: click.Context, param: click.Parameter, value: bool):
        if value:
            ctx.ensure_object(dict)
            ctx.obj["help_verbose"] = True
            # Show help and exit
            console = Console()
            console.print(ctx.get_help())
            ctx.exit()
        return value

    return click.option(
        "--help-verbose",
        is_flag=True,
        callback=callback,
        expose_value=False,
        is_eager=True,
        help="Show detailed help information with all commands and examples",
    )(func)


def check_help_verbose(ctx: click.Context, param: click.Parameter, value: bool) -> bool:
    """Callback to handle --help-verbose option."""
    if value:
        # Store verbose mode in context
        ctx.ensure_object(dict)
        ctx.obj["help_verbose"] = True

        # Show comprehensive help for main command
        show_verbose_main_help(ctx)
        ctx.exit()

    return value


def show_verbose_main_help(ctx: click.Context):
    """Show comprehensive help for the main command."""
    console = Console()

    # Main title and description
    console.print("\n[bold blue]YouTrack CLI[/bold blue] - Command line interface for JetBrains YouTrack\n")
    console.print("A powerful command line tool for managing YouTrack issues, projects, users,")
    console.print("time tracking, and more. Designed for developers and teams who want to integrate")
    console.print("YouTrack into their daily workflows and automation.\n")

    # Usage section
    console.print("[bold]Usage:[/bold] yt [OPTIONS] COMMAND [ARGS]...\n")

    # Getting Started section
    console.print("[bold]Getting Started:[/bold]")
    console.print("  # Interactive setup wizard")
    console.print("  yt setup")
    console.print("")
    console.print("  # Manual authentication")
    console.print("  yt auth login")
    console.print("")
    console.print("  # Test your setup")
    console.print("  yt projects list")
    console.print("")

    # Common Tasks section
    console.print("[bold]Common Tasks:[/bold]")
    console.print("  # List your assigned issues")
    console.print("  yt issues list --assignee me")
    console.print("")
    console.print("  # Create an issue")
    console.print('  yt issues create PROJECT-123 "Fix the bug" --type Bug --priority High')
    console.print("")
    console.print("  # Log work time")
    console.print('  yt time log ISSUE-456 "2h 30m" --description "Fixed the issue"')
    console.print("")
    console.print("  # View project details")
    console.print("  yt projects show PROJECT-123")
    console.print("")
    console.print("  # Search for issues")
    console.print('  yt issues search "API error priority:Critical"')
    console.print("")

    # Options section
    console.print("[bold]Options:[/bold]")
    console.print("  --version              Show version and exit")
    console.print("  -c, --config PATH      Path to configuration file")
    console.print("  -v, --verbose          Enable verbose output")
    console.print("  --debug               Enable debug output")
    console.print("  --no-progress         Disable progress indicators")
    console.print("  --secure              Enable enhanced security mode")
    console.print("  --help-verbose        Show this detailed help")
    console.print("  -h, --help            Show basic help and exit")
    console.print("")

    # Commands section
    if hasattr(ctx.command, "list_commands") and callable(getattr(ctx.command, "list_commands", None)):
        console.print("[bold]Commands:[/bold]")
        commands = ctx.command.list_commands(ctx)
        for cmd_name in sorted(commands):
            if hasattr(ctx.command, "get_command"):
                cmd = ctx.command.get_command(ctx, cmd_name)
                if cmd:
                    help_text = cmd.get_short_help_str(limit=60)
                    console.print(f"  {cmd_name:<15} {help_text}")
        console.print("")

    # Quick Reference section
    console.print("[bold]Quick Reference:[/bold]")
    console.print("  # Command aliases (use short forms)")
    console.print("  yt i = yt issues    |  yt p = yt projects  |  yt t = yt time")
    console.print("  yt u = yt users     |  yt a = yt articles  |  yt b = yt boards")
    console.print("")
    console.print("  # Get help for any command")
    console.print("  yt COMMAND --help")
    console.print("  yt COMMAND --help-verbose  # For detailed help")
    console.print("")
    console.print("  # Check authentication status")
    console.print("  yt auth status")
    console.print("")

    # Documentation
    console.print("[bold]Documentation:[/bold] https://yt-cli.readthedocs.io/")
    console.print("")

    # Tips
    console.print("[bold]Tips:[/bold]")
    console.print("  • Use 'yt setup' for first-time configuration")
    console.print("  • Most commands support both short (-o) and long (--option) flags")
    console.print("  • Use '--help-verbose' on any command for comprehensive help")
    console.print("  • Set YT_* environment variables for default configuration")
    console.print("")
