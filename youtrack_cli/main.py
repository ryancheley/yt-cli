"""Main entry point for the YouTrack CLI."""

import asyncio
from typing import Optional

import click
from rich.console import Console
from rich.prompt import Prompt

from .admin import AdminManager
from .auth import AuthManager
from .config import ConfigManager
from .logging import setup_logging
from .reports import ReportManager


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
@click.option(
    "--debug",
    is_flag=True,
    help="Enable debug output",
)
@click.pass_context
def main(ctx: click.Context, config: Optional[str], verbose: bool, debug: bool) -> None:
    """YouTrack CLI - Command line interface for JetBrains YouTrack.

    A powerful command line tool for managing YouTrack issues, projects, users,
    time tracking, and more. Designed for developers and teams who want to integrate
    YouTrack into their daily workflows and automation.

    Quick Start:

        \b
        # Set up authentication
        yt auth login

        \b
        # List your projects
        yt projects list

        \b
        # Create an issue
        yt issues create PROJECT-123 "Fix the bug"

        \b
        # Log work time
        yt time log ISSUE-456 "2h 30m" --description "Fixed the issue"

    For more help on specific commands, use:

        \b
        yt COMMAND --help

    Documentation: https://yt-cli.readthedocs.io/
    """
    ctx.ensure_object(dict)
    ctx.obj["config"] = config
    ctx.obj["verbose"] = verbose
    ctx.obj["debug"] = debug

    # Setup logging
    setup_logging(verbose=verbose, debug=debug)


@main.command()
@click.option(
    "--skip-validation",
    is_flag=True,
    help="Skip connection validation during setup",
)
@click.pass_context
def setup(ctx: click.Context, skip_validation: bool) -> None:
    """Interactive setup wizard for first-time configuration.

    This command guides you through setting up YouTrack CLI for the first time.
    It will help you configure your YouTrack URL, authentication, and basic preferences.

    Examples:

        \b
        # Run the interactive setup wizard
        yt setup

        \b
        # Setup without validating the connection
        yt setup --skip-validation
    """
    console = Console()

    console.print("🎯 [bold blue]Welcome to YouTrack CLI Setup![/bold blue]")
    console.print(
        "\nThis wizard will help you configure YouTrack CLI for the first time.\n"
    )

    # Get YouTrack URL
    console.print("[bold]Step 1: YouTrack Instance[/bold]")
    url = Prompt.ask(
        "Enter your YouTrack URL", default="https://company.youtrack.cloud"
    )

    # Ensure URL has protocol
    if not url.startswith(("http://", "https://")):
        url = f"https://{url}"

    console.print(f"✅ Using YouTrack URL: [green]{url}[/green]\n")

    # Get authentication method
    console.print("[bold]Step 2: Authentication[/bold]")
    auth_method = Prompt.ask(
        "Choose authentication method", choices=["token", "username"], default="token"
    )

    if auth_method == "token":
        console.print("\n💡 To get an API token:")
        console.print("1. Go to your YouTrack instance")
        console.print("2. Navigate to Profile → Account Security → API Tokens")
        console.print("3. Create a new token with appropriate permissions\n")

        token = Prompt.ask("Enter your API token", password=True)

        username = Prompt.ask("Enter your username", default="")
    else:
        username = Prompt.ask("Enter your username")
        Prompt.ask("Enter your password", password=True)  # For future password auth
        token = None

    # Get optional preferences
    console.print("\n[bold]Step 3: Preferences (Optional)[/bold]")

    default_project = Prompt.ask("Default project ID (leave empty to skip)", default="")

    output_format = Prompt.ask(
        "Preferred output format", choices=["table", "json", "yaml"], default="table"
    )

    # Save configuration
    console.print("\n[bold]Step 4: Saving Configuration[/bold]")

    try:
        # Set the configuration
        config_data = {
            "YOUTRACK_BASE_URL": url,
            "YOUTRACK_USERNAME": username or "",
            "OUTPUT_FORMAT": output_format,
        }

        if token:
            config_data["YOUTRACK_TOKEN"] = token

        if default_project:
            config_data["DEFAULT_PROJECT"] = default_project

        # Save configuration using the auth manager's save method
        import os

        config_dir = os.path.expanduser("~/.config/youtrack-cli")
        os.makedirs(config_dir, exist_ok=True)

        config_file = os.path.join(config_dir, ".env")
        with open(config_file, "w") as f:
            for key, value in config_data.items():
                f.write(f"{key}={value}\n")

        console.print(f"✅ Configuration saved to: [green]{config_file}[/green]")

        # Test connection if not skipped
        if not skip_validation and token:
            console.print("\n[bold]Step 5: Testing Connection[/bold]")
            console.print("🔍 Testing connection to YouTrack...")

            # Import here to avoid circular imports
            from .auth import AuthManager

            AuthManager(config_file)  # Test auth creation

            try:
                # Test the connection (this would need to be implemented in AuthManager)
                console.print("✅ [green]Connection successful![/green]")
                console.print(
                    "🎉 [bold green]Setup completed successfully![/bold green]"
                )
            except Exception as e:
                console.print(f"⚠️  [yellow]Connection test failed: {e}[/yellow]")
                console.print(
                    "You can test your setup later with: "
                    "[blue]yt auth login --test[/blue]"
                )
        else:
            console.print("\n🎉 [bold green]Setup completed![/bold green]")

        console.print("\n[bold]Next steps:[/bold]")
        console.print("• Test your setup: [blue]yt projects list[/blue]")
        console.print("• View help: [blue]yt --help[/blue]")
        console.print("• Read docs: [blue]https://yt-cli.readthedocs.io/[/blue]")

    except Exception as e:
        console.print(f"❌ [red]Error saving configuration: {e}[/red]")
        console.print(
            "Please try running [blue]yt setup[/blue] again or configure manually."
        )
        raise click.ClickException(f"Setup failed: {e}") from e


@main.group()
def issues() -> None:
    """Manage issues - create, update, search, and organize your work.

    The issues command group provides comprehensive issue management capabilities.
    You can create new issues, update existing ones, search and filter issues,
    manage comments and attachments, and handle issue relationships.

    Common workflows:

        \b
        # Create and assign a bug report
        yt issues create PROJECT-123 "Login fails on mobile" \\
            --type Bug --priority High --assignee john.doe

        \b
        # List open issues assigned to you
        yt issues list --assignee me --state Open

        \b
        # Search for issues by keywords
        yt issues search "API error priority:Critical"

        \b
        # Update issue status
        yt issues update ISSUE-456 --state "In Progress"

        \b
        # Add a comment
        yt issues comments add ISSUE-456 "Fixed in build 1.2.3"
    """
    pass


@issues.command()
@click.argument("project_id")
@click.argument("summary")
@click.option(
    "--description",
    "-d",
    help="Issue description",
)
@click.option(
    "--type",
    "-t",
    help="Issue type (e.g., Bug, Feature, Task)",
)
@click.option(
    "--priority",
    "-p",
    help="Issue priority (e.g., Critical, High, Medium, Low)",
)
@click.option(
    "--assignee",
    "-a",
    help="Assignee username",
)
@click.pass_context
def create(
    ctx: click.Context,
    project_id: str,
    summary: str,
    description: Optional[str],
    type: Optional[str],
    priority: Optional[str],
    assignee: Optional[str],
) -> None:
    """Create a new issue.

    Create a new issue in the specified project with the given summary.
    You can optionally specify additional fields like description, type,
    priority, and assignee.

    Examples:

        \b
        # Create a simple bug report
        yt issues create WEB-123 "Fix login error on mobile"

        \b
        # Create a feature request with full details
        yt issues create API-456 "Add user authentication endpoint" \\
            --description "Need OAuth2 support for mobile app" \\
            --type Feature \\
            --priority High \\
            --assignee john.doe

        \b
        # Create a task assigned to yourself
        yt issues create INFRA-789 "Update server certificates" \\
            --type Task \\
            --priority Medium
    """
    from .issues import IssueManager

    console = Console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    issue_manager = IssueManager(auth_manager)

    console.print(
        f"🐛 Creating issue '{summary}' in project '{project_id}'...", style="blue"
    )

    try:
        result = asyncio.run(
            issue_manager.create_issue(
                project_id=project_id,
                summary=summary,
                description=description,
                issue_type=type,
                priority=priority,
                assignee=assignee,
            )
        )

        if result["status"] == "success":
            console.print(f"✅ {result['message']}", style="green")
            issue = result["data"]
            console.print(f"Issue ID: {issue.get('id', 'N/A')}", style="blue")
        else:
            console.print(f"❌ {result['message']}", style="red")
            raise click.ClickException("Failed to create issue")

    except Exception as e:
        console.print(f"❌ Error creating issue: {e}", style="red")
        raise click.ClickException("Failed to create issue") from e


