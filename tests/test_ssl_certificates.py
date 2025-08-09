"""Tests for SSL certificate support in YouTrack CLI."""

import os
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from click.testing import CliRunner

from youtrack_cli.auth import AuthManager
from youtrack_cli.client import HTTPClientManager
from youtrack_cli.main import main


class TestSSLCertificateSupport:
    """Test SSL certificate functionality."""

    @pytest.fixture
    def temp_cert_file(self):
        """Create a temporary certificate file for testing."""
        with tempfile.NamedTemporaryFile(suffix=".pem", delete=False) as f:
            f.write(b"-----BEGIN CERTIFICATE-----\n")
            f.write(b"MIIDXTCCAkWgAwIBAgIJAKLdQVPy90NAaMA0GCSqGSIb3DQEBCwUAMEUxCzAJBgNV\n")
            f.write(b"-----END CERTIFICATE-----\n")
            cert_path = f.name
        yield cert_path
        os.unlink(cert_path)

    @pytest.fixture
    def temp_ca_bundle(self):
        """Create a temporary CA bundle file for testing."""
        with tempfile.NamedTemporaryFile(suffix=".crt", delete=False) as f:
            f.write(b"-----BEGIN CERTIFICATE-----\n")
            f.write(b"CA BUNDLE CONTENT\n")
            f.write(b"-----END CERTIFICATE-----\n")
            bundle_path = f.name
        yield bundle_path
        os.unlink(bundle_path)

    @pytest.mark.asyncio
    async def test_auth_manager_with_missing_cert_file(self):
        """Test AuthManager handles missing certificate files correctly."""
        auth_manager = AuthManager()

        result = await auth_manager.verify_credentials(
            "https://example.com", "test-token", verify_ssl="/nonexistent/cert.pem"
        )

        assert result.status == "error"
        assert "SSL certificate file not found" in result.message

    @pytest.mark.asyncio
    async def test_auth_manager_with_cert_file(self, temp_cert_file):
        """Test AuthManager with valid certificate file path."""
        auth_manager = AuthManager()

        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "login": "testuser",
                "fullName": "Test User",
                "email": "test@example.com",
            }
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)

            await auth_manager.verify_credentials("https://example.com", "test-token", verify_ssl=temp_cert_file)

            # Verify SSL verify parameter was set to cert file path
            mock_client.assert_called_once()
            call_kwargs = mock_client.call_args[1]
            assert call_kwargs["verify"] == temp_cert_file

    @pytest.mark.asyncio
    async def test_auth_manager_ssl_error_handling(self):
        """Test AuthManager provides helpful SSL error messages."""
        auth_manager = AuthManager()

        with patch("httpx.AsyncClient") as mock_client:
            # Simulate SSL certificate verification error
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                side_effect=Exception("certificate verify failed: unable to get local issuer certificate")
            )

            result = await auth_manager.verify_credentials("https://example.com", "test-token", verify_ssl=True)

            assert result.status == "error"
            assert "SSL certificate verification failed" in result.message
            assert "Use --ca-bundle" in result.message
            assert "Use --cert-file" in result.message
            assert "--no-verify-ssl" in result.message

    @pytest.mark.skip(reason="CLI integration test has complex mocking requirements")
    def test_auth_login_with_cert_file(self, temp_cert_file):
        """Test auth login command with certificate file."""
        pass

    @pytest.mark.skip(reason="CLI integration test has complex mocking requirements")
    def test_auth_login_with_ca_bundle(self, temp_ca_bundle):
        """Test auth login command with CA bundle."""
        pass

    @pytest.mark.skip(reason="CLI integration test has complex mocking requirements")
    def test_auth_login_no_verify_ssl(self):
        """Test auth login command with SSL verification disabled."""
        pass

    def test_auth_login_invalid_cert_file(self):
        """Test auth login with non-existent certificate file."""
        runner = CliRunner()
        result = runner.invoke(
            main,
            [
                "auth",
                "login",
                "--base-url",
                "https://test.youtrack.cloud",
                "--token",
                "test_token",
                "--cert-file",
                "/non/existent/cert.pem",
            ],
        )

        # Should fail because certificate file doesn't exist
        assert result.exit_code != 0
        assert "does not exist" in result.output or "File not found" in result.output

    @pytest.mark.asyncio
    async def test_auth_manager_verify_with_cert(self, temp_cert_file):
        """Test AuthManager verify_credentials with certificate file."""
        auth_manager = AuthManager()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "login": "test_user",
                "fullName": "Test User",
                "email": "test@example.com",
            }
            mock_response.raise_for_status = MagicMock()
            mock_client.get.return_value = mock_response

            result = await auth_manager.verify_credentials(
                "https://test.youtrack.cloud",
                "test_token",
                verify_ssl=temp_cert_file,
            )

            assert result.status == "success"
            assert result.username == "test_user"

            # Verify httpx client was created with certificate path
            mock_client_class.assert_called_once()
            call_kwargs = mock_client_class.call_args[1]
            assert call_kwargs["verify"] == temp_cert_file

    @pytest.mark.asyncio
    async def test_http_client_manager_with_cert(self, temp_cert_file):
        """Test HTTPClientManager initialization with certificate file."""
        manager = HTTPClientManager(verify_ssl=temp_cert_file)

        # Verify the certificate path is stored
        assert manager._verify_ssl == temp_cert_file

        # Test client creation with certificate
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = MagicMock()
            mock_client.is_closed = False
            mock_client_class.return_value = mock_client

            await manager._ensure_client()

            # Verify httpx.AsyncClient was called with certificate path
            mock_client_class.assert_called_once()
            call_kwargs = mock_client_class.call_args[1]
            assert call_kwargs["verify"] == temp_cert_file

    def test_config_storage_with_cert_paths(self, temp_cert_file, temp_ca_bundle):
        """Test that certificate paths are properly stored in configuration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / ".env"
            auth_manager = AuthManager(config_path=str(config_path))

            # Save credentials with certificate file
            auth_manager.save_credentials(
                base_url="https://test.youtrack.cloud",
                token="test_token",
                username="test_user",
                verify_ssl=temp_cert_file,
                cert_file=temp_cert_file,
                use_keyring=False,  # Use file storage for testing
            )

            # Read the config file
            with open(config_path) as f:
                config_content = f.read()

            assert "YOUTRACK_CERT_FILE=" in config_content
            assert temp_cert_file in config_content
            # The config stores as quoted string 'true', not unquoted true
            assert "YOUTRACK_VERIFY_SSL='true'" in config_content or "YOUTRACK_VERIFY_SSL=true" in config_content

    def test_environment_variable_cert_loading(self, temp_cert_file):
        """Test loading certificate path from environment variables."""
        with patch.dict(os.environ, {"YOUTRACK_CERT_FILE": temp_cert_file}):
            # Reset singleton for testing
            import youtrack_cli.client
            from youtrack_cli.client import get_client_manager

            youtrack_cli.client._client_manager = None

            with patch("youtrack_cli.client.HTTPClientManager") as mock_manager_class:
                get_client_manager()

                # Verify HTTPClientManager was initialized with certificate path
                mock_manager_class.assert_called_once()
                call_kwargs = mock_manager_class.call_args[1]
                assert call_kwargs["verify_ssl"] == temp_cert_file

    @pytest.mark.skip(reason="CLI integration test has complex mocking requirements")
    def test_deprecated_no_verify_ssl_flag(self):
        """Test that deprecated --no-verify-ssl flag still works."""
        pass
