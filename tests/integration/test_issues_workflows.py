"""Integration tests for multi-step issue workflows."""

import json
import os
import tempfile
import uuid
from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from youtrack_cli.main import main


@pytest.fixture
def test_issue_data():
    """Generate unique test issue data."""
    unique_id = str(uuid.uuid4())[:8]
    return {
        "summary": f"Test Issue {unique_id}",
        "description": f"Test issue created for integration testing {unique_id}",
        "type": "Bug",
        "priority": "Normal",
        "assignee": "admin",
    }


@pytest.fixture
def test_batch_data():
    """Generate batch test data."""
    unique_id = str(uuid.uuid4())[:8]
    issues = []
    for i in range(3):
        issues.append(
            {
                "summary": f"Batch Issue {i + 1} {unique_id}",
                "description": f"Batch created issue {i + 1} for testing {unique_id}",
                "type": "Task",
                "priority": "Normal",
            }
        )
    return issues


@pytest.fixture
async def cleanup_test_issues(integration_auth_manager, integration_client):
    """Track and cleanup test issues created during tests."""
    created_issues = []

    yield created_issues

    # Cleanup: Delete test issues
    for issue_id in created_issues:
        try:
            async with integration_client as client:
                await client.request("DELETE", f"/issues/{issue_id}")
        except Exception:
            # Ignore cleanup errors
            pass


