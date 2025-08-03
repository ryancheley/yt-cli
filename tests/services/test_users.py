"""Tests for UserService."""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from youtrack_cli.auth import AuthManager
from youtrack_cli.services.users import UserService


@pytest.fixture
def auth_manager():
    """Create a mock auth manager."""
    mock_auth = MagicMock(spec=AuthManager)
    return mock_auth


@pytest.fixture
def user_service(auth_manager):
    """Create a UserService instance."""
    return UserService(auth_manager)


@pytest.fixture
def mock_response():
    """Create a mock HTTP response."""
    response = MagicMock(spec=httpx.Response)
    response.status_code = 200
    response.json.return_value = {"id": "user-1", "login": "testuser", "fullName": "Test User"}
    response.headers = {"content-type": "application/json"}
    response.text = '{"id": "user-1", "login": "testuser", "fullName": "Test User"}'
    return response


class TestUserServiceListUsers:
    """Test user listing functionality."""

    @pytest.mark.asyncio
    async def test_list_users_basic(self, user_service, mock_response):
        """Test basic user listing."""
        with (
            patch.object(user_service, "_make_request", new_callable=AsyncMock) as mock_request,
            patch.object(user_service, "_handle_response", new_callable=AsyncMock) as mock_handle,
        ):
            mock_request.return_value = mock_response
            mock_handle.return_value = {
                "status": "success",
                "data": [
                    {"id": "user-1", "login": "testuser", "fullName": "Test User"},
                    {"id": "user-2", "login": "admin", "fullName": "Admin User"},
                ],
            }

            result = await user_service.list_users()

            expected_params = {
                "fields": "id,login,fullName,email,banned,online,guest,ringId,avatarUrl,teams(name,description)"
            }
            mock_request.assert_called_once_with("GET", "users", params=expected_params)
            mock_handle.assert_called_once_with(mock_response)
            assert result["status"] == "success"
            assert len(result["data"]) == 2

    @pytest.mark.asyncio
    async def test_list_users_with_all_parameters(self, user_service, mock_response):
        """Test listing users with all parameters."""
        with (
            patch.object(user_service, "_make_request", new_callable=AsyncMock) as mock_request,
            patch.object(user_service, "_handle_response", new_callable=AsyncMock) as mock_handle,
        ):
            mock_request.return_value = mock_response
            mock_handle.return_value = {"status": "success", "data": []}

            result = await user_service.list_users(fields="id,login,fullName", top=10, skip=5, query="banned: false")

            expected_params = {"fields": "id,login,fullName", "query": "banned: false", "$top": "10", "$skip": "5"}
            mock_request.assert_called_once_with("GET", "users", params=expected_params)
            assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_list_users_value_error(self, user_service):
        """Test list users with ValueError."""
        with (
            patch.object(user_service, "_make_request", new_callable=AsyncMock) as mock_request,
            patch.object(user_service, "_create_error_response") as mock_error,
        ):
            mock_request.side_effect = ValueError("Invalid data")
            mock_error.return_value = {"status": "error", "message": "Invalid data"}

            result = await user_service.list_users()

            mock_error.assert_called_once_with("Invalid data")
            assert result["status"] == "error"

    @pytest.mark.asyncio
    async def test_list_users_general_exception(self, user_service):
        """Test list users with general exception."""
        with (
            patch.object(user_service, "_make_request", new_callable=AsyncMock) as mock_request,
            patch.object(user_service, "_create_error_response") as mock_error,
        ):
            mock_request.side_effect = Exception("Network error")
            mock_error.return_value = {"status": "error", "message": "Error listing users: Network error"}

            result = await user_service.list_users()

            mock_error.assert_called_once_with("Error listing users: Network error")
            assert result["status"] == "error"


