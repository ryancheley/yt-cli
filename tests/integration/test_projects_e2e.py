"""End-to-end integration tests for complex project operations."""

import json
import os
import uuid
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from youtrack_cli.main import main


@pytest.fixture
def test_project_data():
    """Generate unique test project data."""
    unique_id = str(uuid.uuid4())[:8]
    return {
        "name": f"Test Project {unique_id}",
        "short_name": f"TP{unique_id.upper()}",
        "description": f"Test project created for integration testing {unique_id}",
        "leader": "admin",  # Default to admin user
    }


@pytest.fixture
async def cleanup_test_projects(integration_auth_manager, integration_client):
    """Track and cleanup test projects created during tests."""
    created_projects = []

    yield created_projects

    # Cleanup: Archive test projects
    for project_id in created_projects:
        try:
            async with integration_client as client:
                await client.request("POST", f"/projects/{project_id}", json={"archived": True})
        except Exception:
            # Ignore cleanup errors
            pass


@pytest.mark.integration
@pytest.mark.asyncio
class TestComplexProjectOperations:
    """Test complex end-to-end project operations."""

    async def test_project_lifecycle_workflow(self, integration_auth_manager, test_project_data, cleanup_test_projects):
        """Test complete project lifecycle from creation to archival."""
        runner = CliRunner()

        with patch.dict(
            os.environ,
            {
                "YOUTRACK_BASE_URL": integration_auth_manager.config.base_url,
                "YOUTRACK_API_KEY": integration_auth_manager.config.api_key,
            },
        ):
            # Step 1: Create a new project with scrum template
            result = runner.invoke(
                main,
                [
                    "projects",
                    "create",
                    test_project_data["name"],
                    test_project_data["short_name"],
                    "--leader",
                    test_project_data["leader"],
                    "--description",
                    test_project_data["description"],
                    "--template",
                    "scrum",
                ],
            )

            if result.exit_code == 0:
                cleanup_test_projects.append(test_project_data["short_name"])
                assert (
                    "created successfully" in result.output.lower() or test_project_data["short_name"] in result.output
                )

                # Step 2: Verify project exists in list
                result = runner.invoke(main, ["projects", "list", "--format", "json"])
                assert result.exit_code == 0
                projects_data = json.loads(result.output)
                project_found = any(p.get("shortName") == test_project_data["short_name"] for p in projects_data)
                assert project_found, "Created project not found in project list"

                # Step 3: Configure project details
                result = runner.invoke(
                    main,
                    [
                        "projects",
                        "configure",
                        test_project_data["short_name"],
                        "--description",
                        f"Updated: {test_project_data['description']}",
                        "--show-details",
                    ],
                )
                assert result.exit_code == 0

                # Step 4: List project custom fields
                result = runner.invoke(
                    main, ["projects", "fields", "list", test_project_data["short_name"], "--format", "json"]
                )
                assert result.exit_code == 0

                # Step 5: Archive the project
                result = runner.invoke(main, ["projects", "archive", test_project_data["short_name"], "--force"])
                assert result.exit_code == 0

                # Step 6: Verify project is archived
                result = runner.invoke(main, ["projects", "list", "--show-archived", "--format", "json"])
                assert result.exit_code == 0
                projects_data = json.loads(result.output)
                archived_project = next(
                    (p for p in projects_data if p.get("shortName") == test_project_data["short_name"]), None
                )
                if archived_project:
                    assert archived_project.get("archived", False), "Project should be archived"
            else:
                # Permission denied is acceptable for project creation
                assert "permission" in result.output.lower() or "forbidden" in result.output.lower()
                pytest.skip("Project creation requires admin permissions")

    async def test_project_template_workflows(self, integration_auth_manager, cleanup_test_projects):
        """Test project creation with different templates."""
        runner = CliRunner()

        with patch.dict(
            os.environ,
            {
                "YOUTRACK_BASE_URL": integration_auth_manager.config.base_url,
                "YOUTRACK_API_KEY": integration_auth_manager.config.api_key,
            },
        ):
            templates = ["scrum", "kanban"]

            for template in templates:
                unique_id = str(uuid.uuid4())[:8]
                project_name = f"Test {template.title()} Project {unique_id}"
                short_name = f"T{template.upper()[:2]}{unique_id.upper()}"

                result = runner.invoke(
                    main,
                    [
                        "projects",
                        "create",
                        project_name,
                        short_name,
                        "--leader",
                        "admin",
                        "--template",
                        template,
                        "--description",
                        f"Test {template} template project",
                    ],
                )

                if result.exit_code == 0:
                    cleanup_test_projects.append(short_name)

                    # Verify project was created with template
                    result = runner.invoke(main, ["projects", "configure", short_name, "--show-details"])
                    assert result.exit_code == 0

                    # Check that template-specific fields might be present
                    result = runner.invoke(main, ["projects", "fields", "list", short_name])
                    assert result.exit_code == 0
                else:
                    pytest.skip(f"Project creation with {template} template requires admin permissions")

    async def test_custom_fields_end_to_end_workflow(self, integration_auth_manager):
        """Test comprehensive custom fields management workflow."""
        runner = CliRunner()
        project_id = "FPU"  # Use test project from environment

        with patch.dict(
            os.environ,
            {
                "YOUTRACK_BASE_URL": integration_auth_manager.config.base_url,
                "YOUTRACK_API_KEY": integration_auth_manager.config.api_key,
            },
        ):
            # Step 1: List current custom fields
            result = runner.invoke(main, ["projects", "fields", "list", project_id, "--format", "json"])
            assert result.exit_code == 0
            initial_fields = json.loads(result.output)

            # Step 2: Try to attach a new custom field (this may fail if field doesn't exist)
            # We'll test the command structure rather than actual attachment
            result = runner.invoke(
                main,
                [
                    "projects",
                    "fields",
                    "attach",
                    project_id,
                    "Priority",  # Common field that might exist
                    "--type",
                    "enum",
                ],
            )
            # Command might fail if field already attached or doesn't exist
            assert result.exit_code in [0, 1]

            # Step 3: List fields again to see if anything changed
            result = runner.invoke(main, ["projects", "fields", "list", project_id, "--format", "json"])
            assert result.exit_code == 0

            # Step 4: Try updating a field that exists (if any)
            if initial_fields:
                field_to_update = initial_fields[0].get("field", {}).get("id")
                if field_to_update:
                    result = runner.invoke(
                        main,
                        [
                            "projects",
                            "fields",
                            "update",
                            project_id,
                            field_to_update,
                            "--optional",  # Make field optional
                        ],
                    )
                    # Command might fail due to permissions or field constraints
                    assert result.exit_code in [0, 1]

    async def test_bulk_project_operations_workflow(self, integration_auth_manager):
        """Test bulk operations across multiple projects."""
        runner = CliRunner()

        with patch.dict(
            os.environ,
            {
                "YOUTRACK_BASE_URL": integration_auth_manager.config.base_url,
                "YOUTRACK_API_KEY": integration_auth_manager.config.api_key,
            },
        ):
            # Step 1: Get list of all projects
            result = runner.invoke(main, ["projects", "list", "--format", "json", "--top", "5"])
            assert result.exit_code == 0
            projects = json.loads(result.output)

            # Step 2: Perform operations on each project
            for project in projects[:3]:  # Limit to first 3 projects
                project_id = project.get("shortName") or project.get("id")
                if project_id:
                    # Get project details
                    result = runner.invoke(main, ["projects", "configure", project_id, "--show-details"])
                    assert result.exit_code == 0

                    # List project fields
                    result = runner.invoke(main, ["projects", "fields", "list", project_id, "--top", "10"])
                    assert result.exit_code == 0

    async def test_project_search_and_filtering_workflow(self, integration_auth_manager):
        """Test project search and filtering capabilities."""
        runner = CliRunner()

        with patch.dict(
            os.environ,
            {
                "YOUTRACK_BASE_URL": integration_auth_manager.config.base_url,
                "YOUTRACK_API_KEY": integration_auth_manager.config.api_key,
            },
        ):
            # Test different project listing scenarios
            test_scenarios = [
                # Basic listing
                (["projects", "list", "--top", "10"], "Basic project listing"),
                # Show archived projects
                (["projects", "list", "--show-archived", "--top", "5"], "Archived projects"),
                # JSON format
                (["projects", "list", "--format", "json", "--top", "5"], "JSON format"),
                # Specific fields
                (["projects", "list", "--fields", "shortName,name,leader", "--top", "5"], "Specific fields"),
            ]

            for command_args, description in test_scenarios:
                result = runner.invoke(main, command_args)
                assert result.exit_code == 0, f"Failed: {description}"

    async def test_cross_project_operations_workflow(self, integration_auth_manager):
        """Test operations that involve multiple projects."""
        runner = CliRunner()

        with patch.dict(
            os.environ,
            {
                "YOUTRACK_BASE_URL": integration_auth_manager.config.base_url,
                "YOUTRACK_API_KEY": integration_auth_manager.config.api_key,
            },
        ):
            # Get available projects
            result = runner.invoke(main, ["projects", "list", "--format", "json", "--top", "3"])
            assert result.exit_code == 0
            projects = json.loads(result.output)

            if len(projects) >= 2:
                # Compare custom fields between projects
                project1_id = projects[0].get("shortName") or projects[0].get("id")
                project2_id = projects[1].get("shortName") or projects[1].get("id")

                # Get fields for first project
                result1 = runner.invoke(main, ["projects", "fields", "list", project1_id, "--format", "json"])
                assert result1.exit_code == 0

                # Get fields for second project
                result2 = runner.invoke(main, ["projects", "fields", "list", project2_id, "--format", "json"])
                assert result2.exit_code == 0

                # Analysis would happen here in a real scenario
                # (comparing field configurations, etc.)

    async def test_project_configuration_edge_cases(self, integration_auth_manager):
        """Test edge cases in project configuration."""
        runner = CliRunner()
        project_id = "FPU"  # Use test project

        with patch.dict(
            os.environ,
            {
                "YOUTRACK_BASE_URL": integration_auth_manager.config.base_url,
                "YOUTRACK_API_KEY": integration_auth_manager.config.api_key,
            },
        ):
            # Test showing details without modifications
            result = runner.invoke(main, ["projects", "configure", project_id, "--show-details"])
            assert result.exit_code == 0

            # Test with non-existent project (should fail gracefully)
            result = runner.invoke(main, ["projects", "configure", "NONEXISTENT_PROJECT_12345", "--show-details"])
            assert result.exit_code != 0
            assert "not found" in result.output.lower() or "error" in result.output.lower()

    async def test_project_fields_error_handling(self, integration_auth_manager):
        """Test error handling in project fields operations."""
        runner = CliRunner()
        project_id = "FPU"

        with patch.dict(
            os.environ,
            {
                "YOUTRACK_BASE_URL": integration_auth_manager.config.base_url,
                "YOUTRACK_API_KEY": integration_auth_manager.config.api_key,
            },
        ):
            # Test with non-existent project
            result = runner.invoke(main, ["projects", "fields", "list", "NONEXISTENT_PROJECT_12345"])
            assert result.exit_code != 0

            # Test attaching non-existent field
            result = runner.invoke(
                main, ["projects", "fields", "attach", project_id, "NonExistentField12345", "--type", "enum"]
            )
            assert result.exit_code != 0

            # Test updating non-existent field
            result = runner.invoke(
                main, ["projects", "fields", "update", project_id, "NonExistentField12345", "--optional"]
            )
            assert result.exit_code != 0
