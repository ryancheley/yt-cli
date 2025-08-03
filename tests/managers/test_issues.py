"""Tests for IssueManager."""

import tempfile
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from youtrack_cli.auth import AuthManager
from youtrack_cli.managers.issues import IssueManager


@pytest.fixture
def auth_manager():
    """Create a mock auth manager."""
    mock_auth = MagicMock(spec=AuthManager)
    return mock_auth


@pytest.fixture
def issue_manager(auth_manager):
    """Create an IssueManager instance."""
    with (
        patch("youtrack_cli.managers.issues.get_console") as mock_console,
        patch("youtrack_cli.managers.issues.IssueService"),
        patch("youtrack_cli.managers.issues.ProjectService"),
    ):
        manager = IssueManager(auth_manager)
        manager.console = mock_console.return_value

        # Make the service methods async
        manager.issue_service = MagicMock()
        manager.project_service = MagicMock()

        # Set up async methods
        for method_name in [
            "create_issue",
            "get_issue",
            "update_issue",
            "delete_issue",
            "search_issues",
            "assign_issue",
            "add_tag",
            "remove_tag",
            "list_tags",
            "find_tag_by_name",
            "create_tag",
            "add_comment",
            "list_comments",
            "update_comment",
            "delete_comment",
            "upload_attachment",
            "download_attachment",
            "list_attachments",
            "delete_attachment",
            "list_links",
            "move_issue",
        ]:
            setattr(manager.issue_service, method_name, AsyncMock())

        for method_name in ["get_project"]:
            setattr(manager.project_service, method_name, AsyncMock())

        return manager


@pytest.fixture
def sample_issue():
    """Create sample issue data."""
    return {
        "id": "test-123",
        "idReadable": "TEST-123",
        "summary": "Test Issue",
        "description": "Test description",
        "assignee": {"login": "testuser", "fullName": "Test User"},
        "project": {"id": "project-1", "name": "Test Project", "shortName": "TEST"},
        "customFields": [
            {"name": "State", "value": {"name": "Open"}},
            {"name": "Priority", "value": {"name": "High"}},
            {"name": "Type", "value": {"name": "Bug"}},
        ],
    }


class TestIssueManagerCreation:
    """Test issue creation functionality."""

    @pytest.mark.asyncio
    async def test_create_issue_success(self, issue_manager):
        """Test successful issue creation."""
        # Mock project resolution
        issue_manager.project_service.get_project.return_value = {
            "status": "success",
            "data": {"id": "project-123", "shortName": "TEST"},
        }

        # Mock issue creation
        issue_manager.issue_service.create_issue.return_value = {"status": "success", "data": {"id": "issue-123"}}

        # Mock getting friendly ID
        issue_manager.issue_service.get_issue.return_value = {"status": "success", "data": {"idReadable": "TEST-123"}}

        result = await issue_manager.create_issue(project_id="TEST", summary="Test Issue")

        assert result["status"] == "success"
        assert result["message"] == "Issue TEST-123 created successfully"
        assert result["friendly_id"] == "TEST-123"

    @pytest.mark.asyncio
    async def test_create_issue_project_not_found(self, issue_manager):
        """Test issue creation with invalid project."""
        # Mock project resolution returning None
        with patch.object(issue_manager, "_resolve_project_id", return_value=None):
            result = await issue_manager.create_issue(project_id="INVALID", summary="Test Issue")

        assert result["status"] == "error"
        assert "not found" in result["message"]

    @pytest.mark.asyncio
    async def test_create_issue_service_failure(self, issue_manager):
        """Test issue creation when service fails."""
        # Mock project resolution
        issue_manager.project_service.get_project.return_value = {"status": "success", "data": {"id": "project-123"}}

        # Mock issue service failure
        issue_manager.issue_service.create_issue.return_value = {"status": "error", "message": "API error"}

        result = await issue_manager.create_issue(project_id="TEST", summary="Test Issue")

        assert result["status"] == "error"


