"""Tests for configuration functionality."""

import os
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

    def test_list_config_with_complex_values(self):
        """Test list_config with complex values containing equals signs."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.env"

            # Create config file with complex values
            with open(config_path, "w") as f:
                f.write("KEY1=value=with=equals\n")
                f.write('KEY2="quoted value with = signs"\n')
                f.write("KEY3='single quoted value with = signs'\n")
                f.write("URL=https://example.com/path?param=value&other=value\n")

            manager = ConfigManager(str(config_path))
            config_values = manager.list_config()

            assert config_values["KEY1"] == "value=with=equals"
            assert config_values["KEY2"] == "quoted value with = signs"
            assert config_values["KEY3"] == "single quoted value with = signs"
            assert config_values["URL"] == "https://example.com/path?param=value&other=value"

    def test_list_config_with_malformed_file(self):
        """Test list_config with malformed config file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.env"

            # Create malformed config file
            with open(config_path, "wb") as f:
                f.write(b"\xff\xfe\x00\x00malformed")  # Invalid UTF-8

            manager = ConfigManager(str(config_path))
            config_values = manager.list_config()

            # Should return empty dict for malformed files
            assert config_values == {}

    def test_get_config_with_default(self):
        """Test get_config_with_default method."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.env"
            manager = ConfigManager(str(config_path))

            # Test with nonexistent key
            value = manager.get_config_with_default("NONEXISTENT", "default_value")
            assert value == "default_value"

            # Test with existing key
            manager.set_config("EXISTING_KEY", "existing_value")
            value = manager.get_config_with_default("EXISTING_KEY", "default_value")
            assert value == "existing_value"

    def test_get_config_with_env_override(self):
        """Test get_config_with_env_override method."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.env"
            manager = ConfigManager(str(config_path))

            # Set config value
            manager.set_config("test_key", "config_value")

            # Test without environment variable
            value = manager.get_config_with_env_override("test_key", "default")
            assert value == "config_value"

            # Test with environment variable override
            with patch.dict(os.environ, {"YOUTRACK_TEST_KEY": "env_value"}):
                value = manager.get_config_with_env_override("test_key", "default")
                assert value == "env_value"

            # Test with nonexistent key and default
            value = manager.get_config_with_env_override("nonexistent", "default")
            assert value == "default"

    def test_validate_config_empty_file(self):
        """Test validate_config with empty config file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.env"
            manager = ConfigManager(str(config_path))

            errors = manager.validate_config()
            assert len(errors) == 2  # Missing youtrack_url and youtrack_token
            assert "Missing required configuration: youtrack_url" in errors
            assert "Missing required configuration: youtrack_token" in errors

    def test_validate_config_valid_file(self):
        """Test validate_config with valid config file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.env"
            manager = ConfigManager(str(config_path))

            # Set required configuration
            manager.set_config("youtrack_url", "https://example.youtrack.cloud")
            manager.set_config("youtrack_token", "perm:token")

            errors = manager.validate_config()
            assert len(errors) == 0

    def test_validate_config_partial_file(self):
        """Test validate_config with partially valid config file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.env"
            manager = ConfigManager(str(config_path))

            # Set only one required configuration
            manager.set_config("youtrack_url", "https://example.youtrack.cloud")

            errors = manager.validate_config()
            assert len(errors) == 1
            assert "Missing required configuration: youtrack_token" in errors

    def test_validate_config_nonexistent_file(self):
        """Test validate_config with nonexistent config file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "nonexistent.env"
            manager = ConfigManager(str(config_path))

            # Remove the file that was created by initialization
            Path(config_path).unlink()

            errors = manager.validate_config()
            assert len(errors) == 0  # No errors for nonexistent file

    def test_backwards_compatibility(self):
        """Test that the new implementation is backwards compatible."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.env"

            # Create config file with old format (should still work)
            with open(config_path, "w") as f:
                f.write("KEY1=value1\n")
                f.write("KEY2=value2\n")
                f.write("# Comment line\n")
                f.write("\n")  # Empty line
                f.write("KEY3=value3\n")

            manager = ConfigManager(str(config_path))
            config_values = manager.list_config()

            assert config_values == {"KEY1": "value1", "KEY2": "value2", "KEY3": "value3"}
