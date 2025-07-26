"""Tests for IssueService."""

from unittest.mock import MagicMock, Mock, patch

import pytest

from youtrack_cli.services.issues import IssueService


class TestIssueService:
    """Test cases for IssueService."""

    @pytest.fixture
    def mock_auth_manager(self):
        """Create mock auth manager."""
        return MagicMock()

    @pytest.fixture
    def issue_service(self, mock_auth_manager):
        """Create IssueService instance."""
        return IssueService(mock_auth_manager)

    def test_init(self, mock_auth_manager):
        """Test IssueService initialization."""
        service = IssueService(mock_auth_manager)
        assert service.auth_manager == mock_auth_manager

    @pytest.mark.asyncio
    async def test_create_issue_success(self, issue_service):
        """Test create_issue with successful response."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": "TEST-123", "summary": "Test Issue"}

        with (
            patch.object(issue_service, "_make_request", return_value=mock_response),
            patch.object(
                issue_service, "_handle_response", return_value={"status": "success", "data": {"id": "TEST-123"}}
            ),
        ):
            result = await issue_service.create_issue(
                project_id="TEST", summary="Test Issue", description="Test Description"
            )

            assert result["status"] == "success"
            assert result["data"]["id"] == "TEST-123"

    @pytest.mark.asyncio
    async def test_create_issue_error(self, issue_service):
        """Test create_issue with error response."""
        with patch.object(issue_service, "_make_request", side_effect=Exception("API Error")):
            result = await issue_service.create_issue(project_id="TEST", summary="Test Issue")

            assert result["status"] == "error"
            assert "API Error" in result["message"]

    @pytest.mark.asyncio
    async def test_get_issue_success(self, issue_service):
        """Test get_issue with successful response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "TEST-123", "summary": "Test Issue"}

        with (
            patch.object(issue_service, "_make_request", return_value=mock_response),
            patch.object(
                issue_service, "_handle_response", return_value={"status": "success", "data": {"id": "TEST-123"}}
            ),
        ):
            result = await issue_service.get_issue("TEST-123")

            assert result["status"] == "success"
            assert result["data"]["id"] == "TEST-123"

    @pytest.mark.asyncio
    async def test_search_issues_success(self, issue_service):
        """Test search_issues with successful response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"id": "TEST-123", "summary": "Test Issue"}]

        with (
            patch.object(issue_service, "_make_request", return_value=mock_response),
            patch.object(
                issue_service, "_handle_response", return_value={"status": "success", "data": [{"id": "TEST-123"}]}
            ),
        ):
            result = await issue_service.search_issues("State: Open")

            assert result["status"] == "success"
            assert len(result["data"]) == 1

    @pytest.mark.asyncio
    async def test_update_issue_success(self, issue_service):
        """Test update_issue with successful response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "TEST-123", "summary": "Updated Issue"}

        with (
            patch.object(issue_service, "_make_request", return_value=mock_response),
            patch.object(
                issue_service, "_handle_response", return_value={"status": "success", "data": {"id": "TEST-123"}}
            ),
        ):
            result = await issue_service.update_issue("TEST-123", summary="Updated Issue")

            assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_delete_issue_success(self, issue_service):
        """Test delete_issue with successful response."""
        mock_response = Mock()
        mock_response.status_code = 200

        with (
            patch.object(issue_service, "_make_request", return_value=mock_response),
            patch.object(issue_service, "_handle_response", return_value={"status": "success", "data": None}),
        ):
            result = await issue_service.delete_issue("TEST-123")

            assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_assign_issue_success(self, issue_service):
        """Test assign_issue with successful response."""
        mock_response = Mock()
        mock_response.status_code = 200

        with (
            patch.object(issue_service, "_make_request", return_value=mock_response),
            patch.object(issue_service, "_handle_response", return_value={"status": "success", "data": None}),
        ):
            result = await issue_service.assign_issue("TEST-123", "user@example.com")

            assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_add_tag_success(self, issue_service):
        """Test add_tag with successful response."""
        mock_response = Mock()
        mock_response.status_code = 200

        with (
            patch.object(issue_service, "_make_request", return_value=mock_response),
            patch.object(issue_service, "_handle_response", return_value={"status": "success", "data": None}),
        ):
            result = await issue_service.add_tag("TEST-123", "bug")

            assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_list_comments_success(self, issue_service):
        """Test list_comments with successful response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"id": "1", "text": "Test comment"}]

        with (
            patch.object(issue_service, "_make_request", return_value=mock_response),
            patch.object(issue_service, "_handle_response", return_value={"status": "success", "data": [{"id": "1"}]}),
        ):
            result = await issue_service.list_comments("TEST-123")

            assert result["status"] == "success"
            assert len(result["data"]) == 1

    @pytest.mark.asyncio
    async def test_add_comment_success(self, issue_service):
        """Test add_comment with successful response."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": "1", "text": "Test comment"}

        with (
            patch.object(issue_service, "_make_request", return_value=mock_response),
            patch.object(issue_service, "_handle_response", return_value={"status": "success", "data": {"id": "1"}}),
        ):
            result = await issue_service.add_comment("TEST-123", "Test comment")

            assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_list_links_success(self, issue_service):
        """Test list_links with successful response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"id": "1", "linkType": {"name": "relates to"}}]

        with (
            patch.object(issue_service, "_make_request", return_value=mock_response),
            patch.object(issue_service, "_handle_response", return_value={"status": "success", "data": [{"id": "1"}]}),
        ):
            result = await issue_service.list_links("TEST-123")

            assert result["status"] == "success"
            assert len(result["data"]) == 1