class TestIssueManagerRetrieval:
    """Test issue retrieval functionality."""

    @pytest.mark.asyncio
    async def test_get_issue(self, issue_manager):
        """Test getting an issue."""
        expected_result = {"status": "success", "data": {"id": "TEST-123"}}
        issue_manager.issue_service.get_issue.return_value = expected_result

        result = await issue_manager.get_issue("TEST-123")

        issue_manager.issue_service.get_issue.assert_called_once_with("TEST-123")
        assert result == expected_result

    @pytest.mark.asyncio
    async def test_search_issues_basic(self, issue_manager, sample_issue):
        """Test basic issue search."""
        issue_manager.issue_service.search_issues.return_value = {"status": "success", "data": [sample_issue]}

        result = await issue_manager.search_issues("assignee: me")

        assert result["status"] == "success"
        assert result["count"] == 1
        assert "formatted_output" in result

    @pytest.mark.asyncio
    async def test_search_issues_with_project_filter(self, issue_manager):
        """Test search with project filter."""
        issue_manager.issue_service.search_issues.return_value = {"status": "success", "data": []}

        await issue_manager.search_issues("assignee: me", project_id="TEST")

        # Verify query was modified to include project filter
        call_args = issue_manager.issue_service.search_issues.call_args
        assert "project: TEST" in call_args[1]["query"]

    @pytest.mark.asyncio
    async def test_list_issues_with_filters(self, issue_manager):
        """Test list issues with state and assignee filters."""
        issue_manager.issue_service.search_issues.return_value = {"status": "success", "data": []}

        await issue_manager.list_issues(state="Open", assignee="testuser")

        # Verify filters were added to query
        call_args = issue_manager.issue_service.search_issues.call_args
        query = call_args[1]["query"]
        assert "State: Open" in query
        assert "Assignee: testuser" in query


class TestIssueManagerUpdate:
    """Test issue update functionality."""

    @pytest.mark.asyncio
    async def test_update_issue(self, issue_manager):
        """Test updating an issue."""
        expected_result = {"status": "success"}
        issue_manager.issue_service.update_issue.return_value = expected_result

        result = await issue_manager.update_issue("TEST-123", summary="New Summary")

        issue_manager.issue_service.update_issue.assert_called_once_with(
            issue_id="TEST-123",
            summary="New Summary",
            description=None,
            state=None,
            priority=None,
            assignee=None,
            issue_type=None,
        )
        assert result == expected_result

    @pytest.mark.asyncio
    async def test_assign_issue(self, issue_manager):
        """Test assigning an issue."""
        expected_result = {"status": "success"}
        issue_manager.issue_service.assign_issue.return_value = expected_result

        result = await issue_manager.assign_issue("TEST-123", "testuser")

        issue_manager.issue_service.assign_issue.assert_called_once_with("TEST-123", "testuser")
        assert result == expected_result

    @pytest.mark.asyncio
    async def test_move_issue(self, issue_manager):
        """Test moving an issue."""
        expected_result = {"status": "success"}
        issue_manager.issue_service.move_issue.return_value = expected_result

        result = await issue_manager.move_issue("TEST-123", state="In Progress")

        issue_manager.issue_service.move_issue.assert_called_once_with("TEST-123", state="In Progress", project_id=None)
        assert result == expected_result


class TestIssueManagerDelete:
    """Test issue deletion functionality."""

    @pytest.mark.asyncio
    async def test_delete_issue(self, issue_manager):
        """Test deleting an issue."""
        expected_result = {"status": "success"}
        issue_manager.issue_service.delete_issue.return_value = expected_result

        result = await issue_manager.delete_issue("TEST-123")

        issue_manager.issue_service.delete_issue.assert_called_once_with("TEST-123")
        assert result == expected_result


