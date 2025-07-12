"""Projects command group for YouTrack CLI."""

import asyncio
from typing import Optional

import click

from ..auth import AuthManager
from ..console import get_console


@click.group()
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
    from ..projects import ProjectManager

    console = get_console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    project_manager = ProjectManager(auth_manager)

    console.print("📋 Fetching projects...", style="blue")

    try:
        result = asyncio.run(project_manager.list_projects(fields=fields, top=top, show_archived=show_archived))

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
    leader: str,
    description: Optional[str],
    template: Optional[str],
) -> None:
    """Create a new project."""
    from ..projects import ProjectManager

    console = get_console()
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
            console.print(f"Short Name: {project.get('shortName', 'N/A')}", style="blue")
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
    from ..projects import ProjectManager

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
    from ..projects import ProjectManager

    console = get_console()
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
            console.print("Project has been archived and is no longer active.", style="yellow")
        else:
            console.print(f"❌ {result['message']}", style="red")
            raise click.ClickException("Failed to archive project")

    except Exception as e:
        console.print(f"❌ Error archiving project: {e}", style="red")
        raise click.ClickException("Failed to archive project") from e
