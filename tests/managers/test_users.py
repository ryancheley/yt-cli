"""Tests for UserManager."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from youtrack_cli.auth import AuthManager
from youtrack_cli.managers.users import UserManager


@pytest.fixture
def auth_manager():
    """Create a mock auth manager."""
    mock_auth = MagicMock(spec=AuthManager)
    return mock_auth


@pytest.fixture
def user_manager(auth_manager):
    """Create a UserManager instance."""
    with (
        patch("youtrack_cli.managers.users.get_console") as mock_console,
        patch("youtrack_cli.managers.users.UserService"),
    ):
        manager = UserManager(auth_manager)
        manager.console = mock_console.return_value

        # Make the service methods async
        manager.user_service = MagicMock()

        # Set up async methods
        for method_name in [
            "list_users",
            "get_user",
            "create_user",
            "update_user",
            "delete_user",
            "ban_user",
            "unban_user",
            "get_user_groups",
            "add_user_to_group",
            "remove_user_from_group",
            "get_user_roles",
            "assign_user_role",
            "remove_user_role",
            "get_user_teams",
            "add_user_to_team",
            "remove_user_from_team",
            "change_user_password",
            "get_user_permissions",
        ]:
            setattr(manager.user_service, method_name, AsyncMock())

        return manager


@pytest.fixture
def sample_user():
    """Create sample user data."""
    return {
        "id": "user-1",
        "login": "testuser",
        "fullName": "Test User",
        "email": "test@example.com",
        "banned": False,
        "online": True,
        "guest": False,
        "teams": [
            {"name": "Development", "description": "Dev team"},
            {"name": "QA", "description": "Quality assurance"},
        ],
        "groups": [
            {"name": "Users", "description": "Regular users"},
            {"name": "Developers", "description": "Development group"},
        ],
    }


class TestUserManagerListUsers:
    """Test user listing functionality."""

    @pytest.mark.asyncio
    async def test_list_users_basic(self, user_manager, sample_user):
        """Test basic user listing."""
        user_manager.user_service.list_users.return_value = {"status": "success", "data": [sample_user]}

        result = await user_manager.list_users()

        user_manager.user_service.list_users.assert_called_once_with(fields=None, top=None, skip=0, query=None)
        assert result["status"] == "success"
        assert len(result["data"]) == 1

    @pytest.mark.asyncio
    async def test_list_users_with_pagination(self, user_manager, sample_user):
        """Test user listing with pagination enabled."""
        user_manager.user_service.list_users.return_value = {"status": "success", "data": [sample_user]}

        result = await user_manager.list_users(use_pagination=True, page_size=10)

        user_manager.user_service.list_users.assert_called_once_with(fields=None, top=10, skip=0, query=None)
        assert result["status"] == "success"
        assert "pagination" in result
        assert result["pagination"]["total_results"] == 1

    @pytest.mark.asyncio
    async def test_list_users_active_only_with_pagination(self, user_manager):
        """Test user listing with active_only filter and pagination."""
        users_data = [
            {"login": "user1", "banned": False},
            {"login": "user2", "banned": True},
            {"login": "user3", "banned": False},
        ]

        user_manager.user_service.list_users.return_value = {"status": "success", "data": users_data}

        result = await user_manager.list_users(active_only=True, use_pagination=True)

        assert result["status"] == "success"
        assert len(result["data"]) == 2  # Only non-banned users
        assert all(not user.get("banned", False) for user in result["data"])

    @pytest.mark.asyncio
    async def test_list_users_active_only_legacy(self, user_manager):
        """Test user listing with active_only filter in legacy mode."""
        users_data = [{"login": "user1", "banned": False}, {"login": "user2", "banned": True}]

        user_manager.user_service.list_users.return_value = {"status": "success", "data": users_data}

        result = await user_manager.list_users(active_only=True, top=10)

        assert result["status"] == "success"
        assert len(result["data"]) == 1  # Only non-banned users

    @pytest.mark.asyncio
    async def test_list_users_with_top_parameter(self, user_manager, sample_user):
        """Test user listing with legacy top parameter."""
        user_manager.user_service.list_users.return_value = {"status": "success", "data": [sample_user]}

        result = await user_manager.list_users(top=5)

        user_manager.user_service.list_users.assert_called_once_with(fields=None, top=5, skip=0, query=None)
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_list_users_service_error(self, user_manager):
        """Test user listing when service returns error."""
        user_manager.user_service.list_users.return_value = {"status": "error", "message": "API error"}

        result = await user_manager.list_users()

        assert result["status"] == "error"
        assert result["message"] == "API error"


class TestUserManagerGetUser:
    """Test user retrieval functionality."""

    @pytest.mark.asyncio
    async def test_get_user(self, user_manager, sample_user):
        """Test getting a user."""
        expected_result = {"status": "success", "data": sample_user}
        user_manager.user_service.get_user.return_value = expected_result

        result = await user_manager.get_user("testuser")

        user_manager.user_service.get_user.assert_called_once_with("testuser", None)
        assert result == expected_result

    @pytest.mark.asyncio
    async def test_get_user_with_fields(self, user_manager, sample_user):
        """Test getting a user with custom fields."""
        expected_result = {"status": "success", "data": sample_user}
        user_manager.user_service.get_user.return_value = expected_result

        result = await user_manager.get_user("testuser", fields="id,login,email")

        user_manager.user_service.get_user.assert_called_once_with("testuser", "id,login,email")
        assert result == expected_result


class TestUserManagerCreateUser:
    """Test user creation functionality."""

    @pytest.mark.asyncio
    async def test_create_user_success(self, user_manager):
        """Test successful user creation."""
        user_manager.user_service.create_user.return_value = {"status": "success", "data": {"id": "user-1"}}

        result = await user_manager.create_user(login="testuser", full_name="Test User", email="test@example.com")

        user_manager.user_service.create_user.assert_called_once_with(
            login="testuser",
            full_name="Test User",
            email="test@example.com",
            password=None,
            force_change_password=False,
        )
        assert result["status"] == "success"
        assert result["message"] == "User 'testuser' created successfully"

    @pytest.mark.asyncio
    async def test_create_user_with_password(self, user_manager):
        """Test user creation with password."""
        user_manager.user_service.create_user.return_value = {"status": "success", "data": {"id": "user-1"}}

        result = await user_manager.create_user(
            login="testuser",
            full_name="Test User",
            email="test@example.com",
            password="secret123",
            force_change_password=True,
        )

        user_manager.user_service.create_user.assert_called_once_with(
            login="testuser",
            full_name="Test User",
            email="test@example.com",
            password="secret123",
            force_change_password=True,
        )
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_create_user_empty_login(self, user_manager):
        """Test user creation with empty login."""
        result = await user_manager.create_user(login="", full_name="Test User", email="test@example.com")

        assert result["status"] == "error"
        assert result["message"] == "Login cannot be empty"
        user_manager.user_service.create_user.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_user_empty_full_name(self, user_manager):
        """Test user creation with empty full name."""
        result = await user_manager.create_user(login="testuser", full_name="   ", email="test@example.com")

        assert result["status"] == "error"
        assert result["message"] == "Full name cannot be empty"
        user_manager.user_service.create_user.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_user_invalid_email(self, user_manager):
        """Test user creation with invalid email."""
        result = await user_manager.create_user(login="testuser", full_name="Test User", email="invalid-email")

        assert result["status"] == "error"
        assert result["message"] == "Valid email address is required"
        user_manager.user_service.create_user.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_user_service_error(self, user_manager):
        """Test user creation when service returns error."""
        user_manager.user_service.create_user.return_value = {"status": "error", "message": "User already exists"}

        result = await user_manager.create_user(login="testuser", full_name="Test User", email="test@example.com")

        assert result["status"] == "error"
        assert result["message"] == "User already exists"


class TestUserManagerUpdateUser:
    """Test user update functionality."""

    @pytest.mark.asyncio
    async def test_update_user_success(self, user_manager):
        """Test successful user update."""
        user_manager.user_service.update_user.return_value = {"status": "success"}

        result = await user_manager.update_user("user-1", full_name="New Name", email="new@example.com")

        user_manager.user_service.update_user.assert_called_once_with(
            user_id="user-1",
            full_name="New Name",
            email="new@example.com",
            banned=None,
            password=None,
            force_change_password=None,
        )
        assert result["status"] == "success"
        assert result["message"] == "User 'user-1' updated successfully"

    @pytest.mark.asyncio
    async def test_update_user_invalid_email(self, user_manager):
        """Test user update with invalid email."""
        result = await user_manager.update_user("user-1", email="invalid-email")

        assert result["status"] == "error"
        assert result["message"] == "Valid email address is required"
        user_manager.user_service.update_user.assert_not_called()

    @pytest.mark.asyncio
    async def test_update_user_no_updates(self, user_manager):
        """Test user update with no updates provided."""
        result = await user_manager.update_user("user-1")

        assert result["status"] == "error"
        assert result["message"] == "No updates provided."
        user_manager.user_service.update_user.assert_not_called()

    @pytest.mark.asyncio
    async def test_update_user_with_whitespace_stripping(self, user_manager):
        """Test user update with whitespace stripping."""
        user_manager.user_service.update_user.return_value = {"status": "success"}

        result = await user_manager.update_user("user-1", full_name="  New Name  ", email="  new@example.com  ")

        user_manager.user_service.update_user.assert_called_once_with(
            user_id="user-1",
            full_name="New Name",
            email="new@example.com",
            banned=None,
            password=None,
            force_change_password=None,
        )
        assert result["status"] == "success"


class TestUserManagerDeleteUser:
    """Test user deletion functionality."""

    @pytest.mark.asyncio
    async def test_delete_user(self, user_manager):
        """Test user deletion."""
        user_manager.user_service.delete_user.return_value = {"status": "success"}

        result = await user_manager.delete_user("user-1")

        user_manager.user_service.delete_user.assert_called_once_with("user-1")
        assert result["status"] == "success"
        assert result["message"] == "User 'user-1' deleted successfully"


class TestUserManagerBanUnban:
    """Test user ban/unban functionality."""

    @pytest.mark.asyncio
    async def test_ban_user(self, user_manager):
        """Test banning a user."""
        user_manager.user_service.ban_user.return_value = {"status": "success"}

        result = await user_manager.ban_user("user-1")

        user_manager.user_service.ban_user.assert_called_once_with("user-1")
        assert result["status"] == "success"
        assert result["message"] == "User 'user-1' banned successfully"

    @pytest.mark.asyncio
    async def test_unban_user(self, user_manager):
        """Test unbanning a user."""
        user_manager.user_service.unban_user.return_value = {"status": "success"}

        result = await user_manager.unban_user("user-1")

        user_manager.user_service.unban_user.assert_called_once_with("user-1")
        assert result["status"] == "success"
        assert result["message"] == "User 'user-1' unbanned successfully"


class TestUserManagerGroups:
    """Test group management functionality."""

    @pytest.mark.asyncio
    async def test_get_user_groups(self, user_manager):
        """Test getting user groups."""
        expected_result = {"status": "success", "data": []}
        user_manager.user_service.get_user_groups.return_value = expected_result

        result = await user_manager.get_user_groups("user-1")

        user_manager.user_service.get_user_groups.assert_called_once_with("user-1")
        assert result == expected_result

    @pytest.mark.asyncio
    async def test_add_user_to_group(self, user_manager):
        """Test adding user to group."""
        user_manager.user_service.add_user_to_group.return_value = {"status": "success"}

        result = await user_manager.add_user_to_group("user-1", "group-1")

        user_manager.user_service.add_user_to_group.assert_called_once_with("user-1", "group-1")
        assert result["status"] == "success"
        assert result["message"] == "User 'user-1' added to group 'group-1'"

    @pytest.mark.asyncio
    async def test_remove_user_from_group(self, user_manager):
        """Test removing user from group."""
        user_manager.user_service.remove_user_from_group.return_value = {"status": "success"}

        result = await user_manager.remove_user_from_group("user-1", "group-1")

        user_manager.user_service.remove_user_from_group.assert_called_once_with("user-1", "group-1")
        assert result["status"] == "success"
        assert result["message"] == "User 'user-1' removed from group 'group-1'"


class TestUserManagerRoles:
    """Test role management functionality."""

    @pytest.mark.asyncio
    async def test_get_user_roles(self, user_manager):
        """Test getting user roles."""
        expected_result = {"status": "success", "data": []}
        user_manager.user_service.get_user_roles.return_value = expected_result

        result = await user_manager.get_user_roles("user-1")

        user_manager.user_service.get_user_roles.assert_called_once_with("user-1")
        assert result == expected_result

    @pytest.mark.asyncio
    async def test_assign_user_role(self, user_manager):
        """Test assigning user role."""
        user_manager.user_service.assign_user_role.return_value = {"status": "success"}

        result = await user_manager.assign_user_role("user-1", "role-1")

        user_manager.user_service.assign_user_role.assert_called_once_with("user-1", "role-1")
        assert result["status"] == "success"
        assert result["message"] == "Role 'role-1' assigned to user 'user-1'"

    @pytest.mark.asyncio
    async def test_remove_user_role(self, user_manager):
        """Test removing user role."""
        user_manager.user_service.remove_user_role.return_value = {"status": "success"}

        result = await user_manager.remove_user_role("user-1", "role-1")

        user_manager.user_service.remove_user_role.assert_called_once_with("user-1", "role-1")
        assert result["status"] == "success"
        assert result["message"] == "Role 'role-1' removed from user 'user-1'"


class TestUserManagerTeams:
    """Test team management functionality."""

    @pytest.mark.asyncio
    async def test_get_user_teams(self, user_manager):
        """Test getting user teams."""
        expected_result = {"status": "success", "data": []}
        user_manager.user_service.get_user_teams.return_value = expected_result

        result = await user_manager.get_user_teams("user-1")

        user_manager.user_service.get_user_teams.assert_called_once_with("user-1")
        assert result == expected_result

    @pytest.mark.asyncio
    async def test_add_user_to_team(self, user_manager):
        """Test adding user to team."""
        user_manager.user_service.add_user_to_team.return_value = {"status": "success"}

        result = await user_manager.add_user_to_team("user-1", "team-1")

        user_manager.user_service.add_user_to_team.assert_called_once_with("user-1", "team-1")
        assert result["status"] == "success"
        assert result["message"] == "User 'user-1' added to team 'team-1'"

    @pytest.mark.asyncio
    async def test_remove_user_from_team(self, user_manager):
        """Test removing user from team."""
        user_manager.user_service.remove_user_from_team.return_value = {"status": "success"}

        result = await user_manager.remove_user_from_team("user-1", "team-1")

        user_manager.user_service.remove_user_from_team.assert_called_once_with("user-1", "team-1")
        assert result["status"] == "success"
        assert result["message"] == "User 'user-1' removed from team 'team-1'"


class TestUserManagerPasswordAndPermissions:
    """Test password and permission functionality."""

    @pytest.mark.asyncio
    async def test_change_user_password_success(self, user_manager):
        """Test changing user password."""
        user_manager.user_service.change_user_password.return_value = {"status": "success"}

        result = await user_manager.change_user_password("user-1", "newpassword123")

        user_manager.user_service.change_user_password.assert_called_once_with("user-1", "newpassword123", False)
        assert result["status"] == "success"
        assert result["message"] == "Password changed for user 'user-1'"

    @pytest.mark.asyncio
    async def test_change_user_password_with_force(self, user_manager):
        """Test changing user password with force change."""
        user_manager.user_service.change_user_password.return_value = {"status": "success"}

        result = await user_manager.change_user_password("user-1", "newpassword123", force_change=True)

        user_manager.user_service.change_user_password.assert_called_once_with("user-1", "newpassword123", True)
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_change_user_password_too_short(self, user_manager):
        """Test changing user password that's too short."""
        result = await user_manager.change_user_password("user-1", "123")

        assert result["status"] == "error"
        assert result["message"] == "Password must be at least 4 characters long"
        user_manager.user_service.change_user_password.assert_not_called()

    @pytest.mark.asyncio
    async def test_change_user_password_empty(self, user_manager):
        """Test changing user password that's empty."""
        result = await user_manager.change_user_password("user-1", "")

        assert result["status"] == "error"
        assert result["message"] == "Password must be at least 4 characters long"
        user_manager.user_service.change_user_password.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_user_permissions(self, user_manager):
        """Test getting user permissions."""
        expected_result = {"status": "success", "data": []}
        user_manager.user_service.get_user_permissions.return_value = expected_result

        result = await user_manager.get_user_permissions("user-1")

        user_manager.user_service.get_user_permissions.assert_called_once_with("user-1", None)
        assert result == expected_result

    @pytest.mark.asyncio
    async def test_get_user_permissions_with_project(self, user_manager):
        """Test getting user permissions for specific project."""
        expected_result = {"status": "success", "data": []}
        user_manager.user_service.get_user_permissions.return_value = expected_result

        result = await user_manager.get_user_permissions("user-1", project_id="proj-1")

        user_manager.user_service.get_user_permissions.assert_called_once_with("user-1", "proj-1")
        assert result == expected_result


