"""Users command group for YouTrack CLI."""

import asyncio
from typing import Optional

import click
from rich.prompt import Prompt

from ..auth import AuthManager
from ..console import get_console


@click.group()
def users() -> None:
    """User management."""
    pass


@users.command("list")
@click.option(
    "--fields",
    "-f",
    help="Comma-separated list of user fields to return",
)
@click.option(
    "--top",
    "-t",
    type=int,
    help="Maximum number of users to return",
)
@click.option(
    "--query",
    "-q",
    help="Search query to filter users",
)
@click.option(
    "--active-only",
    is_flag=True,
    default=False,
    help="Show only active (non-banned) users",
)
@click.option(
    "--format",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Output format",
)
@click.pass_context
def list_users(
    ctx: click.Context,
    fields: Optional[str],
    top: Optional[int],
    query: Optional[str],
    active_only: bool,
    format: str,
) -> None:
    """List all users."""
    from ..users import UserManager

    console = get_console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    user_manager = UserManager(auth_manager)

    console.print("👥 Fetching users...", style="blue")

    try:
        result = asyncio.run(user_manager.list_users(fields=fields, top=top, query=query, active_only=active_only))

        if result["status"] == "success":
            users = result["data"]

            if format == "table":
                user_manager.display_users_table(users)
                console.print(f"\n[dim]Total: {result['count']} users[/dim]")
            else:
                import json

                console.print(json.dumps(users, indent=2))
        else:
            console.print(f"❌ {result['message']}", style="red")
            raise click.ClickException("Failed to list users")

    except Exception as e:
        console.print(f"❌ Error listing users: {e}", style="red")
        raise click.ClickException("Failed to list users") from e


@users.command("create")
@click.argument("login")
@click.argument("full_name")
@click.argument("email")
@click.option(
    "--password",
    "-p",
    help="User password (will prompt if not provided)",
)
@click.option(
    "--banned",
    is_flag=True,
    help="Create user as banned",
)
@click.option(
    "--force-change-password",
    is_flag=True,
    help="Force password change on first login",
)
@click.pass_context
def create_user(
    ctx: click.Context,
    login: str,
    full_name: str,
    email: str,
    password: Optional[str],
    banned: bool,
    force_change_password: bool,
) -> None:
    """Create a new user.

    Creates a new user with the specified login, full name, and email.
    All three parameters are required as positional arguments.
    Password will be prompted interactively if not provided.

    Examples:
        # Create user with interactive password prompt
        yt users create testuser "Test User" "test@example.com"

        # Create user with password and options
        yt users create jdoe "John Doe" "john@company.com" --password secret123 --force-change-password

    Note: LOGIN, FULL_NAME, and EMAIL are all required positional arguments.
    Use quotes around full name if it contains spaces. Password will be prompted securely.
    """
    from ..users import UserManager

    console = get_console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    user_manager = UserManager(auth_manager)

    # Prompt for password if not provided
    if not password:
        password = Prompt.ask("Enter password for new user", password=True)
    elif password:
        # Show security warning when password is provided via command line
        console.print("⚠️  Warning: Password provided via command line may be visible in shell history", style="yellow")

    console.print(f"👤 Creating user '{login}'...", style="blue")

    try:
        result = asyncio.run(
            user_manager.create_user(
                login=login,
                full_name=full_name,
                email=email,
                password=password,
                banned=banned,
                force_change_password=force_change_password,
            )
        )

        if result["status"] == "success":
            console.print(f"✅ {result['message']}", style="green")
            user = result["data"]
            console.print(f"User ID: {user.get('id', 'N/A')}", style="blue")
            console.print(f"Login: {user.get('login', 'N/A')}", style="blue")
            console.print(f"Name: {user.get('name', user.get('fullName', 'N/A'))}", style="blue")
            console.print(f"Email: {user.get('email', 'N/A')}", style="blue")
        else:
            console.print(f"❌ {result['message']}", style="red")
            raise click.ClickException("Failed to create user")

    except Exception as e:
        console.print(f"❌ Error creating user: {e}", style="red")
        raise click.ClickException("Failed to create user") from e