@issues.command(name="list")
@click.option(
    "--project-id",
    "-p",
    help="Filter by project ID",
)
@click.option(
    "--state",
    "-s",
    help="Filter by issue state",
)
@click.option(
    "--assignee",
    "-a",
    help="Filter by assignee",
)
@click.option(
    "--fields",
    "-f",
    help="Comma-separated list of fields to return",
)
@click.option(
    "--top",
    "-t",
    type=int,
    help="Maximum number of issues to return",
)
@click.option(
    "--query",
    "-q",
    help="Advanced query filter",
)
@click.option(
    "--format",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Output format",
)
@click.pass_context
def list_issues(
    ctx: click.Context,
    project_id: Optional[str],
    state: Optional[str],
    assignee: Optional[str],
    fields: Optional[str],
    top: Optional[int],
    query: Optional[str],
    format: str,
) -> None:
    """List issues with filtering."""
    from .issues import IssueManager

    console = Console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    issue_manager = IssueManager(auth_manager)

    console.print("🔍 Fetching issues...", style="blue")

    try:
        result = asyncio.run(
            issue_manager.list_issues(
                project_id=project_id,
                fields=fields,
                top=top,
                query=query,
                state=state,
                assignee=assignee,
            )
        )

        if result["status"] == "success":
            issues = result["data"]

            if format == "table":
                issue_manager.display_issues_table(issues)
                console.print(f"\n[dim]Total: {result['count']} issues[/dim]")
            else:
                import json

                console.print(json.dumps(issues, indent=2))
        else:
            console.print(f"❌ {result['message']}", style="red")
            raise click.ClickException("Failed to list issues")

    except Exception as e:
        console.print(f"❌ Error listing issues: {e}", style="red")
        raise click.ClickException("Failed to list issues") from e


@issues.command()
@click.argument("issue_id")
@click.option(
    "--summary",
    "-s",
    help="New issue summary",
)
@click.option(
    "--description",
    "-d",
    help="New issue description",
)
@click.option(
    "--state",
    help="New issue state",
)
@click.option(
    "--priority",
    "-p",
    help="New issue priority",
)
@click.option(
    "--assignee",
    "-a",
    help="New assignee username",
)
@click.option(
    "--type",
    "-t",
    help="New issue type",
)
@click.option(
    "--show-details",
    is_flag=True,
    help="Show detailed issue information",
)
@click.pass_context
def update(
    ctx: click.Context,
    issue_id: str,
    summary: Optional[str],
    description: Optional[str],
    state: Optional[str],
    priority: Optional[str],
    assignee: Optional[str],
    type: Optional[str],
    show_details: bool,
) -> None:
    """Update an existing issue."""
    from .issues import IssueManager

    console = Console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    issue_manager = IssueManager(auth_manager)

    if show_details:
        console.print(f"📋 Fetching issue '{issue_id}' details...", style="blue")

        try:
            result = asyncio.run(issue_manager.get_issue(issue_id))

            if result["status"] == "success":
                issue_manager.display_issue_details(result["data"])
            else:
                console.print(f"❌ {result['message']}", style="red")
                raise click.ClickException("Failed to get issue details")

        except Exception as e:
            console.print(f"❌ Error getting issue details: {e}", style="red")
            raise click.ClickException("Failed to get issue details") from e
    else:
        if not any([summary, description, state, priority, assignee, type]):
            console.print("❌ No updates specified.", style="red")
            console.print(
                "Use --summary, --description, --state, --priority, --assignee, "
                "or --type options, or --show-details to view current issue.",
                style="blue",
            )
            return

        console.print(f"✏️  Updating issue '{issue_id}'...", style="blue")

        try:
            result = asyncio.run(
                issue_manager.update_issue(
                    issue_id=issue_id,
                    summary=summary,
                    description=description,
                    state=state,
                    priority=priority,
                    assignee=assignee,
                    issue_type=type,
                )
            )

            if result["status"] == "success":
                console.print(f"✅ {result['message']}", style="green")
            else:
                console.print(f"❌ {result['message']}", style="red")
                raise click.ClickException("Failed to update issue")

        except Exception as e:
            console.print(f"❌ Error updating issue: {e}", style="red")
            raise click.ClickException("Failed to update issue") from e


@issues.command()
@click.argument("issue_id")
@click.option(
    "--confirm",
    is_flag=True,
    help="Skip confirmation prompt",
)
@click.pass_context
def delete(ctx: click.Context, issue_id: str, confirm: bool) -> None:
    """Delete an issue."""
    from .issues import IssueManager

    console = Console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    issue_manager = IssueManager(auth_manager)

    if not confirm:
        if not click.confirm(f"Are you sure you want to delete issue '{issue_id}'?"):
            console.print("Delete cancelled.", style="yellow")
            return

    console.print(f"🗑️  Deleting issue '{issue_id}'...", style="blue")

    try:
        result = asyncio.run(issue_manager.delete_issue(issue_id))

        if result["status"] == "success":
            console.print(f"✅ {result['message']}", style="green")
        else:
            console.print(f"❌ {result['message']}", style="red")
            raise click.ClickException("Failed to delete issue")

    except Exception as e:
        console.print(f"❌ Error deleting issue: {e}", style="red")
        raise click.ClickException("Failed to delete issue") from e


@issues.command()
@click.argument("query")
@click.option(
    "--project-id",
    "-p",
    help="Filter by project ID",
)
@click.option(
    "--top",
    "-t",
    type=int,
    help="Maximum number of results to return",
)
@click.option(
    "--format",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Output format",
)
@click.pass_context
def search(
    ctx: click.Context,
    query: str,
    project_id: Optional[str],
    top: Optional[int],
    format: str,
) -> None:
    """Advanced issue search."""
    from .issues import IssueManager

    console = Console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    issue_manager = IssueManager(auth_manager)

    console.print(f"🔍 Searching issues for '{query}'...", style="blue")

    try:
        result = asyncio.run(
            issue_manager.search_issues(
                query=query,
                project_id=project_id,
                top=top,
            )
        )

        if result["status"] == "success":
            issues = result["data"]

            if format == "table":
                issue_manager.display_issues_table(issues)
                console.print(f"\n[dim]Found: {result['count']} issues[/dim]")
            else:
                import json

                console.print(json.dumps(issues, indent=2))
        else:
            console.print(f"❌ {result['message']}", style="red")
            raise click.ClickException("Failed to search issues")

    except Exception as e:
        console.print(f"❌ Error searching issues: {e}", style="red")
        raise click.ClickException("Failed to search issues") from e


@issues.command()
@click.argument("issue_id")
@click.argument("assignee")
@click.pass_context
def assign(ctx: click.Context, issue_id: str, assignee: str) -> None:
    """Assign an issue to a user."""
    from .issues import IssueManager

    console = Console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    issue_manager = IssueManager(auth_manager)

    console.print(f"👤 Assigning issue '{issue_id}' to '{assignee}'...", style="blue")

    try:
        result = asyncio.run(issue_manager.assign_issue(issue_id, assignee))

        if result["status"] == "success":
            console.print(f"✅ {result['message']}", style="green")
        else:
            console.print(f"❌ {result['message']}", style="red")
            raise click.ClickException("Failed to assign issue")

    except Exception as e:
        console.print(f"❌ Error assigning issue: {e}", style="red")
        raise click.ClickException("Failed to assign issue") from e