class TestUserServiceGetUser:
    """Test user retrieval functionality."""

    @pytest.mark.asyncio
    async def test_get_user_basic(self, user_service, mock_response):
        """Test basic user retrieval."""
        with (
            patch.object(user_service, "_make_request", new_callable=AsyncMock) as mock_request,
            patch.object(user_service, "_handle_response", new_callable=AsyncMock) as mock_handle,
        ):
            mock_request.return_value = mock_response
            mock_handle.return_value = {"status": "success", "data": {"id": "user-1", "login": "testuser"}}

            result = await user_service.get_user("testuser")

            expected_params = {
                "fields": "id,login,fullName,email,banned,online,guest,ringId,avatarUrl,teams(name,description),groups(name,description)"
            }
            mock_request.assert_called_once_with("GET", "users/testuser", params=expected_params)
            mock_handle.assert_called_once_with(mock_response)
            assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_get_user_with_custom_fields(self, user_service, mock_response):
        """Test user retrieval with custom fields."""
        with (
            patch.object(user_service, "_make_request", new_callable=AsyncMock) as mock_request,
            patch.object(user_service, "_handle_response", new_callable=AsyncMock) as mock_handle,
        ):
            mock_request.return_value = mock_response
            mock_handle.return_value = {"status": "success", "data": {"id": "user-1"}}

            result = await user_service.get_user("testuser", fields="id,login")

            expected_params = {"fields": "id,login"}
            mock_request.assert_called_once_with("GET", "users/testuser", params=expected_params)
            assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_get_user_error_handling(self, user_service):
        """Test get user error handling."""
        with (
            patch.object(user_service, "_make_request", new_callable=AsyncMock) as mock_request,
            patch.object(user_service, "_create_error_response") as mock_error,
        ):
            mock_request.side_effect = Exception("Network error")
            mock_error.return_value = {"status": "error", "message": "Error getting user: Network error"}

            result = await user_service.get_user("testuser")

            mock_error.assert_called_once_with("Error getting user: Network error")
            assert result["status"] == "error"


class TestUserServiceCreateUser:
    """Test user creation functionality."""

    @pytest.mark.asyncio
    async def test_create_user_basic(self, user_service, mock_response):
        """Test basic user creation."""
        with (
            patch.object(user_service, "_make_request", new_callable=AsyncMock) as mock_request,
            patch.object(user_service, "_handle_response", new_callable=AsyncMock) as mock_handle,
            patch.object(user_service, "get_user", new_callable=AsyncMock) as mock_get_user,
        ):
            mock_request.return_value = mock_response
            mock_handle.return_value = {"status": "success", "data": {"id": "user-1"}}
            mock_get_user.return_value = {
                "status": "success",
                "data": {"id": "user-1", "login": "testuser", "fullName": "Test User", "email": "test@example.com"},
            }

            result = await user_service.create_user(login="testuser", full_name="Test User", email="test@example.com")

            expected_data = {
                "login": "testuser",
                "fullName": "Test User",
                "email": "test@example.com",
                "forceChangePassword": False,
            }
            mock_request.assert_called_once_with("POST", "../hub/api/rest/users", json_data=expected_data)
            mock_get_user.assert_called_once_with("testuser", fields="id,login,fullName,email,banned,online,guest")
            assert result["status"] == "success"
            assert result["data"]["fullName"] == "Test User"
            assert result["data"]["email"] == "test@example.com"

    @pytest.mark.asyncio
    async def test_create_user_with_password(self, user_service, mock_response):
        """Test user creation with password."""
        with (
            patch.object(user_service, "_make_request", new_callable=AsyncMock) as mock_request,
            patch.object(user_service, "_handle_response", new_callable=AsyncMock) as mock_handle,
            patch.object(user_service, "get_user", new_callable=AsyncMock) as mock_get_user,
        ):
            mock_request.return_value = mock_response
            mock_handle.return_value = {"status": "success"}
            mock_get_user.return_value = {
                "status": "success",
                "data": {"id": "user-1", "login": "testuser", "fullName": "Test User", "email": "test@example.com"},
            }

            result = await user_service.create_user(
                login="testuser",
                full_name="Test User",
                email="test@example.com",
                password="secret123",
                force_change_password=True,
            )

            expected_data = {
                "login": "testuser",
                "fullName": "Test User",
                "email": "test@example.com",
                "password": "secret123",
                "forceChangePassword": True,
            }
            mock_request.assert_called_once_with("POST", "../hub/api/rest/users", json_data=expected_data)
            mock_get_user.assert_called_once_with("testuser", fields="id,login,fullName,email,banned,online,guest")
            assert result["status"] == "success"
            assert result["data"]["fullName"] == "Test User"
            assert result["data"]["email"] == "test@example.com"

    @pytest.mark.asyncio
    async def test_create_user_with_get_user_failure(self, user_service, mock_response):
        """Test user creation when get_user fails - should return fallback data."""
        with (
            patch.object(user_service, "_make_request", new_callable=AsyncMock) as mock_request,
            patch.object(user_service, "_handle_response", new_callable=AsyncMock) as mock_handle,
            patch.object(user_service, "get_user", new_callable=AsyncMock) as mock_get_user,
        ):
            mock_request.return_value = mock_response
            mock_handle.return_value = {"status": "success", "data": {"id": "user-1"}}
            mock_get_user.return_value = {"status": "error", "message": "User not found"}

            result = await user_service.create_user(login="testuser", full_name="Test User", email="test@example.com")

            expected_data = {
                "login": "testuser",
                "fullName": "Test User",
                "email": "test@example.com",
                "forceChangePassword": False,
            }
            mock_request.assert_called_once_with("POST", "../hub/api/rest/users", json_data=expected_data)
            mock_get_user.assert_called_once_with("testuser", fields="id,login,fullName,email,banned,online,guest")
            assert result["status"] == "success"
            assert result["data"]["login"] == "testuser"
            assert result["data"]["fullName"] == "Test User"
            assert result["data"]["email"] == "test@example.com"
            assert "note" in result["data"]

    @pytest.mark.asyncio
    async def test_create_user_error_handling(self, user_service):
        """Test create user error handling."""
        with (
            patch.object(user_service, "_make_request", new_callable=AsyncMock) as mock_request,
            patch.object(user_service, "_create_error_response") as mock_error,
        ):
            mock_request.side_effect = ValueError("Invalid data")
            mock_error.return_value = {"status": "error", "message": "Invalid data"}

            result = await user_service.create_user("testuser", "Test User", "test@example.com")

            mock_error.assert_called_once_with("Invalid data")
            assert result["status"] == "error"


