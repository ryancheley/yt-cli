"""Issues command group for YouTrack CLI.

This module provides comprehensive issue management commands including creation,
updating, searching, commenting, and workflow management for YouTrack issues.

The commands support both interactive and batch operations with rich formatting
and validation to ensure data integrity.
"""

import asyncio
from pathlib import Path
from typing import Optional

import click

from ..auth import AuthManager
from ..cli_utils import AliasedGroup, validate_issue_id_format, validate_project_id_format
from ..console import get_console


def _format_issues_as_csv(issues):
    """Format issues data as CSV."""
    import csv
    import io

    if not issues:
        return "ID,Summary,State,Priority,Type,Assignee,Project\n"

    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    headers = ["ID", "Summary", "State", "Priority", "Type", "Assignee", "Project"]
    writer.writerow(headers)

    # Write data rows
    for issue in issues:
        # Extract project info
        project_name = ""
        if isinstance(issue.get("project"), dict):
            project_name = issue["project"].get("name", issue["project"].get("shortName", ""))

        # Extract assignee info
        assignee_name = "Unassigned"
        if issue.get("assignee") and isinstance(issue["assignee"], dict):
            assignee_name = (
                issue["assignee"].get("fullName")
                or issue["assignee"].get("name")
                or issue["assignee"].get("login")
                or "Unassigned"
            )

        # Extract custom field values
        custom_fields = issue.get("customFields", [])
        state = priority = issue_type = ""

        for field in custom_fields:
            field_name = field.get("name", "")
            field_value = field.get("value")

            if field_name in ["State", "Status"]:
                if isinstance(field_value, dict):
                    state = field_value.get("name", "")
                elif isinstance(field_value, str):
                    state = field_value
            elif field_name == "Priority":
                if isinstance(field_value, dict):
                    priority = field_value.get("name", "")
                elif isinstance(field_value, str):
                    priority = field_value
            elif field_name in ["Type", "Issue Type"]:
                if isinstance(field_value, dict):
                    issue_type = field_value.get("name", "")
                elif isinstance(field_value, str):
                    issue_type = field_value

        # Create the issue ID
        if issue.get("numberInProject"):
            project_short = issue.get("project", {}).get("shortName", "")
            issue_id = f"{project_short}-{issue.get('numberInProject', '')}"
        else:
            issue_id = issue.get("id", "")

        row = [issue_id, issue.get("summary", ""), state, priority, issue_type, assignee_name, project_name]
        writer.writerow(row)

    return output.getvalue()


def _format_attachments_as_csv(attachments):
    """Format attachments data as CSV."""
    import csv
    import io

    if not attachments:
        return "Name,Size,Author,Created\n"

    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    headers = ["Name", "Size", "Author", "Created"]
    writer.writerow(headers)

    # Write data rows
    for attachment in attachments:
        name = attachment.get("name", "N/A")
        size = attachment.get("size", "N/A")

        # Extract author info
        author_name = "Unknown"
        if attachment.get("author") and isinstance(attachment["author"], dict):
            author_name = attachment["author"].get("fullName", "Unknown")

        created = attachment.get("created", "")

        row = [name, str(size), author_name, str(created)]
        writer.writerow(row)

    return output.getvalue()


def show_issues_verbose_help(ctx):
    """Show comprehensive help for the issues command group."""
    from rich.console import Console

    console = Console()

    # Main title
    console.print("\n[bold blue]yt issues[/bold blue] - Comprehensive Issue Management\n")

    # Description
    console.print("Manage YouTrack issues - create, update, search, and organize your work.")
    console.print("The issues command group provides comprehensive issue management capabilities.")
    console.print("You can create new issues, update existing ones, search and filter issues,")
    console.print("manage comments and attachments, and handle issue relationships.\n")

    # Usage
    console.print("[bold]Usage:[/bold] yt issues [OPTIONS] COMMAND [ARGS]...\n")

    # Core Commands
    console.print("[bold]Core Commands:[/bold]")
    console.print("  create        Create a new issue")
    console.print("  update        Update issue properties")
    console.print("  delete        Delete an issue")
    console.print("  show          Display issue details")
    console.print("  search        Search issues by keywords")
    console.print("  assign        Assign issue to user")
    console.print("  state         Change issue state")
    console.print("  links         Manage issue links")
    console.print("  comments      Manage issue comments")
    console.print("")

    # Common Examples
    console.print("[bold]Common Examples:[/bold]")
    console.print("  # Create and assign a bug report")
    console.print(
        '  yt issues create PROJECT-123 "Login fails on mobile" --type Bug --priority High --assignee john.doe'
    )
    console.print("")
    console.print("  # Search for issues by keywords")
    console.print('  yt issues search "API error priority:Critical"')
    console.print("")
    console.print("  # Update issue status")
    console.print('  yt issues update ISSUE-456 --state "In Progress"')
    console.print("")
    console.print("  # Add a comment")
    console.print('  yt issues comments add ISSUE-456 "Fixed in build 1.2.3"')
    console.print("")
    console.print("  # Show issue details")
    console.print("  yt issues show ISSUE-789 --format panel")
    console.print("")

    # Advanced Usage
    console.print("[bold]Advanced Usage:[/bold]")
    console.print("  # Create issue with custom fields")
    console.print('  yt issues create PROJECT-123 "Complex bug" --type Bug --priority High \\')
    console.print('    --description "Detailed description" --assignee john.doe')
    console.print("")
    console.print("  # Link related issues")
    console.print('  yt issues links add ISSUE-123 ISSUE-456 --relation "relates to"')
    console.print("")

    # Command Categories
    console.print("[bold]Command Categories:[/bold]")
    console.print("  Core Operations:  create, update, delete, show")
    console.print("  Search & Filter:  search")
    console.print("  Collaboration:    comments, assign")
    console.print("  Organization:     links, state")
    console.print("")

    # Options
    console.print("[bold]Options:[/bold]")
    console.print("  --help-verbose    Show this detailed help")
    console.print("  -h, --help        Show basic help and exit")
    console.print("")

    # Tips
    console.print("[bold]Tips:[/bold]")
    console.print("  • Issue types and priorities are project-specific")
    console.print("  • Use 'me' as assignee to filter or assign to yourself")
    console.print("  • Most commands accept both short (-t) and long (--type) options")
    console.print("  • Use --format option to change output format (table, json, etc.)")
    console.print("")