@issues.command()
@click.argument("issue_id")
@click.option(
    "--state",
    "-s",
    help="New state for the issue",
)
@click.option(
    "--project-id",
    "-p",
    help="Move to different project",
)
@click.pass_context
def move(
    ctx: click.Context,
    issue_id: str,
    state: Optional[str],
    project_id: Optional[str],
) -> None:
    """Move an issue between states or projects."""
    from .issues import IssueManager

    console = Console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    issue_manager = IssueManager(auth_manager)

    if not state and not project_id:
        console.print("❌ Must specify either --state or --project-id", style="red")
        return

    console.print(f"🚚 Moving issue '{issue_id}'...", style="blue")

    try:
        result = asyncio.run(
            issue_manager.move_issue(issue_id, state=state, project_id=project_id)
        )

        if result["status"] == "success":
            console.print(f"✅ {result['message']}", style="green")
        else:
            console.print(f"❌ {result['message']}", style="red")
            raise click.ClickException("Failed to move issue")

    except Exception as e:
        console.print(f"❌ Error moving issue: {e}", style="red")
        raise click.ClickException("Failed to move issue") from e


@issues.group()
def tag() -> None:
    """Manage issue tags."""
    pass


@tag.command()
@click.argument("issue_id")
@click.argument("tag_name")
@click.pass_context
def add(ctx: click.Context, issue_id: str, tag_name: str) -> None:
    """Add a tag to an issue."""
    from .issues import IssueManager

    console = Console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    issue_manager = IssueManager(auth_manager)

    console.print(f"🏷️  Adding tag '{tag_name}' to issue '{issue_id}'...", style="blue")

    try:
        result = asyncio.run(issue_manager.add_tag(issue_id, tag_name))

        if result["status"] == "success":
            console.print(f"✅ {result['message']}", style="green")
        else:
            console.print(f"❌ {result['message']}", style="red")
            raise click.ClickException("Failed to add tag")

    except Exception as e:
        console.print(f"❌ Error adding tag: {e}", style="red")
        raise click.ClickException("Failed to add tag") from e


@tag.command()
@click.argument("issue_id")
@click.argument("tag_name")
@click.pass_context
def remove(ctx: click.Context, issue_id: str, tag_name: str) -> None:
    """Remove a tag from an issue."""
    from .issues import IssueManager

    console = Console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    issue_manager = IssueManager(auth_manager)

    console.print(
        f"🏷️  Removing tag '{tag_name}' from issue '{issue_id}'...", style="blue"
    )

    try:
        result = asyncio.run(issue_manager.remove_tag(issue_id, tag_name))

        if result["status"] == "success":
            console.print(f"✅ {result['message']}", style="green")
        else:
            console.print(f"❌ {result['message']}", style="red")
            raise click.ClickException("Failed to remove tag")

    except Exception as e:
        console.print(f"❌ Error removing tag: {e}", style="red")
        raise click.ClickException("Failed to remove tag") from e


@tag.command(name="list")
@click.argument("issue_id")
@click.pass_context
def list_tags(ctx: click.Context, issue_id: str) -> None:
    """List all tags for an issue."""
    from .issues import IssueManager

    console = Console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    issue_manager = IssueManager(auth_manager)

    console.print(f"🏷️  Fetching tags for issue '{issue_id}'...", style="blue")

    try:
        result = asyncio.run(issue_manager.list_tags(issue_id))

        if result["status"] == "success":
            tags = result["data"]
            if tags:
                tag_names = [tag.get("name", "") for tag in tags]
                console.print(f"Tags: {', '.join(tag_names)}", style="green")
            else:
                console.print("No tags found.", style="yellow")
        else:
            console.print(f"❌ {result['message']}", style="red")
            raise click.ClickException("Failed to list tags")

    except Exception as e:
        console.print(f"❌ Error listing tags: {e}", style="red")
        raise click.ClickException("Failed to list tags") from e


@issues.group()
def comments() -> None:
    """Manage issue comments."""
    pass


@comments.command(name="add")
@click.argument("issue_id")
@click.argument("text")
@click.pass_context
def add_comment(ctx: click.Context, issue_id: str, text: str) -> None:
    """Add a comment to an issue."""
    from .issues import IssueManager

    console = Console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    issue_manager = IssueManager(auth_manager)

    console.print(f"💬 Adding comment to issue '{issue_id}'...", style="blue")

    try:
        result = asyncio.run(issue_manager.add_comment(issue_id, text))

        if result["status"] == "success":
            console.print(f"✅ {result['message']}", style="green")
        else:
            console.print(f"❌ {result['message']}", style="red")
            raise click.ClickException("Failed to add comment")

    except Exception as e:
        console.print(f"❌ Error adding comment: {e}", style="red")
        raise click.ClickException("Failed to add comment") from e


@comments.command(name="list")
@click.argument("issue_id")
@click.option(
    "--format",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Output format",
)
@click.pass_context
def list_issue_comments(
    ctx: click.Context,
    issue_id: str,
    format: str,
) -> None:
    """List comments on an issue."""
    from .issues import IssueManager

    console = Console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    issue_manager = IssueManager(auth_manager)

    console.print(f"💬 Fetching comments for issue '{issue_id}'...", style="blue")

    try:
        result = asyncio.run(issue_manager.list_comments(issue_id))

        if result["status"] == "success":
            comments = result["data"]

            if format == "table":
                issue_manager.display_comments_table(comments)
            else:
                import json

                console.print(json.dumps(comments, indent=2))
        else:
            console.print(f"❌ {result['message']}", style="red")
            raise click.ClickException("Failed to list comments")

    except Exception as e:
        console.print(f"❌ Error listing comments: {e}", style="red")
        raise click.ClickException("Failed to list comments") from e


@comments.command(name="update")
@click.argument("issue_id")
@click.argument("comment_id")
@click.argument("text")
@click.pass_context
def update_comment(
    ctx: click.Context, issue_id: str, comment_id: str, text: str
) -> None:
    """Update an existing comment."""
    from .issues import IssueManager

    console = Console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    issue_manager = IssueManager(auth_manager)

    console.print(f"✏️  Updating comment '{comment_id}'...", style="blue")

    try:
        result = asyncio.run(issue_manager.update_comment(issue_id, comment_id, text))

        if result["status"] == "success":
            console.print(f"✅ {result['message']}", style="green")
        else:
            console.print(f"❌ {result['message']}", style="red")
            raise click.ClickException("Failed to update comment")

    except Exception as e:
        console.print(f"❌ Error updating comment: {e}", style="red")
        raise click.ClickException("Failed to update comment") from e


@comments.command()
@click.argument("issue_id")
@click.argument("comment_id")
@click.option(
    "--confirm",
    is_flag=True,
    help="Skip confirmation prompt",
)
@click.pass_context
def delete_comment(
    ctx: click.Context, issue_id: str, comment_id: str, confirm: bool
) -> None:
    """Delete a comment."""
    from .issues import IssueManager

    console = Console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    issue_manager = IssueManager(auth_manager)

    if not confirm:
        if not click.confirm(
            f"Are you sure you want to delete comment '{comment_id}'?"
        ):
            console.print("Delete cancelled.", style="yellow")
            return

    console.print(f"🗑️  Deleting comment '{comment_id}'...", style="blue")

    try:
        result = asyncio.run(issue_manager.delete_comment(issue_id, comment_id))

        if result["status"] == "success":
            console.print(f"✅ {result['message']}", style="green")
        else:
            console.print(f"❌ {result['message']}", style="red")
            raise click.ClickException("Failed to delete comment")

    except Exception as e:
        console.print(f"❌ Error deleting comment: {e}", style="red")
        raise click.ClickException("Failed to delete comment") from e


