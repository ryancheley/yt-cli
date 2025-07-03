"""Configuration management for YouTrack CLI."""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv, set_key, unset_key


class ConfigManager:
    """Manages configuration for YouTrack CLI."""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize the config manager.

        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path or self._get_default_config_path()
        self._ensure_config_file_exists()
        load_dotenv(self.config_path)

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
        load_dotenv(self.config_path, override=True)

    def get_config(self, key: str) -> Optional[str]:
        """Get a configuration value.

        Args:
            key: Configuration key

        Returns:
            Configuration value if exists, None otherwise
        """
        return os.getenv(key)

    def list_config(self) -> dict[str, str]:
        """List all configuration values.

        Returns:
            Dictionary of all configuration key-value pairs
        """
        config = {}
        if os.path.exists(self.config_path):
            with open(self.config_path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        # Remove quotes if present
                        if value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                        elif value.startswith("'") and value.endswith("'"):
                            value = value[1:-1]
                        config[key] = value
        return config

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
