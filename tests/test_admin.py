"""Tests for the admin module."""

from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest
from click.testing import CliRunner

from youtrack_cli.admin import AdminManager
from youtrack_cli.auth import AuthConfig
from youtrack_cli.main import main


@pytest.mark.unit
class TestAdminManager:
    """Test AdminManager functionality."""

    @pytest.fixture
    def auth_manager(self):
        """Create a mock auth manager for testing."""
        auth_manager = Mock()
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
    async def test_clear_caches_not_available(self, admin_manager, auth_manager):
        """Test cache clearing returns unavailable message."""
        result = await admin_manager.clear_caches()

        assert result["status"] == "error"
        assert "not available through the YouTrack REST API" in result["message"]
        assert "administrative UI" in result["message"]
        assert "Server restart procedures" in result["message"]

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

    def test_display_methods(self, admin_manager):
        """Test display methods for various data types."""
        # Test global settings display
        settings = [
            {"name": "setting1", "value": "value1", "description": "Description 1"},
        ]
        with patch("rich.console.Console.print") as mock_print:
            admin_manager.display_global_settings(settings)
            mock_print.assert_called()

        # Test license info display
        license_info = {
            "type": "Commercial",
            "licensedTo": "Test Company",
            "isActive": True,
        }
        with patch("rich.console.Console.print") as mock_print:
            admin_manager.display_license_info(license_info)
            mock_print.assert_called_once()

        # Test user groups display (empty and with data)
        with patch("rich.console.Console.print") as mock_print:
            admin_manager.display_user_groups([])
            mock_print.assert_called()

        groups = [{"name": "Developers", "description": "Dev team", "users": []}]
        with patch("rich.console.Console.print") as mock_print:
            admin_manager.display_user_groups(groups)
            mock_print.assert_called()


@pytest.mark.unit
class TestAdminCommands:
    """Test admin CLI commands."""

    def setup_method(self):
        """Set up test method."""
        self.runner = CliRunner()

    @patch("youtrack_cli.main.AdminManager")
    def test_admin_cli_commands(self, mock_admin):
        """Test admin CLI command execution patterns."""
        mock_admin_instance = mock_admin.return_value

        # Test global settings commands
        mock_admin_instance.get_global_settings.return_value = {"status": "success", "data": []}
        with patch("asyncio.run") as mock_asyncio:
            result = self.runner.invoke(main, ["admin", "global-settings", "get"])
            assert result.exit_code == 0
            mock_asyncio.assert_called_once()

        # Test license commands
        mock_admin_instance.get_license_info.return_value = {"status": "success", "data": {}}
        with patch("asyncio.run") as mock_asyncio:
            result = self.runner.invoke(main, ["admin", "license", "show"])
            assert result.exit_code == 0
            mock_asyncio.assert_called_once()

        # Test maintenance commands
        mock_admin_instance.clear_caches.return_value = {
            "status": "error",
            "message": "Cache clearing is not available through the YouTrack REST API.",
        }
        with patch("asyncio.run") as mock_asyncio:
            result = self.runner.invoke(main, ["admin", "maintenance", "clear-cache", "--force"])
            assert result.exit_code == 0
            mock_asyncio.assert_called_once()

        # Test user groups commands
        mock_admin_instance.list_user_groups.return_value = {"status": "success", "data": []}
        with patch("asyncio.run") as mock_asyncio:
            result = self.runner.invoke(main, ["admin", "user-groups", "list"])
            assert result.exit_code == 0
            mock_asyncio.assert_called_once()

    def test_admin_help_commands(self):
        """Test admin help commands."""
        # Test main admin help
        result = self.runner.invoke(main, ["admin", "--help"])
        assert result.exit_code == 0
        assert "Administrative operations" in result.output

        # Test one representative subcommand help
        result = self.runner.invoke(main, ["admin", "global-settings", "--help"])
        assert result.exit_code == 0
        assert "Manage global YouTrack settings" in result.output


@pytest.mark.unit
class TestAdminLocaleManager:
    """Test AdminManager locale functionality."""

    @pytest.fixture
    def auth_manager(self):
        """Create a mock auth manager for testing."""
        auth_manager = Mock()
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
    async def test_locale_operations(self, admin_manager, auth_manager):
        """Test locale settings operations."""
        # Test successful locale settings retrieval
        mock_locale_settings = {
            "locale": {
                "name": "English",
                "id": "en_US",
                "language": "en",
                "locale": "en_US",
                "community": False,
                "$type": "LocaleDescriptor",
            },
            "isRTL": False,
            "$type": "LocaleSettings",
        }

        with patch("youtrack_cli.admin.get_client_manager") as mock_get_client:
            mock_client_manager = Mock()
            mock_response = Mock()
            mock_response.json.return_value = mock_locale_settings
            mock_client_manager.make_request = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_client_manager

            result = await admin_manager.get_locale_settings()
            assert result["status"] == "success"
            assert result["data"] == mock_locale_settings

            # Verify the API call was made with the correct fields parameter
            mock_client_manager.make_request.assert_called_once()
            call_args = mock_client_manager.make_request.call_args
            assert call_args[1]["params"]["fields"] == "locale(id,name,language,locale,community),isRTL"

        # Test locale settings update
        with patch("youtrack_cli.admin.get_client_manager") as mock_get_client:
            mock_client_manager = Mock()
            mock_client_manager.make_request = AsyncMock()
            mock_get_client.return_value = mock_client_manager

            result = await admin_manager.set_locale_settings("de_DE")
            assert result["status"] == "success"
            assert "de_DE" in result["message"]

    @pytest.mark.asyncio
    async def test_locale_auth_and_error_handling(self, admin_manager):
        """Test locale authentication and error handling."""
        # Test no authentication
        admin_manager.auth_manager.load_credentials.return_value = None
        result = await admin_manager.get_locale_settings()
        assert result["status"] == "error"
        assert "Not authenticated" in result["message"]

        # Test invalid locale error
        admin_manager.auth_manager.load_credentials.return_value = AuthConfig(
            base_url="https://test.youtrack.cloud", token="test-token", username="test-user"
        )
        with patch("youtrack_cli.admin.get_client_manager") as mock_get_client:
            mock_client_manager = Mock()
            mock_response = Mock()
            mock_response.status_code = 400
            mock_request = Mock()
            http_error = httpx.HTTPStatusError("Bad Request", request=mock_request, response=mock_response)
            mock_client_manager.make_request = AsyncMock(side_effect=http_error)
            mock_get_client.return_value = mock_client_manager

            result = await admin_manager.set_locale_settings("invalid_locale")
            assert result["status"] == "error"
            assert "Invalid locale ID" in result["message"]
