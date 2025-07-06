"""Security enhancements for YouTrack CLI."""

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import keyring
from cryptography.fernet import Fernet
from pydantic import BaseModel, Field

from .logging import get_logger

__all__ = [
    "AuditLogger",
    "CredentialManager",
    "TokenManager",
    "SecurityConfig",
    "mask_sensitive_output",
]


class SecurityConfig(BaseModel):
    """Configuration for security features."""

    enable_audit_logging: bool = Field(default=True)
    enable_credential_encryption: bool = Field(default=True)
    enable_token_expiration_warnings: bool = Field(default=True)
    audit_log_max_entries: int = Field(default=1000)
    token_warning_days: int = Field(default=7)


class AuditEntry(BaseModel):
    """Represents a single audit log entry."""

    timestamp: datetime
    command: str
    arguments: list[str]
    user: Optional[str] = None
    success: bool = True
    error_message: Optional[str] = None


class AuditLogger:
    """Manages command audit logging."""

    def __init__(self, config: Optional[SecurityConfig] = None):
        """Initialize audit logger.

        Args:
            config: Security configuration
        """
        self.config = config or SecurityConfig()
        self.logger = get_logger("youtrack_cli.security.audit")
        self._audit_file = self._get_audit_file_path()

    def _get_audit_file_path(self) -> Path:
        """Get the audit log file path."""
        data_home = os.environ.get("XDG_DATA_HOME")
        if data_home:
            audit_dir = Path(data_home) / "youtrack-cli"
        else:
            audit_dir = Path.home() / ".local" / "share" / "youtrack-cli"

        audit_dir.mkdir(parents=True, exist_ok=True)
        return audit_dir / "audit.log"

    def log_command(
        self,
        command: str,
        arguments: list[str],
        user: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None,
    ) -> None:
        """Log a command execution.

        Args:
            command: The command that was executed
            arguments: Command arguments (sensitive data will be masked)
            user: Username if available
            success: Whether the command succeeded
            error_message: Error message if command failed
        """
        if not self.config.enable_audit_logging:
            return

        # Mask sensitive arguments
        masked_args = self._mask_sensitive_args(arguments)

        entry = AuditEntry(
            timestamp=datetime.now(),
            command=command,
            arguments=masked_args,
            user=user,
            success=success,
            error_message=error_message,
        )

        self._write_audit_entry(entry)
        self.logger.info(
            "Command executed",
            command=command,
            user=user,
            success=success,
        )

    def _mask_sensitive_args(self, arguments: list[str]) -> list[str]:
        """Mask sensitive information in command arguments."""
        sensitive_patterns = [
            r"--token=\S+",
            r"--password=\S+",
            r"--api-key=\S+",
        ]

        masked_args = []
        for arg in arguments:
            masked_arg = arg
            for pattern in sensitive_patterns:
                masked_arg = re.sub(pattern, "--***MASKED***", masked_arg, flags=re.IGNORECASE)
            masked_args.append(masked_arg)

        return masked_args

    def _write_audit_entry(self, entry: AuditEntry) -> None:
        """Write an audit entry to the log file."""
        try:
            # Read existing entries
            entries = self._read_audit_entries()

            # Add new entry
            entries.append(entry.model_dump(mode="json", serialize_as_any=True))

            # Keep only the most recent entries
            if len(entries) > self.config.audit_log_max_entries:
                entries = entries[-self.config.audit_log_max_entries :]

            # Write back to file
            with open(self._audit_file, "w") as f:
                for entry_dict in entries:
                    json.dump(entry_dict, f, default=str)
                    f.write("\n")

        except Exception as e:
            self.logger.error("Failed to write audit entry", error=str(e))

    def _read_audit_entries(self) -> list[dict[str, Any]]:
        """Read existing audit entries from file."""
        if not self._audit_file.exists():
            return []

        entries = []
        try:
            with open(self._audit_file) as f:
                for line in f:
                    line = line.strip()
                    if line:
                        entries.append(json.loads(line))
        except Exception as e:
            self.logger.error("Failed to read audit entries", error=str(e))

        return entries

    def get_audit_log(self, limit: Optional[int] = None) -> list[AuditEntry]:
        """Get audit log entries.

        Args:
            limit: Maximum number of entries to return

        Returns:
            List of audit entries
        """
        entries_data = self._read_audit_entries()
        entries = []

        for entry_data in entries_data:
            try:
                # Convert timestamp string back to datetime
                if isinstance(entry_data.get("timestamp"), str):
                    entry_data["timestamp"] = datetime.fromisoformat(entry_data["timestamp"].replace("Z", "+00:00"))
                # Validate required fields exist before creating AuditEntry
                required_fields = ["timestamp", "command", "arguments"]
                if all(key in entry_data for key in required_fields):
                    entries.append(AuditEntry(**entry_data))  # type: ignore[misc]
            except Exception as e:
                self.logger.warning("Failed to parse audit entry", error=str(e))

        if limit:
            entries = entries[-limit:]

        return entries


