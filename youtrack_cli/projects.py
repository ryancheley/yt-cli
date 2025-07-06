"""Project management for YouTrack CLI."""

from typing import Any, Optional

import httpx
from rich.console import Console
from rich.table import Table
from rich.text import Text

from .auth import AuthManager
from .client import get_client_manager

__all__ = ["ProjectManager"]


class ProjectManager:
    """Manages YouTrack project operations."""

    def __init__(self, auth_manager: AuthManager):
        """Initialize the project manager.

        Args:
            auth_manager: AuthManager instance for authentication
        """
        self.auth_manager = auth_manager
        self.console = Console()

    async def list_projects(
        self,
        fields: Optional[str] = None,
        top: Optional[int] = None,
        show_archived: bool = False,
    ) -> dict[str, Any]:
        """List all projects.

        Args:
            fields: Comma-separated list of project fields to return
            top: Maximum number of projects to return
            show_archived: Whether to include archived projects

        Returns:
            Dictionary with operation result
        """
        credentials = self.auth_manager.load_credentials()
        if not credentials:
            return {
                "status": "error",
                "message": "Not authenticated. Run 'yt auth login' first.",
            }

        # Default fields to return
        if not fields:
            fields = "id,name,shortName,description,leader(login,fullName),archived,createdBy(login,fullName)"

        # Build query parameters
        params = {"fields": fields}
        if top:
            params["$top"] = str(top)

        headers = {
            "Authorization": f"Bearer {credentials.token}",
            "Accept": "application/json",
        }

        try:
            client_manager = get_client_manager()
            response = await client_manager.make_request(
                "GET",
                f"{credentials.base_url.rstrip('/')}/api/admin/projects",
                headers=headers,
                params=params,
                timeout=10.0,
            )

            projects = response.json()

            # Filter archived projects if requested
            if not show_archived:
                projects = [p for p in projects if not p.get("archived", False)]

            return {"status": "success", "data": projects, "count": len(projects)}

        except httpx.HTTPError as e:
            return {"status": "error", "message": f"HTTP error: {e}"}
        except Exception as e:
            return {"status": "error", "message": f"Unexpected error: {e}"}

    async def create_project(
        self,
        name: str,
        short_name: str,
        leader_id: str,
        description: Optional[str] = None,
        template: Optional[str] = None,
    ) -> dict[str, Any]:
        """Create a new project.

        Args:
            name: Project name
            short_name: Project short name/key
            leader_id: ID of the project leader
            description: Project description
            template: Project template (scrum, kanban, etc.)

        Returns:
            Dictionary with operation result
        """
        credentials = self.auth_manager.load_credentials()
        if not credentials:
            return {
                "status": "error",
                "message": "Not authenticated. Run 'yt auth login' first.",
            }

        # Prepare request body
        project_data = {
            "name": name,
            "shortName": short_name,
            "leader": {"id": leader_id},
        }

        if description:
            project_data["description"] = description
        if template:
            project_data["template"] = template

        headers = {
            "Authorization": f"Bearer {credentials.token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        try:
            client_manager = get_client_manager()
            response = await client_manager.make_request(
                "POST",
                f"{credentials.base_url.rstrip('/')}/api/admin/projects",
                headers=headers,
                json_data=project_data,
                params={"fields": "id,name,shortName,leader(login,fullName)"},
                timeout=10.0,
            )

            created_project = response.json()
            return {
                "status": "success",
                "data": created_project,
                "message": f"Project '{name}' created successfully",
            }

        except httpx.HTTPError as e:
            if hasattr(e, "response") and e.response is not None:
                if e.response.status_code == 400:
                    return {
                        "status": "error",
                        "message": ("Invalid project data. Check name and short name."),
                    }
                elif e.response.status_code == 403:
                    return {
                        "status": "error",
                        "message": "Insufficient permissions to create projects.",
                    }
            return {"status": "error", "message": f"HTTP error: {e}"}
        except Exception as e:
            return {"status": "error", "message": f"Unexpected error: {e}"}

    async def get_project(self, project_id: str, fields: Optional[str] = None) -> dict[str, Any]:
        """Get a specific project.

        Args:
            project_id: Project ID or short name
            fields: Comma-separated list of fields to return

        Returns:
            Dictionary with operation result
        """
        credentials = self.auth_manager.load_credentials()
        if not credentials:
            return {
                "status": "error",
                "message": "Not authenticated. Run 'yt auth login' first.",
            }

        if not fields:
            fields = (
                "id,name,shortName,description,leader(login,fullName),"
                "archived,createdBy(login,fullName),team(users(login,fullName))"
            )

        headers = {
            "Authorization": f"Bearer {credentials.token}",
            "Accept": "application/json",
        }

        try:
            client_manager = get_client_manager()
            response = await client_manager.make_request(
                "GET",
                f"{credentials.base_url.rstrip('/')}/api/admin/projects/{project_id}",
                headers=headers,
                params={"fields": fields},
                timeout=10.0,
            )

            project = response.json()
            return {"status": "success", "data": project}

        except httpx.HTTPError as e:
            if hasattr(e, "response") and e.response is not None:
                if e.response.status_code == 404:
                    return {
                        "status": "error",
                        "message": f"Project '{project_id}' not found.",
                    }
                elif e.response.status_code == 403:
                    return {
                        "status": "error",
                        "message": "Insufficient permissions to view project.",
                    }
            return {"status": "error", "message": f"HTTP error: {e}"}
        except Exception as e:
            return {"status": "error", "message": f"Unexpected error: {e}"}

    async def update_project(
        self,
        project_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        leader_id: Optional[str] = None,
        archived: Optional[bool] = None,
    ) -> dict[str, Any]:
        """Update a project configuration.

        Args:
            project_id: Project ID or short name
            name: New project name
            description: New project description
            leader_id: New project leader ID
            archived: Archive status

        Returns:
            Dictionary with operation result
        """
        credentials = self.auth_manager.load_credentials()
        if not credentials:
            return {
                "status": "error",
                "message": "Not authenticated. Run 'yt auth login' first.",
            }

        # Build update data
        update_data: dict[str, Any] = {}
        if name is not None:
            update_data["name"] = name
        if description is not None:
            update_data["description"] = description
        if leader_id is not None:
            update_data["leader"] = {"id": leader_id}
        if archived is not None:
            update_data["archived"] = archived

        if not update_data:
            return {"status": "error", "message": "No updates provided."}

        headers = {
            "Authorization": f"Bearer {credentials.token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        try:
            client_manager = get_client_manager()
            response = await client_manager.make_request(
                "POST",
                f"{credentials.base_url.rstrip('/')}/api/admin/projects/{project_id}",
                headers=headers,
                json_data=update_data,
                params={"fields": "id,name,shortName,leader(login,fullName),archived"},
                timeout=10.0,
            )

            updated_project = response.json()
            return {
                "status": "success",
                "data": updated_project,
                "message": f"Project '{project_id}' updated successfully",
            }

        except httpx.HTTPError as e:
            if hasattr(e, "response") and e.response is not None:
                if e.response.status_code == 404:
                    return {
                        "status": "error",
                        "message": f"Project '{project_id}' not found.",
                    }
                elif e.response.status_code == 403:
                    return {
                        "status": "error",
                        "message": "Insufficient permissions to update project.",
                    }
            return {"status": "error", "message": f"HTTP error: {e}"}
        except Exception as e:
            return {"status": "error", "message": f"Unexpected error: {e}"}

    async def archive_project(self, project_id: str) -> dict[str, Any]:
        """Archive a project.

        Args:
            project_id: Project ID or short name

        Returns:
            Dictionary with operation result
        """
        return await self.update_project(project_id, archived=True)

    def display_projects_table(self, projects: list[dict[str, Any]]) -> None:
        """Display projects in a formatted table.

        Args:
            projects: List of project dictionaries
        """
        if not projects:
            self.console.print("No projects found.", style="yellow")
            return

        table = Table(title="YouTrack Projects")
        table.add_column("Short Name", style="cyan", no_wrap=True)
        table.add_column("Name", style="blue")
        table.add_column("Leader", style="green")
        table.add_column("Status", style="magenta")
        table.add_column("Description", style="dim")

        for project in projects:
            short_name = project.get("shortName", "N/A")
            name = project.get("name", "N/A")

            # Format leader info
            leader = project.get("leader", {})
            if leader:
                leader_name = leader.get("fullName") or leader.get("login", "N/A")
            else:
                leader_name = "N/A"

            # Format status
            status = "Archived" if project.get("archived", False) else "Active"
            status_style = "red" if project.get("archived", False) else "green"

            description = project.get("description", "")
            if len(description) > 50:
                description = description[:47] + "..."

            table.add_row(
                short_name,
                name,
                leader_name,
                Text(status, style=status_style),
                description,
            )

        self.console.print(table)

    def display_project_details(self, project: dict[str, Any]) -> None:
        """Display detailed information about a project.

        Args:
            project: Project dictionary
        """
        self.console.print("\n[bold blue]Project Details[/bold blue]")
        self.console.print(f"[cyan]Name:[/cyan] {project.get('name', 'N/A')}")
        self.console.print(f"[cyan]Short Name:[/cyan] {project.get('shortName', 'N/A')}")
        self.console.print(f"[cyan]ID:[/cyan] {project.get('id', 'N/A')}")

        # Leader information
        leader = project.get("leader", {})
        if leader:
            leader_name = leader.get("fullName") or leader.get("login", "N/A")
            self.console.print(f"[cyan]Leader:[/cyan] {leader_name}")

        # Status
        status = "Archived" if project.get("archived", False) else "Active"
        status_style = "red" if project.get("archived", False) else "green"
        self.console.print(f"[cyan]Status:[/cyan] [{status_style}]{status}[/{status_style}]")

        # Description
        description = project.get("description", "")
        if description:
            self.console.print(f"[cyan]Description:[/cyan] {description}")

        # Created by
        created_by = project.get("createdBy", {})
        if created_by:
            creator_name = created_by.get("fullName") or created_by.get("login", "N/A")
            self.console.print(f"[cyan]Created By:[/cyan] {creator_name}")

        # Team members
        team = project.get("team", {})
        if team and team.get("users"):
            self.console.print("\n[cyan]Team Members:[/cyan]")
            for user in team["users"]:
                user_name = user.get("fullName") or user.get("login", "N/A")
                self.console.print(f"  • {user_name}")