@users.command(name="update")
@click.argument("user_id")
@click.option(
    "--full-name",
    "-n",
    help="New full name",
)
@click.option(
    "--email",
    "-e",
    help="New email address",
)
@click.option(
    "--password",
    "-p",
    help="New password",
)
@click.option(
    "--banned/--unbanned",
    default=None,
    help="Ban or unban the user",
)
@click.option(
    "--force-change-password",
    is_flag=True,
    help="Force password change on next login",
)
@click.option(
    "--show-details",
    is_flag=True,
    help="Show detailed user information",
)
@click.pass_context
def users_update(
    ctx: click.Context,
    user_id: str,
    full_name: Optional[str],
    email: Optional[str],
    password: Optional[str],
    banned: Optional[bool],
    force_change_password: bool,
    show_details: bool,
) -> None:
    """Update user information."""
    from ..users import UserManager

    console = get_console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    user_manager = UserManager(auth_manager)

    if show_details:
        console.print(f"👤 Fetching user '{user_id}' details...", style="blue")

        try:
            result = asyncio.run(user_manager.get_user(user_id))

            if result["status"] == "success":
                user_manager.display_user_details(result["data"])
            else:
                console.print(f"❌ {result['message']}", style="red")
                raise click.ClickException("Failed to get user details")

        except Exception as e:
            console.print(f"❌ Error getting user details: {e}", style="red")
            raise click.ClickException("Failed to get user details") from e
    else:
        if not any([full_name, email, password, banned is not None, force_change_password]):
            console.print("❌ No updates specified.", style="red")
            console.print(
                "Use --full-name, --email, --password, --banned/--unbanned, "
                "or --force-change-password options, "
                "or --show-details to view current settings.",
                style="blue",
            )
            return

        console.print(f"👤 Updating user '{user_id}'...", style="blue")

        try:
            result = asyncio.run(
                user_manager.update_user(
                    user_id=user_id,
                    full_name=full_name,
                    email=email,
                    password=password,
                    banned=banned,
                    force_change_password=(force_change_password if force_change_password else None),
                )
            )

            if result["status"] == "success":
                console.print(f"✅ {result['message']}", style="green")
                user = result["data"]
                console.print(f"Login: {user.get('login', 'N/A')}", style="blue")
                console.print(f"Full Name: {user.get('fullName', 'N/A')}", style="blue")
                console.print(f"Email: {user.get('email', 'N/A')}", style="blue")
            else:
                console.print(f"❌ {result['message']}", style="red")
                raise click.ClickException("Failed to update user")

        except Exception as e:
            console.print(f"❌ Error updating user: {e}", style="red")
            raise click.ClickException("Failed to update user") from e


@users.command()
@click.argument("user_id")
@click.option(
    "--action",
    "-a",
    type=click.Choice(["add_to_group", "remove_from_group"]),
    required=True,
    help="Permission action to perform (required)",
)
@click.option(
    "--group-id",
    "-g",
    help="Group ID for group operations",
)
@click.pass_context
def permissions(
    ctx: click.Context,
    user_id: str,
    action: str,
    group_id: Optional[str],
) -> None:
    """Manage user permissions.

    Manages user permissions by adding or removing users from groups.
    The --action parameter is required to specify the operation.

    Examples:
        # Add user to a group
        yt users permissions admin --action add_to_group --group-id developers

        # Remove user from a group
        yt users permissions john.doe --action remove_from_group --group-id testers

    Note: USER_ID is a positional argument, and --action is required.
    """
    from ..users import UserManager

    console = get_console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    user_manager = UserManager(auth_manager)

    console.print(f"🔐 Managing permissions for user '{user_id}'...", style="blue")

    try:
        result = asyncio.run(
            user_manager.manage_user_permissions(
                user_id=user_id,
                action=action,
                group_id=group_id,
            )
        )

        if result["status"] == "success":
            console.print(f"✅ {result['message']}", style="green")
        else:
            console.print(f"❌ {result['message']}", style="red")
            raise click.ClickException("Failed to manage user permissions")

    except Exception as e:
        console.print(f"❌ Error managing user permissions: {e}", style="red")
        raise click.ClickException("Failed to manage user permissions") from e


