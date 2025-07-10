"""Issue management for YouTrack CLI."""

from typing import Any, Optional

import httpx
from rich.console import Console
from rich.table import Table

from .auth import AuthManager
from .client import get_client_manager
from .logging import get_logger
from .progress import get_progress_manager

__all__ = ["IssueManager"]

logger = get_logger(__name__)


class IssueManager:
    """Manages YouTrack issues operations."""

    def __init__(self, auth_manager: AuthManager):
        self.auth_manager = auth_manager
        self.console = Console()

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

    def _get_custom_field_value(self, issue: dict[str, Any], field_name: str) -> Optional[str]:
        """Extract value from custom fields by field name."""
        custom_fields = issue.get("customFields", [])
        if not isinstance(custom_fields, list):
            return None

        for field in custom_fields:
            if isinstance(field, dict) and field.get("name") == field_name:
                value = field.get("value")
                if isinstance(value, dict):
                    # Handle single-value bundle fields (like enum fields)
                    return value.get("name") or value.get("id")
                elif isinstance(value, list):
                    # Handle multi-value fields
                    if value and isinstance(value[0], dict):
                        return ", ".join(v.get("name", str(v)) for v in value if v)
                    else:
                        return ", ".join(str(v) for v in value if v)
                elif value is not None:
                    return str(value)
        return None

    async def create_issue(
        self,
        project_id: str,
        summary: str,
        description: Optional[str] = None,
        issue_type: Optional[str] = None,
        priority: Optional[str] = None,
        assignee: Optional[str] = None,
    ) -> dict[str, Any]:
        """Create a new issue."""
        credentials = self.auth_manager.load_credentials()
        if not credentials:
            return {"status": "error", "message": "Not authenticated"}

        issue_data = {
            "project": {"id": project_id},
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
                return {
                    "status": "success",
                    "message": f"Issue '{summary}' created successfully",
                    "data": data,
                }
            else:
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

                    # Try with custom fields format including $type for both Priority and Type
                    custom_fields = [
                        {
                            "$type": "SingleEnumIssueCustomField",
                            "name": "Priority",
                            "value": {"$type": "EnumBundleElement", "name": priority},
                        }
                    ]

                    # Also add Type field if it was specified
                    if issue_type:
                        custom_fields.append(
                            {
                                "$type": "SingleEnumIssueCustomField",
                                "name": "Type",
                                "value": {"$type": "EnumBundleElement", "name": issue_type},
                            }
                        )
                    else:
                        # Default to "Task" if no type specified
                        custom_fields.append(
                            {
                                "$type": "SingleEnumIssueCustomField",
                                "name": "Type",
                                "value": {"$type": "EnumBundleElement", "name": "Task"},
                            }
                        )

                    issue_data_no_priority["customFields"] = custom_fields

                    retry_response = await client_manager.make_request(
                        "POST", url, headers=headers, json_data=issue_data_no_priority
                    )
                    if retry_response.status_code in [200, 201]:
                        data = self._parse_json_response(retry_response)
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
        top: Optional[int] = None,
        query: Optional[str] = None,
        state: Optional[str] = None,
        assignee: Optional[str] = None,
    ) -> dict[str, Any]:
        """List issues with optional filtering."""
        progress_manager = get_progress_manager()

        credentials = self.auth_manager.load_credentials()
        if not credentials:
            return {"status": "error", "message": "Not authenticated"}

        with progress_manager.spinner("Fetching issues..."):
            params = {}
            if fields:
                params["fields"] = fields
            else:
                # Try to get comprehensive field data using multiple approaches
                params["fields"] = (
                    "id,numberInProject,summary,description,"
                    "state(name,id),priority(name,id),type(name,id),"
                    "assignee(login,fullName,id),project(id,name,shortName),created,updated,"
                    "customFields(name,value(name,id,login,fullName))"
                )

            if top:
                params["$top"] = str(top)

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
                client_manager = get_client_manager()
                response = await client_manager.make_request("GET", url, headers=headers, params=params)
                if response.status_code == 200:
                    data = self._parse_json_response(response)
                    return {
                        "status": "success",
                        "data": data,
                        "count": len(data),
                    }
                else:
                    error_text = response.text
                    return {
                        "status": "error",
                        "message": f"Failed to list issues: {error_text}",
                    }
            except Exception as e:
                return {"status": "error", "message": f"Error listing issues: {str(e)}"}

    async def get_issue(self, issue_id: str) -> dict[str, Any]:
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
                "tags(name),links(linkType,direction,issues(id,summary))"
            )
        }

        try:
            client_manager = get_client_manager()
            response = await client_manager.make_request("GET", url, headers=headers, params=params)
            if response.status_code == 200:
                data = self._parse_json_response(response)
                return {"status": "success", "data": data}
            else:
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
    ) -> dict[str, Any]:
        """Update an existing issue."""
        credentials = self.auth_manager.load_credentials()
        if not credentials:
            return {"status": "error", "message": "Not authenticated"}

        # Separate custom fields from regular fields
        update_data: dict[str, Any] = {}
        custom_fields = []

        if summary:
            update_data["summary"] = summary
        if description:
            update_data["description"] = description
        if assignee:
            update_data["assignee"] = {"login": assignee}

        # Handle state, priority and type as custom fields
        if state:
            custom_fields.append({"$type": "StateIssueCustomField", "name": "State", "value": {"name": state}})
        if priority:
            custom_fields.append(
                {"$type": "SingleEnumIssueCustomField", "name": "Priority", "value": {"name": priority}}
            )
        if issue_type:
            custom_fields.append({"$type": "SingleEnumIssueCustomField", "name": "Type", "value": {"name": issue_type}})

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
            else:
                error_text = response.text
                return {
                    "status": "error",
                    "message": f"Failed to update issue: {error_text}",
                }
        except Exception as e:
            return {"status": "error", "message": f"Error updating issue: {str(e)}"}

    async def delete_issue(self, issue_id: str) -> dict[str, Any]:
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
            else:
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
        top: Optional[int] = None,
    ) -> dict[str, Any]:
        """Search issues with advanced query."""
        credentials = self.auth_manager.load_credentials()
        if not credentials:
            return {"status": "error", "message": "Not authenticated"}

        params = {
            "fields": (
                "id,summary,description,state,priority,type,assignee(login,fullName),project(id,name),created,updated"
            )
        }

        if top:
            params["$top"] = str(top)

        # Build search query
        search_query = query
        if project_id:
            search_query = f"project:{project_id} AND ({query})"

        params["query"] = search_query

        url = f"{credentials.base_url.rstrip('/')}/api/issues"
        headers = {"Authorization": f"Bearer {credentials.token}"}

        try:
            client_manager = get_client_manager()
            response = await client_manager.make_request("GET", url, headers=headers, params=params)
            if response.status_code == 200:
                data = self._parse_json_response(response)
                return {
                    "status": "success",
                    "data": data,
                    "count": len(data),
                }
            else:
                error_text = response.text
                return {
                    "status": "error",
                    "message": f"Failed to search issues: {error_text}",
                }
        except Exception as e:
            return {"status": "error", "message": f"Error searching issues: {str(e)}"}

    async def _get_custom_field_id(self, issue_id: str, field_name: str) -> Optional[str]:
        """Get the custom field ID for a given field name."""
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
                for field in data.get("customFields", []):
                    if field.get("name") == field_name:
                        return field.get("id")
        except Exception:
            pass
        return None

    async def assign_issue(self, issue_id: str, assignee: str) -> dict[str, Any]:
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
    ) -> dict[str, Any]:
        """Move an issue to a different state or project."""
        update_data: dict[str, Any] = {}
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

    async def _move_issue_to_project(self, issue_id: str, project_id: str) -> dict[str, Any]:
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
            else:
                error_text = response.text
                return {
                    "status": "error",
                    "message": f"Failed to move issue: {error_text}",
                }
        except Exception as e:
            return {"status": "error", "message": f"Error moving issue: {str(e)}"}

    async def find_tag_by_name(self, tag_name: str) -> dict[str, Any]:
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
            else:
                return {"status": "error", "message": f"Failed to search tags: {response.text}"}
        except Exception as e:
            return {"status": "error", "message": f"Error searching for tag: {str(e)}"}

    async def create_tag(self, tag_name: str) -> dict[str, Any]:
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
            else:
                return {"status": "error", "message": f"Failed to create tag: {response.text}"}
        except Exception as e:
            return {"status": "error", "message": f"Error creating tag: {str(e)}"}

    async def get_or_create_tag(self, tag_name: str) -> dict[str, Any]:
        """Get existing tag or create new one. Returns tag data with ID."""
        # First try to find existing tag
        find_result = await self.find_tag_by_name(tag_name)
        if find_result["status"] == "success":
            return find_result
        elif find_result["status"] == "not_found":
            # Tag doesn't exist, try to create it
            return await self.create_tag(tag_name)
        else:
            # Error occurred during search
            return find_result

    async def add_tag(self, issue_id: str, tag: str) -> dict[str, Any]:
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
            else:
                error_text = response.text
                return {
                    "status": "error",
                    "message": f"Failed to add tag to issue: {error_text}",
                }
        except Exception as e:
            return {"status": "error", "message": f"Error adding tag to issue: {str(e)}"}

    async def remove_tag(self, issue_id: str, tag: str) -> dict[str, Any]:
        """Remove a tag from an issue."""
        credentials = self.auth_manager.load_credentials()
        if not credentials:
            return {"status": "error", "message": "Not authenticated"}

        url = f"{credentials.base_url.rstrip('/')}/api/issues/{issue_id}/tags/{tag}"
        headers = {"Authorization": f"Bearer {credentials.token}"}

        try:
            client_manager = get_client_manager()
            response = await client_manager.make_request("DELETE", url, headers=headers)
            if response.status_code == 200:
                return {
                    "status": "success",
                    "message": (f"Tag '{tag}' removed from issue '{issue_id}' successfully"),
                }
            else:
                error_text = response.text
                return {
                    "status": "error",
                    "message": f"Failed to remove tag: {error_text}",
                }
        except Exception as e:
            return {"status": "error", "message": f"Error removing tag: {str(e)}"}

    async def list_tags(self, issue_id: str) -> dict[str, Any]:
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
            else:
                error_text = response.text
                return {
                    "status": "error",
                    "message": f"Failed to list tags: {error_text}",
                }
        except Exception as e:
            return {"status": "error", "message": f"Error listing tags: {str(e)}"}

    # Comments functionality
    async def add_comment(self, issue_id: str, text: str) -> dict[str, Any]:
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
            else:
                error_text = response.text
                return {
                    "status": "error",
                    "message": f"Failed to add comment: {error_text}",
                }
        except Exception as e:
            return {"status": "error", "message": f"Error adding comment: {str(e)}"}

    async def list_comments(self, issue_id: str) -> dict[str, Any]:
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
            else:
                error_text = response.text
                return {
                    "status": "error",
                    "message": f"Failed to list comments: {error_text}",
                }
        except Exception as e:
            return {"status": "error", "message": f"Error listing comments: {str(e)}"}

    async def update_comment(self, issue_id: str, comment_id: str, text: str) -> dict[str, Any]:
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
            else:
                error_text = response.text
                return {
                    "status": "error",
                    "message": f"Failed to update comment: {error_text}",
                }
        except Exception as e:
            return {"status": "error", "message": f"Error updating comment: {str(e)}"}

    async def delete_comment(self, issue_id: str, comment_id: str) -> dict[str, Any]:
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
            else:
                error_text = response.text
                return {
                    "status": "error",
                    "message": f"Failed to delete comment: {error_text}",
                }
        except Exception as e:
            return {"status": "error", "message": f"Error deleting comment: {str(e)}"}

    # Attachments functionality
    async def upload_attachment(self, issue_id: str, file_path: str) -> dict[str, Any]:
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
                    else:
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

    async def list_attachments(self, issue_id: str) -> dict[str, Any]:
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
            else:
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

    async def download_attachment(self, issue_id: str, attachment_id: str, output_path: str) -> dict[str, Any]:
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
            else:
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

    async def delete_attachment(self, issue_id: str, attachment_id: str) -> dict[str, Any]:
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
            else:
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
    async def _resolve_link_type(self, link_type_name: str) -> Optional[dict[str, Any]]:
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
            else:
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
            else:
                logger.error("Failed to fetch issue ID", issue_id=issue_id, status_code=response.status_code)
                return None
        except Exception as e:
            logger.error("Error fetching issue ID", issue_id=issue_id, error=str(e))
            return None

    async def create_link(self, source_issue_id: str, target_issue_id: str, link_type: str) -> dict[str, Any]:
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
            else:
                error_text = response.text
                return {
                    "status": "error",
                    "message": f"Failed to create link: {error_text}",
                }
        except Exception as e:
            return {"status": "error", "message": f"Error creating link: {str(e)}"}

    async def list_links(self, issue_id: str) -> dict[str, Any]:
        """List all links for an issue."""
        credentials = self.auth_manager.load_credentials()
        if not credentials:
            return {"status": "error", "message": "Not authenticated"}

        url = f"{credentials.base_url.rstrip('/')}/api/issues/{issue_id}"
        headers = {"Authorization": f"Bearer {credentials.token}"}
        params = {"fields": "links(linkType(name),direction,issues(id,summary))"}

        try:
            client_manager = get_client_manager()
            response = await client_manager.make_request("GET", url, headers=headers, params=params)
            if response.status_code == 200:
                data = self._parse_json_response(response)
                links = data.get("links", [])
                return {"status": "success", "data": links}
            else:
                error_text = response.text
                return {
                    "status": "error",
                    "message": f"Failed to list links: {error_text}",
                }
        except Exception as e:
            return {"status": "error", "message": f"Error listing links: {str(e)}"}

    async def delete_link(self, source_issue_id: str, link_id: str) -> dict[str, Any]:
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
            else:
                error_text = response.text
                return {
                    "status": "error",
                    "message": f"Failed to delete link: {error_text}",
                }
        except Exception as e:
            return {"status": "error", "message": f"Error deleting link: {str(e)}"}

    async def list_link_types(self) -> dict[str, Any]:
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
            else:
                error_text = response.text
                return {
                    "status": "error",
                    "message": f"Failed to list link types: {error_text}",
                }
        except Exception as e:
            return {"status": "error", "message": f"Error listing link types: {str(e)}"}

    # Display methods
    def display_issues_table(self, issues: list[dict[str, Any]]) -> None:
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

    def display_issue_details(self, issue: dict[str, Any]) -> None:
        """Display detailed information about a single issue."""
        issue_id = issue.get("id", "N/A")
        self.console.print(f"[bold blue]Issue Details: {issue_id}[/bold blue]")

        summary = issue.get("summary", "N/A")
        self.console.print(f"[bold]Summary:[/bold] {summary}")

        if issue.get("description"):
            description = issue.get("description", "N/A")
            self.console.print(f"[bold]Description:[/bold] {description}")

        state = issue.get("state", {})
        state_name = state.get("name", "N/A") if state else "N/A"
        self.console.print(f"[bold]State:[/bold] {state_name}")

        priority = issue.get("priority", {})
        priority_name = priority.get("name", "N/A") if priority else "N/A"
        self.console.print(f"[bold]Priority:[/bold] {priority_name}")

        issue_type = issue.get("type", {})
        type_name = issue_type.get("name", "N/A") if issue_type else "N/A"
        self.console.print(f"[bold]Type:[/bold] {type_name}")

        assignee = issue.get("assignee", {})
        assignee_name = assignee.get("fullName", "Unassigned") if assignee else "Unassigned"
        self.console.print(f"[bold]Assignee:[/bold] {assignee_name}")

        project = issue.get("project", {})
        project_name = project.get("name", "N/A") if project else "N/A"
        self.console.print(f"[bold]Project:[/bold] {project_name}")

        self.console.print(f"[bold]Created:[/bold] {issue.get('created', 'N/A')}")
        self.console.print(f"[bold]Updated:[/bold] {issue.get('updated', 'N/A')}")

        # Display tags if any
        tags = issue.get("tags", [])
        if tags:
            tag_names = [tag.get("name", "") for tag in tags]
            self.console.print(f"[bold]Tags:[/bold] {', '.join(tag_names)}")

    def display_comments_table(self, comments: list[dict[str, Any]]) -> None:
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

            table.add_row(
                str(comment.get("id", "N/A")),
                author_name,
                truncated_text,
                str(comment.get("created", "N/A")),
            )

        self.console.print(table)

    def display_attachments_table(self, attachments: list[dict[str, Any]]) -> None:
        """Display attachments in a formatted table."""
        if not attachments:
            self.console.print("No attachments found.", style="yellow")
            return

        table = Table(title="Attachments")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Size", style="blue")
        table.add_column("Type", style="yellow")
        table.add_column("Author", style="magenta")

        for attachment in attachments:
            author = attachment.get("author", {})
            author_name = author.get("fullName", "N/A") if author else "N/A"

            table.add_row(
                attachment.get("id", "N/A"),
                attachment.get("name", "N/A"),
                str(attachment.get("size", "N/A")),
                attachment.get("mimeType", "N/A"),
                author_name,
            )

        self.console.print(table)

    def display_links_table(self, links: list[dict[str, Any]]) -> None:
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
                issue_id = issue.get("id", "N/A")
                issue_summary = issue.get("summary", "N/A")
                issue_summaries.append(f"{issue_id}: {issue_summary[:30]}")

            related_issues = "\n".join(issue_summaries) if issue_summaries else "N/A"

            table.add_row(type_name, direction, related_issues)

        self.console.print(table)

    def display_link_types_table(self, link_types: list[dict[str, Any]]) -> None:
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
