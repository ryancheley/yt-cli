"""Issue manager for YouTrack CLI business logic."""

from typing import Any, Dict, List, Optional

from rich.table import Table

from ..auth import AuthManager
from ..console import get_console
from ..custom_field_manager import CustomFieldManager
from ..logging import get_logger
from ..pagination import create_paginated_display
from ..panels import (
    PanelGroup,
    create_custom_fields_panel,
    create_issue_details_panel,
    create_issue_overview_panel,
)
from ..services.issues import IssueService

__all__ = ["IssueManager"]

logger = get_logger(__name__)


class IssueManager:
    """Manages YouTrack issues business logic and presentation.

    This manager orchestrates issue operations using the IssueService
    for API communication and adds business logic, validation, and
    presentation formatting.
    """

    def __init__(self, auth_manager: AuthManager):
        self.auth_manager = auth_manager
        self.console = get_console()
        self.issue_service = IssueService(auth_manager)

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
        """Create a new issue with business logic and validation."""
        # Resolve project short name to internal ID if needed
        resolved_project_id = await self._resolve_project_id(project_id)
        if resolved_project_id is None:
            return {
                "status": "error",
                "message": f"Project '{project_id}' not found. Please check the project short name or ID.",
            }

        # Use service to create the issue
        result = await self.issue_service.create_issue(
            project_id=resolved_project_id,
            summary=summary,
            description=description,
            issue_type=issue_type,
            priority=priority,
            assignee=assignee,
        )

        # Add business logic for follow-up operations if needed
        if result["status"] == "success" and result["data"]:
            issue_data = result["data"]
            issue_id = issue_data.get("id")

            if issue_id:
                # Get the friendly ID (idReadable) for better user experience
                detail_result = await self.issue_service.get_issue(issue_id, fields="idReadable")
                if detail_result["status"] == "success":
                    friendly_id = detail_result["data"].get("idReadable")
                    if friendly_id:
                        result["friendly_id"] = friendly_id

        return result

    async def get_issue(self, issue_id: str) -> Dict[str, Any]:
        """Get issue details with enhanced presentation data."""
        return await self.issue_service.get_issue(issue_id)

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
        """Update an existing issue with validation."""
        return await self.issue_service.update_issue(
            issue_id=issue_id,
            summary=summary,
            description=description,
            state=state,
            priority=priority,
            assignee=assignee,
            issue_type=issue_type,
        )

    async def delete_issue(self, issue_id: str) -> Dict[str, Any]:
        """Delete an issue."""
        return await self.issue_service.delete_issue(issue_id)

    async def search_issues(
        self,
        query: str,
        project_id: Optional[str] = None,
        fields: Optional[str] = None,
        field_profile: Optional[str] = None,
        top: Optional[int] = None,
        skip: Optional[int] = None,
        format_output: str = "table",
        no_pagination: bool = False,
        use_cached_fields: bool = False,
        page_size: int = 100,
        after_cursor: Optional[str] = None,
        before_cursor: Optional[str] = None,
        use_pagination: bool = False,
        max_results: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Search issues with enhanced formatting and pagination."""
        # Handle field_profile parameter (legacy)
        if field_profile and not fields:
            fields = field_profile

        # Build the query with project filter if specified
        full_query = query
        if project_id:
            full_query = f"project: {project_id} {query}".strip()

        # Use service to search issues
        result = await self.issue_service.search_issues(
            query=full_query,
            fields=fields,
            top=top,
            skip=skip,
        )

        # Add count field for backward compatibility with command layer
        if result["status"] == "success" and "data" in result:
            issues = result["data"]
            if isinstance(issues, list):
                result["count"] = len(issues)

        # Add presentation logic for different output formats
        if result["status"] == "success" and format_output != "json":
            issues = result["data"]
            if isinstance(issues, list):
                result["formatted_output"] = self._format_issues_for_display(issues, format_output, no_pagination)

        return result

    async def assign_issue(self, issue_id: str, assignee: str) -> Dict[str, Any]:
        """Assign an issue to a user."""
        return await self.issue_service.assign_issue(issue_id, assignee)

    async def add_tag(self, issue_id: str, tag: str) -> Dict[str, Any]:
        """Add a tag to an issue with tag creation if needed."""
        # First try to add the tag directly
        result = await self.issue_service.add_tag(issue_id, tag)

        # If tag doesn't exist, try to create it first
        if result["status"] == "error" and "not found" in result["message"].lower():
            create_result = await self.issue_service.create_tag(tag)
            if create_result["status"] == "success":
                # Try adding the tag again
                result = await self.issue_service.add_tag(issue_id, tag)

        return result

    async def remove_tag(self, issue_id: str, tag: str) -> Dict[str, Any]:
        """Remove a tag from an issue."""
        return await self.issue_service.remove_tag(issue_id, tag)

    async def list_tags(self, issue_id: str) -> Dict[str, Any]:
        """List tags for an issue."""
        return await self.issue_service.list_tags(issue_id)

    async def add_comment(self, issue_id: str, text: str) -> Dict[str, Any]:
        """Add a comment to an issue."""
        return await self.issue_service.add_comment(issue_id, text)

    async def list_comments(self, issue_id: str) -> Dict[str, Any]:
        """List comments for an issue."""
        return await self.issue_service.list_comments(issue_id)

    async def update_comment(self, issue_id: str, comment_id: str, text: str) -> Dict[str, Any]:
        """Update a comment."""
        return await self.issue_service.update_comment(issue_id, comment_id, text)

    async def delete_comment(self, issue_id: str, comment_id: str) -> Dict[str, Any]:
        """Delete a comment."""
        return await self.issue_service.delete_comment(issue_id, comment_id)

    async def upload_attachment(self, issue_id: str, file_path: str) -> Dict[str, Any]:
        """Upload an attachment to an issue."""
        try:
            # Read file data
            with open(file_path, "rb") as f:
                file_data = f.read()

            return await self.issue_service.upload_attachment(issue_id, file_path, file_data)
        except Exception as e:
            return {"status": "error", "message": f"Error reading file: {str(e)}"}

    async def list_attachments(self, issue_id: str) -> Dict[str, Any]:
        """List attachments for an issue."""
        return await self.issue_service.list_attachments(issue_id)

    async def delete_attachment(self, issue_id: str, attachment_id: str) -> Dict[str, Any]:
        """Delete an attachment."""
        return await self.issue_service.delete_attachment(issue_id, attachment_id)

    async def get_or_create_tag(self, tag_name: str) -> Dict[str, Any]:
        """Get an existing tag or create it if it doesn't exist."""
        # First try to find the tag
        result = await self.issue_service.find_tag_by_name(tag_name)

        if result["status"] == "success" and result["data"]:
            # Tag exists
            return result

        # Tag doesn't exist, create it
        return await self.issue_service.create_tag(tag_name)

    def _format_issues_for_display(
        self, issues: List[Dict[str, Any]], format_type: str, no_pagination: bool = False
    ) -> str:
        """Format issues for CLI display."""
        if not issues:
            return "No issues found."

        if format_type == "csv":
            return self._format_issues_as_csv(issues)
        elif format_type == "table":
            return self._format_issues_as_table(issues, no_pagination)
        else:
            return str(issues)

    def _format_issues_as_csv(self, issues: List[Dict[str, Any]]) -> str:
        """Format issues data as CSV."""
        import csv
        import io

        if not issues:
            return "ID,Summary,State,Priority,Type,Assignee,Project\n"

        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        headers = ["ID", "Summary", "State", "Priority", "Type", "Assignee", "Project"]
        writer.writerow(headers)

        # Write data rows
        for issue in issues:
            # Extract project info
            project_name = ""
            if isinstance(issue.get("project"), dict):
                project_name = issue["project"].get("name", issue["project"].get("shortName", ""))

            # Extract assignee info
            assignee_name = self._get_assignee_name(issue)

            # Extract other fields
            state = self._get_custom_field_value(issue, "State") or ""
            priority = self._get_custom_field_value(issue, "Priority") or ""
            issue_type = self._get_custom_field_value(issue, "Type") or ""

            writer.writerow(
                [
                    issue.get("idReadable", issue.get("id", "")),
                    issue.get("summary", ""),
                    state,
                    priority,
                    issue_type,
                    assignee_name,
                    project_name,
                ]
            )

        return output.getvalue()

    def _format_issues_as_table(self, issues: List[Dict[str, Any]], no_pagination: bool = False) -> str:
        """Format issues as a Rich table."""
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Summary", style="green")
        table.add_column("State", style="yellow")
        table.add_column("Priority", style="red")
        table.add_column("Assignee", style="blue")

        for issue in issues:
            assignee_name = self._get_assignee_name(issue)
            state = self._get_custom_field_value(issue, "State") or ""
            priority = self._get_custom_field_value(issue, "Priority") or ""

            table.add_row(
                issue.get("idReadable", issue.get("id", "")),
                issue.get("summary", ""),
                state,
                priority,
                assignee_name,
            )

        # Convert table to string for return
        with self.console.capture() as capture:
            self.console.print(table)

        return capture.get()

    async def _resolve_project_id(self, project_id_or_short_name: str) -> Optional[str]:
        """Resolve a project ID or short name to internal project ID."""
        # This is a business logic helper that would use the ProjectService
        # For now, return the input as-is (this would need ProjectService integration)
        return project_id_or_short_name

    def display_issue_details(
        self, issue: Dict[str, Any], show_comments: bool = False, format_type: str = "table"
    ) -> None:
        """Display issue details with rich formatting."""
        if not issue:
            self.console.print("[red]No issue data to display[/red]")
            return

        # Create panels for different sections
        overview_panel = create_issue_overview_panel(issue)
        details_panel = create_issue_details_panel(issue)
        custom_fields_panel = create_custom_fields_panel(issue.get("customFields", []))

        # Create panel group
        panel_group = PanelGroup("Issue Details")
        panel_group.add_panel(overview_panel)
        panel_group.add_panel(details_panel)
        panel_group.add_panel(custom_fields_panel)

        # Display the panels
        self.console.print(panel_group)

        # Show comments if requested
        if show_comments:
            # This would require an async context, so we'll skip for now
            pass

    async def list_issues(
        self,
        project_id: Optional[str] = None,
        query: Optional[str] = None,
        fields: Optional[str] = None,
        field_profile: Optional[str] = None,
        top: Optional[int] = None,
        skip: Optional[int] = None,
        format_output: str = "table",
        no_pagination: bool = False,
        use_cached_fields: bool = False,
        page_size: int = 100,
        after_cursor: Optional[str] = None,
        before_cursor: Optional[str] = None,
        use_pagination: bool = False,
        max_results: Optional[int] = None,
        paginated: bool = False,
        show_all: bool = False,
        start_page: int = 1,
        display_page_size: int = 50,
        state: Optional[str] = None,
        assignee: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List issues with enhanced filtering and pagination."""
        # Handle field_profile parameter (legacy)
        if field_profile and not fields:
            fields = field_profile

        # Build query from parameters
        if query is None:
            query = ""

        # Add state filter to query if provided
        if state:
            query = f"State: {state} {query}".strip()

        # Add assignee filter to query if provided
        if assignee:
            query = f"Assignee: {assignee} {query}".strip()

        return await self.search_issues(
            query=query,
            project_id=project_id,
            fields=fields,
            top=top,
            skip=skip,
            format_output=format_output,
            no_pagination=no_pagination,
            use_cached_fields=use_cached_fields,
        )

    def display_issues_table(self, issues: List[Dict[str, Any]]) -> None:
        """Display issues in a simple table format."""
        self.display_issue_list(issues, format_output="table", no_pagination=True)

    def display_issues_table_paginated(
        self,
        issues: List[Dict[str, Any]],
        page_size: int = 50,
        show_all: bool = False,
        start_page: int = 1,
    ) -> None:
        """Display issues in a paginated table format."""
        if not issues:
            self.console.print("[yellow]No issues found.[/yellow]")
            return

        def build_issues_table(issue_subset: List[Dict[str, Any]]) -> Any:
            """Build a Rich table for the given subset of issues."""
            from rich.table import Table

            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("ID", style="cyan", no_wrap=True)
            table.add_column("Summary", style="green")
            table.add_column("State", style="yellow")
            table.add_column("Priority", style="red")
            table.add_column("Assignee", style="blue")

            for issue in issue_subset:
                assignee_name = self._get_assignee_name(issue)
                state = self._get_custom_field_value(issue, "State") or ""
                priority = self._get_custom_field_value(issue, "Priority") or ""

                table.add_row(
                    issue.get("idReadable", issue.get("id", "")),
                    issue.get("summary", ""),
                    state,
                    priority,
                    assignee_name,
                )

            return table

        # Use pagination display
        paginated_display = create_paginated_display(self.console, page_size)
        paginated_display.display_paginated_table(
            issues, build_issues_table, "Issues", show_all=show_all, start_page=start_page
        )

    async def list_links(self, issue_id: str) -> Dict[str, Any]:
        """List links for an issue."""
        return await self.issue_service.list_links(issue_id)

    def display_links_table(self, links: List[Dict[str, Any]]) -> None:
        """Display links in a table format."""
        if not links:
            self.console.print("[yellow]No links found.[/yellow]")
            return

        from rich.table import Table

        table = Table(title="Issue Links")
        table.add_column("Direction", style="cyan", no_wrap=True)
        table.add_column("Type", style="blue")
        table.add_column("Linked Issue", style="green")
        table.add_column("Summary", style="white")

        for link in links:
            direction = link.get("direction", "")
            link_type = link.get("linkType", {}).get("name", "")

            # Handle different link structures
            if "issues" in link:
                for linked_issue in link["issues"]:
                    issue_id = linked_issue.get("idReadable", linked_issue.get("id", ""))
                    summary = linked_issue.get("summary", "")
                    table.add_row(direction, link_type, issue_id, summary)
            else:
                # Handle direct link structure
                linked_issue_id = link.get("issue", {}).get("idReadable", "")
                linked_summary = link.get("issue", {}).get("summary", "")
                table.add_row(direction, link_type, linked_issue_id, linked_summary)

        self.console.print(table)

    async def move_issue(
        self, issue_id: str, state: Optional[str] = None, project_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Move an issue to a different state or project."""
        if not state and not project_id:
            return {"status": "error", "message": "Either state or project_id must be provided"}

        if state:
            # Move to different state
            return await self.update_issue(issue_id, state=state)
        elif project_id:
            # Move to different project - would need project service integration
            return {"status": "error", "message": "Moving issues between projects not yet implemented"}

        # This should never be reached, but adding for type safety
        return {"status": "error", "message": "Invalid parameters"}

    def display_comments_table(self, comments: List[Dict[str, Any]]) -> None:
        """Display comments in a table format."""
        if not comments:
            self.console.print("[yellow]No comments found.[/yellow]")
            return

        from rich.table import Table

        table = Table(title="Issue Comments")
        table.add_column("Author", style="cyan", no_wrap=True)
        table.add_column("Date", style="blue")
        table.add_column("Comment", style="white")

        for comment in comments:
            author = comment.get("author", {}).get("fullName", "Unknown")
            created = comment.get("created", "")
            text = comment.get("text", "")

            # Limit comment text length for table display
            if len(text) > 100:
                text = text[:97] + "..."

            table.add_row(author, created, text)

        self.console.print(table)

    async def download_attachment(
        self, issue_id: str, attachment_id: str, output: Optional[str] = None
    ) -> Dict[str, Any]:
        """Download an attachment from an issue."""
        # This would need to be implemented in the service layer
        return {"status": "error", "message": "Attachment download not yet implemented in service layer"}

    def display_attachments_table(self, attachments: List[Dict[str, Any]]) -> None:
        """Display attachments in a table format."""
        if not attachments:
            self.console.print("[yellow]No attachments found.[/yellow]")
            return

        from rich.table import Table

        table = Table(title="Issue Attachments")
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Size", style="blue")
        table.add_column("Author", style="green")
        table.add_column("Created", style="yellow")

        for attachment in attachments:
            name = attachment.get("name", "N/A")
            size = attachment.get("size", "N/A")
            author = attachment.get("author", {}).get("fullName", "Unknown")
            created = attachment.get("created", "")

            table.add_row(name, str(size), author, created)

        self.console.print(table)

    async def create_link(self, source_issue_id: str, target_issue_id: str, link_type: str) -> Dict[str, Any]:
        """Create a link between two issues."""
        # This would need to be implemented in the service layer
        return {"status": "error", "message": "Issue linking not yet implemented in service layer"}

    async def delete_link(self, source_issue_id: str, link_id: str) -> Dict[str, Any]:
        """Delete a link between issues."""
        # This would need to be implemented in the service layer
        return {"status": "error", "message": "Issue link deletion not yet implemented in service layer"}

    async def list_link_types(self) -> Dict[str, Any]:
        """List available link types."""
        # This would need to be implemented in the service layer
        return {"status": "error", "message": "Link types listing not yet implemented in service layer"}

    def display_link_types_table(self, link_types: List[Dict[str, Any]]) -> None:
        """Display link types in a table format."""
        if not link_types:
            self.console.print("[yellow]No link types found.[/yellow]")
            return

        from rich.table import Table

        table = Table(title="Issue Link Types")
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Description", style="green")
        table.add_column("Directed", style="yellow")

        for link_type in link_types:
            name = link_type.get("name", "N/A")
            description = link_type.get("description", "")
            directed = "Yes" if link_type.get("directed", False) else "No"

            table.add_row(name, description, directed)

        self.console.print(table)

    def display_issue_list(
        self,
        issues: List[Dict[str, Any]],
        format_output: str = "table",
        no_pagination: bool = False,
    ) -> None:
        """Display a list of issues with formatting."""
        if not issues:
            self.console.print("[yellow]No issues found.[/yellow]")
            return

        formatted_output = self._format_issues_for_display(issues, format_output, no_pagination)

        if format_output == "table" and not no_pagination:
            # Use paginated display for tables
            create_paginated_display(formatted_output, self.console)
        else:
            self.console.print(formatted_output)
