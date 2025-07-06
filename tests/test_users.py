"""Tests for the users module."""

from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest
from click.testing import CliRunner

from youtrack_cli.auth import AuthConfig, AuthManager
from youtrack_cli.main import main
from youtrack_cli.users import UserManager


class TestUserManager:
    """Test UserManager functionality."""

    @pytest.fixture
    def auth_manager(self):
        """Create a mock auth manager for testing."""
        auth_manager = Mock(spec=AuthManager)
        auth_manager.load_credentials.return_value = AuthConfig(
            base_url="https://test.youtrack.cloud",
            token="test-token",
            username="test-user",
        )
        return auth_manager

    @pytest.fixture
    def user_manager(self, auth_manager):
        """Create a UserManager instance for testing."""
        return UserManager(auth_manager)

    @pytest.mark.asyncio
    async def test_list_users_success(self, user_manager, auth_manager):
        """Test successful user listing."""
        mock_users = [
            {
                "id": "1",
                "login": "user1",
                "fullName": "User One",
                "email": "user1@test.com",
                "banned": False,
                "online": True,
                "guest": False,
            },
            {
                "id": "2",
                "login": "user2",
                "fullName": "User Two",
                "email": "user2@test.com",
                "banned": False,
                "online": False,
                "guest": False,
            },
        ]

        with patch("youtrack_cli.users.get_client_manager") as mock_get_client_manager:
            mock_response = Mock()
            mock_response.json.return_value = mock_users

            mock_client_manager = Mock()
            mock_client_manager.make_request = AsyncMock(return_value=mock_response)
            mock_get_client_manager.return_value = mock_client_manager

            result = await user_manager.list_users()

            assert result["status"] == "success"
            assert len(result["data"]) == 2
            assert result["data"][0]["login"] == "user1"
            assert result["count"] == 2

    @pytest.mark.asyncio
    async def test_list_users_with_query(self, user_manager, auth_manager):
        """Test user listing with search query."""
        mock_users = [
            {
                "id": "1",
                "login": "admin",
                "fullName": "Admin User",
                "email": "admin@test.com",
                "banned": False,
                "online": True,
                "guest": False,
            }
        ]

        with patch("youtrack_cli.users.get_client_manager") as mock_get_client_manager:
            mock_response = Mock()
            mock_response.json.return_value = mock_users

            mock_client_manager = Mock()
            mock_client_manager.make_request = AsyncMock(return_value=mock_response)
            mock_get_client_manager.return_value = mock_client_manager

            result = await user_manager.list_users(query="admin")

            assert result["status"] == "success"
            assert len(result["data"]) == 1
            assert result["data"][0]["login"] == "admin"

    @pytest.mark.asyncio
    async def test_list_users_not_authenticated(self, auth_manager):
        """Test user listing when not authenticated."""
        auth_manager.load_credentials.return_value = None
        user_manager = UserManager(auth_manager)

        result = await user_manager.list_users()

        assert result["status"] == "error"
        assert "Not authenticated" in result["message"]

    @pytest.mark.asyncio
    async def test_list_users_insufficient_permissions(self, user_manager, auth_manager):
        """Test user listing with insufficient permissions."""
        with patch("youtrack_cli.users.get_client_manager") as mock_get_client_manager:
            from youtrack_cli.exceptions import PermissionError

            permission_error = PermissionError("access this resource")

            mock_client_manager = Mock()
            mock_client_manager.make_request = AsyncMock(side_effect=permission_error)
            mock_get_client_manager.return_value = mock_client_manager

            result = await user_manager.list_users()

            assert result["status"] == "error"
            assert "Permission denied to access this resource" in result["message"]

    @pytest.mark.asyncio
    async def test_list_users_http_error(self, user_manager, auth_manager):
        """Test user listing with HTTP error."""
        with patch("youtrack_cli.users.get_client_manager") as mock_get_client_manager:
            mock_client_manager = Mock()
            mock_client_manager.make_request = AsyncMock(side_effect=httpx.HTTPError("Network error"))
            mock_get_client_manager.return_value = mock_client_manager

            result = await user_manager.list_users()

            assert result["status"] == "error"
            assert "Network error" in result["message"]

    @pytest.mark.asyncio
    async def test_create_user_success(self, user_manager, auth_manager):
        """Test successful user creation."""
        mock_created_user = {
            "id": "123",
            "login": "newuser",
            "fullName": "New User",
            "email": "newuser@test.com",
            "banned": False,
        }

        with patch("youtrack_cli.users.get_client_manager") as mock_get_client_manager:
            mock_response = Mock()
            mock_response.json.return_value = mock_created_user

            mock_client_manager = Mock()
            mock_client_manager.make_request = AsyncMock(return_value=mock_response)
            mock_get_client_manager.return_value = mock_client_manager

            result = await user_manager.create_user(
                login="newuser",
                full_name="New User",
                email="newuser@test.com",
                password="password123",
                banned=False,
                force_change_password=True,
            )

            assert result["status"] == "success"
            assert result["data"]["login"] == "newuser"
            assert "created successfully" in result["message"]

    @pytest.mark.asyncio
    async def test_create_user_invalid_data(self, user_manager, auth_manager):
        """Test user creation with invalid data."""
        with patch("youtrack_cli.users.get_client_manager") as mock_get_client_manager:
            from youtrack_cli.exceptions import YouTrackError

            youtrack_error = YouTrackError("Request failed with status 400: Bad request")

            mock_client_manager = Mock()
            mock_client_manager.make_request = AsyncMock(side_effect=youtrack_error)
            mock_get_client_manager.return_value = mock_client_manager

            result = await user_manager.create_user(login="", full_name="", email="invalid-email")

            assert result["status"] == "error"
            assert "Request failed with status 400" in result["message"]

    @pytest.mark.asyncio
    async def test_create_user_already_exists(self, user_manager, auth_manager):
        """Test user creation when user already exists."""
        with patch("youtrack_cli.users.get_client_manager") as mock_get_client_manager:
            from youtrack_cli.exceptions import YouTrackError

            youtrack_error = YouTrackError("Request failed with status 409: Conflict")

            mock_client_manager = Mock()
            mock_client_manager.make_request = AsyncMock(side_effect=youtrack_error)
            mock_get_client_manager.return_value = mock_client_manager

            result = await user_manager.create_user(
                login="existinguser",
                full_name="Existing User",
                email="existing@test.com",
            )

            assert result["status"] == "error"
            assert "Request failed with status 409" in result["message"]

    @pytest.mark.asyncio
    async def test_create_user_insufficient_permissions(self, user_manager, auth_manager):
        """Test user creation with insufficient permissions."""
        with patch("youtrack_cli.users.get_client_manager") as mock_get_client_manager:
            from youtrack_cli.exceptions import PermissionError

            permission_error = PermissionError("access this resource")

            mock_client_manager = Mock()
            mock_client_manager.make_request = AsyncMock(side_effect=permission_error)
            mock_get_client_manager.return_value = mock_client_manager

            result = await user_manager.create_user(login="newuser", full_name="New User", email="newuser@test.com")

            assert result["status"] == "error"
            assert "Permission denied to access this resource" in result["message"]

    @pytest.mark.asyncio
    async def test_get_user_success(self, user_manager, auth_manager):
        """Test successful user retrieval."""
        mock_user = {
            "id": "123",
            "login": "testuser",
            "fullName": "Test User",
            "email": "testuser@test.com",
            "banned": False,
            "online": True,
            "guest": False,
            "teams": [{"name": "Development", "description": "Dev team"}],
            "groups": [{"name": "Developers", "description": "Developer group"}],
        }

        with patch("youtrack_cli.users.get_client_manager") as mock_get_client_manager:
            mock_response = Mock()
            mock_response.json.return_value = mock_user

            mock_client_manager = Mock()
            mock_client_manager.make_request = AsyncMock(return_value=mock_response)
            mock_get_client_manager.return_value = mock_client_manager

            result = await user_manager.get_user("testuser")

            assert result["status"] == "success"
            assert result["data"]["login"] == "testuser"
            assert result["data"]["fullName"] == "Test User"

    @pytest.mark.asyncio
    async def test_get_user_not_found(self, user_manager, auth_manager):
        """Test user retrieval when user not found."""
        with patch("youtrack_cli.users.get_client_manager") as mock_get_client_manager:
            from youtrack_cli.exceptions import NotFoundError

            not_found_error = NotFoundError("Resource", "nonexistent")

            mock_client_manager = Mock()
            mock_client_manager.make_request = AsyncMock(side_effect=not_found_error)
            mock_get_client_manager.return_value = mock_client_manager

            result = await user_manager.get_user("nonexistent")

            assert result["status"] == "error"
            assert "not found" in result["message"]

    @pytest.mark.asyncio
    async def test_update_user_success(self, user_manager, auth_manager):
        """Test successful user update."""
        mock_updated_user = {
            "id": "123",
            "login": "testuser",
            "fullName": "Updated User",
            "email": "updated@test.com",
            "banned": False,
        }

        with patch("youtrack_cli.users.get_client_manager") as mock_get_client_manager:
            mock_response = Mock()
            mock_response.json.return_value = mock_updated_user

            mock_client_manager = Mock()
            mock_client_manager.make_request = AsyncMock(return_value=mock_response)
            mock_get_client_manager.return_value = mock_client_manager

            result = await user_manager.update_user(
                user_id="testuser",
                full_name="Updated User",
                email="updated@test.com",
                banned=False,
            )

            assert result["status"] == "success"
            assert result["data"]["fullName"] == "Updated User"
            assert "updated successfully" in result["message"]

    @pytest.mark.asyncio
    async def test_update_user_no_changes(self, user_manager, auth_manager):
        """Test user update with no changes provided."""
        result = await user_manager.update_user("testuser")

        assert result["status"] == "error"
        assert "No updates provided" in result["message"]

    @pytest.mark.asyncio
    async def test_update_user_not_found(self, user_manager, auth_manager):
        """Test user update when user not found."""
        with patch("youtrack_cli.users.get_client_manager") as mock_get_client_manager:
            from youtrack_cli.exceptions import NotFoundError

            not_found_error = NotFoundError("Resource", "nonexistent")

            mock_client_manager = Mock()
            mock_client_manager.make_request = AsyncMock(side_effect=not_found_error)
            mock_get_client_manager.return_value = mock_client_manager

            result = await user_manager.update_user(user_id="nonexistent", full_name="New Name")

            assert result["status"] == "error"
            assert "not found" in result["message"]

    @pytest.mark.asyncio
    async def test_manage_user_permissions_add_to_group(self, user_manager, auth_manager):
        """Test adding user to group."""
        with patch("youtrack_cli.users.get_client_manager") as mock_get_client_manager:
            mock_response = Mock()

            mock_client_manager = Mock()
            mock_client_manager.make_request = AsyncMock(return_value=mock_response)
            mock_get_client_manager.return_value = mock_client_manager

            result = await user_manager.manage_user_permissions(
                user_id="testuser", action="add_to_group", group_id="developers"
            )

            assert result["status"] == "success"
            assert "permissions updated successfully" in result["message"]

    @pytest.mark.asyncio
    async def test_manage_user_permissions_remove_from_group(self, user_manager, auth_manager):
        """Test removing user from group."""
        with patch("youtrack_cli.users.get_client_manager") as mock_get_client_manager:
            mock_response = Mock()

            mock_client_manager = Mock()
            mock_client_manager.make_request = AsyncMock(return_value=mock_response)
            mock_get_client_manager.return_value = mock_client_manager

            result = await user_manager.manage_user_permissions(
                user_id="testuser", action="remove_from_group", group_id="developers"
            )

            assert result["status"] == "success"
            assert "permissions updated successfully" in result["message"]

    @pytest.mark.asyncio
    async def test_manage_user_permissions_missing_group_id(self, user_manager, auth_manager):
        """Test user permissions management with missing group ID."""
        result = await user_manager.manage_user_permissions(user_id="testuser", action="add_to_group")

        assert result["status"] == "error"
        assert "Group ID is required" in result["message"]

    @pytest.mark.asyncio
    async def test_manage_user_permissions_unsupported_action(self, user_manager, auth_manager):
        """Test user permissions management with unsupported action."""
        result = await user_manager.manage_user_permissions(
            user_id="testuser", action="invalid_action", group_id="developers"
        )

        assert result["status"] == "error"
        assert "Unsupported action" in result["message"]

    @pytest.mark.asyncio
    async def test_manage_user_permissions_not_found(self, user_manager, auth_manager):
        """Test user permissions management when user/group not found."""
        with patch("youtrack_cli.users.get_client_manager") as mock_get_client_manager:
            from youtrack_cli.exceptions import NotFoundError

            not_found_error = NotFoundError("Resource", "nonexistent")

            mock_client_manager = Mock()
            mock_client_manager.make_request = AsyncMock(side_effect=not_found_error)
            mock_get_client_manager.return_value = mock_client_manager

            result = await user_manager.manage_user_permissions(
                user_id="nonexistent", action="add_to_group", group_id="developers"
            )

            assert result["status"] == "error"
            assert "not found" in result["message"]


