"""Tests for ProjectService."""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from youtrack_cli.auth import AuthManager
from youtrack_cli.services.projects import ProjectService


@pytest.fixture
def auth_manager():
    """Create a mock auth manager."""
    mock_auth = MagicMock(spec=AuthManager)
    return mock_auth


@pytest.fixture
def project_service(auth_manager):
    """Create a ProjectService instance."""
    return ProjectService(auth_manager)


@pytest.fixture
def mock_response():
    """Create a mock HTTP response."""
    response = MagicMock(spec=httpx.Response)
    response.status_code = 200
    response.json.return_value = {"id": "PROJECT-1", "name": "Test Project"}
    response.headers = {"content-type": "application/json"}
    response.text = '{"id": "PROJECT-1", "name": "Test Project"}'
    return response


class TestProjectServiceListProjects:
    """Test project listing functionality."""

    @pytest.mark.asyncio
    async def test_list_projects_basic(self, project_service, mock_response):
        """Test basic project listing."""
        with (
            patch.object(project_service, "_make_request", new_callable=AsyncMock) as mock_request,
            patch.object(project_service, "_handle_response", new_callable=AsyncMock) as mock_handle,
        ):
            mock_request.return_value = mock_response
            mock_handle.return_value = {
                "status": "success",
                "data": [
                    {"id": "proj-1", "name": "Project 1", "archived": False},
                    {"id": "proj-2", "name": "Project 2", "archived": True},
                ],
            }

            result = await project_service.list_projects()

            expected_params = {
                "fields": "id,name,shortName,description,leader(login,fullName),archived,createdBy(login,fullName)"
            }
            mock_request.assert_called_once_with("GET", "admin/projects", params=expected_params)
            mock_handle.assert_called_once_with(mock_response)

            # Should filter out archived projects by default
            assert result["status"] == "success"
            assert len(result["data"]) == 1
            assert result["data"][0]["id"] == "proj-1"

    @pytest.mark.asyncio
    async def test_list_projects_with_archived(self, project_service, mock_response):
        """Test listing projects including archived ones."""
        with (
            patch.object(project_service, "_make_request", new_callable=AsyncMock) as mock_request,
            patch.object(project_service, "_handle_response", new_callable=AsyncMock) as mock_handle,
        ):
            mock_request.return_value = mock_response
            mock_handle.return_value = {
                "status": "success",
                "data": [
                    {"id": "proj-1", "name": "Project 1", "archived": False},
                    {"id": "proj-2", "name": "Project 2", "archived": True},
                ],
            }

            result = await project_service.list_projects(show_archived=True)

            # Should include all projects when show_archived=True
            assert result["status"] == "success"
            assert len(result["data"]) == 2

    @pytest.mark.asyncio
    async def test_list_projects_with_parameters(self, project_service, mock_response):
        """Test listing projects with all parameters."""
        with (
            patch.object(project_service, "_make_request", new_callable=AsyncMock) as mock_request,
            patch.object(project_service, "_handle_response", new_callable=AsyncMock) as mock_handle,
        ):
            mock_request.return_value = mock_response
            mock_handle.return_value = {"status": "success", "data": []}

            result = await project_service.list_projects(fields="id,name", top=10, skip=5, show_archived=True)

            expected_params = {"fields": "id,name", "$top": "10", "$skip": "5"}
            mock_request.assert_called_once_with("GET", "admin/projects", params=expected_params)
            assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_list_projects_value_error(self, project_service):
        """Test list projects with ValueError."""
        with (
            patch.object(project_service, "_make_request", new_callable=AsyncMock) as mock_request,
            patch.object(project_service, "_create_error_response") as mock_error,
        ):
            mock_request.side_effect = ValueError("Invalid data")
            mock_error.return_value = {"status": "error", "message": "Invalid data"}

            result = await project_service.list_projects()

            mock_error.assert_called_once_with("Invalid data")
            assert result["status"] == "error"

    @pytest.mark.asyncio
    async def test_list_projects_general_exception(self, project_service):
        """Test list projects with general exception."""
        with (
            patch.object(project_service, "_make_request", new_callable=AsyncMock) as mock_request,
            patch.object(project_service, "_create_error_response") as mock_error,
        ):
            mock_request.side_effect = Exception("Network error")
            mock_error.return_value = {"status": "error", "message": "Error listing projects: Network error"}

            result = await project_service.list_projects()

            mock_error.assert_called_once_with("Error listing projects: Network error")
            assert result["status"] == "error"


