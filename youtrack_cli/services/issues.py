"""Issue service for YouTrack API operations."""

from typing import Any, Dict, Optional

from .base import BaseService


class IssueService(BaseService):
    """Service for YouTrack issue API operations.
    
    Handles all HTTP communication with YouTrack's issues API endpoints.
    Pure API service with no business logic or presentation concerns.
    """

    async def create_issue(
        self,
        project_id: str,
        summary: str,
        description: Optional[str] = None,
        issue_type: Optional[str] = None,
        priority: Optional[str] = None,
        assignee: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new issue via API.
        
        Args:
            project_id: Internal project ID (not short name)
            summary: Issue summary
            description: Issue description
            issue_type: Issue type name
            priority: Priority name
            assignee: Assignee login
            
        Returns:
            API response with issue data
        """
        try:
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

            response = await self._make_request("POST", "issues", json_data=issue_data)
            return await self._handle_response(response, success_codes=[200, 201])

        except ValueError as e:
            return self._create_error_response(str(e))
        except Exception as e:
            return self._create_error_response(f"Error creating issue: {str(e)}")

    async def get_issue(self, issue_id: str, fields: Optional[str] = None) -> Dict[str, Any]:
        """Get issue details via API.
        
        Args:
            issue_id: Issue ID (idReadable or internal ID)
            fields: Comma-separated list of fields to return
            
        Returns:
            API response with issue data
        """
        try:
            params = {}
            if fields:
                params["fields"] = fields
            else:
                params["fields"] = (
                    "id,summary,description,state,priority,type,"
                    "assignee(login,fullName),project(id,name),created,updated,"
                    "tags(name),links(linkType,direction,issues(id,summary)),"
                    "customFields(id,name,value(login,fullName,name))"
                )

            response = await self._make_request("GET", f"issues/{issue_id}", params=params)
            return await self._handle_response(response)

        except ValueError as e:
            return self._create_error_response(str(e))
        except Exception as e:
            return self._create_error_response(f"Error getting issue: {str(e)}")

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
        """Update an existing issue via API.
        
        Args:
            issue_id: Issue ID to update
            summary: New summary
            description: New description
            state: New state name
            priority: New priority name
            assignee: New assignee login
            issue_type: New issue type name
            
        Returns:
            API response
        """
        try:
            update_data: Dict[str, Any] = {}
            custom_fields = []

            # Handle regular fields
            if summary is not None:
                update_data["summary"] = summary
            if description is not None:
                update_data["description"] = description
            if assignee is not None:
                update_data["assignee"] = {"login": assignee} if assignee else None
            if issue_type is not None:
                update_data["type"] = {"name": issue_type}

            # Handle fields that might be custom fields
            if state is not None:
                custom_fields.append({"name": "State", "value": {"name": state}})
            if priority is not None:
                custom_fields.append({"name": "Priority", "value": {"name": priority}})

            # Add custom fields if any
            if custom_fields:
                update_data["customFields"] = custom_fields

            response = await self._make_request("POST", f"issues/{issue_id}", json_data=update_data)
            return await self._handle_response(response)

        except ValueError as e:
            return self._create_error_response(str(e))
        except Exception as e:
            return self._create_error_response(f"Error updating issue: {str(e)}")

    async def delete_issue(self, issue_id: str) -> Dict[str, Any]:
        """Delete an issue via API.
        
        Args:
            issue_id: Issue ID to delete
            
        Returns:
            API response
        """
        try:
            response = await self._make_request("DELETE", f"issues/{issue_id}")
            return await self._handle_response(response)

        except ValueError as e:
            return self._create_error_response(str(e))
        except Exception as e:
            return self._create_error_response(f"Error deleting issue: {str(e)}")

    async def search_issues(
        self,
        query: str,
        fields: Optional[str] = None,
        top: Optional[int] = None,
        skip: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Search issues via API.
        
        Args:
            query: YouTrack query string
            fields: Comma-separated list of fields to return
            top: Maximum number of results
            skip: Number of results to skip
            
        Returns:
            API response with issue list
        """
        try:
            params = {"query": query}

            if fields:
                params["fields"] = fields
            else:
                params["fields"] = (
                    "id,idReadable,summary,description,state,priority,type,"
                    "assignee(login,fullName),project(id,name,shortName),"
                    "created,updated,tags(name),"
                    "customFields(id,name,value(login,fullName,name))"
                )

            if top is not None:
                params["$top"] = str(top)
            if skip is not None:
                params["$skip"] = str(skip)

            response = await self._make_request("GET", "issues", params=params)
            return await self._handle_response(response)

        except ValueError as e:
            return self._create_error_response(str(e))
        except Exception as e:
            return self._create_error_response(f"Error searching issues: {str(e)}")

    async def assign_issue(self, issue_id: str, assignee: str) -> Dict[str, Any]:
        """Assign an issue to a user via API.
        
        Args:
            issue_id: Issue ID to assign
            assignee: Username/login to assign to
            
        Returns:
            API response
        """
        try:
            update_data = {"assignee": {"login": assignee}}
            response = await self._make_request("POST", f"issues/{issue_id}", json_data=update_data)
            return await self._handle_response(response)

        except ValueError as e:
            return self._create_error_response(str(e))
        except Exception as e:
            return self._create_error_response(f"Error assigning issue: {str(e)}")

    async def add_tag(self, issue_id: str, tag_name: str) -> Dict[str, Any]:
        """Add a tag to an issue via API.
        
        Args:
            issue_id: Issue ID
            tag_name: Tag name to add
            
        Returns:
            API response
        """
        try:
            tag_data = {"name": tag_name}
            response = await self._make_request("POST", f"issues/{issue_id}/tags", json_data=tag_data)
            return await self._handle_response(response, success_codes=[200, 201])

        except ValueError as e:
            return self._create_error_response(str(e))
        except Exception as e:
            return self._create_error_response(f"Error adding tag: {str(e)}")

    async def remove_tag(self, issue_id: str, tag_name: str) -> Dict[str, Any]:
        """Remove a tag from an issue via API.
        
        Args:
            issue_id: Issue ID
            tag_name: Tag name to remove
            
        Returns:
            API response
        """
        try:
            response = await self._make_request("DELETE", f"issues/{issue_id}/tags/{tag_name}")
            return await self._handle_response(response)

        except ValueError as e:
            return self._create_error_response(str(e))
        except Exception as e:
            return self._create_error_response(f"Error removing tag: {str(e)}")

    async def list_tags(self, issue_id: str) -> Dict[str, Any]:
        """List tags for an issue via API.
        
        Args:
            issue_id: Issue ID
            
        Returns:
            API response with tag list
        """
        try:
            response = await self._make_request("GET", f"issues/{issue_id}/tags")
            return await self._handle_response(response)

        except ValueError as e:
            return self._create_error_response(str(e))
        except Exception as e:
            return self._create_error_response(f"Error listing tags: {str(e)}")

    async def add_comment(self, issue_id: str, text: str) -> Dict[str, Any]:
        """Add a comment to an issue via API.
        
        Args:
            issue_id: Issue ID
            text: Comment text
            
        Returns:
            API response with comment data
        """
        try:
            comment_data = {"text": text}
            response = await self._make_request("POST", f"issues/{issue_id}/comments", json_data=comment_data)
            return await self._handle_response(response, success_codes=[200, 201])

        except ValueError as e:
            return self._create_error_response(str(e))
        except Exception as e:
            return self._create_error_response(f"Error adding comment: {str(e)}")

    async def list_comments(self, issue_id: str, fields: Optional[str] = None) -> Dict[str, Any]:
        """List comments for an issue via API.
        
        Args:
            issue_id: Issue ID
            fields: Comma-separated list of fields to return
            
        Returns:
            API response with comment list
        """
        try:
            params = {}
            if fields:
                params["fields"] = fields
            else:
                params["fields"] = "id,text,created,updated,author(login,fullName)"

            response = await self._make_request("GET", f"issues/{issue_id}/comments", params=params)
            return await self._handle_response(response)

        except ValueError as e:
            return self._create_error_response(str(e))
        except Exception as e:
            return self._create_error_response(f"Error listing comments: {str(e)}")

    async def update_comment(self, issue_id: str, comment_id: str, text: str) -> Dict[str, Any]:
        """Update a comment via API.
        
        Args:
            issue_id: Issue ID
            comment_id: Comment ID to update
            text: New comment text
            
        Returns:
            API response
        """
        try:
            comment_data = {"text": text}
            response = await self._make_request(
                "POST", f"issues/{issue_id}/comments/{comment_id}", json_data=comment_data
            )
            return await self._handle_response(response)

        except ValueError as e:
            return self._create_error_response(str(e))
        except Exception as e:
            return self._create_error_response(f"Error updating comment: {str(e)}")

    async def delete_comment(self, issue_id: str, comment_id: str) -> Dict[str, Any]:
        """Delete a comment via API.
        
        Args:
            issue_id: Issue ID
            comment_id: Comment ID to delete
            
        Returns:
            API response
        """
        try:
            response = await self._make_request("DELETE", f"issues/{issue_id}/comments/{comment_id}")
            return await self._handle_response(response)

        except ValueError as e:
            return self._create_error_response(str(e))
        except Exception as e:
            return self._create_error_response(f"Error deleting comment: {str(e)}")

    async def upload_attachment(self, issue_id: str, file_path: str, file_data: bytes) -> Dict[str, Any]:
        """Upload an attachment to an issue via API.
        
        Args:
            issue_id: Issue ID
            file_path: Original file path/name
            file_data: File content as bytes
            
        Returns:
            API response
        """
        try:
            # Note: This is a simplified implementation
            # In reality, you'd need to handle multipart/form-data
            files = {"file": (file_path, file_data)}

            # For now, return a placeholder response
            # Real implementation would require multipart upload support
            return self._create_error_response("Attachment upload not yet implemented in service layer")

        except Exception as e:
            return self._create_error_response(f"Error uploading attachment: {str(e)}")

    async def list_attachments(self, issue_id: str, fields: Optional[str] = None) -> Dict[str, Any]:
        """List attachments for an issue via API.
        
        Args:
            issue_id: Issue ID
            fields: Comma-separated list of fields to return
            
        Returns:
            API response with attachment list
        """
        try:
            params = {}
            if fields:
                params["fields"] = fields
            else:
                params["fields"] = "id,name,size,created,author(login,fullName)"

            response = await self._make_request("GET", f"issues/{issue_id}/attachments", params=params)
            return await self._handle_response(response)

        except ValueError as e:
            return self._create_error_response(str(e))
        except Exception as e:
            return self._create_error_response(f"Error listing attachments: {str(e)}")

    async def delete_attachment(self, issue_id: str, attachment_id: str) -> Dict[str, Any]:
        """Delete an attachment via API.
        
        Args:
            issue_id: Issue ID
            attachment_id: Attachment ID to delete
            
        Returns:
            API response
        """
        try:
            response = await self._make_request("DELETE", f"issues/{issue_id}/attachments/{attachment_id}")
            return await self._handle_response(response)

        except ValueError as e:
            return self._create_error_response(str(e))
        except Exception as e:
            return self._create_error_response(f"Error deleting attachment: {str(e)}")

    async def get_custom_field_value(self, issue_id: str, field_name: str) -> Dict[str, Any]:
        """Get a custom field value for an issue via API.
        
        Args:
            issue_id: Issue ID
            field_name: Custom field name
            
        Returns:
            API response with field data
        """
        try:
            params = {"fields": "customFields(id,name,value)"}
            response = await self._make_request("GET", f"issues/{issue_id}", params=params)
            return await self._handle_response(response)

        except ValueError as e:
            return self._create_error_response(str(e))
        except Exception as e:
            return self._create_error_response(f"Error getting custom field: {str(e)}")

    async def find_tag_by_name(self, tag_name: str) -> Dict[str, Any]:
        """Find a tag by name via API.
        
        Args:
            tag_name: Tag name to search for
            
        Returns:
            API response with tag data
        """
        try:
            params = {"query": tag_name, "fields": "id,name"}
            response = await self._make_request("GET", "issueTags", params=params)
            return await self._handle_response(response)

        except ValueError as e:
            return self._create_error_response(str(e))
        except Exception as e:
            return self._create_error_response(f"Error finding tag: {str(e)}")

    async def create_tag(self, tag_name: str) -> Dict[str, Any]:
        """Create a new tag via API.
        
        Args:
            tag_name: Name of tag to create
            
        Returns:
            API response with created tag data
        """
        try:
            tag_data = {"name": tag_name}
            response = await self._make_request("POST", "issueTags", json_data=tag_data)
            return await self._handle_response(response, success_codes=[200, 201])

        except ValueError as e:
            return self._create_error_response(str(e))
        except Exception as e:
            return self._create_error_response(f"Error creating tag: {str(e)}")
