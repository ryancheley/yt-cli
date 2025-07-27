"""Tests for HTTP client manager with SSL verification warnings."""

import os
import warnings
from tempfile import TemporaryDirectory
from typing import cast
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from youtrack_cli.client import HTTPClientManager, get_client_manager, reset_client_manager_sync
from youtrack_cli.exceptions import ConnectionError, YouTrackError, YouTrackNetworkError, YouTrackServerError
from youtrack_cli.security import AuditLogger


@pytest.mark.unit
class TestSSLVerificationWarnings:
    """Test SSL verification warnings and audit logging."""

    def setup_method(self):
        """Setup for each test method."""
        reset_client_manager_sync()
        warnings.resetwarnings()

    def teardown_method(self):
        """Cleanup after each test method."""
        reset_client_manager_sync()
        warnings.resetwarnings()

    def test_ssl_verification_enabled_by_default(self):
        """Test that SSL verification is enabled by default."""
        with patch.dict(os.environ, {}, clear=True):
            if "YOUTRACK_VERIFY_SSL" in os.environ:
                del os.environ["YOUTRACK_VERIFY_SSL"]
            manager = get_client_manager()
            assert manager._verify_ssl is True

    def test_ssl_verification_disabled_env_var_false(self):
        """Test SSL verification disabled via environment variable 'false'."""
        with patch.dict(os.environ, {"YOUTRACK_VERIFY_SSL": "false"}):
            with warnings.catch_warnings(record=True) as warning_list:
                warnings.simplefilter("always")
                manager = get_client_manager()

                assert manager._verify_ssl is False
                user_warnings = [w for w in warning_list if issubclass(w.category, UserWarning)]
                assert len(user_warnings) == 1
                assert "SSL verification is DISABLED" in str(user_warnings[0].message)

    def test_ssl_verification_enabled_env_var_true(self):
        """Test SSL verification enabled via environment variable 'true'."""
        with patch.dict(os.environ, {"YOUTRACK_VERIFY_SSL": "true"}):
            with warnings.catch_warnings(record=True) as warning_list:
                warnings.simplefilter("always")
                manager = get_client_manager()

                assert manager._verify_ssl is True
                user_warnings = [w for w in warning_list if issubclass(w.category, UserWarning)]
                assert len(user_warnings) == 0

    def test_ssl_verification_case_insensitive(self):
        """Test that environment variable parsing is case insensitive."""
        with patch.dict(os.environ, {"YOUTRACK_VERIFY_SSL": "FALSE"}):
            with warnings.catch_warnings(record=True) as warning_list:
                warnings.simplefilter("always")
                manager = get_client_manager()

                assert manager._verify_ssl is False
                user_warnings = [w for w in warning_list if issubclass(w.category, UserWarning)]
                assert len(user_warnings) == 1

    def test_audit_logging_ssl_verification_enabled(self):
        """Test audit logging when SSL verification is enabled."""
        with TemporaryDirectory():
            with patch.dict(os.environ, {"YOUTRACK_VERIFY_SSL": "true"}):
                with patch("youtrack_cli.security.AuditLogger") as mock_audit_logger_class:
                    mock_audit_logger = MagicMock()
                    mock_audit_logger_class.return_value = mock_audit_logger

                    manager = get_client_manager()

                    mock_audit_logger_class.assert_called_once()
                    mock_audit_logger.log_command.assert_called_once_with(
                        command="ssl_verification_config",
                        arguments=["YOUTRACK_VERIFY_SSL=true", "verify_ssl=True"],
                        user=None,
                        success=True,
                    )
                    assert manager._verify_ssl is True

    def test_client_manager_singleton_behavior(self):
        """Test that client manager maintains singleton behavior with SSL warnings."""
        with patch.dict(os.environ, {"YOUTRACK_VERIFY_SSL": "false"}):
            with warnings.catch_warnings(record=True) as warning_list:
                warnings.simplefilter("always")

                manager1 = get_client_manager()
                user_warnings = [w for w in warning_list if issubclass(w.category, UserWarning)]
                assert len(user_warnings) == 1

                manager2 = get_client_manager()
                assert manager1 is manager2
                user_warnings = [w for w in warning_list if issubclass(w.category, UserWarning)]
                assert len(user_warnings) == 1  # No additional warning


