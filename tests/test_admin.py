"""Tests for the admin module."""

from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest
from click.testing import CliRunner

from youtrack_cli.admin import AdminManager
from youtrack_cli.auth import AuthConfig, AuthManager
from youtrack_cli.main import main


class TestAdminManager:
    """Test AdminManager functionality."""

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
    def admin_manager(self, auth_manager):
        """Create an AdminManager instance for testing."""
        return AdminManager(auth_manager)

    @pytest.mark.asyncio
    async def test_get_global_settings_success(self, admin_manager, auth_manager):
        """Test successful global settings retrieval with new nested format."""
        # Mock responses for each endpoint
        mock_system_settings = {
            "maxExportItems": 500,
            "maxUploadFileSize": 10485760,
            "allowStatisticsCollection": False,
            "$type": "SystemSettings",
        }
        mock_license = {"username": "Test User", "license": "test-license-key", "$type": "License"}
        mock_appearance = {"logo": {"url": "/test.svg", "$type": "Logo"}, "$type": "AppearanceSettings"}
        mock_notification = {"emailSettings": {"$type": "EmailSettings"}, "$type": "NotificationSettings"}

        with patch("youtrack_cli.admin.get_client_manager") as mock_get_client:
            mock_client_manager = Mock()

            # Mock responses for each endpoint call
            mock_responses = [
                Mock(),  # systemSettings
                Mock(),  # license
                Mock(),  # appearanceSettings
                Mock(),  # notificationSettings
            ]
            mock_responses[0].json.return_value = mock_system_settings
            mock_responses[1].json.return_value = mock_license
            mock_responses[2].json.return_value = mock_appearance
            mock_responses[3].json.return_value = mock_notification

            mock_client_manager.make_request = AsyncMock(side_effect=mock_responses)
            mock_get_client.return_value = mock_client_manager

            result = await admin_manager.get_global_settings()

            assert result["status"] == "success"
            # Check that we got nested data with the expected categories
            assert "systemSettings" in result["data"]
            assert "license" in result["data"]
            assert "appearanceSettings" in result["data"]
            assert "notificationSettings" in result["data"]
            assert result["data"]["systemSettings"] == mock_system_settings

    @pytest.mark.asyncio
    async def test_get_global_settings_no_auth(self, admin_manager):
        """Test global settings retrieval without authentication."""
        admin_manager.auth_manager.load_credentials.return_value = None

        result = await admin_manager.get_global_settings()

        assert result["status"] == "error"
        assert "Not authenticated" in result["message"]

    @pytest.mark.asyncio
    async def test_get_global_settings_insufficient_permissions(self, admin_manager, auth_manager):
        """Test global settings retrieval with insufficient permissions."""
        with patch("youtrack_cli.admin.get_client_manager") as mock_get_client:
            mock_client_manager = Mock()
            mock_response = Mock()
            mock_response.status_code = 403
            mock_request = Mock()
            http_error = httpx.HTTPStatusError("Forbidden", request=mock_request, response=mock_response)
            # All endpoints return 403
            mock_client_manager.make_request = AsyncMock(side_effect=http_error)
            mock_get_client.return_value = mock_client_manager

            result = await admin_manager.get_global_settings()

            assert result["status"] == "error"
            assert "Insufficient permissions" in result["message"]

    @pytest.mark.asyncio
    async def test_set_global_setting_success(self, admin_manager, auth_manager):
        """Test successful global setting update."""
        with patch("youtrack_cli.admin.get_client_manager") as mock_get_client:
            mock_client_manager = Mock()
            mock_response = Mock()

            mock_client_manager.make_request = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_client_manager

            result = await admin_manager.set_global_setting("server.name", "New Name")

            assert result["status"] == "success"
            assert "updated successfully" in result["message"]

    @pytest.mark.asyncio
    async def test_set_global_setting_invalid_data(self, admin_manager, auth_manager):
        """Test global setting update with invalid data."""
        with patch("youtrack_cli.admin.get_client_manager") as mock_get_client:
            mock_client_manager = Mock()
            mock_response = Mock()
            mock_response.status_code = 400
            mock_request = Mock()
            http_error = httpx.HTTPStatusError("Bad Request", request=mock_request, response=mock_response)
            mock_client_manager.make_request = AsyncMock(side_effect=http_error)
            mock_get_client.return_value = mock_client_manager

            result = await admin_manager.set_global_setting("invalid.key", "value")

            assert result["status"] == "error"
            assert "Invalid setting" in result["message"]

    @pytest.mark.asyncio
    async def test_get_license_info_success(self, admin_manager, auth_manager):
        """Test successful license information retrieval."""
        mock_license = {
            "type": "Commercial",
            "licensedTo": "Test Company",
            "expirationDate": "2025-12-31",
            "maxUsers": 100,
            "isActive": True,
        }

        with patch("youtrack_cli.admin.get_client_manager") as mock_get_client:
            mock_client_manager = Mock()
            mock_response = Mock()
            mock_response.json.return_value = mock_license

            mock_client_manager.make_request = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_client_manager

            result = await admin_manager.get_license_info()

            assert result["status"] == "success"
            assert result["data"] == mock_license

    @pytest.mark.asyncio
    async def test_get_license_usage_success(self, admin_manager, auth_manager):
        """Test successful license usage retrieval."""
        mock_usage = {"totalUsers": 75, "activeUsers": 50, "remainingUsers": 25}

        with patch("youtrack_cli.admin.get_client_manager") as mock_get_client:
            mock_client_manager = Mock()
            mock_response = Mock()
            mock_response.json.return_value = mock_usage

            mock_client_manager.make_request = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_client_manager

            result = await admin_manager.get_license_usage()

            assert result["status"] == "success"
            assert result["data"] == mock_usage

    @pytest.mark.asyncio
    async def test_get_system_health_success(self, admin_manager, auth_manager):
        """Test successful system health check."""
        mock_health = {
            "status": "healthy",
            "checks": [
                {"name": "Database", "status": "healthy", "message": "OK"},
                {"name": "Memory", "status": "healthy", "message": "OK"},
            ],
        }

        with patch("youtrack_cli.admin.get_client_manager") as mock_get_client:
            mock_client_manager = Mock()
            mock_response = Mock()
            mock_response.json.return_value = mock_health

            mock_client_manager.make_request = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_client_manager

            result = await admin_manager.get_system_health()

            assert result["status"] == "success"
            assert result["data"] == mock_health

    @pytest.mark.asyncio
    async def test_get_system_health_404_error(self, admin_manager, auth_manager):
        """Test system health check with 404 error on all endpoints."""
        with patch("youtrack_cli.admin.get_client_manager") as mock_get_client:
            mock_client_manager = Mock()
            mock_response = Mock()
            mock_response.status_code = 404
            mock_request = Mock()
            http_error = httpx.HTTPStatusError("Not Found", request=mock_request, response=mock_response)
            mock_client_manager.make_request = AsyncMock(side_effect=http_error)
            mock_get_client.return_value = mock_client_manager

            result = await admin_manager.get_system_health()

            assert result["status"] == "error"
            assert "System health endpoint not found (404)" in result["message"]
            assert "YouTrack version doesn't support this endpoint" in result["message"]

    @pytest.mark.asyncio
    async def test_get_system_health_403_error(self, admin_manager, auth_manager):
        """Test system health check with 403 permission error."""
        with patch("youtrack_cli.admin.get_client_manager") as mock_get_client:
            mock_client_manager = Mock()
            mock_response = Mock()
            mock_response.status_code = 403
            mock_request = Mock()
            http_error = httpx.HTTPStatusError("Forbidden", request=mock_request, response=mock_response)
            mock_client_manager.make_request = AsyncMock(side_effect=http_error)
            mock_get_client.return_value = mock_client_manager

            result = await admin_manager.get_system_health()

            assert result["status"] == "error"
            assert "Insufficient permissions for health check" in result["message"]
            assert "Low-level Admin Read" in result["message"]

    @pytest.mark.asyncio
    async def test_clear_caches_success(self, admin_manager, auth_manager):
        """Test successful cache clearing."""
        with patch("youtrack_cli.admin.get_client_manager") as mock_get_client:
            mock_client_manager = Mock()
            mock_response = Mock()

            mock_client_manager.make_request = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_client_manager

            result = await admin_manager.clear_caches()

            assert result["status"] == "success"
            assert "cleared successfully" in result["message"]

    @pytest.mark.asyncio
    async def test_list_user_groups_success(self, admin_manager, auth_manager):
        """Test successful user groups listing."""
        mock_groups = [
            {
                "id": "group1",
                "name": "Developers",
                "description": "Development team",
                "users": [{"login": "dev1", "fullName": "Developer One"}],
            },
            {
                "id": "group2",
                "name": "Admins",
                "description": "System administrators",
                "users": [{"login": "admin1", "fullName": "Admin One"}],
            },
        ]

        with patch("youtrack_cli.admin.get_client_manager") as mock_get_client:
            mock_client_manager = Mock()
            mock_response = Mock()
            mock_response.json.return_value = {"usergroups": mock_groups}

            mock_client_manager.make_request = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_client_manager

            result = await admin_manager.list_user_groups()

            assert result["status"] == "success"
            assert result["data"] == mock_groups

    @pytest.mark.asyncio
    async def test_create_user_group_success(self, admin_manager, auth_manager):
        """Test successful user group creation."""
        mock_created_group = {
            "id": "new-group",
            "name": "New Group",
            "description": "A new group",
        }

        with patch("youtrack_cli.admin.get_client_manager") as mock_get_client:
            mock_client_manager = Mock()
            mock_response = Mock()
            mock_response.json.return_value = mock_created_group

            mock_client_manager.make_request = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_client_manager

            result = await admin_manager.create_user_group("New Group", "A new group")

            assert result["status"] == "success"
            assert result["data"] == mock_created_group
            assert "created successfully" in result["message"]

    @pytest.mark.asyncio
    async def test_create_user_group_already_exists(self, admin_manager, auth_manager):
        """Test user group creation when group already exists."""
        with patch("youtrack_cli.admin.get_client_manager") as mock_get_client:
            mock_client_manager = Mock()
            mock_response = Mock()
            mock_response.status_code = 400
            mock_request = Mock()
            http_error = httpx.HTTPStatusError("Bad Request", request=mock_request, response=mock_response)
            mock_client_manager.make_request = AsyncMock(side_effect=http_error)
            mock_get_client.return_value = mock_client_manager

            result = await admin_manager.create_user_group("Existing Group")

            assert result["status"] == "error"
            assert "Invalid group data" in result["message"]

    @pytest.mark.asyncio
    async def test_list_custom_fields_success(self, admin_manager, auth_manager):
        """Test successful custom fields listing."""
        mock_fields = [
            {
                "id": "field1",
                "name": "Priority",
                "fieldType": {"presentation": "enum"},
                "isPrivate": False,
                "hasStateMachine": False,
            },
            {
                "id": "field2",
                "name": "Status",
                "fieldType": {"presentation": "state"},
                "isPrivate": False,
                "hasStateMachine": True,
            },
        ]

        with patch("youtrack_cli.admin.get_client_manager") as mock_get_client:
            mock_client_manager = Mock()
            mock_response = Mock()
            mock_response.json.return_value = mock_fields

            mock_client_manager.make_request = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_client_manager

            result = await admin_manager.list_custom_fields()

            assert result["status"] == "success"
            assert result["data"] == mock_fields

    def test_display_global_settings_list(self, admin_manager):
        """Test global settings display for list format."""
        settings = [
            {"name": "setting1", "value": "value1", "description": "Description 1"},
            {"name": "setting2", "value": "value2", "description": "Description 2"},
        ]

        with patch("rich.console.Console.print") as mock_print:
            admin_manager.display_global_settings(settings)

            # Verify that print was called
            mock_print.assert_called()

    def test_display_global_settings_single(self, admin_manager):
        """Test global settings display for single setting."""
        setting = {
            "name": "server.name",
            "value": "Test Server",
            "description": "Server name setting",
        }

        with patch("rich.console.Console.print") as mock_print:
            admin_manager.display_global_settings(setting)

            # Verify that print was called multiple times
            assert mock_print.call_count >= 2

    def test_display_global_settings_nested(self, admin_manager):
        """Test global settings display for new nested format."""
        nested_settings = {
            "systemSettings": {
                "maxExportItems": 500,
                "maxUploadFileSize": 10485760,
                "allowStatisticsCollection": False,
                "$type": "SystemSettings",
            },
            "license": {"username": "Test User", "license": "test-license-key", "$type": "License"},
        }

        with patch("rich.console.Console.print") as mock_print:
            admin_manager.display_global_settings(nested_settings)

            # Verify that a table was printed (should call print once for the table)
            mock_print.assert_called_once()

    def test_display_license_info(self, admin_manager):
        """Test license information display."""
        license_info = {
            "type": "Commercial",
            "licensedTo": "Test Company",
            "expirationDate": "2025-12-31",
            "maxUsers": 100,
            "isActive": True,
        }

        with patch("rich.console.Console.print") as mock_print:
            admin_manager.display_license_info(license_info)

            # Verify that print was called multiple times
            assert mock_print.call_count >= 3

    def test_display_system_health(self, admin_manager):
        """Test system health display."""
        health_info = {
            "status": "healthy",
            "checks": [
                {"name": "Database", "status": "healthy", "message": "All good"},
                {"name": "Memory", "status": "warning", "message": "High usage"},
            ],
        }

        with patch("rich.console.Console.print") as mock_print:
            admin_manager.display_system_health(health_info)

            # Verify that print was called
            mock_print.assert_called()

    def test_display_user_groups_empty(self, admin_manager):
        """Test user groups display with empty list."""
        with patch("rich.console.Console.print") as mock_print:
            admin_manager.display_user_groups([])

            # Verify that it shows "No user groups found"
            mock_print.assert_called()
            call_args = [call[0][0] for call in mock_print.call_args_list]
            no_groups_found = any("No user groups found" in str(arg) for arg in call_args)
            assert no_groups_found

    def test_display_user_groups_with_data(self, admin_manager):
        """Test user groups display with data."""
        groups = [
            {
                "name": "Developers",
                "description": "Dev team",
                "users": [{"login": "dev1"}],
            },
            {"name": "Admins", "description": "Admin team", "users": []},
        ]

        with patch("rich.console.Console.print") as mock_print:
            admin_manager.display_user_groups(groups)

            # Verify that print was called
            mock_print.assert_called()

    def test_display_custom_fields_empty(self, admin_manager):
        """Test custom fields display with empty list."""
        with patch("rich.console.Console.print") as mock_print:
            admin_manager.display_custom_fields([])

            # Verify that it shows "No custom fields found"
            mock_print.assert_called()
            call_args = [call[0][0] for call in mock_print.call_args_list]
            no_fields_found = any("No custom fields found" in str(arg) for arg in call_args)
            assert no_fields_found

    def test_display_custom_fields_with_data(self, admin_manager):
        """Test custom fields display with data."""
        fields = [
            {
                "name": "Priority",
                "fieldType": {"presentation": "enum"},
                "isPrivate": False,
                "hasStateMachine": False,
            },
            {
                "name": "Status",
                "fieldType": {"presentation": "state"},
                "isPrivate": True,
                "hasStateMachine": True,
            },
        ]

        with patch("rich.console.Console.print") as mock_print:
            admin_manager.display_custom_fields(fields)

            # Verify that print was called
            mock_print.assert_called()


