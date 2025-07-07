"""Tests for security features."""

import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

from youtrack_cli.security import (
    AuditLogger,
    CredentialManager,
    SecurityConfig,
    TokenManager,
    mask_sensitive_output,
)


class TestSecurityConfig:
    """Test SecurityConfig model."""

    def test_default_config(self):
        """Test default configuration values."""
        config = SecurityConfig()
        assert config.enable_audit_logging is True
        assert config.enable_credential_encryption is True
        assert config.enable_token_expiration_warnings is True
        assert config.audit_log_max_entries == 1000
        assert config.token_warning_days == 7

    def test_custom_config(self):
        """Test custom configuration values."""
        config = SecurityConfig(
            enable_audit_logging=False,
            audit_log_max_entries=500,
            token_warning_days=14,
        )
        assert config.enable_audit_logging is False
        assert config.audit_log_max_entries == 500
        assert config.token_warning_days == 14


class TestAuditLogger:
    """Test AuditLogger functionality."""

    def test_init(self):
        """Test AuditLogger initialization."""
        logger = AuditLogger()
        assert logger.config.enable_audit_logging is True
        assert logger._audit_file.name == "audit.log"

    def test_mask_sensitive_args(self):
        """Test masking of sensitive arguments."""
        logger = AuditLogger()

        args = [
            "issues",
            "list",
            "--token=secret123",
            "--password=mypass",
            "--api-key=key456",
            "--normal=value",
        ]

        masked = logger._mask_sensitive_args(args)

        assert masked == [
            "issues",
            "list",
            "--***MASKED***",
            "--***MASKED***",
            "--***MASKED***",
            "--normal=value",
        ]

    def test_log_command(self):
        """Test command logging."""
        with tempfile.TemporaryDirectory() as temp_dir:
            logger = AuditLogger()
            logger._audit_file = Path(temp_dir) / "test_audit.log"

            logger.log_command(
                command="issues",
                arguments=["list", "--token=secret"],
                user="testuser",
                success=True,
            )

            # Verify log file was created and contains entry
            assert logger._audit_file.exists()

            entries = logger.get_audit_log()
            assert len(entries) == 1

            entry = entries[0]
            assert entry.command == "issues"
            assert entry.arguments == ["list", "--***MASKED***"]
            assert entry.user == "testuser"
            assert entry.success is True

    def test_log_command_disabled(self):
        """Test that logging is disabled when configured."""
        config = SecurityConfig(enable_audit_logging=False)
        logger = AuditLogger(config)

        with tempfile.TemporaryDirectory() as temp_dir:
            logger._audit_file = Path(temp_dir) / "test_audit.log"

            logger.log_command("test", ["arg"])

            # Should not create log file
            assert not logger._audit_file.exists()

    def test_audit_log_rotation(self):
        """Test audit log entry limit enforcement."""
        config = SecurityConfig(audit_log_max_entries=3)
        logger = AuditLogger(config)

        with tempfile.TemporaryDirectory() as temp_dir:
            logger._audit_file = Path(temp_dir) / "test_audit.log"

            # Add 5 entries
            for i in range(5):
                logger.log_command(f"command{i}", [f"arg{i}"])

            entries = logger.get_audit_log()

            # Should only keep the last 3
            assert len(entries) == 3
            assert entries[0].command == "command2"
            assert entries[2].command == "command4"