def add_help_verbose_option(func):
    """Decorator to add --help-verbose option to issues commands."""

    def callback(ctx, param, value):
        if value:
            show_issues_verbose_help(ctx)
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


@click.group(cls=AliasedGroup)
@add_help_verbose_option
def issues() -> None:
    r"""Manage YouTrack issues - create, update, and organize your work.

    Core Commands:
        create    Create a new issue
        list      List issues (coming soon)
        search    Search issues by keywords
        update    Update issue properties

    Quick Start:
        # Create a new issue
        yt issues create PROJECT-123 "Issue title" --type Bug

        # Search for issues
        yt issues search "priority:Critical"

    For complete help with all commands and examples, use:
        yt issues --help-verbose
    """
    pass


@issues.command()
@click.argument("project_id", callback=validate_project_id_format)
@click.argument("summary")
@click.option(
    "--description",
    "-d",
    help="Issue description",
)
@click.option(
    "--type",
    "-t",
    help="Issue type",
)
@click.option(
    "--priority",
    "-p",
    help="Issue priority",
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
    r"""Create a new issue.

    Create a new issue in the specified project with the given summary.
    You can optionally specify additional fields like description, type,
    priority, and assignee.

    Common Examples:
        # Create a simple bug report
        yt issues create WEB-123 "Fix login error on mobile"

        # Create a feature request with details
        yt issues create API-456 "Add user authentication endpoint" \
            --description "Need OAuth2 support for mobile app" \
            --type Feature --priority High --assignee john.doe

        # Create a task with priority
        yt issues create INFRA-789 "Update server certificates" \
            --type Task --priority Medium

    Tip: Issue types and priorities are project-specific. Use values that exist in your YouTrack project.
    """
    from ..exceptions import UsageError, ValidationError
    from ..managers.issues import IssueManager
    from ..utils import display_error, display_success, handle_error

    console = get_console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    issue_manager = IssueManager(auth_manager)

    console.print(f"🐛 Creating issue '{summary}' in project '{project_id}'...", style="blue")

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
            display_success(f"{result['message']}")
            issue = result["data"]
            # Display friendly ID if available, otherwise fall back to internal ID
            issue_id = issue.get("idReadable") or issue.get("id", "N/A")
            console.print(f"[blue]Issue ID:[/blue] {issue_id}")
        else:
            # Create enhanced error for common API failures
            if "project" in result["message"].lower() and "not found" in result["message"].lower():
                error = ValidationError(f"Project '{project_id}' not found", field="project_id")
                error.suggestion = (
                    f"Check if project '{project_id}' exists and you have access to it. "
                    "Use 'yt projects list' to see available projects."
                )
                error_result = handle_error(error, "create issue")
                display_error(error_result)
            else:
                console.print(f"❌ {result['message']}", style="red")

            raise click.ClickException("Failed to create issue")

    except click.ClickException:
        raise
    except Exception as e:
        # Provide helpful guidance for common errors
        error_result = handle_error(e, "create issue")
        display_error(error_result)

        # Add usage guidance for common mistakes
        usage_error = UsageError(
            "Issue creation failed",
            command_path="yt issues create",
            usage_syntax="yt issues create PROJECT_ID SUMMARY [OPTIONS]",
            examples=[
                "yt issues create WEB-123 'Fix login bug'",
                "yt issues create API-456 'Add new endpoint' --type Feature --priority High",
                "yt issues create INFRA-789 'Update certificates' --assignee admin",
            ],
            common_mistakes=[
                "Using lowercase in project ID (use 'WEB-123' not 'web-123')",
                "Missing quotes around summary with spaces",
                "Invalid issue type or priority values",
            ],
        )
        usage_result = handle_error(usage_error, "issue creation guidance")
        display_error(usage_result)

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
    "--profile",
    type=click.Choice(["minimal", "standard", "full"]),
    help="Field selection profile (minimal, standard, full). Standard is default.",
)
@click.option(
    "--top",
    "-t",
    type=int,
    help="Maximum number of issues to return (legacy, use --page-size instead)",
)
@click.option(
    "--page-size",
    type=int,
    default=100,
    help="Number of issues per page (default: 100)",
)
@click.option(
    "--after-cursor",
    help="Start pagination after this cursor",
)
@click.option(
    "--before-cursor",
    help="Start pagination before this cursor",
)
@click.option(
    "--all",
    is_flag=True,
    help="Fetch all results using pagination",
)
@click.option(
    "--max-results",
    type=int,
    help="Maximum total number of results to fetch",
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
@click.option(
    "--paginated",
    is_flag=True,
    help="Use interactive pagination for table display",
)
@click.option(
    "--display-page-size",
    type=int,
    default=50,
    help="Number of items per page for paginated display (default: 50)",
)
@click.option(
    "--show-all",
    is_flag=True,
    help="Show all results without pagination",
)
@click.option(
    "--start-page",
    type=int,
    default=1,
    help="Page number to start displaying from",
)
@click.pass_context
def list_issues(
    ctx: click.Context,
    project_id: Optional[str],
    state: Optional[str],
    assignee: Optional[str],
    fields: Optional[str],
    profile: Optional[str],
    top: Optional[int],
    page_size: int,
    after_cursor: Optional[str],
    before_cursor: Optional[str],
    all: bool,
    max_results: Optional[int],
    query: Optional[str],
    format: str,
    paginated: bool,
    display_page_size: int,
    show_all: bool,
    start_page: int,
) -> None:
    """List issues with filtering and pagination options.

    Display issues from your YouTrack instance with various filtering options.
    Use basic filters for common cases, or combine options for advanced queries.

    Common Examples:
        # List all your assigned issues
        yt issues list --assignee me

        # List open issues in a specific project
        yt issues list --project-id WEB --state Open

        # List issues with custom query
        yt issues list --query "priority:Critical state:Open"

        # List issues with JSON output for automation
        yt issues list --format json --page-size 50

    Tip: For complex filtering, use --query with YouTrack's search syntax.
    Most users only need --project-id, --assignee, and --state options.
    """
    from ..managers.issues import IssueManager

    console = get_console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    issue_manager = IssueManager(auth_manager)

    console.print("🔍 Fetching issues...", style="blue")

    try:
        # Determine pagination settings
        use_pagination = bool(all or after_cursor or before_cursor or max_results)

        # Handle conflicting parameters
        if top and page_size != 100:
            console.print(
                "⚠️  Warning: Both --top and --page-size specified. Using --top for backward compatibility.",
                style="yellow",
            )

        result = asyncio.run(
            issue_manager.list_issues(
                project_id=project_id,
                fields=fields,
                field_profile=profile,
                top=top,
                page_size=page_size,
                after_cursor=after_cursor,
                before_cursor=before_cursor,
                use_pagination=use_pagination,
                max_results=max_results,
                query=query,
                state=state,
                assignee=assignee,
            )
        )

        if result["status"] == "success":
            issues = result["data"]

            if format == "table":
                if paginated:
                    # Use interactive pagination
                    issue_manager.display_issues_table_paginated(
                        issues, page_size=display_page_size, show_all=show_all, start_page=start_page
                    )
                else:
                    # Use traditional table display
                    issue_manager.display_issues_table(issues)
                    console.print(f"\n[dim]Total: {result['count']} issues[/dim]")

                    # Display pagination info if available
                    if "pagination" in result:
                        pagination = result["pagination"]
                        if pagination["has_after"] or pagination["has_before"]:
                            console.print("[dim]Pagination:[/dim]", end="")
                            if pagination["after_cursor"]:
                                console.print(f" [dim]next: --after-cursor {pagination['after_cursor']}[/dim]", end="")
                            if pagination["before_cursor"]:
                                console.print(
                                    f" [dim]prev: --before-cursor {pagination['before_cursor']}[/dim]", end=""
                                )
                            console.print()
            elif format == "csv":
                # Convert issues to CSV format
                csv_output = _format_issues_as_csv(issues)
                console.print(csv_output)
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
@click.option(
    "--format",
    type=click.Choice(["table", "panel"], case_sensitive=False),
    default="table",
    help="Output format for issue details (table or panel)",
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
    format: str,
) -> None:
    """Update an existing issue."""
    from ..managers.issues import IssueManager

    console = get_console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    issue_manager = IssueManager(auth_manager)

    if show_details:
        console.print(f"📋 Fetching issue '{issue_id}' details...", style="blue")

        try:
            result = asyncio.run(issue_manager.get_issue(issue_id))

            if result["status"] == "success":
                issue_manager.display_issue_details(result["data"], format_type=format)
            else:
                console.print(f"❌ {result['message']}", style="red")
                raise click.ClickException("Failed to get issue details")

        except Exception as e:
            console.print(f"❌ Error getting issue details: {e}", style="red")
            raise click.ClickException("Failed to get issue details") from e
    else:
        if not any(
            [
                summary is not None,
                description is not None,
                state is not None,
                priority is not None,
                assignee is not None,
                type is not None,
            ]
        ):
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
                message = result.get("message", "Issue updated successfully")
                console.print(f"✅ {message}", style="green")
            else:
                message = result.get("message", "Failed to update issue")
                console.print(f"❌ {message}", style="red")
                raise click.ClickException("Failed to update issue")

        except Exception as e:
            console.print(f"❌ Error updating issue: {e}", style="red")
            raise click.ClickException("Failed to update issue") from e


@issues.command()
@click.argument("issue_id")
@click.option(
    "--force",
    is_flag=True,
    help="Skip confirmation prompt",
)
@click.pass_context
def delete(ctx: click.Context, issue_id: str, force: bool) -> None:
    """Delete an issue."""
    from ..managers.issues import IssueManager

    console = get_console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    issue_manager = IssueManager(auth_manager)

    if not force:
        if not click.confirm(f"Are you sure you want to delete issue '{issue_id}'?"):
            console.print("Delete cancelled.", style="yellow")
            return

    console.print(f"🗑️  Deleting issue '{issue_id}'...", style="blue")

    try:
        result = asyncio.run(issue_manager.delete_issue(issue_id))

        if result["status"] == "success":
            console.print(f"✅ Issue '{issue_id}' deleted successfully", style="green")
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
    help="Maximum number of results to return (legacy, use --page-size instead)",
)
@click.option(
    "--page-size",
    type=int,
    default=100,
    help="Number of results per page (default: 100)",
)
@click.option(
    "--after-cursor",
    help="Start pagination after this cursor",
)
@click.option(
    "--before-cursor",
    help="Start pagination before this cursor",
)
@click.option(
    "--all",
    is_flag=True,
    help="Fetch all results using pagination",
)
@click.option(
    "--max-results",
    type=int,
    help="Maximum total number of results to fetch",
)
@click.option(
    "--fields",
    "-f",
    help="Comma-separated list of fields to return",
)
@click.option(
    "--profile",
    type=click.Choice(["minimal", "standard", "full"]),
    help="Field selection profile (minimal, standard, full). Standard is default.",
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
    fields: Optional[str],
    profile: Optional[str],
    top: Optional[int],
    page_size: int,
    after_cursor: Optional[str],
    before_cursor: Optional[str],
    all: bool,
    max_results: Optional[int],
    format: str,
) -> None:
    """Advanced issue search."""
    from ..managers.issues import IssueManager

    console = get_console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    issue_manager = IssueManager(auth_manager)

    console.print(f"🔍 Searching issues for '{query}'...", style="blue")

    try:
        # Determine pagination settings
        use_pagination = bool(all or after_cursor or before_cursor or max_results)

        # Handle conflicting parameters
        if top and page_size != 100:
            console.print(
                "⚠️  Warning: Both --top and --page-size specified. Using --top for backward compatibility.",
                style="yellow",
            )

        result = asyncio.run(
            issue_manager.search_issues(
                query=query,
                project_id=project_id,
                fields=fields,
                field_profile=profile,
                top=top,
                page_size=page_size,
                after_cursor=after_cursor,
                before_cursor=before_cursor,
                use_pagination=use_pagination,
                max_results=max_results,
            )
        )

        if result["status"] == "success":
            issues = result["data"]

            if format == "table":
                issue_manager.display_issues_table(issues)
                console.print(f"\n[dim]Found: {result['count']} issues[/dim]")

                # Display pagination info if available
                if "pagination" in result:
                    pagination = result["pagination"]
                    if pagination["has_after"] or pagination["has_before"]:
                        console.print("[dim]Pagination:[/dim]", end="")
                        if pagination["after_cursor"]:
                            console.print(f" [dim]next: --after-cursor {pagination['after_cursor']}[/dim]", end="")
                        if pagination["before_cursor"]:
                            console.print(f" [dim]prev: --before-cursor {pagination['before_cursor']}[/dim]", end="")
                        console.print()
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
    """Assign an issue to a user.

    Assigns the specified issue to a user by their username.
    Use 'me' to assign the issue to yourself.

    Examples:
        # Assign issue to a specific user
        yt issues assign DEMO-20 admin

        # Assign issue to yourself
        yt issues assign WEB-123 me

    Note: Use the username directly as a positional argument, not --assignee flag.
    """
    from ..managers.issues import IssueManager

    console = get_console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    issue_manager = IssueManager(auth_manager)

    # Handle 'me' keyword by resolving to current user's login
    if assignee == "me":
        try:
            credentials = auth_manager.load_credentials()
            if credentials:
                # Try to get current user from API to ensure we have the latest info
                verification_result = asyncio.run(
                    auth_manager.verify_credentials(credentials.base_url, credentials.token)
                )
                if (
                    verification_result.status == "success"
                    and verification_result.username
                    and verification_result.username != "Unknown"
                ):
                    assignee = verification_result.username
                    console.print(f"👤 Resolving 'me' to current user: {assignee}", style="blue")
                elif credentials.username and credentials.username != "Unknown":
                    # Fallback to stored username if API verification doesn't give us the username
                    assignee = credentials.username
                    console.print(f"👤 Resolving 'me' to stored user: {assignee}", style="blue")
                else:
                    console.print("❌ Unable to resolve 'me' - could not determine current user", style="red")
                    console.print("💡 Hint: Try using your actual username instead of 'me'", style="yellow")
                    raise click.ClickException("Unable to resolve current user") from None
            else:
                console.print("❌ Unable to resolve 'me' - not authenticated", style="red")
                raise click.ClickException("Unable to resolve current user") from None
        except Exception as e:
            console.print(f"❌ Unable to resolve 'me' - {str(e)}", style="red")
            raise click.ClickException("Unable to resolve current user") from None

    console.print(f"👤 Assigning issue '{issue_id}' to '{assignee}'...", style="blue")

    try:
        result = asyncio.run(issue_manager.assign_issue(issue_id, assignee))

        if result["status"] == "success":
            message = result.get("message", f"Issue {issue_id} assigned to {assignee}")
            console.print(f"✅ {message}", style="green")
        else:
            message = result.get("message", f"Failed to assign issue {issue_id} to {assignee}")
            console.print(f"❌ {message}", style="red")
            raise click.ClickException("Failed to assign issue")

    except click.ClickException:
        raise
    except Exception as e:
        console.print(f"❌ Error assigning issue: {e}", style="red")
        console.print("💡 Correct usage: yt issues assign ISSUE-ID USERNAME", style="blue")
        console.print("💡 Example: yt issues assign DEMO-20 admin", style="blue")
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
    """Move an issue between states or projects.

    Move an issue to a different state within the same project, or move it
    to a different project entirely. When moving between projects, the issue
    will be transferred with all its data preserved.

    Examples:
        # Move issue to different state
        yt issues move DEMO-123 --state "In Progress"

        # Move issue to different project
        yt issues move DEMO-123 --project-id WEB

        # Using short form
        yt issues move DEMO-123 -s "Done"
        yt issues move DEMO-123 -p TEST

    Note: When moving between projects, ensure you have appropriate permissions
    in both the source and target projects. Custom fields may need attention
    if they differ between projects.
    """
    from ..managers.issues import IssueManager

    console = get_console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    issue_manager = IssueManager(auth_manager)

    if not state and not project_id:
        console.print("❌ Must specify either --state or --project-id", style="red")
        return

    console.print(f"🚚 Moving issue '{issue_id}'...", style="blue")

    try:
        result = asyncio.run(issue_manager.move_issue(issue_id, state=state, project_id=project_id))

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