@pytest.mark.unit
class TestTimeoutConfiguration:
    """Test timeout configuration functionality."""

    def setup_method(self):
        """Setup for each test method."""
        reset_client_manager_sync()

    def teardown_method(self):
        """Cleanup after each test method."""
        reset_client_manager_sync()

    def test_default_timeout_configuration(self):
        """Test default timeout values."""
        with patch.dict(os.environ, {}, clear=True):
            manager = get_client_manager()
            assert manager._default_timeout == 30.0
            assert manager._timeout.connect == 30.0
            assert manager._timeout.read == 30.0

    def test_custom_default_timeout_env_var(self):
        """Test custom default timeout from environment variable."""
        with patch.dict(os.environ, {"YOUTRACK_DEFAULT_TIMEOUT": "45.5"}):
            manager = get_client_manager()
            assert manager._default_timeout == 45.5
            assert manager._timeout.connect == 45.5

    def test_specific_timeout_env_vars(self):
        """Test specific timeout configuration from environment variables."""
        with patch.dict(
            os.environ,
            {
                "YOUTRACK_DEFAULT_TIMEOUT": "30.0",
                "YOUTRACK_CONNECT_TIMEOUT": "10.0",
                "YOUTRACK_READ_TIMEOUT": "60.0",
            },
        ):
            manager = get_client_manager()
            assert manager._default_timeout == 30.0
            assert manager._timeout.connect == 10.0
            assert manager._timeout.read == 60.0

    def test_invalid_timeout_values_warning(self):
        """Test handling of invalid timeout values with warnings."""
        reset_client_manager_sync()
        with patch.dict(os.environ, {"YOUTRACK_DEFAULT_TIMEOUT": "invalid"}):
            with patch("youtrack_cli.client.logger") as mock_logger:
                manager = get_client_manager()
                assert manager._default_timeout == 30.0  # Falls back to default
                warning_calls = [call for call in mock_logger.warning.call_args_list if "Invalid timeout" in str(call)]
                assert len(warning_calls) >= 1

    @pytest.mark.asyncio
    async def test_timeout_parameter_in_make_request(self):
        """Test that timeout parameter in make_request overrides default."""
        manager = HTTPClientManager(default_timeout=30.0)

        with patch.object(manager, "get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_get_client.return_value.__aenter__.return_value = mock_client

            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_client.request.return_value = mock_response

            await manager.make_request("GET", "https://test.com", timeout=15.0)

            mock_client.request.assert_called_once()
            call_args = mock_client.request.call_args
            assert call_args[1]["timeout"] == 15.0


@pytest.mark.unit
class TestHTTPClientManager:
    """Test HTTPClientManager class directly."""

    def test_init_with_ssl_verification_enabled(self):
        """Test HTTPClientManager initialization with SSL verification enabled."""
        manager = HTTPClientManager(verify_ssl=True)
        assert manager._verify_ssl is True

    def test_init_with_ssl_verification_disabled(self):
        """Test HTTPClientManager initialization with SSL verification disabled."""
        manager = HTTPClientManager(verify_ssl=False)
        assert manager._verify_ssl is False

    def test_init_with_custom_timeouts(self):
        """Test HTTPClientManager initialization with custom timeout values."""
        manager = HTTPClientManager(
            default_timeout=40.0,
            connect_timeout=12.0,
            read_timeout=50.0,
        )
        assert manager._default_timeout == 40.0
        assert manager._timeout.connect == 12.0
        assert manager._timeout.read == 50.0

    @pytest.mark.asyncio
    async def test_ensure_client_with_ssl_verification(self):
        """Test that _ensure_client uses SSL verification setting."""
        manager = HTTPClientManager(verify_ssl=False)

        with patch("youtrack_cli.client.httpx.AsyncClient") as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            mock_client.is_closed = False

            await manager._ensure_client()

            mock_client_class.assert_called_once()
            call_args = mock_client_class.call_args
            assert call_args[1]["verify"] is False


@pytest.mark.unit
class TestSecurityIntegration:
    """Test security integration aspects."""

    def test_audit_logger_import(self):
        """Test that AuditLogger can be imported and used."""
        logger = AuditLogger()
        assert logger is not None

    def test_client_manager_reset_functionality(self):
        """Test reset_client_manager functionality."""
        reset_client_manager_sync()
        warnings.resetwarnings()

        with patch.dict(os.environ, {"YOUTRACK_VERIFY_SSL": "false"}):
            with warnings.catch_warnings(record=True) as warning_list1:
                warnings.simplefilter("always")
                manager1 = get_client_manager()
                ssl_warnings1 = [w for w in warning_list1 if "SSL verification is DISABLED" in str(w.message)]

            reset_client_manager_sync()
            with warnings.catch_warnings(record=True) as warning_list2:
                warnings.simplefilter("always")
                manager2 = get_client_manager()
                ssl_warnings2 = [w for w in warning_list2 if "SSL verification is DISABLED" in str(w.message)]

            assert manager1 is not manager2
            assert len(ssl_warnings1) >= 1
            assert len(ssl_warnings2) >= 1

    @pytest.mark.asyncio
    async def test_reset_client_manager_async_cleanup(self):
        """Test that reset_client_manager properly closes connections."""
        from youtrack_cli.client import reset_client_manager

        reset_client_manager_sync()

        manager = get_client_manager()
        async with manager.get_client() as client:
            assert client is not None
            assert not client.is_closed

        await reset_client_manager()
        assert manager._client is None or manager._client.is_closed


@pytest.mark.unit
class TestExceptionHandling:
    """Test exception handling in HTTPClientManager."""

    def setup_method(self):
        """Setup for each test method."""
        reset_client_manager_sync()

    def teardown_method(self):
        """Cleanup after each test method."""
        reset_client_manager_sync()

    @pytest.mark.asyncio
    async def test_network_error_retry_and_failure(self):
        """Test network error handling with retry and eventual failure."""
        manager = HTTPClientManager()

        with patch("asyncio.sleep") as mock_sleep:
            with patch.object(manager, "get_client") as mock_get_client:
                mock_client = AsyncMock()
                mock_get_client.return_value.__aenter__.return_value = mock_client

                mock_client.request = AsyncMock(side_effect=httpx.RequestError("Network error"))

                with pytest.raises(YouTrackNetworkError) as exc_info:
                    await manager.make_request("GET", "https://test.com")

                assert "Network error after 3 retries" in str(exc_info.value)
                assert mock_client.request.call_count == 4
                assert mock_sleep.call_count == 3

    @pytest.mark.asyncio
    async def test_timeout_error_retry_and_failure(self):
        """Test timeout error handling with retry and eventual failure."""
        manager = HTTPClientManager()

        with patch("asyncio.sleep") as mock_sleep:
            with patch.object(manager, "get_client") as mock_get_client:
                mock_client = AsyncMock()
                mock_get_client.return_value.__aenter__.return_value = mock_client

                mock_client.request = AsyncMock(side_effect=httpx.TimeoutException("Timeout"))

                with pytest.raises(ConnectionError) as exc_info:
                    await manager.make_request("GET", "https://test.com")

                assert "timed out" in str(exc_info.value)
                assert mock_client.request.call_count == 4
                assert mock_sleep.call_count == 3

    @pytest.mark.asyncio
    async def test_server_error_retry_and_failure(self):
        """Test server error (5xx) handling with retry and eventual failure."""
        manager = HTTPClientManager()

        with patch("asyncio.sleep") as mock_sleep:
            with patch.object(manager, "get_client") as mock_get_client:
                mock_client = AsyncMock()
                mock_get_client.return_value.__aenter__.return_value = mock_client

                mock_response = MagicMock()
                mock_response.status_code = 500
                mock_response.text = "Internal Server Error"

                mock_client.request = AsyncMock(
                    side_effect=httpx.HTTPStatusError("Server error", request=MagicMock(), response=mock_response)
                )

                with pytest.raises(YouTrackServerError) as exc_info:
                    await manager.make_request("GET", "https://test.com")

                assert "Server error after 3 retries" in str(exc_info.value)
                assert cast(YouTrackServerError, exc_info.value).status_code == 500
                assert mock_client.request.call_count == 4
                assert mock_sleep.call_count == 3

    @pytest.mark.asyncio
    async def test_client_error_no_retry(self):
        """Test client error (4xx) handling - should not retry."""
        manager = HTTPClientManager()

        with patch.object(manager, "get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_get_client.return_value.__aenter__.return_value = mock_client

            mock_response = MagicMock()
            mock_response.status_code = 404
            mock_response.text = "Not Found"

            mock_client.request = AsyncMock(
                side_effect=httpx.HTTPStatusError("Not found", request=MagicMock(), response=mock_response)
            )

            with pytest.raises(httpx.HTTPStatusError):
                await manager.make_request("GET", "https://test.com")

            assert mock_client.request.call_count == 1

    @pytest.mark.asyncio
    async def test_network_error_successful_retry(self):
        """Test successful retry after network error."""
        manager = HTTPClientManager()

        with patch("asyncio.sleep") as mock_sleep:
            with patch.object(manager, "get_client") as mock_get_client:
                mock_client = AsyncMock()
                mock_get_client.return_value.__aenter__.return_value = mock_client

                mock_response = MagicMock()
                mock_response.status_code = 200

                mock_client.request = AsyncMock(side_effect=[httpx.RequestError("Network error"), mock_response])

                result = await manager.make_request("GET", "https://test.com")

                assert result == mock_response
                assert mock_client.request.call_count == 2
                assert mock_sleep.call_count == 1

    @pytest.mark.asyncio
    async def test_unexpected_error_handling(self):
        """Test handling of truly unexpected errors."""
        manager = HTTPClientManager()

        with patch.object(manager, "get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_get_client.return_value.__aenter__.return_value = mock_client

            mock_client.request = AsyncMock(side_effect=ValueError("Unexpected error"))

            with pytest.raises(YouTrackError) as exc_info:
                await manager.make_request("GET", "https://test.com")

            assert "Unexpected error" in str(exc_info.value)
            assert mock_client.request.call_count == 1