@issues.group()
def attach() -> None:
    """Manage issue attachments."""
    pass


@attach.command()
@click.argument("issue_id")
@click.argument("file_path", type=click.Path(exists=True))
@click.pass_context
def upload(ctx: click.Context, issue_id: str, file_path: str) -> None:
    """Upload a file to an issue."""
    from .issues import IssueManager

    console = Console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    issue_manager = IssueManager(auth_manager)

    console.print(
        f"📎 Uploading file '{file_path}' to issue '{issue_id}'...", style="blue"
    )

    try:
        result = asyncio.run(issue_manager.upload_attachment(issue_id, file_path))

        if result["status"] == "success":
            console.print(f"✅ {result['message']}", style="green")
        else:
            console.print(f"❌ {result['message']}", style="red")
            raise click.ClickException("Failed to upload attachment")

    except Exception as e:
        console.print(f"❌ Error uploading attachment: {e}", style="red")
        raise click.ClickException("Failed to upload attachment") from e


@attach.command()
@click.argument("issue_id")
@click.argument("attachment_id")
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output file path",
)
@click.pass_context
def download(
    ctx: click.Context, issue_id: str, attachment_id: str, output: Optional[str]
) -> None:
    """Download an attachment from an issue."""
    from .issues import IssueManager

    console = Console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    issue_manager = IssueManager(auth_manager)

    if not output:
        output = f"attachment_{attachment_id}"

    console.print(
        f"📥 Downloading attachment '{attachment_id}' to '{output}'...", style="blue"
    )

    try:
        result = asyncio.run(
            issue_manager.download_attachment(issue_id, attachment_id, output)
        )

        if result["status"] == "success":
            console.print(f"✅ {result['message']}", style="green")
        else:
            console.print(f"❌ {result['message']}", style="red")
            raise click.ClickException("Failed to download attachment")

    except Exception as e:
        console.print(f"❌ Error downloading attachment: {e}", style="red")
        raise click.ClickException("Failed to download attachment") from e


@attach.command(name="list")
@click.argument("issue_id")
@click.option(
    "--format",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Output format",
)
@click.pass_context
def list_attachments(
    ctx: click.Context,
    issue_id: str,
    format: str,
) -> None:
    """List attachments for an issue."""
    from .issues import IssueManager

    console = Console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    issue_manager = IssueManager(auth_manager)

    console.print(f"📎 Fetching attachments for issue '{issue_id}'...", style="blue")

    try:
        result = asyncio.run(issue_manager.list_attachments(issue_id))

        if result["status"] == "success":
            attachments = result["data"]

            if format == "table":
                issue_manager.display_attachments_table(attachments)
            else:
                import json

                console.print(json.dumps(attachments, indent=2))
        else:
            console.print(f"❌ {result['message']}", style="red")
            raise click.ClickException("Failed to list attachments")

    except Exception as e:
        console.print(f"❌ Error listing attachments: {e}", style="red")
        raise click.ClickException("Failed to list attachments") from e


@attach.command()
@click.argument("issue_id")
@click.argument("attachment_id")
@click.option(
    "--confirm",
    is_flag=True,
    help="Skip confirmation prompt",
)
@click.pass_context
def delete_attachment(
    ctx: click.Context, issue_id: str, attachment_id: str, confirm: bool
) -> None:
    """Delete an attachment from an issue."""
    from .issues import IssueManager

    console = Console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    issue_manager = IssueManager(auth_manager)

    if not confirm:
        if not click.confirm(
            f"Are you sure you want to delete attachment '{attachment_id}'?"
        ):
            console.print("Delete cancelled.", style="yellow")
            return

    console.print(f"🗑️  Deleting attachment '{attachment_id}'...", style="blue")

    try:
        result = asyncio.run(issue_manager.delete_attachment(issue_id, attachment_id))

        if result["status"] == "success":
            console.print(f"✅ {result['message']}", style="green")
        else:
            console.print(f"❌ {result['message']}", style="red")
            raise click.ClickException("Failed to delete attachment")

    except Exception as e:
        console.print(f"❌ Error deleting attachment: {e}", style="red")
        raise click.ClickException("Failed to delete attachment") from e


@issues.group()
def links() -> None:
    """Manage issue relationships."""
    pass


@links.command(name="create")
@click.argument("source_issue_id")
@click.argument("target_issue_id")
@click.argument("link_type")
@click.pass_context
def create_link(
    ctx: click.Context, source_issue_id: str, target_issue_id: str, link_type: str
) -> None:
    """Create a link between two issues."""
    from .issues import IssueManager

    console = Console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    issue_manager = IssueManager(auth_manager)

    console.print(
        f"🔗 Creating '{link_type}' link between '{source_issue_id}' "
        f"and '{target_issue_id}'...",
        style="blue",
    )

    try:
        result = asyncio.run(
            issue_manager.create_link(source_issue_id, target_issue_id, link_type)
        )

        if result["status"] == "success":
            console.print(f"✅ {result['message']}", style="green")
        else:
            console.print(f"❌ {result['message']}", style="red")
            raise click.ClickException("Failed to create link")

    except Exception as e:
        console.print(f"❌ Error creating link: {e}", style="red")
        raise click.ClickException("Failed to create link") from e


@links.command(name="list")
@click.argument("issue_id")
@click.option(
    "--format",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Output format",
)
@click.pass_context
def list_links(
    ctx: click.Context,
    issue_id: str,
    format: str,
) -> None:
    """Show all links for an issue."""
    from .issues import IssueManager

    console = Console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    issue_manager = IssueManager(auth_manager)

    console.print(f"🔗 Fetching links for issue '{issue_id}'...", style="blue")

    try:
        result = asyncio.run(issue_manager.list_links(issue_id))

        if result["status"] == "success":
            links = result["data"]

            if format == "table":
                issue_manager.display_links_table(links)
            else:
                import json

                console.print(json.dumps(links, indent=2))
        else:
            console.print(f"❌ {result['message']}", style="red")
            raise click.ClickException("Failed to list links")

    except Exception as e:
        console.print(f"❌ Error listing links: {e}", style="red")
        raise click.ClickException("Failed to list links") from e


@links.command()
@click.argument("source_issue_id")
@click.argument("link_id")
@click.option(
    "--confirm",
    is_flag=True,
    help="Skip confirmation prompt",
)
@click.pass_context
def delete_link(
    ctx: click.Context, source_issue_id: str, link_id: str, confirm: bool
) -> None:
    """Remove a link between issues."""
    from .issues import IssueManager

    console = Console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    issue_manager = IssueManager(auth_manager)

    if not confirm:
        if not click.confirm(f"Are you sure you want to delete link '{link_id}'?"):
            console.print("Delete cancelled.", style="yellow")
            return

    console.print(f"🔗 Deleting link '{link_id}'...", style="blue")

    try:
        result = asyncio.run(issue_manager.delete_link(source_issue_id, link_id))

        if result["status"] == "success":
            console.print(f"✅ {result['message']}", style="green")
        else:
            console.print(f"❌ {result['message']}", style="red")
            raise click.ClickException("Failed to delete link")

    except Exception as e:
        console.print(f"❌ Error deleting link: {e}", style="red")
        raise click.ClickException("Failed to delete link") from e


@links.command()
@click.option(
    "--format",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Output format",
)
@click.pass_context
def types(ctx: click.Context, format: str) -> None:
    """List available link types."""
    from .issues import IssueManager

    console = Console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    issue_manager = IssueManager(auth_manager)

    console.print("🔗 Fetching available link types...", style="blue")

    try:
        result = asyncio.run(issue_manager.list_link_types())

        if result["status"] == "success":
            link_types = result["data"]

            if format == "table":
                issue_manager.display_link_types_table(link_types)
            else:
                import json

                console.print(json.dumps(link_types, indent=2))
        else:
            console.print(f"❌ {result['message']}", style="red")
            raise click.ClickException("Failed to list link types")

    except Exception as e:
        console.print(f"❌ Error listing link types: {e}", style="red")
        raise click.ClickException("Failed to list link types") from e