@tag.command(name="add")
@click.argument("issue_id")
@click.argument("tag_name")
@click.option(
    "--create-if-missing",
    is_flag=True,
    help="Create the tag if it doesn't exist",
)
@click.pass_context
def add_tag(ctx: click.Context, issue_id: str, tag_name: str, create_if_missing: bool) -> None:
    """Add a tag to an issue.

    By default, the tag must already exist. Use --create-if-missing to create
    the tag if it doesn't exist.

    Examples:
        # Add existing tag
        yt issues tag add DEMO-23 "bug"

        # Create and add new tag
        yt issues tag add DEMO-23 "urgent" --create-if-missing
    """
    from ..managers.issues import IssueManager

    console = get_console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    issue_manager = IssueManager(auth_manager)

    console.print(f"🏷️  Adding tag '{tag_name}' to issue '{issue_id}'...", style="blue")

    try:
        result = asyncio.run(issue_manager.add_tag(issue_id, tag_name, create_if_missing))

        if result["status"] == "success":
            message = result.get("message", "Tag added successfully")
            console.print(f"✅ {message}", style="green")
        else:
            message = result.get("message", "Failed to add tag")
            console.print(f"❌ {message}", style="red")
            if "not found" in message.lower() and not create_if_missing:
                console.print(
                    f"💡 Hint: Use --create-if-missing to create the tag '{tag_name}' if it doesn't exist",
                    style="yellow",
                )
            raise click.ClickException("Failed to add tag")

    except Exception as e:
        console.print(f"❌ Error adding tag: {e}", style="red")
        raise click.ClickException("Failed to add tag") from e