class TestProjectServiceGetProject:
    """Test project retrieval functionality."""

    @pytest.mark.asyncio
    async def test_get_project_basic(self, project_service, mock_response):
        """Test basic project retrieval."""
        with (
            patch.object(project_service, "_make_request", new_callable=AsyncMock) as mock_request,
            patch.object(project_service, "_handle_response", new_callable=AsyncMock) as mock_handle,
        ):
            mock_request.return_value = mock_response
            mock_handle.return_value = {"status": "success", "data": {"id": "TEST", "name": "Test Project"}}

            result = await project_service.get_project("TEST")

            expected_params = {
                "fields": "id,name,shortName,description,leader(login,fullName),archived,createdBy(login,fullName),team(users(login,fullName))"
            }
            mock_request.assert_called_once_with("GET", "admin/projects/TEST", params=expected_params)
            mock_handle.assert_called_once_with(mock_response)
            assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_get_project_with_custom_fields(self, project_service, mock_response):
        """Test project retrieval with custom fields."""
        with (
            patch.object(project_service, "_make_request", new_callable=AsyncMock) as mock_request,
            patch.object(project_service, "_handle_response", new_callable=AsyncMock) as mock_handle,
        ):
            mock_request.return_value = mock_response
            mock_handle.return_value = {"status": "success", "data": {"id": "TEST"}}

            result = await project_service.get_project("TEST", fields="id,name")

            expected_params = {"fields": "id,name"}
            mock_request.assert_called_once_with("GET", "admin/projects/TEST", params=expected_params)
            assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_get_project_error_handling(self, project_service):
        """Test get project error handling."""
        with (
            patch.object(project_service, "_make_request", new_callable=AsyncMock) as mock_request,
            patch.object(project_service, "_create_error_response") as mock_error,
        ):
            mock_request.side_effect = Exception("Network error")
            mock_error.return_value = {"status": "error", "message": "Error getting project: Network error"}

            result = await project_service.get_project("TEST")

            mock_error.assert_called_once_with("Error getting project: Network error")
            assert result["status"] == "error"


class TestProjectServiceCreateProject:
    """Test project creation functionality."""

    @pytest.mark.asyncio
    async def test_create_project_basic(self, project_service, mock_response):
        """Test basic project creation."""
        with (
            patch.object(project_service, "_make_request", new_callable=AsyncMock) as mock_request,
            patch.object(project_service, "_handle_response", new_callable=AsyncMock) as mock_handle,
        ):
            mock_request.return_value = mock_response
            mock_handle.return_value = {"status": "success", "data": {"id": "TEST"}}

            result = await project_service.create_project("TEST", "Test Project")

            expected_data = {"shortName": "TEST", "name": "Test Project"}
            mock_request.assert_called_once_with("POST", "admin/projects", json_data=expected_data)
            mock_handle.assert_called_once_with(mock_response, success_codes=[200, 201])
            assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_create_project_with_all_fields(self, project_service, mock_response):
        """Test project creation with all optional fields."""
        with (
            patch.object(project_service, "_make_request", new_callable=AsyncMock) as mock_request,
            patch.object(project_service, "_handle_response", new_callable=AsyncMock) as mock_handle,
        ):
            mock_request.return_value = mock_response
            mock_handle.return_value = {"status": "success"}

            result = await project_service.create_project(
                short_name="TEST", name="Test Project", description="Test Description", leader_login="testuser"
            )

            expected_data = {
                "shortName": "TEST",
                "name": "Test Project",
                "description": "Test Description",
                "leader": {"id": "testuser"},
            }
            mock_request.assert_called_once_with("POST", "admin/projects", json_data=expected_data)
            assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_create_project_error_handling(self, project_service):
        """Test create project error handling."""
        with (
            patch.object(project_service, "_make_request", new_callable=AsyncMock) as mock_request,
            patch.object(project_service, "_create_error_response") as mock_error,
        ):
            mock_request.side_effect = ValueError("Invalid data")
            mock_error.return_value = {"status": "error", "message": "Invalid data"}

            result = await project_service.create_project("TEST", "Test Project")

            mock_error.assert_called_once_with("Invalid data")
            assert result["status"] == "error"


