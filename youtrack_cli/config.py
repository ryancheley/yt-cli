"""Configuration management for YouTrack CLI.

This module provides configuration file management using environment files
with automatic path resolution, validation, and secure storage.

Example:
    Basic usage for configuration management:

    .. code-block:: python

        config = ConfigManager()
        config.set_config('BASE_URL', 'https://youtrack.example.com')
        url = config.get_config('BASE_URL')
"""

import os
from pathlib import Path
from typing import Optional

from dotenv import dotenv_values, load_dotenv, set_key, unset_key

__all__ = ["ConfigManager"]


class ConfigManager:
    """Manages configuration for YouTrack CLI.

    Provides file-based configuration management using environment files
    stored in the user's home directory. Supports reading, writing, and
    validation of configuration values with automatic file creation.

    Configuration files are stored as .env files in ~/.config/youtrack-cli/
    and are compatible with standard dotenv format.
    """

    def __init__(self, config_path: Optional[str] = None):
        """Initialize the config manager.

        Args:
            config_path: Path to configuration file. If None, uses default
                location in ~/.config/youtrack-cli/.env.
        """
        self.config_path = config_path or self._get_default_config_path()
        self._ensure_config_file_exists()
        try:
            load_dotenv(self.config_path)
        except Exception:
            # Ignore errors loading dotenv during initialization
            # This allows the config manager to still work with malformed files
            pass

    def _get_default_config_path(self) -> str:
        """Get the default configuration file path.

        Creates the configuration directory if it doesn't exist.

        Returns:
            Path to the default configuration file.
        """
        config_dir = Path.home() / ".config" / "youtrack-cli"
        config_dir.mkdir(parents=True, exist_ok=True)
        return str(config_dir / ".env")

    def _ensure_config_file_exists(self) -> None:
        """Ensure the configuration file exists.

        Creates the configuration file and any necessary parent directories
        if they don't already exist.
        """
        config_path = Path(self.config_path)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        if not config_path.exists():
            config_path.touch()

    def set_config(self, key: str, value: str) -> None:
        """Set a configuration value.

        Args:
            key: Configuration key to set.
            value: Configuration value to store.
        """
        set_key(self.config_path, key, value)
        # Reload environment variables after setting
        try:
            load_dotenv(self.config_path, override=True)
        except Exception:
            # Ignore errors loading dotenv after setting
            pass

    def get_config(self, key: str) -> Optional[str]:
        """Get a configuration value.

        Args:
            key: Configuration key

        Returns:
            Configuration value if exists, None otherwise
        """
        # First check environment variable
        value = os.getenv(key)
        if value is not None:
            return value

        # Then check the config file directly
        config = self.list_config()
        return config.get(key)

    def list_config(self) -> dict[str, str]:
        """List all configuration values from the config file.

        Returns:
            Dictionary of all configuration key-value pairs
        """
        if not os.path.exists(self.config_path):
            return {}

        try:
            config = dict(dotenv_values(self.config_path))
            # Filter out None values that dotenv_values might return
            return {k: v for k, v in config.items() if v is not None}
        except Exception:
            # Return empty dict if parsing fails
            return {}

    def unset_config(self, key: str) -> bool:
        """Unset a configuration value.

        Args:
            key: Configuration key

        Returns:
            True if key was removed, False if key didn't exist
        """
        if self.get_config(key) is None:
            return False
        unset_key(self.config_path, key)
        # Remove from current environment as well
        if key in os.environ:
            del os.environ[key]
        return True

    def get_config_path(self) -> str:
        """Get the path to the configuration file.

        Returns:
            Path to configuration file
        """
        return self.config_path

    def get_config_with_default(self, key: str, default: str = "") -> str:
        """Get a configuration value with a default fallback.

        Args:
            key: Configuration key
            default: Default value if key doesn't exist

        Returns:
            Configuration value or default
        """
        value = self.get_config(key)
        return value if value is not None else default

    def get_config_with_env_override(self, key: str, default: str = "") -> str:
        """Get config value with environment variable override.

        Args:
            key: Configuration key
            default: Default value if neither env var nor config exists

        Returns:
            Configuration value from environment variable, config file, or default
        """
        # Check environment variable first
        env_key = f"YOUTRACK_{key.upper()}"
        env_value = os.getenv(env_key)
        if env_value is not None:
            return env_value

        # Fall back to config file value
        config_value = self.get_config(key)
        if config_value is not None:
            return config_value

        # Finally fall back to default
        return default

    def validate_config(self) -> list[str]:
        """Validate configuration file and return any errors.

        Returns:
            List of validation error messages
        """
        errors = []

        if not os.path.exists(self.config_path):
            return errors

        try:
            config = self.list_config()
            # Add validation rules here
            required_keys = ["youtrack_url", "youtrack_token"]
            for key in required_keys:
                if key not in config or not config[key]:
                    errors.append(f"Missing required configuration: {key}")
        except Exception as e:
            errors.append(f"Invalid configuration file format: {e}")

        return errors

    # Alias management methods (Issue #345)

    def set_alias(self, alias: str, command: str) -> None:
        """Set a user-defined alias.

        Args:
            alias: The alias name (e.g., 'myissues')
            command: The full command to run (e.g., 'issues list --assignee me')
        """
        self.set_config(f"ALIAS_{alias}", command)

    def get_alias(self, alias: str) -> Optional[str]:
        """Get a user-defined alias command.

        Args:
            alias: The alias name

        Returns:
            The command for the alias, or None if not found
        """
        return self.get_config(f"ALIAS_{alias}")

    def list_aliases(self) -> dict[str, str]:
        """List all user-defined aliases.

        Returns:
            Dictionary mapping alias names to their commands
        """
        config = self.list_config()
        aliases = {}
        for key, value in config.items():
            if key.startswith("ALIAS_"):
                alias_name = key[6:]  # Remove "ALIAS_" prefix
                aliases[alias_name] = value
        return aliases

    def remove_alias(self, alias: str) -> bool:
        """Remove a user-defined alias.

        Args:
            alias: The alias name to remove

        Returns:
            True if alias was removed, False if it didn't exist
        """
        return self.unset_config(f"ALIAS_{alias}")