class TestUserManagerPermissionsManagement:
    """Test permission management functionality."""

    @pytest.mark.asyncio
    async def test_manage_user_permissions_add_to_group(self, user_manager):
        """Test managing permissions by adding to group."""
        user_manager.user_service.add_user_to_group.return_value = {"status": "success"}

        result = await user_manager.manage_user_permissions("user-1", "add_to_group", group_id="group-1")

        user_manager.user_service.add_user_to_group.assert_called_once_with("user-1", "group-1")
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_manage_user_permissions_remove_from_group(self, user_manager):
        """Test managing permissions by removing from group."""
        user_manager.user_service.remove_user_from_group.return_value = {"status": "success"}

        result = await user_manager.manage_user_permissions("user-1", "remove_from_group", group_id="group-1")

        user_manager.user_service.remove_user_from_group.assert_called_once_with("user-1", "group-1")
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_manage_user_permissions_assign_role(self, user_manager):
        """Test managing permissions by assigning role."""
        user_manager.user_service.assign_user_role.return_value = {"status": "success"}

        result = await user_manager.manage_user_permissions("user-1", "assign_role", role_id="role-1")

        user_manager.user_service.assign_user_role.assert_called_once_with("user-1", "role-1")
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_manage_user_permissions_remove_role(self, user_manager):
        """Test managing permissions by removing role."""
        user_manager.user_service.remove_user_role.return_value = {"status": "success"}

        result = await user_manager.manage_user_permissions("user-1", "remove_role", role_id="role-1")

        user_manager.user_service.remove_user_role.assert_called_once_with("user-1", "role-1")
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_manage_user_permissions_invalid_action(self, user_manager):
        """Test managing permissions with invalid action."""
        result = await user_manager.manage_user_permissions("user-1", "invalid_action")

        assert result["status"] == "error"
        assert "Invalid action 'invalid_action'" in result["message"]

    @pytest.mark.asyncio
    async def test_manage_user_permissions_missing_group_id(self, user_manager):
        """Test managing permissions with missing group ID."""
        result = await user_manager.manage_user_permissions("user-1", "add_to_group")

        assert result["status"] == "error"
        assert "missing required parameters" in result["message"]


