"""User manager for YouTrack CLI business logic."""

from typing import Any, Dict, List, Optional

from rich.table import Table
from rich.text import Text

from ..auth import AuthManager
from ..console import get_console
from ..pagination import create_paginated_display
from ..services.users import UserService

__all__ = ["UserManager"]


class UserManager:
    """Manages YouTrack user business logic and presentation.

    This manager orchestrates user operations using the UserService
    for API communication and adds business logic, validation, and
    presentation formatting.
    """

    def __init__(self, auth_manager: AuthManager):
        """Initialize the user manager.

        Args:
            auth_manager: AuthManager instance for authentication
        """
        self.auth_manager = auth_manager
        self.console = get_console()
        self.user_service = UserService(auth_manager)

    async def list_users(
        self,
        fields: Optional[str] = None,
        top: Optional[int] = None,
        query: Optional[str] = None,
        active_only: bool = False,
        page_size: int = 100,
        after_cursor: Optional[str] = None,
        before_cursor: Optional[str] = None,
        use_pagination: bool = False,
        max_results: Optional[int] = None,
    ) -> Dict[str, Any]:
        """List all users with enhanced filtering and pagination.

        Args:
            fields: Comma-separated list of user fields to return
            top: Maximum number of users to return (legacy, use page_size instead)
            query: Search query to filter users
            active_only: Show only active (non-banned) users
            page_size: Number of users per page
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
            result = await self.user_service.list_users(
                fields=fields,
                top=page_size,
                skip=0,
                query=query,
            )

            if result["status"] == "success":
                users = result["data"]

                # Apply active_only filter client-side
                if active_only and isinstance(users, list):
                    users = [user for user in users if not user.get("banned", False)]
                    result["data"] = users

                return {
                    "status": "success",
                    "data": users,
                    "count": len(users) if isinstance(users, list) else 0,
                    "pagination": {
                        "total_results": len(users) if isinstance(users, list) else 0,
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
            result = await self.user_service.list_users(
                fields=fields,
                top=top,
                skip=0,
                query=query,
            )

            # Apply active_only filter client-side
            if result["status"] == "success" and active_only:
                users = result["data"]
                if isinstance(users, list):
                    filtered_users = [user for user in users if not user.get("banned", False)]
                    result["data"] = filtered_users

            # Add count to result if successful
            if result["status"] == "success":
                result["count"] = len(result["data"]) if isinstance(result["data"], list) else 0

            return result

    async def get_user(self, user_id: str, fields: Optional[str] = None) -> Dict[str, Any]:
        """Get a specific user with enhanced error handling.

        Args:
            user_id: User ID or login
            fields: Comma-separated list of fields to return

        Returns:
            Dictionary with operation result
        """
        return await self.user_service.get_user(user_id, fields)

    async def create_user(
        self,
        login: str,
        full_name: str,
        email: str,
        password: Optional[str] = None,
        force_change_password: bool = False,
    ) -> Dict[str, Any]:
        """Create a new user with business validation.

        Args:
            login: User login name
            full_name: User's full name
            email: User's email address
            password: Initial password
            force_change_password: Force password change on first login

        Returns:
            Dictionary with operation result
        """
        # Validate input parameters
        if not login or not login.strip():
            return {"status": "error", "message": "Login cannot be empty"}

        if not full_name or not full_name.strip():
            return {"status": "error", "message": "Full name cannot be empty"}

        if not email or "@" not in email:
            return {"status": "error", "message": "Valid email address is required"}

        result = await self.user_service.create_user(
            login=login.strip(),
            full_name=full_name.strip(),
            email=email.strip(),
            password=password,
            force_change_password=force_change_password,
        )

        # Add success message enhancement
        if result["status"] == "success":
            result["message"] = f"User '{login}' created successfully"

        return result

    async def update_user(
        self,
        user_id: str,
        full_name: Optional[str] = None,
        email: Optional[str] = None,
        banned: Optional[bool] = None,
        password: Optional[str] = None,
        force_change_password: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Update an existing user with validation.

        Args:
            user_id: User ID to update
            full_name: New full name
            email: New email address
            banned: New banned status
            password: New password
            force_change_password: Force password change on next login

        Returns:
            Dictionary with operation result
        """
        # Validate email format if provided
        if email is not None and email and "@" not in email:
            return {"status": "error", "message": "Valid email address is required"}

        # Check if any updates are provided
        if all(param is None for param in [full_name, email, banned, password, force_change_password]):
            return {"status": "error", "message": "No updates provided."}

        result = await self.user_service.update_user(
            user_id=user_id,
            full_name=full_name.strip() if full_name else None,
            email=email.strip() if email else None,
            banned=banned,
            password=password,
            force_change_password=force_change_password,
        )

        # Add success message enhancement
        if result["status"] == "success":
            result["message"] = f"User '{user_id}' updated successfully"

        return result

    async def delete_user(self, user_id: str) -> Dict[str, Any]:
        """Delete a user with confirmation logic.

        Args:
            user_id: User ID to delete

        Returns:
            Dictionary with operation result
        """
        result = await self.user_service.delete_user(user_id)

        # Add success message enhancement
        if result["status"] == "success":
            result["message"] = f"User '{user_id}' deleted successfully"

        return result

    async def ban_user(self, user_id: str) -> Dict[str, Any]:
        """Ban a user.

        Args:
            user_id: User ID to ban

        Returns:
            Dictionary with operation result
        """
        result = await self.user_service.ban_user(user_id)

        # Add success message enhancement
        if result["status"] == "success":
            result["message"] = f"User '{user_id}' banned successfully"

        return result

    async def unban_user(self, user_id: str) -> Dict[str, Any]:
        """Unban a user.

        Args:
            user_id: User ID to unban

        Returns:
            Dictionary with operation result
        """
        result = await self.user_service.unban_user(user_id)

        # Add success message enhancement
        if result["status"] == "success":
            result["message"] = f"User '{user_id}' unbanned successfully"

        return result

    async def get_user_groups(self, user_id: str) -> Dict[str, Any]:
        """Get groups that a user belongs to.

        Args:
            user_id: User ID or login

        Returns:
            Dictionary with operation result
        """
        return await self.user_service.get_user_groups(user_id)

    async def add_user_to_group(self, user_id: str, group_id: str) -> Dict[str, Any]:
        """Add user to a group.

        Args:
            user_id: User ID or login
            group_id: Group ID to add user to

        Returns:
            Dictionary with operation result
        """
        result = await self.user_service.add_user_to_group(user_id, group_id)

        # Add success message enhancement
        if result["status"] == "success":
            result["message"] = f"User '{user_id}' added to group '{group_id}'"

        return result

    async def remove_user_from_group(self, user_id: str, group_id: str) -> Dict[str, Any]:
        """Remove user from a group.

        Args:
            user_id: User ID or login
            group_id: Group ID to remove user from

        Returns:
            Dictionary with operation result
        """
        result = await self.user_service.remove_user_from_group(user_id, group_id)

        # Add success message enhancement
        if result["status"] == "success":
            result["message"] = f"User '{user_id}' removed from group '{group_id}'"

        return result

    async def get_user_roles(self, user_id: str) -> Dict[str, Any]:
        """Get user's roles.

        Args:
            user_id: User ID or login

        Returns:
            Dictionary with operation result
        """
        return await self.user_service.get_user_roles(user_id)

    async def assign_user_role(self, user_id: str, role_id: str) -> Dict[str, Any]:
        """Assign a role to user.

        Args:
            user_id: User ID or login
            role_id: Role ID to assign

        Returns:
            Dictionary with operation result
        """
        result = await self.user_service.assign_user_role(user_id, role_id)

        # Add success message enhancement
        if result["status"] == "success":
            result["message"] = f"Role '{role_id}' assigned to user '{user_id}'"

        return result

    async def remove_user_role(self, user_id: str, role_id: str) -> Dict[str, Any]:
        """Remove a role from user.

        Args:
            user_id: User ID or login
            role_id: Role ID to remove

        Returns:
            Dictionary with operation result
        """
        result = await self.user_service.remove_user_role(user_id, role_id)

        # Add success message enhancement
        if result["status"] == "success":
            result["message"] = f"Role '{role_id}' removed from user '{user_id}'"

        return result

    async def get_user_teams(self, user_id: str) -> Dict[str, Any]:
        """Get user's teams.

        Args:
            user_id: User ID or login

        Returns:
            Dictionary with operation result
        """
        return await self.user_service.get_user_teams(user_id)

    async def add_user_to_team(self, user_id: str, team_id: str) -> Dict[str, Any]:
        """Add user to a team.

        Args:
            user_id: User ID or login
            team_id: Team ID to add user to

        Returns:
            Dictionary with operation result
        """
        result = await self.user_service.add_user_to_team(user_id, team_id)

        # Add success message enhancement
        if result["status"] == "success":
            result["message"] = f"User '{user_id}' added to team '{team_id}'"

        return result

    async def remove_user_from_team(self, user_id: str, team_id: str) -> Dict[str, Any]:
        """Remove user from a team.

        Args:
            user_id: User ID or login
            team_id: Team ID to remove user from

        Returns:
            Dictionary with operation result
        """
        result = await self.user_service.remove_user_from_team(user_id, team_id)

        # Add success message enhancement
        if result["status"] == "success":
            result["message"] = f"User '{user_id}' removed from team '{team_id}'"

        return result

    async def change_user_password(self, user_id: str, new_password: str, force_change: bool = False) -> Dict[str, Any]:
        """Change user password.

        Args:
            user_id: User ID or login
            new_password: New password
            force_change: Force password change on next login

        Returns:
            Dictionary with operation result
        """
        if not new_password or len(new_password) < 4:
            return {"status": "error", "message": "Password must be at least 4 characters long"}

        result = await self.user_service.change_user_password(user_id, new_password, force_change)

        # Add success message enhancement
        if result["status"] == "success":
            result["message"] = f"Password changed for user '{user_id}'"

        return result

    async def get_user_permissions(self, user_id: str, project_id: Optional[str] = None) -> Dict[str, Any]:
        """Get user permissions.

        Args:
            user_id: User ID or login
            project_id: Optional project ID to get project-specific permissions

        Returns:
            Dictionary with operation result
        """
        return await self.user_service.get_user_permissions(user_id, project_id)

    async def manage_user_permissions(
        self, user_id: str, action: str, group_id: Optional[str] = None, role_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Manage user permissions by adding/removing from groups or roles.

        Args:
            user_id: User ID or login
            action: Action to perform (add_to_group, remove_from_group, assign_role, remove_role)
            group_id: Group ID for group operations
            role_id: Role ID for role operations

        Returns:
            Dictionary with operation result
        """
        if action == "add_to_group" and group_id:
            return await self.add_user_to_group(user_id, group_id)
        elif action == "remove_from_group" and group_id:
            return await self.remove_user_from_group(user_id, group_id)
        elif action == "assign_role" and role_id:
            return await self.assign_user_role(user_id, role_id)
        elif action == "remove_role" and role_id:
            return await self.remove_user_role(user_id, role_id)
        else:
            return {"status": "error", "message": f"Invalid action '{action}' or missing required parameters"}

    def display_users_table(self, users: List[Dict[str, Any]]) -> None:
        """Display users in a simple table format.

        Args:
            users: List of user dictionaries
        """
        if not users:
            self.console.print("No users found.", style="yellow")
            return

        table = Table(title="YouTrack Users")
        table.add_column("Login", style="cyan", no_wrap=True)
        table.add_column("Full Name", style="blue")
        table.add_column("Email", style="green")
        table.add_column("Status", style="magenta")
        table.add_column("Type", style="dim")

        for user in users:
            login = user.get("login", "N/A")
            full_name = user.get("fullName", "N/A")
            email = user.get("email", "N/A")

            # Format status
            if user.get("banned", False):
                status = "Banned"
                status_style = "red"
            elif user.get("online", False):
                status = "Online"
                status_style = "green"
            else:
                status = "Offline"
                status_style = "yellow"

            # Format user type
            user_type = "Guest" if user.get("guest", False) else "User"

            table.add_row(
                login,
                full_name,
                email,
                Text(status, style=status_style),
                user_type,
            )

        self.console.print(table)

    def display_users_table_paginated(
        self, users: List[Dict[str, Any]], page_size: int = 50, show_all: bool = False, start_page: int = 1
    ) -> None:
        """Display users in a paginated table format.

        Args:
            users: List of user dictionaries
            page_size: Number of users per page (default: 50)
            show_all: If True, display all users without pagination
            start_page: Page number to start displaying from
        """
        if not users:
            self.console.print("No users found.", style="yellow")
            return

        def build_users_table(user_subset: List[Dict[str, Any]]) -> Table:
            """Build a Rich table for the given subset of users."""
            table = Table(title="YouTrack Users")
            table.add_column("Login", style="cyan", no_wrap=True)
            table.add_column("Full Name", style="blue")
            table.add_column("Email", style="green")
            table.add_column("Status", style="magenta")
            table.add_column("Type", style="dim")

            for user in user_subset:
                login = user.get("login", "N/A")
                full_name = user.get("fullName", "N/A")
                email = user.get("email", "N/A")

                # Format status
                if user.get("banned", False):
                    status = "Banned"
                    status_style = "red"
                elif user.get("online", False):
                    status = "Online"
                    status_style = "green"
                else:
                    status = "Offline"
                    status_style = "yellow"

                # Format user type
                user_type = "Guest" if user.get("guest", False) else "User"

                table.add_row(
                    login,
                    full_name,
                    email,
                    Text(status, style=status_style),
                    user_type,
                )

            return table

        # Use pagination display
        paginated_display = create_paginated_display(self.console, page_size)
        paginated_display.display_paginated_table(
            users, build_users_table, "Users", show_all=show_all, start_page=start_page
        )

    def display_user_details(self, user: Dict[str, Any]) -> None:
        """Display detailed user information with rich formatting.

        Args:
            user: User dictionary
        """
        if not user:
            self.console.print("[red]No user data to display[/red]")
            return

        # Create a detailed view
        self.console.print(f"\n[bold cyan]User: {user.get('login', 'Unknown')}[/bold cyan]")

        if user.get("fullName"):
            self.console.print(f"[dim]Full Name:[/dim] {user['fullName']}")

        if user.get("email"):
            self.console.print(f"[dim]Email:[/dim] {user['email']}")

        # Status information
        if user.get("banned", False):
            self.console.print("[dim]Status:[/dim] [red]Banned[/red]")
        elif user.get("online", False):
            self.console.print("[dim]Status:[/dim] [green]Online[/green]")
        else:
            self.console.print("[dim]Status:[/dim] [yellow]Offline[/yellow]")

        # User type
        user_type = "Guest" if user.get("guest", False) else "User"
        self.console.print(f"[dim]Type:[/dim] {user_type}")

        # Teams information if available
        if user.get("teams"):
            teams = user["teams"]
            if isinstance(teams, list) and teams:
                self.console.print(f"\n[bold]Teams ({len(teams)}):[/bold]")
                for team in teams:
                    team_name = team.get("name", "Unknown")
                    team_desc = team.get("description", "")
                    if team_desc:
                        self.console.print(f"  • {team_name} - {team_desc}")
                    else:
                        self.console.print(f"  • {team_name}")

        # Groups information if available
        if user.get("groups"):
            groups = user["groups"]
            if isinstance(groups, list) and groups:
                self.console.print(f"\n[bold]Groups ({len(groups)}):[/bold]")
                for group in groups:
                    group_name = group.get("name", "Unknown")
                    group_desc = group.get("description", "")
                    if group_desc:
                        self.console.print(f"  • {group_name} - {group_desc}")
                    else:
                        self.console.print(f"  • {group_name}")

        self.console.print()  # Add spacing

    def display_user_groups(self, groups: List[Dict[str, Any]], user_id: str) -> None:
        """Display user groups in a table format.

        Args:
            groups: List of group dictionaries
            user_id: User ID for display context
        """
        if not groups:
            self.console.print(f"[yellow]User '{user_id}' is not a member of any groups.[/yellow]")
            return

        table = Table(title=f"Groups for User: {user_id}")
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Description", style="green")
        table.add_column("Auto Join", style="yellow")

        for group in groups:
            name = group.get("name", "N/A")
            description = group.get("description", "")
            auto_join = "Yes" if group.get("autoJoin", False) else "No"

            table.add_row(name, description, auto_join)

        self.console.print(table)

    def display_user_roles(self, roles: List[Dict[str, Any]], user_id: str) -> None:
        """Display user roles in a table format.

        Args:
            roles: List of role dictionaries
            user_id: User ID for display context
        """
        if not roles:
            self.console.print(f"[yellow]User '{user_id}' has no assigned roles.[/yellow]")
            return

        table = Table(title=f"Roles for User: {user_id}")
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Description", style="green")

        for role in roles:
            name = role.get("name", "N/A")
            description = role.get("description", "")

            table.add_row(name, description)

        self.console.print(table)

    def display_user_teams(self, teams: List[Dict[str, Any]], user_id: str) -> None:
        """Display user teams in a table format.

        Args:
            teams: List of team dictionaries
            user_id: User ID for display context
        """
        if not teams:
            self.console.print(f"[yellow]User '{user_id}' is not a member of any teams.[/yellow]")
            return

        table = Table(title=f"Teams for User: {user_id}")
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Description", style="green")

        for team in teams:
            name = team.get("name", "N/A")
            description = team.get("description", "")

            table.add_row(name, description)

        self.console.print(table)
