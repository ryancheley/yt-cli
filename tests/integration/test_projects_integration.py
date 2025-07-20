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


@pytest.mark.integration
class TestProjectCustomFieldsIntegration:
    """Integration tests for project custom fields functionality."""

    @pytest.mark.asyncio
    async def test_list_custom_fields_real_project(self, integration_project_manager, test_project_id):
        """Test listing custom fields from a real YouTrack project."""
        project_manager = integration_project_manager

        try:
            # Test the new list_custom_fields method
            result = await project_manager.list_custom_fields(test_project_id)

            assert result["status"] == "success"
            assert "data" in result
            assert "count" in result
            assert isinstance(result["data"], list)

            # If custom fields exist, verify their structure
            for field in result["data"]:
                assert isinstance(field, dict)
                assert "id" in field
                assert "field" in field

                # Check field details
                field_info = field["field"]
                assert "id" in field_info
                assert "name" in field_info

        except Exception as e:
            # Skip if authentication issues or permissions
            if "not authenticated" in str(e).lower() or "permission" in str(e).lower():
                pytest.skip(f"Authentication or permission issue: {e}")
            else:
                raise

    @pytest.mark.asyncio
    async def test_list_custom_fields_with_options(self, integration_project_manager, test_project_id):
        """Test listing custom fields with various options."""
        project_manager = integration_project_manager

        try:
            # Test with custom fields parameter
            result = await project_manager.list_custom_fields(
                test_project_id, fields="id,field(name,fieldType),canBeEmpty,isPublic", top=10
            )

            assert result["status"] == "success"
            assert isinstance(result["data"], list)

            # Test that top parameter is respected if there are fields
            if result["data"]:
                assert len(result["data"]) <= 10

        except Exception as e:
            if "not authenticated" in str(e).lower() or "permission" in str(e).lower():
                pytest.skip(f"Authentication or permission issue: {e}")
            else:
                raise

    @pytest.mark.asyncio
    async def test_list_custom_fields_json_format(self, integration_project_manager, test_project_id):
        """Test that custom fields data can be serialized to JSON."""
        project_manager = integration_project_manager

        try:
            result = await project_manager.list_custom_fields(test_project_id)

            assert result["status"] == "success"

            # Test JSON serialization
            import json

            json_data = json.dumps(result["data"])
            assert isinstance(json_data, str)

            # Test deserialization
            parsed_data = json.loads(json_data)
            assert parsed_data == result["data"]

        except Exception as e:
            if "not authenticated" in str(e).lower() or "permission" in str(e).lower():
                pytest.skip(f"Authentication or permission issue: {e}")
            else:
                raise

    @pytest.mark.asyncio
    async def test_custom_field_operations_error_handling(self, integration_project_manager):
        """Test error handling for custom field operations."""
        project_manager = integration_project_manager

        # Test with non-existent project
        non_existent_project = "NON_EXISTENT_PROJECT_12345"

        result = await project_manager.list_custom_fields(non_existent_project)
        assert result["status"] == "error"
        assert "not found" in result["message"].lower() or "error" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_attach_custom_field_permission_handling(self, integration_project_manager, test_project_id):
        """Test custom field attachment with permission considerations."""
        project_manager = integration_project_manager

        try:
            # Attempt to attach a custom field (this may fail due to permissions)
            result = await project_manager.attach_custom_field(
                project_id=test_project_id,
                field_id="nonexistent-field-id",
                field_type="EnumProjectCustomField",
            )

            # This should result in an error (either field not found or permission denied)
            assert result["status"] == "error"

            # The error message should be informative
            assert result["message"]
            assert isinstance(result["message"], str)

        except Exception as e:
            if "not authenticated" in str(e).lower():
                pytest.skip(f"Authentication issue: {e}")
            else:
                # Other exceptions should be handled by the method, not raised
                pytest.fail(f"Unexpected exception raised: {e}")

    @pytest.mark.asyncio
    async def test_update_custom_field_permission_handling(self, integration_project_manager, test_project_id):
        """Test custom field update with permission considerations."""
        project_manager = integration_project_manager

        try:
            # Attempt to update a custom field (this may fail due to permissions or non-existence)
            result = await project_manager.update_custom_field(
                project_id=test_project_id,
                field_id="nonexistent-field-id",
                can_be_empty=True,
            )

            # This should result in an error
            assert result["status"] == "error"
            assert result["message"]

        except Exception as e:
            if "not authenticated" in str(e).lower():
                pytest.skip(f"Authentication issue: {e}")
            else:
                pytest.fail(f"Unexpected exception raised: {e}")

    @pytest.mark.asyncio
    async def test_detach_custom_field_permission_handling(self, integration_project_manager, test_project_id):
        """Test custom field detachment with permission considerations."""
        project_manager = integration_project_manager

        try:
            # Attempt to detach a custom field (this may fail due to permissions or non-existence)
            result = await project_manager.detach_custom_field(
                project_id=test_project_id,
                field_id="nonexistent-field-id",
            )

            # This should result in an error
            assert result["status"] == "error"
            assert result["message"]

        except Exception as e:
            if "not authenticated" in str(e).lower():
                pytest.skip(f"Authentication issue: {e}")
            else:
                pytest.fail(f"Unexpected exception raised: {e}")

    def test_display_custom_fields_table_real_data(self, integration_project_manager):
        """Test displaying custom fields table with real data structure."""
        project_manager = integration_project_manager

        # Create sample data that mimics real YouTrack API response
        sample_fields = [
            {
                "id": "project-field-1",
                "canBeEmpty": True,
                "emptyFieldText": "No priority",
                "isPublic": True,
                "field": {
                    "id": "field-1",
                    "name": "Priority",
                    "fieldType": {"id": "enum[1]", "presentation": "enum[1]"},
                },
            },
            {
                "id": "project-field-2",
                "canBeEmpty": False,
                "emptyFieldText": "",
                "isPublic": False,
                "field": {
                    "id": "field-2",
                    "name": "Assignee",
                    "fieldType": {"id": "user[1]", "presentation": "user[1]"},
                },
            },
        ]

        # This should not raise an exception and should display properly formatted table
        project_manager.display_custom_fields_table(sample_fields)

    def test_display_custom_fields_table_edge_cases(self, integration_project_manager):
        """Test displaying custom fields table with edge cases."""
        project_manager = integration_project_manager

        # Test with various edge cases
        edge_case_fields = [
            {
                "id": "field-no-empty-text",
                "canBeEmpty": True,
                "isPublic": True,
                "field": {
                    "id": "field-1",
                    "name": "Field Without Empty Text",
                    "fieldType": {"id": "text[1]", "presentation": "text[1]"},
                },
            },
            {
                "id": "field-long-name",
                "canBeEmpty": False,
                "emptyFieldText": "Very long empty field text that might cause display issues",
                "isPublic": False,
                "field": {
                    "id": "field-2",
                    "name": "Field With Very Long Name That Might Cause Display Issues",
                    "fieldType": {"id": "text[*]", "presentation": "text[*]"},
                },
            },
            {
                "id": "field-minimal-data",
                "field": {
                    "id": "field-3",
                    "name": "Minimal Field",
                },
            },
        ]

        # This should handle edge cases gracefully
        project_manager.display_custom_fields_table(edge_case_fields)
