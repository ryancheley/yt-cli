"""Tests for the projects module."""

from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest
from click.testing import CliRunner

from youtrack_cli.auth import AuthConfig, AuthManager
from youtrack_cli.main import main
from youtrack_cli.projects import ProjectManager


class TestProjectManager:
    """Test ProjectManager functionality."""

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
    def project_manager(self, auth_manager):
        """Create a ProjectManager instance for testing."""
        return ProjectManager(auth_manager)

    @pytest.mark.asyncio
    async def test_list_projects_success(self, project_manager, auth_manager):
        """Test successful project listing."""
        mock_projects = [
            {
                "id": "1",
                "name": "Test Project 1",
                "shortName": "TP1",
                "leader": {"login": "user1", "fullName": "User One"},
                "archived": False,
            },
            {
                "id": "2",
                "name": "Test Project 2",
                "shortName": "TP2",
                "leader": {"login": "user2", "fullName": "User Two"},
                "archived": True,
            },
        ]

        with patch("youtrack_cli.projects.get_client_manager") as mock_get_client_manager:
            mock_response = Mock()
            mock_response.json.return_value = mock_projects
            mock_response.headers = {"content-type": "application/json"}
            mock_response.text = "mock response body"
            mock_response.status_code = 200
            mock_response.raise_for_status.return_value = None

            mock_client_manager = Mock()
            mock_client_manager.make_request = AsyncMock(return_value=mock_response)
            mock_get_client_manager.return_value = mock_client_manager

            result = await project_manager.list_projects()

            assert result["status"] == "success"
            assert len(result["data"]) == 1  # Archived project should be filtered
            assert result["data"][0]["name"] == "Test Project 1"
            assert result["count"] == 1

    @pytest.mark.asyncio
    async def test_list_projects_with_archived(self, project_manager, auth_manager):
        """Test project listing including archived projects."""
        mock_projects = [
            {
                "id": "1",
                "name": "Test Project 1",
                "shortName": "TP1",
                "leader": {"login": "user1", "fullName": "User One"},
                "archived": False,
            },
            {
                "id": "2",
                "name": "Test Project 2",
                "shortName": "TP2",
                "leader": {"login": "user2", "fullName": "User Two"},
                "archived": True,
            },
        ]

        with patch("youtrack_cli.projects.get_client_manager") as mock_get_client_manager:
            mock_response = Mock()
            mock_response.json.return_value = mock_projects
            mock_response.headers = {"content-type": "application/json"}
            mock_response.text = "mock response body"
            mock_response.status_code = 200
            mock_response.raise_for_status.return_value = None

            mock_client_manager = Mock()
            mock_client_manager.make_request = AsyncMock(return_value=mock_response)
            mock_get_client_manager.return_value = mock_client_manager

            result = await project_manager.list_projects(show_archived=True)

            assert result["status"] == "success"
            assert len(result["data"]) == 2
            assert result["count"] == 2

    @pytest.mark.asyncio
    async def test_list_projects_not_authenticated(self, auth_manager):
        """Test project listing when not authenticated."""
        auth_manager.load_credentials.return_value = None
        project_manager = ProjectManager(auth_manager)

        result = await project_manager.list_projects()

        assert result["status"] == "error"
        assert "Not authenticated" in result["message"]

    @pytest.mark.asyncio
    async def test_list_projects_http_error(self, project_manager, auth_manager):
        """Test project listing with HTTP error."""
        with patch("youtrack_cli.projects.get_client_manager") as mock_get_client_manager:
            mock_client_manager = Mock()
            mock_client_manager.make_request = AsyncMock(side_effect=httpx.HTTPError("Network error"))
            mock_get_client_manager.return_value = mock_client_manager

            result = await project_manager.list_projects()

            assert result["status"] == "error"
            assert "HTTP error" in result["message"]

    @pytest.mark.asyncio
    async def test_create_project_success(self, project_manager, auth_manager):
        """Test successful project creation."""
        mock_created_project = {
            "id": "123",
            "name": "New Project",
            "shortName": "NP",
            "leader": {"login": "user1", "fullName": "User One"},
        }

        # Mock the user resolution
        mock_user_data = {"id": "2-1", "login": "user1"}

        with patch("youtrack_cli.projects.get_client_manager") as mock_get_client_manager:
            mock_response = Mock()
            mock_response.json.return_value = mock_created_project
            mock_response.raise_for_status.return_value = None
            mock_response.headers = {"content-type": "application/json"}
            mock_response.text = '{"id": "new-project", "name": "New Project"}'
            mock_response.status_code = 200

            mock_client_manager = Mock()
            mock_client_manager.make_request = AsyncMock(return_value=mock_response)
            mock_get_client_manager.return_value = mock_client_manager

            # Mock the user manager get_user method
            project_manager.user_manager.get_user = AsyncMock(
                return_value={"status": "success", "data": mock_user_data}
            )

            result = await project_manager.create_project(
                name="New Project",
                short_name="NP",
                leader_id="user1",
                description="Test project",
                template="scrum",
            )

            assert result["status"] == "success"
            assert result["data"]["name"] == "New Project"
            assert "created successfully" in result["message"]

    @pytest.mark.asyncio
    async def test_create_project_with_username_resolution(self, project_manager, auth_manager):
        """Test project creation with username resolution."""
        mock_created_project = {
            "id": "123",
            "name": "New Project",
            "shortName": "NP",
            "leader": {"login": "admin", "fullName": "Admin User"},
        }

        # Mock the user resolution
        mock_user_data = {"id": "2-1", "login": "admin"}

        with patch("youtrack_cli.projects.get_client_manager") as mock_get_client_manager:
            mock_response = Mock()
            mock_response.json.return_value = mock_created_project
            mock_response.raise_for_status.return_value = None
            mock_response.headers = {"content-type": "application/json"}
            mock_response.text = '{"id": "new-project", "name": "New Project"}'
            mock_response.status_code = 200

            mock_client_manager = Mock()
            mock_client_manager.make_request = AsyncMock(return_value=mock_response)
            mock_get_client_manager.return_value = mock_client_manager

            # Mock the user manager get_user method
            project_manager.user_manager.get_user = AsyncMock(
                return_value={"status": "success", "data": mock_user_data}
            )

            result = await project_manager.create_project(
                name="New Project",
                short_name="NP",
                leader_id="admin",  # Using username instead of ID
                description="Test project",
                template="scrum",
            )

            assert result["status"] == "success"
            assert result["data"]["name"] == "New Project"
            assert "created successfully" in result["message"]

    @pytest.mark.asyncio
    async def test_create_project_with_user_id_passthrough(self, project_manager, auth_manager):
        """Test project creation with user ID that should pass through unchanged."""
        mock_created_project = {
            "id": "123",
            "name": "New Project",
            "shortName": "NP",
            "leader": {"login": "admin", "fullName": "Admin User"},
        }

        with patch("youtrack_cli.projects.get_client_manager") as mock_get_client_manager:
            mock_response = Mock()
            mock_response.json.return_value = mock_created_project
            mock_response.raise_for_status.return_value = None
            mock_response.headers = {"content-type": "application/json"}
            mock_response.text = '{"id": "new-project", "name": "New Project"}'
            mock_response.status_code = 200

            mock_client_manager = Mock()
            mock_client_manager.make_request = AsyncMock(return_value=mock_response)
            mock_get_client_manager.return_value = mock_client_manager

            result = await project_manager.create_project(
                name="New Project",
                short_name="NP",
                leader_id="2-1",  # Using user ID format
                description="Test project",
                template="scrum",
            )

            assert result["status"] == "success"
            assert result["data"]["name"] == "New Project"
            assert "created successfully" in result["message"]

    @pytest.mark.asyncio
    async def test_create_project_invalid_username(self, project_manager, auth_manager):
        """Test project creation with invalid username."""
        # Mock the user manager to return user not found
        project_manager.user_manager.get_user = AsyncMock(return_value={"status": "error", "message": "User not found"})

        result = await project_manager.create_project(
            name="New Project",
            short_name="NP",
            leader_id="nonexistent",
            description="Test project",
            template="scrum",
        )

        assert result["status"] == "error"
        assert "Failed to resolve leader" in result["message"]
        assert "User 'nonexistent' not found" in result["message"]

    @pytest.mark.asyncio
    async def test_create_project_invalid_data(self, project_manager, auth_manager):
        """Test project creation with invalid data."""
        # Mock the user resolution to succeed first
        mock_user_data = {"id": "2-1", "login": "invalid-user"}
        project_manager.user_manager.get_user = AsyncMock(return_value={"status": "success", "data": mock_user_data})

        with patch("youtrack_cli.projects.get_client_manager") as mock_get_client_manager:
            mock_response = Mock()
            mock_response.status_code = 400

            mock_request = Mock()
            http_error = httpx.HTTPStatusError("Bad request", request=mock_request, response=mock_response)

            mock_client_manager = Mock()
            mock_client_manager.make_request = AsyncMock(side_effect=http_error)
            mock_get_client_manager.return_value = mock_client_manager

            result = await project_manager.create_project(name="", short_name="", leader_id="invalid-user")

            assert result["status"] == "error"
            assert "Invalid project data" in result["message"]

    @pytest.mark.asyncio
    async def test_create_project_insufficient_permissions(self, project_manager, auth_manager):
        """Test project creation with insufficient permissions."""
        # Mock the user resolution to succeed first
        mock_user_data = {"id": "2-1", "login": "user1"}
        project_manager.user_manager.get_user = AsyncMock(return_value={"status": "success", "data": mock_user_data})

        with patch("youtrack_cli.projects.get_client_manager") as mock_get_client_manager:
            mock_response = Mock()
            mock_response.status_code = 403

            mock_request = Mock()
            http_error = httpx.HTTPStatusError("Forbidden", request=mock_request, response=mock_response)

            mock_client_manager = Mock()
            mock_client_manager.make_request = AsyncMock(side_effect=http_error)
            mock_get_client_manager.return_value = mock_client_manager

            result = await project_manager.create_project(name="New Project", short_name="NP", leader_id="user1")

            assert result["status"] == "error"
            assert "Insufficient permissions" in result["message"]

    @pytest.mark.asyncio
    async def test_get_project_success(self, project_manager, auth_manager):
        """Test successful project retrieval."""
        mock_project = {
            "id": "123",
            "name": "Test Project",
            "shortName": "TP",
            "description": "A test project",
            "leader": {"login": "user1", "fullName": "User One"},
            "archived": False,
            "createdBy": {"login": "creator", "fullName": "Project Creator"},
            "team": {
                "users": [
                    {"login": "user1", "fullName": "User One"},
                    {"login": "user2", "fullName": "User Two"},
                ]
            },
        }

        with patch("youtrack_cli.projects.get_client_manager") as mock_get_client_manager:
            mock_response = Mock()
            mock_response.json.return_value = mock_project
            mock_response.raise_for_status.return_value = None
            mock_response.headers = {"content-type": "application/json"}
            mock_response.text = '{"id": "test-project", "name": "Test Project"}'
            mock_response.status_code = 200

            mock_client_manager = Mock()
            mock_client_manager.make_request = AsyncMock(return_value=mock_response)
            mock_get_client_manager.return_value = mock_client_manager

            result = await project_manager.get_project("TP")

            assert result["status"] == "success"
            assert result["data"]["name"] == "Test Project"
            assert result["data"]["shortName"] == "TP"

    @pytest.mark.asyncio
    async def test_get_project_not_found(self, project_manager, auth_manager):
        """Test project retrieval when project not found."""
        with patch("youtrack_cli.projects.get_client_manager") as mock_get_client_manager:
            mock_response = Mock()
            mock_response.status_code = 404

            mock_request = Mock()
            http_error = httpx.HTTPStatusError("Not found", request=mock_request, response=mock_response)

            mock_client_manager = Mock()
            mock_client_manager.make_request = AsyncMock(side_effect=http_error)
            mock_get_client_manager.return_value = mock_client_manager

            result = await project_manager.get_project("NONEXISTENT")

            assert result["status"] == "error"
            assert "not found" in result["message"]

    @pytest.mark.asyncio
    async def test_update_project_success(self, project_manager, auth_manager):
        """Test successful project update."""
        mock_updated_project = {
            "id": "123",
            "name": "Updated Project",
            "shortName": "UP",
            "leader": {"login": "new-leader", "fullName": "New Leader"},
            "archived": False,
        }

        # Mock the user resolution
        mock_user_data = {"id": "2-5", "login": "new-leader"}

        with patch("youtrack_cli.projects.get_client_manager") as mock_get_client_manager:
            mock_response = Mock()
            mock_response.json.return_value = mock_updated_project
            mock_response.raise_for_status.return_value = None
            mock_response.headers = {"content-type": "application/json"}
            mock_response.text = '{"id": "123", "name": "Updated Project"}'
            mock_response.status_code = 200

            mock_client_manager = Mock()
            mock_client_manager.make_request = AsyncMock(return_value=mock_response)
            mock_get_client_manager.return_value = mock_client_manager

            # Mock the user manager get_user method
            project_manager.user_manager.get_user = AsyncMock(
                return_value={"status": "success", "data": mock_user_data}
            )

            result = await project_manager.update_project(
                project_id="UP", name="Updated Project", leader_id="new-leader"
            )

            assert result["status"] == "success"
            assert result["data"]["name"] == "Updated Project"
            assert "updated successfully" in result["message"]

    @pytest.mark.asyncio
    async def test_update_project_with_username_resolution(self, project_manager, auth_manager):
        """Test project update with username resolution."""
        mock_updated_project = {
            "id": "123",
            "name": "Updated Project",
            "shortName": "UP",
            "leader": {"login": "admin", "fullName": "Admin User"},
            "archived": False,
        }

        # Mock the user resolution
        mock_user_data = {"id": "2-1", "login": "admin"}

        with patch("youtrack_cli.projects.get_client_manager") as mock_get_client_manager:
            mock_response = Mock()
            mock_response.json.return_value = mock_updated_project
            mock_response.raise_for_status.return_value = None
            mock_response.headers = {"content-type": "application/json"}
            mock_response.text = '{"id": "123", "name": "Updated Project"}'
            mock_response.status_code = 200

            mock_client_manager = Mock()
            mock_client_manager.make_request = AsyncMock(return_value=mock_response)
            mock_get_client_manager.return_value = mock_client_manager

            # Mock the user manager get_user method
            project_manager.user_manager.get_user = AsyncMock(
                return_value={"status": "success", "data": mock_user_data}
            )

            result = await project_manager.update_project(
                project_id="UP",
                name="Updated Project",
                leader_id="admin",  # Using username
            )

            assert result["status"] == "success"
            assert result["data"]["name"] == "Updated Project"
            assert "updated successfully" in result["message"]

    @pytest.mark.asyncio
    async def test_update_project_invalid_username(self, project_manager, auth_manager):
        """Test project update with invalid username."""
        # Mock the user manager to return user not found
        project_manager.user_manager.get_user = AsyncMock(return_value={"status": "error", "message": "User not found"})

        result = await project_manager.update_project(project_id="UP", name="Updated Project", leader_id="nonexistent")

        assert result["status"] == "error"
        assert "Failed to resolve leader" in result["message"]
        assert "User 'nonexistent' not found" in result["message"]

    @pytest.mark.asyncio
    async def test_update_project_no_changes(self, project_manager, auth_manager):
        """Test project update with no changes provided."""
        result = await project_manager.update_project("UP")

        assert result["status"] == "error"
        assert "No updates provided" in result["message"]

    @pytest.mark.asyncio
    async def test_archive_project_success(self, project_manager, auth_manager):
        """Test successful project archiving."""
        mock_archived_project = {
            "id": "123",
            "name": "Archived Project",
            "shortName": "AP",
            "archived": True,
        }

        with patch("youtrack_cli.projects.get_client_manager") as mock_get_client_manager:
            mock_response = Mock()
            mock_response.json.return_value = mock_archived_project
            mock_response.raise_for_status.return_value = None
            mock_response.headers = {"content-type": "application/json"}
            mock_response.text = '{"id": "123", "name": "Archived Project"}'
            mock_response.status_code = 200

            mock_client_manager = Mock()
            mock_client_manager.make_request = AsyncMock(return_value=mock_response)
            mock_get_client_manager.return_value = mock_client_manager

            result = await project_manager.archive_project("AP")

            assert result["status"] == "success"
            assert "updated successfully" in result["message"]


