"""Tests for ProjectService."""

from unittest.mock import MagicMock, Mock, patch

import pytest

from youtrack_cli.services.projects import ProjectService


class TestProjectService:
    """Test cases for ProjectService."""

    @pytest.fixture
    def mock_auth_manager(self):
        """Create mock auth manager."""
        return MagicMock()

    @pytest.fixture
    def project_service(self, mock_auth_manager):
        """Create ProjectService instance."""
        return ProjectService(mock_auth_manager)

    def test_init(self, mock_auth_manager):
        """Test ProjectService initialization."""
        service = ProjectService(mock_auth_manager)
        assert service.auth_manager == mock_auth_manager

    @pytest.mark.asyncio
    async def test_create_project_success(self, project_service):
        """Test create_project with successful response."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": "TEST", "name": "Test Project"}

        with (
            patch.object(project_service, "_make_request", return_value=mock_response),
            patch.object(
                project_service, "_handle_response", return_value={"status": "success", "data": {"id": "TEST"}}
            ),
        ):
            result = await project_service.create_project(short_name="TEST", name="Test Project")

            assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_get_project_success(self, project_service):
        """Test get_project with successful response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "TEST", "name": "Test Project"}

        with (
            patch.object(project_service, "_make_request", return_value=mock_response),
            patch.object(
                project_service, "_handle_response", return_value={"status": "success", "data": {"id": "TEST"}}
            ),
        ):
            result = await project_service.get_project("TEST")

            assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_list_projects_success(self, project_service):
        """Test list_projects with successful response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"id": "TEST", "name": "Test Project"}]

        with (
            patch.object(project_service, "_make_request", return_value=mock_response),
            patch.object(
                project_service, "_handle_response", return_value={"status": "success", "data": [{"id": "TEST"}]}
            ),
        ):
            result = await project_service.list_projects()

            assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_update_project_success(self, project_service):
        """Test update_project with successful response."""
        mock_response = Mock()
        mock_response.status_code = 200

        with (
            patch.object(project_service, "_make_request", return_value=mock_response),
            patch.object(project_service, "_handle_response", return_value={"status": "success", "data": None}),
        ):
            result = await project_service.update_project("TEST", name="Updated Project")

            assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_delete_project_success(self, project_service):
        """Test delete_project with successful response."""
        mock_response = Mock()
        mock_response.status_code = 200

        with (
            patch.object(project_service, "_make_request", return_value=mock_response),
            patch.object(project_service, "_handle_response", return_value={"status": "success", "data": None}),
        ):
            result = await project_service.delete_project("TEST")

            assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_archive_project_success(self, project_service):
        """Test archive_project with successful response."""
        mock_response = Mock()
        mock_response.status_code = 200

        with (
            patch.object(project_service, "_make_request", return_value=mock_response),
            patch.object(project_service, "_handle_response", return_value={"status": "success", "data": None}),
        ):
            result = await project_service.archive_project("TEST")

            assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_get_project_custom_fields_success(self, project_service):
        """Test get_project_custom_fields with successful response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"id": "field1", "name": "Priority"}]

        with (
            patch.object(project_service, "_make_request", return_value=mock_response),
            patch.object(
                project_service, "_handle_response", return_value={"status": "success", "data": [{"id": "field1"}]}
            ),
        ):
            result = await project_service.get_project_custom_fields("TEST")

            assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_attach_custom_field_success(self, project_service):
        """Test attach_custom_field with successful response."""
        mock_response = Mock()
        mock_response.status_code = 200

        with (
            patch.object(project_service, "_make_request", return_value=mock_response),
            patch.object(project_service, "_handle_response", return_value={"status": "success", "data": None}),
        ):
            result = await project_service.attach_custom_field("TEST", "field1")

            assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_create_project_error(self, project_service):
        """Test create_project with error response."""
        with patch.object(project_service, "_make_request", side_effect=Exception("API Error")):
            result = await project_service.create_project(short_name="TEST", name="Test Project")

            assert result["status"] == "error"
            assert "API Error" in result["message"]