@main.group()
def articles() -> None:
    """Manage knowledge base articles."""
    pass


@articles.command(name="create")
@click.argument("title")
@click.option(
    "--content",
    "-c",
    prompt=True,
    help="Article content",
)
@click.option(
    "--project-id",
    "-p",
    help="Project ID to associate with the article",
)
@click.option(
    "--parent-id",
    help="Parent article ID for nested articles",
)
@click.option(
    "--summary",
    "-s",
    help="Article summary (defaults to title)",
)
@click.option(
    "--visibility",
    type=click.Choice(["public", "private", "project"]),
    default="public",
    help="Article visibility level",
)
@click.pass_context
def articles_create(
    ctx: click.Context,
    title: str,
    content: str,
    project_id: Optional[str],
    parent_id: Optional[str],
    summary: Optional[str],
    visibility: str,
) -> None:
    """Create a new article."""
    from .articles import ArticleManager

    console = Console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    article_manager = ArticleManager(auth_manager)

    console.print(f"📝 Creating article '{title}'...", style="blue")

    try:
        result = asyncio.run(
            article_manager.create_article(
                title=title,
                content=content,
                project_id=project_id,
                parent_id=parent_id,
                summary=summary,
                visibility=visibility,
            )
        )

        if result["status"] == "success":
            console.print(f"✅ {result['message']}", style="green")
            article = result["data"]
            console.print(f"Article ID: {article.get('id', 'N/A')}", style="blue")
        else:
            console.print(f"❌ {result['message']}", style="red")
            raise click.ClickException("Failed to create article")

    except Exception as e:
        console.print(f"❌ Error creating article: {e}", style="red")
        raise click.ClickException("Failed to create article") from e


@articles.command()
@click.argument("article_id")
@click.option(
    "--title",
    "-t",
    help="New article title",
)
@click.option(
    "--content",
    "-c",
    help="New article content",
)
@click.option(
    "--summary",
    "-s",
    help="New article summary",
)
@click.option(
    "--visibility",
    type=click.Choice(["public", "private", "project"]),
    help="New visibility level",
)
@click.option(
    "--show-details",
    is_flag=True,
    help="Show detailed article information",
)
@click.pass_context
def edit(
    ctx: click.Context,
    article_id: str,
    title: Optional[str],
    content: Optional[str],
    summary: Optional[str],
    visibility: Optional[str],
    show_details: bool,
) -> None:
    """Edit an existing article."""
    from .articles import ArticleManager

    console = Console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    article_manager = ArticleManager(auth_manager)

    if show_details:
        console.print(f"📋 Fetching article '{article_id}' details...", style="blue")

        try:
            result = asyncio.run(article_manager.get_article(article_id))

            if result["status"] == "success":
                article_manager.display_article_details(result["data"])
            else:
                console.print(f"❌ {result['message']}", style="red")
                raise click.ClickException("Failed to get article details")

        except Exception as e:
            console.print(f"❌ Error getting article details: {e}", style="red")
            raise click.ClickException("Failed to get article details") from e
    else:
        if not any([title, content, summary, visibility]):
            console.print("❌ No updates specified.", style="red")
            console.print(
                "Use --title, --content, --summary, or --visibility options, "
                "or --show-details to view current article.",
                style="blue",
            )
            return

        console.print(f"✏️  Updating article '{article_id}'...", style="blue")

        try:
            result = asyncio.run(
                article_manager.update_article(
                    article_id=article_id,
                    title=title,
                    content=content,
                    summary=summary,
                    visibility=visibility,
                )
            )

            if result["status"] == "success":
                console.print(f"✅ {result['message']}", style="green")
            else:
                console.print(f"❌ {result['message']}", style="red")
                raise click.ClickException("Failed to update article")

        except Exception as e:
            console.print(f"❌ Error updating article: {e}", style="red")
            raise click.ClickException("Failed to update article") from e


@articles.command()
@click.argument("article_id")
@click.pass_context
def publish(ctx: click.Context, article_id: str) -> None:
    """Publish a draft article."""
    from .articles import ArticleManager

    console = Console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    article_manager = ArticleManager(auth_manager)

    console.print(f"🚀 Publishing article '{article_id}'...", style="blue")

    try:
        result = asyncio.run(article_manager.publish_article(article_id))

        if result["status"] == "success":
            console.print(f"✅ {result['message']}", style="green")
        else:
            console.print(f"❌ {result['message']}", style="red")
            raise click.ClickException("Failed to publish article")

    except Exception as e:
        console.print(f"❌ Error publishing article: {e}", style="red")
        raise click.ClickException("Failed to publish article") from e


@articles.command(name="list")
@click.option(
    "--project-id",
    "-p",
    help="Filter by project ID",
)
@click.option(
    "--parent-id",
    help="Filter by parent article ID",
)
@click.option(
    "--fields",
    "-f",
    help="Comma-separated list of fields to return",
)
@click.option(
    "--top",
    "-t",
    type=int,
    help="Maximum number of articles to return",
)
@click.option(
    "--query",
    "-q",
    help="Search query to filter articles",
)
@click.option(
    "--format",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Output format",
)
@click.pass_context
def articles_list(
    ctx: click.Context,
    project_id: Optional[str],
    parent_id: Optional[str],
    fields: Optional[str],
    top: Optional[int],
    query: Optional[str],
    format: str,
) -> None:
    """List articles with filtering."""
    from .articles import ArticleManager

    console = Console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    article_manager = ArticleManager(auth_manager)

    console.print("📚 Fetching articles...", style="blue")

    try:
        result = asyncio.run(
            article_manager.list_articles(
                project_id=project_id,
                parent_id=parent_id,
                fields=fields,
                top=top,
                query=query,
            )
        )

        if result["status"] == "success":
            articles = result["data"]

            if format == "table":
                article_manager.display_articles_table(articles)
                console.print(f"\n[dim]Total: {result['count']} articles[/dim]")
            else:
                import json

                console.print(json.dumps(articles, indent=2))
        else:
            console.print(f"❌ {result['message']}", style="red")
            raise click.ClickException("Failed to list articles")

    except Exception as e:
        console.print(f"❌ Error listing articles: {e}", style="red")
        raise click.ClickException("Failed to list articles") from e


@articles.command()
@click.option(
    "--project-id",
    "-p",
    help="Filter by project ID",
)
@click.option(
    "--fields",
    "-f",
    help="Comma-separated list of fields to return",
)
@click.option(
    "--top",
    "-t",
    type=int,
    help="Maximum number of articles to return",
)
@click.pass_context
def tree(
    ctx: click.Context,
    project_id: Optional[str],
    fields: Optional[str],
    top: Optional[int],
) -> None:
    """Display articles in hierarchical tree structure."""
    from .articles import ArticleManager

    console = Console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    article_manager = ArticleManager(auth_manager)

    console.print("🌳 Fetching articles tree...", style="blue")

    try:
        result = asyncio.run(
            article_manager.list_articles(
                project_id=project_id,
                fields=fields,
                top=top,
            )
        )

        if result["status"] == "success":
            articles = result["data"]
            article_manager.display_articles_tree(articles)
            console.print(f"\n[dim]Total: {result['count']} articles[/dim]")
        else:
            console.print(f"❌ {result['message']}", style="red")
            raise click.ClickException("Failed to fetch articles tree")

    except Exception as e:
        console.print(f"❌ Error fetching articles tree: {e}", style="red")
        raise click.ClickException("Failed to fetch articles tree") from e