class TestUserServiceUpdateUser:
    """Test user update functionality."""

    @pytest.mark.asyncio
    async def test_update_user_basic(self, user_service, mock_response):
        """Test basic user update."""
        with (
            patch.object(user_service, "_make_request", new_callable=AsyncMock) as mock_request,
            patch.object(user_service, "_handle_response", new_callable=AsyncMock) as mock_handle,
            patch.object(user_service, "get_user", new_callable=AsyncMock) as mock_get_user,
        ):
            # Mock get_user to return user with ringId for initial fetch and updated data for final fetch
            mock_get_user.side_effect = [
                {"status": "success", "data": {"id": "user-1", "login": "testuser", "ringId": "ring-123"}},
                {
                    "status": "success",
                    "data": {"id": "user-1", "login": "testuser", "fullName": "New Name", "email": "test@example.com"},
                },
            ]
            mock_request.return_value = mock_response
            mock_handle.return_value = {"status": "success"}

            result = await user_service.update_user("user-1", full_name="New Name")

            expected_data = {"fullName": "New Name"}
            mock_request.assert_called_once_with("POST", "../hub/api/rest/users/ring-123", json_data=expected_data)
            assert mock_get_user.call_count == 2
            mock_get_user.assert_any_call("user-1", fields="id,login,ringId")
            mock_get_user.assert_any_call("user-1", fields="id,login,fullName,email,banned,online,guest")
            assert result["status"] == "success"
            assert result["data"]["fullName"] == "New Name"

    @pytest.mark.asyncio
    async def test_update_user_all_fields(self, user_service, mock_response):
        """Test user update with all fields."""
        with (
            patch.object(user_service, "_make_request", new_callable=AsyncMock) as mock_request,
            patch.object(user_service, "_handle_response", new_callable=AsyncMock) as mock_handle,
            patch.object(user_service, "get_user", new_callable=AsyncMock) as mock_get_user,
        ):
            # Mock get_user to return user with ringId for initial fetch and updated data for final fetch
            mock_get_user.side_effect = [
                {"status": "success", "data": {"id": "user-1", "login": "testuser", "ringId": "ring-123"}},
                {
                    "status": "success",
                    "data": {
                        "id": "user-1",
                        "login": "testuser",
                        "fullName": "New Name",
                        "email": "new@example.com",
                        "banned": True,
                    },
                },
            ]
            mock_request.return_value = mock_response
            mock_handle.return_value = {"status": "success"}

            result = await user_service.update_user(
                "user-1",
                full_name="New Name",
                email="new@example.com",
                banned=True,
                password="newpass123",
                force_change_password=True,
            )

            expected_data = {
                "fullName": "New Name",
                "email": "new@example.com",
                "banned": True,
                "password": "newpass123",
                "forceChangePassword": True,
            }
            mock_request.assert_called_once_with("POST", "../hub/api/rest/users/ring-123", json_data=expected_data)
            assert mock_get_user.call_count == 2
            mock_get_user.assert_any_call("user-1", fields="id,login,ringId")
            mock_get_user.assert_any_call("user-1", fields="id,login,fullName,email,banned,online,guest")
            assert result["status"] == "success"
            assert result["data"]["fullName"] == "New Name"
            assert result["data"]["email"] == "new@example.com"

    @pytest.mark.asyncio
    async def test_update_user_error_handling(self, user_service):
        """Test update user error handling."""
        with (
            patch.object(user_service, "get_user", new_callable=AsyncMock) as mock_get_user,
            patch.object(user_service, "_create_error_response") as mock_error,
        ):
            mock_get_user.side_effect = Exception("Network error")
            mock_error.return_value = {"status": "error", "message": "Error updating user: Network error"}

            result = await user_service.update_user("user-1", full_name="New Name")

            mock_error.assert_called_once_with("Error updating user: Network error")
            assert result["status"] == "error"


