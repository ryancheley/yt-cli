"""Tests for board management functionality."""

from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from youtrack_cli.auth import AuthConfig, AuthManager
from youtrack_cli.boards import BoardManager


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
def board_manager(mock_auth_manager):
    """Board manager instance for testing."""
    return BoardManager(mock_auth_manager)


class TestBoardManager:
    """Test cases for BoardManager class."""

    @pytest.mark.asyncio
    async def test_list_boards_success(self, board_manager):
        """Test successful board listing."""
        mock_response = [
            {
                "id": "123",
                "name": "Test Board",
                "projects": [{"name": "Test Project"}],
                "owner": {"name": "Test User"},
            }
        ]

        with patch("youtrack_cli.boards.get_client_manager") as mock_get_client_manager:
            mock_resp = Mock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = mock_response
            mock_resp.text = '{"mock": "response"}'
            mock_resp.headers = {"content-type": "application/json"}

            mock_client_manager = Mock()
            mock_client_manager.make_request = AsyncMock(return_value=mock_resp)
            mock_get_client_manager.return_value = mock_client_manager

            result = await board_manager.list_boards()

            assert result["status"] == "success"
            assert result["boards"] == mock_response

    @pytest.mark.asyncio
    async def test_list_boards_with_project_filter(self, board_manager):
        """Test board listing with project filter."""
        mock_response = [
            {
                "id": "123",
                "name": "Test Board",
                "projects": [{"name": "Test Project"}],
                "owner": {"name": "Test User"},
            }
        ]

        with patch("youtrack_cli.boards.get_client_manager") as mock_get_client_manager:
            mock_resp = Mock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = mock_response
            mock_resp.text = '{"mock": "response"}'
            mock_resp.headers = {"content-type": "application/json"}

            mock_client_manager = Mock()
            mock_client_manager.make_request = AsyncMock(return_value=mock_resp)
            mock_get_client_manager.return_value = mock_client_manager

            result = await board_manager.list_boards(project_id="TEST")

            assert result["status"] == "success"
            assert result["boards"] == mock_response

    @pytest.mark.asyncio
    async def test_list_boards_not_authenticated(self, mock_auth_manager):
        """Test board listing when not authenticated."""
        mock_auth_manager.load_credentials.return_value = None
        board_manager = BoardManager(mock_auth_manager)

        result = await board_manager.list_boards()

        assert result["status"] == "error"
        assert result["message"] == "Not authenticated"

    @pytest.mark.asyncio
    async def test_view_board_success(self, board_manager):
        """Test successful board viewing."""
        mock_response = {
            "id": "123",
            "name": "Test Board",
            "owner": {"name": "Test User"},
            "projects": [{"name": "Test Project"}],
            "columns": [{"name": "To Do"}, {"name": "In Progress"}, {"name": "Done"}],
            "sprints": [{"name": "Sprint 1"}],
        }

        with patch("youtrack_cli.boards.get_client_manager") as mock_get_client_manager:
            mock_resp = Mock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = mock_response
            mock_resp.text = '{"mock": "response"}'
            mock_resp.headers = {"content-type": "application/json"}

            mock_client_manager = Mock()
            mock_client_manager.make_request = AsyncMock(return_value=mock_resp)
            mock_get_client_manager.return_value = mock_client_manager

            result = await board_manager.view_board("123")

            assert result["status"] == "success"
            assert result["board"] == mock_response

    @pytest.mark.asyncio
    async def test_view_board_not_authenticated(self, mock_auth_manager):
        """Test board viewing when not authenticated."""
        mock_auth_manager.load_credentials.return_value = None
        board_manager = BoardManager(mock_auth_manager)

        result = await board_manager.view_board("123")

        assert result["status"] == "error"
        assert result["message"] == "Not authenticated"

    @pytest.mark.asyncio
    async def test_update_board_success(self, board_manager):
        """Test successful board updating."""
        mock_response = {
            "id": "123",
            "name": "Updated Board Name",
            "owner": {"name": "Test User"},
        }

        with patch("youtrack_cli.boards.get_client_manager") as mock_get_client_manager:
            mock_resp = Mock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = mock_response
            mock_resp.text = '{"mock": "response"}'
            mock_resp.headers = {"content-type": "application/json"}

            mock_client_manager = Mock()
            mock_client_manager.make_request = AsyncMock(return_value=mock_resp)
            mock_get_client_manager.return_value = mock_client_manager

            result = await board_manager.update_board("123", name="Updated Board Name")

            assert result["status"] == "success"
            assert result["board"] == mock_response

    @pytest.mark.asyncio
    async def test_update_board_no_fields(self, board_manager):
        """Test board updating with no fields provided."""
        result = await board_manager.update_board("123")

        assert result["status"] == "error"
        assert result["message"] == "No update fields provided"

    @pytest.mark.asyncio
    async def test_update_board_not_authenticated(self, mock_auth_manager):
        """Test board updating when not authenticated."""
        mock_auth_manager.load_credentials.return_value = None
        board_manager = BoardManager(mock_auth_manager)

        result = await board_manager.update_board("123", name="New Name")

        assert result["status"] == "error"
        assert result["message"] == "Not authenticated"

    @pytest.mark.asyncio
    async def test_list_boards_general_error(self, board_manager):
        """Test board listing with general error."""
        with patch("youtrack_cli.boards.get_client_manager") as mock_get_client_manager:
            mock_client_manager = Mock()
            mock_client_manager.make_request = AsyncMock(side_effect=Exception("Connection error"))
            mock_get_client_manager.return_value = mock_client_manager

            result = await board_manager.list_boards()

            assert result["status"] == "error"
            assert "Connection error" in result["message"]

    @pytest.mark.asyncio
    async def test_view_board_general_error(self, board_manager):
        """Test board viewing with general error."""
        with patch("youtrack_cli.boards.get_client_manager") as mock_get_client_manager:
            mock_client_manager = Mock()
            mock_client_manager.make_request = AsyncMock(side_effect=Exception("Connection error"))
            mock_get_client_manager.return_value = mock_client_manager

            result = await board_manager.view_board("123")

            assert result["status"] == "error"
            assert "Connection error" in result["message"]

    @pytest.mark.asyncio
    async def test_update_board_general_error(self, board_manager):
        """Test board updating with general error."""
        with patch("youtrack_cli.boards.get_client_manager") as mock_get_client_manager:
            mock_client_manager = Mock()
            mock_client_manager.make_request = AsyncMock(side_effect=Exception("Connection error"))
            mock_get_client_manager.return_value = mock_client_manager

            result = await board_manager.update_board("123", name="New Name")

            assert result["status"] == "error"
            assert "Connection error" in result["message"]