@tag.command(name="remove")
@click.argument("issue_id")
@click.argument("tag_name")
@click.pass_context
def remove_tag(ctx: click.Context, issue_id: str, tag_name: str) -> None:
    """Remove a tag from an issue."""
    from ..managers.issues import IssueManager

    console = get_console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    issue_manager = IssueManager(auth_manager)

    console.print(f"🏷️  Removing tag '{tag_name}' from issue '{issue_id}'...", style="blue")

    try:
        result = asyncio.run(issue_manager.remove_tag(issue_id, tag_name))

        if result["status"] == "success":
            message = result.get("message", "Tag removed successfully")
            console.print(f"✅ {message}", style="green")
        else:
            message = result.get("message", "Failed to remove tag")
            console.print(f"❌ {message}", style="red")
            raise click.ClickException("Failed to remove tag")

    except Exception as e:
        console.print(f"❌ Error removing tag: {e}", style="red")
        raise click.ClickException("Failed to remove tag") from e


@tag.command(name="list")
@click.argument("issue_id")
@click.pass_context
def list_tags(ctx: click.Context, issue_id: str) -> None:
    """List all tags for an issue."""
    from ..managers.issues import IssueManager

    console = get_console()
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


class CommentsGroup(AliasedGroup):
    """Enhanced comments group with specific error handling for create vs add."""

    def get_command(self, ctx: click.Context, cmd_name: str):
        """Get command with enhanced error handling for create vs add suggestion."""
        # Handle the specific case of 'create' -> 'add' suggestion
        if cmd_name == "create":
            from ..exceptions import CommandValidationError
            from ..utils import display_error, handle_error

            error = CommandValidationError(
                "Command 'create' not found for comments",
                command_path=f"{ctx.info_name} comments create",
                similar_commands=["add"],
                usage_example=f'{ctx.info_name} comments add ISSUE-ID "Your comment text"',
            )

            error_result = handle_error(error, "command lookup")
            display_error(error_result)

            # Return None to let Click show its normal error, but we've already shown helpful info
            return None

        return super().get_command(ctx, cmd_name)


