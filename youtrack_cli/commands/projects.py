"""Projects command group for YouTrack CLI.

This module provides project management commands for listing, viewing,
and managing YouTrack projects including their metadata and configuration.
"""

import asyncio
from typing import Optional

import click

from ..auth import AuthManager
from ..console import get_console


def show_projects_verbose_help(ctx):
    """Show comprehensive help for the projects command group."""
    from rich.console import Console

    console = Console()

    # Main title
    console.print("\n[bold blue]yt projects[/bold blue] - Project Management\n")

    # Description
    console.print("Manage projects - list, view, and configure project settings.")
    console.print("The projects command group provides access to project-level operations")
    console.print("including listing available projects, viewing project details, and")
    console.print("managing project configuration.\n")

    # Usage
    console.print("[bold]Usage:[/bold] yt projects [OPTIONS] COMMAND [ARGS]...\n")

    # Commands
    console.print("[bold]Commands:[/bold]")
    console.print("  list          List all accessible projects")
    console.print("  show          Show detailed project information")
    console.print("")

    # Common Examples
    console.print("[bold]Common Examples:[/bold]")
    console.print("  # List all projects")
    console.print("  yt projects list")
    console.print("")
    console.print("  # List projects with specific fields")
    console.print("  yt projects list --fields name,shortName,archived --format json")
    console.print("")
    console.print("  # Show project details")
    console.print("  yt projects show PROJECT-ID")
    console.print("")
    console.print("  # List projects including archived ones")
    console.print("  yt projects list --show-archived")
    console.print("")

    # Options
    console.print("[bold]Options:[/bold]")
    console.print("  --help-verbose    Show this detailed help")
    console.print("  -h, --help        Show basic help and exit")
    console.print("")

    # Tips
    console.print("[bold]Tips:[/bold]")
    console.print("  • Use --fields to control which project information is returned")
    console.print("  • Projects are identified by their short name or ID")
    console.print("  • Use --format json for programmatic access to project data")
    console.print("  • Archive status affects project visibility in most operations")
    console.print("")


def add_help_verbose_option(func):
    """Decorator to add --help-verbose option to projects commands."""

    def callback(ctx, param, value):
        if value:
            show_projects_verbose_help(ctx)
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