class TestProjectServiceUpdateProject:
    """Test project update functionality."""

    @pytest.mark.asyncio
    async def test_update_project_basic(self, project_service, mock_response):
        """Test basic project update."""
        with (
            patch.object(project_service, "_make_request", new_callable=AsyncMock) as mock_request,
            patch.object(project_service, "_handle_response", new_callable=AsyncMock) as mock_handle,
        ):
            mock_request.return_value = mock_response
            mock_handle.return_value = {"status": "success"}

            result = await project_service.update_project("TEST", name="New Name")

            expected_data = {"name": "New Name"}
            mock_request.assert_called_once_with("POST", "admin/projects/TEST", json_data=expected_data)
            mock_handle.assert_called_once_with(mock_response)
            assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_update_project_all_fields(self, project_service, mock_response):
        """Test project update with all fields."""
        with (
            patch.object(project_service, "_make_request", new_callable=AsyncMock) as mock_request,
            patch.object(project_service, "_handle_response", new_callable=AsyncMock) as mock_handle,
        ):
            mock_request.return_value = mock_response
            mock_handle.return_value = {"status": "success"}

            result = await project_service.update_project(
                "TEST", name="New Name", description="New Description", leader_login="newuser", archived=True
            )

            expected_data = {
                "name": "New Name",
                "description": "New Description",
                "leader": {"id": "newuser"},
                "archived": True,
            }
            mock_request.assert_called_once_with("POST", "admin/projects/TEST", json_data=expected_data)
            assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_update_project_error_handling(self, project_service):
        """Test update project error handling."""
        with (
            patch.object(project_service, "_make_request", new_callable=AsyncMock) as mock_request,
            patch.object(project_service, "_create_error_response") as mock_error,
        ):
            mock_request.side_effect = Exception("Network error")
            mock_error.return_value = {"status": "error", "message": "Error updating project: Network error"}

            result = await project_service.update_project("TEST", name="New Name")

            mock_error.assert_called_once_with("Error updating project: Network error")
            assert result["status"] == "error"


class TestProjectServiceDeleteProject:
    """Test project deletion functionality."""

    @pytest.mark.asyncio
    async def test_delete_project(self, project_service, mock_response):
        """Test project deletion."""
        with (
            patch.object(project_service, "_make_request", new_callable=AsyncMock) as mock_request,
            patch.object(project_service, "_handle_response", new_callable=AsyncMock) as mock_handle,
        ):
            mock_request.return_value = mock_response
            mock_handle.return_value = {"status": "success"}

            result = await project_service.delete_project("TEST")

            mock_request.assert_called_once_with("DELETE", "admin/projects/TEST")
            mock_handle.assert_called_once_with(mock_response)
            assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_delete_project_error_handling(self, project_service):
        """Test delete project error handling."""
        with (
            patch.object(project_service, "_make_request", new_callable=AsyncMock) as mock_request,
            patch.object(project_service, "_create_error_response") as mock_error,
        ):
            mock_request.side_effect = ValueError("Invalid ID")
            mock_error.return_value = {"status": "error", "message": "Invalid ID"}

            result = await project_service.delete_project("TEST")

            mock_error.assert_called_once_with("Invalid ID")
            assert result["status"] == "error"