class TestAdminCommands:
    """Test admin CLI commands."""

    def setup_method(self):
        """Set up test method."""
        self.runner = CliRunner()

    @patch("youtrack_cli.main.AdminManager")
    def test_admin_global_settings_get_success(self, mock_admin):
        """Test global settings get command execution."""
        mock_admin_instance = mock_admin.return_value
        mock_admin_instance.get_global_settings.return_value = {
            "status": "success",
            "data": [{"name": "server.name", "value": "Test"}],
        }

        with patch("asyncio.run") as mock_asyncio:
            result = self.runner.invoke(main, ["admin", "global-settings", "get"])

            assert result.exit_code == 0
            mock_asyncio.assert_called_once()

    @patch("youtrack_cli.main.AdminManager")
    def test_admin_global_settings_set_success(self, mock_admin):
        """Test global settings set command execution."""
        mock_admin_instance = mock_admin.return_value
        mock_admin_instance.set_global_setting.return_value = {
            "status": "success",
            "message": "Setting updated successfully",
        }

        with patch("asyncio.run") as mock_asyncio:
            result = self.runner.invoke(main, ["admin", "global-settings", "set", "server.name", "New Name"])

            assert result.exit_code == 0
            mock_asyncio.assert_called_once()

    @patch("youtrack_cli.main.AdminManager")
    def test_admin_license_show_success(self, mock_admin):
        """Test license show command execution."""
        mock_admin_instance = mock_admin.return_value
        mock_admin_instance.get_license_info.return_value = {
            "status": "success",
            "data": {"type": "Commercial", "isActive": True},
        }

        with patch("asyncio.run") as mock_asyncio:
            result = self.runner.invoke(main, ["admin", "license", "show"])

            assert result.exit_code == 0
            mock_asyncio.assert_called_once()

    @patch("youtrack_cli.main.AdminManager")
    def test_admin_license_usage_success(self, mock_admin):
        """Test license usage command execution."""
        mock_admin_instance = mock_admin.return_value
        mock_admin_instance.get_license_usage.return_value = {
            "status": "success",
            "data": {"totalUsers": 100, "activeUsers": 75},
        }

        with patch("asyncio.run") as mock_asyncio:
            result = self.runner.invoke(main, ["admin", "license", "usage"])

            assert result.exit_code == 0
            mock_asyncio.assert_called_once()

    @patch("youtrack_cli.main.AdminManager")
    def test_admin_maintenance_clear_cache_with_confirm(self, mock_admin):
        """Test maintenance clear cache command with confirmation."""
        mock_admin_instance = mock_admin.return_value
        mock_admin_instance.clear_caches.return_value = {
            "status": "success",
            "message": "Caches cleared successfully",
        }

        with patch("asyncio.run") as mock_asyncio:
            result = self.runner.invoke(main, ["admin", "maintenance", "clear-cache", "--confirm"])

            assert result.exit_code == 0
            mock_asyncio.assert_called_once()

    @patch("youtrack_cli.main.AdminManager")
    def test_admin_health_check_success(self, mock_admin):
        """Test health check command execution."""
        mock_admin_instance = mock_admin.return_value
        mock_admin_instance.get_system_health.return_value = {
            "status": "success",
            "data": {"status": "healthy", "checks": []},
        }

        with patch("asyncio.run") as mock_asyncio:
            result = self.runner.invoke(main, ["admin", "health", "check"])

            assert result.exit_code == 0
            mock_asyncio.assert_called_once()

    @patch("youtrack_cli.main.AdminManager")
    def test_admin_user_groups_list_success(self, mock_admin):
        """Test user groups list command execution."""
        mock_admin_instance = mock_admin.return_value
        mock_admin_instance.list_user_groups.return_value = {
            "status": "success",
            "data": [{"name": "Developers", "description": "Dev team"}],
        }

        with patch("asyncio.run") as mock_asyncio:
            result = self.runner.invoke(main, ["admin", "user-groups", "list"])

            assert result.exit_code == 0
            mock_asyncio.assert_called_once()

    @patch("youtrack_cli.main.AdminManager")
    def test_admin_user_groups_create_success(self, mock_admin):
        """Test user groups create command execution."""
        mock_admin_instance = mock_admin.return_value
        mock_admin_instance.create_user_group.return_value = {
            "status": "success",
            "message": "Group created successfully",
        }

        with patch("asyncio.run") as mock_asyncio:
            result = self.runner.invoke(main, ["admin", "user-groups", "create", "NewGroup"])

            assert result.exit_code == 0
            mock_asyncio.assert_called_once()

    @patch("youtrack_cli.main.AdminManager")
    def test_admin_fields_list_success(self, mock_admin):
        """Test fields list command execution."""
        mock_admin_instance = mock_admin.return_value
        mock_admin_instance.list_custom_fields.return_value = {
            "status": "success",
            "data": [{"name": "Priority", "fieldType": {"presentation": "enum"}}],
        }

        with patch("asyncio.run") as mock_asyncio:
            result = self.runner.invoke(main, ["admin", "fields", "list"])

            assert result.exit_code == 0
            mock_asyncio.assert_called_once()

    def test_admin_group_help(self):
        """Test admin group help command."""
        result = self.runner.invoke(main, ["admin", "--help"])

        assert result.exit_code == 0
        assert "Administrative operations" in result.output
        assert "global-settings" in result.output
        assert "license" in result.output
        assert "maintenance" in result.output

    def test_admin_global_settings_help(self):
        """Test admin global-settings help command."""
        result = self.runner.invoke(main, ["admin", "global-settings", "--help"])

        assert result.exit_code == 0
        assert "Manage global YouTrack settings" in result.output
        assert "get" in result.output
        assert "set" in result.output

    def test_admin_license_help(self):
        """Test admin license help command."""
        result = self.runner.invoke(main, ["admin", "license", "--help"])

        assert result.exit_code == 0
        assert "License management" in result.output
        assert "show" in result.output
        assert "usage" in result.output

    def test_admin_maintenance_help(self):
        """Test admin maintenance help command."""
        result = self.runner.invoke(main, ["admin", "maintenance", "--help"])

        assert result.exit_code == 0
        assert "System maintenance operations" in result.output
        assert "clear-cache" in result.output

    def test_admin_health_help(self):
        """Test admin health help command."""
        result = self.runner.invoke(main, ["admin", "health", "--help"])

        assert result.exit_code == 0
        assert "System health checks" in result.output
        assert "check" in result.output

    def test_admin_user_groups_help(self):
        """Test admin user-groups help command."""
        result = self.runner.invoke(main, ["admin", "user-groups", "--help"])

        assert result.exit_code == 0
        assert "Manage user groups" in result.output
        assert "list" in result.output
        assert "create" in result.output

    def test_admin_fields_help(self):
        """Test admin fields help command."""
        result = self.runner.invoke(main, ["admin", "fields", "--help"])

        assert result.exit_code == 0
        assert "Manage custom fields" in result.output
        assert "list" in result.output
