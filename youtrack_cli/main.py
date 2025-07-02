"""Main entry point for the YouTrack CLI."""

from typing import Optional

import click


@click.group()
@click.version_option()
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True),
    help="Path to configuration file",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose output",
)
@click.pass_context
def main(ctx: click.Context, config: Optional[str], verbose: bool) -> None:
    """YouTrack CLI - Command line interface for JetBrains YouTrack."""
    ctx.ensure_object(dict)
    ctx.obj["config"] = config
    ctx.obj["verbose"] = verbose


@main.group()
def issues() -> None:
    """Manage issues."""
    pass


@main.group()
def articles() -> None:
    """Manage knowledge base articles."""
    pass


@main.group()
def projects() -> None:
    """Manage projects."""
    pass


@main.group()
def users() -> None:
    """User management."""
    pass


@main.group()
def time() -> None:
    """Time tracking operations."""
    pass


@main.group()
def boards() -> None:
    """Agile board operations."""
    pass


@main.group()
def reports() -> None:
    """Generate cross-entity reports."""
    pass


@main.group()
def auth() -> None:
    """Authentication management."""
    pass


@main.group()
def config() -> None:
    """CLI configuration."""
    pass


@main.group()
def admin() -> None:
    """Administrative operations."""
    pass


if __name__ == "__main__":
    main()
