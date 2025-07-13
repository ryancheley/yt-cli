"""Integration tests for authentication functionality."""

import os
import tempfile
from pathlib import Path

import pytest

from youtrack_cli.auth import AuthConfig, AuthManager


@pytest.mark.integration
class TestAuthIntegration:
    """Integration tests for authentication with real YouTrack API."""

    def test_auth_config_with_real_credentials(self, integration_auth_config):
        """Test AuthConfig with real credentials."""
        assert integration_auth_config.base_url
        assert integration_auth_config.token
        assert integration_auth_config.base_url.startswith("http")
        assert len(integration_auth_config.token) > 10  # Basic sanity check

    def test_auth_manager_load_credentials(self, integration_auth_manager):
        """Test AuthManager can load and provide credentials."""
        credentials = integration_auth_manager.load_credentials()

        assert credentials is not None
        assert credentials.base_url
        assert credentials.token
        assert credentials.base_url.startswith("http")

    def test_client_authentication(self, integration_client):
        """Test that client can authenticate with real API."""
        # This should not raise an exception if authentication works
        client = integration_client
        assert client is not None

        # Test basic API call that requires authentication
        # This will verify the token is valid
        try:
            # Simple API call to verify authentication
            response = client._make_request("GET", "/admin/projects")
            assert response.status_code in [200, 403]  # 200 = success, 403 = no admin permissions but auth worked
        except Exception as e:
            pytest.fail(f"Authentication failed: {e}")

    def test_auth_manager_save_and_load_credentials(self):
        """Test saving and loading credentials to/from file."""
        # Create a temporary config file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as temp_file:
            temp_config_path = temp_file.name

        try:
            # Create auth manager with temp config
            auth_manager = AuthManager(temp_config_path)

            # Create test credentials
            test_config = AuthConfig(
                base_url="https://test-integration.youtrack.cloud",
                token="test-integration-token-123",
                username="test-integration-user",
            )

            # Save credentials
            auth_manager.save_credentials(
                base_url=test_config.base_url, token=test_config.token, username=test_config.username, use_keyring=False
            )

            # Verify file was created
            assert Path(temp_config_path).exists()

            # Create new auth manager and load credentials
            new_auth_manager = AuthManager(temp_config_path)
            loaded_config = new_auth_manager.load_credentials()

            # Verify loaded credentials match saved ones
            assert loaded_config is not None
            assert loaded_config.base_url == test_config.base_url
            assert loaded_config.token == test_config.token
            assert loaded_config.username == test_config.username

        finally:
            # Cleanup temp file
            if Path(temp_config_path).exists():
                os.unlink(temp_config_path)

    @pytest.mark.skip(reason="Requires manual testing with invalid credentials")
    def test_invalid_token_handling(self):
        """Test handling of invalid authentication token."""
        # This test would require setting up invalid credentials
        # Skip for now as it requires manual setup
        pass

    def test_environment_variable_integration(self):
        """Test that auth can be loaded from environment variables."""
        # This test verifies that the integration setup correctly
        # loads credentials from environment variables
        base_url = os.getenv("YOUTRACK_BASE_URL")
        token = os.getenv("YOUTRACK_API_KEY")

        if not base_url or not token:
            pytest.skip("Integration test requires YOUTRACK_BASE_URL and YOUTRACK_API_KEY")

        # Create config from environment
        assert base_url is not None
        assert token is not None
        config = AuthConfig(base_url=base_url, token=token)

        assert config.base_url == base_url
        assert config.token == token