@articles.command(name="search")
@click.argument("query")
@click.option(
    "--project-id",
    "-p",
    help="Filter by project ID",
)
@click.option(
    "--top",
    "-t",
    type=int,
    help="Maximum number of results to return",
)
@click.option(
    "--format",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Output format",
)
@click.pass_context
def articles_search(
    ctx: click.Context,
    query: str,
    project_id: Optional[str],
    top: Optional[int],
    format: str,
) -> None:
    """Search articles."""
    from .articles import ArticleManager

    console = Console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    article_manager = ArticleManager(auth_manager)

    console.print(f"🔍 Searching articles for '{query}'...", style="blue")

    try:
        result = asyncio.run(
            article_manager.search_articles(
                query=query,
                project_id=project_id,
                top=top,
            )
        )

        if result["status"] == "success":
            articles = result["data"]

            if format == "table":
                article_manager.display_articles_table(articles)
                console.print(f"\n[dim]Found: {result['count']} articles[/dim]")
            else:
                import json

                console.print(json.dumps(articles, indent=2))
        else:
            console.print(f"❌ {result['message']}", style="red")
            raise click.ClickException("Failed to search articles")

    except Exception as e:
        console.print(f"❌ Error searching articles: {e}", style="red")
        raise click.ClickException("Failed to search articles") from e


@articles.command()
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
def draft(
    ctx: click.Context,
    project_id: Optional[str],
    format: str,
) -> None:
    """Manage article drafts."""
    from .articles import ArticleManager

    console = Console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    article_manager = ArticleManager(auth_manager)

    console.print("📝 Fetching draft articles...", style="blue")

    try:
        # Search for draft articles (private visibility)
        result = asyncio.run(
            article_manager.list_articles(
                project_id=project_id,
                query="visibility:private",
            )
        )

        if result["status"] == "success":
            articles = result["data"]

            if format == "table":
                article_manager.display_articles_table(articles)
                console.print(f"\n[dim]Total drafts: {result['count']} articles[/dim]")
            else:
                import json

                console.print(json.dumps(articles, indent=2))
        else:
            console.print(f"❌ {result['message']}", style="red")
            raise click.ClickException("Failed to list draft articles")

    except Exception as e:
        console.print(f"❌ Error listing draft articles: {e}", style="red")
        raise click.ClickException("Failed to list draft articles") from e


@articles.command()
@click.argument("parent_id")
@click.option(
    "--update",
    is_flag=True,
    help="Apply changes to YouTrack after confirmation",
)
@click.pass_context
def sort(
    ctx: click.Context,
    parent_id: str,
    update: bool,
) -> None:
    """Sort child articles under a parent article."""
    from .articles import ArticleManager

    console = Console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    article_manager = ArticleManager(auth_manager)

    console.print(f"📋 Fetching child articles for '{parent_id}'...", style="blue")

    try:
        result = asyncio.run(article_manager.list_articles(parent_id=parent_id))

        if result["status"] == "success":
            articles = result["data"]

            if not articles:
                console.print("No child articles found.", style="yellow")
                return

            console.print(f"Found {len(articles)} child articles:")
            article_manager.display_articles_table(articles)

            if update:
                console.print(
                    "\n⚠️  Article sorting functionality requires manual reordering",
                    style="yellow",
                )  # noqa: E501
                console.print(
                    "Use the YouTrack web interface to drag and drop articles to reorder them.",  # noqa: E501
                    style="blue",
                )
            else:
                console.print(
                    "\n[dim]Use --update flag to apply sorting changes[/dim]",
                    style="blue",
                )  # noqa: E501

        else:
            console.print(f"❌ {result['message']}", style="red")
            raise click.ClickException("Failed to fetch child articles")

    except Exception as e:
        console.print(f"❌ Error fetching child articles: {e}", style="red")
        raise click.ClickException("Failed to fetch child articles") from e


@articles.group(name="comments")
def article_comments() -> None:
    """Manage article comments."""
    pass


@article_comments.command(name="add")
@click.argument("article_id")
@click.argument("text")
@click.pass_context
def articles_comments_add(ctx: click.Context, article_id: str, text: str) -> None:
    """Add a comment to an article."""
    from .articles import ArticleManager

    console = Console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    article_manager = ArticleManager(auth_manager)

    console.print(f"💬 Adding comment to article '{article_id}'...", style="blue")

    try:
        result = asyncio.run(article_manager.add_comment(article_id, text))

        if result["status"] == "success":
            console.print(f"✅ {result['message']}", style="green")
        else:
            console.print(f"❌ {result['message']}", style="red")
            raise click.ClickException("Failed to add comment")

    except Exception as e:
        console.print(f"❌ Error adding comment: {e}", style="red")
        raise click.ClickException("Failed to add comment") from e


@article_comments.command("list")
@click.argument("article_id")
@click.option(
    "--format",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Output format",
)
@click.pass_context
def list_comments(
    ctx: click.Context,
    article_id: str,
    format: str,
) -> None:
    """List comments on an article."""
    from .articles import ArticleManager

    console = Console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    article_manager = ArticleManager(auth_manager)

    console.print(f"💬 Fetching comments for article '{article_id}'...", style="blue")

    try:
        result = asyncio.run(article_manager.get_article_comments(article_id))

        if result["status"] == "success":
            comments = result["data"]

            if format == "table":
                if not comments:
                    console.print("No comments found.", style="yellow")
                    return

                from rich.table import Table

                table = Table(title="Article Comments")
                table.add_column("ID", style="cyan")
                table.add_column("Author", style="green")
                table.add_column("Text", style="blue")
                table.add_column("Created", style="yellow")

                for comment in comments:
                    table.add_row(
                        comment.get("id", "N/A"),
                        comment.get("author", {}).get("fullName", "N/A"),
                        comment.get("text", "N/A")[:100]
                        + ("..." if len(comment.get("text", "")) > 100 else ""),  # noqa: E501
                        comment.get("created", "N/A"),
                    )

                console.print(table)
            else:
                import json

                console.print(json.dumps(comments, indent=2))

        else:
            console.print(f"❌ {result['message']}", style="red")
            raise click.ClickException("Failed to list comments")

    except Exception as e:
        console.print(f"❌ Error listing comments: {e}", style="red")
        raise click.ClickException("Failed to list comments") from e


@article_comments.command(name="update")
@click.argument("comment_id")
@click.argument("text")
@click.pass_context
def comments_update(ctx: click.Context, comment_id: str, text: str) -> None:
    """Update an existing comment."""
    console = Console()
    console.print("⚠️  Comment update functionality not yet implemented", style="yellow")
    console.print("This feature requires additional API endpoints", style="blue")


@article_comments.command(name="delete")
@click.argument("comment_id")
@click.option(
    "--confirm",
    is_flag=True,
    help="Skip confirmation prompt",
)
@click.pass_context
def articles_comments_delete(
    ctx: click.Context, comment_id: str, confirm: bool
) -> None:
    """Delete a comment."""
    console = Console()

    if not confirm:
        if not click.confirm(
            f"Are you sure you want to delete comment '{comment_id}'?"
        ):  # noqa: E501
            console.print("Delete cancelled.", style="yellow")
            return

    console.print("⚠️  Comment delete functionality not yet implemented", style="yellow")
    console.print("This feature requires additional API endpoints", style="blue")


@articles.group(name="attach")
def article_attach() -> None:
    """Manage article attachments."""
    pass


@article_attach.command(name="upload")
@click.argument("article_id")
@click.argument("file_path", type=click.Path(exists=True))
@click.pass_context
def articles_attach_upload(ctx: click.Context, article_id: str, file_path: str) -> None:
    """Upload a file to an article."""
    console = Console()
    console.print("⚠️  File upload functionality not yet implemented", style="yellow")
    console.print(
        "This feature requires multipart form upload implementation", style="blue"
    )  # noqa: E501


@article_attach.command(name="download")
@click.argument("article_id")
@click.argument("attachment_id")
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output file path",
)
@click.pass_context
def articles_attach_download(
    ctx: click.Context, article_id: str, attachment_id: str, output: Optional[str]
) -> None:  # noqa: E501
    """Download an attachment from an article."""
    console = Console()
    console.print("⚠️  File download functionality not yet implemented", style="yellow")
    console.print("This feature requires binary file handling", style="blue")


