"""Main entry point for the YouTrack CLI."""

import asyncio
from typing import Optional

import click
from rich.console import Console
from rich.prompt import Prompt

from .auth import AuthManager
from .config import ConfigManager


@click.group()
@click.version_option()
@click.option(
    "--config",
    "-c",
    type=click.Path(),
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


@projects.command()
@click.option(
    "--fields",
    "-f",
    help="Comma-separated list of project fields to return",
)
@click.option(
    "--top",
    "-t",
    type=int,
    help="Maximum number of projects to return",
)
@click.option(
    "--show-archived",
    is_flag=True,
    help="Include archived projects",
)
@click.option(
    "--format",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Output format",
)
@click.pass_context
def list(
    ctx: click.Context,
    fields: Optional[str],
    top: Optional[int],
    show_archived: bool,
    format: str,
) -> None:
    """List all projects."""
    from .projects import ProjectManager

    console = Console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    project_manager = ProjectManager(auth_manager)

    console.print("📋 Fetching projects...", style="blue")

    try:
        result = asyncio.run(
            project_manager.list_projects(
                fields=fields, top=top, show_archived=show_archived
            )
        )

        if result["status"] == "success":
            projects = result["data"]

            if format == "table":
                project_manager.display_projects_table(projects)
                console.print(f"\n[dim]Total: {result['count']} projects[/dim]")
            else:
                import json

                console.print(json.dumps(projects, indent=2))
        else:
            console.print(f"❌ {result['message']}", style="red")
            raise click.ClickException("Failed to list projects")

    except Exception as e:
        console.print(f"❌ Error listing projects: {e}", style="red")
        raise click.ClickException("Failed to list projects") from e


@projects.command()
@click.argument("name")
@click.argument("short_name")
@click.option(
    "--leader",
    "-l",
    prompt=True,
    help="Project leader username or ID",
)
@click.option(
    "--description",
    "-d",
    help="Project description",
)
@click.option(
    "--template",
    "-t",
    type=click.Choice(["scrum", "kanban"]),
    help="Project template",
)
@click.pass_context
def create(
    ctx: click.Context,
    name: str,
    short_name: str,
    leader: str,
    description: Optional[str],
    template: Optional[str],
) -> None:
    """Create a new project."""
    from .projects import ProjectManager

    console = Console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    project_manager = ProjectManager(auth_manager)

    console.print(f"🚀 Creating project '{name}'...", style="blue")

    try:
        result = asyncio.run(
            project_manager.create_project(
                name=name,
                short_name=short_name,
                leader_id=leader,
                description=description,
                template=template,
            )
        )

        if result["status"] == "success":
            console.print(f"✅ {result['message']}", style="green")
            project = result["data"]
            console.print(f"Project ID: {project.get('id', 'N/A')}", style="blue")
            console.print(
                f"Short Name: {project.get('shortName', 'N/A')}", style="blue"
            )
        else:
            console.print(f"❌ {result['message']}", style="red")
            raise click.ClickException("Failed to create project")

    except Exception as e:
        console.print(f"❌ Error creating project: {e}", style="red")
        raise click.ClickException("Failed to create project") from e


@projects.command()
@click.argument("project_id")
@click.option(
    "--name",
    "-n",
    help="New project name",
)
@click.option(
    "--description",
    "-d",
    help="New project description",
)
@click.option(
    "--leader",
    "-l",
    help="New project leader username or ID",
)
@click.option(
    "--show-details",
    is_flag=True,
    help="Show detailed project information",
)
@click.pass_context
def configure(
    ctx: click.Context,
    project_id: str,
    name: Optional[str],
    description: Optional[str],
    leader: Optional[str],
    show_details: bool,
) -> None:
    """Configure project settings."""
    from .projects import ProjectManager

    console = Console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    project_manager = ProjectManager(auth_manager)

    if show_details:
        console.print(f"📋 Fetching project '{project_id}' details...", style="blue")

        try:
            result = asyncio.run(project_manager.get_project(project_id))

            if result["status"] == "success":
                project_manager.display_project_details(result["data"])
            else:
                console.print(f"❌ {result['message']}", style="red")
                raise click.ClickException("Failed to get project details")

        except Exception as e:
            console.print(f"❌ Error getting project details: {e}", style="red")
            raise click.ClickException("Failed to get project details") from e
    else:
        if not any([name, description, leader]):
            console.print("❌ No configuration changes specified.", style="red")
            console.print(
                "Use --name, --description, or --leader options, "
                "or --show-details to view current settings.",
                style="blue",
            )
            return

        console.print(f"⚙️  Updating project '{project_id}'...", style="blue")

        try:
            result = asyncio.run(
                project_manager.update_project(
                    project_id=project_id,
                    name=name,
                    description=description,
                    leader_id=leader,
                )
            )

            if result["status"] == "success":
                console.print(f"✅ {result['message']}", style="green")
                project = result["data"]
                console.print(f"Name: {project.get('name', 'N/A')}", style="blue")
                leader_name = project.get("leader", {}).get("fullName", "N/A")
                console.print(f"Leader: {leader_name}", style="blue")
            else:
                console.print(f"❌ {result['message']}", style="red")
                raise click.ClickException("Failed to update project")

        except Exception as e:
            console.print(f"❌ Error updating project: {e}", style="red")
            raise click.ClickException("Failed to update project") from e


@projects.command()
@click.argument("project_id")
@click.option(
    "--confirm",
    is_flag=True,
    help="Skip confirmation prompt",
)
@click.pass_context
def archive(
    ctx: click.Context,
    project_id: str,
    confirm: bool,
) -> None:
    """Archive a project."""
    from .projects import ProjectManager

    console = Console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    project_manager = ProjectManager(auth_manager)

    if not confirm:
        confirmation_msg = f"Are you sure you want to archive project '{project_id}'?"
        if not click.confirm(confirmation_msg):
            console.print("Archive cancelled.", style="yellow")
            return

    console.print(f"📦 Archiving project '{project_id}'...", style="blue")

    try:
        result = asyncio.run(project_manager.archive_project(project_id))

        if result["status"] == "success":
            console.print(f"✅ {result['message']}", style="green")
            console.print(
                "Project has been archived and is no longer active.", style="yellow"
            )
        else:
            console.print(f"❌ {result['message']}", style="red")
            raise click.ClickException("Failed to archive project")

    except Exception as e:
        console.print(f"❌ Error archiving project: {e}", style="red")
        raise click.ClickException("Failed to archive project") from e


@main.group()
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
    format: str,
) -> None:
    """List all users."""
    from .users import UserManager

    console = Console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    user_manager = UserManager(auth_manager)

    console.print("👥 Fetching users...", style="blue")

    try:
        result = asyncio.run(
            user_manager.list_users(
                fields=fields, top=top, query=query
            )
        )

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
    """Create a new user."""
    from .users import UserManager

    console = Console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    user_manager = UserManager(auth_manager)

    # Prompt for password if not provided
    if not password:
        password = Prompt.ask("Enter password for new user", password=True)

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
            console.print(f"Email: {user.get('email', 'N/A')}", style="blue")
        else:
            console.print(f"❌ {result['message']}", style="red")
            raise click.ClickException("Failed to create user")

    except Exception as e:
        console.print(f"❌ Error creating user: {e}", style="red")
        raise click.ClickException("Failed to create user") from e


