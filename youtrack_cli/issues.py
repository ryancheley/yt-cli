"""Issue management for YouTrack CLI."""

from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx
from rich.table import Table

from .auth import AuthManager
from .client import get_client_manager
from .console import get_console
from .custom_field_manager import CustomFieldManager
from .field_selection import get_field_selector
from .logging import get_logger
from .pagination import create_paginated_display
from .panels import (
    PanelGroup,
    create_custom_fields_panel,
    create_issue_details_panel,
    create_issue_overview_panel,
)
from .progress import get_progress_manager
from .utils import format_timestamp

__all__ = ["IssueManager"]

logger = get_logger(__name__)


class IssueManager:
    """Manages YouTrack issues operations."""

    def __init__(self, auth_manager: AuthManager):
        self.auth_manager = auth_manager
        self.console = get_console()

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

    def _get_custom_field_value(self, issue: Dict[str, Any], field_name: str) -> Optional[str]:
        """Extract value from custom fields by field name using CustomFieldManager.

        Supports all YouTrack custom field types including:
        - avatarUrl, buildLink, color(id), fullName, isResolved
        - localizedName, minutes, presentation, text
        - Complex nested field structures
        """
        custom_fields = issue.get("customFields", [])
        result = CustomFieldManager.extract_field_value(custom_fields, field_name)
        return str(result) if result is not None else None

    def _get_assignee_name(self, issue: Dict[str, Any]) -> str:
        """Get assignee name from either regular field or custom field."""
        # First try the regular assignee field
        assignee = issue.get("assignee")
        if assignee and isinstance(assignee, dict):
            if assignee.get("fullName"):
                return assignee["fullName"]
            if assignee.get("name"):
                return assignee["name"]
            if assignee.get("login"):
                return assignee["login"]

        # If not found, try the Assignee custom field
        custom_assignee = self._get_custom_field_value(issue, "Assignee")
        if custom_assignee:
            return custom_assignee

        return "Unassigned"

    async def create_issue(
        self,
        project_id: str,
        summary: str,
        description: Optional[str] = None,
        issue_type: Optional[str] = None,
        priority: Optional[str] = None,
        assignee: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new issue."""
        credentials = self.auth_manager.load_credentials()
        if not credentials:
            return {"status": "error", "message": "Not authenticated"}

        # Resolve project short name to internal ID
        resolved_project_id = await self._resolve_project_id(project_id)
        if resolved_project_id is None:
            return {
                "status": "error",
                "message": f"Project '{project_id}' not found. Please check the project short name or ID.",
            }

        issue_data = {
            "project": {"id": resolved_project_id},
            "summary": summary,
        }

        if description:
            issue_data["description"] = description
        if issue_type:
            issue_data["type"] = {"name": issue_type}
        if priority:
            issue_data["priority"] = {"name": priority}
        if assignee:
            issue_data["assignee"] = {"login": assignee}

        url = f"{credentials.base_url.rstrip('/')}/api/issues"
        headers = {
            "Authorization": f"Bearer {credentials.token}",
            "Content-Type": "application/json",
        }

        try:
            client_manager = get_client_manager()
            response = await client_manager.make_request("POST", url, headers=headers, json_data=issue_data)
            if response.status_code in [200, 201]:
                data = self._parse_json_response(response)

                # Make follow-up call to get friendly ID (idReadable)
                issue_id = data.get("id")
                if issue_id:
                    try:
                        detail_url = f"{credentials.base_url.rstrip('/')}/api/issues/{issue_id}"
                        detail_params = {"fields": "idReadable"}
                        detail_response = await client_manager.make_request(
                            "GET",
                            detail_url,
                            headers={"Authorization": f"Bearer {credentials.token}"},
                            params=detail_params,
                        )
                        if detail_response.status_code == 200:
                            detail_data = self._parse_json_response(detail_response)
                            friendly_id = detail_data.get("idReadable")
                            if friendly_id:
                                # Update the data with friendly ID for display
                                data["idReadable"] = friendly_id
                    except Exception as e:
                        logger.warning("Failed to fetch friendly ID for created issue", error=str(e), issue_id=issue_id)
                        # Continue with internal ID if friendly ID fetch fails

                return {
                    "status": "success",
                    "message": f"Issue '{summary}' created successfully",
                    "data": data,
                }
            error_text = response.text
            return {
                "status": "error",
                "message": f"Failed to create issue: {error_text}",
            }
        except Exception as e:
            error_message = str(e)
            # Check if this is a priority field requirement issue
            if "Priority is required" in error_message and priority:
                try:
                    client_manager = get_client_manager()
                    issue_data_no_priority = issue_data.copy()
                    if "priority" in issue_data_no_priority:
                        del issue_data_no_priority["priority"]
                    if "type" in issue_data_no_priority:
                        del issue_data_no_priority["type"]

                    # Try with custom fields format using CustomFieldManager
                    custom_fields = [CustomFieldManager.create_single_enum_field("Priority", priority)]

                    # Also add Type field if it was specified
                    if issue_type:
                        custom_fields.append(CustomFieldManager.create_single_enum_field("Type", issue_type))
                    else:
                        # Default to "Task" if no type specified
                        custom_fields.append(CustomFieldManager.create_single_enum_field("Type", "Task"))

                    issue_data_no_priority["customFields"] = custom_fields

                    retry_response = await client_manager.make_request(
                        "POST", url, headers=headers, json_data=issue_data_no_priority
                    )
                    if retry_response.status_code in [200, 201]:
                        data = self._parse_json_response(retry_response)

                        # Make follow-up call to get friendly ID (idReadable)
                        issue_id = data.get("id")
                        if issue_id:
                            try:
                                detail_url = f"{credentials.base_url.rstrip('/')}/api/issues/{issue_id}"
                                detail_params = {"fields": "idReadable"}
                                detail_response = await client_manager.make_request(
                                    "GET",
                                    detail_url,
                                    headers={"Authorization": f"Bearer {credentials.token}"},
                                    params=detail_params,
                                )
                                if detail_response.status_code == 200:
                                    detail_data = self._parse_json_response(detail_response)
                                    friendly_id = detail_data.get("idReadable")
                                    if friendly_id:
                                        # Update the data with friendly ID for display
                                        data["idReadable"] = friendly_id
                            except Exception as e:
                                logger.warning(
                                    "Failed to fetch friendly ID for created issue",
                                    error=str(e),
                                    issue_id=issue_id,
                                )
                                # Continue with internal ID if friendly ID fetch fails

                        return {
                            "status": "success",
                            "message": f"Issue '{summary}' created successfully (using custom field format)",
                            "data": data,
                        }
                except Exception:
                    pass  # Fallback failed, return original error

            return {"status": "error", "message": f"Error creating issue: {error_message}"}

    async def list_issues(
        self,
        project_id: Optional[str] = None,
        fields: Optional[str] = None,
        field_profile: Optional[str] = None,
        page_size: int = 100,
        top: Optional[int] = None,  # Legacy parameter for backward compatibility
        query: Optional[str] = None,
        state: Optional[str] = None,
        assignee: Optional[str] = None,
        after_cursor: Optional[str] = None,
        before_cursor: Optional[str] = None,
        use_pagination: bool = False,
        max_results: Optional[int] = None,
    ) -> Dict[str, Any]:
        """List issues with optional filtering and cursor pagination support."""
        from .utils import paginate_results  # Import here to avoid circular imports

        progress_manager = get_progress_manager()

        credentials = self.auth_manager.load_credentials()
        if not credentials:
            return {"status": "error", "message": "Not authenticated"}

        # Handle legacy top parameter
        if top is not None:
            page_size = top
            use_pagination = False

        with progress_manager.spinner("Fetching issues..."):
            params = {}

            # Use field selector for optimized field selection
            field_selector = get_field_selector()
            if fields:
                # User provided custom fields
                if field_selector.validate_fields(fields, "issues"):
                    params["fields"] = fields
                else:
                    logger.warning("Invalid field specification, using standard profile", fields=fields)
                    params["fields"] = field_selector.get_fields("issues", "standard")
            else:
                # Use field profile or default to standard
                profile = field_profile or "standard"
                params["fields"] = field_selector.get_fields("issues", profile)

            # Build query string
            query_parts = []
            if project_id:
                query_parts.append(f"project:{project_id}")
            if state:
                query_parts.append(f"state:{state}")
            if assignee:
                query_parts.append(f"assignee:{assignee}")
            if query:
                query_parts.append(query)

            if query_parts:
                params["query"] = " AND ".join(query_parts)

            url = f"{credentials.base_url.rstrip('/')}/api/issues"
            headers = {"Authorization": f"Bearer {credentials.token}"}

            try:
                if use_pagination:
                    # Use enhanced pagination with cursor support
                    result = await paginate_results(
                        endpoint=url,
                        headers=headers,
                        params=params,
                        page_size=page_size,
                        max_results=max_results,
                        after_cursor=after_cursor,
                        before_cursor=before_cursor,
                        use_cursor_pagination=bool(after_cursor or before_cursor),
                    )
                    return {
                        "status": "success",
                        "data": result["results"],
                        "count": result["total_results"],
                        "pagination": {
                            "has_after": result["has_after"],
                            "has_before": result["has_before"],
                            "after_cursor": result["after_cursor"],
                            "before_cursor": result["before_cursor"],
                        },
                    }
                # Single request (legacy behavior)
                if top:
                    params["$top"] = str(top)
                elif page_size != 100:  # Only set if different from default
                    params["$top"] = str(page_size)

                client_manager = get_client_manager()
                response = await client_manager.make_request("GET", url, headers=headers, params=params)
                if response.status_code == 200:
                    data = self._parse_json_response(response)
                    return {
                        "status": "success",
                        "data": data,
                        "count": len(data),
                    }
                error_text = response.text
                return {
                    "status": "error",
                    "message": f"Failed to list issues: {error_text}",
                }
            except Exception as e:
                return {"status": "error", "message": f"Error listing issues: {str(e)}"}

    async def get_issue(self, issue_id: str) -> Dict[str, Any]:
        """Get details of a specific issue."""
        credentials = self.auth_manager.load_credentials()
        if not credentials:
            return {"status": "error", "message": "Not authenticated"}

        url = f"{credentials.base_url.rstrip('/')}/api/issues/{issue_id}"
        headers = {"Authorization": f"Bearer {credentials.token}"}
        params = {
            "fields": (
                "id,summary,description,state,priority,type,"
                "assignee(login,fullName),project(id,name),created,updated,"
                "tags(name),links(linkType,direction,issues(id,summary)),"
                "customFields(id,name,value(login,fullName,name))"
            )
        }

        try:
            client_manager = get_client_manager()
            response = await client_manager.make_request("GET", url, headers=headers, params=params)
            if response.status_code == 200:
                data = self._parse_json_response(response)
                return {"status": "success", "data": data}
            error_text = response.text
            return {
                "status": "error",
                "message": f"Failed to get issue: {error_text}",
            }
        except Exception as e:
            return {"status": "error", "message": f"Error getting issue: {str(e)}"}

    async def update_issue(
        self,
        issue_id: str,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        state: Optional[str] = None,
        priority: Optional[str] = None,
        assignee: Optional[str] = None,
        issue_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update an existing issue."""
        credentials = self.auth_manager.load_credentials()
        if not credentials:
            return {"status": "error", "message": "Not authenticated"}

        # Separate custom fields from regular fields
        update_data: Dict[str, Any] = {}
        custom_fields = []

        if summary:
            update_data["summary"] = summary
        if description:
            update_data["description"] = description

        # Handle state, priority, type and assignee as custom fields using CustomFieldManager
        if state:
            # Try to get the actual state field name/id for this issue
            state_field_id = await self._get_custom_field_id(issue_id, "State")
            if not state_field_id:
                # Try common alternative state field names
                for field_name in ["Status", "Workflow State", "state"]:
                    state_field_id = await self._get_custom_field_id(issue_id, field_name)
                    if state_field_id:
                        break

            if state_field_id:
                # Create custom field with ID for proper state update - remove name when using ID
                state_field = CustomFieldManager.create_state_field("State", state)
                state_field["id"] = state_field_id
                del state_field["name"]  # Remove name when using ID to avoid conflicts
                custom_fields.append(state_field)
            else:
                # Fallback to name-based state field
                custom_fields.append(CustomFieldManager.create_state_field("State", state))
        if priority:
            custom_fields.append(CustomFieldManager.create_single_enum_field("Priority", priority))
        if issue_type:
            custom_fields.append(CustomFieldManager.create_single_enum_field("Type", issue_type))
        if assignee:
            # For assignee, we need to get the field ID and user ID for proper assignment
            field_id = await self._get_custom_field_id(issue_id, "Assignee")
            if field_id:
                # Get user info to get the user ID
                from .users import UserManager

                user_manager = UserManager(self.auth_manager)
                user_result = await user_manager.get_user(assignee)

                if user_result["status"] == "success":
                    user_data = user_result["data"]
                    user_id = user_data.get("id")
                    # Create custom field with ID for proper assignment
                    user_field = CustomFieldManager.create_single_user_field("Assignee", assignee)
                    user_field["id"] = field_id
                    user_field["value"]["$type"] = "User"
                    user_field["value"]["id"] = user_id
                    del user_field["value"]["login"]  # Remove login when using ID
                    custom_fields.append(user_field)
                else:
                    # Fallback to login-based assignment
                    custom_fields.append(CustomFieldManager.create_single_user_field("Assignee", assignee))
            else:
                # No field ID found, use the fallback approach
                custom_fields.append(CustomFieldManager.create_single_user_field("Assignee", assignee))

        if not update_data and not custom_fields:
            return {"status": "error", "message": "No fields to update"}

        # Add custom fields to update data if present
        if custom_fields:
            update_data["customFields"] = custom_fields

        url = f"{credentials.base_url.rstrip('/')}/api/issues/{issue_id}"
        headers = {
            "Authorization": f"Bearer {credentials.token}",
            "Content-Type": "application/json",
        }

        try:
            client_manager = get_client_manager()
            response = await client_manager.make_request("POST", url, headers=headers, json_data=update_data)
            if response.status_code == 200:
                data = self._parse_json_response(response)
                return {
                    "status": "success",
                    "message": f"Issue '{issue_id}' updated successfully",
                    "data": data,
                }
            error_text = response.text
            return {
                "status": "error",
                "message": f"Failed to update issue: {error_text}",
            }
        except Exception as e:
            return {"status": "error", "message": f"Error updating issue: {str(e)}"}

    async def delete_issue(self, issue_id: str) -> Dict[str, Any]:
        """Delete an issue."""
        credentials = self.auth_manager.load_credentials()
        if not credentials:
            return {"status": "error", "message": "Not authenticated"}

        url = f"{credentials.base_url.rstrip('/')}/api/issues/{issue_id}"
        headers = {"Authorization": f"Bearer {credentials.token}"}

        try:
            client_manager = get_client_manager()
            response = await client_manager.make_request("DELETE", url, headers=headers)
            if response.status_code == 200:
                return {
                    "status": "success",
                    "message": f"Issue '{issue_id}' deleted successfully",
                }
            error_text = response.text
            return {
                "status": "error",
                "message": f"Failed to delete issue: {error_text}",
            }
        except Exception as e:
            return {"status": "error", "message": f"Error deleting issue: {str(e)}"}

    async def search_issues(
        self,
        query: str,
        project_id: Optional[str] = None,
        fields: Optional[str] = None,
        field_profile: Optional[str] = None,
        page_size: int = 100,
        top: Optional[int] = None,  # Legacy parameter for backward compatibility
        after_cursor: Optional[str] = None,
        before_cursor: Optional[str] = None,
        use_pagination: bool = False,
        max_results: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Search issues with advanced query and cursor pagination support."""
        from .utils import paginate_results  # Import here to avoid circular imports

        credentials = self.auth_manager.load_credentials()
        if not credentials:
            return {"status": "error", "message": "Not authenticated"}

        # Handle legacy top parameter
        if top is not None:
            page_size = top
            use_pagination = False

        # Use field selector for optimized field selection
        field_selector = get_field_selector()
        if fields:
            # User provided custom fields
            if field_selector.validate_fields(fields, "issues"):
                selected_fields = fields
            else:
                logger.warning("Invalid field specification, using standard profile", fields=fields)
                selected_fields = field_selector.get_fields("issues", "standard")
        else:
            # Use field profile or default to standard for search
            profile = field_profile or "standard"
            selected_fields = field_selector.get_fields("issues", profile)

        params = {"fields": selected_fields}

        # Build search query
        search_query = query
        if project_id:
            search_query = f"project:{project_id} AND ({query})"

        params["query"] = search_query

        url = f"{credentials.base_url.rstrip('/')}/api/issues"
        headers = {"Authorization": f"Bearer {credentials.token}"}

        try:
            if use_pagination:
                # Use enhanced pagination with cursor support
                result = await paginate_results(
                    endpoint=url,
                    headers=headers,
                    params=params,
                    page_size=page_size,
                    max_results=max_results,
                    after_cursor=after_cursor,
                    before_cursor=before_cursor,
                    use_cursor_pagination=bool(after_cursor or before_cursor),
                )
                return {
                    "status": "success",
                    "data": result["results"],
                    "count": result["total_results"],
                    "pagination": {
                        "has_after": result["has_after"],
                        "has_before": result["has_before"],
                        "after_cursor": result["after_cursor"],
                        "before_cursor": result["before_cursor"],
                    },
                }
            # Single request (legacy behavior)
            if top:
                params["$top"] = str(top)
            elif page_size != 100:  # Only set if different from default
                params["$top"] = str(page_size)

            client_manager = get_client_manager()
            response = await client_manager.make_request("GET", url, headers=headers, params=params)
            if response.status_code == 200:
                data = self._parse_json_response(response)
                return {
                    "status": "success",
                    "data": data,
                    "count": len(data),
                }
            error_text = response.text
            return {
                "status": "error",
                "message": f"Failed to search issues: {error_text}",
            }
        except Exception as e:
            return {"status": "error", "message": f"Error searching issues: {str(e)}"}

    async def _get_custom_field_id(self, issue_id: str, field_name: str) -> Optional[str]:
        """Get the custom field ID for a given field name using CustomFieldManager."""
        credentials = self.auth_manager.load_credentials()
        if not credentials:
            return None

        url = f"{credentials.base_url.rstrip('/')}/api/issues/{issue_id}"
        headers = {"Authorization": f"Bearer {credentials.token}"}
        params = {"fields": "customFields(id,name)"}

        try:
            client_manager = get_client_manager()
            response = await client_manager.make_request("GET", url, headers=headers, params=params)
            if response.status_code == 200:
                data = self._parse_json_response(response)
                custom_fields = data.get("customFields", [])
                return CustomFieldManager.get_field_id(custom_fields, field_name)
        except Exception:
            pass
        return None

    async def assign_issue(self, issue_id: str, assignee: str) -> Dict[str, Any]:
        """Assign an issue to a user."""
        # First try the standard field update
        result = await self.update_issue(issue_id, assignee=assignee)

        # If successful, check if the assignment actually worked
        if result["status"] == "success":
            # Get the issue to verify assignment
            check_result = await self.get_issue(issue_id)
            if check_result["status"] == "success":
                issue_data = check_result["data"]

                # Check if assignee was set at top level
                if issue_data.get("assignee"):
                    return result

                # If not, try to find and use the custom field
                field_id = await self._get_custom_field_id(issue_id, "Assignee")
                if field_id:
                    # Get user info
                    from .users import UserManager

                    user_manager = UserManager(self.auth_manager)
                    user_result = await user_manager.get_user(assignee)

                    if user_result["status"] == "success":
                        user_data = user_result["data"]
                        user_id = user_data.get("id")

                        # Update using custom field
                        credentials = self.auth_manager.load_credentials()
                        url = f"{credentials.base_url.rstrip('/')}/api/issues/{issue_id}"
                        headers = {
                            "Authorization": f"Bearer {credentials.token}",
                            "Content-Type": "application/json",
                        }

                        update_data = {
                            "customFields": [
                                {
                                    "$type": "SingleUserIssueCustomField",
                                    "id": field_id,
                                    "value": {"$type": "User", "id": user_id},
                                }
                            ]
                        }

                        try:
                            client_manager = get_client_manager()
                            response = await client_manager.make_request(
                                "POST", url, headers=headers, json_data=update_data
                            )
                            if response.status_code == 200:
                                return {
                                    "status": "success",
                                    "message": f"Issue '{issue_id}' assigned to '{assignee}' successfully",
                                }
                        except Exception as e:
                            return {"status": "error", "message": f"Error assigning issue: {str(e)}"}

        return result

    async def move_issue(
        self,
        issue_id: str,
        state: Optional[str] = None,
        project_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Move an issue to a different state or project."""
        update_data: Dict[str, Any] = {}
        if state:
            update_data["state"] = state
        if project_id:
            # Moving between projects requires special handling
            return await self._move_issue_to_project(issue_id, project_id)

        if not update_data:
            return {
                "status": "error",
                "message": "No target state or project specified",
            }

        return await self.update_issue(issue_id, **update_data)

    async def _resolve_project_id(self, project_id_or_short_name: str) -> Optional[str]:
        """Resolve project short name to internal ID."""
        from .projects import ProjectManager

        project_manager = ProjectManager(self.auth_manager)
        result = await project_manager.get_project(project_id_or_short_name, fields="id,shortName")

        if result["status"] == "success":
            return result["data"]["id"]
        return None

    async def _move_issue_to_project(self, issue_id: str, project_id: str) -> Dict[str, Any]:
        """Move an issue to a different project."""
        credentials = self.auth_manager.load_credentials()
        if not credentials:
            return {"status": "error", "message": "Not authenticated"}

        # First try to resolve the project short name to internal ID
        resolved_project_id = await self._resolve_project_id(project_id)
        if resolved_project_id is None:
            return {
                "status": "error",
                "message": f"Project '{project_id}' not found. Please check the project short name or ID.",
            }

        url = f"{credentials.base_url.rstrip('/')}/api/issues/{issue_id}"
        headers = {
            "Authorization": f"Bearer {credentials.token}",
            "Content-Type": "application/json",
        }
        update_data = {"project": {"id": resolved_project_id}}

        try:
            client_manager = get_client_manager()
            response = await client_manager.make_request("POST", url, headers=headers, json_data=update_data)
            if response.status_code == 200:
                return {
                    "status": "success",
                    "message": (f"Issue '{issue_id}' moved to project '{project_id}' successfully"),
                }
            error_text = response.text
            return {
                "status": "error",
                "message": f"Failed to move issue: {error_text}",
            }
        except Exception as e:
            return {"status": "error", "message": f"Error moving issue: {str(e)}"}

    async def find_tag_by_name(self, tag_name: str) -> Dict[str, Any]:
        """Find a tag by name. Returns tag data with ID if found."""
        credentials = self.auth_manager.load_credentials()
        if not credentials:
            return {"status": "error", "message": "Not authenticated"}

        url = f"{credentials.base_url.rstrip('/')}/api/tags"
        headers = {
            "Authorization": f"Bearer {credentials.token}",
            "Content-Type": "application/json",
        }
        params = {"fields": "id,name", "query": tag_name}

        try:
            client_manager = get_client_manager()
            response = await client_manager.make_request("GET", url, headers=headers, params=params)
            if response.status_code == 200:
                tags = response.json()
                # Look for exact name match
                for tag in tags:
                    if tag.get("name") == tag_name:
                        return {"status": "success", "tag": tag, "message": f"Found existing tag '{tag_name}'"}
                return {"status": "not_found", "message": f"Tag '{tag_name}' not found"}
            return {"status": "error", "message": f"Failed to search tags: {response.text}"}
        except Exception as e:
            return {"status": "error", "message": f"Error searching for tag: {str(e)}"}

    async def create_tag(self, tag_name: str) -> Dict[str, Any]:
        """Create a new tag. Returns tag data with ID if successful."""
        credentials = self.auth_manager.load_credentials()
        if not credentials:
            return {"status": "error", "message": "Not authenticated"}

        url = f"{credentials.base_url.rstrip('/')}/api/tags"
        headers = {
            "Authorization": f"Bearer {credentials.token}",
            "Content-Type": "application/json",
        }
        tag_data = {"name": tag_name}
        params = {"fields": "id,name"}

        try:
            client_manager = get_client_manager()
            response = await client_manager.make_request(
                "POST", url, headers=headers, json_data=tag_data, params=params
            )
            if response.status_code == 200:
                tag = response.json()
                return {"status": "success", "tag": tag, "message": f"Created new tag '{tag_name}'"}
            return {"status": "error", "message": f"Failed to create tag: {response.text}"}
        except Exception as e:
            return {"status": "error", "message": f"Error creating tag: {str(e)}"}

    async def get_or_create_tag(self, tag_name: str) -> Dict[str, Any]:
        """Get existing tag or create new one. Returns tag data with ID."""
        # First try to find existing tag
        find_result = await self.find_tag_by_name(tag_name)
        if find_result["status"] == "success":
            return find_result
        if find_result["status"] == "not_found":
            # Tag doesn't exist, try to create it
            return await self.create_tag(tag_name)
        # Error occurred during search
        return find_result

    async def add_tag(self, issue_id: str, tag: str) -> Dict[str, Any]:
        """Add a tag to an issue."""
        credentials = self.auth_manager.load_credentials()
        if not credentials:
            return {"status": "error", "message": "Not authenticated"}

        # First get or create the tag to ensure we have the tag ID
        tag_result = await self.get_or_create_tag(tag)
        if tag_result["status"] != "success":
            return tag_result

        tag_id = tag_result["tag"]["id"]
        was_created = "Created" in tag_result["message"]

        url = f"{credentials.base_url.rstrip('/')}/api/issues/{issue_id}/tags"
        headers = {
            "Authorization": f"Bearer {credentials.token}",
            "Content-Type": "application/json",
        }
        tag_data = {"id": tag_id}

        try:
            client_manager = get_client_manager()
            response = await client_manager.make_request("POST", url, headers=headers, json_data=tag_data)
            if response.status_code == 200:
                creation_note = " (created new tag)" if was_created else ""
                return {
                    "status": "success",
                    "message": (f"Tag '{tag}' added to issue '{issue_id}' successfully{creation_note}"),
                }
            error_text = response.text
            return {
                "status": "error",
                "message": f"Failed to add tag to issue: {error_text}",
            }
        except Exception as e:
            return {"status": "error", "message": f"Error adding tag to issue: {str(e)}"}

    async def remove_tag(self, issue_id: str, tag: str) -> Dict[str, Any]:
        """Remove a tag from an issue."""
        credentials = self.auth_manager.load_credentials()
        if not credentials:
            return {"status": "error", "message": "Not authenticated"}

        # First find the tag to get its ID
        tag_result = await self.find_tag_by_name(tag)
        if tag_result["status"] == "not_found":
            return {"status": "error", "message": f"Tag '{tag}' not found"}
        if tag_result["status"] != "success":
            return tag_result

        tag_id = tag_result["tag"]["id"]

        url = f"{credentials.base_url.rstrip('/')}/api/issues/{issue_id}/tags/{tag_id}"
        headers = {"Authorization": f"Bearer {credentials.token}"}

        try:
            client_manager = get_client_manager()
            response = await client_manager.make_request("DELETE", url, headers=headers)
            if response.status_code == 200:
                return {
                    "status": "success",
                    "message": (f"Tag '{tag}' removed from issue '{issue_id}' successfully"),
                }
            error_text = response.text
            return {
                "status": "error",
                "message": f"Failed to remove tag: {error_text}",
            }
        except Exception as e:
            return {"status": "error", "message": f"Error removing tag: {str(e)}"}

    async def list_tags(self, issue_id: str) -> Dict[str, Any]:
        """List all tags for an issue."""
        credentials = self.auth_manager.load_credentials()
        if not credentials:
            return {"status": "error", "message": "Not authenticated"}

        url = f"{credentials.base_url.rstrip('/')}/api/issues/{issue_id}"
        headers = {"Authorization": f"Bearer {credentials.token}"}
        params = {"fields": "tags(name)"}

        try:
            client_manager = get_client_manager()
            response = await client_manager.make_request("GET", url, headers=headers, params=params)
            if response.status_code == 200:
                data = self._parse_json_response(response)
                tags = data.get("tags", [])
                return {"status": "success", "data": tags}
            error_text = response.text
            return {
                "status": "error",
                "message": f"Failed to list tags: {error_text}",
            }
        except Exception as e:
            return {"status": "error", "message": f"Error listing tags: {str(e)}"}

    # Comments functionality
    async def add_comment(self, issue_id: str, text: str) -> Dict[str, Any]:
        """Add a comment to an issue."""
        credentials = self.auth_manager.load_credentials()
        if not credentials:
            return {"status": "error", "message": "Not authenticated"}

        url = f"{credentials.base_url.rstrip('/')}/api/issues/{issue_id}/comments"
        headers = {
            "Authorization": f"Bearer {credentials.token}",
            "Content-Type": "application/json",
        }
        comment_data = {"text": text}

        try:
            client_manager = get_client_manager()
            response = await client_manager.make_request("POST", url, headers=headers, json_data=comment_data)
            if response.status_code == 200:
                return {
                    "status": "success",
                    "message": (f"Comment added to issue '{issue_id}' successfully"),
                }
            error_text = response.text
            return {
                "status": "error",
                "message": f"Failed to add comment: {error_text}",
            }
        except Exception as e:
            return {"status": "error", "message": f"Error adding comment: {str(e)}"}

    async def list_comments(self, issue_id: str) -> Dict[str, Any]:
        """List all comments for an issue."""
        credentials = self.auth_manager.load_credentials()
        if not credentials:
            return {"status": "error", "message": "Not authenticated"}

        url = f"{credentials.base_url.rstrip('/')}/api/issues/{issue_id}/comments"
        headers = {"Authorization": f"Bearer {credentials.token}"}
        params = {"fields": "id,text,author(login,fullName),created,updated"}

        try:
            client_manager = get_client_manager()
            response = await client_manager.make_request("GET", url, headers=headers, params=params)
            if response.status_code == 200:
                data = self._parse_json_response(response)
                return {"status": "success", "data": data}
            error_text = response.text
            return {
                "status": "error",
                "message": f"Failed to list comments: {error_text}",
            }
        except Exception as e:
            return {"status": "error", "message": f"Error listing comments: {str(e)}"}

    async def update_comment(self, issue_id: str, comment_id: str, text: str) -> Dict[str, Any]:
        """Update an existing comment."""
        credentials = self.auth_manager.load_credentials()
        if not credentials:
            return {"status": "error", "message": "Not authenticated"}

        url = f"{credentials.base_url.rstrip('/')}/api/issues/{issue_id}/comments/{comment_id}"
        headers = {
            "Authorization": f"Bearer {credentials.token}",
            "Content-Type": "application/json",
        }
        comment_data = {"text": text}

        try:
            client_manager = get_client_manager()
            response = await client_manager.make_request("POST", url, headers=headers, json_data=comment_data)
            if response.status_code == 200:
                return {
                    "status": "success",
                    "message": f"Comment '{comment_id}' updated successfully",
                }
            error_text = response.text
            return {
                "status": "error",
                "message": f"Failed to update comment: {error_text}",
            }
        except Exception as e:
            return {"status": "error", "message": f"Error updating comment: {str(e)}"}

    async def delete_comment(self, issue_id: str, comment_id: str) -> Dict[str, Any]:
        """Delete a comment from an issue."""
        credentials = self.auth_manager.load_credentials()
        if not credentials:
            return {"status": "error", "message": "Not authenticated"}

        url = f"{credentials.base_url.rstrip('/')}/api/issues/{issue_id}/comments/{comment_id}"
        headers = {"Authorization": f"Bearer {credentials.token}"}

        try:
            client_manager = get_client_manager()
            response = await client_manager.make_request("DELETE", url, headers=headers)
            if response.status_code == 200:
                return {
                    "status": "success",
                    "message": f"Comment '{comment_id}' deleted successfully",
                }
            error_text = response.text
            return {
                "status": "error",
                "message": f"Failed to delete comment: {error_text}",
            }
        except Exception as e:
            return {"status": "error", "message": f"Error deleting comment: {str(e)}"}

    # Attachments functionality
    async def upload_attachment(self, issue_id: str, file_path: str) -> Dict[str, Any]:
        """Upload an attachment to an issue."""
        credentials = self.auth_manager.load_credentials()
        if not credentials:
            return {"status": "error", "message": "Not authenticated"}

        url = f"{credentials.base_url.rstrip('/')}/api/issues/{issue_id}/attachments"
        headers = {"Authorization": f"Bearer {credentials.token}"}

        try:
            with open(file_path, "rb") as file:
                files = {"file": file}
                client_manager = get_client_manager()
                async with client_manager.get_client() as client:
                    response = await client.post(url, files=files, headers=headers)
                    if response.status_code == 200:
                        return {
                            "status": "success",
                            "message": (f"File '{file_path}' uploaded to issue '{issue_id}' successfully"),
                        }
                    error_text = response.text
                    return {
                        "status": "error",
                        "message": f"Failed to upload attachment: {error_text}",
                    }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error uploading attachment: {str(e)}",
            }

    async def list_attachments(self, issue_id: str) -> Dict[str, Any]:
        """List all attachments for an issue."""
        credentials = self.auth_manager.load_credentials()
        if not credentials:
            return {"status": "error", "message": "Not authenticated"}

        url = f"{credentials.base_url.rstrip('/')}/api/issues/{issue_id}/attachments"
        headers = {"Authorization": f"Bearer {credentials.token}"}
        params = {"fields": "id,name,size,mimeType,author(login,fullName),created"}

        try:
            client_manager = get_client_manager()
            response = await client_manager.make_request("GET", url, headers=headers, params=params)
            if response.status_code == 200:
                data = self._parse_json_response(response)
                return {"status": "success", "data": data}
            error_text = response.text
            return {
                "status": "error",
                "message": f"Failed to list attachments: {error_text}",
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error listing attachments: {str(e)}",
            }

    async def download_attachment(self, issue_id: str, attachment_id: str, output_path: str) -> Dict[str, Any]:
        """Download an attachment from an issue."""
        credentials = self.auth_manager.load_credentials()
        if not credentials:
            return {"status": "error", "message": "Not authenticated"}

        # Step 1: Get attachment metadata including download URL
        metadata_url = f"{credentials.base_url.rstrip('/')}/api/issues/{issue_id}/attachments/{attachment_id}"
        headers = {"Authorization": f"Bearer {credentials.token}"}
        params = {"fields": "id,name,url"}

        try:
            client_manager = get_client_manager()

            # Get attachment metadata with URL
            metadata_response = await client_manager.make_request("GET", metadata_url, headers=headers, params=params)
            if metadata_response.status_code != 200:
                error_text = metadata_response.text
                return {
                    "status": "error",
                    "message": f"Failed to get attachment metadata: {error_text}",
                }

            metadata = self._parse_json_response(metadata_response)
            download_url = metadata.get("url")

            if not download_url:
                return {
                    "status": "error",
                    "message": "No download URL found in attachment metadata",
                }

            # Step 2: Download the file content using the URL with signature
            # The URL already includes the sign parameter, so no Authorization header needed
            full_download_url = f"{credentials.base_url.rstrip('/')}{download_url}"
            download_response = await client_manager.make_request("GET", full_download_url)

            if download_response.status_code == 200:
                with open(output_path, "wb") as file:
                    file.write(download_response.content)
                return {
                    "status": "success",
                    "message": (f"Attachment downloaded to '{output_path}' successfully"),
                }
            error_text = download_response.text
            return {
                "status": "error",
                "message": f"Failed to download attachment: {error_text}",
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error downloading attachment: {str(e)}",
            }

    async def delete_attachment(self, issue_id: str, attachment_id: str) -> Dict[str, Any]:
        """Delete an attachment from an issue."""
        credentials = self.auth_manager.load_credentials()
        if not credentials:
            return {"status": "error", "message": "Not authenticated"}

        url = f"{credentials.base_url.rstrip('/')}/api/issues/{issue_id}/attachments/{attachment_id}"
        headers = {"Authorization": f"Bearer {credentials.token}"}

        try:
            client_manager = get_client_manager()
            response = await client_manager.make_request("DELETE", url, headers=headers)
            if response.status_code == 200:
                return {
                    "status": "success",
                    "message": f"Attachment '{attachment_id}' deleted successfully",
                }
            error_text = response.text
            return {
                "status": "error",
                "message": f"Failed to delete attachment: {error_text}",
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error deleting attachment: {str(e)}",
            }

    # Links functionality
    async def _resolve_link_type(self, link_type_name: str) -> Optional[Dict[str, Any]]:
        """Resolve a link type name to its ID and direction information."""
        credentials = self.auth_manager.load_credentials()
        if not credentials:
            return None

        url = f"{credentials.base_url.rstrip('/')}/api/issueLinkTypes"
        headers = {"Authorization": f"Bearer {credentials.token}"}
        params = {"fields": "id,name,sourceToTarget,targetToSource,directed"}

        try:
            client_manager = get_client_manager()
            response = await client_manager.make_request("GET", url, headers=headers, params=params)
            if response.status_code == 200:
                link_types = self._parse_json_response(response)

                # Try to find exact match first
                for link_type in link_types:
                    if link_type.get("name", "").lower() == link_type_name.lower():
                        return link_type
                    # Also check sourceToTarget and targetToSource names
                    if link_type.get("sourceToTarget", "").lower() == link_type_name.lower():
                        return {**link_type, "direction": "outward"}
                    if link_type.get("targetToSource", "").lower() == link_type_name.lower():
                        return {**link_type, "direction": "inward"}

                return None
            logger.error("Failed to fetch link types", status_code=response.status_code)
            return None
        except Exception as e:
            logger.error("Error fetching link types", error=str(e))
            return None

    async def _get_issue_database_id(self, issue_id: str) -> Optional[str]:
        """Get the database ID for an issue given its readable ID."""
        credentials = self.auth_manager.load_credentials()
        if not credentials:
            return None

        url = f"{credentials.base_url.rstrip('/')}/api/issues/{issue_id}"
        headers = {"Authorization": f"Bearer {credentials.token}"}
        params = {"fields": "id"}

        try:
            client_manager = get_client_manager()
            response = await client_manager.make_request("GET", url, headers=headers, params=params)
            if response.status_code == 200:
                data = self._parse_json_response(response)
                return data.get("id")
            logger.error("Failed to fetch issue ID", issue_id=issue_id, status_code=response.status_code)
            return None
        except Exception as e:
            logger.error("Error fetching issue ID", issue_id=issue_id, error=str(e))
            return None

    async def create_link(self, source_issue_id: str, target_issue_id: str, link_type: str) -> Dict[str, Any]:
        """Create a link between two issues."""
        credentials = self.auth_manager.load_credentials()
        if not credentials:
            return {"status": "error", "message": "Not authenticated"}

        # First resolve the link type name to ID
        link_type_info = await self._resolve_link_type(link_type)
        if not link_type_info:
            return {"status": "error", "message": f"Unknown link type: '{link_type}'"}

        # Get the database ID for the target issue
        target_db_id = await self._get_issue_database_id(target_issue_id)
        if not target_db_id:
            return {"status": "error", "message": f"Could not find issue: '{target_issue_id}'"}

        link_type_id = link_type_info.get("id")
        is_directed = link_type_info.get("directed", False)

        # Determine the link ID to use in the URL
        # For directed links, we need to append 's' for outward or 't' for inward
        if is_directed:
            # Default to outward direction unless explicitly set
            direction = link_type_info.get("direction", "outward")
            if direction == "inward":
                link_id = f"{link_type_id}t"
            else:
                link_id = f"{link_type_id}s"
        else:
            link_id = link_type_id

        url = f"{credentials.base_url.rstrip('/')}/api/issues/{source_issue_id}/links/{link_id}/issues"
        headers = {
            "Authorization": f"Bearer {credentials.token}",
            "Content-Type": "application/json",
        }
        # Only send the target issue database ID in the body
        link_data = {"id": target_db_id}

        try:
            client_manager = get_client_manager()
            response = await client_manager.make_request("POST", url, headers=headers, json_data=link_data)
            if response.status_code in [200, 201]:
                return {
                    "status": "success",
                    "message": (f"Link created between '{source_issue_id}' and '{target_issue_id}' successfully"),
                }
            error_text = response.text
            return {
                "status": "error",
                "message": f"Failed to create link: {error_text}",
            }
        except Exception as e:
            return {"status": "error", "message": f"Error creating link: {str(e)}"}

    async def list_links(self, issue_id: str) -> Dict[str, Any]:
        """List all links for an issue."""
        credentials = self.auth_manager.load_credentials()
        if not credentials:
            return {"status": "error", "message": "Not authenticated"}

        url = f"{credentials.base_url.rstrip('/')}/api/issues/{issue_id}"
        headers = {"Authorization": f"Bearer {credentials.token}"}
        params = {"fields": "links(linkType(name),direction,issues(id,summary,numberInProject,project(shortName)))"}

        try:
            client_manager = get_client_manager()
            response = await client_manager.make_request("GET", url, headers=headers, params=params)
            if response.status_code == 200:
                data = self._parse_json_response(response)
                links = data.get("links", [])
                return {"status": "success", "data": links}
            error_text = response.text
            return {
                "status": "error",
                "message": f"Failed to list links: {error_text}",
            }
        except Exception as e:
            return {"status": "error", "message": f"Error listing links: {str(e)}"}

    async def delete_link(self, source_issue_id: str, link_id: str) -> Dict[str, Any]:
        """Delete a link between issues."""
        credentials = self.auth_manager.load_credentials()
        if not credentials:
            return {"status": "error", "message": "Not authenticated"}

        url = f"{credentials.base_url.rstrip('/')}/api/issues/{source_issue_id}/links/{link_id}"
        headers = {"Authorization": f"Bearer {credentials.token}"}

        try:
            client_manager = get_client_manager()
            response = await client_manager.make_request("DELETE", url, headers=headers)
            if response.status_code == 200:
                return {
                    "status": "success",
                    "message": f"Link '{link_id}' deleted successfully",
                }
            error_text = response.text
            return {
                "status": "error",
                "message": f"Failed to delete link: {error_text}",
            }
        except Exception as e:
            return {"status": "error", "message": f"Error deleting link: {str(e)}"}

    async def list_link_types(self) -> Dict[str, Any]:
        """List all available link types."""
        credentials = self.auth_manager.load_credentials()
        if not credentials:
            return {"status": "error", "message": "Not authenticated"}

        url = f"{credentials.base_url.rstrip('/')}/api/issueLinkTypes"
        headers = {"Authorization": f"Bearer {credentials.token}"}
        params = {"fields": "name,sourceToTarget,targetToSource"}

        try:
            client_manager = get_client_manager()
            response = await client_manager.make_request("GET", url, headers=headers, params=params)
            if response.status_code == 200:
                data = self._parse_json_response(response)
                return {"status": "success", "data": data}
            error_text = response.text
            return {
                "status": "error",
                "message": f"Failed to list link types: {error_text}",
            }
        except Exception as e:
            return {"status": "error", "message": f"Error listing link types: {str(e)}"}

    def _get_field_with_fallback(self, issue: Dict[str, Any], field_name: str, custom_field_names: List[str]) -> str:
        """Get field value with fallback to custom fields using CustomFieldManager.

        Args:
            issue: The issue dictionary
            field_name: The built-in field name to check first (e.g., 'state', 'priority', 'type')
            custom_field_names: List of custom field names to try as fallback

        Returns:
            The field value or "N/A" if not found
        """
        # Check built-in field first
        field_value = issue.get(field_name.lower(), {})
        if field_value and isinstance(field_value, dict):
            name = field_value.get("name")
            if name:
                return name
        elif isinstance(field_value, str) and field_value:
            return field_value

        # Fallback to custom fields using CustomFieldManager
        custom_fields = issue.get("customFields", [])
        for custom_name in custom_field_names:
            result = CustomFieldManager.extract_field_value(custom_fields, custom_name)
            if result is not None and str(result) != "N/A":
                return str(result)

        return "N/A"

    # Display methods
    def display_issues_table(self, issues: List[Dict[str, Any]]) -> None:
        """Display issues in a formatted table."""
        if not issues:
            self.console.print("No issues found.", style="yellow")
            return

        table = Table(title="Issues")
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Summary", style="blue")
        table.add_column("State", style="green")
        table.add_column("Priority", style="red")
        table.add_column("Type", style="magenta")
        table.add_column("Assignee", style="yellow")
        table.add_column("Project", style="white")

        for issue in issues:
            # Format issue ID to show user-friendly project format
            issue_id = issue.get("id", "N/A")
            project = issue.get("project", {})
            project_short_name = project.get("shortName") if project else None
            issue_number = issue.get("numberInProject") if issue.get("numberInProject") else None

            # Create user-friendly ID format (e.g., "DATA-5" instead of "2-57152")
            if project_short_name and issue_number:
                formatted_id = f"{project_short_name}-{issue_number}"
            else:
                formatted_id = issue_id

            # Handle assignee - could be in top-level field or custom fields
            assignee = issue.get("assignee", {})
            if assignee and (assignee.get("fullName") or assignee.get("login")):
                assignee_name = assignee.get("fullName") or assignee.get("login", "Unassigned")
            else:
                # Check custom fields for Assignee
                custom_assignee = self._get_custom_field_value(issue, "Assignee")
                assignee_name = custom_assignee or "Unassigned"

            project_name = project.get("name", "N/A") if project else "N/A"

            # Handle state field - could be string, object with name, or in custom fields
            state = issue.get("state")
            if isinstance(state, dict):
                state_name = state.get("name", "N/A")
            elif isinstance(state, str):
                state_name = state
            else:
                # Check custom fields for State or Stage (different YouTrack configs use different names)
                state_name = (
                    self._get_custom_field_value(issue, "State")
                    or self._get_custom_field_value(issue, "Stage")
                    or "N/A"
                )

            # Handle priority field - could be string, object with name, or in custom fields
            priority = issue.get("priority")
            if isinstance(priority, dict):
                priority_name = priority.get("name", "N/A")
            elif isinstance(priority, str):
                priority_name = priority
            else:
                # Check custom fields for Priority
                priority_name = self._get_custom_field_value(issue, "Priority") or "N/A"

            # Handle type field - could be string, object with name, or in custom fields
            issue_type = issue.get("type")
            if isinstance(issue_type, dict):
                type_name = issue_type.get("name", "N/A")
            elif isinstance(issue_type, str):
                type_name = issue_type
            else:
                # Check custom fields for Type
                type_name = self._get_custom_field_value(issue, "Type") or "N/A"

            summary = issue.get("summary", "N/A")
            truncated_summary = summary[:50] + ("..." if len(summary) > 50 else "")

            table.add_row(
                formatted_id,
                truncated_summary,
                state_name,
                priority_name,
                type_name,
                assignee_name,
                project_name,
            )

        self.console.print(table)

    def display_issues_table_paginated(
        self, issues: List[Dict[str, Any]], page_size: int = 50, show_all: bool = False, start_page: int = 1
    ) -> None:
        """Display issues in a paginated table format.

        Args:
            issues: List of issues to display
            page_size: Number of issues per page (default: 50)
            show_all: If True, display all issues without pagination
            start_page: Page number to start displaying from
        """
        if not issues:
            self.console.print("No issues found.", style="yellow")
            return

        def build_issues_table(issue_subset: List[Dict[str, Any]]) -> Table:
            """Build a Rich table for the given subset of issues."""
            table = Table(title="Issues")
            table.add_column("ID", style="cyan", no_wrap=True)
            table.add_column("Summary", style="blue")
            table.add_column("State", style="green")
            table.add_column("Priority", style="red")
            table.add_column("Type", style="magenta")
            table.add_column("Assignee", style="yellow")
            table.add_column("Project", style="white")

            for issue in issue_subset:
                # Format issue ID to show user-friendly project format
                issue_id = issue.get("id", "N/A")
                project = issue.get("project", {})
                project_short_name = project.get("shortName") if project else None
                issue_number = issue.get("numberInProject") if issue.get("numberInProject") else None

                # Create user-friendly ID format (e.g., "DATA-5" instead of "2-57152")
                if project_short_name and issue_number:
                    formatted_id = f"{project_short_name}-{issue_number}"
                else:
                    formatted_id = issue_id

                # Handle assignee - could be in top-level field or custom fields
                assignee = issue.get("assignee", {})
                if assignee and (assignee.get("fullName") or assignee.get("login")):
                    assignee_name = assignee.get("fullName") or assignee.get("login", "Unassigned")
                else:
                    # Check custom fields for Assignee
                    custom_assignee = self._get_custom_field_value(issue, "Assignee")
                    assignee_name = custom_assignee or "Unassigned"

                project_name = project.get("name", "N/A") if project else "N/A"

                # Handle state field - could be string, object with name, or in custom fields
                state = issue.get("state")
                if isinstance(state, dict):
                    state_name = state.get("name", "N/A")
                elif isinstance(state, str):
                    state_name = state
                else:
                    # Check custom fields for State or Stage (different YouTrack configs use different names)
                    state_name = (
                        self._get_custom_field_value(issue, "State")
                        or self._get_custom_field_value(issue, "Stage")
                        or "N/A"
                    )

                # Handle priority field - could be string, object with name, or in custom fields
                priority = issue.get("priority")
                if isinstance(priority, dict):
                    priority_name = priority.get("name", "N/A")
                elif isinstance(priority, str):
                    priority_name = priority
                else:
                    # Check custom fields for Priority
                    priority_name = self._get_custom_field_value(issue, "Priority") or "N/A"

                # Handle type field - could be string, object with name, or in custom fields
                issue_type = issue.get("type")
                if isinstance(issue_type, dict):
                    type_name = issue_type.get("name", "N/A")
                elif isinstance(issue_type, str):
                    type_name = issue_type
                else:
                    # Check custom fields for Type
                    type_name = self._get_custom_field_value(issue, "Type") or "N/A"

                summary = issue.get("summary", "N/A")
                truncated_summary = summary[:50] + ("..." if len(summary) > 50 else "")

                table.add_row(
                    formatted_id,
                    truncated_summary,
                    state_name,
                    priority_name,
                    type_name,
                    assignee_name,
                    project_name,
                )

            return table

        # Use pagination display
        paginated_display = create_paginated_display(self.console, page_size)
        paginated_display.display_paginated_table(
            issues, build_issues_table, "Issues", show_all=show_all, start_page=start_page
        )

    def display_issue_details(self, issue: Dict[str, Any], format_type: str = "table") -> None:
        """Display detailed information about a single issue.

        Args:
            issue: Issue data dictionary
            format_type: Display format - 'table' (default) or 'panel'
        """
        if format_type == "panel":
            self._display_issue_details_panels(issue)
        else:
            self._display_issue_details_traditional(issue)

    def _display_issue_details_traditional(self, issue: Dict[str, Any]) -> None:
        """Display issue details in Rich table format."""
        issue_id = issue.get("id", "N/A")

        table = Table(title=f"Issue Details: {issue_id}")
        table.add_column("Field", style="cyan", no_wrap=True)
        table.add_column("Value", style="blue")

        # Basic information
        table.add_row("ID", issue_id)

        summary = issue.get("summary", "N/A")
        table.add_row("Summary", summary)

        # Description if present
        if issue.get("description"):
            description = issue.get("description", "N/A")
            # Truncate long descriptions for table display
            if len(description) > 100:
                description = description[:100] + "..."
            table.add_row("Description", description)

        # State with fallback to custom fields
        state_name = self._get_field_with_fallback(issue, "state", ["State", "Stage"])
        table.add_row("State", state_name)

        # Priority with fallback to custom fields
        priority_name = self._get_field_with_fallback(issue, "priority", ["Priority"])
        table.add_row("Priority", priority_name)

        # Type with fallback to custom fields
        type_name = self._get_field_with_fallback(issue, "type", ["Type", "Issue Type"])
        table.add_row("Type", type_name)

        # Assignee
        assignee_name = self._get_assignee_name(issue)
        table.add_row("Assignee", assignee_name)

        # Project
        project = issue.get("project", {})
        project_name = project.get("name", "N/A") if project else "N/A"
        table.add_row("Project", project_name)

        # Timestamps
        table.add_row("Created", format_timestamp(issue.get("created")))
        table.add_row("Updated", format_timestamp(issue.get("updated")))

        # Tags if any
        tags = issue.get("tags", [])
        if tags:
            tag_names = [tag.get("name", "") for tag in tags]
            table.add_row("Tags", ", ".join(tag_names))

        self.console.print(table)

    def _display_issue_details_panels(self, issue: Dict[str, Any]) -> None:
        """Display issue details using Rich panels for enhanced presentation."""
        issue_id = issue.get("id", "N/A")

        # Create a panel group for organized display
        panel_group = PanelGroup(title=f"Issue Details: {issue_id}")

        # Add overview panel
        overview_panel = create_issue_overview_panel(issue)
        panel_group.add_panel(overview_panel)

        # Add details panel
        details_panel = create_issue_details_panel(issue)
        panel_group.add_panel(details_panel)

        # Add custom fields panel if present
        custom_fields = issue.get("customFields", [])
        if custom_fields:
            custom_fields_panel = create_custom_fields_panel(custom_fields)
            panel_group.add_panel(custom_fields_panel)

        # Add tags panel if present
        tags = issue.get("tags", [])
        if tags:
            tag_names = [tag.get("name", "") for tag in tags]
            panel_group.add_details_panel(
                title="Tags",
                data={"Tags": ", ".join(tag_names)},
            )

        # Display all panels
        panel_group.display()

    def display_comments_table(self, comments: List[Dict[str, Any]]) -> None:
        """Display comments in a formatted table."""
        if not comments:
            self.console.print("No comments found.", style="yellow")
            return

        table = Table(title="Comments")
        table.add_column("ID", style="cyan")
        table.add_column("Author", style="green")
        table.add_column("Text", style="blue")
        table.add_column("Created", style="yellow")

        for comment in comments:
            author = comment.get("author", {})
            author_name = author.get("fullName", "N/A") if author else "N/A"

            text = comment.get("text", "N/A")
            truncated_text = text[:100] + ("..." if len(text) > 100 else "")

            # Format timestamp from epoch milliseconds to human-readable format
            created = comment.get("created", "N/A")
            if isinstance(created, (int, str)) and created != "N/A":
                try:
                    # Convert milliseconds to seconds
                    timestamp = int(created) / 1000
                    dt = datetime.fromtimestamp(timestamp)
                    formatted_date = dt.strftime("%b %d, %Y %H:%M")
                except (ValueError, TypeError):
                    formatted_date = str(created)
            else:
                formatted_date = str(created)

            table.add_row(
                str(comment.get("id", "N/A")),
                author_name,
                truncated_text,
                formatted_date,
            )

        self.console.print(table)

    def display_attachments_table(self, attachments: List[Dict[str, Any]]) -> None:
        """Display attachments in a formatted table."""
        if not attachments:
            self.console.print("No attachments found.", style="yellow")
            return

        table = Table(title="Attachments")
        table.add_column("Name", style="green")
        table.add_column("Size", style="blue")
        table.add_column("Type", style="yellow")
        table.add_column("Author", style="magenta")
        table.add_column("ID", style="cyan")

        for attachment in attachments:
            author = attachment.get("author", {})
            author_name = author.get("fullName", "N/A") if author else "N/A"

            # For attachments, use filename as primary identifier since it's more user-friendly
            # Move internal ID to last column for reference when needed
            table.add_row(
                attachment.get("name", "N/A"),
                str(attachment.get("size", "N/A")),
                attachment.get("mimeType", "N/A"),
                author_name,
                attachment.get("id", "N/A"),
            )

        self.console.print(table)

    def display_links_table(self, links: List[Dict[str, Any]]) -> None:
        """Display issue links in a formatted table."""
        if not links:
            self.console.print("No links found.", style="yellow")
            return

        table = Table(title="Issue Links")
        table.add_column("Link Type", style="cyan")
        table.add_column("Direction", style="green")
        table.add_column("Related Issues", style="blue")

        for link in links:
            link_type = link.get("linkType", {})
            type_name = link_type.get("name", "N/A") if link_type else "N/A"

            direction = link.get("direction", "N/A")

            issues = link.get("issues", [])
            issue_summaries = []
            for issue in issues:
                # Format issue ID to show user-friendly project format
                issue_id = issue.get("id", "N/A")
                project = issue.get("project", {})
                project_short_name = project.get("shortName") if project else None
                issue_number = issue.get("numberInProject") if issue.get("numberInProject") else None

                # Create user-friendly ID format (e.g., "FPU-5" instead of "3-2")
                if project_short_name and issue_number:
                    formatted_id = f"{project_short_name}-{issue_number}"
                else:
                    formatted_id = issue_id

                issue_summary = issue.get("summary", "N/A")
                issue_summaries.append(f"{formatted_id}: {issue_summary[:30]}")

            related_issues = "\n".join(issue_summaries) if issue_summaries else "N/A"

            table.add_row(type_name, direction, related_issues)

        self.console.print(table)

    def display_link_types_table(self, link_types: List[Dict[str, Any]]) -> None:
        """Display available link types in a formatted table."""
        if not link_types:
            self.console.print("No link types found.", style="yellow")
            return

        table = Table(title="Available Link Types")
        table.add_column("Name", style="cyan")
        table.add_column("Source to Target", style="green")
        table.add_column("Target to Source", style="blue")

        for link_type in link_types:
            table.add_row(
                link_type.get("name", "N/A"),
                link_type.get("sourceToTarget", "N/A"),
                link_type.get("targetToSource", "N/A"),
            )

        self.console.print(table)