class TestProjectServiceArchive:
    """Test project archiving functionality."""

    @pytest.mark.asyncio
    async def test_archive_project(self, project_service, mock_response):
        """Test archiving a project."""
        with (
            patch.object(project_service, "_make_request", new_callable=AsyncMock) as mock_request,
            patch.object(project_service, "_handle_response", new_callable=AsyncMock) as mock_handle,
        ):
            mock_request.return_value = mock_response
            mock_handle.return_value = {"status": "success"}

            result = await project_service.archive_project("TEST")

            expected_data = {"archived": True}
            mock_request.assert_called_once_with("POST", "admin/projects/TEST", json_data=expected_data)
            mock_handle.assert_called_once_with(mock_response)
            assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_unarchive_project(self, project_service, mock_response):
        """Test unarchiving a project."""
        with (
            patch.object(project_service, "_make_request", new_callable=AsyncMock) as mock_request,
            patch.object(project_service, "_handle_response", new_callable=AsyncMock) as mock_handle,
        ):
            mock_request.return_value = mock_response
            mock_handle.return_value = {"status": "success"}

            result = await project_service.unarchive_project("TEST")

            expected_data = {"archived": False}
            mock_request.assert_called_once_with("POST", "admin/projects/TEST", json_data=expected_data)
            mock_handle.assert_called_once_with(mock_response)
            assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_archive_project_error_handling(self, project_service):
        """Test archive project error handling."""
        with (
            patch.object(project_service, "_make_request", new_callable=AsyncMock) as mock_request,
            patch.object(project_service, "_create_error_response") as mock_error,
        ):
            mock_request.side_effect = Exception("Network error")
            mock_error.return_value = {"status": "error", "message": "Error archiving project: Network error"}

            result = await project_service.archive_project("TEST")

            mock_error.assert_called_once_with("Error archiving project: Network error")
            assert result["status"] == "error"

    @pytest.mark.asyncio
    async def test_unarchive_project_error_handling(self, project_service):
        """Test unarchive project error handling."""
        with (
            patch.object(project_service, "_make_request", new_callable=AsyncMock) as mock_request,
            patch.object(project_service, "_create_error_response") as mock_error,
        ):
            mock_request.side_effect = Exception("Network error")
            mock_error.return_value = {"status": "error", "message": "Error unarchiving project: Network error"}

            result = await project_service.unarchive_project("TEST")

            mock_error.assert_called_once_with("Error unarchiving project: Network error")
            assert result["status"] == "error"


class TestProjectServiceTeam:
    """Test project team management functionality."""

    @pytest.mark.asyncio
    async def test_get_project_team(self, project_service, mock_response):
        """Test getting project team."""
        with (
            patch.object(project_service, "_make_request", new_callable=AsyncMock) as mock_request,
            patch.object(project_service, "_handle_response", new_callable=AsyncMock) as mock_handle,
        ):
            mock_request.return_value = mock_response
            mock_handle.return_value = {"status": "success", "data": []}

            result = await project_service.get_project_team("TEST")

            expected_params = {"fields": "login,fullName,email,avatarUrl"}
            mock_request.assert_called_once_with("GET", "admin/projects/TEST/team", params=expected_params)
            mock_handle.assert_called_once_with(mock_response)
            assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_get_project_team_custom_fields(self, project_service, mock_response):
        """Test getting project team with custom fields."""
        with (
            patch.object(project_service, "_make_request", new_callable=AsyncMock) as mock_request,
            patch.object(project_service, "_handle_response", new_callable=AsyncMock) as mock_handle,
        ):
            mock_request.return_value = mock_response
            mock_handle.return_value = {"status": "success", "data": []}

            result = await project_service.get_project_team("TEST", fields="login,fullName")

            expected_params = {"fields": "login,fullName"}
            mock_request.assert_called_once_with("GET", "admin/projects/TEST/team", params=expected_params)
            assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_add_team_member(self, project_service, mock_response):
        """Test adding a team member."""
        with (
            patch.object(project_service, "_make_request", new_callable=AsyncMock) as mock_request,
            patch.object(project_service, "_handle_response", new_callable=AsyncMock) as mock_handle,
        ):
            mock_request.return_value = mock_response
            mock_handle.return_value = {"status": "success"}

            result = await project_service.add_team_member("TEST", "testuser")

            expected_data = {"login": "testuser"}
            mock_request.assert_called_once_with("POST", "admin/projects/TEST/team", json_data=expected_data)
            mock_handle.assert_called_once_with(mock_response, success_codes=[200, 201])
            assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_remove_team_member(self, project_service, mock_response):
        """Test removing a team member."""
        with (
            patch.object(project_service, "_make_request", new_callable=AsyncMock) as mock_request,
            patch.object(project_service, "_handle_response", new_callable=AsyncMock) as mock_handle,
        ):
            mock_request.return_value = mock_response
            mock_handle.return_value = {"status": "success"}

            result = await project_service.remove_team_member("TEST", "testuser")

            mock_request.assert_called_once_with("DELETE", "admin/projects/TEST/team/testuser")
            mock_handle.assert_called_once_with(mock_response)
            assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_team_management_error_handling(self, project_service):
        """Test team management error handling."""
        with (
            patch.object(project_service, "_make_request", new_callable=AsyncMock) as mock_request,
            patch.object(project_service, "_create_error_response") as mock_error,
        ):
            mock_request.side_effect = Exception("Network error")
            mock_error.return_value = {"status": "error", "message": "Error getting project team: Network error"}

            result = await project_service.get_project_team("TEST")

            mock_error.assert_called_once_with("Error getting project team: Network error")
            assert result["status"] == "error"