class TestUserServiceDeleteUser:
    """Test user deletion functionality."""

    @pytest.mark.asyncio
    async def test_delete_user(self, user_service, mock_response):
        """Test user deletion."""
        with (
            patch.object(user_service, "_make_request", new_callable=AsyncMock) as mock_request,
            patch.object(user_service, "_handle_response", new_callable=AsyncMock) as mock_handle,
        ):
            mock_request.return_value = mock_response
            mock_handle.return_value = {"status": "success"}

            result = await user_service.delete_user("user-1")

            mock_request.assert_called_once_with("DELETE", "users/user-1")
            mock_handle.assert_called_once_with(mock_response)
            assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_delete_user_error_handling(self, user_service):
        """Test delete user error handling."""
        with (
            patch.object(user_service, "_make_request", new_callable=AsyncMock) as mock_request,
            patch.object(user_service, "_create_error_response") as mock_error,
        ):
            mock_request.side_effect = ValueError("Invalid ID")
            mock_error.return_value = {"status": "error", "message": "Invalid ID"}

            result = await user_service.delete_user("user-1")

            mock_error.assert_called_once_with("Invalid ID")
            assert result["status"] == "error"


class TestUserServiceBanUnban:
    """Test user ban/unban functionality."""

    @pytest.mark.asyncio
    async def test_ban_user(self, user_service, mock_response):
        """Test banning a user."""
        with (
            patch.object(user_service, "get_user", new_callable=AsyncMock) as mock_get_user,
            patch.object(user_service, "_make_request", new_callable=AsyncMock) as mock_request,
            patch.object(user_service, "_handle_response", new_callable=AsyncMock) as mock_handle,
        ):
            # Mock get_user to return user with ringId
            mock_get_user.return_value = {
                "status": "success",
                "data": {"id": "user-1", "login": "testuser", "ringId": "ring-123"},
            }
            mock_request.return_value = mock_response
            mock_handle.return_value = {"status": "success"}

            result = await user_service.ban_user("user-1")

            mock_get_user.assert_called_once_with("user-1", fields="id,login,ringId")
            expected_data = {"banned": True}
            mock_request.assert_called_once_with("POST", "../hub/api/rest/users/ring-123", json_data=expected_data)
            mock_handle.assert_called_once_with(mock_response)
            assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_unban_user(self, user_service, mock_response):
        """Test unbanning a user."""
        with (
            patch.object(user_service, "get_user", new_callable=AsyncMock) as mock_get_user,
            patch.object(user_service, "_make_request", new_callable=AsyncMock) as mock_request,
            patch.object(user_service, "_handle_response", new_callable=AsyncMock) as mock_handle,
        ):
            # Mock get_user to return user with ringId
            mock_get_user.return_value = {
                "status": "success",
                "data": {"id": "user-1", "login": "testuser", "ringId": "ring-123"},
            }
            mock_request.return_value = mock_response
            mock_handle.return_value = {"status": "success"}

            result = await user_service.unban_user("user-1")

            mock_get_user.assert_called_once_with("user-1", fields="id,login,ringId")
            expected_data = {"banned": False}
            mock_request.assert_called_once_with("POST", "../hub/api/rest/users/ring-123", json_data=expected_data)
            mock_handle.assert_called_once_with(mock_response)
            assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_ban_user_error_handling(self, user_service):
        """Test ban user error handling."""
        with (
            patch.object(user_service, "get_user", new_callable=AsyncMock) as mock_get_user,
            patch.object(user_service, "_create_error_response") as mock_error,
        ):
            mock_get_user.side_effect = Exception("Network error")
            mock_error.return_value = {"status": "error", "message": "Error banning user: Network error"}

            result = await user_service.ban_user("user-1")

            mock_error.assert_called_once_with("Error banning user: Network error")
            assert result["status"] == "error"

    @pytest.mark.asyncio
    async def test_unban_user_error_handling(self, user_service):
        """Test unban user error handling."""
        with (
            patch.object(user_service, "get_user", new_callable=AsyncMock) as mock_get_user,
            patch.object(user_service, "_create_error_response") as mock_error,
        ):
            mock_get_user.side_effect = Exception("Network error")
            mock_error.return_value = {"status": "error", "message": "Error unbanning user: Network error"}

            result = await user_service.unban_user("user-1")

            mock_error.assert_called_once_with("Error unbanning user: Network error")
            assert result["status"] == "error"