@click.group()
@add_help_verbose_option
def projects() -> None:
    """Manage YouTrack projects - list, view, and configure settings.

    Core Commands:
        list    List all accessible projects
        show    Show detailed project information

    Quick Start:
        # List all projects
        yt projects list

        # Show project details
        yt projects show PROJECT-ID

    For complete help with all commands and examples, use:
        yt projects --help-verbose
    """
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
    help="Maximum number of projects to return (legacy, use --page-size instead)",
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
@click.option(
    "--page-size",
    type=int,
    default=100,
    help="Number of projects per page (default: 100)",
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
@click.pass_context
def projects_list(
    ctx: click.Context,
    fields: Optional[str],
    top: Optional[int],
    show_archived: bool,
    format: str,
    page_size: int,
    after_cursor: Optional[str],
    before_cursor: Optional[str],
    all: bool,
    max_results: Optional[int],
) -> None:
    """List all projects."""
    from ..managers.projects import ProjectManager

    console = get_console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    project_manager = ProjectManager(auth_manager)

    console.print("📋 Fetching projects...", style="blue")

    try:
        # Determine pagination settings
        use_pagination = bool(all or after_cursor or before_cursor or max_results)

        result = asyncio.run(
            project_manager.list_projects(
                fields=fields,
                top=top,
                show_archived=show_archived,
                page_size=page_size,
                after_cursor=after_cursor,
                before_cursor=before_cursor,
                use_pagination=use_pagination,
                max_results=max_results,
            )
        )

        if result["status"] == "success":
            projects = result["data"]

            if format == "table":
                project_manager.display_project_list(projects, format_output="table")
                console.print(f"\n[dim]Total: {result['count']} projects[/dim]")

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

                console.print(json.dumps(projects, indent=2))
        else:
            console.print(f"❌ {result['message']}", style="red")
            raise click.ClickException("Failed to list projects")

    except Exception as e:
        console.print(f"❌ Error listing projects: {e}", style="red")
        raise click.ClickException("Failed to list projects") from e


@projects.command(name="show")
@click.argument("project_id")
@click.option(
    "--fields",
    "-f",
    help="Comma-separated list of project fields to return",
)
@click.option(
    "--format",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Output format",
)
@click.pass_context
def projects_show(
    ctx: click.Context,
    project_id: str,
    fields: Optional[str],
    format: str,
) -> None:
    """Show detailed project information.

    Display comprehensive information about a specific project including
    its settings, metadata, and configuration.

    Examples:
        # Show basic project information
        yt projects show PROJECT-ID

        # Show specific project fields
        yt projects show PROJECT-ID --fields name,shortName,leader

        # Show project data in JSON format
        yt projects show PROJECT-ID --format json
    """
    from ..managers.projects import ProjectManager

    console = get_console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    project_manager = ProjectManager(auth_manager)

    console.print(f"📋 Fetching project '{project_id}' details...", style="blue")

    try:
        result = asyncio.run(project_manager.get_project(project_id, fields=fields))

        if result["status"] == "success":
            project = result["data"]

            if format == "table":
                project_manager.display_project_details(project)
            else:
                import json

                console.print(json.dumps(project, indent=2))
        else:
            console.print(f"❌ {result['message']}", style="red")
            raise click.ClickException("Failed to get project details")

    except Exception as e:
        console.print(f"❌ Error getting project details: {e}", style="red")
        raise click.ClickException("Failed to get project details") from e


@projects.command(name="create")
@click.argument("name")
@click.argument("short_name")
@click.option(
    "--leader",
    "-l",
    help="Project leader username (e.g., 'admin', 'ryan') or ID (e.g., '2-3')",
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
    leader: Optional[str],
    description: Optional[str],
    template: Optional[str],
) -> None:
    """Create a new project.

    Creates a new project with the specified name and short name.
    Both name and short_name are required positional arguments.

    Examples:
        # Create a basic project (will prompt for leader)
        yt projects create "CLI Testing Project" CLI-TEST

        # Create a project with all options
        yt projects create "My Project" MP --leader admin --description "Project description" --template scrum

    Note: Both NAME and SHORT_NAME are required positional arguments.
    The leader will be prompted interactively if not specified with --leader.
    """
    from ..managers.projects import ProjectManager

    console = get_console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    project_manager = ProjectManager(auth_manager)

    # Prompt for leader if not provided (maintains backward compatibility)
    if not leader:
        leader = click.prompt("Project leader username (e.g., 'admin', 'ryan') or ID (e.g., '2-3')")

    console.print(f"🚀 Creating project '{name}'...", style="blue")

    try:
        result = asyncio.run(
            project_manager.create_project(
                name=name,
                short_name=short_name,
                leader_login=leader,
                description=description,
                template=template,
            )
        )

        if result["status"] == "success":
            project = result["data"]
            project_name = project.get("name", name)
            console.print(f"✅ Project '{project_name}' created successfully", style="green")
            console.print(f"Project ID: {project.get('id', 'N/A')}", style="blue")
            console.print(f"Short Name: {project.get('shortName', 'N/A')}", style="blue")
        else:
            error_message = result.get("message", "Unknown error occurred")
            console.print(f"❌ {error_message}", style="red")
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
    help="New project leader username (e.g., 'admin', 'ryan') or ID (e.g., '2-3')",
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
    from ..managers.projects import ProjectManager

    console = get_console()
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
                "Use --name, --description, or --leader options, or --show-details to view current settings.",
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
                    leader_login=leader,
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
    "--force",
    is_flag=True,
    help="Skip confirmation prompt",
)
@click.pass_context
def archive(
    ctx: click.Context,
    project_id: str,
    force: bool,
) -> None:
    """Archive a project."""
    from ..managers.projects import ProjectManager

    console = get_console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    project_manager = ProjectManager(auth_manager)

    if not force:
        confirmation_msg = f"Are you sure you want to archive project '{project_id}'?"
        if not click.confirm(confirmation_msg):
            console.print("Archive cancelled.", style="yellow")
            return

    console.print(f"📦 Archiving project '{project_id}'...", style="blue")

    try:
        result = asyncio.run(project_manager.archive_project(project_id))

        if result["status"] == "success":
            console.print(f"✅ {result['message']}", style="green")
            console.print("Project has been archived and is no longer active.", style="yellow")
        else:
            console.print(f"❌ {result['message']}", style="red")
            raise click.ClickException("Failed to archive project")

    except Exception as e:
        console.print(f"❌ Error archiving project: {e}", style="red")
        raise click.ClickException("Failed to archive project") from e


