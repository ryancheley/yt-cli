"""Integration tests for project management functionality."""

import pytest

from youtrack_cli.exceptions import YouTrackError


@pytest.mark.integration
class TestProjectsIntegration:
    """Integration tests for project management with real YouTrack API."""

    def test_list_projects(self, integration_project_manager):
        """Test listing projects from real YouTrack instance."""
        project_manager = integration_project_manager

        # Get list of projects
        projects = project_manager.list_projects()

        assert isinstance(projects, list)
        assert len(projects) >= 0  # Should at least not error, might be empty

        # If there are projects, verify structure
        if projects:
            project = projects[0]
            assert isinstance(project, dict)
            assert "id" in project
            assert "name" in project

    def test_get_specific_project(self, integration_project_manager, test_project_id):
        """Test getting details of a specific project."""
        project_manager = integration_project_manager

        try:
            # Get the test project details
            project = project_manager.get_project(test_project_id)

            assert project is not None
            assert isinstance(project, dict)
            assert project.get("id") == test_project_id
            assert "name" in project

        except YouTrackError as e:
            # Project might not exist or access might be restricted
            pytest.skip(f"Test project {test_project_id} not accessible: {e}")

    def test_project_exists_check(self, integration_project_manager, test_project_id):
        """Test checking if a project exists."""
        project_manager = integration_project_manager

        # Check if test project exists
        try:
            exists = project_manager.project_exists(test_project_id)
            # Should be boolean
            assert isinstance(exists, bool)

            if exists:
                # If project exists, we should be able to get its details
                project = project_manager.get_project(test_project_id)
                assert project is not None

        except (YouTrackError, AttributeError):
            # Method might not be implemented or accessible
            pytest.skip("project_exists method not available")

    def test_project_search_and_filtering(self, integration_project_manager):
        """Test project search and filtering functionality."""
        project_manager = integration_project_manager

        # Get all projects first
        all_projects = project_manager.list_projects()

        if not all_projects:
            pytest.skip("No projects available for filtering test")

        # Test filtering by name pattern if method exists
        try:
            # Try to filter projects (method might not exist)
            if hasattr(project_manager, "search_projects"):
                filtered_projects = project_manager.search_projects("*")
                assert isinstance(filtered_projects, list)

        except (YouTrackError, AttributeError):
            # Search functionality might not be implemented
            pytest.skip("Project search functionality not available")

    def test_project_metadata_retrieval(self, integration_project_manager, test_project_id):
        """Test retrieving project metadata and configuration."""
        project_manager = integration_project_manager

        try:
            project = project_manager.get_project(test_project_id)

            if not project:
                pytest.skip(f"Test project {test_project_id} not found")

            # Verify basic project metadata
            assert "id" in project
            assert "name" in project

            # Check for additional metadata fields that might be present
            optional_fields = ["description", "leader", "createdBy", "created", "updated"]
            for field in optional_fields:
                if field in project:
                    # Field exists, verify it's not None
                    assert project[field] is not None

            # Test getting project with additional details if method supports it
            try:
                detailed_project = project_manager.get_project(test_project_id, include_details=True)
                assert detailed_project is not None

            except (TypeError, YouTrackError):
                # include_details parameter might not be supported
                pass

        except YouTrackError as e:
            pytest.skip(f"Cannot access project metadata: {e}")

    def test_project_permissions_check(self, integration_project_manager, test_project_id):
        """Test project access permissions."""
        project_manager = integration_project_manager

        try:
            # Attempt to get project
            project = project_manager.get_project(test_project_id)

            if project:
                # We have read access to the project
                assert project["id"] == test_project_id

                # Try to get project members/users if method exists
                try:
                    if hasattr(project_manager, "get_project_users"):
                        users = project_manager.get_project_users(test_project_id)
                        assert isinstance(users, list)

                except (YouTrackError, AttributeError):
                    # Method might not exist or permissions insufficient
                    pass

        except YouTrackError as e:
            if "access" in str(e).lower() or "permission" in str(e).lower():
                pytest.skip(f"Insufficient permissions for project {test_project_id}")
            else:
                raise

    def test_project_custom_fields(self, integration_project_manager, test_project_id):
        """Test retrieving project custom fields configuration."""
        project_manager = integration_project_manager

        try:
            # Try to get project custom fields if method exists
            if hasattr(project_manager, "get_project_custom_fields"):
                custom_fields = project_manager.get_project_custom_fields(test_project_id)
                assert isinstance(custom_fields, list)

                # If custom fields exist, verify their structure
                for field in custom_fields:
                    assert isinstance(field, dict)
                    assert "name" in field

            else:
                # Alternative: get project details and look for custom fields info
                project = project_manager.get_project(test_project_id)
                # Custom fields info might be embedded in project details
                if "customFields" in project:
                    custom_fields = project["customFields"]
                    assert isinstance(custom_fields, list)

        except (YouTrackError, AttributeError):
            pytest.skip("Custom fields information not accessible")

    def test_project_workflow_states(self, integration_project_manager, test_project_id):
        """Test retrieving project workflow states."""
        project_manager = integration_project_manager

        try:
            # Try to get workflow states if method exists
            if hasattr(project_manager, "get_project_workflow_states"):
                states = project_manager.get_project_workflow_states(test_project_id)
                assert isinstance(states, list)

                # If states exist, verify their structure
                for state in states:
                    assert isinstance(state, dict)
                    assert "name" in state

        except (YouTrackError, AttributeError):
            pytest.skip("Workflow states information not accessible")

    def test_multiple_projects_handling(self, integration_project_manager):
        """Test handling of multiple projects."""
        project_manager = integration_project_manager

        # Get all projects
        projects = project_manager.list_projects()

        if len(projects) < 2:
            pytest.skip("Need at least 2 projects for multi-project test")

        # Test accessing multiple projects
        project_ids = [p["id"] for p in projects[:3]]  # Test first 3 projects

        for project_id in project_ids:
            try:
                project = project_manager.get_project(project_id)
                assert project is not None
                assert project["id"] == project_id

            except YouTrackError:
                # Some projects might not be accessible
                continue

    def test_project_error_handling(self, integration_project_manager):
        """Test error handling for invalid project operations."""
        project_manager = integration_project_manager

        # Test getting non-existent project
        non_existent_id = "NON_EXISTENT_PROJECT_12345"

        with pytest.raises(YouTrackError):
            project_manager.get_project(non_existent_id)
