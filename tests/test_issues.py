"""Tests for issue management functionality."""

from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
from click.testing import CliRunner

from youtrack_cli.auth import AuthConfig, AuthManager
from youtrack_cli.issues import IssueManager


@pytest.fixture
def mock_credentials():
    """Mock credentials for testing."""
    return AuthConfig(
        base_url="https://test.youtrack.cloud",
        token="test-token",
        username="test-user",
    )


@pytest.fixture
def mock_auth_manager(mock_credentials):
    """Mock auth manager for testing."""
    auth_manager = MagicMock(spec=AuthManager)
    auth_manager.load_credentials.return_value = mock_credentials
    return auth_manager


@pytest.fixture
def issue_manager(mock_auth_manager):
    """Issue manager instance for testing."""
    return IssueManager(mock_auth_manager)


@pytest.fixture
def sample_issue():
    """Sample issue data for testing."""
    return {
        "id": "PROJ-123",
        "summary": "Test Issue",
        "description": "Test description",
        "state": {"name": "Open"},
        "priority": {"name": "High"},
        "type": {"name": "Bug"},
        "assignee": {"login": "test-user", "fullName": "Test User"},
        "project": {"id": "PROJ", "name": "Test Project"},
        "created": "2024-01-01T10:00:00Z",
        "updated": "2024-01-01T10:00:00Z",
        "tags": [{"name": "urgent"}],
    }