class TestIssueManagerTags:
    """Test tag-related functionality."""

    @pytest.mark.asyncio
    async def test_add_tag_success(self, issue_manager):
        """Test adding a tag successfully."""
        issue_manager.issue_service.add_tag.return_value = {"status": "success"}

        result = await issue_manager.add_tag("TEST-123", "urgent")

        issue_manager.issue_service.add_tag.assert_called_once_with("TEST-123", "urgent")
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_add_tag_create_if_not_found(self, issue_manager):
        """Test adding a tag that doesn't exist - should create it."""
        # First call fails with tag not found
        issue_manager.issue_service.add_tag.side_effect = [
            {"status": "error", "message": "Tag not found"},
            {"status": "success"},  # Second call succeeds
        ]

        # Tag creation succeeds
        issue_manager.issue_service.create_tag.return_value = {"status": "success"}

        result = await issue_manager.add_tag("TEST-123", "newtag", create_if_missing=True)

        # Verify create_tag was called
        issue_manager.issue_service.create_tag.assert_called_once_with("newtag")
        # Verify add_tag was called twice
        assert issue_manager.issue_service.add_tag.call_count == 2
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_remove_tag(self, issue_manager):
        """Test removing a tag."""
        expected_result = {"status": "success"}
        issue_manager.issue_service.remove_tag.return_value = expected_result

        result = await issue_manager.remove_tag("TEST-123", "urgent")

        issue_manager.issue_service.remove_tag.assert_called_once_with("TEST-123", "urgent")
        assert result == expected_result

    @pytest.mark.asyncio
    async def test_list_tags(self, issue_manager):
        """Test listing tags."""
        expected_result = {"status": "success", "data": [{"name": "urgent"}]}
        issue_manager.issue_service.list_tags.return_value = expected_result

        result = await issue_manager.list_tags("TEST-123")

        issue_manager.issue_service.list_tags.assert_called_once_with("TEST-123")
        assert result == expected_result

    @pytest.mark.asyncio
    async def test_get_or_create_tag_exists(self, issue_manager):
        """Test get_or_create_tag when tag exists."""
        issue_manager.issue_service.find_tag_by_name.return_value = {
            "status": "success",
            "data": [{"id": "tag-1", "name": "urgent"}],
        }

        result = await issue_manager.get_or_create_tag("urgent")

        issue_manager.issue_service.find_tag_by_name.assert_called_once_with("urgent")
        issue_manager.issue_service.create_tag.assert_not_called()
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_get_or_create_tag_creates(self, issue_manager):
        """Test get_or_create_tag when tag doesn't exist."""
        issue_manager.issue_service.find_tag_by_name.return_value = {"status": "success", "data": []}
        issue_manager.issue_service.create_tag.return_value = {
            "status": "success",
            "data": {"id": "tag-1", "name": "newtag"},
        }

        result = await issue_manager.get_or_create_tag("newtag")

        issue_manager.issue_service.find_tag_by_name.assert_called_once_with("newtag")
        issue_manager.issue_service.create_tag.assert_called_once_with("newtag")
        assert result["status"] == "success"


class TestIssueManagerComments:
    """Test comment-related functionality."""

    @pytest.mark.asyncio
    async def test_add_comment(self, issue_manager):
        """Test adding a comment."""
        expected_result = {"status": "success"}
        issue_manager.issue_service.add_comment.return_value = expected_result

        result = await issue_manager.add_comment("TEST-123", "Test comment")

        issue_manager.issue_service.add_comment.assert_called_once_with("TEST-123", "Test comment")
        assert result == expected_result

    @pytest.mark.asyncio
    async def test_list_comments(self, issue_manager):
        """Test listing comments."""
        expected_result = {"status": "success", "data": []}
        issue_manager.issue_service.list_comments.return_value = expected_result

        result = await issue_manager.list_comments("TEST-123")

        issue_manager.issue_service.list_comments.assert_called_once_with("TEST-123")
        assert result == expected_result

    @pytest.mark.asyncio
    async def test_update_comment(self, issue_manager):
        """Test updating a comment."""
        expected_result = {"status": "success"}
        issue_manager.issue_service.update_comment.return_value = expected_result

        result = await issue_manager.update_comment("TEST-123", "comment-1", "Updated text")

        issue_manager.issue_service.update_comment.assert_called_once_with("TEST-123", "comment-1", "Updated text")
        assert result == expected_result

    @pytest.mark.asyncio
    async def test_delete_comment(self, issue_manager):
        """Test deleting a comment."""
        expected_result = {"status": "success"}
        issue_manager.issue_service.delete_comment.return_value = expected_result

        result = await issue_manager.delete_comment("TEST-123", "comment-1")

        issue_manager.issue_service.delete_comment.assert_called_once_with("TEST-123", "comment-1")
        assert result == expected_result


