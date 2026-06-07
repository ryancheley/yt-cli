"""Boards command group for YouTrack CLI."""

import asyncio

import click

from ..auth import AuthManager
from ..console import get_console, print_status


@click.group()
def boards() -> None:
    """Agile board operations."""
    pass


@boards.command(name="list")
@click.option(
    "--project-id",
    "-p",
    help="Filter by project ID",
)
@click.option(
    "--format",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Output format",
)
@click.pass_context
def list_boards(
    ctx: click.Context,
    project_id: str | None,
    format: str,
) -> None:
    """List all agile boards."""
    from ..boards import BoardManager

    console = get_console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    board_manager = BoardManager(auth_manager)

    print_status("📋 Listing boards...", output_format=format)

    try:
        result = asyncio.run(board_manager.list_boards(project_id=project_id))

        if result["status"] == "success":
            if format == "json":
                console.print_json(data=result["boards"])
            # Table format is handled by the manager
        else:
            console.print(f"❌ {result['message']}", style="red")
            raise click.ClickException(result["message"])
    except Exception as e:
        console.print(f"❌ Error: {str(e)}", style="red")
        raise click.ClickException("Failed to list boards") from e


@boards.command(name="show")
@click.argument("board_id")
@click.option(
    "--format",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Output format",
)
@click.pass_context
def show_board(
    ctx: click.Context,
    board_id: str,
    format: str,
) -> None:
    """Show details of a specific agile board."""
    from ..boards import BoardManager

    console = get_console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    board_manager = BoardManager(auth_manager)

    print_status(f"👀 Viewing board {board_id}...", output_format=format)

    try:
        result = asyncio.run(board_manager.view_board(board_id))

        if result["status"] == "success":
            if format == "json":
                console.print_json(data=result["board"])
            # Table format is handled by the manager
        else:
            console.print(f"❌ {result['message']}", style="red")
            raise click.ClickException(result["message"])
    except Exception as e:
        console.print(f"❌ Error: {str(e)}", style="red")
        raise click.ClickException("Failed to view board") from e


@boards.command(name="view", hidden=True)
@click.argument("board_id")
@click.option(
    "--format",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Output format",
)
@click.pass_context
def view_board_alias(
    ctx: click.Context,
    board_id: str,
    format: str,
) -> None:
    """View details of a specific agile board (deprecated, use 'show' instead)."""
    ctx.invoke(show_board, board_id=board_id, format=format)


@boards.command(name="update")
@click.argument("board_id")
@click.option(
    "--name",
    "-n",
    help="New name for the board",
)
@click.pass_context
def update_board(
    ctx: click.Context,
    board_id: str,
    name: str | None,
) -> None:
    """Update an agile board configuration."""
    from ..boards import BoardManager

    console = get_console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    board_manager = BoardManager(auth_manager)

    console.print(f"🔄 Updating board {board_id}...", style="blue")

    try:
        result = asyncio.run(board_manager.update_board(board_id, name=name))

        if result["status"] == "success":
            console.print("✅ Board updated successfully", style="green")
        else:
            console.print(f"❌ {result['message']}", style="red")
            raise click.ClickException(result["message"])
    except Exception as e:
        console.print(f"❌ Error: {str(e)}", style="red")
        raise click.ClickException("Failed to update board") from e
