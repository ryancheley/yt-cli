"""Tests for the main CLI module."""

import tempfile
from pathlib import Path

import pytest
from click.testing import CliRunner

from youtrack_cli.main import main


def test_main_help() -> None:
    """Test that the main command shows help."""
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "YouTrack CLI" in result.output


def test_main_version() -> None:
    """Test that the version command works."""
    runner = CliRunner()
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0


@pytest.mark.parametrize(
    "command",
    [
        "issues",
        "articles",
        "projects",
        "users",
        "time",
        "boards",
        "reports",
        "auth",
        "config",
        "admin",
    ],
)
def test_command_groups_exist(command: str) -> None:
    """Test that all main command groups are available."""
    runner = CliRunner()
    result = runner.invoke(main, [command, "--help"])
    assert result.exit_code == 0


class TestConfigCommands:
    """Test config command functionality."""

    def test_config_help(self):
        """Test config command help."""
        runner = CliRunner()
        result = runner.invoke(main, ["config", "--help"])
        assert result.exit_code == 0
        assert "CLI configuration" in result.output

    def test_config_set_help(self):
        """Test config set command help."""
        runner = CliRunner()
        result = runner.invoke(main, ["config", "set", "--help"])
        assert result.exit_code == 0
        assert "Set a configuration value" in result.output

    def test_config_get_help(self):
        """Test config get command help."""
        runner = CliRunner()
        result = runner.invoke(main, ["config", "get", "--help"])
        assert result.exit_code == 0
        assert "Get a configuration value" in result.output

    def test_config_list_help(self):
        """Test config list command help."""
        runner = CliRunner()
        result = runner.invoke(main, ["config", "list", "--help"])
        assert result.exit_code == 0
        assert "List all configuration values" in result.output

    def test_config_set_and_get(self):
        """Test setting and getting a configuration value."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.env"
            runner = CliRunner()

            # Set a configuration value
            result = runner.invoke(
                main,
                [
                    "--config",
                    str(config_path),
                    "config",
                    "set",
                    "TEST_KEY",
                    "test_value",
                ],
            )
            assert result.exit_code == 0
            assert "Set TEST_KEY = test_value" in result.output

            # Get the configuration value
            result = runner.invoke(
                main, ["--config", str(config_path), "config", "get", "TEST_KEY"]
            )
            assert result.exit_code == 0
            assert "TEST_KEY = test_value" in result.output

    def test_config_get_nonexistent(self):
        """Test getting a nonexistent configuration value."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.env"
            runner = CliRunner()

            result = runner.invoke(
                main, ["--config", str(config_path), "config", "get", "NONEXISTENT_KEY"]
            )
            assert result.exit_code == 1
            assert "Configuration key 'NONEXISTENT_KEY' not found" in result.output

    def test_config_list_empty(self):
        """Test listing configuration when no values exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.env"
            runner = CliRunner()

            result = runner.invoke(
                main, ["--config", str(config_path), "config", "list"]
            )
            assert result.exit_code == 0
            assert "No configuration values found" in result.output

    def test_config_list_with_values(self):
        """Test listing configuration with values."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.env"
            runner = CliRunner()

            # Set multiple configuration values
            runner.invoke(
                main, ["--config", str(config_path), "config", "set", "KEY1", "value1"]
            )
            runner.invoke(
                main, ["--config", str(config_path), "config", "set", "KEY2", "value2"]
            )

            # List all configuration values
            result = runner.invoke(
                main, ["--config", str(config_path), "config", "list"]
            )
            assert result.exit_code == 0
            assert "Configuration values:" in result.output
            assert "KEY1 = value1" in result.output
            assert "KEY2 = value2" in result.output

    def test_config_list_masks_sensitive_values(self):
        """Test that sensitive values are masked in list output."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.env"
            runner = CliRunner()

            # Set a sensitive configuration value
            runner.invoke(
                main,
                [
                    "--config",
                    str(config_path),
                    "config",
                    "set",
                    "API_TOKEN",
                    "very-secret-token-123456789",
                ],
            )

            # List configuration values
            result = runner.invoke(
                main, ["--config", str(config_path), "config", "list"]
            )
            assert result.exit_code == 0
            assert "API_TOKEN = very-sec...6789" in result.output
            assert "very-secret-token-123456789" not in result.output