class TestUserServiceGroups:
    """Test user group management functionality."""

    @pytest.mark.asyncio
    async def test_get_user_groups(self, user_service, mock_response):
        """Test getting user groups."""
        with (
            patch.object(user_service, "_make_request", new_callable=AsyncMock) as mock_request,
            patch.object(user_service, "_handle_response", new_callable=AsyncMock) as mock_handle,
        ):
            mock_request.return_value = mock_response
            mock_handle.return_value = {"status": "success", "data": []}

            result = await user_service.get_user_groups("user-1")

            expected_params = {"fields": "id,name,description,autoJoin,teamAutoJoin"}
            mock_request.assert_called_once_with("GET", "users/user-1/groups", params=expected_params)
            mock_handle.assert_called_once_with(mock_response)
            assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_get_user_groups_custom_fields(self, user_service, mock_response):
        """Test getting user groups with custom fields."""
        with (
            patch.object(user_service, "_make_request", new_callable=AsyncMock) as mock_request,
            patch.object(user_service, "_handle_response", new_callable=AsyncMock) as mock_handle,
        ):
            mock_request.return_value = mock_response
            mock_handle.return_value = {"status": "success", "data": []}

            result = await user_service.get_user_groups("user-1", fields="id,name")

            expected_params = {"fields": "id,name"}
            mock_request.assert_called_once_with("GET", "users/user-1/groups", params=expected_params)
            assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_add_user_to_group(self, user_service, mock_response):
        """Test adding user to group."""
        with (
            patch.object(user_service, "_make_request", new_callable=AsyncMock) as mock_request,
            patch.object(user_service, "_handle_response", new_callable=AsyncMock) as mock_handle,
        ):
            mock_request.return_value = mock_response
            mock_handle.return_value = {"status": "success"}

            result = await user_service.add_user_to_group("user-1", "group-1")

            expected_data = {"id": "group-1"}
            mock_request.assert_called_once_with("POST", "users/user-1/groups", json_data=expected_data)
            mock_handle.assert_called_once_with(mock_response, success_codes=[200, 201])
            assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_remove_user_from_group(self, user_service, mock_response):
        """Test removing user from group."""
        with (
            patch.object(user_service, "_make_request", new_callable=AsyncMock) as mock_request,
            patch.object(user_service, "_handle_response", new_callable=AsyncMock) as mock_handle,
        ):
            mock_request.return_value = mock_response
            mock_handle.return_value = {"status": "success"}

            result = await user_service.remove_user_from_group("user-1", "group-1")

            mock_request.assert_called_once_with("DELETE", "users/user-1/groups/group-1")
            mock_handle.assert_called_once_with(mock_response)
            assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_group_management_error_handling(self, user_service):
        """Test group management error handling."""
        with (
            patch.object(user_service, "_make_request", new_callable=AsyncMock) as mock_request,
            patch.object(user_service, "_create_error_response") as mock_error,
        ):
            mock_request.side_effect = Exception("Network error")
            mock_error.return_value = {"status": "error", "message": "Error getting user groups: Network error"}

            result = await user_service.get_user_groups("user-1")

            mock_error.assert_called_once_with("Error getting user groups: Network error")
            assert result["status"] == "error"


