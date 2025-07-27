"""Tests for user commands."""

from unittest.mock import MagicMock, patch

import click
import pytest
from click.testing import CliRunner

from youtrack_cli.commands.users import (
    add_help_verbose_option,
    create_user,
    list_users,
    permissions,
    show_users_verbose_help,
    users,
    users_groups,
    users_roles,
    users_teams,
    users_update,
)


@pytest.fixture
def runner():
    """Create a Click test runner."""
    return CliRunner()


@pytest.fixture
def mock_ctx():
    """Create a mock Click context."""
    ctx = MagicMock()
    ctx.obj = {"config": {"base_url": "http://localhost:8080"}}
    return ctx


@pytest.fixture
def sample_users():
    """Sample user data."""
    return [
        {
            "id": "user-1",
            "login": "testuser",
            "fullName": "Test User",
            "email": "test@example.com",
            "banned": False,
            "online": True,
            "guest": False,
        },
        {
            "id": "user-2",
            "login": "admin",
            "fullName": "Admin User",
            "email": "admin@example.com",
            "banned": False,
            "online": False,
            "guest": False,
        },
    ]


class TestUsersHelpVerbose:
    """Test verbose help functionality."""

    def test_show_users_verbose_help(self, runner):
        """Test verbose help display."""
        with patch("rich.console.Console") as mock_console_class:
            mock_console = MagicMock()
            mock_console_class.return_value = mock_console

            ctx = MagicMock()
            show_users_verbose_help(ctx)

            # Verify console was created and print was called multiple times
            mock_console_class.assert_called_once()
            assert mock_console.print.call_count >= 10  # Should print many help sections

    def test_add_help_verbose_option_decorator(self):
        """Test the help-verbose option decorator."""

        @add_help_verbose_option
        def dummy_command():
            pass

        # Check that the option was added
        assert hasattr(dummy_command, "__click_params__")
        params = dummy_command.__click_params__
        assert len(params) > 0
        help_param = params[0]
        assert help_param.name == "help_verbose"


class TestUsersGroup:
    """Test the main users command group."""

    def test_users_group_exists(self):
        """Test that users group is properly configured."""
        assert isinstance(users, click.Group)
        assert users.name == "users"

    def test_users_group_has_commands(self):
        """Test that users group has expected commands."""
        command_names = list(users.commands.keys())
        expected_commands = ["list", "create", "update", "permissions", "groups", "roles", "teams"]

        for cmd in expected_commands:
            assert cmd in command_names


