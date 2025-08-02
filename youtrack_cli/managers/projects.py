"""Project manager for YouTrack CLI business logic."""

from typing import Any, Dict, List, Optional

from rich.table import Table

from ..auth import AuthManager
from ..console import get_console
from ..services.projects import ProjectService
from .users import UserManager

__all__ = ["ProjectManager"]


class ProjectManager:
    """Manages YouTrack project business logic and presentation.

    This manager orchestrates project operations using the ProjectService
    for API communication and adds business logic, validation, and
    presentation formatting.
    """

    def __init__(self, auth_manager: AuthManager):
        """Initialize the project manager.

        Args:
            auth_manager: AuthManager instance for authentication
        """
        self.auth_manager = auth_manager
        self.console = get_console()
        self.project_service = ProjectService(auth_manager)
        self.user_manager = UserManager(auth_manager)

    async def _resolve_user_id(self, username_or_id: str) -> tuple[str, Optional[str]]:
        """Resolve a username or ID to a YouTrack user ID.

        Args:
            username_or_id: Either a username (login) or user ID

        Returns:
            Tuple of (user_id, error_message). If successful, error_message is None.
        """
        # Better user ID detection: YouTrack user IDs typically follow patterns like:
        # "2-1", "guest", or other specific formats. If it contains only digits and dashes,
        # or is a known system user, treat as user ID. Otherwise, try username resolution.

        # Check if it looks like a user ID pattern (digits with dashes, or known system users)
        if (
            username_or_id.replace("-", "").isdigit()
            or username_or_id in ["guest", "root"]
            or (len(username_or_id) >= 3 and "-" in username_or_id and any(c.isdigit() for c in username_or_id))
        ):
            # Validate that this user ID actually exists
            try:
                result = await self.user_manager.get_user(username_or_id, fields="id,login")
                if result["status"] == "success":
                    user_data = result["data"]
                    user_id = user_data.get("id")
                    if user_id:
                        return user_id, None
                    return username_or_id, f"User ID '{username_or_id}' found but missing ID field"
                # If the presumed user ID doesn't exist, fall through to username resolution
            except Exception:
                # If validation fails, fall through to username resolution
                pass

        # Try to resolve as username
        try:
            result = await self.user_manager.get_user(username_or_id, fields="id,login")
            if result["status"] == "success":
                user_data = result["data"]
                user_id = user_data.get("id")
                if user_id:
                    return user_id, None
                return username_or_id, f"User '{username_or_id}' found but missing ID field"
            # If user not found, return error instead of original input
            return username_or_id, f"User '{username_or_id}' not found"
        except Exception as e:
            return username_or_id, f"Error resolving username '{username_or_id}': {e}"

    async def list_projects(
        self,
        fields: Optional[str] = None,
        top: Optional[int] = None,
        show_archived: bool = False,
        page_size: int = 100,
        after_cursor: Optional[str] = None,
        before_cursor: Optional[str] = None,
        use_pagination: bool = False,
        max_results: Optional[int] = None,
    ) -> Dict[str, Any]:
        """List all projects with enhanced pagination and filtering.

        Args:
            fields: Comma-separated list of project fields to return
            top: Maximum number of projects to return (legacy, use page_size instead)
            show_archived: Whether to include archived projects
            page_size: Number of projects per page
            after_cursor: Start pagination after this cursor
            before_cursor: Start pagination before this cursor
            use_pagination: Enable pagination for large result sets
            max_results: Maximum total number of results to fetch

        Returns:
            Dictionary with operation result including pagination metadata
        """
        # Handle legacy top parameter
        if top is not None:
            page_size = top
            use_pagination = False

        if use_pagination:
            # Enhanced pagination logic would go here
            # For now, use simple service call
            result = await self.project_service.list_projects(
                fields=fields,
                top=page_size,
                skip=0,
                show_archived=show_archived,
            )

            if result["status"] == "success":
                projects = result["data"]
                return {
                    "status": "success",
                    "data": projects,
                    "count": len(projects) if isinstance(projects, list) else 0,
                    "pagination": {
                        "total_results": len(projects) if isinstance(projects, list) else 0,
                        "has_after": False,
                        "has_before": False,
                        "after_cursor": None,
                        "before_cursor": None,
                        "pagination_type": "offset",
                    },
                }
            return result
        else:
            # Legacy single request approach
            result = await self.project_service.list_projects(
                fields=fields,
                top=top,
                skip=0,
                show_archived=show_archived,
            )

            # Ensure count field is always present
            if result["status"] == "success" and isinstance(result["data"], list):
                result["count"] = len(result["data"])

            return result

    async def get_project(self, project_id: str, fields: Optional[str] = None) -> Dict[str, Any]:
        """Get a specific project with enhanced error handling.

        Args:
            project_id: Project ID or short name
            fields: Comma-separated list of fields to return

        Returns:
            Dictionary with operation result
        """
        return await self.project_service.get_project(project_id, fields)

    async def create_project(
        self,
        short_name: str,
        name: str,
        description: Optional[str] = None,
        leader_login: Optional[str] = None,
        template: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new project with business validation.

        Args:
            short_name: Project short name (ID)
            name: Project full name
            description: Project description
            leader_login: Project leader login

        Returns:
            Dictionary with operation result
        """
        # Validate project short name format
        if not short_name or not short_name.replace("-", "").replace("_", "").isalnum():
            return {
                "status": "error",
                "message": "Project short name must contain only alphanumeric characters, hyphens, and underscores",
            }

        # Resolve leader if provided
        resolved_leader = None
        if leader_login:
            resolved_leader, error_msg = await self._resolve_user_id(leader_login)
            if error_msg:
                return {
                    "status": "error",
                    "message": f"Failed to resolve project leader: {error_msg}",
                }

        return await self.project_service.create_project(
            short_name=short_name,
            name=name,
            description=description,
            leader_login=resolved_leader,
        )

    async def update_project(
        self,
        project_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        leader_login: Optional[str] = None,
        archived: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Update a project configuration with user resolution.

        Args:
            project_id: Project ID or short name
            name: New project name
            description: New project description
            leader_id: New project leader ID or username
            archived: Archive status

        Returns:
            Dictionary with operation result
        """
        # Resolve leader username to user ID if provided
        resolved_leader = None
        if leader_login is not None:
            resolved_leader, error_msg = await self._resolve_user_id(leader_login)
            if error_msg:
                return {
                    "status": "error",
                    "message": f"Failed to resolve leader: {error_msg}",
                }

        # Check if any updates are provided
        if all(param is None for param in [name, description, leader_login, archived]):
            return {"status": "error", "message": "No updates provided."}

        result = await self.project_service.update_project(
            project_id=project_id,
            name=name,
            description=description,
            leader_login=resolved_leader,
            archived=archived,
        )

        # Add success message enhancement
        if result["status"] == "success":
            result["message"] = f"Project '{project_id}' updated successfully"

        return result

    async def delete_project(self, project_id: str) -> Dict[str, Any]:
        """Delete a project with confirmation logic.

        Args:
            project_id: Project ID to delete

        Returns:
            Dictionary with operation result
        """
        return await self.project_service.delete_project(project_id)

    async def archive_project(self, project_id: str) -> Dict[str, Any]:
        """Archive a project.

        Args:
            project_id: Project ID to archive

        Returns:
            Dictionary with operation result
        """
        result = await self.project_service.archive_project(project_id)

        # Add success message enhancement
        if result["status"] == "success":
            result["message"] = f"Project '{project_id}' archived successfully"

        return result

    async def unarchive_project(self, project_id: str) -> Dict[str, Any]:
        """Unarchive a project.

        Args:
            project_id: Project ID to unarchive

        Returns:
            Dictionary with operation result
        """
        result = await self.project_service.unarchive_project(project_id)

        # Add success message enhancement
        if result["status"] == "success":
            result["message"] = f"Project '{project_id}' unarchived successfully"

        return result

    async def get_project_team(self, project_id: str, fields: Optional[str] = None) -> Dict[str, Any]:
        """Get project team members.

        Args:
            project_id: Project ID
            fields: Comma-separated list of user fields to return

        Returns:
            Dictionary with operation result
        """
        return await self.project_service.get_project_team(project_id, fields)

    async def add_team_member(self, project_id: str, user_login: str) -> Dict[str, Any]:
        """Add a user to project team with validation.

        Args:
            project_id: Project ID
            user_login: User login to add

        Returns:
            Dictionary with operation result
        """
        # Validate user exists
        user_result = await self.user_manager.get_user(user_login, fields="id,login")
        if user_result["status"] != "success":
            return {"status": "error", "message": f"User '{user_login}' not found"}

        result = await self.project_service.add_team_member(project_id, user_login)

        # Add success message enhancement
        if result["status"] == "success":
            result["message"] = f"User '{user_login}' added to project '{project_id}' team"

        return result

    async def remove_team_member(self, project_id: str, user_login: str) -> Dict[str, Any]:
        """Remove a user from project team.

        Args:
            project_id: Project ID
            user_login: User login to remove

        Returns:
            Dictionary with operation result
        """
        result = await self.project_service.remove_team_member(project_id, user_login)

        # Add success message enhancement
        if result["status"] == "success":
            result["message"] = f"User '{user_login}' removed from project '{project_id}' team"

        return result

    async def get_project_custom_fields(self, project_id: str, fields: Optional[str] = None) -> Dict[str, Any]:
        """Get project custom fields.

        Args:
            project_id: Project ID
            fields: Comma-separated list of field properties to return

        Returns:
            Dictionary with operation result
        """
        return await self.project_service.get_project_custom_fields(project_id, fields)

    async def list_custom_fields(
        self, project_id: str, fields: Optional[str] = None, top: Optional[int] = None
    ) -> Dict[str, Any]:
        """List custom fields for a project.

        Args:
            project_id: Project ID
            fields: Comma-separated list of field properties to return
            top: Maximum number of fields to return

        Returns:
            Dictionary with operation result including count
        """
        result = await self.project_service.get_project_custom_fields(project_id, fields)

        # Add count information for display
        if result["status"] == "success" and isinstance(result["data"], list):
            result["count"] = len(result["data"])
            # Apply top limit if specified
            if top is not None and top > 0:
                result["data"] = result["data"][:top]
                result["count"] = min(result["count"], top)

        return result

    async def attach_custom_field(
        self,
        project_id: str,
        field_id: str,
        field_type: Optional[str] = None,
        can_be_empty: Optional[bool] = None,
        empty_field_text: Optional[str] = None,
        is_public: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Attach a custom field to a project.

        Args:
            project_id: Project ID
            field_id: Custom field ID
            field_type: Type of custom field
            can_be_empty: Whether field can be empty
            empty_field_text: Text to display when field is empty
            is_public: Whether field should be public

        Returns:
            Dictionary with operation result
        """
        result = await self.project_service.attach_custom_field(project_id, field_id, is_public)

        # Add success message enhancement
        if result["status"] == "success":
            result["message"] = f"Custom field '{field_id}' attached to project '{project_id}'"

        return result

    async def detach_custom_field(self, project_id: str, field_id: str) -> Dict[str, Any]:
        """Detach a custom field from a project.

        Args:
            project_id: Project ID
            field_id: Custom field ID to detach

        Returns:
            Dictionary with operation result
        """
        result = await self.project_service.detach_custom_field(project_id, field_id)

        # Add success message enhancement
        if result["status"] == "success":
            result["message"] = f"Custom field '{field_id}' detached from project '{project_id}'"

        return result

    async def update_custom_field(
        self,
        project_id: str,
        field_id: str,
        can_be_empty: Optional[bool] = None,
        empty_field_text: Optional[str] = None,
        is_public: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Update custom field settings in a project.

        Args:
            project_id: Project ID
            field_id: Custom field ID to update
            can_be_empty: Whether field can be empty
            empty_field_text: Text to display when field is empty
            is_public: Whether field should be public

        Returns:
            Dictionary with operation result
        """
        # This would need to be implemented in the service layer
        # For now, return a placeholder
        return {"status": "error", "message": "Custom field update not yet implemented in service layer"}

    def display_custom_fields_table(self, custom_fields: List[Dict[str, Any]]) -> None:
        """Display custom fields in a table format.

        Args:
            custom_fields: List of custom field dictionaries
        """
        if not custom_fields:
            self.console.print("[yellow]No custom fields found.[/yellow]")
            return

        from rich.table import Table

        table = Table(title="Project Custom Fields")
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Type", style="blue")
        table.add_column("Required", style="yellow")
        table.add_column("Public", style="green")

        for field in custom_fields:
            field_data = field.get("field", {})
            name = field_data.get("name", "N/A")
            field_type = field.get("$type", "N/A")

            # Simplify field type display
            if "ProjectCustomField" in field_type:
                field_type = field_type.replace("ProjectCustomField", "")

            required = "No" if field.get("canBeEmpty", True) else "Yes"
            public = "Yes" if field.get("isPublic", True) else "No"

            table.add_row(name, field_type, required, public)

        self.console.print(table)

    def display_project_list(
        self,
        projects: List[Dict[str, Any]],
        format_output: str = "table",
        show_archived: bool = False,
    ) -> None:
        """Display a list of projects with rich formatting.

        Args:
            projects: List of project dictionaries
            format_output: Output format (table, json, csv)
            show_archived: Whether archived projects are included
        """
        if not projects:
            self.console.print("[yellow]No projects found.[/yellow]")
            return

        if format_output == "table":
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Short Name", style="cyan", no_wrap=True)
            table.add_column("Name", style="green")
            table.add_column("Leader", style="blue")
            table.add_column("Status", style="yellow")

            for project in projects:
                # Extract leader info
                leader_name = "None"
                if project.get("leader") and isinstance(project["leader"], dict):
                    leader_name = project["leader"].get("fullName") or project["leader"].get("login") or "Unknown"

                # Determine status
                status = "Archived" if project.get("archived", False) else "Active"
                status_style = "red" if project.get("archived", False) else "green"

                table.add_row(
                    project.get("shortName", ""),
                    project.get("name", ""),
                    leader_name,
                    f"[{status_style}]{status}[/{status_style}]",
                )

            self.console.print(table)
        else:
            # For other formats, just print the data
            self.console.print(projects)

    def display_project_details(self, project: Dict[str, Any]) -> None:
        """Display detailed project information with rich formatting.

        Args:
            project: Project dictionary
        """
        if not project:
            self.console.print("[red]No project data to display[/red]")
            return

        # Create a detailed view
        self.console.print(f"\n[bold cyan]Project: {project.get('name', 'Unknown')}[/bold cyan]")
        self.console.print(f"[dim]Short Name:[/dim] {project.get('shortName', 'N/A')}")

        if project.get("description"):
            self.console.print(f"[dim]Description:[/dim] {project['description']}")

        # Leader information
        if project.get("leader"):
            leader = project["leader"]
            leader_name = leader.get("fullName") or leader.get("login") or "Unknown"
            self.console.print(f"[dim]Leader:[/dim] {leader_name}")

        # Status
        status = "Archived" if project.get("archived", False) else "Active"
        status_color = "red" if project.get("archived", False) else "green"
        self.console.print(f"[dim]Status:[/dim] [{status_color}]{status}[/{status_color}]")

        # Team information if available
        if project.get("team") and isinstance(project["team"], dict):
            team_users = project["team"].get("users", [])
            if team_users:
                self.console.print(f"\n[bold]Team Members ({len(team_users)}):[/bold]")
                for user in team_users:
                    user_name = user.get("fullName") or user.get("login") or "Unknown"
                    self.console.print(f"  • {user_name}")

        self.console.print()  # Add spacing