class TestIssueManagerAttachments:
    """Test attachment-related functionality."""

    @pytest.mark.asyncio
    async def test_upload_attachment_success(self, issue_manager):
        """Test uploading an attachment."""
        issue_manager.issue_service.upload_attachment.return_value = {"status": "success"}

        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(b"test content")
            temp_path = temp_file.name

        try:
            result = await issue_manager.upload_attachment("TEST-123", temp_path)

            issue_manager.issue_service.upload_attachment.assert_called_once_with(
                "TEST-123", temp_path, b"test content"
            )
            assert result["status"] == "success"
        finally:
            import os

            os.unlink(temp_path)

    @pytest.mark.asyncio
    async def test_upload_attachment_file_error(self, issue_manager):
        """Test uploading attachment with file error."""
        result = await issue_manager.upload_attachment("TEST-123", "/nonexistent/file")

        assert result["status"] == "error"
        assert "Error reading file" in result["message"]

    @pytest.mark.asyncio
    async def test_list_attachments(self, issue_manager):
        """Test listing attachments."""
        expected_result = {"status": "success", "data": []}
        issue_manager.issue_service.list_attachments.return_value = expected_result

        result = await issue_manager.list_attachments("TEST-123")

        issue_manager.issue_service.list_attachments.assert_called_once_with("TEST-123")
        assert result == expected_result

    @pytest.mark.asyncio
    async def test_delete_attachment(self, issue_manager):
        """Test deleting an attachment."""
        expected_result = {"status": "success"}
        issue_manager.issue_service.delete_attachment.return_value = expected_result

        result = await issue_manager.delete_attachment("TEST-123", "attachment-1")

        issue_manager.issue_service.delete_attachment.assert_called_once_with("TEST-123", "attachment-1")
        assert result == expected_result

    @pytest.mark.asyncio
    async def test_download_attachment_success(self, issue_manager):
        """Test successful attachment download."""
        # Mock the service layer response
        issue_manager.issue_service.download_attachment.return_value = {
            "status": "success",
            "data": {"content": b"test content", "filename": "test.txt", "metadata": {"name": "test.txt", "size": 12}},
        }

        with patch("pathlib.Path.write_bytes") as mock_write:
            result = await issue_manager.download_attachment("TEST-123", "attachment-1", "output.txt")

            assert result["status"] == "success"
            assert "Attachment downloaded successfully" in result["message"]
            mock_write.assert_called_once_with(b"test content")
            issue_manager.issue_service.download_attachment.assert_called_once_with("TEST-123", "attachment-1")


class TestIssueManagerLinks:
    """Test link-related functionality."""

    @pytest.mark.asyncio
    async def test_list_links(self, issue_manager):
        """Test listing links."""
        expected_result = {"status": "success", "data": []}
        issue_manager.issue_service.list_links.return_value = expected_result

        result = await issue_manager.list_links("TEST-123")

        issue_manager.issue_service.list_links.assert_called_once_with("TEST-123")
        assert result == expected_result

    @pytest.mark.asyncio
    async def test_create_link(self, issue_manager):
        """Test create link calls service layer."""
        expected_result = {"status": "success", "message": "Link created"}
        issue_manager.issue_service.create_link = AsyncMock(return_value=expected_result)

        result = await issue_manager.create_link("TEST-123", "TEST-456", "relates to")

        assert result == expected_result
        issue_manager.issue_service.create_link.assert_called_once_with("TEST-123", "TEST-456", "relates to")

    @pytest.mark.asyncio
    async def test_delete_link(self, issue_manager):
        """Test delete link calls service layer."""
        expected_result = {"status": "success", "message": "Link deleted"}
        issue_manager.issue_service.delete_link = AsyncMock(return_value=expected_result)

        result = await issue_manager.delete_link("TEST-123", "TEST-456", "relates to")

        assert result == expected_result
        issue_manager.issue_service.delete_link.assert_called_once_with("TEST-123", "TEST-456", "relates to")

    @pytest.mark.asyncio
    async def test_list_link_types(self, issue_manager):
        """Test list link types calls service layer."""
        expected_result = {"status": "success", "data": []}
        issue_manager.issue_service.list_link_types = AsyncMock(return_value=expected_result)

        result = await issue_manager.list_link_types()

        assert result == expected_result
        issue_manager.issue_service.list_link_types.assert_called_once()


