"""Tests for authentication functionality."""

import os
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import ValidationError

from youtrack_cli.auth import AuthConfig, AuthManager
from youtrack_cli.config import ConfigManager


class TestAuthConfig:
    """Test AuthConfig model."""

    def test_valid_config(self):
        """Test creating a valid auth config."""
        config = AuthConfig(
            base_url="https://example.youtrack.cloud",
            token="test-token-123",
            username="testuser",
        )
        assert config.base_url == "https://example.youtrack.cloud"
        assert config.token == "test-token-123"
        assert config.username == "testuser"

    def test_config_without_username(self):
        """Test creating config without username."""
        config = AuthConfig(base_url="https://example.youtrack.cloud", token="test-token-123")
        assert config.base_url == "https://example.youtrack.cloud"
        assert config.token == "test-token-123"
        assert config.username is None

    def test_invalid_config(self):
        """Test creating invalid config raises validation error."""
        with pytest.raises(ValidationError):
            AuthConfig()


class TestAuthManager:
    """Test AuthManager class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, ".env")
        self.auth_manager = AuthManager(self.config_path)

        # Store original environment variables to restore later
        self.original_env = {
            key: os.environ.get(key) for key in ["YOUTRACK_BASE_URL", "YOUTRACK_TOKEN", "YOUTRACK_USERNAME"]
        }

    def teardown_method(self):
        """Clean up test fixtures and restore environment."""
        # Remove any YouTrack environment variables that were set during tests
        for key in ["YOUTRACK_BASE_URL", "YOUTRACK_TOKEN", "YOUTRACK_USERNAME"]:
            if key in os.environ:
                del os.environ[key]

        # Restore original environment variables
        for key, value in self.original_env.items():
            if value is not None:
                os.environ[key] = value

    def test_default_config_path(self):
        """Test default config path generation."""
        manager = AuthManager()
        expected_path = Path.home() / ".config" / "youtrack-cli" / ".env"
        assert manager.config_path == str(expected_path)

    def test_save_credentials(self):
        """Test saving credentials to config file."""
        # Force file storage instead of keyring for this test
        self.auth_manager.save_credentials(
            "https://example.youtrack.cloud",
            "test-token-123",
            "testuser",
            use_keyring=False,
        )

        # Use ConfigManager to read values instead of raw file content
        config_manager = ConfigManager(self.config_path)
        config_values = config_manager.list_config()

        assert config_values.get("YOUTRACK_BASE_URL") == "https://example.youtrack.cloud"
        assert config_values.get("YOUTRACK_TOKEN") == "test-token-123"
        assert config_values.get("YOUTRACK_USERNAME") == "testuser"

    def test_save_credentials_without_username(self):
        """Test saving credentials without username."""
        # Force file storage instead of keyring for this test
        self.auth_manager.save_credentials("https://example.youtrack.cloud", "test-token-123", use_keyring=False)

        # Use ConfigManager to read values instead of raw file content
        config_manager = ConfigManager(self.config_path)
        config_values = config_manager.list_config()

        assert config_values.get("YOUTRACK_BASE_URL") == "https://example.youtrack.cloud"
        assert config_values.get("YOUTRACK_TOKEN") == "test-token-123"
        assert "YOUTRACK_USERNAME" not in config_values

    @patch.dict(
        os.environ,
        {
            "YOUTRACK_BASE_URL": "https://example.youtrack.cloud",
            "YOUTRACK_TOKEN": "test-token-123",
            "YOUTRACK_USERNAME": "testuser",
        },
    )
    def test_load_credentials(self):
        """Test loading credentials from environment."""
        config = self.auth_manager.load_credentials()

        assert config is not None
        assert config.base_url == "https://example.youtrack.cloud"
        assert config.token == "test-token-123"
        assert config.username == "testuser"

    @patch.dict(
        os.environ,
        {
            "YOUTRACK_BASE_URL": "https://example.youtrack.cloud",
            "YOUTRACK_TOKEN": "test-token-123",
        },
    )
    @patch("youtrack_cli.auth.load_dotenv")
    def test_load_credentials_without_username(self, mock_load_dotenv):
        """Test loading credentials without username."""
        config = self.auth_manager.load_credentials()

        assert config is not None
        assert config.base_url == "https://example.youtrack.cloud"
        assert config.token == "test-token-123"
        assert config.username is None

    @patch.dict(os.environ, {}, clear=True)
    @patch("youtrack_cli.security.keyring")
    def test_load_credentials_missing(self, mock_keyring):
        """Test loading credentials when none exist."""
        # Mock keyring to return None (no stored credentials)
        mock_keyring.get_password.return_value = None
        config = self.auth_manager.load_credentials()
        assert config is None

    @patch.dict(os.environ, {"YOUTRACK_BASE_URL": "https://example.youtrack.cloud"})
    @patch("youtrack_cli.security.keyring")
    def test_load_credentials_incomplete(self, mock_keyring):
        """Test loading incomplete credentials."""
        # Mock keyring to return None (no stored credentials)
        mock_keyring.get_password.return_value = None
        config = self.auth_manager.load_credentials()
        assert config is None

    def test_clear_credentials(self):
        """Test clearing credentials."""
        # Create config file with auth-related data
        config_manager = ConfigManager(self.config_path)
        config_manager.set_config("YOUTRACK_TOKEN", "test-token")
        config_manager.set_config("YOUTRACK_BASE_URL", "https://example.youtrack.cloud")
        config_manager.set_config("OTHER_CONFIG", "should_remain")

        assert os.path.exists(self.config_path)

        self.auth_manager.clear_credentials()

        # File should still exist but auth keys should be removed
        assert os.path.exists(self.config_path)
        config_values = config_manager.list_config()
        assert "YOUTRACK_TOKEN" not in config_values
        assert "YOUTRACK_BASE_URL" not in config_values
        assert config_values.get("OTHER_CONFIG") == "should_remain"

    def test_clear_credentials_no_file(self):
        """Test clearing credentials when no file exists."""
        # ConfigManager will create the file, so let's remove it first
        if os.path.exists(self.config_path):
            os.remove(self.config_path)

        # Should not raise an error even if file doesn't exist
        self.auth_manager.clear_credentials()

        # File will be created by ConfigManager but should be empty
        config_manager = ConfigManager(self.config_path)
        config_values = config_manager.list_config()
        assert "YOUTRACK_TOKEN" not in config_values
        assert "YOUTRACK_BASE_URL" not in config_values

    @pytest.mark.asyncio
    async def test_verify_credentials_success(self):
        """Test successful credential verification."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "login": "testuser",
            "fullName": "Test User",
            "email": "test@example.com",
        }
        mock_response.raise_for_status.return_value = None

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)

            result = await self.auth_manager.verify_credentials("https://example.youtrack.cloud", "test-token-123")

        assert result.status == "success"
        assert result.username == "testuser"
        assert result.full_name == "Test User"
        assert result.email == "test@example.com"

    @pytest.mark.asyncio
    async def test_verify_credentials_failure(self):
        """Test failed credential verification."""
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(side_effect=Exception("HTTP Error"))

            result = await self.auth_manager.verify_credentials("https://example.youtrack.cloud", "invalid-token")

        assert result.status == "error"
        assert "HTTP Error" in result.message

    @patch("youtrack_cli.auth.CredentialManager")
    def test_save_credentials_with_keyring_persists_config(self, mock_cred_manager):
        """Test that save_credentials with keyring still persists non-sensitive config to .env."""
        # Mock the credential manager to simulate keyring storage
        mock_cred_manager_instance = MagicMock()
        mock_cred_manager.return_value = mock_cred_manager_instance

        # Create auth manager with keyring enabled
        auth_manager = AuthManager(self.config_path)
        auth_manager.credential_manager = mock_cred_manager_instance
        auth_manager.security_config.enable_credential_encryption = True

        # Save credentials with keyring enabled
        auth_manager.save_credentials(
            base_url="https://example.youtrack.cloud",
            token="test-token-123",
            username="testuser",
            verify_ssl=False,
            use_keyring=True,
        )

        # Check that non-sensitive config was persisted to .env
        config_manager = ConfigManager(self.config_path)
        config_values = config_manager.list_config()

        assert config_values.get("YOUTRACK_BASE_URL") == "https://example.youtrack.cloud"
        assert config_values.get("YOUTRACK_USERNAME") == "testuser"
        assert config_values.get("YOUTRACK_VERIFY_SSL") == "false"
        assert config_values.get("YOUTRACK_API_KEY") == "[Stored in keyring]"

    def test_save_credentials_ssl_verification_persisted(self):
        """Test that SSL verification preference is persisted correctly."""
        # Test with SSL verification disabled
        self.auth_manager.save_credentials(
            base_url="https://example.youtrack.cloud", token="test-token-123", verify_ssl=False, use_keyring=False
        )

        config_manager = ConfigManager(self.config_path)
        assert config_manager.get_config("YOUTRACK_VERIFY_SSL") == "false"

        # Test with SSL verification enabled (create new auth manager to ensure fresh read)
        self.auth_manager.save_credentials(
            base_url="https://example.youtrack.cloud", token="test-token-123", verify_ssl=True, use_keyring=False
        )

        # Re-read config to ensure it's updated
        config_manager2 = ConfigManager(self.config_path)
        assert config_manager2.get_config("YOUTRACK_VERIFY_SSL") == "true"

    def test_clear_credentials_removes_config_keys(self):
        """Test that clear_credentials removes individual config keys instead of entire file."""
        # Set up some config values including non-auth related ones
        config_manager = ConfigManager(self.config_path)
        config_manager.set_config("YOUTRACK_BASE_URL", "https://example.youtrack.cloud")
        config_manager.set_config("YOUTRACK_TOKEN", "test-token")
        config_manager.set_config("YOUTRACK_USERNAME", "testuser")
        config_manager.set_config("YOUTRACK_VERIFY_SSL", "false")
        config_manager.set_config("YOUTRACK_API_KEY", "[Stored in keyring]")
        config_manager.set_config("OTHER_CONFIG", "should_remain")

        # Clear credentials
        self.auth_manager.clear_credentials()

        # Check that auth-related keys are removed but other keys remain
        config_values = config_manager.list_config()
        assert "YOUTRACK_BASE_URL" not in config_values
        assert "YOUTRACK_TOKEN" not in config_values
        assert "YOUTRACK_USERNAME" not in config_values
        assert "YOUTRACK_VERIFY_SSL" not in config_values
        assert "YOUTRACK_API_KEY" not in config_values
        assert config_values.get("OTHER_CONFIG") == "should_remain"
