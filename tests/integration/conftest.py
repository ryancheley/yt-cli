"""Integration test configuration and fixtures."""

import os
import uuid
from typing import List

import pytest

from youtrack_cli.auth import AuthConfig, AuthManager
from youtrack_cli.client import HTTPClientManager
from youtrack_cli.issues import IssueManager
from youtrack_cli.projects import ProjectManager


@pytest.fixture(scope="session")
def integration_auth_config():
    """Load real YouTrack credentials for integration tests."""
    base_url = os.getenv("YOUTRACK_BASE_URL")
    token = os.getenv("YOUTRACK_API_KEY")

    if not base_url or not token:
        pytest.skip("Integration tests require YOUTRACK_BASE_URL and YOUTRACK_API_KEY environment variables")

    # Type assertions for mypy/ty
    assert base_url is not None
    assert token is not None

    return AuthConfig(base_url=base_url, token=token, username=os.getenv("YOUTRACK_USERNAME", "integration-test-user"))


@pytest.fixture(scope="session")
def integration_auth_manager(integration_auth_config):
    """AuthManager with real credentials for integration tests."""
    # Use a temporary config path to avoid interfering with real config
    temp_config_path = f"/tmp/yt-cli-integration-test-{uuid.uuid4()}.env"
    auth_manager = AuthManager(temp_config_path)

    # Save the integration credentials to the temp config
    auth_manager.save_credentials(
        base_url=integration_auth_config.base_url,
        token=integration_auth_config.token,
        username=integration_auth_config.username,
        use_keyring=False,  # Don't use keyring in tests
    )

    yield auth_manager

    # Cleanup: remove temp config file if it exists
    if os.path.exists(temp_config_path):
        os.unlink(temp_config_path)


@pytest.fixture(scope="session")
def integration_client(integration_auth_manager):
    """HTTP client manager for integration tests."""
    return HTTPClientManager(integration_auth_manager)


@pytest.fixture(scope="session")
def integration_project_manager(integration_auth_manager):
    """ProjectManager for integration tests."""
    return ProjectManager(integration_auth_manager)


@pytest.fixture(scope="session")
def integration_issue_manager(integration_auth_manager):
    """IssueManager for integration tests."""
    return IssueManager(integration_auth_manager)


@pytest.fixture(scope="session")
def test_project_id():
    """Test project ID to use for integration tests."""
    project_id = os.getenv("YOUTRACK_TEST_PROJECT", "FPU")
    return project_id


@pytest.fixture(scope="function")
def test_issue_data(test_project_id):
    """Generate test issue data with unique identifier."""
    unique_id = str(uuid.uuid4())[:8]
    return {
        "project": {"id": test_project_id},
        "summary": f"Integration Test Issue {unique_id}",
        "description": f"This is an integration test issue created for testing purposes. ID: {unique_id}",
    }


@pytest.fixture(scope="function")
async def cleanup_test_issues(integration_issue_manager, test_project_id):
    """Track and cleanup test issues created during integration tests."""
    created_issues: List[str] = []

    def track_issue(issue_id: str):
        """Track an issue for cleanup."""
        created_issues.append(issue_id)

    # Provide the tracking function to tests
    yield track_issue

    # Cleanup after test
    for issue_id in created_issues:
        try:
            # Delete the test issue (properly await the async method)
            await integration_issue_manager.delete_issue(issue_id)
        except Exception as e:
            # Log but don't fail the test if cleanup fails
            print(f"Warning: Failed to cleanup test issue {issue_id}: {e}")


@pytest.fixture(scope="function")
def integration_test_data():
    """Provide test data generators for integration tests."""
    unique_id = str(uuid.uuid4())[:8]

    return {
        "unique_id": unique_id,
        "test_summary": f"Integration Test {unique_id}",
        "test_description": f"Integration test description {unique_id}",
        "test_tag": f"integration-test-{unique_id}",
    }


@pytest.fixture(autouse=True)
def integration_test_marker_check(request):
    """Ensure integration tests are properly marked and have required environment."""
    if "integration" in request.keywords:
        # Check that required environment variables are present
        required_vars = ["YOUTRACK_BASE_URL", "YOUTRACK_API_KEY"]
        missing_vars = [var for var in required_vars if not os.getenv(var)]

        if missing_vars:
            pytest.skip(f"Integration test requires environment variables: {', '.join(missing_vars)}")


@pytest.fixture(scope="session")
def integration_test_cleanup():
    """Session-level cleanup for integration tests."""
    cleanup_data = {
        "issues_to_cleanup": [],
        "projects_to_cleanup": [],
    }

    yield cleanup_data

    # Perform session-level cleanup
    # This could include removing any test projects or other resources
    # created during the integration test session
    pass