class TestIssueManagerUtilities:
    """Test utility functions."""

    def test_get_custom_field_value(self, issue_manager, sample_issue):
        """Test extracting custom field values."""
        with patch("youtrack_cli.managers.issues.CustomFieldManager") as mock_cfm:
            mock_cfm.extract_field_value.return_value = "High"

            result = issue_manager._get_custom_field_value(sample_issue, "Priority")

            mock_cfm.extract_field_value.assert_called_once_with(sample_issue["customFields"], "Priority")
            assert result == "High"

    def test_get_assignee_name_from_regular_field(self, issue_manager, sample_issue):
        """Test getting assignee name from regular field."""
        result = issue_manager._get_assignee_name(sample_issue)
        assert result == "Test User"

    def test_get_assignee_name_unassigned(self, issue_manager):
        """Test getting assignee name when unassigned."""
        issue = {"assignee": None}
        with patch.object(issue_manager, "_get_custom_field_value", return_value=None):
            result = issue_manager._get_assignee_name(issue)
            assert result == "Unassigned"

    def test_get_state_field_value(self, issue_manager, sample_issue):
        """Test getting state field value."""
        with patch.object(issue_manager, "_get_custom_field_value", side_effect=["Open", None, None, None]):
            result = issue_manager._get_state_field_value(sample_issue)
            assert result == "Open"

    @pytest.mark.asyncio
    async def test_resolve_project_id_success(self, issue_manager):
        """Test successful project ID resolution."""
        issue_manager.project_service.get_project.return_value = {
            "status": "success",
            "data": {"id": "project-123", "shortName": "TEST"},
        }

        result = await issue_manager._resolve_project_id("TEST")
        assert result == "project-123"

    @pytest.mark.asyncio
    async def test_resolve_project_id_not_found(self, issue_manager):
        """Test project ID resolution when project not found."""
        issue_manager.project_service.get_project.return_value = {"status": "error", "message": "Not found"}

        result = await issue_manager._resolve_project_id("INVALID")
        assert result is None

    @pytest.mark.asyncio
    async def test_resolve_project_id_exception(self, issue_manager):
        """Test project ID resolution with exception."""
        issue_manager.project_service.get_project.side_effect = Exception("Network error")

        result = await issue_manager._resolve_project_id("TEST")
        assert result is None