class TestListUsersCommand:
    """Test the list users command."""

    @patch("youtrack_cli.managers.users.UserManager")
    @patch("youtrack_cli.auth.AuthManager")
    @patch("youtrack_cli.console.get_console")
    @patch("asyncio.run")
    def test_list_users_success_table_format(
        self, mock_asyncio, mock_console, mock_auth, mock_manager_class, runner, sample_users
    ):
        """Test successful user listing in table format."""
        # Setup mocks
        mock_console_instance = MagicMock()
        mock_console.return_value = mock_console_instance

        mock_manager = MagicMock()
        mock_manager_class.return_value = mock_manager

        mock_asyncio.return_value = {"status": "success", "data": sample_users, "count": 2}

        # Run command
        result = runner.invoke(list_users, ["--format", "table"], obj={"config": {}})

        # Assertions
        assert result.exit_code == 0
        mock_manager.list_users.assert_called_once()
        mock_manager.display_users_table.assert_called_once_with(sample_users)
        assert "👥 Fetching users..." in result.output

    @patch("youtrack_cli.managers.users.UserManager")
    @patch("youtrack_cli.auth.AuthManager")
    @patch("youtrack_cli.console.get_console")
    @patch("asyncio.run")
    def test_list_users_success_json_format(
        self, mock_asyncio, mock_console, mock_auth, mock_manager_class, runner, sample_users
    ):
        """Test successful user listing in JSON format."""
        # Setup mocks
        mock_console_instance = MagicMock()
        mock_console.return_value = mock_console_instance

        mock_manager = MagicMock()
        mock_manager_class.return_value = mock_manager

        mock_asyncio.return_value = {"status": "success", "data": sample_users, "count": 2}

        # Run command
        result = runner.invoke(list_users, ["--format", "json"], obj={"config": {}})

        # Assertions
        assert result.exit_code == 0
        mock_manager.list_users.assert_called_once()
        # Should print JSON instead of using display_users_table
        mock_manager.display_users_table.assert_not_called()

    @patch("youtrack_cli.managers.users.UserManager")
    @patch("youtrack_cli.auth.AuthManager")
    @patch("youtrack_cli.console.get_console")
    @patch("asyncio.run")
    def test_list_users_with_pagination_options(
        self, mock_asyncio, mock_console, mock_auth, mock_manager_class, runner
    ):
        """Test user listing with pagination options."""
        # Setup mocks
        mock_console_instance = MagicMock()
        mock_console.return_value = mock_console_instance

        mock_manager = MagicMock()
        mock_manager_class.return_value = mock_manager

        mock_asyncio.return_value = {
            "status": "success",
            "data": [],
            "count": 0,
            "pagination": {"has_after": True, "has_before": False, "after_cursor": "cursor123", "before_cursor": None},
        }

        # Run command with pagination options
        result = runner.invoke(
            list_users, ["--all", "--page-size", "50", "--after-cursor", "abc123"], obj={"config": {}}
        )

        # Assertions
        assert result.exit_code == 0
        # Verify pagination was enabled (use_pagination=True)
        call_args = mock_manager.list_users.call_args
        assert call_args[1]["use_pagination"]
        assert call_args[1]["page_size"] == 50
        assert call_args[1]["after_cursor"] == "abc123"

    @patch("youtrack_cli.managers.users.UserManager")
    @patch("youtrack_cli.auth.AuthManager")
    @patch("youtrack_cli.console.get_console")
    @patch("asyncio.run")
    def test_list_users_error(self, mock_asyncio, mock_console, mock_auth, mock_manager_class, runner):
        """Test user listing error handling."""
        # Setup mocks
        mock_console_instance = MagicMock()
        mock_console.return_value = mock_console_instance

        mock_manager = MagicMock()
        mock_manager_class.return_value = mock_manager

        mock_asyncio.return_value = {"status": "error", "message": "API error"}

        # Run command
        result = runner.invoke(list_users, [], obj={"config": {}})

        # Assertions
        assert result.exit_code == 1
        assert "❌ API error" in result.output

    @patch("youtrack_cli.managers.users.UserManager")
    @patch("youtrack_cli.auth.AuthManager")
    @patch("youtrack_cli.console.get_console")
    @patch("asyncio.run")
    def test_list_users_exception(self, mock_asyncio, mock_console, mock_auth, mock_manager_class, runner):
        """Test user listing exception handling."""
        # Setup mocks
        mock_console_instance = MagicMock()
        mock_console.return_value = mock_console_instance

        mock_manager = MagicMock()
        mock_manager_class.return_value = mock_manager

        mock_asyncio.side_effect = Exception("Network error")

        # Run command
        result = runner.invoke(list_users, [], obj={"config": {}})

        # Assertions
        assert result.exit_code == 1
        assert "❌ Error listing users: Network error" in result.output