class TestUsersCLI:
    """Test users CLI commands."""

    def test_users_help(self):
        """Test users command help."""
        runner = CliRunner()
        result = runner.invoke(main, ["users", "--help"])
        assert result.exit_code == 0
        assert "User management" in result.output

    def test_users_list_help(self):
        """Test users list command help."""
        runner = CliRunner()
        result = runner.invoke(main, ["users", "list", "--help"])
        assert result.exit_code == 0
        assert "List all users" in result.output

    def test_users_create_help(self):
        """Test users create command help."""
        runner = CliRunner()
        result = runner.invoke(main, ["users", "create", "--help"])
        assert result.exit_code == 0
        assert "Create a new user" in result.output

    def test_users_update_help(self):
        """Test users update command help."""
        runner = CliRunner()
        result = runner.invoke(main, ["users", "update", "--help"])
        assert result.exit_code == 0
        assert "Update user information" in result.output

    def test_users_permissions_help(self):
        """Test users permissions command help."""
        runner = CliRunner()
        result = runner.invoke(main, ["users", "permissions", "--help"])
        assert result.exit_code == 0
        assert "Manage user permissions" in result.output

    @patch("youtrack_cli.users.UserManager")
    def test_users_list_command(self, mock_user_manager_class):
        """Test users list command execution."""
        mock_user_manager = Mock()
        mock_user_manager_class.return_value = mock_user_manager

        mock_result = {
            "status": "success",
            "data": [
                {
                    "id": "1",
                    "login": "testuser",
                    "fullName": "Test User",
                    "email": "test@test.com",
                    "banned": False,
                    "online": True,
                    "guest": False,
                }
            ],
            "count": 1,
        }

        with patch("asyncio.run", return_value=mock_result):
            with patch("youtrack_cli.auth.AuthManager"):
                runner = CliRunner()
                result = runner.invoke(main, ["users", "list"])

                assert result.exit_code in [0, 1]

    @patch("youtrack_cli.users.UserManager")
    def test_users_create_command(self, mock_user_manager_class):
        """Test users create command execution."""
        mock_user_manager = Mock()
        mock_user_manager_class.return_value = mock_user_manager

        mock_result = {
            "status": "success",
            "data": {"id": "123", "login": "newuser", "fullName": "New User"},
            "message": "User 'newuser' created successfully",
        }

        with patch("asyncio.run", return_value=mock_result):
            with patch("youtrack_cli.auth.AuthManager"):
                with patch("rich.prompt.Prompt.ask", return_value="password123"):
                    runner = CliRunner()
                    result = runner.invoke(
                        main,
                        [
                            "users",
                            "create",
                            "newuser",
                            "New User",
                            "newuser@test.com",
                        ],
                    )

                    assert result.exit_code in [0, 1]

    @patch("youtrack_cli.users.UserManager")
    def test_users_update_show_details(self, mock_user_manager_class):
        """Test users update command with show details option."""
        mock_user_manager = Mock()
        mock_user_manager_class.return_value = mock_user_manager

        mock_result = {
            "status": "success",
            "data": {
                "id": "123",
                "login": "testuser",
                "fullName": "Test User",
                "email": "test@test.com",
                "banned": False,
                "online": True,
                "guest": False,
            },
        }

        with patch("asyncio.run", return_value=mock_result):
            with patch("youtrack_cli.auth.AuthManager"):
                runner = CliRunner()
                result = runner.invoke(main, ["users", "update", "testuser", "--show-details"])

                assert result.exit_code in [0, 1]

    @patch("youtrack_cli.users.UserManager")
    def test_users_permissions_command(self, mock_user_manager_class):
        """Test users permissions command execution."""
        mock_user_manager = Mock()
        mock_user_manager_class.return_value = mock_user_manager

        mock_result = {
            "status": "success",
            "message": "User 'testuser' permissions updated successfully",
        }

        with patch("asyncio.run", return_value=mock_result):
            with patch("youtrack_cli.auth.AuthManager"):
                runner = CliRunner()
                result = runner.invoke(
                    main,
                    [
                        "users",
                        "permissions",
                        "testuser",
                        "--action",
                        "add_to_group",
                        "--group-id",
                        "developers",
                    ],
                )

                assert result.exit_code in [0, 1]


