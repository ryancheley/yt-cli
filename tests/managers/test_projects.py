"""Tests for ProjectManager."""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from youtrack_cli.auth import AuthManager
from youtrack_cli.managers.projects import ProjectManager


@pytest.fixture
def auth_manager():
    """Create a mock auth manager."""
    mock_auth = Mock(spec=AuthManager)
    return mock_auth


@pytest.fixture
def project_manager(auth_manager):
    """Create a ProjectManager instance."""
    return ProjectManager(auth_manager)


class TestProjectManagerUserResolution:
    """Test user resolution functionality in ProjectManager."""

    @pytest.mark.asyncio
    async def test_resolve_user_id_with_valid_username(self, project_manager):
        """Test resolving a valid username to user ID."""
        mock_user_data = {"id": "2-1", "login": "admin"}

        with patch.object(project_manager.user_manager, "get_user", new_callable=AsyncMock) as mock_get_user:
            mock_get_user.return_value = {"status": "success", "data": mock_user_data}

            user_id, error = await project_manager._resolve_user_id("admin")

            assert user_id == "2-1"
            assert error is None
            mock_get_user.assert_called_once_with("admin", fields="id,login")

    @pytest.mark.asyncio
    async def test_resolve_user_id_with_invalid_username(self, project_manager):
        """Test resolving an invalid username."""
        with patch.object(project_manager.user_manager, "get_user", new_callable=AsyncMock) as mock_get_user:
            mock_get_user.return_value = {"status": "error", "message": "User not found"}

            user_id, error = await project_manager._resolve_user_id("nonexistent")

            assert user_id == "nonexistent"
            assert error == "User 'nonexistent' not found"
            mock_get_user.assert_called_once_with("nonexistent", fields="id,login")

    @pytest.mark.asyncio
    async def test_resolve_user_id_with_valid_user_id_digits_and_dash(self, project_manager):
        """Test resolving a valid user ID that contains digits and dashes."""
        mock_user_data = {"id": "2-1", "login": "admin"}

        with patch.object(project_manager.user_manager, "get_user", new_callable=AsyncMock) as mock_get_user:
            mock_get_user.return_value = {"status": "success", "data": mock_user_data}

            user_id, error = await project_manager._resolve_user_id("2-1")

            assert user_id == "2-1"
            assert error is None
            mock_get_user.assert_called_once_with("2-1", fields="id,login")

    @pytest.mark.asyncio
    async def test_resolve_user_id_with_system_user_guest(self, project_manager):
        """Test resolving system user 'guest'."""
        mock_user_data = {"id": "guest", "login": "guest"}

        with patch.object(project_manager.user_manager, "get_user", new_callable=AsyncMock) as mock_get_user:
            mock_get_user.return_value = {"status": "success", "data": mock_user_data}

            user_id, error = await project_manager._resolve_user_id("guest")

            assert user_id == "guest"
            assert error is None
            mock_get_user.assert_called_once_with("guest", fields="id,login")

    @pytest.mark.asyncio
    async def test_resolve_user_id_with_presumed_user_id_that_does_not_exist(self, project_manager):
        """Test resolving what looks like a user ID but doesn't exist, falls back to username resolution."""
        with patch.object(project_manager.user_manager, "get_user", new_callable=AsyncMock) as mock_get_user:
            # First call (validating presumed user ID) fails
            # Second call (username resolution) also fails
            mock_get_user.return_value = {"status": "error", "message": "User not found"}

            user_id, error = await project_manager._resolve_user_id("99-99")

            assert user_id == "99-99"
            assert error == "User '99-99' not found"
            # Should be called twice: once for ID validation, once for username resolution
            assert mock_get_user.call_count == 2

    @pytest.mark.asyncio
    async def test_resolve_user_id_with_user_missing_id_field(self, project_manager):
        """Test resolving user with missing ID field in response."""
        mock_user_data = {"login": "admin"}  # Missing 'id' field

        with patch.object(project_manager.user_manager, "get_user", new_callable=AsyncMock) as mock_get_user:
            mock_get_user.return_value = {"status": "success", "data": mock_user_data}

            user_id, error = await project_manager._resolve_user_id("admin")

            assert user_id == "admin"
            assert error == "User 'admin' found but missing ID field"

    @pytest.mark.asyncio
    async def test_resolve_user_id_with_network_error(self, project_manager):
        """Test resolving user when network error occurs."""
        with patch.object(project_manager.user_manager, "get_user", new_callable=AsyncMock) as mock_get_user:
            mock_get_user.side_effect = Exception("Network error")

            user_id, error = await project_manager._resolve_user_id("admin")

            assert user_id == "admin"
            assert "Error resolving username 'admin': Network error" in error

    @pytest.mark.asyncio
    async def test_resolve_user_id_with_complex_user_id_format(self, project_manager):
        """Test resolving complex user ID formats."""
        test_cases = [
            ("123", True),  # Pure digits
            ("2-1", True),  # Digits with dash
            ("10-25-3", True),  # Multiple dashes with digits
            ("user123", False),  # Username with digits
            ("admin", False),  # Simple username
            ("test-user", False),  # Username with dash but no digits
        ]

        for input_value, _should_be_treated_as_id in test_cases:
            mock_user_data = {"id": input_value, "login": "test"}

            with patch.object(project_manager.user_manager, "get_user", new_callable=AsyncMock) as mock_get_user:
                mock_get_user.return_value = {"status": "success", "data": mock_user_data}

                user_id, error = await project_manager._resolve_user_id(input_value)

                assert user_id == input_value
                assert error is None
                mock_get_user.assert_called_with(input_value, fields="id,login")