@issues.group(cls=CommentsGroup)
def comments() -> None:
    """Manage issue comments.

    Use 'add' to create new comments, not 'create'.

    Examples:
        # Add a comment to an issue
        yt issues comments add ISSUE-123 "Your comment text"

        # List comments on an issue
        yt issues comments list ISSUE-123
    """
    pass


@comments.command(name="add")
@click.argument("issue_id", callback=validate_issue_id_format)
@click.argument("text")
@click.pass_context
def add_comment(ctx: click.Context, issue_id: str, text: str) -> None:
    """Add a comment to an issue.

    Adds a comment to the specified issue with the provided text.

    Examples:
        # Add a simple comment
        yt issues comments add DEMO-20 "Fixed in latest build"

        # Add a longer comment with quotes
        yt issues comments add WEB-123 "This issue was caused by a race condition in the login module"

    Note: Use the comment text directly as a positional argument, not --text flag.
    There is no 'create' subcommand; use 'add' instead.
    """
    from ..managers.issues import IssueManager

    console = get_console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    issue_manager = IssueManager(auth_manager)

    console.print(f"💬 Adding comment to issue '{issue_id}'...", style="blue")

    try:
        result = asyncio.run(issue_manager.add_comment(issue_id, text))

        if result["status"] == "success":
            console.print(f"✅ Comment added successfully to issue '{issue_id}'", style="green")
        else:
            console.print(f"❌ {result['message']}", style="red")
            raise click.ClickException("Failed to add comment")

    except click.ClickException:
        raise
    except Exception as e:
        console.print(f"❌ Error adding comment: {e}", style="red")
        console.print('💡 Correct usage: yt issues comments add ISSUE-ID "Your comment text"', style="blue")
        console.print('💡 Example: yt issues comments add DEMO-20 "Fixed in latest build"', style="blue")
        console.print("💡 Note: Use 'add' not 'create' for comments", style="blue")
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
    from ..managers.issues import IssueManager

    console = get_console()
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
def update_comment(ctx: click.Context, issue_id: str, comment_id: str, text: str) -> None:
    """Update an existing comment."""
    from ..managers.issues import IssueManager

    console = get_console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    issue_manager = IssueManager(auth_manager)

    console.print(f"✏️  Updating comment '{comment_id}'...", style="blue")

    try:
        result = asyncio.run(issue_manager.update_comment(issue_id, comment_id, text))

        if result["status"] == "success":
            console.print(f"✅ Comment '{comment_id}' updated successfully", style="green")
        else:
            console.print(f"❌ {result['message']}", style="red")
            raise click.ClickException("Failed to update comment")

    except Exception as e:
        console.print(f"❌ Error updating comment: {e}", style="red")
        raise click.ClickException("Failed to update comment") from e


@comments.command(name="delete")
@click.argument("issue_id")
@click.argument("comment_id")
@click.option(
    "--force",
    is_flag=True,
    help="Skip confirmation prompt",
)
@click.pass_context
def delete_comment(ctx: click.Context, issue_id: str, comment_id: str, force: bool) -> None:
    """Delete a comment."""
    from ..managers.issues import IssueManager

    console = get_console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    issue_manager = IssueManager(auth_manager)

    if not force:
        if not click.confirm(f"Are you sure you want to delete comment '{comment_id}'?"):
            console.print("Delete cancelled.", style="yellow")
            return

    console.print(f"🗑️  Deleting comment '{comment_id}'...", style="blue")

    try:
        result = asyncio.run(issue_manager.delete_comment(issue_id, comment_id))

        if result["status"] == "success":
            console.print(f"✅ Comment '{comment_id}' deleted successfully", style="green")
        else:
            console.print(f"❌ {result['message']}", style="red")
            raise click.ClickException("Failed to delete comment")

    except Exception as e:
        console.print(f"❌ Error deleting comment: {e}", style="red")
        raise click.ClickException("Failed to delete comment") from e


@issues.group()
def attach() -> None:
    """Manage issue attachments.

    This command group requires a subcommand to specify the action.
    Available subcommands: list, upload, download, delete

    Examples:
        # List attachments for an issue
        yt issues attach list ISSUE-123

        # Upload a file to an issue
        yt issues attach upload ISSUE-123 /path/to/file.txt

    Note: Use 'yt issues attach --help' to see all available subcommands.
    """
    pass