class TestIssueManager:
    """Test cases for IssueManager class."""

    @pytest.mark.asyncio
    async def test_create_issue_success(self, issue_manager, sample_issue):
        """Test successful issue creation."""
        with patch("youtrack_cli.issues.get_client_manager") as mock_get_client_manager:
            mock_resp = Mock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = sample_issue
            mock_resp.text = '{"mock": "response"}'
            mock_resp.headers = {"content-type": "application/json"}
            mock_client_manager = Mock()
            mock_client_manager.make_request = AsyncMock(return_value=mock_resp)
            mock_get_client_manager.return_value = mock_client_manager

            result = await issue_manager.create_issue(
                project_id="PROJ",
                summary="Test Issue",
                description="Test description",
                issue_type="Bug",
                priority="High",
                assignee="test-user",
            )

            assert result["status"] == "success"
            assert "Test Issue" in result["message"]
            assert result["data"] == sample_issue

    @pytest.mark.asyncio
    async def test_create_issue_auth_error(self, mock_auth_manager):
        """Test issue creation with authentication error."""
        mock_auth_manager.load_credentials.return_value = None
        issue_manager = IssueManager(mock_auth_manager)

        result = await issue_manager.create_issue("PROJ", "Test Issue")

        assert result["status"] == "error"
        assert "Not authenticated" in result["message"]

    @pytest.mark.asyncio
    async def test_create_issue_api_error(self, issue_manager):
        """Test issue creation with API error."""
        with patch("youtrack_cli.issues.get_client_manager") as mock_get_client_manager:
            mock_resp = Mock()
            mock_resp.status_code = 400
            mock_resp.text = "Bad Request"
            mock_client_manager = Mock()
            mock_client_manager.make_request = AsyncMock(return_value=mock_resp)
            mock_get_client_manager.return_value = mock_client_manager

            result = await issue_manager.create_issue("PROJ", "Test Issue")

            assert result["status"] == "error"
            assert "Bad Request" in result["message"]

    @pytest.mark.asyncio
    async def test_list_issues_success(self, issue_manager, sample_issue):
        """Test successful issue listing."""
        issues = [sample_issue]

        with patch("youtrack_cli.issues.get_client_manager") as mock_get_client_manager:
            mock_resp = Mock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = issues
            mock_resp.text = '{"mock": "response"}'
            mock_resp.headers = {"content-type": "application/json"}
            mock_client_manager = Mock()
            mock_client_manager.make_request = AsyncMock(return_value=mock_resp)
            mock_get_client_manager.return_value = mock_client_manager

            result = await issue_manager.list_issues(project_id="PROJ")

            assert result["status"] == "success"
            assert result["data"] == issues
            assert result["count"] == 1

    @pytest.mark.asyncio
    async def test_list_issues_with_filters(self, issue_manager, sample_issue):
        """Test issue listing with filters."""
        with patch("youtrack_cli.issues.get_client_manager") as mock_get_client_manager:
            mock_resp = Mock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = [sample_issue]
            mock_resp.text = '{"mock": "response"}'
            mock_resp.headers = {"content-type": "application/json"}
            mock_client_manager = Mock()
            mock_client_manager.make_request = AsyncMock(return_value=mock_resp)
            mock_get_client_manager.return_value = mock_client_manager

            result = await issue_manager.list_issues(
                project_id="PROJ",
                state="Open",
                assignee="test-user",
                top=10,
                query="priority:High",
            )

            assert result["status"] == "success"
            # Verify the make_request call was made with proper parameters
            mock_client_manager.make_request.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_issue_success(self, issue_manager, sample_issue):
        """Test successful issue retrieval."""
        with patch("youtrack_cli.issues.get_client_manager") as mock_get_client_manager:
            mock_resp = Mock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = sample_issue
            mock_resp.text = '{"mock": "response"}'
            mock_resp.headers = {"content-type": "application/json"}
            mock_client_manager = Mock()
            mock_client_manager.make_request = AsyncMock(return_value=mock_resp)
            mock_get_client_manager.return_value = mock_client_manager

            result = await issue_manager.get_issue("PROJ-123")

            assert result["status"] == "success"
            assert result["data"] == sample_issue

    @pytest.mark.asyncio
    async def test_update_issue_success(self, issue_manager, sample_issue):
        """Test successful issue update."""
        with patch("youtrack_cli.issues.get_client_manager") as mock_get_client_manager:
            mock_resp = Mock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = sample_issue
            mock_resp.text = '{"mock": "response"}'
            mock_resp.headers = {"content-type": "application/json"}
            mock_client_manager = Mock()
            mock_client_manager.make_request = AsyncMock(return_value=mock_resp)
            mock_get_client_manager.return_value = mock_client_manager

            result = await issue_manager.update_issue(
                issue_id="PROJ-123",
                summary="Updated Summary",
                priority="Critical",
            )

            assert result["status"] == "success"
            assert "PROJ-123" in result["message"]

    @pytest.mark.asyncio
    async def test_update_issue_no_fields(self, issue_manager):
        """Test issue update with no fields provided."""
        result = await issue_manager.update_issue("PROJ-123")

        assert result["status"] == "error"
        assert "No fields to update" in result["message"]

    @pytest.mark.asyncio
    async def test_delete_issue_success(self, issue_manager):
        """Test successful issue deletion."""
        with patch("youtrack_cli.issues.get_client_manager") as mock_get_client_manager:
            mock_resp = Mock()
            mock_resp.status_code = 200
            mock_client_manager = Mock()
            mock_client_manager.make_request = AsyncMock(return_value=mock_resp)
            mock_get_client_manager.return_value = mock_client_manager

            result = await issue_manager.delete_issue("PROJ-123")

            assert result["status"] == "success"
            assert "PROJ-123" in result["message"]

    @pytest.mark.asyncio
    async def test_search_issues_success(self, issue_manager, sample_issue):
        """Test successful issue search."""
        with patch("youtrack_cli.issues.get_client_manager") as mock_get_client_manager:
            mock_resp = Mock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = [sample_issue]
            mock_resp.text = '{"mock": "response"}'
            mock_resp.headers = {"content-type": "application/json"}
            mock_client_manager = Mock()
            mock_client_manager.make_request = AsyncMock(return_value=mock_resp)
            mock_get_client_manager.return_value = mock_client_manager

            result = await issue_manager.search_issues(
                query="priority:High",
                project_id="PROJ",
                top=10,
            )

            assert result["status"] == "success"
            assert result["count"] == 1

    @pytest.mark.asyncio
    async def test_assign_issue_success(self, issue_manager, sample_issue):
        """Test successful issue assignment."""
        with patch("youtrack_cli.issues.get_client_manager") as mock_get_client_manager:
            mock_resp = Mock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = sample_issue
            mock_resp.text = '{"mock": "response"}'
            mock_resp.headers = {"content-type": "application/json"}
            mock_client_manager = Mock()
            mock_client_manager.make_request = AsyncMock(return_value=mock_resp)
            mock_get_client_manager.return_value = mock_client_manager

            result = await issue_manager.assign_issue("PROJ-123", "new-user")

            assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_move_issue_state_success(self, issue_manager):
        """Test successful issue state move."""
        with patch("youtrack_cli.issues.get_client_manager") as mock_get_client_manager:
            mock_resp = Mock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = {}
            mock_resp.text = '{"mock": "response"}'
            mock_resp.headers = {"content-type": "application/json"}
            mock_client_manager = Mock()
            mock_client_manager.make_request = AsyncMock(return_value=mock_resp)
            mock_get_client_manager.return_value = mock_client_manager

            result = await issue_manager.move_issue("PROJ-123", state="In Progress")

            assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_move_issue_project_success(self, issue_manager):
        """Test successful issue project move."""
        with patch("youtrack_cli.issues.get_client_manager") as mock_get_client_manager:
            mock_resp = Mock()
            mock_resp.status_code = 200
            mock_client_manager = Mock()
            mock_client_manager.make_request = AsyncMock(return_value=mock_resp)
            mock_get_client_manager.return_value = mock_client_manager

            result = await issue_manager.move_issue("PROJ-123", project_id="OTHER")

            assert result["status"] == "success"
            assert "OTHER" in result["message"]

    @pytest.mark.asyncio
    async def test_move_issue_no_params(self, issue_manager):
        """Test issue move with no parameters."""
        result = await issue_manager.move_issue("PROJ-123")

        assert result["status"] == "error"
        assert "No target state or project" in result["message"]

    @pytest.mark.asyncio
    async def test_add_tag_success(self, issue_manager):
        """Test successful tag addition."""
        with patch("youtrack_cli.issues.get_client_manager") as mock_get_client_manager:
            mock_resp = Mock()
            mock_resp.status_code = 200
            mock_client_manager = Mock()
            mock_client_manager.make_request = AsyncMock(return_value=mock_resp)
            mock_get_client_manager.return_value = mock_client_manager

            result = await issue_manager.add_tag("PROJ-123", "urgent")

            assert result["status"] == "success"
            assert "urgent" in result["message"]

    @pytest.mark.asyncio
    async def test_remove_tag_success(self, issue_manager):
        """Test successful tag removal."""
        with patch("youtrack_cli.issues.get_client_manager") as mock_get_client_manager:
            mock_resp = Mock()
            mock_resp.status_code = 200
            mock_client_manager = Mock()
            mock_client_manager.make_request = AsyncMock(return_value=mock_resp)
            mock_get_client_manager.return_value = mock_client_manager

            result = await issue_manager.remove_tag("PROJ-123", "urgent")

            assert result["status"] == "success"
            assert "urgent" in result["message"]

    @pytest.mark.asyncio
    async def test_list_tags_success(self, issue_manager):
        """Test successful tag listing."""
        tags_data = {"tags": [{"name": "urgent"}, {"name": "bug"}]}

        with patch("youtrack_cli.issues.get_client_manager") as mock_get_client_manager:
            mock_resp = Mock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = tags_data
            mock_resp.text = '{"mock": "response"}'
            mock_resp.headers = {"content-type": "application/json"}
            mock_client_manager = Mock()
            mock_client_manager.make_request = AsyncMock(return_value=mock_resp)
            mock_get_client_manager.return_value = mock_client_manager

            result = await issue_manager.list_tags("PROJ-123")

            assert result["status"] == "success"
            assert len(result["data"]) == 2

    @pytest.mark.asyncio
    async def test_add_comment_success(self, issue_manager):
        """Test successful comment addition."""
        with patch("youtrack_cli.issues.get_client_manager") as mock_get_client_manager:
            mock_resp = Mock()
            mock_resp.status_code = 200
            mock_client_manager = Mock()
            mock_client_manager.make_request = AsyncMock(return_value=mock_resp)
            mock_get_client_manager.return_value = mock_client_manager

            result = await issue_manager.add_comment("PROJ-123", "Test comment")

            assert result["status"] == "success"
            assert "Comment added" in result["message"]

    @pytest.mark.asyncio
    async def test_list_comments_success(self, issue_manager):
        """Test successful comment listing."""
        comments = [
            {
                "id": "comment-1",
                "text": "Test comment",
                "author": {"login": "test-user", "fullName": "Test User"},
                "created": "2024-01-01T10:00:00Z",
            }
        ]

        with patch("youtrack_cli.issues.get_client_manager") as mock_get_client_manager:
            mock_resp = Mock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = comments
            mock_resp.text = '{"mock": "response"}'
            mock_resp.headers = {"content-type": "application/json"}
            mock_client_manager = Mock()
            mock_client_manager.make_request = AsyncMock(return_value=mock_resp)
            mock_get_client_manager.return_value = mock_client_manager

            result = await issue_manager.list_comments("PROJ-123")

            assert result["status"] == "success"
            assert len(result["data"]) == 1

    @pytest.mark.asyncio
    async def test_update_comment_success(self, issue_manager):
        """Test successful comment update."""
        with patch("youtrack_cli.issues.get_client_manager") as mock_get_client_manager:
            mock_resp = Mock()
            mock_resp.status_code = 200
            mock_client_manager = Mock()
            mock_client_manager.make_request = AsyncMock(return_value=mock_resp)
            mock_get_client_manager.return_value = mock_client_manager

            result = await issue_manager.update_comment("PROJ-123", "comment-1", "Updated comment")

            assert result["status"] == "success"
            assert "comment-1" in result["message"]

    @pytest.mark.asyncio
    async def test_delete_comment_success(self, issue_manager):
        """Test successful comment deletion."""
        with patch("youtrack_cli.issues.get_client_manager") as mock_get_client_manager:
            mock_resp = Mock()
            mock_resp.status_code = 200
            mock_client_manager = Mock()
            mock_client_manager.make_request = AsyncMock(return_value=mock_resp)
            mock_get_client_manager.return_value = mock_client_manager

            result = await issue_manager.delete_comment("PROJ-123", "comment-1")

            assert result["status"] == "success"
            assert "comment-1" in result["message"]

    @pytest.mark.asyncio
    async def test_upload_attachment_success(self, issue_manager):
        """Test successful attachment upload."""
        with (
            patch("youtrack_cli.issues.get_client_manager") as mock_get_client_manager,
            patch("builtins.open", create=True) as mock_open,
        ):
            mock_resp = Mock()
            mock_resp.status_code = 200
            mock_client = Mock()
            mock_client.post = AsyncMock(return_value=mock_resp)
            mock_client_manager = Mock()
            mock_client_manager.get_client.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client_manager.get_client.return_value.__aexit__ = AsyncMock(return_value=None)
            mock_get_client_manager.return_value = mock_client_manager
            mock_open.return_value.__enter__.return_value = MagicMock()

            result = await issue_manager.upload_attachment("PROJ-123", "test.txt")

            assert result["status"] == "success"
            assert "test.txt" in result["message"]

    @pytest.mark.asyncio
    async def test_list_attachments_success(self, issue_manager):
        """Test successful attachment listing."""
        attachments = [
            {
                "id": "attach-1",
                "name": "test.txt",
                "size": 1024,
                "mimeType": "text/plain",
                "author": {"login": "test-user", "fullName": "Test User"},
            }
        ]

        with patch("youtrack_cli.issues.get_client_manager") as mock_get_client_manager:
            mock_resp = Mock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = attachments
            mock_resp.text = '{"mock": "response"}'
            mock_resp.headers = {"content-type": "application/json"}
            mock_client_manager = Mock()
            mock_client_manager.make_request = AsyncMock(return_value=mock_resp)
            mock_get_client_manager.return_value = mock_client_manager

            result = await issue_manager.list_attachments("PROJ-123")

            assert result["status"] == "success"
            assert len(result["data"]) == 1

    @pytest.mark.asyncio
    async def test_download_attachment_success(self, issue_manager):
        """Test successful attachment download."""
        with (
            patch("youtrack_cli.issues.get_client_manager") as mock_get_client_manager,
            patch("builtins.open", create=True) as mock_open,
        ):
            mock_resp = Mock()
            mock_resp.status_code = 200
            mock_resp.content = b"file content"
            mock_client_manager = Mock()
            mock_client_manager.make_request = AsyncMock(return_value=mock_resp)
            mock_get_client_manager.return_value = mock_client_manager
            mock_file = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_file

            result = await issue_manager.download_attachment("PROJ-123", "attach-1", "output.txt")

            assert result["status"] == "success"
            assert "output.txt" in result["message"]
            mock_file.write.assert_called_once_with(b"file content")

    @pytest.mark.asyncio
    async def test_delete_attachment_success(self, issue_manager):
        """Test successful attachment deletion."""
        with patch("youtrack_cli.issues.get_client_manager") as mock_get_client_manager:
            mock_resp = Mock()
            mock_resp.status_code = 200
            mock_client_manager = Mock()
            mock_client_manager.make_request = AsyncMock(return_value=mock_resp)
            mock_get_client_manager.return_value = mock_client_manager

            result = await issue_manager.delete_attachment("PROJ-123", "attach-1")

            assert result["status"] == "success"
            assert "attach-1" in result["message"]

    @pytest.mark.asyncio
    async def test_create_link_success(self, issue_manager):
        """Test successful link creation."""
        with patch("youtrack_cli.issues.get_client_manager") as mock_get_client_manager:
            mock_resp = Mock()
            mock_resp.status_code = 200
            mock_client_manager = Mock()
            mock_client_manager.make_request = AsyncMock(return_value=mock_resp)
            mock_get_client_manager.return_value = mock_client_manager

            result = await issue_manager.create_link("PROJ-123", "PROJ-124", "depends on")

            assert result["status"] == "success"
            assert "PROJ-123" in result["message"]
            assert "PROJ-124" in result["message"]

    @pytest.mark.asyncio
    async def test_list_links_success(self, issue_manager):
        """Test successful link listing."""
        links_data = {
            "links": [
                {
                    "linkType": {"name": "depends on"},
                    "direction": "outward",
                    "issues": [{"id": "PROJ-124", "summary": "Related issue"}],
                }
            ]
        }

        with patch("youtrack_cli.issues.get_client_manager") as mock_get_client_manager:
            mock_resp = Mock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = links_data
            mock_resp.text = '{"mock": "response"}'
            mock_resp.headers = {"content-type": "application/json"}
            mock_client_manager = Mock()
            mock_client_manager.make_request = AsyncMock(return_value=mock_resp)
            mock_get_client_manager.return_value = mock_client_manager

            result = await issue_manager.list_links("PROJ-123")

            assert result["status"] == "success"
            assert len(result["data"]) == 1

    @pytest.mark.asyncio
    async def test_delete_link_success(self, issue_manager):
        """Test successful link deletion."""
        with patch("youtrack_cli.issues.get_client_manager") as mock_get_client_manager:
            mock_resp = Mock()
            mock_resp.status_code = 200
            mock_client_manager = Mock()
            mock_client_manager.make_request = AsyncMock(return_value=mock_resp)
            mock_get_client_manager.return_value = mock_client_manager

            result = await issue_manager.delete_link("PROJ-123", "link-1")

            assert result["status"] == "success"
            assert "link-1" in result["message"]

    @pytest.mark.asyncio
    async def test_list_link_types_success(self, issue_manager):
        """Test successful link types listing."""
        link_types = [
            {
                "name": "depends on",
                "sourceToTarget": "depends on",
                "targetToSource": "is required for",
            }
        ]

        with patch("youtrack_cli.issues.get_client_manager") as mock_get_client_manager:
            mock_resp = Mock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = link_types
            mock_resp.text = '{"mock": "response"}'
            mock_resp.headers = {"content-type": "application/json"}
            mock_client_manager = Mock()
            mock_client_manager.make_request = AsyncMock(return_value=mock_resp)
            mock_get_client_manager.return_value = mock_client_manager

            result = await issue_manager.list_link_types()

            assert result["status"] == "success"
            assert len(result["data"]) == 1

    def test_display_issues_table(self, issue_manager, sample_issue, capsys):
        """Test issues table display."""
        issues = [sample_issue]
        issue_manager.display_issues_table(issues)

        captured = capsys.readouterr()
        assert "PROJ-123" in captured.out
        assert "Test Issue" in captured.out

    def test_display_issues_table_empty(self, issue_manager, capsys):
        """Test empty issues table display."""
        issue_manager.display_issues_table([])

        captured = capsys.readouterr()
        assert "No issues found" in captured.out

    def test_display_issue_details(self, issue_manager, sample_issue, capsys):
        """Test issue details display."""
        issue_manager.display_issue_details(sample_issue)

        captured = capsys.readouterr()
        assert "PROJ-123" in captured.out
        assert "Test Issue" in captured.out
        assert "High" in captured.out

    def test_display_comments_table(self, issue_manager, capsys):
        """Test comments table display."""
        comments = [
            {
                "id": "comment-1",
                "text": "Test comment",
                "author": {"fullName": "Test User"},
                "created": "2024-01-01T10:00:00Z",
            }
        ]
        issue_manager.display_comments_table(comments)

        captured = capsys.readouterr()
        assert "comment-1" in captured.out
        assert "Test comment" in captured.out

    def test_display_attachments_table(self, issue_manager, capsys):
        """Test attachments table display."""
        attachments = [
            {
                "id": "attach-1",
                "name": "test.txt",
                "size": 1024,
                "mimeType": "text/plain",
                "author": {"fullName": "Test User"},
            }
        ]
        issue_manager.display_attachments_table(attachments)

        captured = capsys.readouterr()
        assert "attach-1" in captured.out
        assert "test.txt" in captured.out

    def test_display_links_table(self, issue_manager, capsys):
        """Test links table display."""
        links = [
            {
                "linkType": {"name": "depends on"},
                "direction": "outward",
                "issues": [{"id": "PROJ-124", "summary": "Related issue"}],
            }
        ]
        issue_manager.display_links_table(links)

        captured = capsys.readouterr()
        assert "depends on" in captured.out
        assert "PROJ-124" in captured.out

    def test_display_link_types_table(self, issue_manager, capsys):
        """Test link types table display."""
        link_types = [
            {
                "name": "depends on",
                "sourceToTarget": "depends on",
                "targetToSource": "is required for",
            }
        ]
        issue_manager.display_link_types_table(link_types)

        captured = capsys.readouterr()
        assert "depends on" in captured.out
        assert "is required for" in captured.out