class TestCredentialManager:
    """Test CredentialManager functionality."""

    def test_init(self):
        """Test CredentialManager initialization."""
        manager = CredentialManager()
        assert manager.config.enable_credential_encryption is True

    @patch("youtrack_cli.security.keyring")
    def test_get_encryption_key_existing(self, mock_keyring):
        """Test retrieving existing encryption key."""
        mock_keyring.get_password.return_value = "test_key"

        manager = CredentialManager()
        key = manager._get_encryption_key()

        assert key == b"test_key"
        mock_keyring.get_password.assert_called_once()

    @patch("youtrack_cli.security.keyring")
    @patch("youtrack_cli.security.Fernet")
    def test_get_encryption_key_new(self, mock_fernet, mock_keyring):
        """Test generating new encryption key."""
        mock_keyring.get_password.return_value = None
        mock_fernet.generate_key.return_value = b"new_key"

        manager = CredentialManager()
        key = manager._get_encryption_key()

        assert key == b"new_key"
        mock_fernet.generate_key.assert_called_once()
        mock_keyring.set_password.assert_called_once()

    @patch("youtrack_cli.security.keyring")
    def test_encrypt_decrypt_credential(self, mock_keyring):
        """Test credential encryption and decryption."""
        # Use a fixed valid Fernet key to ensure consistent encryption/decryption
        test_key = "TlXEPFdKOmOEFMJpORrYqLQeYelqSXvO8aJRdNeFgBA="
        mock_keyring.get_password.return_value = test_key
        mock_keyring.set_password.return_value = None

        manager = CredentialManager()

        original = "secret_token_123"
        encrypted = manager.encrypt_credential(original)
        decrypted = manager.decrypt_credential(encrypted)

        assert encrypted != original
        assert decrypted == original

    def test_encrypt_disabled(self):
        """Test that encryption is bypassed when disabled."""
        config = SecurityConfig(enable_credential_encryption=False)
        manager = CredentialManager(config)

        original = "secret_token_123"
        encrypted = manager.encrypt_credential(original)
        decrypted = manager.decrypt_credential(encrypted)

        # Should return original value unchanged
        assert encrypted == original
        assert decrypted == original

    @patch("youtrack_cli.security.keyring")
    def test_store_retrieve_credential(self, mock_keyring):
        """Test storing and retrieving credentials."""
        mock_keyring.get_password.return_value = None  # No existing key
        mock_keyring.set_password.return_value = None

        manager = CredentialManager()

        # Store credential
        result = manager.store_credential("test_key", "test_value")
        assert result is True

        # Mock keyring returning the encrypted value
        # This is a simplified test - in reality, the value would be encrypted
        mock_keyring.get_password.return_value = "test_value"

        # Retrieve credential
        retrieved = manager.retrieve_credential("test_key")
        assert retrieved == "test_value"

    @patch("youtrack_cli.security.keyring")
    def test_delete_credential(self, mock_keyring):
        """Test deleting credentials."""
        mock_keyring.delete_password.return_value = None

        manager = CredentialManager()
        result = manager.delete_credential("test_key")

        assert result is True
        mock_keyring.delete_password.assert_called_once()


class TestTokenManager:
    """Test TokenManager functionality."""

    def test_init(self):
        """Test TokenManager initialization."""
        manager = TokenManager()
        assert manager.config.enable_token_expiration_warnings is True

    def test_check_token_expiration_valid(self):
        """Test token expiration check for valid token."""
        manager = TokenManager()
        future_date = datetime.now() + timedelta(days=30)

        result = manager.check_token_expiration(future_date)

        assert result["status"] == "valid"
        assert result["message"] is None
        assert result["days"] >= 29  # Account for timing variations

    def test_check_token_expiration_expiring(self):
        """Test token expiration check for expiring token."""
        config = SecurityConfig(token_warning_days=10)
        manager = TokenManager(config)
        expiring_date = datetime.now() + timedelta(days=5)

        result = manager.check_token_expiration(expiring_date)

        assert result["status"] == "expiring"
        assert "expires in" in result["message"]
        assert result["days"] >= 4 and result["days"] <= 5  # Account for timing variations

    def test_check_token_expiration_expired(self):
        """Test token expiration check for expired token."""
        manager = TokenManager()
        past_date = datetime.now() - timedelta(days=1)

        result = manager.check_token_expiration(past_date)

        assert result["status"] == "expired"
        assert "expired" in result["message"]
        assert result["days"] <= -1  # Account for timing variations

    def test_check_token_expiration_disabled(self):
        """Test token expiration check when disabled."""
        config = SecurityConfig(enable_token_expiration_warnings=False)
        manager = TokenManager(config)
        future_date = datetime.now() + timedelta(days=1)

        result = manager.check_token_expiration(future_date)

        assert result["status"] == "unknown"
        assert result["message"] is None

    def test_check_token_expiration_none(self):
        """Test token expiration check with None expiry."""
        manager = TokenManager()

        result = manager.check_token_expiration(None)

        assert result["status"] == "unknown"
        assert result["message"] is None

    def test_estimate_token_expiry(self):
        """Test token expiry estimation."""
        manager = TokenManager()

        # This is a placeholder implementation
        result = manager.estimate_token_expiry("some_token")

        assert result is None