class TestUserServiceRoles:
    """Test user role management functionality."""

    @pytest.mark.asyncio
    async def test_get_user_roles(self, user_service, mock_response):
        """Test getting user roles."""
        with (
            patch.object(user_service, "_make_request", new_callable=AsyncMock) as mock_request,
            patch.object(user_service, "_handle_response", new_callable=AsyncMock) as mock_handle,
        ):
            mock_request.return_value = mock_response
            mock_handle.return_value = {"status": "success", "data": []}

            result = await user_service.get_user_roles("user-1")

            expected_params = {"fields": "id,name,description"}
            mock_request.assert_called_once_with("GET", "users/user-1/roles", params=expected_params)
            mock_handle.assert_called_once_with(mock_response)
            assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_get_user_roles_custom_fields(self, user_service, mock_response):
        """Test getting user roles with custom fields."""
        with (
            patch.object(user_service, "_make_request", new_callable=AsyncMock) as mock_request,
            patch.object(user_service, "_handle_response", new_callable=AsyncMock) as mock_handle,
        ):
            mock_request.return_value = mock_response
            mock_handle.return_value = {"status": "success", "data": []}

            result = await user_service.get_user_roles("user-1", fields="id,name")

            expected_params = {"fields": "id,name"}
            mock_request.assert_called_once_with("GET", "users/user-1/roles", params=expected_params)
            assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_assign_user_role(self, user_service, mock_response):
        """Test assigning user role."""
        with (
            patch.object(user_service, "_make_request", new_callable=AsyncMock) as mock_request,
            patch.object(user_service, "_handle_response", new_callable=AsyncMock) as mock_handle,
        ):
            mock_request.return_value = mock_response
            mock_handle.return_value = {"status": "success"}

            result = await user_service.assign_user_role("user-1", "role-1")

            expected_data = {"id": "role-1"}
            mock_request.assert_called_once_with("POST", "users/user-1/roles", json_data=expected_data)
            mock_handle.assert_called_once_with(mock_response, success_codes=[200, 201])
            assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_remove_user_role(self, user_service, mock_response):
        """Test removing user role."""
        with (
            patch.object(user_service, "_make_request", new_callable=AsyncMock) as mock_request,
            patch.object(user_service, "_handle_response", new_callable=AsyncMock) as mock_handle,
        ):
            mock_request.return_value = mock_response
            mock_handle.return_value = {"status": "success"}

            result = await user_service.remove_user_role("user-1", "role-1")

            mock_request.assert_called_once_with("DELETE", "users/user-1/roles/role-1")
            mock_handle.assert_called_once_with(mock_response)
            assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_role_management_error_handling(self, user_service):
        """Test role management error handling."""
        with (
            patch.object(user_service, "_make_request", new_callable=AsyncMock) as mock_request,
            patch.object(user_service, "_create_error_response") as mock_error,
        ):
            mock_request.side_effect = Exception("Network error")
            mock_error.return_value = {"status": "error", "message": "Error getting user roles: Network error"}

            result = await user_service.get_user_roles("user-1")

            mock_error.assert_called_once_with("Error getting user roles: Network error")
            assert result["status"] == "error"


