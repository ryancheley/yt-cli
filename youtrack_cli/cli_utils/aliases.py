"""Utilities for command aliases support."""

from typing import Optional

import click


class AliasedGroup(click.Group):
    """Click group that supports command aliases."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.aliases: dict[str, str] = {}

    def add_alias(self, alias: str, command_name: str) -> None:
        """Add an alias for a command."""
        self.aliases[alias] = command_name

    def get_command(self, ctx: click.Context, cmd_name: str) -> Optional[click.Command]:
        """Override to support aliases."""
        # Check if it's an alias first
        if cmd_name in self.aliases:
            cmd_name = self.aliases[cmd_name]
        return super().get_command(ctx, cmd_name)

    def list_commands(self, ctx: click.Context) -> list[str]:
        """List all commands, excluding aliases to avoid duplicates in help."""
        # Only return actual commands, not aliases
        # This prevents duplicates in help output while still allowing alias resolution
        return super().list_commands(ctx)