@users.command("groups")
@click.argument("user_id")
@click.option(
    "--format",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Output format",
)
@click.pass_context
def users_groups(ctx: click.Context, user_id: str, format: str) -> None:
    """Display groups that a user belongs to.

    Shows all groups the specified user is a member of, including group
    descriptions and permissions.

    Examples:
        # View user's groups in table format
        yt users groups john.doe

        # View user's groups in JSON format
        yt users groups admin --format json
    """
    from ..users import UserManager

    console = get_console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    user_manager = UserManager(auth_manager)

    console.print(f"👥 Fetching groups for user '{user_id}'...", style="blue")

    try:
        result = asyncio.run(user_manager.get_user_groups(user_id))

        if result["status"] == "success":
            groups = result["data"]

            if format == "table":
                user_manager.display_user_groups(groups, user_id)
                console.print(f"\n[dim]Total: {len(groups)} groups[/dim]")
            else:
                import json

                console.print(json.dumps(groups, indent=2))
        else:
            console.print(f"❌ {result['message']}", style="red")
            raise click.ClickException("Failed to get user groups")

    except Exception as e:
        console.print(f"❌ Error getting user groups: {e}", style="red")
        raise click.ClickException("Failed to get user groups") from e


@users.command("roles")
@click.argument("user_id")
@click.option(
    "--format",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Output format",
)
@click.pass_context
def users_roles(ctx: click.Context, user_id: str, format: str) -> None:
    """Display roles assigned to a user.

    Shows all roles assigned to the specified user, including role
    descriptions and permissions.

    Examples:
        # View user's roles in table format
        yt users roles john.doe

        # View user's roles in JSON format
        yt users roles admin --format json
    """
    from ..users import UserManager

    console = get_console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    user_manager = UserManager(auth_manager)

    console.print(f"🔐 Fetching roles for user '{user_id}'...", style="blue")

    try:
        result = asyncio.run(user_manager.get_user_roles(user_id))

        if result["status"] == "success":
            roles = result["data"]

            if format == "table":
                user_manager.display_user_roles(roles, user_id)
                console.print(f"\n[dim]Total: {len(roles)} roles[/dim]")
            else:
                import json

                console.print(json.dumps(roles, indent=2))
        else:
            console.print(f"❌ {result['message']}", style="red")
            raise click.ClickException("Failed to get user roles")

    except Exception as e:
        console.print(f"❌ Error getting user roles: {e}", style="red")
        raise click.ClickException("Failed to get user roles") from e


@users.command("teams")
@click.argument("user_id")
@click.option(
    "--format",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Output format",
)
@click.pass_context
def users_teams(ctx: click.Context, user_id: str, format: str) -> None:
    """Display teams that a user is a member of.

    Shows all teams the specified user belongs to, including team
    descriptions.

    Examples:
        # View user's teams in table format
        yt users teams john.doe

        # View user's teams in JSON format
        yt users teams jane.smith --format json
    """
    from ..users import UserManager

    console = get_console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    user_manager = UserManager(auth_manager)

    console.print(f"🏆 Fetching teams for user '{user_id}'...", style="blue")

    try:
        result = asyncio.run(user_manager.get_user_teams(user_id))

        if result["status"] == "success":
            teams = result["data"]

            if format == "table":
                user_manager.display_user_teams(teams, user_id)
                console.print(f"\n[dim]Total: {len(teams)} teams[/dim]")
            else:
                import json

                console.print(json.dumps(teams, indent=2))
        else:
            console.print(f"❌ {result['message']}", style="red")
            raise click.ClickException("Failed to get user teams")

    except Exception as e:
        console.print(f"❌ Error getting user teams: {e}", style="red")
        raise click.ClickException("Failed to get user teams") from e
