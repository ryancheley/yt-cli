"""Issues command group for YouTrack CLI."""

import asyncio
from typing import Optional

import click

from ..auth import AuthManager
from ..cli_utils import AliasedGroup
from ..console import get_console


@click.group(cls=AliasedGroup)
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
    from ..issues import IssueManager

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
    """List issues with filtering."""
    from ..issues import IssueManager

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
    from ..issues import IssueManager

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
    from ..issues import IssueManager

    console = get_console()
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
    page_size: int,
    after_cursor: Optional[str],
    before_cursor: Optional[str],
    all: bool,
    max_results: Optional[int],
    format: str,
) -> None:
    """Advanced issue search."""
    from ..issues import IssueManager

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
    """Assign an issue to a user."""
    from ..issues import IssueManager

    console = get_console()
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
    from ..issues import IssueManager

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
@click.pass_context
def add_tag(ctx: click.Context, issue_id: str, tag_name: str) -> None:
    """Add a tag to an issue. Creates the tag if it doesn't exist."""
    from ..issues import IssueManager

    console = get_console()
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


@tag.command(name="remove")
@click.argument("issue_id")
@click.argument("tag_name")
@click.pass_context
def remove_tag(ctx: click.Context, issue_id: str, tag_name: str) -> None:
    """Remove a tag from an issue."""
    from ..issues import IssueManager

    console = get_console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    issue_manager = IssueManager(auth_manager)

    console.print(f"🏷️  Removing tag '{tag_name}' from issue '{issue_id}'...", style="blue")

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
    from ..issues import IssueManager

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
    from ..issues import IssueManager

    console = get_console()
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
    from ..issues import IssueManager

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
    from ..issues import IssueManager

    console = get_console()
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


@comments.command(name="delete")
@click.argument("issue_id")
@click.argument("comment_id")
@click.option(
    "--confirm",
    is_flag=True,
    help="Skip confirmation prompt",
)
@click.pass_context
def delete_comment(ctx: click.Context, issue_id: str, comment_id: str, confirm: bool) -> None:
    """Delete a comment."""
    from ..issues import IssueManager

    console = get_console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    issue_manager = IssueManager(auth_manager)

    if not confirm:
        if not click.confirm(f"Are you sure you want to delete comment '{comment_id}'?"):
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


@attach.command(name="upload")
@click.argument("issue_id")
@click.argument("file_path", type=click.Path(exists=True))
@click.pass_context
def upload(ctx: click.Context, issue_id: str, file_path: str) -> None:
    """Upload a file to an issue."""
    from ..issues import IssueManager

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
    from ..issues import IssueManager

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
    from ..issues import IssueManager

    console = get_console()
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


@attach.command(name="delete")
@click.argument("issue_id")
@click.argument("attachment_id")
@click.option(
    "--confirm",
    is_flag=True,
    help="Skip confirmation prompt",
)
@click.pass_context
def delete_attachment(ctx: click.Context, issue_id: str, attachment_id: str, confirm: bool) -> None:
    """Delete an attachment from an issue."""
    from ..issues import IssueManager

    console = get_console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    issue_manager = IssueManager(auth_manager)

    if not confirm:
        if not click.confirm(f"Are you sure you want to delete attachment '{attachment_id}'?"):
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
def create_link(ctx: click.Context, source_issue_id: str, target_issue_id: str, link_type: str) -> None:
    """Create a link between two issues."""
    from ..issues import IssueManager

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
    from ..issues import IssueManager

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
@click.argument("link_id")
@click.option(
    "--confirm",
    is_flag=True,
    help="Skip confirmation prompt",
)
@click.pass_context
def delete_link(ctx: click.Context, source_issue_id: str, link_id: str, confirm: bool) -> None:
    """Remove a link between issues."""
    from ..issues import IssueManager

    console = get_console()
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
    from ..issues import IssueManager

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
    from ..issues import IssueManager

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
    from ..issues import IssueManager
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