class TestProjectManagerCreateProjectWithUserResolution:
    """Test project creation with user resolution."""

    @pytest.mark.asyncio
    async def test_create_project_with_username_resolution_success(self, project_manager):
        """Test successful project creation with username resolution."""
        mock_user_data = {"id": "2-1", "login": "admin"}
        mock_project_response = {
            "status": "success",
            "data": {"id": "TEST", "name": "Test Project", "shortName": "TEST"},
        }

        with patch.object(project_manager.user_manager, "get_user", new_callable=AsyncMock) as mock_get_user:
            mock_get_user.return_value = {"status": "success", "data": mock_user_data}

            with patch.object(project_manager.project_service, "create_project", new_callable=AsyncMock) as mock_create:
                mock_create.return_value = mock_project_response

                result = await project_manager.create_project(
                    name="Test Project", short_name="TEST", leader_login="admin"
                )

                assert result["status"] == "success"
                # Verify that the service was called with the resolved user ID
                mock_create.assert_called_once_with(
                    short_name="TEST",
                    name="Test Project",
                    description=None,
                    leader_login="2-1",  # Resolved user ID, not original username
                )

    @pytest.mark.asyncio
    async def test_create_project_with_username_resolution_failure(self, project_manager):
        """Test project creation failure when username resolution fails."""
        with patch.object(project_manager.user_manager, "get_user", new_callable=AsyncMock) as mock_get_user:
            mock_get_user.return_value = {"status": "error", "message": "User not found"}

            result = await project_manager.create_project(
                name="Test Project", short_name="TEST", leader_login="nonexistent"
            )

            assert result["status"] == "error"
            assert "Failed to resolve project leader" in result["message"]
            assert "User 'nonexistent' not found" in result["message"]

    @pytest.mark.asyncio
    async def test_create_project_with_user_id_passthrough(self, project_manager):
        """Test project creation with user ID that passes through validation."""
        mock_user_data = {"id": "2-1", "login": "admin"}
        mock_project_response = {
            "status": "success",
            "data": {"id": "TEST", "name": "Test Project", "shortName": "TEST"},
        }

        with patch.object(project_manager.user_manager, "get_user", new_callable=AsyncMock) as mock_get_user:
            mock_get_user.return_value = {"status": "success", "data": mock_user_data}

            with patch.object(project_manager.project_service, "create_project", new_callable=AsyncMock) as mock_create:
                mock_create.return_value = mock_project_response

                result = await project_manager.create_project(
                    name="Test Project",
                    short_name="TEST",
                    leader_login="2-1",  # Already a user ID
                )

                assert result["status"] == "success"
                # Should still call the service with the validated user ID
                mock_create.assert_called_once_with(
                    short_name="TEST", name="Test Project", description=None, leader_login="2-1"
                )


class TestProjectManagerUpdateProjectWithUserResolution:
    """Test project update with user resolution."""

    @pytest.mark.asyncio
    async def test_update_project_with_username_resolution_success(self, project_manager):
        """Test successful project update with username resolution."""
        mock_user_data = {"id": "2-1", "login": "admin"}
        mock_project_response = {"status": "success", "data": {"id": "TEST", "name": "Updated Project"}}

        with patch.object(project_manager.user_manager, "get_user", new_callable=AsyncMock) as mock_get_user:
            mock_get_user.return_value = {"status": "success", "data": mock_user_data}

            with patch.object(project_manager.project_service, "update_project", new_callable=AsyncMock) as mock_update:
                mock_update.return_value = mock_project_response

                result = await project_manager.update_project(
                    project_id="TEST", name="Updated Project", leader_login="admin"
                )

                assert result["status"] == "success"
                # Verify that the service was called with the resolved user ID
                mock_update.assert_called_once_with(
                    project_id="TEST",
                    name="Updated Project",
                    description=None,
                    leader_login="2-1",  # Resolved user ID
                    archived=None,
                )

    @pytest.mark.asyncio
    async def test_update_project_with_username_resolution_failure(self, project_manager):
        """Test project update failure when username resolution fails."""
        with patch.object(project_manager.user_manager, "get_user", new_callable=AsyncMock) as mock_get_user:
            mock_get_user.return_value = {"status": "error", "message": "User not found"}

            result = await project_manager.update_project(
                project_id="TEST", name="Updated Project", leader_login="nonexistent"
            )

            assert result["status"] == "error"
            assert "Failed to resolve leader" in result["message"]
            assert "User 'nonexistent' not found" in result["message"]