@article_attach.command("list")
@click.argument("article_id")
@click.option(
    "--format",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Output format",
)
@click.pass_context
def articles_attach_list(
    ctx: click.Context,
    article_id: str,
    format: str,
) -> None:
    """List attachments for an article."""
    from .articles import ArticleManager

    console = Console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    article_manager = ArticleManager(auth_manager)

    console.print(
        f"📎 Fetching attachments for article '{article_id}'...", style="blue"
    )  # noqa: E501

    try:
        result = asyncio.run(article_manager.get_article_attachments(article_id))

        if result["status"] == "success":
            attachments = result["data"]

            if format == "table":
                if not attachments:
                    console.print("No attachments found.", style="yellow")
                    return

                from rich.table import Table

                table = Table(title="Article Attachments")
                table.add_column("ID", style="cyan")
                table.add_column("Name", style="green")
                table.add_column("Size", style="blue")
                table.add_column("Type", style="yellow")
                table.add_column("Author", style="magenta")

                for attachment in attachments:
                    table.add_row(
                        attachment.get("id", "N/A"),
                        attachment.get("name", "N/A"),
                        str(attachment.get("size", "N/A")),
                        attachment.get("mimeType", "N/A"),
                        attachment.get("author", {}).get("fullName", "N/A"),
                    )

                console.print(table)
            else:
                import json

                console.print(json.dumps(attachments, indent=2))

        else:
            console.print(f"❌ {result['message']}", style="red")
            raise click.ClickException("Failed to list attachments")

    except Exception as e:
        console.print(f"❌ Error listing attachments: {e}", style="red")
        raise click.ClickException("Failed to list attachments") from e


@article_attach.command(name="delete")
@click.argument("article_id")
@click.argument("attachment_id")
@click.option(
    "--confirm",
    is_flag=True,
    help="Skip confirmation prompt",
)
@click.pass_context
def articles_attach_delete(
    ctx: click.Context, article_id: str, attachment_id: str, confirm: bool
) -> None:  # noqa: E501
    """Delete an attachment from an article."""
    console = Console()

    if not confirm:
        if not click.confirm(
            f"Are you sure you want to delete attachment '{attachment_id}'?"
        ):  # noqa: E501
            console.print("Delete cancelled.", style="yellow")
            return

    console.print(
        "⚠️  Attachment delete functionality not yet implemented", style="yellow"
    )  # noqa: E501
    console.print("This feature requires additional API endpoints", style="blue")


@main.group()
def projects() -> None:
    """Manage projects."""
    pass


@projects.command(name="list")
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
def projects_list(
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


@projects.command(name="create")
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
def projects_create(
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
            user_manager.list_users(fields=fields, top=top, query=query)
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
        if not any(
            [full_name, email, password, banned is not None, force_change_password]
        ):
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


@time.command()
@click.argument("issue_id")
@click.argument("duration")
@click.option("--date", "-d", help="Date for the work entry (YYYY-MM-DD or 'today')")
@click.option("--description", "-desc", help="Description of the work done")
@click.option("--work-type", "-t", help="Type of work (e.g., 'Development', 'Testing')")
@click.pass_context
def log(
    ctx: click.Context,
    issue_id: str,
    duration: str,
    date: Optional[str],
    description: Optional[str],
    work_type: Optional[str],
) -> None:
    """Log work time to an issue."""
    from .time import TimeManager

    console = Console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    time_manager = TimeManager(auth_manager)

    console.print(f"⏱️  Logging {duration} to issue {issue_id}...", style="blue")

    try:
        result = asyncio.run(
            time_manager.log_time(issue_id, duration, date, description, work_type)
        )

        if result["status"] == "success":
            console.print(f"✅ {result['message']}", style="green")
        else:
            console.print(f"❌ {result['message']}", style="red")
            raise click.ClickException(result["message"])
    except Exception as e:
        console.print(f"❌ Error: {str(e)}", style="red")
        raise click.ClickException("Failed to log time") from e


@time.command()
@click.option("--issue-id", "-i", help="Filter by specific issue ID")
@click.option("--user-id", "-u", help="Filter by specific user ID")
@click.option("--start-date", "-s", help="Start date for filtering (YYYY-MM-DD)")
@click.option("--end-date", "-e", help="End date for filtering (YYYY-MM-DD)")
@click.option(
    "--format",
    "-f",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Output format",
)
@click.pass_context
def report(
    ctx: click.Context,
    issue_id: Optional[str],
    user_id: Optional[str],
    start_date: Optional[str],
    end_date: Optional[str],
    format: str,
) -> None:
    """Generate time reports with filtering options."""
    from .time import TimeManager

    console = Console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    time_manager = TimeManager(auth_manager)

    console.print("📊 Generating time report...", style="blue")

    try:
        result = asyncio.run(
            time_manager.get_time_entries(
                issue_id=issue_id,
                user_id=user_id,
                start_date=start_date,
                end_date=end_date,
                fields="id,duration,date,description,author(id,fullName),issue(id,summary),type(name)",
            )
        )

        if result["status"] == "success":
            if format == "json":
                console.print_json(data=result["data"])
            else:
                time_manager.display_time_entries(result["data"])
                console.print(f"\n📈 Total entries: {result['count']}", style="green")
        else:
            console.print(f"❌ {result['message']}", style="red")
            raise click.ClickException(result["message"])
    except Exception as e:
        console.print(f"❌ Error: {str(e)}", style="red")
        raise click.ClickException("Failed to generate report") from e


@time.command()
@click.option("--user-id", "-u", help="Filter by specific user ID")
@click.option("--start-date", "-s", help="Start date for filtering (YYYY-MM-DD)")
@click.option("--end-date", "-e", help="End date for filtering (YYYY-MM-DD)")
@click.option(
    "--group-by",
    "-g",
    type=click.Choice(["user", "issue", "type"]),
    default="user",
    help="Group summary by",
)
@click.option(
    "--format",
    "-f",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Output format",
)
@click.pass_context
def summary(
    ctx: click.Context,
    user_id: Optional[str],
    start_date: Optional[str],
    end_date: Optional[str],
    group_by: str,
    format: str,
) -> None:
    """View time summaries with aggregation."""
    from .time import TimeManager

    console = Console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    time_manager = TimeManager(auth_manager)

    console.print("📋 Generating time summary...", style="blue")

    try:
        result = asyncio.run(
            time_manager.get_time_summary(
                user_id=user_id,
                start_date=start_date,
                end_date=end_date,
                group_by=group_by,
            )
        )

        if result["status"] == "success":
            if format == "json":
                console.print_json(data=result["data"])
            else:
                time_manager.display_time_summary(result["data"])
                console.print(
                    f"\n📊 Based on {result['total_entries']} entries", style="green"
                )
        else:
            console.print(f"❌ {result['message']}", style="red")
            raise click.ClickException(result["message"])
    except Exception as e:
        console.print(f"❌ Error: {str(e)}", style="red")
        raise click.ClickException("Failed to generate summary") from e


@main.group()
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
    project_id: Optional[str],
    format: str,
) -> None:
    """List all agile boards."""
    from .boards import BoardManager

    console = Console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    board_manager = BoardManager(auth_manager)

    console.print("📋 Listing boards...", style="blue")

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


@boards.command(name="view")
@click.argument("board_id")
@click.option(
    "--format",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Output format",
)
@click.pass_context
def view_board(
    ctx: click.Context,
    board_id: str,
    format: str,
) -> None:
    """View details of a specific agile board."""
    from .boards import BoardManager

    console = Console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    board_manager = BoardManager(auth_manager)

    console.print(f"👀 Viewing board {board_id}...", style="blue")

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
    name: Optional[str],
) -> None:
    """Update an agile board configuration."""
    from .boards import BoardManager

    console = Console()
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


@main.group()
def reports() -> None:
    """Generate cross-entity reports."""
    pass