@click.command(name="list")
@click.argument("project_id")
@click.option(
    "--fields",
    "-f",
    help="Comma-separated list of custom field attributes to return",
)
@click.option(
    "--top",
    "-t",
    type=int,
    help="Maximum number of custom fields to return",
)
@click.option(
    "--format",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Output format",
)
@click.pass_context
def fields_list(
    ctx: click.Context,
    project_id: str,
    fields: Optional[str],
    top: Optional[int],
    format: str,
) -> None:
    """List custom fields for a project."""
    from ..managers.projects import ProjectManager

    console = get_console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    project_manager = ProjectManager(auth_manager)

    console.print(f"📋 Fetching custom fields for project '{project_id}'...", style="blue")

    try:
        result = asyncio.run(project_manager.list_custom_fields(project_id=project_id, fields=fields, top=top))

        if result["status"] == "success":
            custom_fields = result["data"]

            if format == "table":
                project_manager.display_custom_fields_table(custom_fields)
                console.print(f"\n[dim]Total: {result['count']} custom fields[/dim]")
            else:
                import json

                console.print(json.dumps(custom_fields, indent=2))
        else:
            console.print(f"❌ {result['message']}", style="red")
            raise click.ClickException("Failed to list custom fields")

    except Exception as e:
        console.print(f"❌ Error listing custom fields: {e}", style="red")
        raise click.ClickException("Failed to list custom fields") from e


@click.command(name="attach")
@click.argument("project_id")
@click.argument("field_id")
@click.option(
    "--type",
    "field_type",
    required=True,
    type=click.Choice(
        [
            "EnumProjectCustomField",
            "MultiEnumProjectCustomField",
            "SingleUserProjectCustomField",
            "MultiUserProjectCustomField",
            "SimpleProjectCustomField",
            "VersionProjectCustomField",
            "MultiVersionProjectCustomField",
            "DateProjectCustomField",
            "IntegerProjectCustomField",
            "FloatProjectCustomField",
            "BooleanProjectCustomField",
        ]
    ),
    help="Type of project custom field to create",
)
@click.option(
    "--required",
    is_flag=True,
    help="Make the field required (cannot be empty)",
)
@click.option(
    "--empty-text",
    help="Text to display when field is empty",
)
@click.option(
    "--private",
    is_flag=True,
    help="Make the field private (not visible to all users)",
)
@click.pass_context
def fields_attach(
    ctx: click.Context,
    project_id: str,
    field_id: str,
    field_type: str,
    required: bool,
    empty_text: Optional[str],
    private: bool,
) -> None:
    """Attach an existing custom field to a project.

    PROJECT_ID: The project ID or short name
    FIELD_ID: The global custom field ID to attach
    """
    from ..managers.projects import ProjectManager

    console = get_console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    project_manager = ProjectManager(auth_manager)

    console.print(f"🔗 Attaching custom field '{field_id}' to project '{project_id}'...", style="blue")

    try:
        result = asyncio.run(
            project_manager.attach_custom_field(
                project_id=project_id,
                field_id=field_id,
                field_type=field_type,
                can_be_empty=not required,
                empty_field_text=empty_text,
                is_public=not private,
            )
        )

        if result["status"] == "success":
            console.print(f"✅ {result['message']}", style="green")
            field_data = result["data"]
            field_name = field_data.get("field", {}).get("name", "N/A")
            console.print(f"Field Name: {field_name}", style="blue")
            console.print(f"Required: {'Yes' if not field_data.get('canBeEmpty', True) else 'No'}", style="blue")
        else:
            console.print(f"❌ {result['message']}", style="red")
            raise click.ClickException("Failed to attach custom field")

    except Exception as e:
        console.print(f"❌ Error attaching custom field: {e}", style="red")
        raise click.ClickException("Failed to attach custom field") from e


