"""Tests for configuration functionality."""

import tempfile
from pathlib import Path
from unittest.mock import patch

from youtrack_cli.config import ConfigManager


class TestConfigManager:
    """Test ConfigManager class."""

    def test_init_with_custom_path(self):
        """Test initialization with custom config path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "custom_config.env"
            manager = ConfigManager(str(config_path))
            assert manager.config_path == str(config_path)
            assert config_path.exists()

    def test_init_with_default_path(self):
        """Test initialization with default config path."""
        with patch("pathlib.Path.home") as mock_home:
            mock_home.return_value = Path("/tmp/test_home")
            manager = ConfigManager()
            expected_path = "/tmp/test_home/.config/youtrack-cli/.env"
            assert manager.config_path == expected_path

    def test_set_and_get_config(self):
        """Test setting and getting configuration values."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.env"
            manager = ConfigManager(str(config_path))

            # Set a configuration value
            manager.set_config("TEST_KEY", "test_value")

            # Get the configuration value
            value = manager.get_config("TEST_KEY")
            assert value == "test_value"

    def test_get_nonexistent_config(self):
        """Test getting a nonexistent configuration value."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.env"
            manager = ConfigManager(str(config_path))

            value = manager.get_config("NONEXISTENT_KEY")
            assert value is None

    def test_list_config_empty(self):
        """Test listing configuration when no values exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.env"
            manager = ConfigManager(str(config_path))

            config_values = manager.list_config()
            assert config_values == {}

    def test_list_config_with_values(self):
        """Test listing configuration with values."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.env"
            manager = ConfigManager(str(config_path))

            # Set multiple configuration values
            manager.set_config("KEY1", "value1")
            manager.set_config("KEY2", "value2")
            manager.set_config("KEY3", "value3")

            config_values = manager.list_config()
            assert config_values == {
                "KEY1": "value1",
                "KEY2": "value2",
                "KEY3": "value3",
            }

    def test_list_config_ignores_comments(self):
        """Test that list_config ignores comments and empty lines."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.env"

            # Create config file with comments and empty lines
            with open(config_path, "w") as f:
                f.write("# This is a comment\n")
                f.write("\n")
                f.write("KEY1=value1\n")
                f.write("# Another comment\n")
                f.write("KEY2=value2\n")
                f.write("\n")

            manager = ConfigManager(str(config_path))
            config_values = manager.list_config()
            assert config_values == {"KEY1": "value1", "KEY2": "value2"}

    def test_unset_existing_config(self):
        """Test unsetting an existing configuration value."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.env"
            manager = ConfigManager(str(config_path))

            # Set a configuration value
            manager.set_config("TEST_KEY", "test_value")
            assert manager.get_config("TEST_KEY") == "test_value"

            # Unset the configuration value
            result = manager.unset_config("TEST_KEY")
            assert result is True
            assert manager.get_config("TEST_KEY") is None

    def test_unset_nonexistent_config(self):
        """Test unsetting a nonexistent configuration value."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.env"
            manager = ConfigManager(str(config_path))

            result = manager.unset_config("NONEXISTENT_KEY")
            assert result is False

    def test_get_config_path(self):
        """Test getting the configuration file path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.env"
            manager = ConfigManager(str(config_path))

            assert manager.get_config_path() == str(config_path)

    def test_set_config_with_special_characters(self):
        """Test setting configuration with special characters."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.env"
            manager = ConfigManager(str(config_path))

            # Set configuration with special characters
            manager.set_config("SPECIAL_KEY", "value with spaces and = signs")

            # Get the configuration value
            value = manager.get_config("SPECIAL_KEY")
            assert value == "value with spaces and = signs"

    def test_overwrite_existing_config(self):
        """Test overwriting an existing configuration value."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.env"
            manager = ConfigManager(str(config_path))

            # Set initial value
            manager.set_config("TEST_KEY", "initial_value")
            assert manager.get_config("TEST_KEY") == "initial_value"

            # Overwrite with new value
            manager.set_config("TEST_KEY", "new_value")
            assert manager.get_config("TEST_KEY") == "new_value"

    def test_ensure_config_file_exists(self):
        """Test that config file is created if it doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "new_config.env"
            assert not config_path.exists()

            ConfigManager(str(config_path))
            assert config_path.exists()

    def test_config_directory_creation(self):
        """Test that config directory is created if it doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir) / "new_dir" / "subdir"
            config_path = config_dir / "config.env"
            assert not config_dir.exists()

            ConfigManager(str(config_path))
            assert config_dir.exists()
            assert config_path.exists()
