"""User management for YouTrack CLI."""

from typing import Any, Optional

from rich.table import Table
from rich.text import Text

from .auth import AuthManager
from .client import get_client_manager
from .console import get_console
from .pagination import create_paginated_display

__all__ = ["UserManager"]


class UserManager:
    """Manages YouTrack user operations."""

    def __init__(self, auth_manager: AuthManager):
        """Initialize the user manager.

        Args:
            auth_manager: AuthManager instance for authentication
        """
        self.auth_manager = auth_manager
        self.console = get_console()

    async def list_users(
        self,
        fields: Optional[str] = None,
        top: Optional[int] = None,
        query: Optional[str] = None,
    ) -> dict[str, Any]:
        """List all users.

        Args:
            fields: Comma-separated list of user fields to return
            top: Maximum number of users to return
            query: Search query to filter users

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
            fields = "id,login,fullName,email,banned,online,guest,ringId,avatarUrl,teams(name,description)"

        # Build query parameters
        params = {"fields": fields}
        if top:
            params["$top"] = str(top)
        if query:
            params["query"] = query

        headers = {
            "Authorization": f"Bearer {credentials.token}",
            "Accept": "application/json",
        }

        try:
            client_manager = get_client_manager()
            response = await client_manager.make_request(
                "GET",
                f"{credentials.base_url.rstrip('/')}/api/users",
                headers=headers,
                params=params,
                timeout=10.0,
            )

            users = response.json()
            return {"status": "success", "data": users, "count": len(users)}

        except Exception as e:
            # HTTPClientManager already handles specific HTTP errors
            return {"status": "error", "message": str(e)}

    async def create_user(
        self,
        login: str,
        full_name: str,
        email: str,
        password: Optional[str] = None,
        banned: bool = False,
        force_change_password: bool = False,
    ) -> dict[str, Any]:
        """Create a new user.

        Args:
            login: User login name
            full_name: User's full name
            email: User's email address
            password: User's password (optional, can be set later)
            banned: Whether the user is banned
            force_change_password: Whether to force password change on first login

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
        user_data = {
            "login": login,
            "fullName": full_name,
            "email": email,
            "banned": banned,
            "forceChangePassword": force_change_password,
        }

        if password:
            user_data["password"] = password

        headers = {
            "Authorization": f"Bearer {credentials.token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        try:
            client_manager = get_client_manager()
            response = await client_manager.make_request(
                "POST",
                f"{credentials.base_url.rstrip('/')}/api/users",
                headers=headers,
                json_data=user_data,
                params={"fields": "id,login,fullName,email,banned"},
                timeout=10.0,
            )

            created_user = response.json()
            return {
                "status": "success",
                "data": created_user,
                "message": f"User '{login}' created successfully",
            }

        except Exception as e:
            # HTTPClientManager already handles specific HTTP errors
            return {"status": "error", "message": str(e)}

    async def get_user(self, user_id: str, fields: Optional[str] = None) -> dict[str, Any]:
        """Get a specific user.

        Args:
            user_id: User ID or login
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
                "id,login,fullName,email,banned,online,guest,ringId,avatarUrl,"
                "teams(name,description),groups(name,description)"
            )

        headers = {
            "Authorization": f"Bearer {credentials.token}",
            "Accept": "application/json",
        }

        try:
            client_manager = get_client_manager()
            response = await client_manager.make_request(
                "GET",
                f"{credentials.base_url.rstrip('/')}/api/users/{user_id}",
                headers=headers,
                params={"fields": fields},
                timeout=10.0,
            )

            user = response.json()
            return {"status": "success", "data": user}

        except Exception as e:
            # HTTPClientManager already handles specific HTTP errors
            return {"status": "error", "message": str(e)}

    async def update_user(
        self,
        user_id: str,
        full_name: Optional[str] = None,
        email: Optional[str] = None,
        banned: Optional[bool] = None,
        password: Optional[str] = None,
        force_change_password: Optional[bool] = None,
    ) -> dict[str, Any]:
        """Update a user.

        Args:
            user_id: User ID or login
            full_name: New full name
            email: New email address
            banned: New banned status
            password: New password
            force_change_password: Force password change on next login

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
        if full_name is not None:
            update_data["fullName"] = full_name
        if email is not None:
            update_data["email"] = email
        if banned is not None:
            update_data["banned"] = banned
        if password is not None:
            update_data["password"] = password
        if force_change_password is not None:
            update_data["forceChangePassword"] = force_change_password

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
                f"{credentials.base_url.rstrip('/')}/api/users/{user_id}",
                headers=headers,
                json_data=update_data,
                params={"fields": "id,login,fullName,email,banned"},
                timeout=10.0,
            )

            updated_user = response.json()
            return {
                "status": "success",
                "data": updated_user,
                "message": f"User '{user_id}' updated successfully",
            }

        except Exception as e:
            # HTTPClientManager already handles specific HTTP errors
            return {"status": "error", "message": str(e)}

    async def manage_user_permissions(
        self,
        user_id: str,
        action: str,
        group_id: Optional[str] = None,
        role_id: Optional[str] = None,
        project_id: Optional[str] = None,
    ) -> dict[str, Any]:
        """Manage user permissions and group memberships.

        Args:
            user_id: User ID or login
            action: Action to perform
                (add_to_group, remove_from_group, add_role, remove_role)
            group_id: Group ID for group operations
            role_id: Role ID for role operations
            project_id: Project ID for project-specific roles

        Returns:
            Dictionary with operation result
        """
        credentials = self.auth_manager.load_credentials()
        if not credentials:
            return {
                "status": "error",
                "message": "Not authenticated. Run 'yt auth login' first.",
            }

        if action in ["add_to_group", "remove_from_group"] and not group_id:
            return {
                "status": "error",
                "message": "Group ID is required for group operations.",
            }

        if action in ["add_role", "remove_role"] and not role_id:
            return {
                "status": "error",
                "message": "Role ID is required for role operations.",
            }

        headers = {
            "Authorization": f"Bearer {credentials.token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        try:
            client_manager = get_client_manager()

            if action == "add_to_group":
                # Add user to group
                await client_manager.make_request(
                    "POST",
                    f"{credentials.base_url.rstrip('/')}/api/admin/groups/{group_id}/users",
                    headers=headers,
                    json_data={"id": user_id},
                    timeout=10.0,
                )
            elif action == "remove_from_group":
                # Remove user from group
                await client_manager.make_request(
                    "DELETE",
                    f"{credentials.base_url.rstrip('/')}/api/admin/groups/{group_id}/users/{user_id}",
                    headers=headers,
                    timeout=10.0,
                )
            else:
                return {
                    "status": "error",
                    "message": f"Unsupported action: {action}",
                }

            return {
                "status": "success",
                "message": f"User '{user_id}' permissions updated successfully",
            }

        except Exception as e:
            # HTTPClientManager already handles specific HTTP errors
            return {"status": "error", "message": str(e)}

    def display_users_table(self, users: list[dict[str, Any]]) -> None:
        """Display users in a formatted table.

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
        self, users: list[dict[str, Any]], page_size: int = 50, show_all: bool = False, start_page: int = 1
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

        def build_users_table(user_subset: list[dict[str, Any]]) -> Table:
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

    def display_user_details(self, user: dict[str, Any]) -> None:
        """Display detailed information about a user.

        Args:
            user: User dictionary
        """
        self.console.print("\n[bold blue]User Details[/bold blue]")
        self.console.print(f"[cyan]Login:[/cyan] {user.get('login', 'N/A')}")
        self.console.print(f"[cyan]Full Name:[/cyan] {user.get('fullName', 'N/A')}")
        self.console.print(f"[cyan]Email:[/cyan] {user.get('email', 'N/A')}")
        self.console.print(f"[cyan]ID:[/cyan] {user.get('id', 'N/A')}")

        # Status information
        if user.get("banned", False):
            status = "Banned"
            status_style = "red"
        elif user.get("online", False):
            status = "Online"
            status_style = "green"
        else:
            status = "Offline"
            status_style = "yellow"

        self.console.print(f"[cyan]Status:[/cyan] [{status_style}]{status}[/{status_style}]")

        # User type
        user_type = "Guest" if user.get("guest", False) else "User"
        self.console.print(f"[cyan]Type:[/cyan] {user_type}")

        # Teams
        teams = user.get("teams", [])
        if teams:
            self.console.print("\n[cyan]Teams:[/cyan]")
            for team in teams:
                team_name = team.get("name", "N/A")
                team_desc = team.get("description", "")
                if team_desc:
                    self.console.print(f"  • {team_name} - {team_desc}")
                else:
                    self.console.print(f"  • {team_name}")

        # Groups
        groups = user.get("groups", [])
        if groups:
            self.console.print("\n[cyan]Groups:[/cyan]")
            for group in groups:
                group_name = group.get("name", "N/A")
                group_desc = group.get("description", "")
                if group_desc:
                    self.console.print(f"  • {group_name} - {group_desc}")
                else:
                    self.console.print(f"  • {group_name}")