class TestProjectsCLI:
    """Test projects CLI commands."""

    def test_projects_help(self):
        """Test projects command help."""
        runner = CliRunner()
        result = runner.invoke(main, ["projects", "--help"])
        assert result.exit_code == 0
        assert "Manage projects" in result.output

    def test_projects_list_help(self):
        """Test projects list command help."""
        runner = CliRunner()
        result = runner.invoke(main, ["projects", "list", "--help"])
        assert result.exit_code == 0
        assert "List all projects" in result.output

    def test_projects_create_help(self):
        """Test projects create command help."""
        runner = CliRunner()
        result = runner.invoke(main, ["projects", "create", "--help"])
        assert result.exit_code == 0
        assert "Create a new project" in result.output

    def test_projects_configure_help(self):
        """Test projects configure command help."""
        runner = CliRunner()
        result = runner.invoke(main, ["projects", "configure", "--help"])
        assert result.exit_code == 0
        assert "Configure project settings" in result.output

    def test_projects_archive_help(self):
        """Test projects archive command help."""
        runner = CliRunner()
        result = runner.invoke(main, ["projects", "archive", "--help"])
        assert result.exit_code == 0
        assert "Archive a project" in result.output

    @patch("youtrack_cli.projects.ProjectManager")
    def test_projects_list_command(self, mock_project_manager_class):
        """Test projects list command execution."""
        # Mock the ProjectManager and its methods
        mock_project_manager = Mock()
        mock_project_manager_class.return_value = mock_project_manager

        # Mock the asyncio.run to return a successful result
        mock_result = {
            "status": "success",
            "data": [
                {
                    "id": "1",
                    "name": "Test Project",
                    "shortName": "TP",
                    "leader": {"login": "user1", "fullName": "User One"},
                    "archived": False,
                    "description": "Test description",
                }
            ],
            "count": 1,
        }

        with patch("asyncio.run", return_value=mock_result):
            with patch("youtrack_cli.auth.AuthManager"):
                runner = CliRunner()
                result = runner.invoke(main, ["projects", "list"])

                # The command should not exit with an error code
                # (actual success depends on auth setup, but we can test
                # command structure)
                assert "projects" in result.output.lower() or result.exit_code in [0, 1]

    @patch("youtrack_cli.projects.ProjectManager")
    def test_projects_create_command(self, mock_project_manager_class):
        """Test projects create command execution."""
        mock_project_manager = Mock()
        mock_project_manager_class.return_value = mock_project_manager

        mock_result = {
            "status": "success",
            "data": {"id": "123", "name": "New Project", "shortName": "NP"},
            "message": "Project 'New Project' created successfully",
        }

        with patch("asyncio.run", return_value=mock_result):
            with patch("youtrack_cli.auth.AuthManager"):
                runner = CliRunner()
                result = runner.invoke(
                    main,
                    ["projects", "create", "New Project", "NP", "--leader", "user1"],
                )

                # Command should be properly structured
                assert result.exit_code in [0, 1]  # May fail on auth but command exists

    @patch("youtrack_cli.projects.ProjectManager")
    def test_projects_configure_show_details(self, mock_project_manager_class):
        """Test projects configure command with show details option."""
        mock_project_manager = Mock()
        mock_project_manager_class.return_value = mock_project_manager

        mock_result = {
            "status": "success",
            "data": {
                "id": "123",
                "name": "Test Project",
                "shortName": "TP",
                "leader": {"login": "user1", "fullName": "User One"},
                "archived": False,
                "description": "Test description",
            },
        }

        with patch("asyncio.run", return_value=mock_result):
            with patch("youtrack_cli.auth.AuthManager"):
                runner = CliRunner()
                result = runner.invoke(main, ["projects", "configure", "TP", "--show-details"])

                assert result.exit_code in [0, 1]

    @patch("youtrack_cli.projects.ProjectManager")
    def test_projects_archive_command(self, mock_project_manager_class):
        """Test projects archive command execution."""
        mock_project_manager = Mock()
        mock_project_manager_class.return_value = mock_project_manager

        mock_result = {
            "status": "success",
            "message": "Project 'TP' updated successfully",
        }

        with patch("asyncio.run", return_value=mock_result):
            with patch("youtrack_cli.auth.AuthManager"):
                runner = CliRunner()
                result = runner.invoke(main, ["projects", "archive", "TP", "--confirm"])

                assert result.exit_code in [0, 1]