class TestIssuesCLI:
    """Test cases for issues CLI commands."""

    def test_issues_create_command(self):
        """Test the issues create CLI command."""
        from youtrack_cli.main import main

        runner = CliRunner()

        with patch("youtrack_cli.main.asyncio.run") as mock_run:
            mock_run.return_value = {
                "status": "success",
                "message": "Issue created successfully",
                "data": {"id": "PROJ-123"},
            }

            result = runner.invoke(
                main,
                [
                    "issues",
                    "create",
                    "PROJ",
                    "Test Issue",
                    "-d",
                    "Test description",
                    "-t",
                    "Bug",
                    "-p",
                    "High",
                ],
            )

            assert result.exit_code == 0
            assert "creating issue" in result.output.lower()

    def test_issues_list_command(self):
        """Test the issues list CLI command."""
        from youtrack_cli.main import main

        runner = CliRunner()

        with patch("youtrack_cli.main.asyncio.run") as mock_run:
            mock_run.return_value = {
                "status": "success",
                "data": [],
                "count": 0,
            }

            with patch("youtrack_cli.issues.IssueManager.display_issues_table"):
                result = runner.invoke(main, ["issues", "list", "-p", "PROJ"])

            assert result.exit_code == 0
            assert "fetching issues" in result.output.lower()

    def test_issues_update_command(self):
        """Test the issues update CLI command."""
        from youtrack_cli.main import main

        runner = CliRunner()

        with patch("youtrack_cli.main.asyncio.run") as mock_run:
            mock_run.return_value = {
                "status": "success",
                "message": "Issue updated successfully",
            }

            result = runner.invoke(
                main,
                [
                    "issues",
                    "update",
                    "PROJ-123",
                    "-s",
                    "Updated summary",
                    "-p",
                    "Critical",
                ],
            )

            assert result.exit_code == 0
            assert "updating issue" in result.output.lower()

    def test_issues_delete_command_with_confirm(self):
        """Test the issues delete CLI command with confirmation."""
        from youtrack_cli.main import main

        runner = CliRunner()

        with patch("youtrack_cli.main.asyncio.run") as mock_run:
            mock_run.return_value = {
                "status": "success",
                "message": "Issue deleted successfully",
            }

            result = runner.invoke(main, ["issues", "delete", "PROJ-123", "--confirm"])

            assert result.exit_code == 0
            assert "deleting issue" in result.output.lower()

    def test_issues_search_command(self):
        """Test the issues search CLI command."""
        from youtrack_cli.main import main

        runner = CliRunner()

        with patch("youtrack_cli.main.asyncio.run") as mock_run:
            mock_run.return_value = {
                "status": "success",
                "data": [],
                "count": 0,
            }

            with patch("youtrack_cli.issues.IssueManager.display_issues_table"):
                result = runner.invoke(main, ["issues", "search", "priority:High"])

            assert result.exit_code == 0
            assert "searching issues" in result.output.lower()

    def test_issues_assign_command(self):
        """Test the issues assign CLI command."""
        from youtrack_cli.main import main

        runner = CliRunner()

        with patch("youtrack_cli.main.asyncio.run") as mock_run:
            mock_run.return_value = {
                "status": "success",
                "message": "Issue assigned successfully",
            }

            result = runner.invoke(main, ["issues", "assign", "PROJ-123", "test-user"])

            assert result.exit_code == 0
            assert "assigning issue" in result.output.lower()

    def test_issues_tag_add_command(self):
        """Test the issues tag add CLI command."""
        from youtrack_cli.main import main

        runner = CliRunner()

        with patch("youtrack_cli.main.asyncio.run") as mock_run:
            mock_run.return_value = {
                "status": "success",
                "message": "Tag added successfully",
            }

            result = runner.invoke(main, ["issues", "tag", "add", "PROJ-123", "urgent"])

            assert result.exit_code == 0
            assert "adding tag" in result.output.lower()

    def test_issues_comments_add_command(self):
        """Test the issues comments add CLI command."""
        from youtrack_cli.main import main

        runner = CliRunner()

        with patch("youtrack_cli.main.asyncio.run") as mock_run:
            mock_run.return_value = {
                "status": "success",
                "message": "Comment added successfully",
            }

            result = runner.invoke(main, ["issues", "comments", "add", "PROJ-123", "Test comment"])

            assert result.exit_code == 0
            assert "adding comment" in result.output.lower()

    def test_issues_attach_upload_command(self):
        """Test the issues attach upload CLI command."""
        from youtrack_cli.main import main

        runner = CliRunner()

        with patch("youtrack_cli.main.asyncio.run") as mock_run:
            mock_run.return_value = {
                "status": "success",
                "message": "File uploaded successfully",
            }

            # Create a temporary file for testing
            import tempfile

            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                tmp_file.write(b"test content")
                tmp_file_path = tmp_file.name

            try:
                result = runner.invoke(main, ["issues", "attach", "upload", "PROJ-123", tmp_file_path])

                assert result.exit_code == 0
                assert "uploading file" in result.output.lower()
            finally:
                import os

                os.unlink(tmp_file_path)

    def test_issues_links_create_command(self):
        """Test the issues links create CLI command."""
        from youtrack_cli.main import main

        runner = CliRunner()

        with patch("youtrack_cli.main.asyncio.run") as mock_run:
            mock_run.return_value = {
                "status": "success",
                "message": "Link created successfully",
            }

            result = runner.invoke(
                main,
                ["issues", "links", "create", "PROJ-123", "PROJ-124", "depends on"],
            )

            assert result.exit_code == 0
            assert "creating" in result.output.lower()
            assert "link" in result.output.lower()

    def test_command_authentication_error(self):
        """Test CLI command with authentication error."""
        from youtrack_cli.main import main

        runner = CliRunner()

        with patch("youtrack_cli.main.asyncio.run") as mock_run:
            mock_run.return_value = {
                "status": "error",
                "message": "Not authenticated",
            }

            result = runner.invoke(main, ["issues", "create", "PROJ", "Test Issue"])

            assert result.exit_code == 1
            assert "not authenticated" in result.output.lower()

    def test_command_api_error(self):
        """Test CLI command with API error."""
        from youtrack_cli.main import main

        runner = CliRunner()

        with patch("youtrack_cli.main.asyncio.run") as mock_run:
            mock_run.return_value = {
                "status": "error",
                "message": "API request failed",
            }

            result = runner.invoke(main, ["issues", "list"])

            assert result.exit_code == 1
            assert "api request failed" in result.output.lower()
