"""Main entry point for the YouTrack CLI."""

import asyncio
from typing import Optional

import click
from rich.console import Console
from rich.prompt import Prompt

from .auth import AuthManager


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
@click.pass_context
def auth(ctx: click.Context) -> None:
    """Authentication management."""
    pass


@auth.command()
@click.option(
    "--base-url",
    "-u",
    prompt=True,
    help="YouTrack instance URL (e.g., https://yourdomain.youtrack.cloud)",
)
@click.option("--token", "-t", prompt=True, hide_input=True, help="YouTrack API token")
@click.option("--username", "-n", help="Username (optional)")
@click.pass_context
def login(
    ctx: click.Context, base_url: str, token: str, username: Optional[str]
) -> None:
    """Authenticate with YouTrack."""
    console = Console()
    auth_manager = AuthManager(ctx.obj.get("config"))

    console.print("🔐 Authenticating with YouTrack...", style="blue")

    try:
        # Verify credentials
        result = asyncio.run(auth_manager.verify_credentials(base_url, token))

        if result["status"] == "success":
            # Save credentials
            auth_manager.save_credentials(base_url, token, username)

            console.print("✅ Authentication successful!", style="green")
            console.print(f"Logged in as: {result['username']}", style="green")
            console.print(f"Full name: {result['full_name']}", style="green")
            if result["email"]:
                console.print(f"Email: {result['email']}", style="green")
        else:
            console.print(f"❌ Authentication failed: {result['message']}", style="red")
            raise click.ClickException("Authentication failed")

    except Exception as e:
        console.print(f"❌ Error during authentication: {e}", style="red")
        raise click.ClickException("Authentication failed") from e


@auth.command()
@click.pass_context
def logout(ctx: click.Context) -> None:
    """Clear authentication credentials."""
    console = Console()
    auth_manager = AuthManager(ctx.obj.get("config"))

    # Check if credentials exist
    if not auth_manager.load_credentials():
        console.print("ℹ️  No authentication credentials found.", style="yellow")
        return

    # Confirm logout
    if not click.confirm("Are you sure you want to logout?"):
        console.print("Logout cancelled.", style="yellow")
        return

    # Clear credentials
    auth_manager.clear_credentials()
    console.print("✅ Successfully logged out.", style="green")


@auth.command()
@click.option("--show", is_flag=True, help="Show current token (masked)")
@click.option("--update", is_flag=True, help="Update the current token")
@click.pass_context
def token(ctx: click.Context, show: bool, update: bool) -> None:
    """Manage API tokens."""
    console = Console()
    auth_manager = AuthManager(ctx.obj.get("config"))

    if show:
        credentials = auth_manager.load_credentials()
        if not credentials:
            console.print("❌ No authentication credentials found.", style="red")
            console.print("Run 'yt auth login' to authenticate first.", style="blue")
            return

        # Show masked token
        masked_token = credentials.token[:8] + "..." + credentials.token[-4:]
        console.print(f"Current token: {masked_token}", style="blue")
        console.print(f"Base URL: {credentials.base_url}", style="blue")
        if credentials.username:
            console.print(f"Username: {credentials.username}", style="blue")

    elif update:
        credentials = auth_manager.load_credentials()
        if not credentials:
            console.print("❌ No authentication credentials found.", style="red")
            console.print("Run 'yt auth login' to authenticate first.", style="blue")
            return

        new_token = Prompt.ask("Enter new API token", password=True)

        console.print("🔐 Verifying new token...", style="blue")

        try:
            result = asyncio.run(
                auth_manager.verify_credentials(credentials.base_url, new_token)
            )

            if result["status"] == "success":
                auth_manager.save_credentials(
                    credentials.base_url, new_token, credentials.username
                )
                console.print("✅ Token updated successfully!", style="green")
            else:
                console.print(
                    f"❌ Token verification failed: {result['message']}", style="red"
                )
                raise click.ClickException("Token update failed")

        except Exception as e:
            console.print(f"❌ Error updating token: {e}", style="red")
            raise click.ClickException("Token update failed") from e

    else:
        console.print(
            "Use --show to display current token or --update to change it.",
            style="blue",
        )


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
