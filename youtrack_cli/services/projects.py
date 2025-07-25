"""Project service for YouTrack API operations."""

from typing import Any, Dict, Optional

from .base import BaseService


class ProjectService(BaseService):
    """Service for YouTrack project API operations.
    
    Handles all HTTP communication with YouTrack's projects API endpoints.
    Pure API service with no business logic or presentation concerns.
    """

    async def list_projects(
        self,
        fields: Optional[str] = None,
        top: Optional[int] = None,
        skip: Optional[int] = None,
        show_archived: bool = False,
    ) -> Dict[str, Any]:
        """List all projects via API.
        
        Args:
            fields: Comma-separated list of project fields to return
            top: Maximum number of projects to return
            skip: Number of projects to skip
            show_archived: Whether to include archived projects
            
        Returns:
            API response with project list
        """
        try:
            params = {}

            if fields:
                params["fields"] = fields
            else:
                params["fields"] = "id,name,shortName,description,leader(login,fullName),archived,createdBy(login,fullName)"

            if top is not None:
                params["$top"] = str(top)
            if skip is not None:
                params["$skip"] = str(skip)

            response = await self._make_request("GET", "admin/projects", params=params)
            result = await self._handle_response(response)

            # Filter archived projects if requested
            if result["status"] == "success" and not show_archived:
                projects = result["data"]
                if isinstance(projects, list):
                    filtered_projects = [p for p in projects if p is not None and not p.get("archived", False)]
                    result["data"] = filtered_projects

            return result

        except ValueError as e:
            return self._create_error_response(str(e))
        except Exception as e:
            return self._create_error_response(f"Error listing projects: {str(e)}")

    async def get_project(self, project_id: str, fields: Optional[str] = None) -> Dict[str, Any]:
        """Get a specific project via API.
        
        Args:
            project_id: Project ID or short name
            fields: Comma-separated list of fields to return
            
        Returns:
            API response with project data
        """
        try:
            params = {}

            if fields:
                params["fields"] = fields
            else:
                params["fields"] = (
                    "id,name,shortName,description,leader(login,fullName),"
                    "archived,createdBy(login,fullName),team(users(login,fullName))"
                )

            response = await self._make_request("GET", f"admin/projects/{project_id}", params=params)
            return await self._handle_response(response)

        except ValueError as e:
            return self._create_error_response(str(e))
        except Exception as e:
            return self._create_error_response(f"Error getting project: {str(e)}")

    async def create_project(
        self,
        short_name: str,
        name: str,
        description: Optional[str] = None,
        leader_login: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new project via API.
        
        Args:
            short_name: Project short name (ID)
            name: Project full name
            description: Project description
            leader_login: Project leader login
            
        Returns:
            API response with created project data
        """
        try:
            project_data = {
                "shortName": short_name,
                "name": name,
            }

            if description:
                project_data["description"] = description
            if leader_login:
                project_data["leader"] = {"login": leader_login}

            response = await self._make_request("POST", "admin/projects", json_data=project_data)
            return await self._handle_response(response, success_codes=[200, 201])

        except ValueError as e:
            return self._create_error_response(str(e))
        except Exception as e:
            return self._create_error_response(f"Error creating project: {str(e)}")

    async def update_project(
        self,
        project_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        leader_login: Optional[str] = None,
        archived: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Update an existing project via API.
        
        Args:
            project_id: Project ID to update
            name: New project name
            description: New project description
            leader_login: New project leader login
            archived: Archive status
            
        Returns:
            API response
        """
        try:
            update_data: Dict[str, Any] = {}

            if name is not None:
                update_data["name"] = name
            if description is not None:
                update_data["description"] = description
            if leader_login is not None:
                update_data["leader"] = {"login": leader_login}
            if archived is not None:
                update_data["archived"] = archived

            response = await self._make_request("POST", f"admin/projects/{project_id}", json_data=update_data)
            return await self._handle_response(response)

        except ValueError as e:
            return self._create_error_response(str(e))
        except Exception as e:
            return self._create_error_response(f"Error updating project: {str(e)}")

    async def delete_project(self, project_id: str) -> Dict[str, Any]:
        """Delete a project via API.
        
        Args:
            project_id: Project ID to delete
            
        Returns:
            API response
        """
        try:
            response = await self._make_request("DELETE", f"admin/projects/{project_id}")
            return await self._handle_response(response)

        except ValueError as e:
            return self._create_error_response(str(e))
        except Exception as e:
            return self._create_error_response(f"Error deleting project: {str(e)}")

    async def archive_project(self, project_id: str) -> Dict[str, Any]:
        """Archive a project via API.
        
        Args:
            project_id: Project ID to archive
            
        Returns:
            API response
        """
        try:
            update_data = {"archived": True}
            response = await self._make_request("POST", f"admin/projects/{project_id}", json_data=update_data)
            return await self._handle_response(response)

        except ValueError as e:
            return self._create_error_response(str(e))
        except Exception as e:
            return self._create_error_response(f"Error archiving project: {str(e)}")

    async def unarchive_project(self, project_id: str) -> Dict[str, Any]:
        """Unarchive a project via API.
        
        Args:
            project_id: Project ID to unarchive
            
        Returns:
            API response
        """
        try:
            update_data = {"archived": False}
            response = await self._make_request("POST", f"admin/projects/{project_id}", json_data=update_data)
            return await self._handle_response(response)

        except ValueError as e:
            return self._create_error_response(str(e))
        except Exception as e:
            return self._create_error_response(f"Error unarchiving project: {str(e)}")

    async def get_project_team(self, project_id: str, fields: Optional[str] = None) -> Dict[str, Any]:
        """Get project team members via API.
        
        Args:
            project_id: Project ID
            fields: Comma-separated list of user fields to return
            
        Returns:
            API response with team member list
        """
        try:
            params = {}
            if fields:
                params["fields"] = fields
            else:
                params["fields"] = "login,fullName,email,avatarUrl"

            response = await self._make_request("GET", f"admin/projects/{project_id}/team", params=params)
            return await self._handle_response(response)

        except ValueError as e:
            return self._create_error_response(str(e))
        except Exception as e:
            return self._create_error_response(f"Error getting project team: {str(e)}")

    async def add_team_member(self, project_id: str, user_login: str) -> Dict[str, Any]:
        """Add a user to project team via API.
        
        Args:
            project_id: Project ID
            user_login: User login to add
            
        Returns:
            API response
        """
        try:
            user_data = {"login": user_login}
            response = await self._make_request("POST", f"admin/projects/{project_id}/team", json_data=user_data)
            return await self._handle_response(response, success_codes=[200, 201])

        except ValueError as e:
            return self._create_error_response(str(e))
        except Exception as e:
            return self._create_error_response(f"Error adding team member: {str(e)}")

    async def remove_team_member(self, project_id: str, user_login: str) -> Dict[str, Any]:
        """Remove a user from project team via API.
        
        Args:
            project_id: Project ID
            user_login: User login to remove
            
        Returns:
            API response
        """
        try:
            response = await self._make_request("DELETE", f"admin/projects/{project_id}/team/{user_login}")
            return await self._handle_response(response)

        except ValueError as e:
            return self._create_error_response(str(e))
        except Exception as e:
            return self._create_error_response(f"Error removing team member: {str(e)}")

    async def get_project_custom_fields(self, project_id: str, fields: Optional[str] = None) -> Dict[str, Any]:
        """Get project custom fields via API.
        
        Args:
            project_id: Project ID
            fields: Comma-separated list of field properties to return
            
        Returns:
            API response with custom field list
        """
        try:
            params = {}
            if fields:
                params["fields"] = fields
            else:
                params["fields"] = "id,name,fieldType,localizedName,isPublic,ordinal"

            response = await self._make_request("GET", f"admin/projects/{project_id}/customFields", params=params)
            return await self._handle_response(response)

        except ValueError as e:
            return self._create_error_response(str(e))
        except Exception as e:
            return self._create_error_response(f"Error getting project custom fields: {str(e)}")

    async def attach_custom_field(
        self,
        project_id: str,
        field_id: str,
        is_public: Optional[bool] = None
    ) -> Dict[str, Any]:
        """Attach a custom field to a project via API.
        
        Args:
            project_id: Project ID
            field_id: Custom field ID
            is_public: Whether field should be public
            
        Returns:
            API response
        """
        try:
            field_data: Dict[str, Any] = {"field": {"id": field_id}}

            if is_public is not None:
                field_data["isPublic"] = is_public

            response = await self._make_request(
                "POST", f"admin/projects/{project_id}/customFields", json_data=field_data
            )
            return await self._handle_response(response, success_codes=[200, 201])

        except ValueError as e:
            return self._create_error_response(str(e))
        except Exception as e:
            return self._create_error_response(f"Error attaching custom field: {str(e)}")

    async def detach_custom_field(self, project_id: str, field_id: str) -> Dict[str, Any]:
        """Detach a custom field from a project via API.
        
        Args:
            project_id: Project ID
            field_id: Custom field ID to detach
            
        Returns:
            API response
        """
        try:
            response = await self._make_request("DELETE", f"admin/projects/{project_id}/customFields/{field_id}")
            return await self._handle_response(response)

        except ValueError as e:
            return self._create_error_response(str(e))
        except Exception as e:
            return self._create_error_response(f"Error detaching custom field: {str(e)}")

    async def get_project_versions(self, project_id: str, fields: Optional[str] = None) -> Dict[str, Any]:
        """Get project versions via API.
        
        Args:
            project_id: Project ID
            fields: Comma-separated list of version fields to return
            
        Returns:
            API response with version list
        """
        try:
            params = {}
            if fields:
                params["fields"] = fields
            else:
                params["fields"] = "id,name,description,archived,released,releaseDate"

            response = await self._make_request("GET", f"admin/projects/{project_id}/versions", params=params)
            return await self._handle_response(response)

        except ValueError as e:
            return self._create_error_response(str(e))
        except Exception as e:
            return self._create_error_response(f"Error getting project versions: {str(e)}")

    async def create_project_version(
        self,
        project_id: str,
        name: str,
        description: Optional[str] = None,
        released: Optional[bool] = None,
        archived: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Create a project version via API.
        
        Args:
            project_id: Project ID
            name: Version name
            description: Version description
            released: Whether version is released
            archived: Whether version is archived
            
        Returns:
            API response with created version data
        """
        try:
            version_data: Dict[str, Any] = {"name": name}

            if description is not None:
                version_data["description"] = description
            if released is not None:
                version_data["released"] = released
            if archived is not None:
                version_data["archived"] = archived

            response = await self._make_request(
                "POST", f"admin/projects/{project_id}/versions", json_data=version_data
            )
            return await self._handle_response(response, success_codes=[200, 201])

        except ValueError as e:
            return self._create_error_response(str(e))
        except Exception as e:
            return self._create_error_response(f"Error creating project version: {str(e)}")
