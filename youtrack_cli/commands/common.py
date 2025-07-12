"""Common utilities for command modules."""

from typing import Optional

import click

from ..console import get_console

console = get_console()


def handle_api_error(error: Exception, ctx: click.Context) -> None:
    """Common error handling for API operations."""
    console.print(f"[red]Error: {error}[/red]")
    ctx.exit(1)


def format_output(data: Optional[dict], format_type: str = "table") -> None:
    """Common output formatting."""
    if not data:
        console.print("[yellow]No data found[/yellow]")
        return

    if format_type == "json":
        console.print_json(data=data)
    else:
        # Default table formatting
        console.print(data)


def confirm_action(message: str, default: bool = False) -> bool:
    """Common confirmation prompt."""
    return click.confirm(message, default=default)
