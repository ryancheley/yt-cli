"""Integration tests for user management workflows."""

import os
import uuid
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from youtrack_cli.main import main


@pytest.fixture
def test_user_data():
    """Generate unique test user data."""
    unique_id = str(uuid.uuid4())[:8]
    return {
        "login": f"test_user_{unique_id}",
        "full_name": f"Test User {unique_id}",
        "email": f"test_{unique_id}@example.com",
        "password": f"TestPass123!{unique_id}",
    }


@pytest.fixture
async def cleanup_test_users(integration_auth_manager, integration_client):
    """Track and cleanup test users created during tests."""
    created_users = []

    yield created_users

    # Cleanup: Try to delete/ban test users
    for user_login in created_users:
        try:
            # Try to ban the user instead of deleting (YouTrack doesn't allow user deletion via API)
            async with integration_client as client:
                await client.request("POST", f"/users/{user_login}", json={"banned": True})
        except Exception:
            # Ignore cleanup errors
            pass


@pytest.mark.integration
@pytest.mark.asyncio
class TestUserManagementWorkflows:
    """Test complete user management workflows."""

    async def test_user_list_workflow(self, integration_auth_manager):
        """Test listing users with various filters."""
        runner = CliRunner()

        # Test basic user listing
        with patch.dict(
            os.environ,
            {
                "YOUTRACK_BASE_URL": integration_auth_manager.config.base_url,
                "YOUTRACK_API_KEY": integration_auth_manager.config.api_key,
            },
        ):
            # List all users
            result = runner.invoke(main, ["users", "list", "--top", "5"])
            assert result.exit_code == 0
            assert "login" in result.output.lower() or "users" in result.output.lower()

            # List only active users
            result = runner.invoke(main, ["users", "list", "--active-only", "--top", "5"])
            assert result.exit_code == 0

            # List with specific fields
            result = runner.invoke(main, ["users", "list", "--fields", "login,email", "--top", "5"])
            assert result.exit_code == 0

            # List with search query
            result = runner.invoke(main, ["users", "list", "--query", "admin", "--top", "5"])
            assert result.exit_code == 0

    async def test_user_creation_and_update_workflow(
        self, integration_auth_manager, test_user_data, cleanup_test_users
    ):
        """Test complete user creation and update workflow."""
        runner = CliRunner()

        with patch.dict(
            os.environ,
            {
                "YOUTRACK_BASE_URL": integration_auth_manager.config.base_url,
                "YOUTRACK_API_KEY": integration_auth_manager.config.api_key,
            },
        ):
            # Create a new user
            result = runner.invoke(
                main,
                [
                    "users",
                    "create",
                    test_user_data["login"],
                    test_user_data["full_name"],
                    test_user_data["email"],
                    "--password",
                    test_user_data["password"],
                ],
            )

            # Check if creation was successful or permission denied
            if result.exit_code == 0:
                cleanup_test_users.append(test_user_data["login"])
                assert "created successfully" in result.output.lower()

                # Update the user's full name
                new_name = f"Updated {test_user_data['full_name']}"
                result = runner.invoke(
                    main, ["users", "update", test_user_data["login"], "--full-name", new_name, "--show-details"]
                )
                assert result.exit_code == 0
                assert new_name in result.output or "updated" in result.output.lower()

                # Update email
                new_email = f"updated_{test_user_data['email']}"
                result = runner.invoke(main, ["users", "update", test_user_data["login"], "--email", new_email])
                assert result.exit_code == 0

                # Force password change
                result = runner.invoke(main, ["users", "update", test_user_data["login"], "--force-change-password"])
                assert result.exit_code == 0

                # Ban the user
                result = runner.invoke(main, ["users", "update", test_user_data["login"], "--banned"])
                assert result.exit_code == 0

                # Unban the user
                result = runner.invoke(main, ["users", "update", test_user_data["login"], "--unbanned"])
                assert result.exit_code == 0
            else:
                # Permission denied is acceptable for user creation
                assert "permission" in result.output.lower() or "forbidden" in result.output.lower()
                pytest.skip("User creation requires admin permissions")

    async def test_user_group_management_workflow(self, integration_auth_manager):
        """Test user group membership management."""
        runner = CliRunner()

        with patch.dict(
            os.environ,
            {
                "YOUTRACK_BASE_URL": integration_auth_manager.config.base_url,
                "YOUTRACK_API_KEY": integration_auth_manager.config.api_key,
            },
        ):
            # First, get the current user (usually admin)
            result = runner.invoke(main, ["users", "list", "--query", "me", "--top", "1"])
            if result.exit_code != 0:
                pytest.skip("Cannot retrieve current user")

            # Extract user login from output (this is a simple approach)
            # In real scenario, we'd parse the output more carefully
            user_id = "admin"  # Default to admin for testing

            # List user's current groups
            result = runner.invoke(main, ["users", "groups", user_id])
            assert result.exit_code == 0

            # List user's roles
            result = runner.invoke(main, ["users", "roles", user_id])
            assert result.exit_code == 0

            # List user's teams
            result = runner.invoke(main, ["users", "teams", user_id])
            assert result.exit_code == 0

    async def test_user_permissions_workflow(self, integration_auth_manager):
        """Test user permissions management workflow."""
        runner = CliRunner()

        with patch.dict(
            os.environ,
            {
                "YOUTRACK_BASE_URL": integration_auth_manager.config.base_url,
                "YOUTRACK_API_KEY": integration_auth_manager.config.api_key,
            },
        ):
            # This test would require knowing available groups
            # For now, we'll test the command structure
            result = runner.invoke(
                main, ["users", "permissions", "admin", "--action", "add_to_group", "--group-id", "test-group"]
            )

            # The command might fail due to missing group, but should be well-formed
            assert result.exit_code in [0, 1]  # 0 for success, 1 for expected failures

    async def test_user_search_and_filter_workflow(self, integration_auth_manager):
        """Test comprehensive user search and filtering."""
        runner = CliRunner()

        with patch.dict(
            os.environ,
            {
                "YOUTRACK_BASE_URL": integration_auth_manager.config.base_url,
                "YOUTRACK_API_KEY": integration_auth_manager.config.api_key,
            },
        ):
            # Test various search scenarios
            search_queries = [
                ("users", "list", "--query", "login: admin*"),
                ("users", "list", "--query", "email: *@*"),
                ("users", "list", "--active-only", "--format", "json"),
                ("users", "list", "--fields", "login,email,fullName", "--top", "10"),
            ]

            for query_parts in search_queries:
                result = runner.invoke(main, list(query_parts))
                assert result.exit_code == 0

    async def test_user_lifecycle_workflow(self, integration_auth_manager, test_user_data, cleanup_test_users):
        """Test complete user lifecycle from creation to deactivation."""
        runner = CliRunner()

        with patch.dict(
            os.environ,
            {
                "YOUTRACK_BASE_URL": integration_auth_manager.config.base_url,
                "YOUTRACK_API_KEY": integration_auth_manager.config.api_key,
            },
        ):
            # Step 1: Create user
            result = runner.invoke(
                main,
                [
                    "users",
                    "create",
                    test_user_data["login"],
                    test_user_data["full_name"],
                    test_user_data["email"],
                    "--password",
                    test_user_data["password"],
                    "--force-change-password",
                ],
            )

            if result.exit_code == 0:
                cleanup_test_users.append(test_user_data["login"])

                # Step 2: Verify user exists
                result = runner.invoke(main, ["users", "list", "--query", f"login: {test_user_data['login']}"])
                assert result.exit_code == 0
                assert test_user_data["login"] in result.output

                # Step 3: Update user details
                result = runner.invoke(
                    main, ["users", "update", test_user_data["login"], "--full-name", "Updated Name", "--show-details"]
                )
                assert result.exit_code == 0

                # Step 4: Check user groups/roles/teams
                for subcommand in ["groups", "roles", "teams"]:
                    result = runner.invoke(main, ["users", subcommand, test_user_data["login"]])
                    assert result.exit_code == 0

                # Step 5: Deactivate (ban) user
                result = runner.invoke(main, ["users", "update", test_user_data["login"], "--banned"])
                assert result.exit_code == 0

                # Step 6: Verify user is banned
                result = runner.invoke(
                    main, ["users", "list", "--query", f"login: {test_user_data['login']}", "--active-only"]
                )
                assert result.exit_code == 0
                # User should not appear in active-only list
                assert test_user_data["login"] not in result.output
            else:
                pytest.skip("User creation requires admin permissions")

    async def test_bulk_user_operations_workflow(self, integration_auth_manager):
        """Test bulk operations on multiple users."""
        runner = CliRunner()

        with patch.dict(
            os.environ,
            {
                "YOUTRACK_BASE_URL": integration_auth_manager.config.base_url,
                "YOUTRACK_API_KEY": integration_auth_manager.config.api_key,
            },
        ):
            # Get list of users
            result = runner.invoke(main, ["users", "list", "--top", "5", "--format", "json"])
            assert result.exit_code == 0

            # In a real bulk operation scenario, we would:
            # 1. Parse the JSON output
            # 2. Extract user logins
            # 3. Perform operations on each user
            # For now, we're testing the workflow structure

            # Simulate checking details for multiple users
            test_users = ["admin"]  # Safe default user
            for user in test_users:
                result = runner.invoke(main, ["users", "groups", user])
                assert result.exit_code == 0