class TestProjectServiceCustomFields:
    """Test project custom fields functionality."""

    @pytest.mark.asyncio
    async def test_get_project_custom_fields(self, project_service, mock_response):
        """Test getting project custom fields."""
        with (
            patch.object(project_service, "_make_request", new_callable=AsyncMock) as mock_request,
            patch.object(project_service, "_handle_response", new_callable=AsyncMock) as mock_handle,
        ):
            mock_request.return_value = mock_response
            mock_handle.return_value = {"status": "success", "data": []}

            result = await project_service.get_project_custom_fields("TEST")

            expected_params = {"fields": "id,field(name,fieldType),canBeEmpty,isPublic,ordinal"}
            mock_request.assert_called_once_with("GET", "admin/projects/TEST/customFields", params=expected_params)
            mock_handle.assert_called_once_with(mock_response)
            assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_attach_custom_field(self, project_service, mock_response):
        """Test attaching a custom field."""
        with (
            patch.object(project_service, "_make_request", new_callable=AsyncMock) as mock_request,
            patch.object(project_service, "_handle_response", new_callable=AsyncMock) as mock_handle,
        ):
            mock_request.return_value = mock_response
            mock_handle.return_value = {"status": "success"}

            result = await project_service.attach_custom_field("TEST", "field-1", is_public=True)

            expected_data = {"field": {"id": "field-1"}, "isPublic": True}
            mock_request.assert_called_once_with("POST", "admin/projects/TEST/customFields", json_data=expected_data)
            mock_handle.assert_called_once_with(mock_response, success_codes=[200, 201])
            assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_attach_custom_field_minimal(self, project_service, mock_response):
        """Test attaching a custom field with minimal parameters."""
        with (
            patch.object(project_service, "_make_request", new_callable=AsyncMock) as mock_request,
            patch.object(project_service, "_handle_response", new_callable=AsyncMock) as mock_handle,
        ):
            mock_request.return_value = mock_response
            mock_handle.return_value = {"status": "success"}

            result = await project_service.attach_custom_field("TEST", "field-1")

            expected_data = {"field": {"id": "field-1"}}
            mock_request.assert_called_once_with("POST", "admin/projects/TEST/customFields", json_data=expected_data)
            assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_detach_custom_field(self, project_service, mock_response):
        """Test detaching a custom field."""
        with (
            patch.object(project_service, "_make_request", new_callable=AsyncMock) as mock_request,
            patch.object(project_service, "_handle_response", new_callable=AsyncMock) as mock_handle,
        ):
            mock_request.return_value = mock_response
            mock_handle.return_value = {"status": "success"}

            result = await project_service.detach_custom_field("TEST", "field-1")

            mock_request.assert_called_once_with("DELETE", "admin/projects/TEST/customFields/field-1")
            mock_handle.assert_called_once_with(mock_response)
            assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_custom_fields_error_handling(self, project_service):
        """Test custom fields error handling."""
        with (
            patch.object(project_service, "_make_request", new_callable=AsyncMock) as mock_request,
            patch.object(project_service, "_create_error_response") as mock_error,
        ):
            mock_request.side_effect = Exception("Network error")
            mock_error.return_value = {
                "status": "error",
                "message": "Error getting project custom fields: Network error",
            }

            result = await project_service.get_project_custom_fields("TEST")

            mock_error.assert_called_once_with("Error getting project custom fields: Network error")
            assert result["status"] == "error"


