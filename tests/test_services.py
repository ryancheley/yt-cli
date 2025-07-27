"""Tests for all service classes."""

from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from youtrack_cli.services.base import BaseService
from youtrack_cli.services.issues import IssueService
from youtrack_cli.services.projects import ProjectService
from youtrack_cli.services.users import UserService


class TestBaseService:
    """Test cases for BaseService."""

    @pytest.fixture
    def mock_auth_manager(self):
        """Create mock auth manager."""
        return Mock()

    @pytest.fixture
    def base_service(self, mock_auth_manager):
        """Create BaseService instance."""
        return BaseService(mock_auth_manager)

    def test_init(self, mock_auth_manager):
        """Test BaseService initialization."""
        service = BaseService(mock_auth_manager)
        assert service.auth_manager == mock_auth_manager

    def test_create_error_response(self, base_service):
        """Test _create_error_response method."""
        error_msg = "Test error"
        response = base_service._create_error_response(error_msg)

        assert response["status"] == "error"
        assert response["message"] == error_msg

    def test_parse_json_response_success(self, base_service):
        """Test successful JSON parsing."""
        mock_response = Mock()
        mock_response.headers = {"content-type": "application/json"}
        mock_response.text = '{"key": "value"}'
        mock_response.json.return_value = {"key": "value"}

        result = base_service._parse_json_response(mock_response)
        assert result == {"key": "value"}

    def test_parse_json_response_empty(self, base_service):
        """Test parsing empty response."""
        mock_response = Mock()
        mock_response.text = ""

        with pytest.raises(ValueError, match="Empty response body"):
            base_service._parse_json_response(mock_response)

    def test_parse_json_response_not_json(self, base_service):
        """Test parsing non-JSON response."""
        mock_response = Mock()
        mock_response.headers = {"content-type": "text/html"}
        mock_response.text = "<html>Not JSON</html>"

        with pytest.raises(ValueError, match="Response is not JSON"):
            base_service._parse_json_response(mock_response)


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
        with (
            patch.object(issue_service, "_make_request", side_effect=Exception("Network error")),
            patch.object(
                issue_service, "_create_error_response", return_value={"status": "error", "message": "Network error"}
            ),
        ):
            result = await issue_service.create_issue(project_id="TEST", summary="Test Issue")

            assert result["status"] == "error"
            assert "Network error" in result["message"]


class TestProjectService:
    """Test cases for ProjectService."""

    @pytest.fixture
    def mock_auth_manager(self):
        """Create mock auth manager."""
        return MagicMock()

    @pytest.fixture
    def project_service(self, mock_auth_manager):
        """Create ProjectService instance."""
        return ProjectService(mock_auth_manager)

    def test_init(self, mock_auth_manager):
        """Test ProjectService initialization."""
        service = ProjectService(mock_auth_manager)
        assert service.auth_manager == mock_auth_manager

    @pytest.mark.asyncio
    async def test_create_project_success(self, project_service):
        """Test create_project with successful response."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": "TEST", "name": "Test Project"}

        with (
            patch.object(project_service, "_make_request", return_value=mock_response),
            patch.object(
                project_service, "_handle_response", return_value={"status": "success", "data": {"id": "TEST"}}
            ),
        ):
            result = await project_service.create_project(short_name="TEST", name="Test Project")

            assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_get_project_success(self, project_service):
        """Test get_project with successful response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "TEST", "name": "Test Project"}

        with (
            patch.object(project_service, "_make_request", return_value=mock_response),
            patch.object(
                project_service, "_handle_response", return_value={"status": "success", "data": {"id": "TEST"}}
            ),
        ):
            result = await project_service.get_project("TEST")

            assert result["status"] == "success"


class TestUserService:
    """Test cases for UserService."""

    @pytest.fixture
    def mock_auth_manager(self):
        """Create a mock auth manager for testing."""
        return MagicMock()

    @pytest.fixture
    def user_service(self, mock_auth_manager):
        """Create UserService instance with mock auth manager."""
        return UserService(mock_auth_manager)

    @pytest.mark.asyncio
    async def test_list_users_success(self, user_service):
        """Test successful user listing."""
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(
            return_value=[
                {"id": "user1", "login": "testuser1", "fullName": "Test User 1"},
                {"id": "user2", "login": "testuser2", "fullName": "Test User 2"},
            ]
        )

        with patch.object(user_service, "_make_request", return_value=mock_response):
            with patch.object(
                user_service,
                "_handle_response",
                return_value={
                    "status": "success",
                    "data": [
                        {"id": "user1", "login": "testuser1", "fullName": "Test User 1"},
                        {"id": "user2", "login": "testuser2", "fullName": "Test User 2"},
                    ],
                },
            ):
                result = await user_service.list_users()

        assert result["status"] == "success"
        assert len(result["data"]) == 2

    @pytest.mark.asyncio
    async def test_create_user_success(self, user_service):
        """Test successful user creation."""
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": "newuser", "login": "newuser", "fullName": "New User"}

        with patch.object(user_service, "_make_request", return_value=mock_response):
            with patch.object(
                user_service,
                "_handle_response",
                return_value={"status": "success", "data": {"id": "newuser"}},
            ):
                result = await user_service.create_user(
                    login="newuser", password="password", full_name="New User", email="new@example.com"
                )

        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_get_user_success(self, user_service):
        """Test successful user retrieval."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "user1", "login": "testuser", "fullName": "Test User"}

        with patch.object(user_service, "_make_request", return_value=mock_response):
            with patch.object(
                user_service,
                "_handle_response",
                return_value={"status": "success", "data": {"id": "user1"}},
            ):
                result = await user_service.get_user("user1")

        assert result["status"] == "success"