class TestCreateUserCommand:
    """Test the create user command."""

    @patch("youtrack_cli.managers.users.UserManager")
    @patch("youtrack_cli.auth.AuthManager")
    @patch("youtrack_cli.console.get_console")
    @patch("asyncio.run")
    @patch("rich.prompt.Prompt.ask")
    def test_create_user_success_with_prompt(
        self, mock_prompt, mock_asyncio, mock_console, mock_auth, mock_manager_class, runner
    ):
        """Test successful user creation with password prompt."""
        # Setup mocks
        mock_console_instance = MagicMock()
        mock_console.return_value = mock_console_instance

        mock_manager = MagicMock()
        mock_manager_class.return_value = mock_manager

        mock_prompt.return_value = "secret123"

        mock_asyncio.return_value = {
            "status": "success",
            "message": "User created successfully",
            "data": {"id": "user-1", "login": "testuser", "fullName": "Test User", "email": "test@example.com"},
        }

        # Run command
        result = runner.invoke(create_user, ["testuser", "Test User", "test@example.com"], obj={"config": {}})

        # Assertions
        assert result.exit_code == 0
        mock_prompt.assert_called_once_with("Enter password for new user", password=True)
        mock_manager.create_user.assert_called_once()

        # Check the output instead of console calls since Click captures output
        assert "✅ User created successfully" in result.output
        assert "User ID: user-1" in result.output

    @patch("youtrack_cli.managers.users.UserManager")
    @patch("youtrack_cli.auth.AuthManager")
    @patch("youtrack_cli.console.get_console")
    @patch("asyncio.run")
    def test_create_user_with_password_option(self, mock_asyncio, mock_console, mock_auth, mock_manager_class, runner):
        """Test user creation with password provided via option."""
        # Setup mocks
        mock_console_instance = MagicMock()
        mock_console.return_value = mock_console_instance

        mock_manager = MagicMock()
        mock_manager_class.return_value = mock_manager

        mock_asyncio.return_value = {
            "status": "success",
            "message": "User created successfully",
            "data": {"id": "user-1", "login": "testuser"},
        }

        # Run command
        result = runner.invoke(
            create_user, ["testuser", "Test User", "test@example.com", "--password", "secret123"], obj={"config": {}}
        )

        # Assertions
        assert result.exit_code == 0
        assert "⚠️  Warning: Password provided via command line may be visible in shell history" in result.output

    @patch("youtrack_cli.managers.users.UserManager")
    @patch("youtrack_cli.auth.AuthManager")
    @patch("youtrack_cli.console.get_console")
    @patch("asyncio.run")
    def test_create_user_with_banned_flag(self, mock_asyncio, mock_console, mock_auth, mock_manager_class, runner):
        """Test user creation with banned flag."""
        # Setup mocks
        mock_console_instance = MagicMock()
        mock_console.return_value = mock_console_instance

        mock_manager = MagicMock()
        mock_manager_class.return_value = mock_manager

        # Mock both create_user and ban_user responses
        create_response = {
            "status": "success",
            "message": "User created successfully",
            "data": {"id": "user-1", "login": "testuser"},
        }
        ban_response = {"status": "success", "message": "User banned successfully"}

        mock_asyncio.side_effect = [create_response, ban_response]

        # Run command
        result = runner.invoke(
            create_user,
            ["testuser", "Test User", "test@example.com", "--password", "secret123", "--banned"],
            obj={"config": {}},
        )

        # Assertions
        assert result.exit_code == 0
        assert mock_asyncio.call_count == 2  # create_user and ban_user
        mock_manager.ban_user.assert_called_once_with("testuser")

    @patch("youtrack_cli.managers.users.UserManager")
    @patch("youtrack_cli.auth.AuthManager")
    @patch("youtrack_cli.console.get_console")
    @patch("asyncio.run")
    @patch("rich.prompt.Prompt.ask")
    def test_create_user_error(self, mock_prompt, mock_asyncio, mock_console, mock_auth, mock_manager_class, runner):
        """Test user creation error handling."""
        # Setup mocks
        mock_console_instance = MagicMock()
        mock_console.return_value = mock_console_instance

        mock_manager = MagicMock()
        mock_manager_class.return_value = mock_manager

        mock_prompt.return_value = "secret123"

        mock_asyncio.return_value = {"status": "error", "message": "User already exists"}

        # Run command
        result = runner.invoke(create_user, ["testuser", "Test User", "test@example.com"], obj={"config": {}})

        # Assertions
        assert result.exit_code == 1
        assert "❌ User already exists" in result.output


class TestUpdateUserCommand:
    """Test the update user command."""

    @patch("youtrack_cli.managers.users.UserManager")
    @patch("youtrack_cli.auth.AuthManager")
    @patch("youtrack_cli.console.get_console")
    @patch("asyncio.run")
    def test_update_user_success(self, mock_asyncio, mock_console, mock_auth, mock_manager_class, runner):
        """Test successful user update."""
        # Setup mocks
        mock_console_instance = MagicMock()
        mock_console.return_value = mock_console_instance

        mock_manager = MagicMock()
        mock_manager_class.return_value = mock_manager

        mock_asyncio.return_value = {
            "status": "success",
            "message": "User updated successfully",
            "data": {"login": "testuser", "fullName": "New Name", "email": "new@example.com"},
        }

        # Run command
        result = runner.invoke(
            users_update, ["testuser", "--full-name", "New Name", "--email", "new@example.com"], obj={"config": {}}
        )

        # Assertions
        assert result.exit_code == 0
        mock_manager.update_user.assert_called_once()
        assert "✅ User updated successfully" in result.output

    @patch("youtrack_cli.managers.users.UserManager")
    @patch("youtrack_cli.auth.AuthManager")
    @patch("youtrack_cli.console.get_console")
    @patch("asyncio.run")
    def test_update_user_show_details(self, mock_asyncio, mock_console, mock_auth, mock_manager_class, runner):
        """Test user update with show details flag."""
        # Setup mocks
        mock_console_instance = MagicMock()
        mock_console.return_value = mock_console_instance

        mock_manager = MagicMock()
        mock_manager_class.return_value = mock_manager

        mock_asyncio.return_value = {"status": "success", "data": {"login": "testuser", "fullName": "Test User"}}

        # Run command
        result = runner.invoke(users_update, ["testuser", "--show-details"], obj={"config": {}})

        # Assertions
        assert result.exit_code == 0
        mock_manager.get_user.assert_called_once_with("testuser")
        mock_manager.display_user_details.assert_called_once()

    @patch("youtrack_cli.managers.users.UserManager")
    @patch("youtrack_cli.auth.AuthManager")
    @patch("youtrack_cli.console.get_console")
    def test_update_user_no_options(self, mock_console, mock_auth, mock_manager_class, runner):
        """Test user update with no options provided."""
        # Setup mocks
        mock_console_instance = MagicMock()
        mock_console.return_value = mock_console_instance

        mock_manager = MagicMock()
        mock_manager_class.return_value = mock_manager

        # Run command
        result = runner.invoke(users_update, ["testuser"], obj={"config": {}})

        # Assertions
        assert result.exit_code == 0
        assert "❌ No updates specified." in result.output
        # Should not call update_user
        mock_manager.update_user.assert_not_called()


