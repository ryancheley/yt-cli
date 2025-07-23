"""Utilities for command aliases support."""

import difflib
from typing import Optional

import click

from ..config import ConfigManager
from ..exceptions import CommandValidationError
from ..utils import display_error, handle_error


class AliasedGroup(click.Group):
    """Click group that supports command aliases."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.aliases: dict[str, str] = {}
        self.user_aliases: dict[str, str] = {}
        self._load_user_aliases()

    def _load_user_aliases(self) -> None:
        """Load user-defined aliases from configuration."""
        try:
            config = ConfigManager()
            self.user_aliases = config.list_aliases()
        except Exception:
            # If loading fails, continue without user aliases
            self.user_aliases = {}

    def add_alias(self, alias: str, command_name: str) -> None:
        """Add an alias for a command."""
        self.aliases[alias] = command_name

    def reload_user_aliases(self) -> None:
        """Reload user-defined aliases from configuration."""
        self._load_user_aliases()

    def get_command(self, ctx: click.Context, cmd_name: str) -> Optional[click.Command]:
        """Override to support aliases and provide helpful error messages."""
        # Check user-defined aliases first (they take precedence)
        if cmd_name in self.user_aliases:
            alias_command = self.user_aliases[cmd_name]
            # For now, only handle simple single-word aliases
            # Complex aliases will be handled by alias management commands
            if " " not in alias_command:
                cmd_name = alias_command
            else:
                # For complex aliases, we'll need special handling
                # This will be implemented in Phase 3 with alias management commands
                pass

        # Check built-in aliases
        if cmd_name in self.aliases:
            cmd_name = self.aliases[cmd_name]

        command = super().get_command(ctx, cmd_name)

        # If command not found, provide helpful suggestions
        if command is None:
            self._handle_command_not_found(ctx, cmd_name)

        return command

    def _handle_command_not_found(self, ctx: click.Context, cmd_name: str) -> None:
        """Handle command not found with helpful suggestions."""
        available_commands = self.list_commands(ctx)
        all_commands_and_aliases = available_commands + list(self.aliases.keys()) + list(self.user_aliases.keys())

        # Get suggestions using difflib
        suggestions = difflib.get_close_matches(cmd_name, all_commands_and_aliases, n=3, cutoff=0.6)

        # Handle common mistakes
        common_mistakes = {
            "version": "--version",
            "help": "--help",
            "h": "--help",
            "v": "--version",
        }

        if cmd_name in common_mistakes:
            suggestions = [common_mistakes[cmd_name]]

        # Create helpful error
        error = CommandValidationError(
            f"No such command '{cmd_name}'",
            command_path=f"{ctx.info_name} {cmd_name}",
            similar_commands=suggestions,
            usage_example=f"{ctx.info_name} --help" if not suggestions else f"{ctx.info_name} {suggestions[0]}",
        )

        error_result = handle_error(error, "command lookup")
        display_error(error_result)

        # Don't raise here, let Click handle it normally
        # This just provides additional helpful output

    def list_commands(self, ctx: click.Context) -> list[str]:
        """List all commands, excluding aliases to avoid duplicates in help."""
        # Only return actual commands, not aliases
        # This prevents duplicates in help output while still allowing alias resolution
        return super().list_commands(ctx)