class TestIssueManagerFormatting:
    """Test formatting functionality."""

    def test_format_issues_for_display_empty(self, issue_manager):
        """Test formatting empty issue list."""
        result = issue_manager._format_issues_for_display([], "table")
        assert result == "No issues found."

    def test_format_issues_for_display_csv(self, issue_manager, sample_issue):
        """Test formatting issues as CSV."""
        with (
            patch.object(issue_manager, "_get_assignee_name", return_value="Test User"),
            patch.object(issue_manager, "_get_state_field_value", return_value="Open"),
            patch.object(issue_manager, "_get_custom_field_value", side_effect=["High", "Bug"]),
        ):
            result = issue_manager._format_issues_for_display([sample_issue], "csv")

            assert "ID,Summary,State,Priority,Type,Assignee,Project" in result
            assert "TEST-123,Test Issue,Open,High,Bug,Test User,Test Project" in result

    def test_format_issues_for_display_table(self, issue_manager, sample_issue):
        """Test formatting issues as table."""
        mock_console = MagicMock()
        mock_console.capture.return_value.__enter__.return_value.get.return_value = "table output"
        issue_manager.console = mock_console

        with (
            patch.object(issue_manager, "_get_assignee_name", return_value="Test User"),
            patch.object(issue_manager, "_get_state_field_value", return_value="Open"),
            patch.object(issue_manager, "_get_custom_field_value", return_value="High"),
        ):
            result = issue_manager._format_issues_for_display([sample_issue], "table")
            assert result == "table output"

    def test_display_issue_details(self, issue_manager, sample_issue):
        """Test displaying issue details."""
        with (
            patch("youtrack_cli.managers.issues.create_issue_overview_panel") as mock_overview,
            patch("youtrack_cli.managers.issues.create_issue_details_panel") as mock_details,
            patch("youtrack_cli.managers.issues.create_custom_fields_panel") as mock_fields,
            patch("youtrack_cli.managers.issues.PanelGroup") as mock_panel_group,
        ):
            issue_manager.display_issue_details(sample_issue)

            mock_overview.assert_called_once_with(sample_issue)
            mock_details.assert_called_once_with(sample_issue)
            mock_fields.assert_called_once_with(sample_issue["customFields"])
            mock_panel_group.assert_called_once_with("Issue Details")

    def test_display_issue_details_empty(self, issue_manager):
        """Test displaying issue details with no data."""
        issue_manager.display_issue_details(None)

        issue_manager.console.print.assert_called_once_with("[red]No issue data to display[/red]")

    def test_display_issues_table(self, issue_manager, sample_issue):
        """Test displaying issues table."""
        with (
            patch.object(issue_manager, "_get_assignee_name", return_value="Test User"),
            patch.object(issue_manager, "_get_state_field_value", return_value="Open"),
            patch.object(issue_manager, "_get_custom_field_value", return_value="High"),
        ):
            issue_manager.display_issues_table([sample_issue])

            issue_manager.console.print.assert_called_once()

    def test_display_issues_table_empty(self, issue_manager):
        """Test displaying empty issues table."""
        issue_manager.display_issues_table([])

        issue_manager.console.print.assert_called_once_with("[yellow]No issues found.[/yellow]")

    def test_display_issues_table_paginated(self, issue_manager, sample_issue):
        """Test displaying paginated issues table."""
        with patch("youtrack_cli.managers.issues.create_paginated_display") as mock_paginated:
            mock_display = MagicMock()
            mock_paginated.return_value = mock_display

            issue_manager.display_issues_table_paginated([sample_issue])

            mock_paginated.assert_called_once_with(issue_manager.console, 50)
            mock_display.display_paginated_table.assert_called_once()

    def test_display_links_table(self, issue_manager):
        """Test displaying links table."""
        links = [
            {
                "direction": "outward",
                "linkType": {"name": "relates to"},
                "issues": [{"idReadable": "TEST-456", "summary": "Related issue"}],
            }
        ]

        issue_manager.display_links_table(links)
        issue_manager.console.print.assert_called_once()

    def test_display_links_table_empty(self, issue_manager):
        """Test displaying empty links table."""
        issue_manager.display_links_table([])

        issue_manager.console.print.assert_called_once_with("[yellow]No links found.[/yellow]")

    def test_display_comments_table(self, issue_manager):
        """Test displaying comments table."""
        comments = [{"author": {"fullName": "Test User"}, "created": "2023-01-01", "text": "Test comment"}]

        issue_manager.display_comments_table(comments)
        issue_manager.console.print.assert_called_once()

    def test_display_comments_table_empty(self, issue_manager):
        """Test displaying empty comments table."""
        issue_manager.display_comments_table([])

        issue_manager.console.print.assert_called_once_with("[yellow]No comments found.[/yellow]")

    def test_display_attachments_table(self, issue_manager):
        """Test displaying attachments table."""
        attachments = [{"name": "test.txt", "size": 1234, "author": {"fullName": "Test User"}, "created": "2023-01-01"}]

        issue_manager.display_attachments_table(attachments)
        issue_manager.console.print.assert_called_once()

    def test_display_attachments_table_empty(self, issue_manager):
        """Test displaying empty attachments table."""
        issue_manager.display_attachments_table([])

        issue_manager.console.print.assert_called_once_with("[yellow]No attachments found.[/yellow]")

    def test_display_link_types_table(self, issue_manager):
        """Test displaying link types table."""
        link_types = [{"name": "relates to", "description": "Related issues", "directed": True}]

        issue_manager.display_link_types_table(link_types)
        issue_manager.console.print.assert_called_once()

    def test_display_link_types_table_empty(self, issue_manager):
        """Test displaying empty link types table."""
        issue_manager.display_link_types_table([])

        issue_manager.console.print.assert_called_once_with("[yellow]No link types found.[/yellow]")

    def test_display_issue_list(self, issue_manager, sample_issue):
        """Test displaying issue list."""
        with patch.object(issue_manager, "_format_issues_for_display", return_value="formatted output"):
            issue_manager.display_issue_list([sample_issue], format_output="csv")

            issue_manager.console.print.assert_called_once_with("formatted output")

    def test_display_issue_list_empty(self, issue_manager):
        """Test displaying empty issue list."""
        issue_manager.display_issue_list([])

        issue_manager.console.print.assert_called_once_with("[yellow]No issues found.[/yellow]")