@attach.command(name="upload")
@click.argument("issue_id")
@click.argument("file_path", type=click.Path(exists=True))
@click.pass_context
def upload(ctx: click.Context, issue_id: str, file_path: str) -> None:
    """Upload a file to an issue."""
    from ..managers.issues import IssueManager

    console = get_console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    issue_manager = IssueManager(auth_manager)

    console.print(f"📎 Uploading file '{file_path}' to issue '{issue_id}'...", style="blue")

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


@attach.command(name="download")
@click.argument("issue_id")
@click.argument("attachment_id")
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output file path",
)
@click.pass_context
def download(ctx: click.Context, issue_id: str, attachment_id: str, output: Optional[str]) -> None:
    """Download an attachment from an issue."""
    from ..managers.issues import IssueManager

    console = get_console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    issue_manager = IssueManager(auth_manager)

    if not output:
        output = f"attachment_{attachment_id}"

    console.print(f"📥 Downloading attachment '{attachment_id}' to '{output}'...", style="blue")

    try:
        result = asyncio.run(issue_manager.download_attachment(issue_id, attachment_id, output))

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
    type=click.Choice(["table", "json", "csv"]),
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
    from ..managers.issues import IssueManager

    console = get_console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    issue_manager = IssueManager(auth_manager)

    # Print progress message to stderr when JSON format is used to avoid polluting JSON output
    if format == "json":
        import sys

        from rich.console import Console

        stderr_console = Console(file=sys.stderr)
        stderr_console.print(f"📎 Fetching attachments for issue '{issue_id}'...", style="blue")
    else:
        console.print(f"📎 Fetching attachments for issue '{issue_id}'...", style="blue")

    try:
        result = asyncio.run(issue_manager.list_attachments(issue_id))

        if result["status"] == "success":
            attachments = result["data"]

            if format == "table":
                issue_manager.display_attachments_table(attachments)
            elif format == "csv":
                csv_output = _format_attachments_as_csv(attachments)
                console.print(csv_output)
            else:
                import json

                console.print(json.dumps(attachments, indent=2))
        else:
            console.print(f"❌ {result['message']}", style="red")
            raise click.ClickException("Failed to list attachments")

    except Exception as e:
        console.print(f"❌ Error listing attachments: {e}", style="red")
        raise click.ClickException("Failed to list attachments") from e


@attach.command(name="delete")
@click.argument("issue_id")
@click.argument("attachment_id")
@click.option(
    "--force",
    is_flag=True,
    help="Skip confirmation prompt",
)
@click.pass_context
def delete_attachment(ctx: click.Context, issue_id: str, attachment_id: str, force: bool) -> None:
    """Delete an attachment from an issue."""
    from ..managers.issues import IssueManager

    console = get_console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    issue_manager = IssueManager(auth_manager)

    if not force:
        if not click.confirm(f"Are you sure you want to delete attachment '{attachment_id}'?"):
            console.print("Delete cancelled.", style="yellow")
            return

    console.print(f"🗑️  Deleting attachment '{attachment_id}'...", style="blue")

    try:
        result = asyncio.run(issue_manager.delete_attachment(issue_id, attachment_id))

        if result["status"] == "success":
            console.print(f"✅ Attachment '{attachment_id}' deleted successfully", style="green")
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
def create_link(ctx: click.Context, source_issue_id: str, target_issue_id: str, link_type: str) -> None:
    """Create a link between two issues."""
    from ..managers.issues import IssueManager

    console = get_console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    issue_manager = IssueManager(auth_manager)

    console.print(
        f"🔗 Creating '{link_type}' link between '{source_issue_id}' and '{target_issue_id}'...",
        style="blue",
    )

    try:
        result = asyncio.run(issue_manager.create_link(source_issue_id, target_issue_id, link_type))

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
    from ..managers.issues import IssueManager

    console = get_console()
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


@links.command(name="delete")
@click.argument("source_issue_id")
@click.argument("target_issue_id")
@click.argument("link_type")
@click.option(
    "--force",
    is_flag=True,
    help="Skip confirmation prompt",
)
@click.pass_context
def delete_link(ctx: click.Context, source_issue_id: str, target_issue_id: str, link_type: str, force: bool) -> None:
    """Remove a link between issues."""
    from ..managers.issues import IssueManager

    console = get_console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    issue_manager = IssueManager(auth_manager)

    if not force:
        if not click.confirm(
            f"Are you sure you want to delete '{link_type}' link between '{source_issue_id}' and '{target_issue_id}'?"
        ):
            console.print("Delete cancelled.", style="yellow")
            return

    console.print(
        f"🔗 Deleting '{link_type}' link between '{source_issue_id}' and '{target_issue_id}'...", style="blue"
    )

    try:
        result = asyncio.run(issue_manager.delete_link(source_issue_id, target_issue_id, link_type))

        if result["status"] == "success":
            console.print(f"✅ {result['message']}", style="green")
        else:
            console.print(f"❌ {result['message']}", style="red")
            raise click.ClickException("Failed to delete link")

    except Exception as e:
        console.print(f"❌ Error deleting link: {e}", style="red")
        raise click.ClickException("Failed to delete link") from e


@links.command(name="types")
@click.option(
    "--format",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Output format",
)
@click.pass_context
def types(ctx: click.Context, format: str) -> None:
    """List available link types."""
    from ..managers.issues import IssueManager

    console = get_console()
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


@issues.command()
@click.argument("issue_id")
@click.option(
    "--format",
    type=click.Choice(["table", "panel"], case_sensitive=False),
    default="table",
    help="Output format for issue details (table or panel)",
)
@click.pass_context
def show(ctx: click.Context, issue_id: str, format: str) -> None:
    """Show detailed information about an issue."""
    from ..managers.issues import IssueManager

    console = get_console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    issue_manager = IssueManager(auth_manager)

    console.print(f"📋 Fetching issue '{issue_id}' details...", style="blue")

    try:
        result = asyncio.run(issue_manager.get_issue(issue_id))

        if result["status"] == "success":
            issue_manager.display_issue_details(result["data"], format_type=format)
        else:
            console.print(f"❌ {result['message']}", style="red")
            raise click.ClickException("Failed to get issue details")

    except Exception as e:
        console.print(f"❌ Error getting issue details: {e}", style="red")
        raise click.ClickException("Failed to get issue details") from e


