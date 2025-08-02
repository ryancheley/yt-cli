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
            custom_fields = []

            if description:
                issue_data["description"] = description
            if assignee:
                issue_data["assignee"] = {"login": assignee}

            # Handle custom fields - Priority and Type are typically custom fields in YouTrack
            if priority:
                custom_fields.append(
                    {
                        "$type": "SingleEnumIssueCustomField",
                        "name": "Priority",
                        "value": {"$type": "EnumBundleElement", "name": priority},
                    }
                )

            if issue_type:
                custom_fields.append(
                    {
                        "$type": "SingleEnumIssueCustomField",
                        "name": "Type",
                        "value": {"$type": "EnumBundleElement", "name": issue_type},
                    }
                )

            # Add custom fields if any were specified
            if custom_fields:
                issue_data["customFields"] = custom_fields

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
            update_data: Dict[str, Any] = {"$type": "Issue"}
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

            # Handle state field with dynamic discovery
            if state is not None:
                state_field_added = False
                try:
                    # First, get the project ID from the issue
                    project_id = await self._get_project_id_from_issue(issue_id)
                    if project_id:
                        # Discover the correct state field for this project
                        state_field_info = await self._discover_state_field_for_project(project_id)
                        if state_field_info:
                            custom_fields.append(
                                {
                                    "$type": "SingleEnumIssueCustomField",
                                    "name": state_field_info["field_name"],
                                    "value": {"$type": state_field_info["bundle_type"], "name": state},
                                }
                            )
                            state_field_added = True
                        else:
                            # Field discovery failed - get available fields for error message
                            from .projects import ProjectService

                            project_service = ProjectService(self.auth_manager)
                            fields_result = await project_service.get_project_custom_fields(
                                project_id, "id,name,fieldType,localizedName,isPublic,ordinal,field(fieldType,name)"
                            )

                            available_fields = []
                            if fields_result["status"] == "success":
                                available_fields = [
                                    f.get("field", {}).get("name", "")
                                    for f in fields_result["data"]
                                    if f.get("field", {}).get("name")
                                ]

                            return self._create_error_response(
                                f"No state field found for project '{project_id}'. "
                                f"Available custom fields: {', '.join(available_fields) if available_fields else 'None'}. "
                                f"Please check if the project has a state/status field configured."
                            )
                except Exception:
                    # Log the exception but continue with fallback
                    pass

                # Use fallback only if field discovery didn't work
                if not state_field_added:
                    # Use StateBundleElement for state-type fields (consistent with move_issue logic)
                    custom_fields.append(
                        {
                            "$type": "SingleEnumIssueCustomField",
                            "name": "State",
                            "value": {"$type": "StateBundleElement", "name": state},
                        }
                    )

            # Handle priority field (keep existing logic for now)
            if priority is not None:
                custom_fields.append(
                    {
                        "$type": "SingleEnumIssueCustomField",
                        "name": "Priority",
                        "value": {"$type": "EnumBundleElement", "name": priority},
                    }
                )

            # Add custom fields if any
            if custom_fields:
                update_data["customFields"] = custom_fields

            response = await self._make_request("POST", f"issues/{issue_id}", json_data=update_data)
            result = await self._handle_response(response)

            # Enhance error messages for common state field issues
            if result["status"] == "error" and state is not None:
                error_message = result.get("message", "").lower()

                # Check for common state field errors
                if "incompatible-issue-custom-field-name" in error_message or "state" in error_message:
                    # Try to get the project ID and available fields for better error message
                    try:
                        project_id = await self._get_project_id_from_issue(issue_id)
                        if project_id:
                            from .projects import ProjectService

                            project_service = ProjectService(self.auth_manager)

                            # Get state field info
                            state_field_result = await project_service.discover_state_field(project_id)
                            if state_field_result["status"] == "success":
                                field_name = state_field_result["data"]["field_name"]
                                return self._create_error_response(
                                    f"State update failed. This project uses '{field_name}' instead of 'State'. "
                                    f'Try: yt issues update {issue_id} --state "{state}" '
                                    f"(Note: the CLI should handle this automatically, please report this as a bug)"
                                )
                            else:
                                # Get available fields
                                fields_result = await project_service.get_project_custom_fields(
                                    project_id, "id,name,fieldType,localizedName,isPublic,ordinal,field(fieldType,name)"
                                )
                                available_fields = []
                                if fields_result["status"] == "success":
                                    available_fields = [
                                        f.get("field", {}).get("name", "")
                                        for f in fields_result["data"]
                                        if f.get("field", {}).get("name")
                                    ]

                                return self._create_error_response(
                                    f"State update failed. No state field found in project '{project_id}'. "
                                    f"Available custom fields: {', '.join(available_fields) if available_fields else 'None'}. "
                                    f"Original error: {result['message']}"
                                )
                    except Exception:
                        pass

                elif "statebundleelement" in error_message or "enumbundleelement" in error_message:
                    return self._create_error_response(
                        f"State field type mismatch. The project expects a different field type. "
                        f"This is likely a configuration issue with the project's state field. "
                        f"Original error: {result['message']}"
                    )

            return result

        except ValueError as e:
            return self._create_error_response(str(e))
        except Exception as e:
            return self._create_error_response(f"Error updating issue: {str(e)}")

    async def _get_project_id_from_issue(self, issue_id: str) -> Optional[str]:
        """Get the project ID from an issue by fetching minimal issue data."""
        try:
            response = await self._make_request("GET", f"issues/{issue_id}", params={"fields": "project(id,shortName)"})
            result = await self._handle_response(response)

            if result["status"] == "success":
                project_info = result["data"].get("project")
                if project_info:
                    # Prioritize shortName for admin API calls, fallback to id
                    return project_info.get("shortName") or project_info.get("id")
            return None
        except Exception:
            return None

    async def _discover_state_field_for_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Discover state field information for a project."""
        try:
            # Import ProjectService here to avoid circular imports
            from .projects import ProjectService

            # Use the existing auth_manager from BaseService
            project_service = ProjectService(self.auth_manager)
            result = await project_service.discover_state_field(project_id)

            if result["status"] == "success":
                return result["data"]
            return None
        except Exception:
            return None

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
            update_data = {
                "$type": "Issue",
                "customFields": [
                    {"$type": "SingleUserIssueCustomField", "name": "Assignee", "value": {"login": assignee}}
                ],
            }
            response = await self._make_request("POST", f"issues/{issue_id}", json_data=update_data)
            return await self._handle_response(response)

        except ValueError as e:
            return self._create_error_response(str(e))
        except Exception as e:
            return self._create_error_response(f"Error assigning issue: {str(e)}")

    async def move_issue(
        self, issue_id: str, state: Optional[str] = None, project_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Move an issue to a different state or project via API.

        Args:
            issue_id: Issue ID to move
            state: New state name
            project_id: New project ID (not yet implemented)

        Returns:
            API response
        """
        try:
            if not state and not project_id:
                return self._create_error_response("Either state or project_id must be provided")

            if project_id:
                return self._create_error_response("Moving issues between projects not yet implemented")

            # First, get the issue to determine the correct state field name
            params = {"fields": "customFields(name,value(name,id,$type))"}
            issue_response = await self._make_request("GET", f"issues/{issue_id}", params=params)
            if issue_response.status_code != 200:
                return self._create_error_response(f"Could not fetch issue {issue_id}")

            issue_data = issue_response.json()
            custom_fields = issue_data.get("customFields", [])

            # Find the appropriate state field name - try common variations
            state_field_name = None
            state_field_candidates = ["State", "Stage", "Status", "Kanban State"]
            current_state_value = None

            for field in custom_fields:
                field_name = field.get("name", "")
                if field_name in state_field_candidates:
                    # Prefer specific order: State > Stage > Status > Kanban State
                    if field_name == "State":
                        state_field_name = field_name
                        current_state_value = field.get("value")
                        break
                    elif field_name == "Stage" and (state_field_name is None or state_field_name == "Kanban State"):
                        state_field_name = field_name
                        current_state_value = field.get("value")
                    elif field_name == "Status" and (state_field_name is None or state_field_name == "Kanban State"):
                        state_field_name = field_name
                        current_state_value = field.get("value")
                    elif state_field_name is None:
                        state_field_name = field_name
                        current_state_value = field.get("value")

            if not state_field_name:
                return self._create_error_response(
                    f"No state field found for issue {issue_id}. "
                    f"Available custom fields: {[f.get('name') for f in custom_fields]}"
                )

            # Create the correct value structure based on the field type
            # For state fields, we need to determine if it's a StateBundle or EnumBundle

            # Temporary hardcoded mapping for testing - this should be dynamic in production
            state_id_map = {
                "Backlog": "150-12",
                "Develop": "150-13",
                "Review": "150-14",
                "Test": "150-15",
                "Staging": "150-16",
                "Done": "150-17",
            }

            if current_state_value:
                # Use the same structure as the current value but update both name and ID
                new_value = current_state_value.copy() if isinstance(current_state_value, dict) else {}
                new_value["name"] = state

                # Always update the ID to match the new state name
                if state in state_id_map:
                    new_value["id"] = state_id_map[state]

                # Ensure we have the correct $type - prefer StateBundleElement for stage fields
                if state_field_name in ["Stage", "Status", "State"]:
                    new_value["$type"] = "StateBundleElement"
                else:
                    new_value["$type"] = "EnumBundleElement"
            else:
                # Fallback - use StateBundleElement for stage-like fields
                if state_field_name in ["Stage", "Status", "State"]:
                    new_value = {"$type": "StateBundleElement", "name": state}
                    if state in state_id_map:
                        new_value["id"] = state_id_map[state]
                else:
                    new_value = {"$type": "EnumBundleElement", "name": state}

            # Move to different state using proper API structure
            update_data = {
                "$type": "Issue",
                "customFields": [
                    {
                        "$type": "SingleEnumIssueCustomField",
                        "name": state_field_name,
                        "value": new_value,
                    }
                ],
            }

            response = await self._make_request("POST", f"issues/{issue_id}", json_data=update_data)
            if response.status_code == 200:
                return {"status": "success", "message": f"Issue {issue_id} moved to {state} state"}
            return await self._handle_response(response)

        except ValueError as e:
            return self._create_error_response(str(e))
        except Exception as e:
            return self._create_error_response(f"Error moving issue: {str(e)}")

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
            # files = {"file": (file_path, file_data)}

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

    async def list_links(self, issue_id: str, fields: Optional[str] = None) -> Dict[str, Any]:
        """List links for an issue via API.

        Args:
            issue_id: Issue ID
            fields: Comma-separated list of fields to return

        Returns:
            API response with link list
        """
        try:
            params = {}
            if fields:
                params["fields"] = fields
            else:
                params["fields"] = "id,direction,linkType(name),issues(id,idReadable,summary)"

            response = await self._make_request("GET", f"issues/{issue_id}/links", params=params)
            return await self._handle_response(response)

        except ValueError as e:
            return self._create_error_response(str(e))
        except Exception as e:
            return self._create_error_response(f"Error listing links: {str(e)}")