class CredentialManager:
    """Manages encrypted credential storage."""

    KEYRING_SERVICE = "youtrack-cli"
    KEYRING_USERNAME = "default"
    ENCRYPTION_KEY_NAME = "encryption-key"

    def __init__(self, config: Optional[SecurityConfig] = None):
        """Initialize credential manager.

        Args:
            config: Security configuration
        """
        self.config = config or SecurityConfig()
        self.logger = get_logger("youtrack_cli.security.credentials")

    def _get_encryption_key(self) -> bytes:
        """Get or create encryption key."""
        try:
            # Try to get existing key from keyring
            key_str = keyring.get_password(self.KEYRING_SERVICE, self.ENCRYPTION_KEY_NAME)
            if key_str:
                return key_str.encode()
        except Exception as e:
            self.logger.debug("Could not retrieve encryption key from keyring", error=str(e))

        # Generate new key
        key = Fernet.generate_key()

        try:
            # Store in keyring
            keyring.set_password(self.KEYRING_SERVICE, self.ENCRYPTION_KEY_NAME, key.decode())
        except Exception as e:
            self.logger.warning("Could not store encryption key in keyring", error=str(e))

        return key

    def encrypt_credential(self, value: str) -> str:
        """Encrypt a credential value.

        Args:
            value: The credential value to encrypt

        Returns:
            Encrypted credential as base64 string
        """
        if not self.config.enable_credential_encryption:
            return value

        try:
            key = self._get_encryption_key()
            fernet = Fernet(key)
            encrypted = fernet.encrypt(value.encode())
            return encrypted.decode()
        except Exception as e:
            self.logger.error("Failed to encrypt credential", error=str(e))
            return value

    def decrypt_credential(self, encrypted_value: str) -> str:
        """Decrypt a credential value.

        Args:
            encrypted_value: The encrypted credential value

        Returns:
            Decrypted credential value
        """
        if not self.config.enable_credential_encryption:
            return encrypted_value

        try:
            key = self._get_encryption_key()
            fernet = Fernet(key)
            decrypted = fernet.decrypt(encrypted_value.encode())
            return decrypted.decode()
        except Exception as e:
            self.logger.error("Failed to decrypt credential", error=str(e))
            return encrypted_value

    def store_credential(self, key: str, value: str) -> bool:
        """Store an encrypted credential in the keyring.

        Args:
            key: Credential key/identifier
            value: Credential value

        Returns:
            True if stored successfully
        """
        try:
            encrypted_value = self.encrypt_credential(value)
            keyring.set_password(self.KEYRING_SERVICE, key, encrypted_value)
            self.logger.info("Credential stored securely", key=key)
            return True
        except Exception as e:
            self.logger.error("Failed to store credential", key=key, error=str(e))
            return False

    def retrieve_credential(self, key: str) -> Optional[str]:
        """Retrieve and decrypt a credential from the keyring.

        Args:
            key: Credential key/identifier

        Returns:
            Decrypted credential value or None if not found
        """
        try:
            encrypted_value = keyring.get_password(self.KEYRING_SERVICE, key)
            if encrypted_value:
                return self.decrypt_credential(encrypted_value)
        except Exception as e:
            self.logger.error("Failed to retrieve credential", key=key, error=str(e))

        return None

    def delete_credential(self, key: str) -> bool:
        """Delete a credential from the keyring.

        Args:
            key: Credential key/identifier

        Returns:
            True if deleted successfully
        """
        try:
            keyring.delete_password(self.KEYRING_SERVICE, key)
            self.logger.info("Credential deleted", key=key)
            return True
        except Exception as e:
            self.logger.error("Failed to delete credential", key=key, error=str(e))
            return False


class TokenManager:
    """Manages token expiration checking and warnings."""

    def __init__(self, config: Optional[SecurityConfig] = None):
        """Initialize token manager.

        Args:
            config: Security configuration
        """
        self.config = config or SecurityConfig()
        self.logger = get_logger("youtrack_cli.security.tokens")

    def check_token_expiration(self, token_expiry: Optional[datetime]) -> dict[str, Any]:
        """Check if a token is expired or expiring soon.

        Args:
            token_expiry: Token expiration datetime

        Returns:
            Dictionary with expiration status and warning message
        """
        if not self.config.enable_token_expiration_warnings or not token_expiry:
            return {"status": "unknown", "message": None}

        now = datetime.now()
        days_until_expiry = (token_expiry - now).days

        if days_until_expiry < 0:
            message = "Token has expired and needs to be renewed"
            self.logger.error("Token expired", expiry_date=token_expiry)
            return {"status": "expired", "message": message, "days": days_until_expiry}

        elif days_until_expiry <= self.config.token_warning_days:
            message = f"Token expires in {days_until_expiry} days"
            self.logger.warning("Token expiring soon", days_until_expiry=days_until_expiry)
            return {"status": "expiring", "message": message, "days": days_until_expiry}

        else:
            return {"status": "valid", "message": None, "days": days_until_expiry}

    def estimate_token_expiry(self, token: str) -> Optional[datetime]:
        """Estimate token expiry from token format (if possible).

        Args:
            token: The API token

        Returns:
            Estimated expiry datetime or None if cannot determine
        """
        # This is a placeholder implementation
        # In practice, you'd need to decode JWT tokens or use API calls
        # to determine actual expiration dates
        self.logger.debug("Token expiry estimation not implemented for this token format")
        return None


def mask_sensitive_output(text: str) -> str:
    """Mask sensitive information in output text.

    Args:
        text: Text that may contain sensitive information

    Returns:
        Text with sensitive information masked
    """
    patterns = [
        (r"(token[\"'\s]*[=:][\"'\s]*)([^\s\"']+)", r"\1***MASKED***"),
        (r"(password[\"'\s]*[=:][\"'\s]*)([^\s\"']+)", r"\1***MASKED***"),
        (r"(api[_-]?key[\"'\s]*[=:][\"'\s]*)([^\s\"']+)", r"\1***MASKED***"),
        (r"(authorization[\"'\s]*[=:][\"'\s]*)([^\s\"']+)", r"\1***MASKED***"),
        (r"(bearer\s+)([^\s]+)", r"\1***MASKED***"),
    ]

    masked_text = text
    for pattern, replacement in patterns:
        masked_text = re.sub(pattern, replacement, masked_text, flags=re.IGNORECASE)

    return masked_text
