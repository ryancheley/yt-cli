"""User service for YouTrack API operations."""

from typing import Any, Dict, Optional

from .base import BaseService


class UserService(BaseService):
    """Service for YouTrack user API operations.

    Handles all HTTP communication with YouTrack's users API endpoints.
    Pure API service with no business logic or presentation concerns.
    """

    async def list_users(
        self,
        fields: Optional[str] = None,
        top: Optional[int] = None,
        skip: Optional[int] = None,
        query: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List all users via API.

        Args:
            fields: Comma-separated list of user fields to return
            top: Maximum number of users to return
            skip: Number of users to skip
            query: Search query to filter users

        Returns:
            API response with user list
        """
        try:
            params = {}

            if fields:
                params["fields"] = fields
            else:
                params["fields"] = (
                    "id,login,fullName,email,banned,online,guest,ringId,avatarUrl,teams(name,description)"
                )

            if query:
                params["query"] = query
            if top is not None:
                params["$top"] = str(top)
            if skip is not None:
                params["$skip"] = str(skip)

            response = await self._make_request("GET", "users", params=params)
            return await self._handle_response(response)

        except ValueError as e:
            return self._create_error_response(str(e))
        except Exception as e:
            return self._create_error_response(f"Error listing users: {str(e)}")

    async def get_user(self, user_id: str, fields: Optional[str] = None) -> Dict[str, Any]:
        """Get a specific user via API.

        Args:
            user_id: User ID or login
            fields: Comma-separated list of fields to return

        Returns:
            API response with user data
        """
        try:
            params = {}

            if fields:
                params["fields"] = fields
            else:
                params["fields"] = (
                    "id,login,fullName,email,banned,online,guest,ringId,avatarUrl,"
                    "teams(name,description),groups(name,description)"
                )

            response = await self._make_request("GET", f"users/{user_id}", params=params)
            return await self._handle_response(response)

        except ValueError as e:
            return self._create_error_response(str(e))
        except Exception as e:
            return self._create_error_response(f"Error getting user: {str(e)}")

    async def create_user(
        self,
        login: str,
        full_name: str,
        email: str,
        password: Optional[str] = None,
        force_change_password: bool = False,
    ) -> Dict[str, Any]:
        """Create a new user via API.

        Args:
            login: User login name
            full_name: User's full name
            email: User's email address
            password: Initial password
            force_change_password: Force password change on first login

        Returns:
            API response with created user data
        """
        try:
            user_data = {
                "login": login,
                "fullName": full_name,
                "email": email,
                "forceChangePassword": force_change_password,
            }

            if password:
                user_data["password"] = password

            response = await self._make_request("POST", "users", json_data=user_data)
            return await self._handle_response(response, success_codes=[200, 201])

        except ValueError as e:
            return self._create_error_response(str(e))
        except Exception as e:
            return self._create_error_response(f"Error creating user: {str(e)}")

    async def update_user(
        self,
        user_id: str,
        full_name: Optional[str] = None,
        email: Optional[str] = None,
        banned: Optional[bool] = None,
        password: Optional[str] = None,
        force_change_password: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Update an existing user via API.

        Args:
            user_id: User ID to update
            full_name: New full name
            email: New email address
            banned: New banned status
            password: New password
            force_change_password: Force password change on next login

        Returns:
            API response
        """
        try:
            update_data: Dict[str, Any] = {}

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

            response = await self._make_request("POST", f"users/{user_id}", json_data=update_data)
            return await self._handle_response(response)

        except ValueError as e:
            return self._create_error_response(str(e))
        except Exception as e:
            return self._create_error_response(f"Error updating user: {str(e)}")

    async def delete_user(self, user_id: str) -> Dict[str, Any]:
        """Delete a user via API.

        Args:
            user_id: User ID to delete

        Returns:
            API response
        """
        try:
            response = await self._make_request("DELETE", f"users/{user_id}")
            return await self._handle_response(response)

        except ValueError as e:
            return self._create_error_response(str(e))
        except Exception as e:
            return self._create_error_response(f"Error deleting user: {str(e)}")

    async def ban_user(self, user_id: str) -> Dict[str, Any]:
        """Ban a user via API.

        Args:
            user_id: User ID to ban

        Returns:
            API response
        """
        try:
            update_data = {"banned": True}
            response = await self._make_request("POST", f"users/{user_id}", json_data=update_data)
            return await self._handle_response(response)

        except ValueError as e:
            return self._create_error_response(str(e))
        except Exception as e:
            return self._create_error_response(f"Error banning user: {str(e)}")

    async def unban_user(self, user_id: str) -> Dict[str, Any]:
        """Unban a user via API.

        Args:
            user_id: User ID to unban

        Returns:
            API response
        """
        try:
            update_data = {"banned": False}
            response = await self._make_request("POST", f"users/{user_id}", json_data=update_data)
            return await self._handle_response(response)

        except ValueError as e:
            return self._create_error_response(str(e))
        except Exception as e:
            return self._create_error_response(f"Error unbanning user: {str(e)}")

    async def get_user_groups(self, user_id: str, fields: Optional[str] = None) -> Dict[str, Any]:
        """Get user's groups via API.

        Args:
            user_id: User ID or login
            fields: Comma-separated list of group fields to return

        Returns:
            API response with group list
        """
        try:
            params = {}
            if fields:
                params["fields"] = fields
            else:
                params["fields"] = "id,name,description,autoJoin,teamAutoJoin"

            response = await self._make_request("GET", f"users/{user_id}/groups", params=params)
            return await self._handle_response(response)

        except ValueError as e:
            return self._create_error_response(str(e))
        except Exception as e:
            return self._create_error_response(f"Error getting user groups: {str(e)}")

    async def add_user_to_group(self, user_id: str, group_id: str) -> Dict[str, Any]:
        """Add user to a group via API.

        Args:
            user_id: User ID or login
            group_id: Group ID to add user to

        Returns:
            API response
        """
        try:
            group_data = {"id": group_id}
            response = await self._make_request("POST", f"users/{user_id}/groups", json_data=group_data)
            return await self._handle_response(response, success_codes=[200, 201])

        except ValueError as e:
            return self._create_error_response(str(e))
        except Exception as e:
            return self._create_error_response(f"Error adding user to group: {str(e)}")

    async def remove_user_from_group(self, user_id: str, group_id: str) -> Dict[str, Any]:
        """Remove user from a group via API.

        Args:
            user_id: User ID or login
            group_id: Group ID to remove user from

        Returns:
            API response
        """
        try:
            response = await self._make_request("DELETE", f"users/{user_id}/groups/{group_id}")
            return await self._handle_response(response)

        except ValueError as e:
            return self._create_error_response(str(e))
        except Exception as e:
            return self._create_error_response(f"Error removing user from group: {str(e)}")

    async def get_user_roles(self, user_id: str, fields: Optional[str] = None) -> Dict[str, Any]:
        """Get user's roles via API.

        Args:
            user_id: User ID or login
            fields: Comma-separated list of role fields to return

        Returns:
            API response with role list
        """
        try:
            params = {}
            if fields:
                params["fields"] = fields
            else:
                params["fields"] = "id,name,description"

            response = await self._make_request("GET", f"users/{user_id}/roles", params=params)
            return await self._handle_response(response)

        except ValueError as e:
            return self._create_error_response(str(e))
        except Exception as e:
            return self._create_error_response(f"Error getting user roles: {str(e)}")

    async def assign_user_role(self, user_id: str, role_id: str) -> Dict[str, Any]:
        """Assign a role to user via API.

        Args:
            user_id: User ID or login
            role_id: Role ID to assign

        Returns:
            API response
        """
        try:
            role_data = {"id": role_id}
            response = await self._make_request("POST", f"users/{user_id}/roles", json_data=role_data)
            return await self._handle_response(response, success_codes=[200, 201])

        except ValueError as e:
            return self._create_error_response(str(e))
        except Exception as e:
            return self._create_error_response(f"Error assigning user role: {str(e)}")

    async def remove_user_role(self, user_id: str, role_id: str) -> Dict[str, Any]:
        """Remove a role from user via API.

        Args:
            user_id: User ID or login
            role_id: Role ID to remove

        Returns:
            API response
        """
        try:
            response = await self._make_request("DELETE", f"users/{user_id}/roles/{role_id}")
            return await self._handle_response(response)

        except ValueError as e:
            return self._create_error_response(str(e))
        except Exception as e:
            return self._create_error_response(f"Error removing user role: {str(e)}")

    async def get_user_teams(self, user_id: str, fields: Optional[str] = None) -> Dict[str, Any]:
        """Get user's teams via API.

        Args:
            user_id: User ID or login
            fields: Comma-separated list of team fields to return

        Returns:
            API response with team list
        """
        try:
            params = {}
            if fields:
                params["fields"] = fields
            else:
                params["fields"] = "id,name,description"

            response = await self._make_request("GET", f"users/{user_id}/teams", params=params)
            return await self._handle_response(response)

        except ValueError as e:
            return self._create_error_response(str(e))
        except Exception as e:
            return self._create_error_response(f"Error getting user teams: {str(e)}")

    async def add_user_to_team(self, user_id: str, team_id: str) -> Dict[str, Any]:
        """Add user to a team via API.

        Args:
            user_id: User ID or login
            team_id: Team ID to add user to

        Returns:
            API response
        """
        try:
            team_data = {"id": team_id}
            response = await self._make_request("POST", f"users/{user_id}/teams", json_data=team_data)
            return await self._handle_response(response, success_codes=[200, 201])

        except ValueError as e:
            return self._create_error_response(str(e))
        except Exception as e:
            return self._create_error_response(f"Error adding user to team: {str(e)}")

    async def remove_user_from_team(self, user_id: str, team_id: str) -> Dict[str, Any]:
        """Remove user from a team via API.

        Args:
            user_id: User ID or login
            team_id: Team ID to remove user from

        Returns:
            API response
        """
        try:
            response = await self._make_request("DELETE", f"users/{user_id}/teams/{team_id}")
            return await self._handle_response(response)

        except ValueError as e:
            return self._create_error_response(str(e))
        except Exception as e:
            return self._create_error_response(f"Error removing user from team: {str(e)}")

    async def change_user_password(self, user_id: str, new_password: str, force_change: bool = False) -> Dict[str, Any]:
        """Change user password via API.

        Args:
            user_id: User ID or login
            new_password: New password
            force_change: Force password change on next login

        Returns:
            API response
        """
        try:
            password_data = {
                "password": new_password,
                "forceChangePassword": force_change,
            }

            response = await self._make_request("POST", f"users/{user_id}", json_data=password_data)
            return await self._handle_response(response)

        except ValueError as e:
            return self._create_error_response(str(e))
        except Exception as e:
            return self._create_error_response(f"Error changing user password: {str(e)}")

    async def get_user_permissions(self, user_id: str, project_id: Optional[str] = None) -> Dict[str, Any]:
        """Get user permissions via API.

        Args:
            user_id: User ID or login
            project_id: Optional project ID to get project-specific permissions

        Returns:
            API response with permission list
        """
        try:
            endpoint = f"users/{user_id}/permissions"
            params = {}

            if project_id:
                params["project"] = project_id

            response = await self._make_request("GET", endpoint, params=params)
            return await self._handle_response(response)

        except ValueError as e:
            return self._create_error_response(str(e))
        except Exception as e:
            return self._create_error_response(f"Error getting user permissions: {str(e)}")