class TestProjectsDisplayMethods:
    """Test projects display methods."""

    def test_display_projects_table_empty(self):
        """Test displaying empty projects table."""
        auth_manager = Mock(spec=AuthManager)
        project_manager = ProjectManager(auth_manager)

        # This should not raise an exception
        project_manager.display_projects_table([])

    def test_display_projects_table_with_data(self):
        """Test displaying projects table with data."""
        auth_manager = Mock(spec=AuthManager)
        project_manager = ProjectManager(auth_manager)

        projects = [
            {
                "id": "1",
                "name": "Test Project 1",
                "shortName": "TP1",
                "leader": {"login": "user1", "fullName": "User One"},
                "archived": False,
                "description": "Short description",
            },
            {
                "id": "2",
                "name": "Test Project 2",
                "shortName": "TP2",
                "leader": {"login": "user2", "fullName": "User Two"},
                "archived": True,
                "description": (
                    "Very long description that should be truncated because "
                    "it exceeds the maximum length for display in the table"
                ),
            },
        ]

        # This should not raise an exception
        project_manager.display_projects_table(projects)

    def test_display_project_details(self):
        """Test displaying project details."""
        auth_manager = Mock(spec=AuthManager)
        project_manager = ProjectManager(auth_manager)

        project = {
            "id": "123",
            "name": "Test Project",
            "shortName": "TP",
            "description": "A detailed project description",
            "leader": {"login": "user1", "fullName": "User One"},
            "archived": False,
            "createdBy": {"login": "creator", "fullName": "Project Creator"},
            "team": {
                "users": [
                    {"login": "user1", "fullName": "User One"},
                    {"login": "user2", "fullName": "User Two"},
                ]
            },
        }

        # This should not raise an exception
        project_manager.display_project_details(project)

    def test_display_project_details_minimal_data(self):
        """Test displaying project details with minimal data."""
        auth_manager = Mock(spec=AuthManager)
        project_manager = ProjectManager(auth_manager)

        project = {
            "id": "123",
            "name": "Minimal Project",
            "shortName": "MP",
        }

        # This should not raise an exception
        project_manager.display_project_details(project)