class TestUserServiceTeams:
    """Test user team management functionality."""

    @pytest.mark.asyncio
    async def test_get_user_teams(self, user_service, mock_response):
        """Test getting user teams."""
        with (
            patch.object(user_service, "_make_request", new_callable=AsyncMock) as mock_request,
            patch.object(user_service, "_handle_response", new_callable=AsyncMock) as mock_handle,
        ):
            mock_request.return_value = mock_response
            mock_handle.return_value = {"status": "success", "data": []}

            result = await user_service.get_user_teams("user-1")

            expected_params = {"fields": "id,name,description"}
            mock_request.assert_called_once_with("GET", "users/user-1/teams", params=expected_params)
            mock_handle.assert_called_once_with(mock_response)
            assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_get_user_teams_custom_fields(self, user_service, mock_response):
        """Test getting user teams with custom fields."""
        with (
            patch.object(user_service, "_make_request", new_callable=AsyncMock) as mock_request,
            patch.object(user_service, "_handle_response", new_callable=AsyncMock) as mock_handle,
        ):
            mock_request.return_value = mock_response
            mock_handle.return_value = {"status": "success", "data": []}

            result = await user_service.get_user_teams("user-1", fields="id,name")

            expected_params = {"fields": "id,name"}
            mock_request.assert_called_once_with("GET", "users/user-1/teams", params=expected_params)
            assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_add_user_to_team(self, user_service, mock_response):
        """Test adding user to team."""
        with (
            patch.object(user_service, "_make_request", new_callable=AsyncMock) as mock_request,
            patch.object(user_service, "_handle_response", new_callable=AsyncMock) as mock_handle,
        ):
            mock_request.return_value = mock_response
            mock_handle.return_value = {"status": "success"}

            result = await user_service.add_user_to_team("user-1", "team-1")

            expected_data = {"id": "team-1"}
            mock_request.assert_called_once_with("POST", "users/user-1/teams", json_data=expected_data)
            mock_handle.assert_called_once_with(mock_response, success_codes=[200, 201])
            assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_remove_user_from_team(self, user_service, mock_response):
        """Test removing user from team."""
        with (
            patch.object(user_service, "_make_request", new_callable=AsyncMock) as mock_request,
            patch.object(user_service, "_handle_response", new_callable=AsyncMock) as mock_handle,
        ):
            mock_request.return_value = mock_response
            mock_handle.return_value = {"status": "success"}

            result = await user_service.remove_user_from_team("user-1", "team-1")

            mock_request.assert_called_once_with("DELETE", "users/user-1/teams/team-1")
            mock_handle.assert_called_once_with(mock_response)
            assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_team_management_error_handling(self, user_service):
        """Test team management error handling."""
        with (
            patch.object(user_service, "_make_request", new_callable=AsyncMock) as mock_request,
            patch.object(user_service, "_create_error_response") as mock_error,
        ):
            mock_request.side_effect = Exception("Network error")
            mock_error.return_value = {"status": "error", "message": "Error getting user teams: Network error"}

            result = await user_service.get_user_teams("user-1")

            mock_error.assert_called_once_with("Error getting user teams: Network error")
            assert result["status"] == "error"