@click.command(name="update")
@click.argument("project_id")
@click.argument("field_id")
@click.option(
    "--required/--optional",
    default=None,
    help="Make the field required or optional",
)
@click.option(
    "--empty-text",
    help="Text to display when field is empty",
)
@click.option(
    "--public/--private",
    default=None,
    help="Make the field public or private",
)
@click.pass_context
def fields_update(
    ctx: click.Context,
    project_id: str,
    field_id: str,
    required: Optional[bool],
    empty_text: Optional[str],
    public: Optional[bool],
) -> None:
    """Update settings of a custom field in a project.

    PROJECT_ID: The project ID or short name
    FIELD_ID: The project custom field ID to update
    """
    from ..managers.projects import ProjectManager

    console = get_console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    project_manager = ProjectManager(auth_manager)

    if required is None and empty_text is None and public is None:
        console.print("❌ No updates specified.", style="red")
        console.print(
            "Use --required/--optional, --empty-text, or --public/--private options.",
            style="blue",
        )
        return

    console.print(f"⚙️  Updating custom field '{field_id}' in project '{project_id}'...", style="blue")

    try:
        result = asyncio.run(
            project_manager.update_custom_field(
                project_id=project_id,
                field_id=field_id,
                can_be_empty=not required if required is not None else None,
                empty_field_text=empty_text,
                is_public=public,
            )
        )

        if result["status"] == "success":
            console.print(f"✅ {result['message']}", style="green")
            field_data = result["data"]
            field_name = field_data.get("field", {}).get("name", "N/A")
            console.print(f"Field Name: {field_name}", style="blue")
            console.print(f"Required: {'Yes' if not field_data.get('canBeEmpty', True) else 'No'}", style="blue")
            console.print(f"Visibility: {'Public' if field_data.get('isPublic', True) else 'Private'}", style="blue")
        else:
            console.print(f"❌ {result['message']}", style="red")
            raise click.ClickException("Failed to update custom field")

    except Exception as e:
        console.print(f"❌ Error updating custom field: {e}", style="red")
        raise click.ClickException("Failed to update custom field") from e


@click.command(name="detach")
@click.argument("project_id")
@click.argument("field_id")
@click.option(
    "--force",
    is_flag=True,
    help="Skip confirmation prompt",
)
@click.pass_context
def fields_detach(
    ctx: click.Context,
    project_id: str,
    field_id: str,
    force: bool,
) -> None:
    """Remove a custom field from a project.

    PROJECT_ID: The project ID or short name
    FIELD_ID: The project custom field ID to remove
    """
    from ..managers.projects import ProjectManager

    console = get_console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    project_manager = ProjectManager(auth_manager)

    if not force:
        confirmation_msg = f"Are you sure you want to remove custom field '{field_id}' from project '{project_id}'?"
        if not click.confirm(confirmation_msg):
            console.print("Operation cancelled.", style="yellow")
            return

    console.print(f"🗑️  Removing custom field '{field_id}' from project '{project_id}'...", style="blue")

    try:
        result = asyncio.run(project_manager.detach_custom_field(project_id, field_id))

        if result["status"] == "success":
            console.print(f"✅ {result['message']}", style="green")
        else:
            console.print(f"❌ {result['message']}", style="red")
            raise click.ClickException("Failed to remove custom field")

    except Exception as e:
        console.print(f"❌ Error removing custom field: {e}", style="red")
        raise click.ClickException("Failed to remove custom field") from e


# Create a simple fields group
@click.group()
def fields() -> None:
    """Manage project custom fields.

    This command group provides access to project custom field operations
    including listing, attaching, updating, and removing custom fields.

    Example:
        yt projects fields list PROJECT-ID
        yt projects fields attach PROJECT-ID FIELD-ID
    """
    pass


# Add all the commands to the group
fields.add_command(fields_list)
fields.add_command(fields_attach)
fields.add_command(fields_update)
fields.add_command(fields_detach)

# Add the fields command group to the projects group
projects.add_command(fields)