@issues.command()
@click.argument("issue_id")
@click.option(
    "--format",
    type=click.Choice(["tree", "table"], case_sensitive=False),
    default="tree",
    help="Output format for dependencies display",
)
@click.option(
    "--show-status",
    is_flag=True,
    default=True,
    help="Show status indicators in tree view",
)
@click.pass_context
def dependencies(ctx: click.Context, issue_id: str, format: str, show_status: bool) -> None:
    """Show issue dependencies and relationships in tree format."""
    from ..managers.issues import IssueManager
    from ..trees import create_issue_dependencies_tree

    console = get_console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    issue_manager = IssueManager(auth_manager)

    console.print(f"🔗 Fetching dependencies for issue '{issue_id}'...", style="blue")

    async def get_issue_and_links():
        """Get both issue details and links in a single async context."""
        issue_result = await issue_manager.get_issue(issue_id)
        if issue_result["status"] != "success":
            return issue_result, None

        links_result = await issue_manager.list_links(issue_id)
        return issue_result, links_result

    try:
        issue_result, links_result = asyncio.run(get_issue_and_links())

        if issue_result["status"] != "success":
            console.print(f"❌ {issue_result['message']}", style="red")
            raise click.ClickException("Failed to get issue details")

        if links_result is None or links_result["status"] != "success":
            console.print(f"❌ {links_result['message'] if links_result else 'Failed to get links'}", style="red")
            raise click.ClickException("Failed to get issue links")

        issue_data = issue_result["data"]
        links_data = links_result["data"]

        if format == "tree":
            # Create and display dependency tree
            tree = create_issue_dependencies_tree(issue_data, links_data, show_status)
            console.print(tree)
        else:
            # Fall back to table format
            issue_manager.display_links_table(links_data)

    except Exception as e:
        console.print(f"❌ Error getting dependencies: {e}", style="red")
        raise click.ClickException("Failed to get dependencies") from e


@issues.command()
@click.option(
    "--project-id",
    "-p",
    help="Project ID to benchmark with",
)
@click.option(
    "--sample-size",
    type=int,
    default=50,
    help="Number of issues to fetch for benchmarking (default: 50)",
)
@click.pass_context
def benchmark(ctx: click.Context, project_id: Optional[str], sample_size: int) -> None:
    """Benchmark field selection performance improvements.

    This command runs performance tests comparing minimal, standard, and full
    field selection profiles to demonstrate the optimization benefits.
    """
    from ..performance_benchmark import run_benchmark

    console = get_console()
    auth_manager = AuthManager(ctx.obj.get("config"))

    console.print("🚀 Starting field selection performance benchmark...", style="blue")
    console.print(f"Sample size: {sample_size} issues", style="dim")
    if project_id:
        console.print(f"Project: {project_id}", style="dim")

    try:
        asyncio.run(run_benchmark(auth_manager=auth_manager, project_id=project_id, sample_size=sample_size))

    except Exception as e:
        console.print(f"❌ Benchmark failed: {e}", style="red")
        raise click.ClickException("Benchmark failed") from e


@issues.group()
def batch() -> None:
    """Batch operations for issues."""
    pass


@batch.command(name="create")
@click.option(
    "--file",
    "-f",
    "file_path",
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help="Path to CSV or JSON file containing issue data",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Validate and preview operations without executing them",
)
@click.option(
    "--continue-on-error",
    is_flag=True,
    default=True,
    help="Continue processing after errors (default: true)",
)
@click.option(
    "--save-failed",
    type=click.Path(path_type=Path),
    help="Save failed operations to specified file for retry",
)
@click.option(
    "--rollback-on-error",
    is_flag=True,
    help="Rollback (delete) created issues if any operation fails",
)
@click.pass_context
def batch_create(
    ctx: click.Context,
    file_path: Path,
    dry_run: bool,
    continue_on_error: bool,
    save_failed: Optional[Path],
    rollback_on_error: bool,
) -> None:
    r"""Batch create issues from CSV or JSON file.

    Create multiple issues at once from a properly formatted CSV or JSON file.
    The file should contain columns/fields for: project_id, summary, description,
    type, priority, and assignee.

    Examples:
        # Create issues from CSV file
        yt issues batch create --file issues.csv

        # Dry run to preview operations
        yt issues batch create --file issues.csv --dry-run

        # Create with error handling
        yt issues batch create --file issues.csv --save-failed failed.csv

        # Create with rollback on error
        yt issues batch create --file issues.csv --rollback-on-error
    """
    from ..batch import BatchOperationManager, BatchValidationError

    console = get_console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    batch_manager = BatchOperationManager(auth_manager)

    console.print(f"🔍 Validating batch create file: {file_path}", style="blue")

    try:
        # Validate the input file
        validated_items = batch_manager.validate_file(file_path, "create")
        console.print(f"✅ Validation successful! Found {len(validated_items)} items to process.", style="green")

        # Perform the batch operation
        result = asyncio.run(
            batch_manager.batch_create_issues(validated_items, dry_run=dry_run, continue_on_error=continue_on_error)  # type: ignore[arg-type]
        )

        # Display summary
        batch_manager.display_operation_summary(result)

        # Handle failures
        if result.errors:
            if rollback_on_error and result.created_items and not dry_run:
                console.print(f"[yellow]Rolling back {len(result.created_items)} created issues...[/yellow]")
                rollback_count = asyncio.run(batch_manager.rollback_created_issues(result.created_items))
                console.print(f"[yellow]Rolled back {rollback_count} issues.[/yellow]")

            if save_failed:
                batch_manager.save_failed_operations(result, save_failed)

        # Exit with appropriate code
        if result.failed > 0 and not dry_run:
            raise click.ClickException(f"Batch operation completed with {result.failed} failures")

    except BatchValidationError as e:
        console.print(f"❌ Validation failed: {e.message}", style="red")
        batch_manager.display_validation_errors(e.errors)
        raise click.ClickException("File validation failed") from e
    except Exception as e:
        console.print(f"❌ Error during batch create: {e}", style="red")
        raise click.ClickException("Batch create failed") from e