class TestSensitiveDataMasking:
    """Test sensitive data masking functionality."""

    def test_mask_tokens(self):
        """Test masking of various token formats."""
        test_cases = [
            ('token="abc123"', 'token="***MASKED***"'),
            ("token=xyz789", "token=***MASKED***"),
            ("token: secret_key", "token: ***MASKED***"),
            ('api_key="my_key"', 'api_key="***MASKED***"'),
            ("api-key=another_key", "api-key=***MASKED***"),
            ("bearer abc123def", "bearer ***MASKED***"),
            ("BEARER token123", "BEARER ***MASKED***"),
        ]

        for original, expected in test_cases:
            result = mask_sensitive_output(original)
            assert result == expected

    def test_mask_passwords(self):
        """Test masking of password fields."""
        test_cases = [
            ('password="secret123"', 'password="***MASKED***"'),
            ("password=mypass", "password=***MASKED***"),
            ("password: hidden", "password: ***MASKED***"),
        ]

        for original, expected in test_cases:
            result = mask_sensitive_output(original)
            assert result == expected

    def test_mask_authorization(self):
        """Test masking of authorization headers."""
        test_cases = [
            (
                'authorization="Bearer token123"',
                'authorization="***MASKED*** token123"',
            ),
            ("authorization=Basic", "authorization=***MASKED***"),
        ]

        for original, expected in test_cases:
            result = mask_sensitive_output(original)
            assert result == expected

    def test_preserve_non_sensitive(self):
        """Test that non-sensitive data is preserved."""
        test_cases = [
            "username=john.doe",
            "url=https://example.com",
            "project=PROJECT-123",
            "This is a normal log message",
        ]

        for text in test_cases:
            result = mask_sensitive_output(text)
            assert result == text

    def test_mask_multiple_patterns(self):
        """Test masking multiple sensitive patterns in one string."""
        original = 'Config: token="secret123" password="mypass" username="john"'
        expected = 'Config: token="***MASKED***" password="***MASKED***" username="john"'

        result = mask_sensitive_output(original)
        assert result == expected

    def test_case_insensitive_masking(self):
        """Test that masking is case-insensitive."""
        test_cases = [
            ("TOKEN=secret", "TOKEN=***MASKED***"),
            ("Password=secret", "Password=***MASKED***"),
            ("API_KEY=secret", "API_KEY=***MASKED***"),
            ("BEARER secret", "BEARER ***MASKED***"),
        ]

        for original, expected in test_cases:
            result = mask_sensitive_output(original)
            assert result == expected


class TestSecurityIntegration:
    """Test integration between security components."""

    def test_audit_logger_masks_sensitive_data(self):
        """Test that audit logger automatically masks sensitive data."""
        logger = AuditLogger()

        with tempfile.TemporaryDirectory() as temp_dir:
            logger._audit_file = Path(temp_dir) / "test_audit.log"

            # Log command with sensitive data
            logger.log_command(
                command="auth",
                arguments=["login", "--token=secret123", "--password=mypass"],
                success=True,
            )

            entries = logger.get_audit_log()
            entry = entries[0]

            # Verify sensitive data is masked
            assert "--***MASKED***" in entry.arguments
            assert "secret123" not in str(entry.arguments)
            assert "mypass" not in str(entry.arguments)

    @patch("youtrack_cli.security.keyring")
    def test_auth_manager_integration(self, mock_keyring):
        """Test that AuthManager properly integrates with security features."""
        from datetime import datetime

        from youtrack_cli.auth import AuthManager

        # Mock keyring operations
        mock_keyring.get_password.return_value = None
        mock_keyring.set_password.return_value = None

        auth_manager = AuthManager()

        # Test saving credentials with security features
        test_expiry = datetime.now() + timedelta(days=30)
        auth_manager.save_credentials(
            base_url="https://test.youtrack.cloud",
            token="test_token_123",
            username="testuser",
            token_expiry=test_expiry,
            use_keyring=True,
        )

        # Verify keyring was called for credential storage
        assert mock_keyring.set_password.call_count >= 1


