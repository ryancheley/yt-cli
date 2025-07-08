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


class TestSSLVerificationWarnings:
    """Test SSL verification warnings and audit logging."""

    def setup_method(self):
        """Setup for each test method."""
        # Reset client manager before each test
        reset_client_manager_sync()
        # Clear any warnings that might be cached
        warnings.resetwarnings()

    def teardown_method(self):
        """Cleanup after each test method."""
        # Reset client manager after each test
        reset_client_manager_sync()
        # Clear any warnings that might be cached
        warnings.resetwarnings()

    def test_ssl_verification_enabled_by_default(self):
        """Test that SSL verification is enabled by default."""
        with patch.dict(os.environ, {}, clear=True):
            # Remove YOUTRACK_VERIFY_SSL if it exists
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

                # Check SSL verification is disabled
                assert manager._verify_ssl is False

                # Check warning was issued
                assert len(warning_list) == 1
                assert issubclass(warning_list[0].category, UserWarning)
                assert "SSL verification is DISABLED" in str(warning_list[0].message)
                assert "insecure" in str(warning_list[0].message).lower()

    def test_ssl_verification_disabled_env_var_zero(self):
        """Test SSL verification disabled via environment variable '0'."""
        with patch.dict(os.environ, {"YOUTRACK_VERIFY_SSL": "0"}):
            with warnings.catch_warnings(record=True) as warning_list:
                warnings.simplefilter("always")

                manager = get_client_manager()

                # Check SSL verification is disabled
                assert manager._verify_ssl is False

                # Check warning was issued (filter for UserWarnings only)
                user_warnings = [w for w in warning_list if issubclass(w.category, UserWarning)]
                assert len(user_warnings) == 1
                assert "SSL verification is DISABLED" in str(user_warnings[0].message)

    def test_ssl_verification_disabled_env_var_no(self):
        """Test SSL verification disabled via environment variable 'no'."""
        with patch.dict(os.environ, {"YOUTRACK_VERIFY_SSL": "no"}):
            with warnings.catch_warnings(record=True) as warning_list:
                warnings.simplefilter("always")

                manager = get_client_manager()

                # Check SSL verification is disabled
                assert manager._verify_ssl is False

                # Check warning was issued (filter for UserWarnings only)
                user_warnings = [w for w in warning_list if issubclass(w.category, UserWarning)]
                assert len(user_warnings) == 1
                assert "SSL verification is DISABLED" in str(user_warnings[0].message)

    def test_ssl_verification_disabled_env_var_off(self):
        """Test SSL verification disabled via environment variable 'off'."""
        with patch.dict(os.environ, {"YOUTRACK_VERIFY_SSL": "off"}):
            with warnings.catch_warnings(record=True) as warning_list:
                warnings.simplefilter("always")

                manager = get_client_manager()

                # Check SSL verification is disabled
                assert manager._verify_ssl is False

                # Check warning was issued (filter for UserWarnings only)
                user_warnings = [w for w in warning_list if issubclass(w.category, UserWarning)]
                assert len(user_warnings) == 1
                assert "SSL verification is DISABLED" in str(user_warnings[0].message)

    def test_ssl_verification_enabled_env_var_true(self):
        """Test SSL verification enabled via environment variable 'true'."""
        with patch.dict(os.environ, {"YOUTRACK_VERIFY_SSL": "true"}):
            with warnings.catch_warnings(record=True) as warning_list:
                warnings.simplefilter("always")

                manager = get_client_manager()

                # Check SSL verification is enabled
                assert manager._verify_ssl is True

                # Check no warning was issued (filter for UserWarnings only)
                user_warnings = [w for w in warning_list if issubclass(w.category, UserWarning)]
                assert len(user_warnings) == 0

    def test_ssl_verification_enabled_env_var_one(self):
        """Test SSL verification enabled via environment variable '1'."""
        with patch.dict(os.environ, {"YOUTRACK_VERIFY_SSL": "1"}):
            with warnings.catch_warnings(record=True) as warning_list:
                warnings.simplefilter("always")

                manager = get_client_manager()

                # Check SSL verification is enabled
                assert manager._verify_ssl is True

                # Check no warning was issued (filter for UserWarnings only)
                user_warnings = [w for w in warning_list if issubclass(w.category, UserWarning)]
                assert len(user_warnings) == 0

    def test_ssl_verification_enabled_env_var_yes(self):
        """Test SSL verification enabled via environment variable 'yes'."""
        with patch.dict(os.environ, {"YOUTRACK_VERIFY_SSL": "yes"}):
            with warnings.catch_warnings(record=True) as warning_list:
                warnings.simplefilter("always")

                manager = get_client_manager()

                # Check SSL verification is enabled
                assert manager._verify_ssl is True

                # Check no warning was issued (filter for UserWarnings only)
                user_warnings = [w for w in warning_list if issubclass(w.category, UserWarning)]
                assert len(user_warnings) == 0

    def test_ssl_verification_case_insensitive(self):
        """Test that environment variable parsing is case insensitive."""
        with patch.dict(os.environ, {"YOUTRACK_VERIFY_SSL": "FALSE"}):
            with warnings.catch_warnings(record=True) as warning_list:
                warnings.simplefilter("always")

                manager = get_client_manager()

                # Check SSL verification is disabled
                assert manager._verify_ssl is False

                # Check warning was issued (filter for UserWarnings only)
                user_warnings = [w for w in warning_list if issubclass(w.category, UserWarning)]
                assert len(user_warnings) == 1
                assert "SSL verification is DISABLED" in str(user_warnings[0].message)

    def test_audit_logging_ssl_verification_enabled(self):
        """Test audit logging when SSL verification is enabled."""
        with TemporaryDirectory():
            with patch.dict(os.environ, {"YOUTRACK_VERIFY_SSL": "true"}):
                with patch("youtrack_cli.security.AuditLogger") as mock_audit_logger_class:
                    mock_audit_logger = MagicMock()
                    mock_audit_logger_class.return_value = mock_audit_logger

                    manager = get_client_manager()

                    # Verify audit logger was called
                    mock_audit_logger_class.assert_called_once()
                    mock_audit_logger.log_command.assert_called_once_with(
                        command="ssl_verification_config",
                        arguments=["YOUTRACK_VERIFY_SSL=true", "verify_ssl=True"],
                        user=None,
                        success=True,
                    )

                    # Verify SSL verification is enabled
                    assert manager._verify_ssl is True

    def test_audit_logging_ssl_verification_disabled(self):
        """Test audit logging when SSL verification is disabled."""
        with TemporaryDirectory():
            with patch.dict(os.environ, {"YOUTRACK_VERIFY_SSL": "false"}):
                with patch("youtrack_cli.security.AuditLogger") as mock_audit_logger_class:
                    mock_audit_logger = MagicMock()
                    mock_audit_logger_class.return_value = mock_audit_logger

                    with warnings.catch_warnings(record=True):
                        warnings.simplefilter("always")

                        manager = get_client_manager()

                        # Verify audit logger was called
                        mock_audit_logger_class.assert_called_once()
                        mock_audit_logger.log_command.assert_called_once_with(
                            command="ssl_verification_config",
                            arguments=["YOUTRACK_VERIFY_SSL=false", "verify_ssl=False"],
                            user=None,
                            success=True,
                        )

                        # Verify SSL verification is disabled
                        assert manager._verify_ssl is False

    def test_audit_logging_ssl_verification_default(self):
        """Test audit logging when SSL verification uses default value."""
        with TemporaryDirectory():
            with patch.dict(os.environ, {}, clear=True):
                # Remove YOUTRACK_VERIFY_SSL if it exists
                if "YOUTRACK_VERIFY_SSL" in os.environ:
                    del os.environ["YOUTRACK_VERIFY_SSL"]

                with patch("youtrack_cli.security.AuditLogger") as mock_audit_logger_class:
                    mock_audit_logger = MagicMock()
                    mock_audit_logger_class.return_value = mock_audit_logger

                    manager = get_client_manager()

                    # Verify audit logger was called
                    mock_audit_logger_class.assert_called_once()
                    mock_audit_logger.log_command.assert_called_once_with(
                        command="ssl_verification_config",
                        arguments=["YOUTRACK_VERIFY_SSL=true", "verify_ssl=True"],
                        user=None,
                        success=True,
                    )

                    # Verify SSL verification is enabled
                    assert manager._verify_ssl is True

    def test_warning_stacklevel_correct(self):
        """Test that warning stacklevel is set correctly."""
        with patch.dict(os.environ, {"YOUTRACK_VERIFY_SSL": "false"}):
            with warnings.catch_warnings(record=True) as warning_list:
                warnings.simplefilter("always")

                get_client_manager()

                # Check warning was issued with correct stacklevel (filter for UserWarnings only)
                user_warnings = [w for w in warning_list if issubclass(w.category, UserWarning)]
                assert len(user_warnings) == 1
                warning = user_warnings[0]

                # The warning should point to the call to get_client_manager()
                # rather than the internal implementation
                assert warning.filename.endswith("test_client.py")
                assert warning.lineno > 0

    def test_client_manager_singleton_behavior(self):
        """Test that client manager maintains singleton behavior with SSL warnings."""
        with patch.dict(os.environ, {"YOUTRACK_VERIFY_SSL": "false"}):
            with warnings.catch_warnings(record=True) as warning_list:
                warnings.simplefilter("always")

                # First call should create manager and issue warning
                manager1 = get_client_manager()
                user_warnings = [w for w in warning_list if issubclass(w.category, UserWarning)]
                assert len(user_warnings) == 1

                # Second call should return same manager without additional warning
                manager2 = get_client_manager()
                assert manager1 is manager2
                user_warnings = [w for w in warning_list if issubclass(w.category, UserWarning)]
                assert len(user_warnings) == 1  # No additional warning

    def test_client_manager_logging_info(self):
        """Test that client manager logs initialization information."""
        with patch.dict(os.environ, {"YOUTRACK_VERIFY_SSL": "false"}):
            with patch("youtrack_cli.client.logger") as mock_logger:
                with warnings.catch_warnings(record=True):
                    warnings.simplefilter("always")

                    get_client_manager()

                    # Verify info logging was called
                    mock_logger.info.assert_called_once_with(
                        "HTTP client manager initialized", verify_ssl=False, env_var="false"
                    )

    def test_multiple_environment_values(self):
        """Test various environment variable values for SSL verification."""
        test_cases = [
            # (env_value, expected_ssl_verification, should_warn)
            ("false", False, True),
            ("0", False, True),
            ("no", False, True),
            ("off", False, True),
            ("FALSE", False, True),
            ("Off", False, True),
            ("true", True, False),
            ("1", True, False),
            ("yes", True, False),
            ("on", True, False),
            ("TRUE", True, False),
            ("anything_else", True, False),
            ("", True, False),
        ]

        for env_value, expected_ssl, should_warn in test_cases:
            # Reset client manager for each test iteration
            reset_client_manager_sync()
            # Reset warnings system to ensure clean state
            warnings.resetwarnings()

            with patch.dict(os.environ, {"YOUTRACK_VERIFY_SSL": env_value}):
                with warnings.catch_warnings(record=True) as warning_list:
                    warnings.simplefilter("always")

                    manager = get_client_manager()

                    # Check SSL verification setting
                    assert manager._verify_ssl is expected_ssl, f"Failed for env_value: {env_value}"

                    # Check warning behavior
                    ssl_warnings = [w for w in warning_list if "SSL verification is DISABLED" in str(w.message)]
                    if should_warn:
                        assert len(ssl_warnings) == 1, (
                            f"Expected 1 SSL warning for env_value: {env_value}, got {len(ssl_warnings)}"
                        )
                    else:
                        assert len(ssl_warnings) == 0, (
                            f"Unexpected SSL warning for env_value: {env_value}, got {len(ssl_warnings)}"
                        )


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

    def test_init_default_ssl_verification(self):
        """Test HTTPClientManager initialization with default SSL verification."""
        manager = HTTPClientManager()
        assert manager._verify_ssl is True  # Default should be True

    @pytest.mark.asyncio
    async def test_ensure_client_with_ssl_verification(self):
        """Test that _ensure_client uses SSL verification setting."""
        manager = HTTPClientManager(verify_ssl=False)

        # Mock httpx.AsyncClient to verify verify parameter
        with patch("youtrack_cli.client.httpx.AsyncClient") as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            mock_client.is_closed = False

            await manager._ensure_client()

            # Verify httpx.AsyncClient was called with correct verify parameter
            mock_client_class.assert_called_once()
            call_args = mock_client_class.call_args
            assert call_args[1]["verify"] is False

    @pytest.mark.asyncio
    async def test_ensure_client_ssl_verification_enabled(self):
        """Test that _ensure_client uses SSL verification when enabled."""
        manager = HTTPClientManager(verify_ssl=True)

        # Mock httpx.AsyncClient to verify verify parameter
        with patch("youtrack_cli.client.httpx.AsyncClient") as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            mock_client.is_closed = False

            await manager._ensure_client()

            # Verify httpx.AsyncClient was called with correct verify parameter
            mock_client_class.assert_called_once()
            call_args = mock_client_class.call_args
            assert call_args[1]["verify"] is True