@users.command()
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
def update(
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
    from .users import UserManager

    console = Console()
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
        if not any([
            full_name,
            email,
            password,
            banned is not None,
            force_change_password
        ]):
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
                    force_change_password=(
                        force_change_password if force_change_password else None
                    ),
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
    help="Permission action to perform",
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
    """Manage user permissions."""
    from .users import UserManager

    console = Console()
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


@config.command()
@click.argument("key")
@click.argument("value")
@click.pass_context
def set(ctx: click.Context, key: str, value: str) -> None:
    """Set a configuration value."""
    console = Console()
    config_manager = ConfigManager(ctx.obj.get("config"))

    try:
        config_manager.set_config(key, value)
        console.print(f"✅ Set {key} = {value}", style="green")
    except Exception as e:
        console.print(f"❌ Error setting configuration: {e}", style="red")
        raise click.ClickException("Configuration set failed") from e


@config.command()
@click.argument("key")
@click.pass_context
def get(ctx: click.Context, key: str) -> None:
    """Get a configuration value."""
    console = Console()
    config_manager = ConfigManager(ctx.obj.get("config"))

    try:
        value = config_manager.get_config(key)
        if value is not None:
            console.print(f"{key} = {value}", style="blue")
        else:
            console.print(f"❌ Configuration key '{key}' not found", style="red")
            raise click.ClickException("Configuration key not found")
    except Exception as e:
        console.print(f"❌ Error getting configuration: {e}", style="red")
        raise click.ClickException("Configuration get failed") from e


@config.command("list")
@click.pass_context
def list_config(ctx: click.Context) -> None:
    """List all configuration values."""
    console = Console()
    config_manager = ConfigManager(ctx.obj.get("config"))

    try:
        config_values = config_manager.list_config()
        if config_values:
            console.print("📋 Configuration values:", style="blue bold")
            for key, value in sorted(config_values.items()):
                # Mask sensitive values
                sensitive_keys = ["token", "password", "secret"]
                if any(sensitive in key.lower() for sensitive in sensitive_keys):
                    if len(value) > 12:
                        masked_value = value[:8] + "..." + value[-4:]
                    else:
                        masked_value = "***"
                    console.print(f"  {key} = {masked_value}", style="yellow")
                else:
                    console.print(f"  {key} = {value}", style="blue")
        else:
            console.print("ℹ️  No configuration values found", style="yellow")
    except Exception as e:
        console.print(f"❌ Error listing configuration: {e}", style="red")
        raise click.ClickException("Configuration list failed") from e


@main.group()
def admin() -> None:
    """Administrative operations."""
    pass


if __name__ == "__main__":
    main()