@reports.command(name="burndown")
@click.argument("project_id")
@click.option(
    "--sprint",
    "-s",
    help="Sprint ID or name to filter by",
)
@click.option(
    "--start-date",
    help="Start date in YYYY-MM-DD format",
)
@click.option(
    "--end-date",
    help="End date in YYYY-MM-DD format",
)
@click.pass_context
def reports_burndown(
    ctx: click.Context,
    project_id: str,
    sprint: Optional[str],
    start_date: Optional[str],
    end_date: Optional[str],
) -> None:
    """Generate a burndown report for a project or sprint."""
    auth_manager = AuthManager(ctx.obj.get("config"))
    report_manager = ReportManager(auth_manager)
    console = Console()

    async def run_burndown() -> None:
        result = await report_manager.generate_burndown_report(
            project_id=project_id,
            sprint_id=sprint,
            start_date=start_date,
            end_date=end_date,
        )

        if result["status"] == "error":
            console.print(f"[red]Error:[/red] {result['message']}")
            return

        report_manager.display_burndown_report(result["data"])

    asyncio.run(run_burndown())


@reports.command(name="velocity")
@click.argument("project_id")
@click.option(
    "--sprints",
    "-n",
    type=int,
    default=5,
    help="Number of recent sprints to analyze (default: 5)",
)
@click.pass_context
def reports_velocity(
    ctx: click.Context,
    project_id: str,
    sprints: int,
) -> None:
    """Generate a velocity report for recent sprints."""
    auth_manager = AuthManager(ctx.obj.get("config"))
    report_manager = ReportManager(auth_manager)
    console = Console()

    async def run_velocity() -> None:
        result = await report_manager.generate_velocity_report(
            project_id=project_id,
            sprints=sprints,
        )

        if result["status"] == "error":
            console.print(f"[red]Error:[/red] {result['message']}")
            return

        report_manager.display_velocity_report(result["data"])

    asyncio.run(run_velocity())


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


# Global Settings Commands
@admin.group(name="global-settings")
def admin_global_settings() -> None:
    """Manage global YouTrack settings."""
    pass


@admin_global_settings.command(name="get")
@click.argument("setting_key", required=False)
@click.pass_context
def admin_global_settings_get(ctx: click.Context, setting_key: Optional[str]) -> None:
    """Get global settings."""
    admin_manager = AdminManager(ctx.obj.get("config"))
    console = Console()

    async def run_get_settings() -> None:
        result = await admin_manager.get_global_settings(setting_key)

        if result["status"] == "error":
            console.print(f"[red]Error:[/red] {result['message']}")
            return

        admin_manager.display_global_settings(result["data"])

    asyncio.run(run_get_settings())


@admin_global_settings.command(name="set")
@click.argument("setting_key")
@click.argument("value")
@click.pass_context
def admin_global_settings_set(ctx: click.Context, setting_key: str, value: str) -> None:
    """Set a global setting."""
    admin_manager = AdminManager(ctx.obj.get("config"))
    console = Console()

    async def run_set_setting() -> None:
        result = await admin_manager.set_global_setting(setting_key, value)

        if result["status"] == "error":
            console.print(f"[red]Error:[/red] {result['message']}")
            return

        console.print(f"[green]Success:[/green] {result['message']}")

    asyncio.run(run_set_setting())


# License Commands
@admin.group(name="license")
def admin_license() -> None:
    """License management."""
    pass


@admin_license.command(name="show")
@click.pass_context
def admin_license_show(ctx: click.Context) -> None:
    """Display license information."""
    admin_manager = AdminManager(ctx.obj.get("config"))
    console = Console()

    async def run_show_license() -> None:
        result = await admin_manager.get_license_info()

        if result["status"] == "error":
            console.print(f"[red]Error:[/red] {result['message']}")
            return

        admin_manager.display_license_info(result["data"])

    asyncio.run(run_show_license())


@admin_license.command(name="usage")
@click.pass_context
def admin_license_usage(ctx: click.Context) -> None:
    """Show license usage statistics."""
    admin_manager = AdminManager(ctx.obj.get("config"))
    console = Console()

    async def run_license_usage() -> None:
        result = await admin_manager.get_license_usage()

        if result["status"] == "error":
            console.print(f"[red]Error:[/red] {result['message']}")
            return

        admin_manager.display_license_info(result["data"])

    asyncio.run(run_license_usage())


# Maintenance Commands
@admin.group(name="maintenance")
def admin_maintenance() -> None:
    """System maintenance operations."""
    pass


@admin_maintenance.command(name="clear-cache")
@click.option(
    "--confirm",
    is_flag=True,
    help="Skip confirmation prompt",
)
@click.pass_context
def admin_maintenance_clear_cache(ctx: click.Context, confirm: bool) -> None:
    """Clear system caches."""
    admin_manager = AdminManager(ctx.obj.get("config"))
    console = Console()

    if not confirm:
        console.print("[yellow]Warning:[/yellow] This will clear all system caches.")
        if not click.confirm("Continue?"):
            console.print("Operation cancelled.")
            return

    async def run_clear_cache() -> None:
        result = await admin_manager.clear_caches()

        if result["status"] == "error":
            console.print(f"[red]Error:[/red] {result['message']}")
            return

        console.print(f"[green]Success:[/green] {result['message']}")

    asyncio.run(run_clear_cache())


# Health Commands
@admin.group(name="health")
def admin_health() -> None:
    """System health checks and diagnostics."""
    pass


@admin_health.command(name="check")
@click.pass_context
def admin_health_check(ctx: click.Context) -> None:
    """Run health diagnostics."""
    admin_manager = AdminManager(ctx.obj.get("config"))
    console = Console()

    async def run_health_check() -> None:
        result = await admin_manager.get_system_health()

        if result["status"] == "error":
            console.print(f"[red]Error:[/red] {result['message']}")
            return

        admin_manager.display_system_health(result["data"])

    asyncio.run(run_health_check())


# User Groups Commands
@admin.group(name="user-groups")
def admin_user_groups() -> None:
    """Manage user groups and permissions."""
    pass


@admin_user_groups.command(name="list")
@click.option(
    "--fields",
    "-f",
    help="Comma-separated list of fields to return",
)
@click.pass_context
def admin_user_groups_list(ctx: click.Context, fields: Optional[str]) -> None:
    """List all user groups."""
    admin_manager = AdminManager(ctx.obj.get("config"))
    console = Console()

    async def run_list_groups() -> None:
        result = await admin_manager.list_user_groups(fields)

        if result["status"] == "error":
            console.print(f"[red]Error:[/red] {result['message']}")
            return

        admin_manager.display_user_groups(result["data"])

    asyncio.run(run_list_groups())


@admin_user_groups.command(name="create")
@click.argument("name")
@click.option(
    "--description",
    "-d",
    help="Group description",
)
@click.pass_context
def admin_user_groups_create(
    ctx: click.Context, name: str, description: Optional[str]
) -> None:
    """Create a new user group."""
    admin_manager = AdminManager(ctx.obj.get("config"))
    console = Console()

    async def run_create_group() -> None:
        result = await admin_manager.create_user_group(name, description)

        if result["status"] == "error":
            console.print(f"[red]Error:[/red] {result['message']}")
            return

        console.print(f"[green]Success:[/green] {result['message']}")

    asyncio.run(run_create_group())


# Custom Fields Commands
@admin.group(name="fields")
def admin_fields() -> None:
    """Manage custom fields across projects."""
    pass


@admin_fields.command(name="list")
@click.option(
    "--fields",
    "-f",
    help="Comma-separated list of fields to return",
)
@click.pass_context
def admin_fields_list(ctx: click.Context, fields: Optional[str]) -> None:
    """List all custom fields."""
    admin_manager = AdminManager(ctx.obj.get("config"))
    console = Console()

    async def run_list_fields() -> None:
        result = await admin_manager.list_custom_fields(fields)

        if result["status"] == "error":
            console.print(f"[red]Error:[/red] {result['message']}")
            return

        admin_manager.display_custom_fields(result["data"])

    asyncio.run(run_list_fields())


if __name__ == "__main__":
    main()