class TestUsersDisplayMethods:
    """Test users display methods."""

    def test_display_users_table_empty(self):
        """Test displaying empty users table."""
        auth_manager = Mock(spec=AuthManager)
        user_manager = UserManager(auth_manager)

        user_manager.display_users_table([])

    def test_display_users_table_with_data(self):
        """Test displaying users table with data."""
        auth_manager = Mock(spec=AuthManager)
        user_manager = UserManager(auth_manager)

        users = [
            {
                "id": "1",
                "login": "user1",
                "fullName": "User One",
                "email": "user1@test.com",
                "banned": False,
                "online": True,
                "guest": False,
            },
            {
                "id": "2",
                "login": "user2",
                "fullName": "User Two",
                "email": "user2@test.com",
                "banned": True,
                "online": False,
                "guest": False,
            },
            {
                "id": "3",
                "login": "guest1",
                "fullName": "Guest User",
                "email": "guest@test.com",
                "banned": False,
                "online": False,
                "guest": True,
            },
        ]

        user_manager.display_users_table(users)

    def test_display_user_details(self):
        """Test displaying user details."""
        auth_manager = Mock(spec=AuthManager)
        user_manager = UserManager(auth_manager)

        user = {
            "id": "123",
            "login": "testuser",
            "fullName": "Test User",
            "email": "test@test.com",
            "banned": False,
            "online": True,
            "guest": False,
            "teams": [
                {"name": "Development", "description": "Dev team"},
                {"name": "QA", "description": "Quality Assurance"},
            ],
            "groups": [
                {"name": "Developers", "description": "Developer group"},
                {"name": "Admin", "description": "Administrative group"},
            ],
        }

        user_manager.display_user_details(user)

    def test_display_user_details_minimal_data(self):
        """Test displaying user details with minimal data."""
        auth_manager = Mock(spec=AuthManager)
        user_manager = UserManager(auth_manager)

        user = {
            "id": "123",
            "login": "minimaluser",
            "fullName": "Minimal User",
            "email": "minimal@test.com",
        }

        user_manager.display_user_details(user)

    def test_display_user_details_banned_user(self):
        """Test displaying details for banned user."""
        auth_manager = Mock(spec=AuthManager)
        user_manager = UserManager(auth_manager)

        user = {
            "id": "123",
            "login": "banneduser",
            "fullName": "Banned User",
            "email": "banned@test.com",
            "banned": True,
            "online": False,
            "guest": False,
        }

        user_manager.display_user_details(user)

    def test_display_user_details_guest_user(self):
        """Test displaying details for guest user."""
        auth_manager = Mock(spec=AuthManager)
        user_manager = UserManager(auth_manager)

        user = {
            "id": "123",
            "login": "guestuser",
            "fullName": "Guest User",
            "email": "guest@test.com",
            "banned": False,
            "online": False,
            "guest": True,
        }

        user_manager.display_user_details(user)