# Performance and stress tests
class TestSecurityPerformance:
    """Test performance aspects of security features."""

    def test_audit_log_performance(self):
        """Test audit logging performance with many entries."""
        logger = AuditLogger()

        with tempfile.TemporaryDirectory() as temp_dir:
            logger._audit_file = Path(temp_dir) / "performance_test.log"

            # Log many entries quickly
            import time

            start_time = time.time()

            for i in range(100):
                logger.log_command(f"command{i}", [f"arg{i}"])

            end_time = time.time()
            duration = end_time - start_time

            # Should complete quickly (adjust threshold as needed)
            assert duration < 5.0  # 5 seconds max for 100 entries

            # Verify all entries were logged
            entries = logger.get_audit_log()
            assert len(entries) == 100

    @patch("youtrack_cli.security.keyring")
    def test_encryption_performance(self, mock_keyring):
        """Test encryption/decryption performance."""
        # Use a fixed valid Fernet key to ensure consistent encryption/decryption
        test_key = "TlXEPFdKOmOEFMJpORrYqLQeYelqSXvO8aJRdNeFgBA="
        mock_keyring.get_password.return_value = test_key
        mock_keyring.set_password.return_value = None

        manager = CredentialManager()

        # Test encrypting/decrypting many values
        import time

        start_time = time.time()

        for i in range(50):
            original = f"secret_value_{i}"
            encrypted = manager.encrypt_credential(original)
            decrypted = manager.decrypt_credential(encrypted)
            assert decrypted == original

        end_time = time.time()
        duration = end_time - start_time

        # Should complete quickly
        assert duration < 3.0  # 3 seconds max for 50 encrypt/decrypt cycles

    def test_masking_performance(self):
        """Test sensitive data masking performance."""
        # Create a large text with sensitive data
        large_text = ""
        for i in range(100):
            large_text += f"Line {i}: token=secret{i} password=pass{i} normal_data=value{i}\n"

        import time

        start_time = time.time()

        # Mask the large text
        masked = mask_sensitive_output(large_text)

        end_time = time.time()
        duration = end_time - start_time

        # Should complete quickly
        assert duration < 1.0  # 1 second max

        # Verify masking worked
        assert "***MASKED***" in masked
        assert "secret" not in masked
        # Check that password values are masked but password= prefix remains
        assert "password=" in masked.lower()  # The prefix should remain
        assert "normal_data=value" in masked  # Non-sensitive data preserved


class TestClientManagerSecurity:
    """Test security aspects of the HTTP client manager."""

    def test_get_client_manager_assertion(self):
        """Test that get_client_manager has proper assertion for security."""
        from youtrack_cli.client import get_client_manager, reset_client_manager_sync

        # Reset client manager to ensure clean state
        reset_client_manager_sync()

        # Test normal operation - should not raise assertion error
        manager = get_client_manager()
        assert manager is not None

        # Test repeated calls return same instance
        manager2 = get_client_manager()
        assert manager is manager2

        # Reset for clean state
        reset_client_manager_sync()

    def test_client_manager_ssl_verification(self):
        """Test that SSL verification setting is properly handled."""
        import os
        from unittest.mock import patch

        from youtrack_cli.client import get_client_manager, reset_client_manager_sync

        # Reset client manager
        reset_client_manager_sync()

        # Test with SSL verification disabled
        with patch.dict(os.environ, {"YOUTRACK_VERIFY_SSL": "false"}):
            manager = get_client_manager()
            assert manager is not None
            assert manager._verify_ssl is False

        # Reset and test with SSL verification enabled (default)
        reset_client_manager_sync()
        with patch.dict(os.environ, {"YOUTRACK_VERIFY_SSL": "true"}):
            manager = get_client_manager()
            assert manager is not None
            assert manager._verify_ssl is True

        # Reset for clean state
        reset_client_manager_sync()