class TestUserServicePasswordAndPermissions:
    """Test password and permission functionality."""

    @pytest.mark.asyncio
    async def test_change_user_password_basic(self, user_service, mock_response):
        """Test changing user password."""
        with (
            patch.object(user_service, "get_user", new_callable=AsyncMock) as mock_get_user,
            patch.object(user_service, "_make_request", new_callable=AsyncMock) as mock_request,
            patch.object(user_service, "_handle_response", new_callable=AsyncMock) as mock_handle,
        ):
            # Mock get_user to return user with ringId
            mock_get_user.return_value = {
                "status": "success",
                "data": {"id": "user-1", "login": "testuser", "ringId": "ring-123"},
            }
            mock_request.return_value = mock_response
            mock_handle.return_value = {"status": "success"}

            result = await user_service.change_user_password("user-1", "newpass123")

            mock_get_user.assert_called_once_with("user-1", fields="id,login,ringId")
            expected_data = {"password": "newpass123", "forceChangePassword": False}
            mock_request.assert_called_once_with("POST", "../hub/api/rest/users/ring-123", json_data=expected_data)
            mock_handle.assert_called_once_with(mock_response)
            assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_change_user_password_with_force(self, user_service, mock_response):
        """Test changing user password with force change."""
        with (
            patch.object(user_service, "get_user", new_callable=AsyncMock) as mock_get_user,
            patch.object(user_service, "_make_request", new_callable=AsyncMock) as mock_request,
            patch.object(user_service, "_handle_response", new_callable=AsyncMock) as mock_handle,
        ):
            # Mock get_user to return user with ringId
            mock_get_user.return_value = {
                "status": "success",
                "data": {"id": "user-1", "login": "testuser", "ringId": "ring-123"},
            }
            mock_request.return_value = mock_response
            mock_handle.return_value = {"status": "success"}

            result = await user_service.change_user_password("user-1", "newpass123", force_change=True)

            mock_get_user.assert_called_once_with("user-1", fields="id,login,ringId")
            expected_data = {"password": "newpass123", "forceChangePassword": True}
            mock_request.assert_called_once_with("POST", "../hub/api/rest/users/ring-123", json_data=expected_data)
            assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_change_user_password_error_handling(self, user_service):
        """Test change password error handling."""
        with (
            patch.object(user_service, "get_user", new_callable=AsyncMock) as mock_get_user,
            patch.object(user_service, "_create_error_response") as mock_error,
        ):
            mock_get_user.side_effect = Exception("Network error")
            mock_error.return_value = {"status": "error", "message": "Error changing user password: Network error"}

            result = await user_service.change_user_password("user-1", "newpass123")

            mock_error.assert_called_once_with("Error changing user password: Network error")
            assert result["status"] == "error"

    @pytest.mark.asyncio
    async def test_get_user_permissions_basic(self, user_service, mock_response):
        """Test getting user permissions."""
        with (
            patch.object(user_service, "_make_request", new_callable=AsyncMock) as mock_request,
            patch.object(user_service, "_handle_response", new_callable=AsyncMock) as mock_handle,
        ):
            mock_request.return_value = mock_response
            mock_handle.return_value = {"status": "success", "data": []}

            result = await user_service.get_user_permissions("user-1")

            mock_request.assert_called_once_with("GET", "users/user-1/permissions", params={})
            mock_handle.assert_called_once_with(mock_response)
            assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_get_user_permissions_with_project(self, user_service, mock_response):
        """Test getting user permissions for specific project."""
        with (
            patch.object(user_service, "_make_request", new_callable=AsyncMock) as mock_request,
            patch.object(user_service, "_handle_response", new_callable=AsyncMock) as mock_handle,
        ):
            mock_request.return_value = mock_response
            mock_handle.return_value = {"status": "success", "data": []}

            result = await user_service.get_user_permissions("user-1", project_id="proj-1")

            expected_params = {"project": "proj-1"}
            mock_request.assert_called_once_with("GET", "users/user-1/permissions", params=expected_params)
            assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_get_user_permissions_error_handling(self, user_service):
        """Test get permissions error handling."""
        with (
            patch.object(user_service, "_make_request", new_callable=AsyncMock) as mock_request,
            patch.object(user_service, "_create_error_response") as mock_error,
        ):
            mock_request.side_effect = Exception("Network error")
            mock_error.return_value = {"status": "error", "message": "Error getting user permissions: Network error"}

            result = await user_service.get_user_permissions("user-1")

            mock_error.assert_called_once_with("Error getting user permissions: Network error")
            assert result["status"] == "error"