@batch.command(name="update")
@click.option(
    "--file",
    "-f",
    "file_path",
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help="Path to CSV or JSON file containing issue update data",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Validate and preview operations without executing them",
)
@click.option(
    "--continue-on-error",
    is_flag=True,
    default=True,
    help="Continue processing after errors (default: true)",
)
@click.option(
    "--save-failed",
    type=click.Path(path_type=Path),
    help="Save failed operations to specified file for retry",
)
@click.pass_context
def batch_update(
    ctx: click.Context,
    file_path: Path,
    dry_run: bool,
    continue_on_error: bool,
    save_failed: Optional[Path],
) -> None:
    r"""Batch update issues from CSV or JSON file.

    Update multiple issues at once from a properly formatted CSV or JSON file.
    The file should contain columns/fields for: issue_id (required), and any
    combination of summary, description, state, type, priority, assignee.

    Examples:
        # Update issues from CSV file
        yt issues batch update --file updates.csv

        # Dry run to preview operations
        yt issues batch update --file updates.csv --dry-run

        # Update with error handling
        yt issues batch update --file updates.csv --save-failed failed.csv
    """
    from ..batch import BatchOperationManager, BatchValidationError

    console = get_console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    batch_manager = BatchOperationManager(auth_manager)

    console.print(f"🔍 Validating batch update file: {file_path}", style="blue")

    async def run_batch_update():
        # Validate the input file with API compatibility checking
        validated_items = await batch_manager.validate_file_with_api_check(file_path, "update")
        console.print(f"✅ Validation successful! Found {len(validated_items)} items to process.", style="green")

        # Perform the batch operation
        return await batch_manager.batch_update_issues(
            validated_items, dry_run=dry_run, continue_on_error=continue_on_error
        )  # type: ignore[arg-type]

    try:
        result = asyncio.run(run_batch_update())

        # Display summary
        batch_manager.display_operation_summary(result)

        # Handle failures
        if result.errors and save_failed:
            batch_manager.save_failed_operations(result, save_failed)

        # Exit with appropriate code
        if result.failed > 0 and not dry_run:
            raise click.ClickException(f"Batch operation completed with {result.failed} failures")

    except BatchValidationError as e:
        console.print(f"❌ Validation failed: {e.message}", style="red")
        batch_manager.display_validation_errors(e.errors)
        raise click.ClickException("File validation failed") from e
    except Exception as e:
        console.print(f"❌ Error during batch update: {e}", style="red")
        raise click.ClickException("Batch update failed") from e


@batch.command()
@click.option(
    "--file",
    "-f",
    "file_path",
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help="Path to CSV or JSON file to validate",
)
@click.option(
    "--operation",
    type=click.Choice(["create", "update"]),
    required=True,
    help="Type of operation to validate for",
)
@click.pass_context
def validate(
    ctx: click.Context,
    file_path: Path,
    operation: str,
) -> None:
    r"""Validate a batch operation file without executing operations.

    Check if a CSV or JSON file is properly formatted for batch operations
    and display any validation errors found.

    Examples:
        # Validate a file for batch create
        yt issues batch validate --file issues.csv --operation create

        # Validate a file for batch update
        yt issues batch validate --file updates.json --operation update
    """
    from ..batch import BatchOperationManager, BatchValidationError

    console = get_console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    batch_manager = BatchOperationManager(auth_manager)

    console.print(f"🔍 Validating {operation} file: {file_path}", style="blue")

    async def run_validation():
        # Use enhanced validation for update operations to check API compatibility
        if operation == "update":
            return await batch_manager.validate_file_with_api_check(file_path, operation)
        else:
            return batch_manager.validate_file(file_path, operation)

    try:
        validated_items = asyncio.run(run_validation())
        console.print("✅ Validation successful!", style="green")
        console.print(f"Found {len(validated_items)} valid items for {operation} operation.", style="green")

        # Show a preview of the first few items
        if validated_items:
            console.print(f"\n📋 Preview of first {min(3, len(validated_items))} items:", style="blue")
            for i, item in enumerate(validated_items[:3]):
                console.print(f"  {i + 1}. {item}", style="dim")

            if len(validated_items) > 3:
                console.print(f"  ... and {len(validated_items) - 3} more items", style="dim")

    except BatchValidationError as e:
        console.print(f"❌ Validation failed: {e.message}", style="red")
        batch_manager.display_validation_errors(e.errors)
        raise click.ClickException("File validation failed") from e
    except Exception as e:
        console.print(f"❌ Error during validation: {e}", style="red")
        raise click.ClickException("Validation failed") from e


@batch.command()
@click.option(
    "--format",
    type=click.Choice(["csv", "json"]),
    default="csv",
    help="Template format to generate (default: csv)",
)
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(path_type=Path),
    default=".",
    help="Directory to save template files (default: current directory)",
)
@click.pass_context
def templates(
    ctx: click.Context,
    format: str,
    output_dir: Path,
) -> None:
    r"""Generate template files for batch operations.

    Create example template files that can be used as starting points
    for batch create and update operations.

    Examples:
        # Generate CSV templates in current directory
        yt issues batch templates

        # Generate JSON templates in specific directory
        yt issues batch templates --format json --output-dir ./templates
    """
    from ..batch import generate_template_files

    console = get_console()

    console.print(f"📄 Generating {format.upper()} template files in {output_dir}...", style="blue")

    try:
        generate_template_files(output_dir, format)

        console.print("\n💡 [blue]Next steps:[/blue]")
        console.print("1. Edit the template files with your data")
        console.print(f"2. Validate: [cyan]yt issues batch validate --file template.{format} --operation create[/cyan]")
        console.print(f"3. Test: [cyan]yt issues batch create --file template.{format} --dry-run[/cyan]")
        console.print(f"4. Execute: [cyan]yt issues batch create --file template.{format}[/cyan]")

    except Exception as e:
        console.print(f"❌ Error generating templates: {e}", style="red")
        raise click.ClickException("Template generation failed") from e


# Add aliases for common subcommands
issues.add_alias("c", "create")
issues.add_alias("new", "create")
issues.add_alias("l", "list")
issues.add_alias("ls", "list")
issues.add_alias("u", "update")
issues.add_alias("edit", "update")
issues.add_alias("s", "search")
issues.add_alias("find", "search")
issues.add_alias("d", "delete")
issues.add_alias("del", "delete")
issues.add_alias("rm", "delete")
