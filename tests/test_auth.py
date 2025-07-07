"""Tests for authentication functionality."""

import os
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import ValidationError

from youtrack_cli.auth import AuthConfig, AuthManager


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

        with open(self.config_path) as f:
            content = f.read()

        assert "YOUTRACK_BASE_URL=https://example.youtrack.cloud" in content
        assert "YOUTRACK_TOKEN=test-token-123" in content
        assert "YOUTRACK_USERNAME=testuser" in content

    def test_save_credentials_without_username(self):
        """Test saving credentials without username."""
        # Force file storage instead of keyring for this test
        self.auth_manager.save_credentials("https://example.youtrack.cloud", "test-token-123", use_keyring=False)

        with open(self.config_path) as f:
            content = f.read()

        assert "YOUTRACK_BASE_URL=https://example.youtrack.cloud" in content
        assert "YOUTRACK_TOKEN=test-token-123" in content
        assert "YOUTRACK_USERNAME" not in content

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
    def test_load_credentials_without_username(self):
        """Test loading credentials without username."""
        config = self.auth_manager.load_credentials()

        assert config is not None
        assert config.base_url == "https://example.youtrack.cloud"
        assert config.token == "test-token-123"
        assert config.username is None

    @patch.dict(os.environ, {}, clear=True)
    def test_load_credentials_missing(self):
        """Test loading credentials when none exist."""
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
        # Create config file
        with open(self.config_path, "w") as f:
            f.write("YOUTRACK_TOKEN=test-token")

        assert os.path.exists(self.config_path)

        self.auth_manager.clear_credentials()

        assert not os.path.exists(self.config_path)

    def test_clear_credentials_no_file(self):
        """Test clearing credentials when no file exists."""
        assert not os.path.exists(self.config_path)

        # Should not raise an error
        self.auth_manager.clear_credentials()

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
