"""Project management for YouTrack CLI."""

from typing import Any, Optional

import httpx
from rich.table import Table
from rich.text import Text

from .auth import AuthManager
from .client import get_client_manager
from .console import get_console
from .pagination import create_paginated_display
from .users import UserManager

__all__ = ["ProjectManager"]


class ProjectManager:
    """Manages YouTrack project operations."""

    def __init__(self, auth_manager: AuthManager):
        """Initialize the project manager.

        Args:
            auth_manager: AuthManager instance for authentication
        """
        self.auth_manager = auth_manager
        self.console = get_console()
        self.user_manager = UserManager(auth_manager)

    def _parse_json_response(self, response: httpx.Response) -> Any:
        """Safely parse JSON response, handling empty or non-JSON responses."""
        try:
            content_type = response.headers.get("content-type", "")
            if not response.text:
                raise ValueError("Empty response body")

            if "application/json" not in content_type:
                raise ValueError(f"Response is not JSON. Content-Type: {content_type}")

            return response.json()
        except Exception as e:
            # Try to provide more context about the error
            status_code = response.status_code
            preview = response.text[:200] if response.text else "empty"
            raise ValueError(
                f"Failed to parse JSON response (status {status_code}): {str(e)}. Response preview: {preview}"
            ) from e

    async def _resolve_user_id(self, username_or_id: str) -> tuple[str, Optional[str]]:
        """Resolve a username or ID to a YouTrack user ID.

        Args:
            username_or_id: Either a username (login) or user ID

        Returns:
            Tuple of (user_id, error_message). If successful, error_message is None.
        """
        # If it looks like a user ID (contains dash), return as-is
        if "-" in username_or_id:
            return username_or_id, None

        # Try to resolve as username
        try:
            result = await self.user_manager.get_user(username_or_id, fields="id,login")
            if result["status"] == "success":
                user_data = result["data"]
                user_id = user_data.get("id")
                if user_id:
                    return user_id, None
                else:
                    return username_or_id, f"User '{username_or_id}' found but missing ID"
            else:
                return username_or_id, f"User '{username_or_id}' not found"
        except Exception as e:
            return username_or_id, f"Error resolving username '{username_or_id}': {e}"

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

            projects = self._parse_json_response(response)

            # Ensure we have a valid list of projects
            if projects is None:
                return {"status": "error", "message": "No project data received from YouTrack API"}

            if not isinstance(projects, list):
                data_type = type(projects).__name__
                # Include more details about what we received for debugging
                preview = str(projects)[:200] if projects is not None else "None"
                return {
                    "status": "error",
                    "message": (
                        f"Unexpected data format from YouTrack API: expected list, got {data_type}. "
                        f"Response preview: {preview}"
                    ),
                }

            # Filter archived projects if requested
            if not show_archived:
                filtered_projects = []
                for p in projects:
                    if p is not None and not p.get("archived", False):
                        filtered_projects.append(p)
                projects = filtered_projects

            # Final null check before count
            if projects is None:
                projects = []

            return {"status": "success", "data": projects, "count": len(projects)}

        except ValueError as e:
            return {"status": "error", "message": f"Failed to parse response: {e}"}
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
            leader_id: ID or username of the project leader
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

        # Resolve leader username to user ID
        resolved_leader_id, error_msg = await self._resolve_user_id(leader_id)
        if error_msg:
            return {
                "status": "error",
                "message": f"Failed to resolve leader: {error_msg}",
            }

        # Prepare request body
        project_data = {
            "name": name,
            "shortName": short_name,
            "leader": {"id": resolved_leader_id},
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

            created_project = self._parse_json_response(response)
            if created_project is None:
                return {"status": "error", "message": "Failed to parse project creation response"}
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

            project = self._parse_json_response(response)
            if project is None:
                return {"status": "error", "message": "Failed to parse project response"}
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
            leader_id: New project leader ID or username
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
            # Resolve leader username to user ID
            resolved_leader_id, error_msg = await self._resolve_user_id(leader_id)
            if error_msg:
                return {
                    "status": "error",
                    "message": f"Failed to resolve leader: {error_msg}",
                }
            update_data["leader"] = {"id": resolved_leader_id}
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

            updated_project = self._parse_json_response(response)
            if updated_project is None:
                return {"status": "error", "message": "Failed to parse project update response"}
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
            # Skip None projects
            if project is None:
                continue

            short_name = project.get("shortName", "N/A")
            name = project.get("name", "N/A")

            # Format leader info
            leader = project.get("leader", {})
            if leader and isinstance(leader, dict):
                leader_name = leader.get("fullName") or leader.get("login", "N/A")
            else:
                leader_name = "N/A"

            # Format status
            status = "Archived" if project.get("archived", False) else "Active"
            status_style = "red" if project.get("archived", False) else "green"

            description = project.get("description", "") or ""
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

    def display_projects_table_paginated(
        self, projects: list[dict[str, Any]], page_size: int = 50, show_all: bool = False, start_page: int = 1
    ) -> None:
        """Display projects in a paginated table format.

        Args:
            projects: List of project dictionaries
            page_size: Number of projects per page (default: 50)
            show_all: If True, display all projects without pagination
            start_page: Page number to start displaying from
        """
        if not projects:
            self.console.print("No projects found.", style="yellow")
            return

        def build_projects_table(project_subset: list[dict[str, Any]]) -> Table:
            """Build a Rich table for the given subset of projects."""
            table = Table(title="YouTrack Projects")
            table.add_column("Short Name", style="cyan", no_wrap=True)
            table.add_column("Name", style="blue")
            table.add_column("Leader", style="green")
            table.add_column("Status", style="magenta")
            table.add_column("Description", style="dim")

            for project in project_subset:
                # Skip None projects
                if project is None:
                    continue

                short_name = project.get("shortName", "N/A")
                name = project.get("name", "N/A")

                # Format leader info
                leader = project.get("leader", {})
                if leader and isinstance(leader, dict):
                    leader_name = leader.get("fullName") or leader.get("login", "No leader")
                else:
                    leader_name = "No leader"

                # Format status with appropriate color
                archived = project.get("archived", False)
                status = "Archived" if archived else "Active"
                status_style = "dim" if archived else "green"

                # Truncate description if too long
                description = project.get("description", "No description")
                if len(description) > 50:
                    description = description[:47] + "..."

                table.add_row(
                    short_name,
                    name,
                    leader_name,
                    Text(status, style=status_style),
                    description,
                )

            return table

        # Use pagination display
        paginated_display = create_paginated_display(self.console, page_size)
        paginated_display.display_paginated_table(
            projects, build_projects_table, "Projects", show_all=show_all, start_page=start_page
        )

    def display_project_details(self, project: dict[str, Any]) -> None:
        """Display detailed information about a project.

        Args:
            project: Project dictionary
        """
        if project is None:
            self.console.print("[red]Error: No project data to display[/red]")
            return

        self.console.print("\n[bold blue]Project Details[/bold blue]")
        self.console.print(f"[cyan]Name:[/cyan] {project.get('name', 'N/A')}")
        self.console.print(f"[cyan]Short Name:[/cyan] {project.get('shortName', 'N/A')}")
        self.console.print(f"[cyan]ID:[/cyan] {project.get('id', 'N/A')}")

        # Leader information
        leader = project.get("leader", {})
        if leader and isinstance(leader, dict):
            leader_name = leader.get("fullName") or leader.get("login", "N/A")
            self.console.print(f"[cyan]Leader:[/cyan] {leader_name}")

        # Status
        status = "Archived" if project.get("archived", False) else "Active"
        status_style = "red" if project.get("archived", False) else "green"
        self.console.print(f"[cyan]Status:[/cyan] [{status_style}]{status}[/{status_style}]")

        # Description
        description = project.get("description", "") or ""
        if description:
            self.console.print(f"[cyan]Description:[/cyan] {description}")

        # Created by
        created_by = project.get("createdBy", {})
        if created_by and isinstance(created_by, dict):
            creator_name = created_by.get("fullName") or created_by.get("login", "N/A")
            self.console.print(f"[cyan]Created By:[/cyan] {creator_name}")

        # Team members
        team = project.get("team", {})
        if team and isinstance(team, dict) and team.get("users"):
            users = team.get("users", [])
            if isinstance(users, list):
                self.console.print("\n[cyan]Team Members:[/cyan]")
                for user in users:
                    if user and isinstance(user, dict):
                        user_name = user.get("fullName") or user.get("login", "N/A")
                        self.console.print(f"  • {user_name}")