class TestSecurityIntegration:
    """Test security integration aspects."""

    def test_audit_logger_import(self):
        """Test that AuditLogger can be imported and used."""

        # This should not raise any import errors
        logger = AuditLogger()
        assert logger is not None

    def test_client_manager_reset_functionality(self):
        """Test reset_client_manager functionality."""
        # Ensure clean state
        reset_client_manager_sync()
        warnings.resetwarnings()

        with patch.dict(os.environ, {"YOUTRACK_VERIFY_SSL": "false"}):
            # Test first manager creation
            with warnings.catch_warnings(record=True) as warning_list1:
                warnings.simplefilter("always")
                manager1 = get_client_manager()
                ssl_warnings1 = [w for w in warning_list1 if "SSL verification is DISABLED" in str(w.message)]

            # Reset and test second manager creation
            reset_client_manager_sync()
            with warnings.catch_warnings(record=True) as warning_list2:
                warnings.simplefilter("always")
                manager2 = get_client_manager()
                ssl_warnings2 = [w for w in warning_list2 if "SSL verification is DISABLED" in str(w.message)]

            # Verify behavior
            assert manager1 is not manager2, "Managers should be different instances after reset"
            assert len(ssl_warnings1) >= 1, f"Expected at least 1 SSL warning in first call, got {len(ssl_warnings1)}"
            assert len(ssl_warnings2) >= 1, f"Expected at least 1 SSL warning in second call, got {len(ssl_warnings2)}"

    @pytest.mark.asyncio
    async def test_reset_client_manager_async_cleanup(self):
        """Test that reset_client_manager properly closes connections."""
        from youtrack_cli.client import reset_client_manager

        # Ensure clean state
        reset_client_manager_sync()

        # Get a manager and ensure it has a client
        manager = get_client_manager()
        async with manager.get_client() as client:
            assert client is not None
            assert not client.is_closed

        # Reset asynchronously and verify cleanup
        await reset_client_manager()

        # Verify the client was closed
        assert manager._client is None or manager._client.is_closed

    @pytest.mark.asyncio
    async def test_reset_client_manager_cleanup_error_handling(self):
        """Test that reset_client_manager handles cleanup errors gracefully."""
        from youtrack_cli.client import reset_client_manager

        # Ensure clean state
        reset_client_manager_sync()

        # Get a manager
        manager = get_client_manager()

        # Mock the close method to raise an exception
        with patch.object(manager, "close", side_effect=Exception("Test cleanup error")):
            # This should not raise an exception
            await reset_client_manager()

        # Verify the manager was still reset despite the error
        from youtrack_cli.client import _client_manager

        assert _client_manager is None

    def test_reset_client_manager_sync_compatibility(self):
        """Test backwards compatibility of reset_client_manager_sync."""
        # Ensure clean state
        reset_client_manager_sync()

        # Get a manager
        manager1 = get_client_manager()

        # Reset using sync version
        reset_client_manager_sync()

        # Get a new manager
        manager2 = get_client_manager()

        # Verify they are different instances
        assert manager1 is not manager2

    def test_reset_client_manager_sync_without_event_loop(self):
        """Test reset_client_manager_sync when no event loop is running."""
        # Ensure clean state
        reset_client_manager_sync()

        # Get a manager to ensure something exists to reset
        get_client_manager()

        # This should work without an event loop
        reset_client_manager_sync()

        # Verify cleanup occurred
        from youtrack_cli.client import _client_manager

        assert _client_manager is None


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

        # Mock asyncio.sleep to eliminate wait times
        with patch("asyncio.sleep") as mock_sleep:
            with patch.object(manager, "get_client") as mock_get_client:
                mock_client = AsyncMock()
                mock_get_client.return_value.__aenter__.return_value = mock_client

                # Mock request to raise a network error
                mock_client.request = AsyncMock(side_effect=httpx.RequestError("Network error"))

                with pytest.raises(YouTrackNetworkError) as exc_info:
                    await manager.make_request("GET", "https://test.com")

                # Verify the error message includes retry information
                assert "Network error after 3 retries" in str(exc_info.value)
                # Verify it retried max_retries times (4 attempts total: initial + 3 retries)
                assert mock_client.request.call_count == 4
                # Verify sleep was called for retries (3 times)
                assert mock_sleep.call_count == 3

    @pytest.mark.asyncio
    async def test_timeout_error_retry_and_failure(self):
        """Test timeout error handling with retry and eventual failure."""
        manager = HTTPClientManager()

        # Mock asyncio.sleep to eliminate wait times
        with patch("asyncio.sleep") as mock_sleep:
            with patch.object(manager, "get_client") as mock_get_client:
                mock_client = AsyncMock()
                mock_get_client.return_value.__aenter__.return_value = mock_client

                # Mock request to raise a timeout error
                mock_client.request = AsyncMock(side_effect=httpx.TimeoutException("Timeout"))

                with pytest.raises(ConnectionError) as exc_info:
                    await manager.make_request("GET", "https://test.com")

                # Verify the error message is about timeout
                assert "timed out" in str(exc_info.value)
                # Verify it retried max_retries times (4 attempts total: initial + 3 retries)
                assert mock_client.request.call_count == 4
                # Verify sleep was called for retries (3 times)
                assert mock_sleep.call_count == 3

    @pytest.mark.asyncio
    async def test_os_error_retry_and_failure(self):
        """Test OS error handling with retry and eventual failure."""
        manager = HTTPClientManager()

        # Mock asyncio.sleep to eliminate wait times
        with patch("asyncio.sleep") as mock_sleep:
            with patch.object(manager, "get_client") as mock_get_client:
                mock_client = AsyncMock()
                mock_get_client.return_value.__aenter__.return_value = mock_client

                # Mock request to raise an OS error
                mock_client.request = AsyncMock(side_effect=OSError("Network unavailable"))

                with pytest.raises(YouTrackNetworkError) as exc_info:
                    await manager.make_request("GET", "https://test.com")

                # Verify the error message includes retry information
                assert "Network error after 3 retries" in str(exc_info.value)
                # Verify it retried max_retries times (4 attempts total: initial + 3 retries)
                assert mock_client.request.call_count == 4
                # Verify sleep was called for retries (3 times)
                assert mock_sleep.call_count == 3

    @pytest.mark.asyncio
    async def test_server_error_retry_and_failure(self):
        """Test server error (5xx) handling with retry and eventual failure."""
        manager = HTTPClientManager()

        # Mock asyncio.sleep to eliminate wait times
        with patch("asyncio.sleep") as mock_sleep:
            with patch.object(manager, "get_client") as mock_get_client:
                mock_client = AsyncMock()
                mock_get_client.return_value.__aenter__.return_value = mock_client

                # Mock response for server error
                mock_response = MagicMock()
                mock_response.status_code = 500
                mock_response.text = "Internal Server Error"

                # Mock request to raise a server error
                mock_client.request = AsyncMock(
                    side_effect=httpx.HTTPStatusError("Server error", request=MagicMock(), response=mock_response)
                )

                with pytest.raises(YouTrackServerError) as exc_info:
                    await manager.make_request("GET", "https://test.com")

                # Verify the error message includes retry information
                assert "Server error after 3 retries" in str(exc_info.value)
                # Verify status code is captured
                assert cast(YouTrackServerError, exc_info.value).status_code == 500
                # Verify it retried max_retries times (4 attempts total: initial + 3 retries)
                assert mock_client.request.call_count == 4
                # Verify sleep was called for retries (3 times)
                assert mock_sleep.call_count == 3

    @pytest.mark.asyncio
    async def test_client_error_no_retry(self):
        """Test client error (4xx) handling - should not retry."""
        manager = HTTPClientManager()

        with patch.object(manager, "get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_get_client.return_value.__aenter__.return_value = mock_client

            # Mock response for client error
            mock_response = MagicMock()
            mock_response.status_code = 404
            mock_response.text = "Not Found"

            # Mock request to raise a client error
            mock_client.request = AsyncMock(
                side_effect=httpx.HTTPStatusError("Not found", request=MagicMock(), response=mock_response)
            )

            with pytest.raises(httpx.HTTPStatusError):
                await manager.make_request("GET", "https://test.com")

            # Verify it did not retry (only 1 attempt)
            assert mock_client.request.call_count == 1

    @pytest.mark.asyncio
    async def test_network_error_successful_retry(self):
        """Test successful retry after network error."""
        manager = HTTPClientManager()

        # Mock asyncio.sleep to eliminate wait times
        with patch("asyncio.sleep") as mock_sleep:
            with patch.object(manager, "get_client") as mock_get_client:
                mock_client = AsyncMock()
                mock_get_client.return_value.__aenter__.return_value = mock_client

                # Mock successful response
                mock_response = MagicMock()
                mock_response.status_code = 200

                # Mock request to fail first time, then succeed
                mock_client.request = AsyncMock(side_effect=[httpx.RequestError("Network error"), mock_response])

                result = await manager.make_request("GET", "https://test.com")

                # Verify the successful response was returned
                assert result == mock_response
                # Verify it retried once (2 attempts total)
                assert mock_client.request.call_count == 2
                # Verify sleep was called once for retry
                assert mock_sleep.call_count == 1

    @pytest.mark.asyncio
    async def test_unexpected_error_handling(self):
        """Test handling of truly unexpected errors."""
        manager = HTTPClientManager()

        with patch.object(manager, "get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_get_client.return_value.__aenter__.return_value = mock_client

            # Mock request to raise an unexpected error
            mock_client.request = AsyncMock(side_effect=ValueError("Unexpected error"))

            with pytest.raises(YouTrackError) as exc_info:
                await manager.make_request("GET", "https://test.com")

            # Verify the error message includes the unexpected error
            assert "Unexpected error" in str(exc_info.value)
            # Verify it did not retry (only 1 attempt)
            assert mock_client.request.call_count == 1

    @pytest.mark.asyncio
    async def test_logging_for_network_errors(self):
        """Test proper logging for network errors."""
        manager = HTTPClientManager()

        # Mock asyncio.sleep to eliminate wait times
        with patch("asyncio.sleep") as mock_sleep:
            with patch.object(manager, "get_client") as mock_get_client:
                mock_client = AsyncMock()
                mock_get_client.return_value.__aenter__.return_value = mock_client

                # Mock request to raise a network error
                mock_client.request = AsyncMock(side_effect=httpx.RequestError("Network error"))

                with patch("youtrack_cli.client.logger") as mock_logger:
                    with pytest.raises(YouTrackNetworkError):
                        await manager.make_request("GET", "https://test.com")

                    # Verify warning logs were created for retries
                    assert mock_logger.warning.call_count == 3  # 3 retry attempts after initial failure
                    # Verify error log was created after max retries
                    assert mock_logger.error.call_count == 1
                    # Verify sleep was called for retries (3 times)
                    assert mock_sleep.call_count == 3

                    # Check that error type is logged
                    warning_calls = mock_logger.warning.call_args_list
                    for call in warning_calls:
                        assert "error_type" in call[1]
                        assert call[1]["error_type"] == "RequestError"

    @pytest.mark.asyncio
    async def test_logging_for_unexpected_errors(self):
        """Test proper logging for unexpected errors."""
        manager = HTTPClientManager()

        with patch.object(manager, "get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_get_client.return_value.__aenter__.return_value = mock_client

            # Mock request to raise an unexpected error
            mock_client.request = AsyncMock(side_effect=ValueError("Unexpected error"))

            with patch("youtrack_cli.client.logger") as mock_logger:
                with pytest.raises(YouTrackError):
                    await manager.make_request("GET", "https://test.com")

                # Verify exception logging was called
                assert mock_logger.exception.call_count == 1

                # Check that error type is logged
                exception_call = mock_logger.exception.call_args
                assert "error_type" in exception_call[1]
                assert exception_call[1]["error_type"] == "ValueError"
