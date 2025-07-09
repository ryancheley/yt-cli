"""Configuration management for YouTrack CLI."""

import os
from pathlib import Path
from typing import Optional

from dotenv import dotenv_values, load_dotenv, set_key, unset_key

__all__ = ["ConfigManager"]


class ConfigManager:
    """Manages configuration for YouTrack CLI."""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize the config manager.

        Args:
            config_path: Path to configuration file
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
        """Get the default configuration file path."""
        config_dir = Path.home() / ".config" / "youtrack-cli"
        config_dir.mkdir(parents=True, exist_ok=True)
        return str(config_dir / ".env")

    def _ensure_config_file_exists(self) -> None:
        """Ensure the configuration file exists."""
        config_path = Path(self.config_path)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        if not config_path.exists():
            config_path.touch()

    def set_config(self, key: str, value: str) -> None:
        """Set a configuration value.

        Args:
            key: Configuration key
            value: Configuration value
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