class TestProjectServiceVersions:
    """Test project versions functionality."""

    @pytest.mark.asyncio
    async def test_get_project_versions(self, project_service, mock_response):
        """Test getting project versions."""
        with (
            patch.object(project_service, "_make_request", new_callable=AsyncMock) as mock_request,
            patch.object(project_service, "_handle_response", new_callable=AsyncMock) as mock_handle,
        ):
            mock_request.return_value = mock_response
            mock_handle.return_value = {"status": "success", "data": []}

            result = await project_service.get_project_versions("TEST")

            expected_params = {"fields": "id,name,description,archived,released,releaseDate"}
            mock_request.assert_called_once_with("GET", "admin/projects/TEST/versions", params=expected_params)
            mock_handle.assert_called_once_with(mock_response)
            assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_get_project_versions_custom_fields(self, project_service, mock_response):
        """Test getting project versions with custom fields."""
        with (
            patch.object(project_service, "_make_request", new_callable=AsyncMock) as mock_request,
            patch.object(project_service, "_handle_response", new_callable=AsyncMock) as mock_handle,
        ):
            mock_request.return_value = mock_response
            mock_handle.return_value = {"status": "success", "data": []}

            result = await project_service.get_project_versions("TEST", fields="id,name")

            expected_params = {"fields": "id,name"}
            mock_request.assert_called_once_with("GET", "admin/projects/TEST/versions", params=expected_params)
            assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_create_project_version_basic(self, project_service, mock_response):
        """Test creating a project version."""
        with (
            patch.object(project_service, "_make_request", new_callable=AsyncMock) as mock_request,
            patch.object(project_service, "_handle_response", new_callable=AsyncMock) as mock_handle,
        ):
            mock_request.return_value = mock_response
            mock_handle.return_value = {"status": "success"}

            result = await project_service.create_project_version("TEST", "v1.0")

            expected_data = {"name": "v1.0"}
            mock_request.assert_called_once_with("POST", "admin/projects/TEST/versions", json_data=expected_data)
            mock_handle.assert_called_once_with(mock_response, success_codes=[200, 201])
            assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_create_project_version_all_fields(self, project_service, mock_response):
        """Test creating a project version with all fields."""
        with (
            patch.object(project_service, "_make_request", new_callable=AsyncMock) as mock_request,
            patch.object(project_service, "_handle_response", new_callable=AsyncMock) as mock_handle,
        ):
            mock_request.return_value = mock_response
            mock_handle.return_value = {"status": "success"}

            result = await project_service.create_project_version(
                "TEST", "v1.0", description="First version", released=True, archived=False
            )

            expected_data = {"name": "v1.0", "description": "First version", "released": True, "archived": False}
            mock_request.assert_called_once_with("POST", "admin/projects/TEST/versions", json_data=expected_data)
            assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_versions_error_handling(self, project_service):
        """Test versions error handling."""
        with (
            patch.object(project_service, "_make_request", new_callable=AsyncMock) as mock_request,
            patch.object(project_service, "_create_error_response") as mock_error,
        ):
            mock_request.side_effect = Exception("Network error")
            mock_error.return_value = {"status": "error", "message": "Error getting project versions: Network error"}

            result = await project_service.get_project_versions("TEST")

            mock_error.assert_called_once_with("Error getting project versions: Network error")
            assert result["status"] == "error"
