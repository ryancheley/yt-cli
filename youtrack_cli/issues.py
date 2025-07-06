"""Issue management for YouTrack CLI."""

from typing import Any, Optional

import httpx
from rich.console import Console
from rich.table import Table

from .auth import AuthManager
from .client import get_client_manager
from .progress import get_progress_manager

__all__ = ["IssueManager"]


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
            return {"status": "error", "message": f"Error creating issue: {str(e)}"}

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
                params["fields"] = (
                    "id,summary,description,state,priority,type,"
                    "assignee(login,fullName),project(id,name),created,updated"
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

        update_data: dict[str, Any] = {}
        if summary:
            update_data["summary"] = summary
        if description:
            update_data["description"] = description
        if state:
            update_data["state"] = {"name": state}
        if priority:
            update_data["priority"] = {"name": priority}
        if assignee:
            update_data["assignee"] = {"login": assignee}
        if issue_type:
            update_data["type"] = {"name": issue_type}

        if not update_data:
            return {"status": "error", "message": "No fields to update"}

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

    async def assign_issue(self, issue_id: str, assignee: str) -> dict[str, Any]:
        """Assign an issue to a user."""
        return await self.update_issue(issue_id, assignee=assignee)

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

    async def _move_issue_to_project(self, issue_id: str, project_id: str) -> dict[str, Any]:
        """Move an issue to a different project."""
        credentials = self.auth_manager.load_credentials()
        if not credentials:
            return {"status": "error", "message": "Not authenticated"}

        url = f"{credentials.base_url.rstrip('/')}/api/issues/{issue_id}"
        headers = {
            "Authorization": f"Bearer {credentials.token}",
            "Content-Type": "application/json",
        }
        update_data = {"project": {"id": project_id}}

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

    async def add_tag(self, issue_id: str, tag: str) -> dict[str, Any]:
        """Add a tag to an issue."""
        credentials = self.auth_manager.load_credentials()
        if not credentials:
            return {"status": "error", "message": "Not authenticated"}

        url = f"{credentials.base_url.rstrip('/')}/api/issues/{issue_id}/tags"
        headers = {
            "Authorization": f"Bearer {credentials.token}",
            "Content-Type": "application/json",
        }
        tag_data = {"name": tag}

        try:
            client_manager = get_client_manager()
            response = await client_manager.make_request("POST", url, headers=headers, json_data=tag_data)
            if response.status_code == 200:
                return {
                    "status": "success",
                    "message": (f"Tag '{tag}' added to issue '{issue_id}' successfully"),
                }
            else:
                error_text = response.text
                return {
                    "status": "error",
                    "message": f"Failed to add tag: {error_text}",
                }
        except Exception as e:
            return {"status": "error", "message": f"Error adding tag: {str(e)}"}

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

        url = f"{credentials.base_url.rstrip('/')}/api/issues/{issue_id}/attachments/{attachment_id}"
        headers = {"Authorization": f"Bearer {credentials.token}"}

        try:
            client_manager = get_client_manager()
            response = await client_manager.make_request("GET", url, headers=headers)
            if response.status_code == 200:
                with open(output_path, "wb") as file:
                    file.write(response.content)
                return {
                    "status": "success",
                    "message": (f"Attachment downloaded to '{output_path}' successfully"),
                }
            else:
                error_text = response.text
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
    async def create_link(self, source_issue_id: str, target_issue_id: str, link_type: str) -> dict[str, Any]:
        """Create a link between two issues."""
        credentials = self.auth_manager.load_credentials()
        if not credentials:
            return {"status": "error", "message": "Not authenticated"}

        url = f"{credentials.base_url.rstrip('/')}/api/issues/{source_issue_id}/links"
        headers = {
            "Authorization": f"Bearer {credentials.token}",
            "Content-Type": "application/json",
        }
        link_data = {
            "linkType": {"name": link_type},
            "issues": [{"id": target_issue_id}],
        }

        try:
            client_manager = get_client_manager()
            response = await client_manager.make_request("POST", url, headers=headers, json_data=link_data)
            if response.status_code == 200:
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
            assignee = issue.get("assignee", {})
            assignee_name = assignee.get("fullName", "Unassigned") if assignee else "Unassigned"

            project = issue.get("project", {})
            project_name = project.get("name", "N/A") if project else "N/A"

            state = issue.get("state", {})
            state_name = state.get("name", "N/A") if state else "N/A"

            priority = issue.get("priority", {})
            priority_name = priority.get("name", "N/A") if priority else "N/A"

            issue_type = issue.get("type", {})
            type_name = issue_type.get("name", "N/A") if issue_type else "N/A"

            summary = issue.get("summary", "N/A")
            truncated_summary = summary[:50] + ("..." if len(summary) > 50 else "")

            table.add_row(
                issue.get("id", "N/A"),
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
                comment.get("id", "N/A"),
                author_name,
                truncated_text,
                comment.get("created", "N/A"),
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
