"""Tests for UserService."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from youtrack_cli.services.users import UserService


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
                    "success": True,
                    "data": [
                        {"id": "user1", "login": "testuser1", "fullName": "Test User 1"},
                        {"id": "user2", "login": "testuser2", "fullName": "Test User 2"},
                    ],
                },
            ):
                result = await user_service.list_users()

        assert result["success"] is True
        assert len(result["data"]) == 2
        assert result["data"][0]["login"] == "testuser1"

    @pytest.mark.asyncio
    async def test_list_users_with_query(self, user_service):
        """Test user listing with search query."""
        mock_response = MagicMock()
        mock_response.status = 200

        with patch.object(user_service, "_make_request", return_value=mock_response) as mock_request:
            with patch.object(user_service, "_handle_response", return_value={"success": True, "data": []}):
                await user_service.list_users(query="test")

        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert call_args[0][1] == "users"
        assert "query" in call_args[1]["params"]
        assert call_args[1]["params"]["query"] == "test"

    @pytest.mark.asyncio
    async def test_list_users_with_parameters(self, user_service):
        """Test user listing with various parameters."""
        mock_response = MagicMock()
        mock_response.status = 200

        with patch.object(user_service, "_make_request", return_value=mock_response) as mock_request:
            with patch.object(user_service, "_handle_response", return_value={"success": True, "data": []}):
                await user_service.list_users(fields="id,login,fullName", top=10, skip=5)

        call_args = mock_request.call_args
        params = call_args[1]["params"]
        assert params["fields"] == "id,login,fullName"
        assert params["$top"] == "10"
        assert params["$skip"] == "5"

    @pytest.mark.asyncio
    async def test_get_user_success(self, user_service):
        """Test successful user retrieval."""
        mock_response = MagicMock()
        mock_response.status = 200

        with patch.object(user_service, "_make_request", return_value=mock_response):
            with patch.object(
                user_service,
                "_handle_response",
                return_value={"success": True, "data": {"id": "user1", "login": "testuser"}},
            ):
                result = await user_service.get_user("user1")

        assert result["success"] is True
        assert result["data"]["login"] == "testuser"

    @pytest.mark.asyncio
    async def test_create_user_success(self, user_service):
        """Test successful user creation."""
        mock_response = MagicMock()
        mock_response.status = 201

        with patch.object(user_service, "_make_request", return_value=mock_response) as mock_request:
            with patch.object(
                user_service,
                "_handle_response",
                return_value={"success": True, "data": {"id": "newuser", "login": "newuser"}},
            ):
                result = await user_service.create_user("newuser", "New User", "newuser@example.com")

        assert result["success"] is True
        assert result["data"]["login"] == "newuser"
        mock_request.assert_called_once_with(
            "POST",
            "users",
            json_data={
                "login": "newuser",
                "fullName": "New User",
                "email": "newuser@example.com",
                "forceChangePassword": False,
            },
        )

    @pytest.mark.asyncio
    async def test_update_user_success(self, user_service):
        """Test successful user update."""
        mock_response = MagicMock()
        mock_response.status = 200

        with patch.object(user_service, "_make_request", return_value=mock_response) as mock_request:
            with patch.object(
                user_service,
                "_handle_response",
                return_value={"success": True, "data": {"id": "user1", "fullName": "Updated User"}},
            ):
                result = await user_service.update_user("user1", full_name="Updated User")

        assert result["success"] is True
        assert result["data"]["fullName"] == "Updated User"
        mock_request.assert_called_once_with("POST", "users/user1", json_data={"fullName": "Updated User"})

    @pytest.mark.asyncio
    async def test_delete_user_success(self, user_service):
        """Test successful user deletion."""
        mock_response = MagicMock()
        mock_response.status = 200

        with patch.object(user_service, "_make_request", return_value=mock_response) as mock_request:
            with patch.object(user_service, "_handle_response", return_value={"success": True, "data": {}}):
                result = await user_service.delete_user("user1")

        assert result["success"] is True
        mock_request.assert_called_once_with("DELETE", "users/user1")

    @pytest.mark.asyncio
    async def test_get_user_groups_success(self, user_service):
        """Test successful user groups listing."""
        mock_response = MagicMock()
        mock_response.status = 200

        with patch.object(user_service, "_make_request", return_value=mock_response) as mock_request:
            with patch.object(
                user_service,
                "_handle_response",
                return_value={"success": True, "data": [{"id": "group1", "name": "Developers"}]},
            ):
                result = await user_service.get_user_groups("user1")

        assert result["success"] is True
        assert len(result["data"]) == 1
        assert result["data"][0]["name"] == "Developers"
        mock_request.assert_called_once_with(
            "GET", "users/user1/groups", params={"fields": "id,name,description,autoJoin,teamAutoJoin"}
        )

    @pytest.mark.asyncio
    async def test_add_user_to_group_success(self, user_service):
        """Test successful user addition to group."""
        mock_response = MagicMock()
        mock_response.status = 200

        with patch.object(user_service, "_make_request", return_value=mock_response) as mock_request:
            with patch.object(user_service, "_handle_response", return_value={"success": True, "data": {}}):
                result = await user_service.add_user_to_group("user1", "group1")

        assert result["success"] is True
        mock_request.assert_called_once_with("POST", "users/user1/groups", json_data={"id": "group1"})

    @pytest.mark.asyncio
    async def test_remove_user_from_group_success(self, user_service):
        """Test successful user removal from group."""
        mock_response = MagicMock()
        mock_response.status = 200

        with patch.object(user_service, "_make_request", return_value=mock_response) as mock_request:
            with patch.object(user_service, "_handle_response", return_value={"success": True, "data": {}}):
                result = await user_service.remove_user_from_group("user1", "group1")

        assert result["success"] is True
        mock_request.assert_called_once_with("DELETE", "users/user1/groups/group1")

    @pytest.mark.asyncio
    async def test_ban_user_success(self, user_service):
        """Test successful user banning."""
        mock_response = MagicMock()
        mock_response.status = 200

        with patch.object(user_service, "_make_request", return_value=mock_response) as mock_request:
            with patch.object(user_service, "_handle_response", return_value={"success": True, "data": {}}):
                result = await user_service.ban_user("user1")

        assert result["success"] is True
        mock_request.assert_called_once_with("POST", "users/user1", json_data={"banned": True})

    @pytest.mark.asyncio
    async def test_error_handling(self, user_service):
        """Test error handling in user operations."""
        with patch.object(user_service, "_make_request", side_effect=ValueError("Invalid request")):
            result = await user_service.list_users()

        assert result["success"] is False
        assert "Invalid request" in result["error"]

    @pytest.mark.asyncio
    async def test_exception_handling(self, user_service):
        """Test general exception handling."""
        with patch.object(user_service, "_make_request", side_effect=Exception("Network error")):
            result = await user_service.get_user("user1")

        assert result["success"] is False
        assert "Error getting user" in result["error"]

    @pytest.mark.asyncio
    async def test_get_user_roles_success(self, user_service):
        """Test successful user roles retrieval."""
        mock_response = MagicMock()
        mock_response.status = 200

        with patch.object(user_service, "_make_request", return_value=mock_response) as mock_request:
            with patch.object(
                user_service,
                "_handle_response",
                return_value={"success": True, "data": [{"id": "role1", "name": "Admin"}]},
            ):
                result = await user_service.get_user_roles("user1")

        assert result["success"] is True
        assert len(result["data"]) == 1
        assert result["data"][0]["name"] == "Admin"
        mock_request.assert_called_once_with("GET", "users/user1/roles", params={"fields": "id,name,description"})

    @pytest.mark.asyncio
    async def test_get_user_teams_success(self, user_service):
        """Test successful user teams retrieval."""
        mock_response = MagicMock()
        mock_response.status = 200

        with patch.object(user_service, "_make_request", return_value=mock_response) as mock_request:
            with patch.object(
                user_service,
                "_handle_response",
                return_value={"success": True, "data": [{"id": "team1", "name": "Development"}]},
            ):
                result = await user_service.get_user_teams("user1")

        assert result["success"] is True
        assert len(result["data"]) == 1
        assert result["data"][0]["name"] == "Development"
        mock_request.assert_called_once_with("GET", "users/user1/teams", params={"fields": "id,name,description"})

    @pytest.mark.asyncio
    async def test_change_user_password_success(self, user_service):
        """Test successful password change."""
        mock_response = MagicMock()
        mock_response.status = 200

        with patch.object(user_service, "_make_request", return_value=mock_response) as mock_request:
            with patch.object(user_service, "_handle_response", return_value={"success": True, "data": {}}):
                result = await user_service.change_user_password("user1", "newpassword", force_change=True)

        assert result["success"] is True
        mock_request.assert_called_once_with(
            "POST", "users/user1", json_data={"password": "newpassword", "forceChangePassword": True}
        )

    @pytest.mark.asyncio
    async def test_get_user_permissions_success(self, user_service):
        """Test successful user permissions retrieval."""
        mock_response = MagicMock()
        mock_response.status = 200

        with patch.object(user_service, "_make_request", return_value=mock_response) as mock_request:
            with patch.object(user_service, "_handle_response", return_value={"success": True, "data": []}):
                result = await user_service.get_user_permissions("user1", project_id="project1")

        assert result["success"] is True
        mock_request.assert_called_once_with("GET", "users/user1/permissions", params={"project": "project1"})