class TestPermissionsCommand:
    """Test the permissions command."""

    @patch("youtrack_cli.managers.users.UserManager")
    @patch("youtrack_cli.auth.AuthManager")
    @patch("youtrack_cli.console.get_console")
    @patch("asyncio.run")
    def test_permissions_add_to_group(self, mock_asyncio, mock_console, mock_auth, mock_manager_class, runner):
        """Test permissions add to group."""
        # Setup mocks
        mock_console_instance = MagicMock()
        mock_console.return_value = mock_console_instance

        mock_manager = MagicMock()
        mock_manager_class.return_value = mock_manager

        mock_asyncio.return_value = {"status": "success", "message": "User added to group successfully"}

        # Run command
        result = runner.invoke(
            permissions, ["testuser", "--action", "add_to_group", "--group-id", "developers"], obj={"config": {}}
        )

        # Assertions
        assert result.exit_code == 0
        mock_manager.manage_user_permissions.assert_called_once_with(
            user_id="testuser", action="add_to_group", group_id="developers"
        )
        assert "✅ User added to group successfully" in result.output

    @patch("youtrack_cli.managers.users.UserManager")
    @patch("youtrack_cli.auth.AuthManager")
    @patch("youtrack_cli.console.get_console")
    @patch("asyncio.run")
    def test_permissions_error(self, mock_asyncio, mock_console, mock_auth, mock_manager_class, runner):
        """Test permissions command error handling."""
        # Setup mocks
        mock_console_instance = MagicMock()
        mock_console.return_value = mock_console_instance

        mock_manager = MagicMock()
        mock_manager_class.return_value = mock_manager

        mock_asyncio.return_value = {"status": "error", "message": "Permission denied"}

        # Run command
        result = runner.invoke(
            permissions, ["testuser", "--action", "add_to_group", "--group-id", "developers"], obj={"config": {}}
        )

        # Assertions
        assert result.exit_code == 1
        assert "❌ Permission denied" in result.output


class TestGroupsCommand:
    """Test the groups command."""

    @patch("youtrack_cli.managers.users.UserManager")
    @patch("youtrack_cli.auth.AuthManager")
    @patch("youtrack_cli.console.get_console")
    @patch("asyncio.run")
    def test_users_groups_table_format(self, mock_asyncio, mock_console, mock_auth, mock_manager_class, runner):
        """Test users groups command in table format."""
        # Setup mocks
        mock_console_instance = MagicMock()
        mock_console.return_value = mock_console_instance

        mock_manager = MagicMock()
        mock_manager_class.return_value = mock_manager

        groups_data = [
            {"name": "Developers", "description": "Dev group"},
            {"name": "Admins", "description": "Admin group"},
        ]

        mock_asyncio.return_value = {"status": "success", "data": groups_data}

        # Run command
        result = runner.invoke(users_groups, ["testuser"], obj={"config": {}})

        # Assertions
        assert result.exit_code == 0
        mock_manager.get_user_groups.assert_called_once_with("testuser")
        mock_manager.display_user_groups.assert_called_once_with(groups_data, "testuser")

    @patch("youtrack_cli.managers.users.UserManager")
    @patch("youtrack_cli.auth.AuthManager")
    @patch("youtrack_cli.console.get_console")
    @patch("asyncio.run")
    def test_users_groups_json_format(self, mock_asyncio, mock_console, mock_auth, mock_manager_class, runner):
        """Test users groups command in JSON format."""
        # Setup mocks
        mock_console_instance = MagicMock()
        mock_console.return_value = mock_console_instance

        mock_manager = MagicMock()
        mock_manager_class.return_value = mock_manager

        groups_data = [{"name": "Developers"}]

        mock_asyncio.return_value = {"status": "success", "data": groups_data}

        # Run command
        result = runner.invoke(users_groups, ["testuser", "--format", "json"], obj={"config": {}})

        # Assertions
        assert result.exit_code == 0
        mock_manager.display_user_groups.assert_not_called()  # Should not call table display
        # Should print JSON instead


