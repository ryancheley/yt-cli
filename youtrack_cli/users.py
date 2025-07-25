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
        active_only: bool = False,
        page_size: int = 100,
        after_cursor: Optional[str] = None,
        before_cursor: Optional[str] = None,
        use_pagination: bool = False,
        max_results: Optional[int] = None,
    ) -> dict[str, Any]:
        """List all users.

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
        from .utils import paginate_results  # Import here to avoid circular imports

        credentials = self.auth_manager.load_credentials()
        if not credentials:
            return {
                "status": "error",
                "message": "Not authenticated. Run 'yt auth login' first.",
            }

        # Handle legacy top parameter
        if top is not None:
            page_size = top
            use_pagination = False

        # Default fields to return
        if not fields:
            fields = "id,login,fullName,email,banned,online,guest,ringId,avatarUrl,teams(name,description)"

        # Build query parameters
        params = {"fields": fields}

        # Build the query filter - only add user-provided query to API call
        # We'll handle active_only filtering client-side since YouTrack users API
        # may not support banned field queries
        if query:
            params["query"] = query

        headers = {
            "Authorization": f"Bearer {credentials.token}",
            "Accept": "application/json",
        }

        try:
            if use_pagination:
                # Use enhanced pagination with offset support
                result = await paginate_results(
                    endpoint=f"{credentials.base_url.rstrip('/')}/api/users",
                    headers=headers,
                    params=params,
                    page_size=page_size,
                    max_results=max_results,
                    after_cursor=after_cursor,
                    before_cursor=before_cursor,
                    use_cursor_pagination=False,  # Users use offset pagination
                )
                users = result["results"]

                # Apply client-side filtering for active_only
                if active_only:
                    users = [user for user in users if not user.get("banned", False)]

                return {
                    "status": "success",
                    "data": users,
                    "count": len(users),
                    "pagination": {
                        "total_results": result["total_results"],
                        "has_after": result["has_after"],
                        "has_before": result["has_before"],
                        "after_cursor": result["after_cursor"],
                        "before_cursor": result["before_cursor"],
                        "pagination_type": result["pagination_type"],
                    },
                }
            else:
                # Legacy single request approach
                if top:
                    params["$top"] = str(top)

                client_manager = get_client_manager()
                response = await client_manager.make_request(
                    "GET",
                    f"{credentials.base_url.rstrip('/')}/api/users",
                    headers=headers,
                    params=params,
                )

                users = response.json()

                # Apply client-side filtering for active_only
                if active_only:
                    users = [user for user in users if not user.get("banned", False)]

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

        # Prepare request body for Hub API
        user_data = {
            "login": login,
            "name": full_name,
            "email": email,
            "banned": banned,
        }

        # Add profile information
        profile_data = {}
        if force_change_password:
            profile_data["forceChangePassword"] = force_change_password

        if profile_data:
            user_data["profile"] = profile_data

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
                f"{credentials.base_url.rstrip('/')}/hub/api/rest/users",
                headers=headers,
                json_data=user_data,
                params={"fields": "id,login,name,email,banned"},
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
            base_url = credentials.base_url.rstrip("/")

            if action == "add_to_group":
                # Get user details first to obtain Hub ID and login for the request
                user_details_result = await self.get_user(user_id, fields="id,login,ringId")
                if user_details_result["status"] != "success":
                    return {
                        "status": "error",
                        "message": f"Failed to get user details: {user_details_result['message']}",
                    }

                user_data = user_details_result["data"]
                hub_user_id = user_data.get("ringId") or user_data.get("id")
                user_login = user_data.get("login")

                if not hub_user_id or not user_login:
                    return {
                        "status": "error",
                        "message": f"Could not get Hub ID or login for user '{user_id}'",
                    }

                # Add user to group using Hub API
                request_data = {
                    "type": "user",
                    "id": hub_user_id,
                    "login": user_login,
                }

                await client_manager.make_request(
                    "POST",
                    f"{base_url}/hub/api/rest/usergroups/{group_id}/users",
                    headers=headers,
                    json_data=request_data,
                    timeout=10.0,
                )
            elif action == "remove_from_group":
                # Get user details to obtain Hub ID for removal
                user_details_result = await self.get_user(user_id, fields="id,login,ringId")
                if user_details_result["status"] != "success":
                    return {
                        "status": "error",
                        "message": f"Failed to get user details: {user_details_result['message']}",
                    }

                user_data = user_details_result["data"]
                hub_user_id = user_data.get("ringId") or user_data.get("id")

                if not hub_user_id:
                    return {
                        "status": "error",
                        "message": f"Could not get Hub ID for user '{user_id}'",
                    }

                # Remove user from group using Hub API
                await client_manager.make_request(
                    "DELETE",
                    f"{base_url}/hub/api/rest/usergroups/{group_id}/users/{hub_user_id}",
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

    async def get_user_groups(self, user_id: str) -> dict[str, Any]:
        """Get groups that a user belongs to.

        Args:
            user_id: User ID or login

        Returns:
            Dictionary with operation result
        """
        credentials = self.auth_manager.load_credentials()
        if not credentials:
            return {
                "status": "error",
                "message": "Not authenticated. Run 'yt auth login' first.",
            }

        headers = {
            "Authorization": f"Bearer {credentials.token}",
            "Accept": "application/json",
        }

        try:
            client_manager = get_client_manager()
            base_url = credentials.base_url.rstrip("/")

            # Try different field configurations to find one that works
            # Note: Groups don't have permissions in YouTrack, they are organizational units
            field_configs = [
                "groups(id,name,description)",
                "groups(id,name)",
                "groups",
            ]

            for fields in field_configs:
                try:
                    response = await client_manager.make_request(
                        "GET",
                        f"{base_url}/api/users/{user_id}",
                        headers=headers,
                        params={"fields": fields},
                        timeout=10.0,
                    )

                    user = response.json()
                    groups = user.get("groups", [])

                    # If we found groups, return them (groups don't have permissions in YouTrack)
                    if groups:
                        # Add empty permissions array to match expected format
                        for group in groups:
                            if "permissions" not in group:
                                group["permissions"] = []
                        return {"status": "success", "data": groups, "user_id": user_id}

                except Exception:
                    continue

            # If user endpoint doesn't work, try getting all groups and filter
            try:
                # Try to get all groups - Note: Groups in YouTrack typically don't have permissions
                # directly attached. They are organizational units, while permissions come from roles.
                group_field_configs = [
                    "id,name,description,users(id,login)",
                ]

                for group_fields in group_field_configs:
                    try:
                        response = await client_manager.make_request(
                            "GET",
                            f"{base_url}/api/groups",
                            headers=headers,
                            params={"fields": group_fields},
                            timeout=10.0,
                        )

                        all_groups = response.json()
                        user_groups = []

                        for group in all_groups:
                            users = group.get("users", [])
                            for user in users:
                                user_login = user.get("login")
                                user_id_from_api = user.get("id")
                                if user_login == user_id or user_id_from_api == user_id:
                                    user_groups.append(
                                        {
                                            "id": group.get("id"),
                                            "name": group.get("name"),
                                            "description": group.get("description", ""),
                                            "permissions": [],  # Groups don't have permissions in YouTrack
                                        }
                                    )
                                    break

                        if user_groups:
                            return {"status": "success", "data": user_groups, "user_id": user_id}
                    except Exception:
                        continue

                # If no groups found, return empty result
                return {"status": "success", "data": [], "user_id": user_id}

            except Exception:
                pass

            # If all methods fail, return empty result
            return {"status": "success", "data": [], "user_id": user_id}

        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def get_user_roles(self, user_id: str) -> dict[str, Any]:
        """Get roles assigned to a user.

        Args:
            user_id: User ID or login

        Returns:
            Dictionary with operation result
        """
        credentials = self.auth_manager.load_credentials()
        if not credentials:
            return {
                "status": "error",
                "message": "Not authenticated. Run 'yt auth login' first.",
            }

        headers = {
            "Authorization": f"Bearer {credentials.token}",
            "Accept": "application/json",
        }

        try:
            client_manager = get_client_manager()
            base_url = credentials.base_url.rstrip("/")

            # Try different field configurations to find one that works
            field_configs = [
                "roles(id,name,description,permissions(name,permission))",
                "roles(id,name,description)",
                "roles(id,name)",
                "roles",
            ]

            for fields in field_configs:
                try:
                    response = await client_manager.make_request(
                        "GET",
                        f"{base_url}/api/users/{user_id}",
                        headers=headers,
                        params={"fields": fields},
                        timeout=10.0,
                    )

                    user = response.json()
                    roles = user.get("roles", [])

                    # If we found roles with permissions, return them
                    if roles:
                        # Check if any role has permissions data
                        has_permissions = any(role.get("permissions") for role in roles)
                        if has_permissions or fields == "roles":  # Return if has permissions or is last attempt
                            return {"status": "success", "data": roles, "user_id": user_id}
                        # Continue to try other field configurations if no permissions found

                except Exception:
                    continue

            # Try Hub API with user query as fallback
            try:
                response = await client_manager.make_request(
                    "GET",
                    f"{base_url}/hub/api/rest/users",
                    headers=headers,
                    params={"query": user_id},
                    timeout=10.0,
                )

                data = response.json()
                users = data.get("users", [])

                if users:
                    user = users[0]
                    # Extract roles from transitiveProjectRoles
                    transitive_roles = user.get("transitiveProjectRoles", [])
                    roles = []

                    for project_role in transitive_roles:
                        role_info = project_role.get("role", {})
                        if role_info:
                            role_data = {
                                "id": role_info.get("id"),
                                "name": role_info.get("name"),
                                "key": role_info.get("key"),
                                "description": role_info.get("description", ""),
                                "permissions": [],  # Initialize empty permissions
                            }

                            # Try to get role permissions from Hub API
                            try:
                                role_id = role_info.get("id")
                                if role_id:
                                    role_response = await client_manager.make_request(
                                        "GET",
                                        f"{base_url}/hub/api/rest/roles/{role_id}",
                                        headers=headers,
                                        timeout=10.0,
                                    )
                                    detailed_role = role_response.json()
                                    role_permissions = detailed_role.get("permissions", [])
                                    if role_permissions:
                                        role_data["permissions"] = role_permissions
                            except Exception:
                                # If we can't get permissions, continue with empty list
                                pass

                            roles.append(role_data)

                    # Remove duplicates based on role ID
                    unique_roles = []
                    seen_ids = set()
                    for role in roles:
                        if role["id"] not in seen_ids:
                            unique_roles.append(role)
                            seen_ids.add(role["id"])

                    return {"status": "success", "data": unique_roles, "user_id": user_id}

            except Exception:
                pass

            # If all methods fail, return empty result
            return {"status": "success", "data": [], "user_id": user_id}

        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def get_user_teams(self, user_id: str) -> dict[str, Any]:
        """Get teams that a user is a member of.

        Args:
            user_id: User ID or login

        Returns:
            Dictionary with operation result
        """
        credentials = self.auth_manager.load_credentials()
        if not credentials:
            return {
                "status": "error",
                "message": "Not authenticated. Run 'yt auth login' first.",
            }

        headers = {
            "Authorization": f"Bearer {credentials.token}",
            "Accept": "application/json",
        }

        try:
            client_manager = get_client_manager()
            base_url = credentials.base_url.rstrip("/")

            # Try different field configurations to find one that works
            field_configs = ["teams(id,name,description)", "teams(id,name)", "teams"]

            for fields in field_configs:
                try:
                    response = await client_manager.make_request(
                        "GET",
                        f"{base_url}/api/users/{user_id}",
                        headers=headers,
                        params={"fields": fields},
                        timeout=10.0,
                    )

                    user = response.json()
                    teams = user.get("teams", [])

                    # If we found teams, return them
                    if teams:
                        return {"status": "success", "data": teams, "user_id": user_id}

                except Exception:
                    continue

            # Try Hub API with user query as fallback
            try:
                response = await client_manager.make_request(
                    "GET",
                    f"{base_url}/hub/api/rest/users",
                    headers=headers,
                    params={"query": user_id},
                    timeout=10.0,
                )

                data = response.json()
                users = data.get("users", [])

                if users:
                    user = users[0]
                    # Extract teams from transitiveTeams
                    transitive_teams = user.get("transitiveTeams", [])
                    teams = []

                    for team_info in transitive_teams:
                        team_id = team_info.get("id")
                        if team_id:
                            # Try to get team details
                            try:
                                team_response = await client_manager.make_request(
                                    "GET",
                                    f"{base_url}/hub/api/rest/projectteams/{team_id}",
                                    headers=headers,
                                    timeout=10.0,
                                )
                                team_data = team_response.json()
                                teams.append(
                                    {
                                        "id": team_data.get("id"),
                                        "name": team_data.get("name", f"Team {team_id}"),
                                        "description": team_data.get("description", ""),
                                    }
                                )
                            except Exception:
                                # If we can't get team details, add basic info
                                teams.append({"id": team_id, "name": f"Team {team_id}", "description": ""})

                    return {"status": "success", "data": teams, "user_id": user_id}

            except Exception:
                pass

            # If all methods fail, return empty result
            return {"status": "success", "data": [], "user_id": user_id}

        except Exception as e:
            return {"status": "error", "message": str(e)}

    def display_user_groups(self, groups: list[dict[str, Any]], user_id: str) -> None:
        """Display user groups in a formatted table.

        Args:
            groups: List of group dictionaries
            user_id: User ID for context
        """
        if not groups:
            self.console.print(f"No groups found for user '{user_id}'.", style="yellow")
            return

        table = Table(title=f"Groups for User: {user_id}")
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Description", style="blue")
        table.add_column("Type", style="green")

        for group in groups:
            name = group.get("name", "N/A")
            description = group.get("description", "")

            # Groups are organizational units in YouTrack, not permission holders
            group_type = "Organizational"

            table.add_row(name, description or "No description", group_type)

        self.console.print(table)
        self.console.print(
            "\n[dim]Note: Groups are organizational units. User permissions are managed through roles.[/dim]"
        )

    def display_user_roles(self, roles: list[dict[str, Any]], user_id: str) -> None:
        """Display user roles in a formatted table.

        Args:
            roles: List of role dictionaries
            user_id: User ID for context
        """
        if not roles:
            self.console.print(f"No roles found for user '{user_id}'.", style="yellow")
            return

        table = Table(title=f"Roles for User: {user_id}")
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Description", style="blue")
        table.add_column("Permissions", style="green")

        for role in roles:
            name = role.get("name", "N/A")
            description = role.get("description", "")
            permissions = role.get("permissions", [])

            # Format permissions
            if permissions:
                perm_names = [p.get("name", "N/A") for p in permissions]
                perm_text = ", ".join(perm_names)
            else:
                perm_text = "None"

            table.add_row(name, description or "No description", perm_text)

        self.console.print(table)

    def display_user_teams(self, teams: list[dict[str, Any]], user_id: str) -> None:
        """Display user teams in a formatted table.

        Args:
            teams: List of team dictionaries
            user_id: User ID for context
        """
        if not teams:
            self.console.print(f"No teams found for user '{user_id}'.", style="yellow")
            return

        table = Table(title=f"Teams for User: {user_id}")
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Description", style="blue")

        for team in teams:
            name = team.get("name", "N/A")
            description = team.get("description", "")

            table.add_row(name, description or "No description")

        self.console.print(table)

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
