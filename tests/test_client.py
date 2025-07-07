"""Tests for HTTP client manager with SSL verification warnings."""

import os
import warnings
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock, patch

import pytest

from youtrack_cli.client import HTTPClientManager, get_client_manager, reset_client_manager
from youtrack_cli.security import AuditLogger


class TestSSLVerificationWarnings:
    """Test SSL verification warnings and audit logging."""

    def setup_method(self):
        """Setup for each test method."""
        # Reset client manager before each test
        reset_client_manager()
        # Clear any warnings that might be cached
        warnings.resetwarnings()

    def teardown_method(self):
        """Cleanup after each test method."""
        # Reset client manager after each test
        reset_client_manager()
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

                # Check warning was issued
                assert len(warning_list) == 1
                assert "SSL verification is DISABLED" in str(warning_list[0].message)

    def test_ssl_verification_disabled_env_var_no(self):
        """Test SSL verification disabled via environment variable 'no'."""
        with patch.dict(os.environ, {"YOUTRACK_VERIFY_SSL": "no"}):
            with warnings.catch_warnings(record=True) as warning_list:
                warnings.simplefilter("always")

                manager = get_client_manager()

                # Check SSL verification is disabled
                assert manager._verify_ssl is False

                # Check warning was issued
                assert len(warning_list) == 1
                assert "SSL verification is DISABLED" in str(warning_list[0].message)

    def test_ssl_verification_disabled_env_var_off(self):
        """Test SSL verification disabled via environment variable 'off'."""
        with patch.dict(os.environ, {"YOUTRACK_VERIFY_SSL": "off"}):
            with warnings.catch_warnings(record=True) as warning_list:
                warnings.simplefilter("always")

                manager = get_client_manager()

                # Check SSL verification is disabled
                assert manager._verify_ssl is False

                # Check warning was issued
                assert len(warning_list) == 1
                assert "SSL verification is DISABLED" in str(warning_list[0].message)

    def test_ssl_verification_enabled_env_var_true(self):
        """Test SSL verification enabled via environment variable 'true'."""
        with patch.dict(os.environ, {"YOUTRACK_VERIFY_SSL": "true"}):
            with warnings.catch_warnings(record=True) as warning_list:
                warnings.simplefilter("always")

                manager = get_client_manager()

                # Check SSL verification is enabled
                assert manager._verify_ssl is True

                # Check no warning was issued
                assert len(warning_list) == 0

    def test_ssl_verification_enabled_env_var_one(self):
        """Test SSL verification enabled via environment variable '1'."""
        with patch.dict(os.environ, {"YOUTRACK_VERIFY_SSL": "1"}):
            with warnings.catch_warnings(record=True) as warning_list:
                warnings.simplefilter("always")

                manager = get_client_manager()

                # Check SSL verification is enabled
                assert manager._verify_ssl is True

                # Check no warning was issued
                assert len(warning_list) == 0

    def test_ssl_verification_enabled_env_var_yes(self):
        """Test SSL verification enabled via environment variable 'yes'."""
        with patch.dict(os.environ, {"YOUTRACK_VERIFY_SSL": "yes"}):
            with warnings.catch_warnings(record=True) as warning_list:
                warnings.simplefilter("always")

                manager = get_client_manager()

                # Check SSL verification is enabled
                assert manager._verify_ssl is True

                # Check no warning was issued
                assert len(warning_list) == 0

    def test_ssl_verification_case_insensitive(self):
        """Test that environment variable parsing is case insensitive."""
        with patch.dict(os.environ, {"YOUTRACK_VERIFY_SSL": "FALSE"}):
            with warnings.catch_warnings(record=True) as warning_list:
                warnings.simplefilter("always")

                manager = get_client_manager()

                # Check SSL verification is disabled
                assert manager._verify_ssl is False

                # Check warning was issued
                assert len(warning_list) == 1
                assert "SSL verification is DISABLED" in str(warning_list[0].message)

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

                # Check warning was issued with correct stacklevel
                assert len(warning_list) == 1
                warning = warning_list[0]

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
                assert len(warning_list) == 1

                # Second call should return same manager without additional warning
                manager2 = get_client_manager()
                assert manager1 is manager2
                assert len(warning_list) == 1  # No additional warning

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
            reset_client_manager()
            # Reset warnings system to ensure clean state
            warnings.resetwarnings()

            with patch.dict(os.environ, {"YOUTRACK_VERIFY_SSL": env_value}):
                with warnings.catch_warnings(record=True) as warning_list:
                    warnings.simplefilter("always")

                    manager = get_client_manager()

                    # Check SSL verification setting
                    assert manager._verify_ssl is expected_ssl, f"Failed for env_value: {env_value}"

                    # Check warning behavior
                    if should_warn:
                        assert len(warning_list) == 1, (
                            f"Expected warning for env_value: {env_value}, got {len(warning_list)} warnings"
                        )
                        assert "SSL verification is DISABLED" in str(warning_list[0].message)
                    else:
                        assert len(warning_list) == 0, (
                            f"Unexpected warning for env_value: {env_value}, got {len(warning_list)} warnings"
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
        with patch.dict(os.environ, {"YOUTRACK_VERIFY_SSL": "false"}):
            with warnings.catch_warnings(record=True) as warning_list:
                warnings.simplefilter("always")

                # Create first manager
                manager1 = get_client_manager()
                assert len(warning_list) == 1

                # Reset and create second manager
                reset_client_manager()
                manager2 = get_client_manager()

                # Should be a new instance and issue another warning
                assert manager1 is not manager2
                assert len(warning_list) == 2