class TestUserManagerDisplay:
    """Test display functionality."""

    def test_display_users_table_empty(self, user_manager):
        """Test displaying empty users table."""
        user_manager.display_users_table([])

        user_manager.console.print.assert_called_once_with("No users found.", style="yellow")

    def test_display_users_table_with_users(self, user_manager, sample_user):
        """Test displaying users table with users."""
        user_manager.display_users_table([sample_user])

        # Verify that print was called and table was created
        user_manager.console.print.assert_called_once()
        args = user_manager.console.print.call_args[0]
        assert len(args) == 1  # Should have one argument (the table)

    def test_display_users_table_paginated_empty(self, user_manager):
        """Test displaying empty paginated users table."""
        user_manager.display_users_table_paginated([])

        user_manager.console.print.assert_called_once_with("No users found.", style="yellow")

    def test_display_users_table_paginated_with_users(self, user_manager, sample_user):
        """Test displaying paginated users table with users."""
        with patch("youtrack_cli.managers.users.create_paginated_display") as mock_paginated:
            mock_display = MagicMock()
            mock_paginated.return_value = mock_display

            user_manager.display_users_table_paginated([sample_user])

            mock_paginated.assert_called_once_with(user_manager.console, 50)
            mock_display.display_paginated_table.assert_called_once()

    def test_display_user_details_empty(self, user_manager):
        """Test displaying user details with no data."""
        user_manager.display_user_details(None)

        user_manager.console.print.assert_called_once_with("[red]No user data to display[/red]")

    def test_display_user_details_with_user(self, user_manager, sample_user):
        """Test displaying user details with user data."""
        user_manager.display_user_details(sample_user)

        # Verify multiple print calls were made for different parts of user info
        assert user_manager.console.print.call_count >= 5

    def test_display_user_details_banned_user(self, user_manager):
        """Test displaying details for banned user."""
        banned_user = {
            "login": "banneduser",
            "fullName": "Banned User",
            "email": "banned@example.com",
            "banned": True,
            "guest": False,
        }

        user_manager.display_user_details(banned_user)

        # Check that status was displayed as banned - safely handle the calls
        print_calls = []
        for call in user_manager.console.print.call_args_list:
            if call and len(call) > 0 and len(call[0]) > 0:
                print_calls.append(str(call[0][0]))

        status_calls = [call for call in print_calls if "Status" in call and "Banned" in call]
        assert len(status_calls) > 0

    def test_display_user_groups_empty(self, user_manager):
        """Test displaying empty user groups."""
        user_manager.display_user_groups([], "user-1")

        user_manager.console.print.assert_called_once_with(
            "[yellow]User 'user-1' is not a member of any groups.[/yellow]"
        )

    def test_display_user_groups_with_groups(self, user_manager):
        """Test displaying user groups with groups."""
        groups = [
            {"name": "Developers", "description": "Dev group", "autoJoin": True},
            {"name": "Users", "description": "User group", "autoJoin": False},
        ]

        user_manager.display_user_groups(groups, "user-1")

        user_manager.console.print.assert_called_once()

    def test_display_user_roles_empty(self, user_manager):
        """Test displaying empty user roles."""
        user_manager.display_user_roles([], "user-1")

        user_manager.console.print.assert_called_once_with("[yellow]User 'user-1' has no assigned roles.[/yellow]")

    def test_display_user_roles_with_roles(self, user_manager):
        """Test displaying user roles with roles."""
        roles = [
            {"name": "Administrator", "description": "Admin role"},
            {"name": "Developer", "description": "Dev role"},
        ]

        user_manager.display_user_roles(roles, "user-1")

        user_manager.console.print.assert_called_once()

    def test_display_user_teams_empty(self, user_manager):
        """Test displaying empty user teams."""
        user_manager.display_user_teams([], "user-1")

        user_manager.console.print.assert_called_once_with(
            "[yellow]User 'user-1' is not a member of any teams.[/yellow]"
        )

    def test_display_user_teams_with_teams(self, user_manager):
        """Test displaying user teams with teams."""
        teams = [{"name": "Development", "description": "Dev team"}, {"name": "QA", "description": "Quality team"}]

        user_manager.display_user_teams(teams, "user-1")

        user_manager.console.print.assert_called_once()
