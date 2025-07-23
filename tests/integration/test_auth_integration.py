"""Integration tests for authentication functionality."""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from youtrack_cli.auth import AuthConfig, AuthManager
from youtrack_cli.main import main


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


@pytest.mark.integration
@pytest.mark.asyncio
class TestAuthFlowIntegration:
    """Test comprehensive authentication flows and session management."""

    async def test_complete_auth_login_workflow(self, integration_auth_manager):
        """Test complete authentication login workflow via CLI."""
        runner = CliRunner()

        # Create temporary config for test
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as temp_file:
            temp_config_path = temp_file.name

        try:
            # Test auth login command
            result = runner.invoke(
                main,
                [
                    "auth",
                    "login",
                    "--token",
                    integration_auth_manager.config.token,
                    "--base-url",
                    integration_auth_manager.config.base_url,
                    "--config-file",
                    temp_config_path,
                ],
            )

            assert result.exit_code == 0
            assert "successfully" in result.output.lower() or "authenticated" in result.output.lower()

            # Verify config file was created
            assert Path(temp_config_path).exists()

            # Test that subsequent commands work with saved config
            with patch.dict(os.environ, {"YOUTRACK_CONFIG_FILE": temp_config_path}):
                result = runner.invoke(main, ["projects", "list", "--top", "1"])
                assert result.exit_code == 0

        finally:
            if Path(temp_config_path).exists():
                os.unlink(temp_config_path)

    async def test_auth_logout_workflow(self, integration_auth_manager):
        """Test authentication logout workflow."""
        runner = CliRunner()

        # Create temporary config with credentials
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as temp_file:
            temp_config_path = temp_file.name

        try:
            # First login
            result = runner.invoke(
                main,
                [
                    "auth",
                    "login",
                    "--token",
                    integration_auth_manager.config.token,
                    "--base-url",
                    integration_auth_manager.config.base_url,
                    "--config-file",
                    temp_config_path,
                ],
            )
            assert result.exit_code == 0

            # Then logout
            result = runner.invoke(main, ["auth", "logout", "--config-file", temp_config_path])
            assert result.exit_code == 0

            # Verify config file is cleared or credentials removed
            with patch.dict(os.environ, {"YOUTRACK_CONFIG_FILE": temp_config_path}):
                result = runner.invoke(main, ["projects", "list", "--top", "1"])
                # Should fail due to missing authentication
                assert result.exit_code != 0
                assert "authentication" in result.output.lower() or "credentials" in result.output.lower()

        finally:
            if Path(temp_config_path).exists():
                os.unlink(temp_config_path)

    async def test_auth_status_workflow(self, integration_auth_manager):
        """Test authentication status checking workflow."""
        runner = CliRunner()

        with patch.dict(
            os.environ,
            {
                "YOUTRACK_BASE_URL": integration_auth_manager.config.base_url,
                "YOUTRACK_API_KEY": integration_auth_manager.config.token,
            },
        ):
            # Test auth status command
            result = runner.invoke(main, ["auth", "status"])
            assert result.exit_code == 0
            assert "authenticated" in result.output.lower() or "connected" in result.output.lower()
            assert integration_auth_manager.config.base_url in result.output

    async def test_session_persistence_workflow(self, integration_auth_manager):
        """Test authentication session persistence across commands."""
        runner = CliRunner()

        with patch.dict(
            os.environ,
            {
                "YOUTRACK_BASE_URL": integration_auth_manager.config.base_url,
                "YOUTRACK_API_KEY": integration_auth_manager.config.token,
            },
        ):
            # Execute multiple commands to test session persistence
            commands = [
                ["projects", "list", "--top", "1"],
                ["auth", "status"],
                ["projects", "list", "--top", "1", "--format", "json"],
            ]

            for command in commands:
                result = runner.invoke(main, command)
                assert result.exit_code == 0, f"Command {' '.join(command)} failed"

    async def test_invalid_credentials_handling(self):
        """Test handling of invalid authentication credentials."""
        runner = CliRunner()

        # Test with invalid token
        with patch.dict(
            os.environ, {"YOUTRACK_BASE_URL": "http://0.0.0.0:8080", "YOUTRACK_API_KEY": "invalid_token_12345"}
        ):
            result = runner.invoke(main, ["projects", "list", "--top", "1"])
            assert result.exit_code != 0
            assert "authentication" in result.output.lower() or "unauthorized" in result.output.lower()

    async def test_missing_credentials_handling(self):
        """Test handling of missing authentication credentials."""
        runner = CliRunner()

        # Remove auth environment variables
        env_without_auth = {k: v for k, v in os.environ.items() if not k.startswith("YOUTRACK_")}

        with patch.dict(os.environ, env_without_auth, clear=True):
            result = runner.invoke(main, ["projects", "list", "--top", "1"])
            assert result.exit_code != 0
            assert (
                "credentials" in result.output.lower()
                or "authentication" in result.output.lower()
                or "configuration" in result.output.lower()
            )

    async def test_environment_vs_config_file_precedence(self, integration_auth_manager):
        """Test precedence between environment variables and config file."""
        runner = CliRunner()

        # Create config file with different (invalid) credentials
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as temp_file:
            temp_config_path = temp_file.name
            temp_file.write("YOUTRACK_BASE_URL=http://invalid.example.com\n")
            temp_file.write("YOUTRACK_API_KEY=invalid_token\n")

        try:
            # Environment variables should take precedence
            with patch.dict(
                os.environ,
                {
                    "YOUTRACK_BASE_URL": integration_auth_manager.config.base_url,
                    "YOUTRACK_API_KEY": integration_auth_manager.config.token,
                    "YOUTRACK_CONFIG_FILE": temp_config_path,
                },
            ):
                result = runner.invoke(main, ["auth", "status"])
                assert result.exit_code == 0
                assert integration_auth_manager.config.base_url in result.output

        finally:
            if Path(temp_config_path).exists():
                os.unlink(temp_config_path)

    async def test_token_refresh_simulation(self, integration_auth_manager):
        """Test token refresh-like behavior by re-authenticating."""
        runner = CliRunner()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as temp_file:
            temp_config_path = temp_file.name

        try:
            # Initial authentication
            result = runner.invoke(
                main,
                [
                    "auth",
                    "login",
                    "--token",
                    integration_auth_manager.config.token,
                    "--base-url",
                    integration_auth_manager.config.base_url,
                    "--config-file",
                    temp_config_path,
                ],
            )
            assert result.exit_code == 0

            # Simulate token refresh by logging in again with same credentials
            result = runner.invoke(
                main,
                [
                    "auth",
                    "login",
                    "--token",
                    integration_auth_manager.config.token,
                    "--base-url",
                    integration_auth_manager.config.base_url,
                    "--config-file",
                    temp_config_path,
                ],
            )
            assert result.exit_code == 0

            # Verify authentication still works
            with patch.dict(os.environ, {"YOUTRACK_CONFIG_FILE": temp_config_path}):
                result = runner.invoke(main, ["auth", "status"])
                assert result.exit_code == 0

        finally:
            if Path(temp_config_path).exists():
                os.unlink(temp_config_path)

    async def test_multi_instance_authentication(self, integration_auth_manager):
        """Test authentication with multiple YouTrack instances."""
        runner = CliRunner()

        # Create configs for different instances
        configs = []

        for i in range(2):
            temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=f"_{i}.env", delete=False)
            config_path = temp_file.name
            temp_file.close()
            configs.append(config_path)

        try:
            # Set up authentication for "different" instances
            # (using same instance but different config files)
            for _i, config_path in enumerate(configs):
                result = runner.invoke(
                    main,
                    [
                        "auth",
                        "login",
                        "--token",
                        integration_auth_manager.config.token,
                        "--base-url",
                        integration_auth_manager.config.base_url,
                        "--config-file",
                        config_path,
                    ],
                )
                assert result.exit_code == 0

            # Test that each config works independently
            for config_path in configs:
                with patch.dict(os.environ, {"YOUTRACK_CONFIG_FILE": config_path}):
                    result = runner.invoke(main, ["auth", "status"])
                    assert result.exit_code == 0

        finally:
            for config_path in configs:
                if Path(config_path).exists():
                    os.unlink(config_path)

    async def test_authentication_error_recovery(self, integration_auth_manager):
        """Test recovery from authentication errors."""
        runner = CliRunner()

        # First, test with invalid credentials to trigger error
        with patch.dict(os.environ, {"YOUTRACK_BASE_URL": "http://0.0.0.0:8080", "YOUTRACK_API_KEY": "invalid_token"}):
            result = runner.invoke(main, ["projects", "list", "--top", "1"])
            assert result.exit_code != 0

        # Then recover with valid credentials
        with patch.dict(
            os.environ,
            {
                "YOUTRACK_BASE_URL": integration_auth_manager.config.base_url,
                "YOUTRACK_API_KEY": integration_auth_manager.config.token,
            },
        ):
            result = runner.invoke(main, ["projects", "list", "--top", "1"])
            assert result.exit_code == 0

    async def test_concurrent_authentication_sessions(self, integration_auth_manager):
        """Test handling of concurrent authentication sessions."""
        runner = CliRunner()

        # Simulate concurrent sessions by running multiple commands
        with patch.dict(
            os.environ,
            {
                "YOUTRACK_BASE_URL": integration_auth_manager.config.base_url,
                "YOUTRACK_API_KEY": integration_auth_manager.config.token,
            },
        ):
            # Run multiple commands that would simulate concurrent access
            results = []
            commands = [
                ["auth", "status"],
                ["projects", "list", "--top", "1"],
                ["auth", "status"],
            ]

            for command in commands:
                result = runner.invoke(main, command)
                results.append(result)

            # All should succeed
            for i, result in enumerate(results):
                assert result.exit_code == 0, f"Command {i} failed: {result.output}"