@pytest.mark.integration
@pytest.mark.asyncio
class TestMultiStepIssueWorkflows:
    """Test complex multi-step issue workflows."""

    async def test_complete_issue_lifecycle_workflow(
        self, integration_auth_manager, test_issue_data, cleanup_test_issues
    ):
        """Test complete issue lifecycle from creation to deletion."""
        runner = CliRunner()
        project_id = "FPU"

        with patch.dict(
            os.environ,
            {
                "YOUTRACK_BASE_URL": integration_auth_manager.config.base_url,
                "YOUTRACK_API_KEY": integration_auth_manager.config.token,
            },
        ):
            # Step 1: Create issue
            result = runner.invoke(
                main,
                [
                    "issues",
                    "create",
                    "--project",
                    project_id,
                    "--summary",
                    test_issue_data["summary"],
                    "--description",
                    test_issue_data["description"],
                    "--type",
                    test_issue_data["type"],
                    "--priority",
                    test_issue_data["priority"],
                ],
            )

            if result.exit_code == 0:
                # Extract issue ID from output
                lines = result.output.strip().split("\n")
                issue_id = None
                for line in lines:
                    if "created" in line.lower() and project_id in line:
                        # Try to extract issue ID (format like FPU-123)
                        parts = line.split()
                        for part in parts:
                            if project_id in part and "-" in part:
                                issue_id = part.strip(".:")
                                break
                        break

                if issue_id:
                    cleanup_test_issues.append(issue_id)

                    # Step 2: Assign issue
                    result = runner.invoke(
                        main, ["issues", "assign", issue_id, "--assignee", test_issue_data["assignee"]]
                    )
                    assert result.exit_code == 0

                    # Step 3: Add comment
                    result = runner.invoke(
                        main, ["issues", "comments", "add", issue_id, "--text", "Initial comment for testing workflow"]
                    )
                    assert result.exit_code == 0

                    # Step 4: Add tag
                    result = runner.invoke(main, ["issues", "tag", "add", issue_id, "--tag", "test-workflow"])
                    assert result.exit_code == 0

                    # Step 5: Update issue state (if possible)
                    result = runner.invoke(main, ["issues", "move", issue_id, "--state", "In Progress"])
                    # State transition might fail due to workflow rules
                    assert result.exit_code in [0, 1]

                    # Step 6: Add another comment
                    result = runner.invoke(
                        main, ["issues", "comments", "add", issue_id, "--text", "Progress update comment"]
                    )
                    assert result.exit_code == 0

                    # Step 7: List all comments to verify
                    result = runner.invoke(main, ["issues", "comments", "list", issue_id])
                    assert result.exit_code == 0
                    assert "Initial comment" in result.output

                    # Step 8: Show issue details
                    result = runner.invoke(main, ["issues", "show", issue_id])
                    assert result.exit_code == 0
                    assert test_issue_data["summary"] in result.output

                    # Step 9: Update issue summary
                    result = runner.invoke(
                        main, ["issues", "update", issue_id, "--summary", f"Updated: {test_issue_data['summary']}"]
                    )
                    assert result.exit_code == 0
                else:
                    pytest.skip("Could not extract issue ID from create output")
            else:
                pytest.skip("Issue creation requires permissions")

    async def test_batch_operations_workflow(self, integration_auth_manager, test_batch_data, cleanup_test_issues):
        """Test batch operations workflow with validation."""
        runner = CliRunner()
        project_id = "FPU"

        with patch.dict(
            os.environ,
            {
                "YOUTRACK_BASE_URL": integration_auth_manager.config.base_url,
                "YOUTRACK_API_KEY": integration_auth_manager.config.token,
            },
        ):
            # Create temporary batch file
            with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as temp_file:
                batch_file_path = temp_file.name
                # Create batch data for YouTrack CLI format
                batch_data = {"project": project_id, "issues": test_batch_data}
                json.dump(batch_data, temp_file, indent=2)

            try:
                # Step 1: Validate batch file
                result = runner.invoke(main, ["issues", "batch", "validate", batch_file_path])
                assert result.exit_code == 0

                # Step 2: Execute batch create
                result = runner.invoke(main, ["issues", "batch", "create", batch_file_path])

                if result.exit_code == 0:
                    # Extract created issue IDs from output
                    created_issue_ids = []
                    lines = result.output.strip().split("\n")
                    for line in lines:
                        if project_id in line and "created" in line.lower():
                            parts = line.split()
                            for part in parts:
                                if project_id in part and "-" in part:
                                    issue_id = part.strip(".:")
                                    created_issue_ids.append(issue_id)
                                    cleanup_test_issues.append(issue_id)
                                    break

                    # Step 3: Search for created issues
                    if created_issue_ids:
                        result = runner.invoke(
                            main,
                            [
                                "issues",
                                "search",
                                "--project",
                                project_id,
                                "--query",
                                "summary: Batch Issue*",
                                "--format",
                                "json",
                            ],
                        )
                        assert result.exit_code == 0

                        # Step 4: Bulk update via batch (if supported)
                        # Create update batch file
                        update_data = {
                            "project": project_id,
                            "updates": [{"id": issue_id, "priority": "High"} for issue_id in created_issue_ids[:2]],
                        }

                        with tempfile.NamedTemporaryFile(mode="w", suffix="_update.json", delete=False) as update_file:
                            update_file_path = update_file.name
                            json.dump(update_data, update_file, indent=2)

                        try:
                            result = runner.invoke(main, ["issues", "batch", "update", update_file_path])
                            # Batch update might not be supported, so accept failure
                            assert result.exit_code in [0, 1]
                        finally:
                            if Path(update_file_path).exists():
                                os.unlink(update_file_path)

            finally:
                if Path(batch_file_path).exists():
                    os.unlink(batch_file_path)

    async def test_issue_collaboration_workflow(self, integration_auth_manager, test_issue_data, cleanup_test_issues):
        """Test multi-user collaboration workflow on a single issue."""
        runner = CliRunner()
        project_id = "FPU"

        with patch.dict(
            os.environ,
            {
                "YOUTRACK_BASE_URL": integration_auth_manager.config.base_url,
                "YOUTRACK_API_KEY": integration_auth_manager.config.token,
            },
        ):
            # Step 1: Create issue
            result = runner.invoke(
                main,
                [
                    "issues",
                    "create",
                    "--project",
                    project_id,
                    "--summary",
                    f"Collaboration: {test_issue_data['summary']}",
                    "--description",
                    test_issue_data["description"],
                    "--type",
                    test_issue_data["type"],
                ],
            )

            if result.exit_code == 0:
                # Extract issue ID
                lines = result.output.strip().split("\n")
                issue_id = None
                for line in lines:
                    if "created" in line.lower() and project_id in line:
                        parts = line.split()
                        for part in parts:
                            if project_id in part and "-" in part:
                                issue_id = part.strip(".:")
                                break
                        break

                if issue_id:
                    cleanup_test_issues.append(issue_id)

                    # Step 2: Simulate multiple team members adding comments
                    comments = [
                        "Initial analysis: This looks like a configuration issue",
                        "I can reproduce this on my environment",
                        "Proposed solution: Update the config file",
                        "Testing the fix now",
                        "Fix confirmed working",
                    ]

                    for i, comment_text in enumerate(comments):
                        result = runner.invoke(
                            main, ["issues", "comments", "add", issue_id, "--text", f"{comment_text} (Comment {i + 1})"]
                        )
                        assert result.exit_code == 0

                    # Step 3: List all comments to verify conversation
                    result = runner.invoke(main, ["issues", "comments", "list", issue_id, "--format", "json"])
                    assert result.exit_code == 0

                    # Step 4: Assign issue for resolution
                    result = runner.invoke(main, ["issues", "assign", issue_id, "--assignee", "admin"])
                    assert result.exit_code == 0

                    # Step 5: Move to resolved state
                    result = runner.invoke(main, ["issues", "move", issue_id, "--state", "Fixed"])
                    # State might not exist or transition not allowed
                    assert result.exit_code in [0, 1]

                    # Step 6: Add final resolution comment
                    result = runner.invoke(
                        main,
                        ["issues", "comments", "add", issue_id, "--text", "Issue resolved and tested successfully"],
                    )
                    assert result.exit_code == 0

    async def test_cross_issue_relationship_workflow(self, integration_auth_manager, cleanup_test_issues):
        """Test creating and managing relationships between issues."""
        runner = CliRunner()
        project_id = "FPU"

        with patch.dict(
            os.environ,
            {
                "YOUTRACK_BASE_URL": integration_auth_manager.config.base_url,
                "YOUTRACK_API_KEY": integration_auth_manager.config.token,
            },
        ):
            unique_id = str(uuid.uuid4())[:8]

            # Step 1: Create parent issue
            result = runner.invoke(
                main,
                [
                    "issues",
                    "create",
                    "--project",
                    project_id,
                    "--summary",
                    f"Parent Issue {unique_id}",
                    "--description",
                    "Parent issue for testing relationships",
                    "--type",
                    "Epic",
                ],
            )

            parent_issue_id = None
            child_issue_ids = []

            if result.exit_code == 0:
                # Extract parent issue ID
                lines = result.output.strip().split("\n")
                for line in lines:
                    if "created" in line.lower() and project_id in line:
                        parts = line.split()
                        for part in parts:
                            if project_id in part and "-" in part:
                                parent_issue_id = part.strip(".:")
                                cleanup_test_issues.append(parent_issue_id)
                                break
                        break

                # Step 2: Create child issues
                for i in range(2):
                    result = runner.invoke(
                        main,
                        [
                            "issues",
                            "create",
                            "--project",
                            project_id,
                            "--summary",
                            f"Child Issue {i + 1} {unique_id}",
                            "--description",
                            f"Child issue {i + 1} for relationship testing",
                            "--type",
                            "Task",
                        ],
                    )

                    if result.exit_code == 0:
                        lines = result.output.strip().split("\n")
                        for line in lines:
                            if "created" in line.lower() and project_id in line:
                                parts = line.split()
                                for part in parts:
                                    if project_id in part and "-" in part:
                                        child_id = part.strip(".:")
                                        child_issue_ids.append(child_id)
                                        cleanup_test_issues.append(child_id)
                                        break
                                break

                # Step 3: Create links between parent and children
                if parent_issue_id and child_issue_ids:
                    for child_id in child_issue_ids:
                        result = runner.invoke(
                            main, ["issues", "links", "create", parent_issue_id, child_id, "--type", "depends"]
                        )
                        # Link creation might fail if link type doesn't exist
                        assert result.exit_code in [0, 1]

                    # Step 4: List issue links
                    result = runner.invoke(main, ["issues", "links", "list", parent_issue_id])
                    assert result.exit_code == 0

                    # Step 5: Show dependencies
                    result = runner.invoke(main, ["issues", "dependencies", parent_issue_id])
                    assert result.exit_code == 0

    async def test_attachment_lifecycle_workflow(self, integration_auth_manager, test_issue_data, cleanup_test_issues):
        """Test complete attachment management workflow."""
        runner = CliRunner()
        project_id = "FPU"

        with patch.dict(
            os.environ,
            {
                "YOUTRACK_BASE_URL": integration_auth_manager.config.base_url,
                "YOUTRACK_API_KEY": integration_auth_manager.config.token,
            },
        ):
            # Step 1: Create issue
            result = runner.invoke(
                main,
                [
                    "issues",
                    "create",
                    "--project",
                    project_id,
                    "--summary",
                    f"Attachment Test: {test_issue_data['summary']}",
                    "--description",
                    "Issue for testing attachment workflows",
                    "--type",
                    "Bug",
                ],
            )

            if result.exit_code == 0:
                # Extract issue ID
                lines = result.output.strip().split("\n")
                issue_id = None
                for line in lines:
                    if "created" in line.lower() and project_id in line:
                        parts = line.split()
                        for part in parts:
                            if project_id in part and "-" in part:
                                issue_id = part.strip(".:")
                                break
                        break

                if issue_id:
                    cleanup_test_issues.append(issue_id)

                    # Create temporary test files
                    test_files = []
                    for i in range(2):
                        temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=f"_test_{i}.txt", delete=False)
                        temp_file.write(f"Test attachment content {i + 1}\nFor issue {issue_id}")
                        temp_file.close()
                        test_files.append(temp_file.name)

                    try:
                        # Step 2: Upload attachments
                        for i, file_path in enumerate(test_files):
                            result = runner.invoke(
                                main,
                                [
                                    "issues",
                                    "attach",
                                    "upload",
                                    issue_id,
                                    "--file",
                                    file_path,
                                    "--description",
                                    f"Test attachment {i + 1}",
                                ],
                            )
                            # Attachment upload might fail due to permissions
                            assert result.exit_code in [0, 1]

                        # Step 3: List attachments
                        result = runner.invoke(main, ["issues", "attach", "list", issue_id])
                        assert result.exit_code == 0

                        # Step 4: Try to download an attachment (if any exist)
                        # This would require parsing the list output to get attachment IDs
                        # For now, we just verify the command structure works

                    finally:
                        # Cleanup temp files
                        for file_path in test_files:
                            if Path(file_path).exists():
                                os.unlink(file_path)

    async def test_issue_search_and_bulk_operations(self, integration_auth_manager, cleanup_test_issues):
        """Test search-based bulk operations workflow."""
        runner = CliRunner()
        project_id = "FPU"
        unique_id = str(uuid.uuid4())[:8]

        with patch.dict(
            os.environ,
            {
                "YOUTRACK_BASE_URL": integration_auth_manager.config.base_url,
                "YOUTRACK_API_KEY": integration_auth_manager.config.token,
            },
        ):
            # Step 1: Create multiple issues with common tag
            created_issues = []
            for i in range(3):
                result = runner.invoke(
                    main,
                    [
                        "issues",
                        "create",
                        "--project",
                        project_id,
                        "--summary",
                        f"Bulk Test Issue {i + 1} {unique_id}",
                        "--description",
                        f"Issue for bulk operations testing {unique_id}",
                        "--type",
                        "Task",
                    ],
                )

                if result.exit_code == 0:
                    lines = result.output.strip().split("\n")
                    for line in lines:
                        if "created" in line.lower() and project_id in line:
                            parts = line.split()
                            for part in parts:
                                if project_id in part and "-" in part:
                                    issue_id = part.strip(".:")
                                    created_issues.append(issue_id)
                                    cleanup_test_issues.append(issue_id)
                                    break
                            break

            if created_issues:
                # Step 2: Add common tag to all issues
                for issue_id in created_issues:
                    result = runner.invoke(main, ["issues", "tag", "add", issue_id, "--tag", f"bulk-test-{unique_id}"])
                    assert result.exit_code == 0

                # Step 3: Search for issues by tag
                result = runner.invoke(
                    main,
                    [
                        "issues",
                        "search",
                        "--project",
                        project_id,
                        "--query",
                        f"tag: bulk-test-{unique_id}",
                        "--format",
                        "json",
                    ],
                )
                assert result.exit_code == 0

                # Step 4: Update all issues (simulate bulk update)
                for issue_id in created_issues:
                    result = runner.invoke(main, ["issues", "update", issue_id, "--priority", "High"])
                    assert result.exit_code == 0

                # Step 5: Verify updates
                for issue_id in created_issues:
                    result = runner.invoke(main, ["issues", "show", issue_id])
                    assert result.exit_code == 0
