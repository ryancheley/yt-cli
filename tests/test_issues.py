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


@pytest.fixture
def sample_issue_with_custom_fields():
    """Sample issue data with custom fields for testing."""
    return {
        "id": "HIP-25",
        "numberInProject": 2,
        "summary": "Find Painter",
        "description": "Test description",
        "project": {"id": "0-2", "name": "Home Improvement Projects", "shortName": "HIP"},
        "created": 1736614471891,
        "updated": 1752033822789,
        "customFields": [
            {
                "value": {"name": "Medium", "id": "143-17", "$type": "EnumBundleElement"},
                "name": "Priority",
                "$type": "SingleEnumIssueCustomField",
            },
            {
                "value": {
                    "name": "Ryan Cheley",
                    "fullName": "Ryan Cheley",
                    "login": "ryan",
                    "id": "2-3",
                    "$type": "User",
                },
                "name": "Assignee",
                "$type": "SingleUserIssueCustomField",
            },
            {
                "value": {"name": "To Do", "id": "145-18", "$type": "StateBundleElement"},
                "name": "Stage",
                "$type": "StateIssueCustomField",
            },
            {
                "value": {"name": "Task", "id": "143-9", "$type": "EnumBundleElement"},
                "name": "Type",
                "$type": "SingleEnumIssueCustomField",
            },
            {"value": None, "name": "Kanban State", "$type": "SingleEnumIssueCustomField"},
        ],
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
    async def test_update_issue_state_custom_field_format(self, issue_manager):
        """Test that issue state updates use correct custom field format."""
        with patch("youtrack_cli.issues.get_client_manager") as mock_get_client_manager:
            mock_resp = Mock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = {}
            mock_resp.text = '{"mock": "response"}'
            mock_resp.headers = {"content-type": "application/json"}
            mock_client_manager = Mock()
            mock_client_manager.make_request = AsyncMock(return_value=mock_resp)
            mock_get_client_manager.return_value = mock_client_manager

            result = await issue_manager.update_issue("PROJ-123", state="Fixed")

            assert result["status"] == "success"
            # Verify the request was made with correct custom field format for state
            call_args = mock_client_manager.make_request.call_args
            json_data = call_args[1]["json_data"]
            assert "customFields" in json_data
            state_field = json_data["customFields"][0]
            assert state_field["$type"] == "StateIssueCustomField"
            assert state_field["name"] == "State"
            assert state_field["value"]["name"] == "Fixed"

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
            # Verify the request was made with correct custom field format for state
            call_args = mock_client_manager.make_request.call_args
            assert call_args[1]["json_data"]["customFields"][0]["$type"] == "StateIssueCustomField"
            assert call_args[1]["json_data"]["customFields"][0]["name"] == "State"
            assert call_args[1]["json_data"]["customFields"][0]["value"]["name"] == "In Progress"

    @pytest.mark.asyncio
    async def test_move_issue_project_success(self, issue_manager):
        """Test successful issue project move."""
        with (
            patch("youtrack_cli.issues.get_client_manager") as mock_get_client_manager,
            patch("youtrack_cli.projects.ProjectManager") as mock_project_manager,
        ):
            mock_resp = Mock()
            mock_resp.status_code = 200
            mock_client_manager = Mock()
            mock_client_manager.make_request = AsyncMock(return_value=mock_resp)
            mock_get_client_manager.return_value = mock_client_manager

            # Mock the project manager's get_project method
            mock_project_manager_instance = Mock()
            mock_project_manager_instance.get_project = AsyncMock(
                return_value={"status": "success", "data": {"id": "0-1", "shortName": "OTHER"}}
            )
            mock_project_manager.return_value = mock_project_manager_instance

            result = await issue_manager.move_issue("PROJ-123", project_id="OTHER")

            assert result["status"] == "success"
            assert "OTHER" in result["message"]

    @pytest.mark.asyncio
    async def test_move_issue_project_not_found(self, issue_manager):
        """Test issue move with invalid project."""
        with patch("youtrack_cli.projects.ProjectManager") as mock_project_manager:
            # Mock the project manager's get_project method to return project not found
            mock_project_manager_instance = Mock()
            mock_project_manager_instance.get_project = AsyncMock(
                return_value={"status": "error", "message": "Project not found"}
            )
            mock_project_manager.return_value = mock_project_manager_instance

            result = await issue_manager.move_issue("PROJ-123", project_id="INVALID")

            assert result["status"] == "error"
            assert "Project 'INVALID' not found" in result["message"]

    @pytest.mark.asyncio
    async def test_move_issue_no_params(self, issue_manager):
        """Test issue move with no parameters."""
        result = await issue_manager.move_issue("PROJ-123")

        assert result["status"] == "error"
        assert "No target state or project" in result["message"]

    @pytest.mark.asyncio
    async def test_add_tag_success(self, issue_manager):
        """Test successful tag addition with existing tag."""
        with patch("youtrack_cli.issues.get_client_manager") as mock_get_client_manager:
            # First call for search (found)
            search_resp = Mock()
            search_resp.status_code = 200
            search_resp.json.return_value = [{"id": "6-4", "name": "urgent"}]

            # Second call to add tag to issue
            add_resp = Mock()
            add_resp.status_code = 200

            mock_client_manager = Mock()
            mock_client_manager.make_request = AsyncMock(side_effect=[search_resp, add_resp])
            mock_get_client_manager.return_value = mock_client_manager

            result = await issue_manager.add_tag("PROJ-123", "urgent")

            assert result["status"] == "success"
            assert "urgent" in result["message"]
            assert "PROJ-123" in result["message"]

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
    async def test_find_tag_by_name_success(self, issue_manager):
        """Test successful tag lookup by name."""
        tag_data = [{"id": "6-4", "name": "urgent"}]

        with patch("youtrack_cli.issues.get_client_manager") as mock_get_client_manager:
            mock_resp = Mock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = tag_data
            mock_client_manager = Mock()
            mock_client_manager.make_request = AsyncMock(return_value=mock_resp)
            mock_get_client_manager.return_value = mock_client_manager

            result = await issue_manager.find_tag_by_name("urgent")

            assert result["status"] == "success"
            assert result["tag"]["id"] == "6-4"
            assert result["tag"]["name"] == "urgent"

    @pytest.mark.asyncio
    async def test_find_tag_by_name_not_found(self, issue_manager):
        """Test tag lookup when tag doesn't exist."""
        tag_data = []

        with patch("youtrack_cli.issues.get_client_manager") as mock_get_client_manager:
            mock_resp = Mock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = tag_data
            mock_client_manager = Mock()
            mock_client_manager.make_request = AsyncMock(return_value=mock_resp)
            mock_get_client_manager.return_value = mock_client_manager

            result = await issue_manager.find_tag_by_name("nonexistent")

            assert result["status"] == "not_found"
            assert "not found" in result["message"]

    @pytest.mark.asyncio
    async def test_create_tag_success(self, issue_manager):
        """Test successful tag creation."""
        tag_data = {"id": "6-5", "name": "testing"}

        with patch("youtrack_cli.issues.get_client_manager") as mock_get_client_manager:
            mock_resp = Mock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = tag_data
            mock_client_manager = Mock()
            mock_client_manager.make_request = AsyncMock(return_value=mock_resp)
            mock_get_client_manager.return_value = mock_client_manager

            result = await issue_manager.create_tag("testing")

            assert result["status"] == "success"
            assert result["tag"]["id"] == "6-5"
            assert result["tag"]["name"] == "testing"
            assert "Created" in result["message"]

    @pytest.mark.asyncio
    async def test_get_or_create_tag_existing(self, issue_manager):
        """Test get_or_create with existing tag."""
        tag_data = [{"id": "6-4", "name": "urgent"}]

        with patch("youtrack_cli.issues.get_client_manager") as mock_get_client_manager:
            mock_resp = Mock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = tag_data
            mock_client_manager = Mock()
            mock_client_manager.make_request = AsyncMock(return_value=mock_resp)
            mock_get_client_manager.return_value = mock_client_manager

            result = await issue_manager.get_or_create_tag("urgent")

            assert result["status"] == "success"
            assert result["tag"]["id"] == "6-4"
            assert "Found existing" in result["message"]

    @pytest.mark.asyncio
    async def test_get_or_create_tag_new(self, issue_manager):
        """Test get_or_create with new tag."""
        with patch("youtrack_cli.issues.get_client_manager") as mock_get_client_manager:
            # First call for search (not found)
            search_resp = Mock()
            search_resp.status_code = 200
            search_resp.json.return_value = []

            # Second call for creation
            create_resp = Mock()
            create_resp.status_code = 200
            create_resp.json.return_value = {"id": "6-6", "name": "newtag"}

            mock_client_manager = Mock()
            mock_client_manager.make_request = AsyncMock(side_effect=[search_resp, create_resp])
            mock_get_client_manager.return_value = mock_client_manager

            result = await issue_manager.get_or_create_tag("newtag")

            assert result["status"] == "success"
            assert result["tag"]["id"] == "6-6"
            assert "Created new" in result["message"]

    @pytest.mark.asyncio
    async def test_add_tag_with_creation(self, issue_manager):
        """Test add_tag that creates a new tag."""
        with patch("youtrack_cli.issues.get_client_manager") as mock_get_client_manager:
            # First call for search (not found)
            search_resp = Mock()
            search_resp.status_code = 200
            search_resp.json.return_value = []

            # Second call for creation
            create_resp = Mock()
            create_resp.status_code = 200
            create_resp.json.return_value = {"id": "6-7", "name": "testing"}

            # Third call to add tag to issue
            add_resp = Mock()
            add_resp.status_code = 200

            mock_client_manager = Mock()
            mock_client_manager.make_request = AsyncMock(side_effect=[search_resp, create_resp, add_resp])
            mock_get_client_manager.return_value = mock_client_manager

            result = await issue_manager.add_tag("PROJ-123", "testing")

            assert result["status"] == "success"
            assert "created new tag" in result["message"]
            assert "PROJ-123" in result["message"]

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
            # Mock the first request (metadata)
            mock_metadata_resp = Mock()
            mock_metadata_resp.status_code = 200
            mock_metadata_resp.text = '{"id": "attach-1", "url": "/api/files/attach-1?sign=abc123"}'
            mock_metadata_resp.headers = {"content-type": "application/json"}
            mock_metadata_resp.json.return_value = {"id": "attach-1", "url": "/api/files/attach-1?sign=abc123"}

            # Mock the second request (file content)
            mock_download_resp = Mock()
            mock_download_resp.status_code = 200
            mock_download_resp.content = b"file content"

            mock_client_manager = Mock()
            # Make the make_request method return different responses for different calls
            mock_client_manager.make_request = AsyncMock(side_effect=[mock_metadata_resp, mock_download_resp])
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
            # Mock responses for different API calls
            mock_link_types_resp = Mock()
            mock_link_types_resp.status_code = 200
            mock_link_types_resp.json.return_value = [
                {"id": "depends-on", "name": "Depends", "sourceToTarget": "depends on", "directed": True}
            ]
            mock_link_types_resp.text = '{"mock": "response"}'
            mock_link_types_resp.headers = {"content-type": "application/json"}

            mock_issue_resp = Mock()
            mock_issue_resp.status_code = 200
            mock_issue_resp.json.return_value = {"id": "2-124"}
            mock_issue_resp.text = '{"id": "2-124"}'
            mock_issue_resp.headers = {"content-type": "application/json"}

            mock_create_resp = Mock()
            mock_create_resp.status_code = 200

            # Configure mock to return different responses based on URL
            async def mock_make_request(method, url, **kwargs):
                if "issueLinkTypes" in url:
                    return mock_link_types_resp
                elif "PROJ-124" in url and method == "GET":
                    return mock_issue_resp
                else:
                    return mock_create_resp

            mock_client_manager = Mock()
            mock_client_manager.make_request = AsyncMock(side_effect=mock_make_request)
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

    def test_get_custom_field_value_enum_field(self, issue_manager, sample_issue_with_custom_fields):
        """Test extracting enum values from custom fields."""
        # Test Priority field
        priority_value = issue_manager._get_custom_field_value(sample_issue_with_custom_fields, "Priority")
        assert priority_value == "Medium"

        # Test Type field
        type_value = issue_manager._get_custom_field_value(sample_issue_with_custom_fields, "Type")
        assert type_value == "Task"

        # Test Stage field
        stage_value = issue_manager._get_custom_field_value(sample_issue_with_custom_fields, "Stage")
        assert stage_value == "To Do"

    def test_get_custom_field_value_user_field(self, issue_manager, sample_issue_with_custom_fields):
        """Test extracting user values from custom fields."""
        assignee_value = issue_manager._get_custom_field_value(sample_issue_with_custom_fields, "Assignee")
        assert assignee_value == "Ryan Cheley"

    def test_get_custom_field_value_null_field(self, issue_manager, sample_issue_with_custom_fields):
        """Test handling null values in custom fields."""
        kanban_value = issue_manager._get_custom_field_value(sample_issue_with_custom_fields, "Kanban State")
        assert kanban_value is None

    def test_get_custom_field_value_nonexistent_field(self, issue_manager, sample_issue_with_custom_fields):
        """Test handling nonexistent custom fields."""
        missing_value = issue_manager._get_custom_field_value(sample_issue_with_custom_fields, "NonexistentField")
        assert missing_value is None

    def test_get_custom_field_value_no_custom_fields(self, issue_manager, sample_issue):
        """Test handling issues without custom fields."""
        value = issue_manager._get_custom_field_value(sample_issue, "Priority")
        assert value is None

    def test_get_custom_field_value_invalid_custom_fields(self, issue_manager):
        """Test handling invalid custom fields structure."""
        issue_with_invalid_fields = {
            "id": "TEST-1",
            "customFields": "not a list",  # Invalid structure
        }
        value = issue_manager._get_custom_field_value(issue_with_invalid_fields, "Priority")
        assert value is None

    def test_get_custom_field_value_multi_value_field(self, issue_manager):
        """Test handling multi-value custom fields."""
        issue_with_multi_values = {
            "id": "TEST-1",
            "customFields": [
                {
                    "name": "Tags",
                    "value": [{"name": "urgent", "id": "tag-1"}, {"name": "backend", "id": "tag-2"}],
                    "$type": "MultiEnumIssueCustomField",
                }
            ],
        }
        value = issue_manager._get_custom_field_value(issue_with_multi_values, "Tags")
        assert value == "urgent, backend"

    def test_get_custom_field_value_string_value(self, issue_manager):
        """Test handling string values in custom fields."""
        issue_with_string_field = {
            "id": "TEST-1",
            "customFields": [
                {"name": "Description", "value": "Some text description", "$type": "TextIssueCustomField"}
            ],
        }
        value = issue_manager._get_custom_field_value(issue_with_string_field, "Description")
        assert value == "Some text description"

    def test_get_custom_field_value_avatar_url(self, issue_manager):
        """Test extracting avatarUrl from user field."""
        issue_with_avatar = {
            "id": "TEST-1",
            "customFields": [
                {
                    "name": "Reporter",
                    "value": {
                        "login": "user1",
                        "name": "John Doe",
                        "fullName": "John Doe",
                        "avatarUrl": "https://example.com/avatar.jpg",
                        "id": "user-123",
                    },
                    "$type": "SingleUserIssueCustomField",
                }
            ],
        }
        value = issue_manager._get_custom_field_value(issue_with_avatar, "Reporter")
        assert value == "John Doe"

    def test_get_custom_field_value_build_link(self, issue_manager):
        """Test extracting buildLink field."""
        issue_with_build_link = {
            "id": "TEST-1",
            "customFields": [
                {
                    "name": "Build",
                    "value": {"buildLink": "https://build.example.com/job/123", "id": "build-123"},
                    "$type": "BuildIssueCustomField",
                }
            ],
        }
        value = issue_manager._get_custom_field_value(issue_with_build_link, "Build")
        assert value == "https://build.example.com/job/123"

    def test_get_custom_field_value_color_id(self, issue_manager):
        """Test extracting color(id) from enum field."""
        issue_with_color = {
            "id": "TEST-1",
            "customFields": [
                {
                    "name": "Priority",
                    "value": {
                        "name": "High",
                        "localizedName": "Высокий",
                        "color": {"id": "red-1"},
                        "id": "priority-high",
                    },
                    "$type": "SingleEnumIssueCustomField",
                }
            ],
        }
        value = issue_manager._get_custom_field_value(issue_with_color, "Priority")
        assert value == "Высокий"

    def test_get_custom_field_value_full_name_priority(self, issue_manager):
        """Test fullName has higher priority than name."""
        issue_with_names = {
            "id": "TEST-1",
            "customFields": [
                {
                    "name": "Assignee",
                    "value": {"name": "jdoe", "fullName": "John Doe", "login": "john.doe", "id": "user-456"},
                    "$type": "SingleUserIssueCustomField",
                }
            ],
        }
        value = issue_manager._get_custom_field_value(issue_with_names, "Assignee")
        assert value == "John Doe"

    def test_get_custom_field_value_is_resolved(self, issue_manager):
        """Test extracting isResolved boolean field."""
        issue_with_resolved = {
            "id": "TEST-1",
            "customFields": [
                {
                    "name": "Resolved",
                    "value": {"isResolved": True, "name": "Fixed", "id": "state-fixed"},
                    "$type": "StateIssueCustomField",
                }
            ],
        }
        value = issue_manager._get_custom_field_value(issue_with_resolved, "Resolved")
        assert value == "Fixed"

    def test_get_custom_field_value_localized_name(self, issue_manager):
        """Test extracting localizedName field."""
        issue_with_localized = {
            "id": "TEST-1",
            "customFields": [
                {
                    "name": "Status",
                    "value": {"localizedName": "En Progreso", "name": "In Progress", "id": "status-progress"},
                    "$type": "SingleEnumIssueCustomField",
                }
            ],
        }
        value = issue_manager._get_custom_field_value(issue_with_localized, "Status")
        assert value == "En Progreso"

    def test_get_custom_field_value_minutes(self, issue_manager):
        """Test extracting minutes time field."""
        issue_with_time = {
            "id": "TEST-1",
            "customFields": [
                {"name": "Time Spent", "value": {"minutes": 120, "id": "time-1"}, "$type": "PeriodIssueCustomField"}
            ],
        }
        value = issue_manager._get_custom_field_value(issue_with_time, "Time Spent")
        assert value == "120"

    def test_get_custom_field_value_presentation(self, issue_manager):
        """Test extracting presentation field (highest priority)."""
        issue_with_presentation = {
            "id": "TEST-1",
            "customFields": [
                {
                    "name": "Due Date",
                    "value": {
                        "presentation": "Dec 25, 2024",
                        "timestamp": 1735084800000,
                        "name": "2024-12-25",
                        "id": "date-1",
                    },
                    "$type": "DateIssueCustomField",
                }
            ],
        }
        value = issue_manager._get_custom_field_value(issue_with_presentation, "Due Date")
        assert value == "Dec 25, 2024"

    def test_get_custom_field_value_text_field(self, issue_manager):
        """Test extracting rich text field."""
        issue_with_text = {
            "id": "TEST-1",
            "customFields": [
                {
                    "name": "Comments",
                    "value": {"text": "This is a rich text comment with **bold** formatting.", "id": "text-1"},
                    "$type": "TextIssueCustomField",
                }
            ],
        }
        value = issue_manager._get_custom_field_value(issue_with_text, "Comments")
        assert value == "This is a rich text comment with **bold** formatting."

    def test_get_custom_field_value_complex_multi_value(self, issue_manager):
        """Test handling complex multi-value fields with new extraction logic."""
        issue_with_complex_multi = {
            "id": "TEST-1",
            "customFields": [
                {
                    "name": "Reviewers",
                    "value": [
                        {
                            "fullName": "Alice Smith",
                            "name": "asmith",
                            "avatarUrl": "https://example.com/alice.jpg",
                            "id": "user-alice",
                        },
                        {
                            "fullName": "Bob Johnson",
                            "name": "bjohnson",
                            "avatarUrl": "https://example.com/bob.jpg",
                            "id": "user-bob",
                        },
                    ],
                    "$type": "MultiUserIssueCustomField",
                }
            ],
        }
        value = issue_manager._get_custom_field_value(issue_with_complex_multi, "Reviewers")
        assert value == "Alice Smith, Bob Johnson"

    def test_get_custom_field_value_fallback_to_id(self, issue_manager):
        """Test fallback to id when no other fields are available."""
        issue_with_id_only = {
            "id": "TEST-1",
            "customFields": [
                {"name": "Custom", "value": {"id": "custom-field-123"}, "$type": "CustomIssueCustomField"}
            ],
        }
        value = issue_manager._get_custom_field_value(issue_with_id_only, "Custom")
        assert value == "custom-field-123"

    def test_get_custom_field_value_empty_dict(self, issue_manager):
        """Test handling empty value dictionary."""
        issue_with_empty_dict = {
            "id": "TEST-1",
            "customFields": [{"name": "Empty", "value": {}, "$type": "CustomIssueCustomField"}],
        }
        value = issue_manager._get_custom_field_value(issue_with_empty_dict, "Empty")
        assert value is None

    def test_extract_dict_value_color_nested(self, issue_manager):
        """Test _extract_dict_value method with nested color structure."""
        color_dict = {"name": "High Priority", "color": {"id": "red-1", "value": "#FF0000"}, "id": "priority-high"}
        value = issue_manager._extract_dict_value(color_dict)
        assert value == "High Priority"

    def test_extract_dict_value_invalid_input(self, issue_manager):
        """Test _extract_dict_value method with invalid input."""
        value = issue_manager._extract_dict_value("not a dict")
        assert value is None

        value = issue_manager._extract_dict_value(None)
        assert value is None


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


class TestIssueTablePagination:
    """Test pagination functionality for issue table display."""

    @pytest.fixture
    def sample_issues(self):
        """Generate sample issues for pagination testing."""
        issues = []
        for i in range(100):
            issues.append(
                {
                    "id": f"TEST-{i + 1}",
                    "numberInProject": i + 1,
                    "summary": f"Test Issue {i + 1}",
                    "state": {"name": "Open"},
                    "priority": {"name": "Normal"},
                    "type": {"name": "Task"},
                    "assignee": {"fullName": f"User {i + 1}"},
                    "project": {"shortName": "TEST", "name": "Test Project"},
                }
            )
        return issues

    @patch("builtins.input")
    def test_display_issues_table_paginated_basic(self, mock_input, issue_manager, sample_issues):
        """Test basic paginated display functionality."""
        mock_input.return_value = "q"

        with patch.object(issue_manager, "console") as mock_console:
            issue_manager.display_issues_table_paginated(sample_issues[:10], page_size=5)

            # Should display the table and pagination info
            assert mock_console.print.call_count >= 1

    @patch("builtins.input")
    def test_display_issues_table_paginated_navigation(self, mock_input, issue_manager, sample_issues):
        """Test navigation through pages."""
        mock_input.side_effect = ["n", "p", "q"]

        with patch.object(issue_manager, "console") as mock_console:
            issue_manager.display_issues_table_paginated(sample_issues[:10], page_size=3)

            # Should have multiple print calls for navigation
            assert mock_console.print.call_count >= 3

    def test_display_issues_table_paginated_empty(self, issue_manager):
        """Test paginated display with empty data."""
        with patch.object(issue_manager, "console") as mock_console:
            issue_manager.display_issues_table_paginated([], page_size=5)

            mock_console.print.assert_called_once_with("No issues found.", style="yellow")

    def test_display_issues_table_paginated_show_all(self, issue_manager, sample_issues):
        """Test show_all option."""
        with patch.object(issue_manager, "console") as mock_console:
            issue_manager.display_issues_table_paginated(sample_issues[:10], show_all=True)

            # Should display all data without pagination
            assert mock_console.print.call_count == 1

    def test_display_issues_table_paginated_small_dataset(self, issue_manager, sample_issues):
        """Test with dataset smaller than page size."""
        with patch.object(issue_manager, "console") as mock_console:
            issue_manager.display_issues_table_paginated(sample_issues[:5], page_size=10)

            # Should display all data without pagination
            assert mock_console.print.call_count == 1

    @patch("builtins.input")
    def test_display_issues_table_paginated_start_page(self, mock_input, issue_manager, sample_issues):
        """Test starting from a specific page."""
        mock_input.return_value = "q"

        with patch.object(issue_manager, "console") as mock_console:
            issue_manager.display_issues_table_paginated(sample_issues[:20], page_size=5, start_page=3)

            # Should start from page 3
            assert mock_console.print.call_count >= 1

    def test_build_issues_table_format(self, issue_manager, sample_issues):
        """Test that the table builder formats issues correctly."""
        sample_issue = sample_issues[0]

        # Call the paginated method to test the internal table builder
        with patch.object(issue_manager, "console") as mock_console:
            issue_manager.display_issues_table_paginated([sample_issue], show_all=True)

            # Verify the table was printed
            mock_console.print.assert_called_once()
            # The argument should be a Rich Table object
            table_arg = mock_console.print.call_args[0][0]
            assert hasattr(table_arg, "add_row")  # Rich Table has add_row method

    def test_paginated_table_handles_custom_fields(self, issue_manager):
        """Test that paginated table handles custom fields correctly."""
        issue_with_custom_fields = {
            "id": "TEST-1",
            "numberInProject": 1,
            "summary": "Test Issue",
            "project": {"shortName": "TEST", "name": "Test Project"},
            "customFields": [
                {"name": "State", "value": {"name": "In Progress"}, "$type": "StateIssueCustomField"},
                {"name": "Priority", "value": {"name": "High"}, "$type": "EnumIssueCustomField"},
                {"name": "Type", "value": {"name": "Bug"}, "$type": "EnumIssueCustomField"},
                {"name": "Assignee", "value": {"fullName": "John Doe"}, "$type": "UserIssueCustomField"},
            ],
        }

        with patch.object(issue_manager, "console") as mock_console:
            issue_manager.display_issues_table_paginated([issue_with_custom_fields], show_all=True)

            # Should handle custom fields without error
            mock_console.print.assert_called_once()

    def test_paginated_table_truncates_long_summary(self, issue_manager):
        """Test that long summaries are properly truncated."""
        issue_with_long_summary = {
            "id": "TEST-1",
            "numberInProject": 1,
            "summary": "This is a very long summary that should be truncated when displayed",
            "project": {"shortName": "TEST", "name": "Test Project"},
        }

        with patch.object(issue_manager, "console") as mock_console:
            issue_manager.display_issues_table_paginated([issue_with_long_summary], show_all=True)

            # Should truncate without error
            mock_console.print.assert_called_once()

    def test_paginated_table_user_friendly_ids(self, issue_manager):
        """Test that user-friendly IDs are displayed correctly."""
        issue_with_project_info = {
            "id": "internal-id-123",
            "numberInProject": 42,
            "summary": "Test Issue",
            "project": {"shortName": "PROJ", "name": "Test Project"},
        }

        with patch.object(issue_manager, "console") as mock_console:
            issue_manager.display_issues_table_paginated([issue_with_project_info], show_all=True)

            # Should format ID as PROJ-42
            mock_console.print.assert_called_once()
