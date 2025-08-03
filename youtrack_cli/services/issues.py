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

            # Handle assignee field (custom field)
            if assignee is not None:
                custom_fields.append(
                    {
                        "$type": "SingleUserIssueCustomField",
                        "name": "Assignee",
                        "value": {"login": assignee} if assignee else None,
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

    async def _resolve_project_database_id(self, project_id_or_short_name: str) -> Optional[str]:
        """Resolve a project short name to database ID for move operations.

        Args:
            project_id_or_short_name: Project short name (e.g. 'DEMO') or database ID

        Returns:
            Database ID if found, None otherwise
        """
        try:
            from .projects import ProjectService

            project_service = ProjectService(self.auth_manager)
            result = await project_service.get_project(project_id_or_short_name, fields="id,shortName,name")

            if result["status"] == "success" and result["data"]:
                project_data = result["data"]
                return project_data.get("id")
            return None
        except Exception:
            return None

    async def _move_issue_to_project(self, issue_id: str, target_project_id: str) -> Dict[str, Any]:
        """Move an issue to a different project using YouTrack API.

        Args:
            issue_id: Issue ID to move
            target_project_id: Target project short name or database ID

        Returns:
            API response
        """
        try:
            # Resolve target project to database ID
            target_db_id = await self._resolve_project_database_id(target_project_id)
            if not target_db_id:
                return self._create_error_response(
                    f"Target project '{target_project_id}' not found. "
                    "Please check the project short name or ID and ensure you have access to it."
                )

            # Get current issue info for validation and feedback
            current_issue_result = await self.get_issue(
                issue_id, fields="id,idReadable,summary,project(id,shortName,name)"
            )
            if current_issue_result["status"] != "success":
                return self._create_error_response(
                    f"Unable to access issue '{issue_id}': {current_issue_result.get('message', 'Issue not found')}"
                )

            current_issue = current_issue_result["data"]
            current_project = current_issue.get("project", {})
            current_project_name = current_project.get("name", current_project.get("shortName", "Unknown"))

            # Check if already in target project
            if current_project.get("id") == target_db_id:
                return self._create_error_response(f"Issue '{issue_id}' is already in project '{target_project_id}'")

            # Make the API call to move the issue
            response = await self._make_request("POST", f"issues/{issue_id}/project", json_data={"id": target_db_id})

            result = await self._handle_response(response)

            # Enhance success message
            if result["status"] == "success":
                issue_readable_id = current_issue.get("idReadable", issue_id)
                result["message"] = (
                    f"Issue '{issue_readable_id}' successfully moved from '{current_project_name}' "
                    f"to '{target_project_id}'"
                )

            return result

        except Exception as e:
            return self._create_error_response(f"Error moving issue to project: {str(e)}")

    async def delete_issue(self, issue_id: str) -> Dict[str, Any]:
        """Delete an issue via API.

        Args:
            issue_id: Issue ID to delete

        Returns:
            API response
        """
        try:
            response = await self._make_request("DELETE", f"issues/{issue_id}")
            return await self._handle_response(response, success_codes=[200, 204])

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
            project_id: New project short name or database ID

        Returns:
            API response
        """
        try:
            if not state and not project_id:
                return self._create_error_response("Either state or project_id must be provided")

            # Handle project move
            if project_id:
                return await self._move_issue_to_project(issue_id, project_id)

            # Handle state field with dynamic discovery (same approach as update_issue)
            state_field_added = False
            try:
                # First, get the project ID from the issue
                project_id_from_issue = await self._get_project_id_from_issue(issue_id)
                if project_id_from_issue:
                    # Discover the correct state field for this project
                    state_field_info = await self._discover_state_field_for_project(project_id_from_issue)
                    if state_field_info:
                        # Use discovered field information
                        update_data = {
                            "$type": "Issue",
                            "customFields": [
                                {
                                    "$type": "SingleEnumIssueCustomField",
                                    "name": state_field_info["field_name"],
                                    "value": {"$type": state_field_info["bundle_type"], "name": state},
                                }
                            ],
                        }
                        state_field_added = True
                    else:
                        # Field discovery failed - get available fields for error message
                        from .projects import ProjectService

                        project_service = ProjectService(self.auth_manager)
                        fields_result = await project_service.get_project_custom_fields(
                            project_id_from_issue,
                            "id,name,fieldType,localizedName,isPublic,ordinal,field(fieldType,name)",
                        )

                        available_fields = []
                        if fields_result["status"] == "success":
                            available_fields = [
                                f.get("field", {}).get("name", "")
                                for f in fields_result["data"]
                                if f.get("field", {}).get("name")
                            ]

                        return self._create_error_response(
                            f"No state field found for project '{project_id_from_issue}'. "
                            f"Available custom fields: {', '.join(available_fields) if available_fields else 'None'}. "
                            f"Please check if the project has a state/status field configured."
                        )
            except Exception:
                # Log the exception but continue with fallback
                pass

            # Use fallback only if field discovery didn't work
            if not state_field_added:
                # Use StateBundleElement for state-type fields (consistent with update_issue logic)
                update_data = {
                    "$type": "Issue",
                    "customFields": [
                        {
                            "$type": "SingleEnumIssueCustomField",
                            "name": "State",
                            "value": {"$type": "StateBundleElement", "name": state},
                        }
                    ],
                }

            response = await self._make_request("POST", f"issues/{issue_id}", json_data=update_data)
            result = await self._handle_response(response)

            # Enhance error messages for common state field issues (same as update_issue)
            if result["status"] == "error":
                error_message = result.get("message", "").lower()

                # Check for common state field errors
                if "incompatible-issue-custom-field-name" in error_message or "state" in error_message:
                    # Try to get the project ID and available fields for better error message
                    try:
                        project_id_from_issue = await self._get_project_id_from_issue(issue_id)
                        if project_id_from_issue:
                            from .projects import ProjectService

                            project_service = ProjectService(self.auth_manager)

                            # Get state field info
                            state_field_result = await project_service.discover_state_field(project_id_from_issue)
                            if state_field_result["status"] == "success":
                                field_name = state_field_result["data"]["field_name"]
                                return self._create_error_response(
                                    f"State move failed. This project uses '{field_name}' instead of 'State'. "
                                    f'Try: yt issues move {issue_id} --state "{state}" '
                                    f"(Note: the CLI should handle this automatically, please report this as a bug)"
                                )
                            else:
                                # Get available fields
                                fields_result = await project_service.get_project_custom_fields(
                                    project_id_from_issue,
                                    "id,name,fieldType,localizedName,isPublic,ordinal,field(fieldType,name)",
                                )
                                available_fields = []
                                if fields_result["status"] == "success":
                                    available_fields = [
                                        f.get("field", {}).get("name", "")
                                        for f in fields_result["data"]
                                        if f.get("field", {}).get("name")
                                    ]

                                return self._create_error_response(
                                    f"State move failed. No state field found in project '{project_id_from_issue}'. "
                                    f"Available custom fields: {', '.join(available_fields) if available_fields else 'None'}. "
                                    f"Original error: {result['message']}"
                                )
                    except Exception:
                        # Continue with original error if enhanced error handling fails
                        pass

            # Return the original result without overriding the message
            return result

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
            # First, find the tag by name to get its ID
            tag_result = await self.find_tag_by_name(tag_name)

            if tag_result["status"] != "success" or not tag_result["data"]:
                return self._create_error_response(
                    f"Tag '{tag_name}' not found. Use 'yt tags create {tag_name}' to create it first."
                )

            tag_id = tag_result["data"]["id"]
            tag_data = {"id": tag_id}
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
            # First, find the tag by name to get its ID
            tag_result = await self.find_tag_by_name(tag_name)

            if tag_result["status"] != "success" or not tag_result["data"]:
                return self._create_error_response(f"Tag '{tag_name}' not found.")

            tag_id = tag_result["data"]["id"]
            response = await self._make_request("DELETE", f"issues/{issue_id}/tags/{tag_id}")
            return await self._handle_response(response, success_codes=[200, 204])

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
            return await self._handle_response(response, success_codes=[200, 204])

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
            from pathlib import Path

            import httpx

            # Extract filename from path
            filename = Path(file_path).name

            # Create multipart form data
            files = {"file": (filename, file_data, "application/octet-stream")}

            # Build the URL
            base_url = self._get_base_url()
            url = f"{base_url}/api/issues/{issue_id}/attachments"

            # Get authentication headers
            headers = self._get_auth_headers()
            # Don't set Content-Type manually - httpx will set it for multipart

            # Make the request with httpx directly for multipart support
            async with httpx.AsyncClient() as client:
                response = await client.post(url=url, headers=headers, files=files, timeout=30.0)

            # Handle the response
            if response.status_code == 200:
                try:
                    data = response.json() if response.text else {}
                    return {"status": "success", "message": "Attachment uploaded successfully", "data": data}
                except Exception:
                    # Success but no JSON response
                    return {"status": "success", "message": "Attachment uploaded successfully", "data": {}}
            else:
                return self._create_error_response(f"Upload failed with status {response.status_code}: {response.text}")

        except Exception as e:
            return self._create_error_response(f"Error uploading attachment: {str(e)}")

    async def download_attachment(self, issue_id: str, attachment_id: str) -> Dict[str, Any]:
        """Download an attachment from an issue via API.

        Args:
            issue_id: Issue ID
            attachment_id: Attachment ID

        Returns:
            API response containing attachment content and metadata
        """
        try:
            import httpx

            # Build the URL for attachment metadata
            base_url = self._get_base_url()
            metadata_url = f"{base_url}/api/issues/{issue_id}/attachments/{attachment_id}"

            # Get authentication headers
            headers = self._get_auth_headers()

            async with httpx.AsyncClient() as client:
                # First, get attachment metadata
                metadata_response = await client.get(
                    url=metadata_url,
                    headers=headers,
                    params={"fields": "id,name,size,mimeType,author(name),created,url,content"},
                    timeout=30.0,
                )

                if metadata_response.status_code != 200:
                    return self._create_error_response(
                        f"Failed to get attachment metadata: {metadata_response.status_code} - {metadata_response.text}"
                    )

                metadata = metadata_response.json()

                # Try to get URL from metadata first
                possible_urls = []

                # Check if metadata provides URL fields
                if "url" in metadata:
                    url_from_meta = metadata["url"]
                    if url_from_meta.startswith("/"):
                        possible_urls.append(f"{base_url}{url_from_meta}")
                    else:
                        possible_urls.append(url_from_meta)

                # Add standard URL patterns
                possible_urls.extend(
                    [
                        f"{base_url}/api/files/{attachment_id}",
                        f"{base_url}/files/{attachment_id}",
                        f"{base_url}/api/issues/{issue_id}/attachments/{attachment_id}/download",
                        f"{base_url}/api/issues/{issue_id}/attachments/{attachment_id}/content",
                    ]
                )

                for url_to_try in possible_urls:
                    content_response = await client.get(url=url_to_try, headers=headers, timeout=60.0)

                    if content_response.status_code == 200:
                        # Check if we got HTML instead of actual file content
                        content_type = content_response.headers.get("content-type", "")
                        if "text/html" in content_type:
                            # This is likely the login page, try next URL
                            continue

                        return {
                            "status": "success",
                            "message": f"Attachment downloaded successfully using {url_to_try}",
                            "data": {
                                "metadata": metadata,
                                "content": content_response.content,
                                "filename": metadata.get("name", f"attachment_{attachment_id}"),
                            },
                        }

                # If none worked, return error
                return self._create_error_response(
                    f"Could not find working download URL for attachment {attachment_id}. Tried: {', '.join(possible_urls)}"
                )

        except Exception as e:
            return self._create_error_response(f"Error downloading attachment: {str(e)}")

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
            return await self._handle_response(response, success_codes=[200, 204])

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
            params = {"fields": "id,name"}
            response = await self._make_request("GET", "tags", params=params)
            result = await self._handle_response(response)

            if result["status"] == "success":
                # Filter tags by name since API doesn't support name-based queries
                tags = result["data"]
                matching_tags = [tag for tag in tags if tag.get("name") == tag_name]
                result["data"] = matching_tags[0] if matching_tags else None

            return result

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
            response = await self._make_request("POST", "tags", json_data=tag_data)
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

    async def _resolve_issue_id(self, issue_id: str) -> str:
        """Resolve issue ID to internal format if needed.

        Args:
            issue_id: Issue ID (readable like FPU-1 or internal like 3-21)

        Returns:
            Internal issue ID
        """
        # If it looks like an internal ID already, return as-is
        if issue_id.count("-") == 1 and all(part.isdigit() for part in issue_id.split("-")):
            return issue_id

        # Otherwise, fetch the issue to get the internal ID
        result = await self.get_issue(issue_id, fields="id")
        if result["status"] == "success":
            return result["data"]["id"]
        else:
            # If we can't resolve it, return original and let the API handle the error
            return issue_id

    async def create_link(self, source_issue_id: str, target_issue_id: str, link_type_id: str) -> Dict[str, Any]:
        """Create a link between two issues via API.

        Args:
            source_issue_id: Source issue ID (readable or internal format)
            target_issue_id: Target issue ID (readable or internal format)
            link_type_id: Link type ID or name

        Returns:
            API response with creation result
        """
        try:
            # Resolve issue IDs to internal format
            source_issue_id = await self._resolve_issue_id(source_issue_id)
            target_issue_id = await self._resolve_issue_id(target_issue_id)
            # If link_type_id looks like a name (not an ID), we need to get the actual ID first
            if not (link_type_id.replace("-", "").replace("s", "").replace("t", "").isdigit()):
                # Get all link types to find the ID by name
                link_types_result = await self.list_link_types()
                if link_types_result["status"] != "success":
                    return link_types_result

                link_types = link_types_result["data"]
                matching_type = None
                for link_type in link_types:
                    if (
                        link_type.get("name", "").lower() == link_type_id.lower()
                        or link_type.get("sourceToTarget", "").lower() == link_type_id.lower()
                        or link_type.get("targetToSource", "").lower() == link_type_id.lower()
                    ):
                        matching_type = link_type
                        break

                if not matching_type:
                    return self._create_error_response(f"Link type '{link_type_id}' not found")

                # For directed links, determine direction
                base_link_id = matching_type["id"]
                if matching_type.get("directed", False):
                    # If user specified a directional name, use appropriate suffix
                    if link_type_id.lower() == matching_type.get("sourceToTarget", "").lower():
                        link_type_id = f"{base_link_id}s"  # outward link
                    elif link_type_id.lower() == matching_type.get("targetToSource", "").lower():
                        link_type_id = f"{base_link_id}t"  # inward link
                    else:
                        # Default to outward for directed links when just name is given
                        link_type_id = f"{base_link_id}s"
                else:
                    # Undirected link, use base ID
                    link_type_id = base_link_id

            # Create the link by posting to the source issue's links endpoint
            data = {"id": target_issue_id}
            response = await self._make_request(
                "POST", f"issues/{source_issue_id}/links/{link_type_id}/issues", json_data=data
            )

            if response.status_code == 200:
                return {
                    "status": "success",
                    "message": f"Link created between {source_issue_id} and {target_issue_id}",
                    "data": {},
                }
            else:
                return await self._handle_response(response)

        except ValueError as e:
            return self._create_error_response(str(e))
        except Exception as e:
            return self._create_error_response(f"Error creating link: {str(e)}")

    async def delete_link(self, source_issue_id: str, target_issue_id: str, link_type: str) -> Dict[str, Any]:
        """Delete a specific link between two issues via API.

        Args:
            source_issue_id: Source issue ID (readable or internal format)
            target_issue_id: Target issue ID (readable or internal format)
            link_type: Link type name or ID

        Returns:
            API response with deletion result
        """
        try:
            # Resolve issue IDs to internal format
            source_issue_id = await self._resolve_issue_id(source_issue_id)
            target_issue_id = await self._resolve_issue_id(target_issue_id)

            # Resolve link type to ID format
            if not (link_type.replace("-", "").replace("s", "").replace("t", "").isdigit()):
                # Get all link types to find the ID by name
                link_types_result = await self.list_link_types()
                if link_types_result["status"] != "success":
                    return link_types_result

                link_types = link_types_result["data"]
                matching_type = None
                for link_type_data in link_types:
                    if (
                        link_type_data.get("name", "").lower() == link_type.lower()
                        or link_type_data.get("sourceToTarget", "").lower() == link_type.lower()
                        or link_type_data.get("targetToSource", "").lower() == link_type.lower()
                    ):
                        matching_type = link_type_data
                        break

                if not matching_type:
                    return self._create_error_response(f"Link type '{link_type}' not found")

                # For directed links, determine direction
                base_link_id = matching_type["id"]
                if matching_type.get("directed", False):
                    # If user specified a directional name, use appropriate suffix
                    if link_type.lower() == matching_type.get("sourceToTarget", "").lower():
                        link_type_id = f"{base_link_id}s"  # outward link
                    elif link_type.lower() == matching_type.get("targetToSource", "").lower():
                        link_type_id = f"{base_link_id}t"  # inward link
                    else:
                        # Default to outward for directed links when just name is given
                        link_type_id = f"{base_link_id}s"
                else:
                    # Undirected link, use base ID
                    link_type_id = base_link_id
            else:
                link_type_id = link_type

            # Delete the link using the specific endpoint
            response = await self._make_request(
                "DELETE", f"issues/{source_issue_id}/links/{link_type_id}/issues/{target_issue_id}"
            )

            if response.status_code == 200:
                return {
                    "status": "success",
                    "message": f"Link deleted between {source_issue_id} and {target_issue_id}",
                    "data": {},
                }
            else:
                return await self._handle_response(response)

        except ValueError as e:
            return self._create_error_response(str(e))
        except Exception as e:
            return self._create_error_response(f"Error deleting link: {str(e)}")

    async def list_link_types(self, fields: Optional[str] = None) -> Dict[str, Any]:
        """List available issue link types via API.

        Args:
            fields: Comma-separated list of fields to return

        Returns:
            API response with link types list
        """
        try:
            params = {}
            if fields:
                params["fields"] = fields
            else:
                params["fields"] = "id,name,directed,sourceToTarget,targetToSource,aggregation,readOnly"

            response = await self._make_request("GET", "issueLinkTypes", params=params)
            return await self._handle_response(response)

        except ValueError as e:
            return self._create_error_response(str(e))
        except Exception as e:
            return self._create_error_response(f"Error listing link types: {str(e)}")