class TestRolesCommand:
    """Test the roles command."""

    @patch("youtrack_cli.managers.users.UserManager")
    @patch("youtrack_cli.auth.AuthManager")
    @patch("youtrack_cli.console.get_console")
    @patch("asyncio.run")
    def test_users_roles_success(self, mock_asyncio, mock_console, mock_auth, mock_manager_class, runner):
        """Test users roles command success."""
        # Setup mocks
        mock_console_instance = MagicMock()
        mock_console.return_value = mock_console_instance

        mock_manager = MagicMock()
        mock_manager_class.return_value = mock_manager

        roles_data = [
            {"name": "Admin", "description": "Administrator role"},
            {"name": "Developer", "description": "Developer role"},
        ]

        mock_asyncio.return_value = {"status": "success", "data": roles_data}

        # Run command
        result = runner.invoke(users_roles, ["testuser"], obj={"config": {}})

        # Assertions
        assert result.exit_code == 0
        mock_manager.get_user_roles.assert_called_once_with("testuser")
        mock_manager.display_user_roles.assert_called_once_with(roles_data, "testuser")

    @patch("youtrack_cli.managers.users.UserManager")
    @patch("youtrack_cli.auth.AuthManager")
    @patch("youtrack_cli.console.get_console")
    @patch("asyncio.run")
    def test_users_roles_error(self, mock_asyncio, mock_console, mock_auth, mock_manager_class, runner):
        """Test users roles command error handling."""
        # Setup mocks
        mock_console_instance = MagicMock()
        mock_console.return_value = mock_console_instance

        mock_manager = MagicMock()
        mock_manager_class.return_value = mock_manager

        mock_asyncio.return_value = {"status": "error", "message": "User not found"}

        # Run command
        result = runner.invoke(users_roles, ["testuser"], obj={"config": {}})

        # Assertions
        assert result.exit_code == 1
        assert "❌ User not found" in result.output


class TestTeamsCommand:
    """Test the teams command."""

    @patch("youtrack_cli.managers.users.UserManager")
    @patch("youtrack_cli.auth.AuthManager")
    @patch("youtrack_cli.console.get_console")
    @patch("asyncio.run")
    def test_users_teams_success(self, mock_asyncio, mock_console, mock_auth, mock_manager_class, runner):
        """Test users teams command success."""
        # Setup mocks
        mock_console_instance = MagicMock()
        mock_console.return_value = mock_console_instance

        mock_manager = MagicMock()
        mock_manager_class.return_value = mock_manager

        teams_data = [
            {"name": "Development", "description": "Dev team"},
            {"name": "QA", "description": "Quality assurance team"},
        ]

        mock_asyncio.return_value = {"status": "success", "data": teams_data}

        # Run command
        result = runner.invoke(users_teams, ["testuser"], obj={"config": {}})

        # Assertions
        assert result.exit_code == 0
        mock_manager.get_user_teams.assert_called_once_with("testuser")
        mock_manager.display_user_teams.assert_called_once_with(teams_data, "testuser")

    @patch("youtrack_cli.managers.users.UserManager")
    @patch("youtrack_cli.auth.AuthManager")
    @patch("youtrack_cli.console.get_console")
    @patch("asyncio.run")
    def test_users_teams_exception(self, mock_asyncio, mock_console, mock_auth, mock_manager_class, runner):
        """Test users teams command exception handling."""
        # Setup mocks
        mock_console_instance = MagicMock()
        mock_console.return_value = mock_console_instance

        mock_manager = MagicMock()
        mock_manager_class.return_value = mock_manager

        mock_asyncio.side_effect = Exception("Network timeout")

        # Run command
        result = runner.invoke(users_teams, ["testuser"], obj={"config": {}})

        # Assertions
        assert result.exit_code == 1
        assert "❌ Error getting user teams: Network timeout" in result.output
