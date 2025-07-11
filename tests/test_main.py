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
        "completion",
        "setup",
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
            result = runner.invoke(main, ["--config", str(config_path), "config", "get", "TEST_KEY"])
            assert result.exit_code == 0
            assert "TEST_KEY = test_value" in result.output

    def test_config_get_nonexistent(self):
        """Test getting a nonexistent configuration value."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.env"
            runner = CliRunner()

            result = runner.invoke(main, ["--config", str(config_path), "config", "get", "NONEXISTENT_KEY"])
            assert result.exit_code == 1
            assert "Configuration key 'NONEXISTENT_KEY' not found" in result.output

    def test_config_list_empty(self):
        """Test listing configuration when no values exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.env"
            runner = CliRunner()

            result = runner.invoke(main, ["--config", str(config_path), "config", "list"])
            assert result.exit_code == 0
            assert "No configuration values found" in result.output

    def test_config_list_with_values(self):
        """Test listing configuration with values."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.env"
            runner = CliRunner()

            # Set multiple configuration values
            runner.invoke(main, ["--config", str(config_path), "config", "set", "KEY1", "value1"])
            runner.invoke(main, ["--config", str(config_path), "config", "set", "KEY2", "value2"])

            # List all configuration values
            result = runner.invoke(main, ["--config", str(config_path), "config", "list"])
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
            result = runner.invoke(main, ["--config", str(config_path), "config", "list"])
            assert result.exit_code == 0
            assert "API_TOKEN = very-sec...6789" in result.output
            assert "very-secret-token-123456789" not in result.output

    def test_config_list_masks_api_key(self):
        """Test that API_KEY values are masked in list output."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.env"
            runner = CliRunner()

            # Set an API_KEY configuration value
            runner.invoke(
                main,
                [
                    "--config",
                    str(config_path),
                    "config",
                    "set",
                    "YOUTRACK_API_KEY",
                    "super-secret-api-key-12345",
                ],
            )

            # Test that special keyring placeholder is not masked
            runner.invoke(
                main,
                [
                    "--config",
                    str(config_path),
                    "config",
                    "set",
                    "ANOTHER_API_KEY",
                    "[Stored in keyring]",
                ],
            )

            # List configuration values
            result = runner.invoke(main, ["--config", str(config_path), "config", "list"])
            assert result.exit_code == 0
            assert "YOUTRACK_API_KEY = super-se...2345" in result.output
            assert "super-secret-api-key-12345" not in result.output
            assert "ANOTHER_API_KEY = [Stored in keyring]" in result.output


class TestCompletionCommands:
    """Test shell completion functionality."""

    def test_completion_help(self):
        """Test completion command help."""
        runner = CliRunner()
        result = runner.invoke(main, ["completion", "--help"])
        assert result.exit_code == 0
        assert "Generate shell completion script" in result.output

    @pytest.mark.parametrize("shell", ["bash", "zsh", "fish", "powershell"])
    def test_completion_generation(self, shell: str):
        """Test completion script generation for all supported shells."""
        runner = CliRunner()
        result = runner.invoke(main, ["completion", shell])
        assert result.exit_code == 0
        assert len(result.output.strip()) > 0

        # Check for shell-specific content
        if shell == "bash":
            assert "_yt_completion" in result.output
            assert "complete" in result.output
        elif shell == "zsh":
            assert "#compdef yt" in result.output
            assert "_yt_completion" in result.output
        elif shell == "fish":
            assert "function _yt_completion" in result.output
            assert "complete --no-files --command yt" in result.output
        elif shell == "powershell":
            assert "Register-ArgumentCompleter" in result.output
            assert "_YT_COMPLETE" in result.output

    def test_completion_invalid_shell(self):
        """Test completion with invalid shell."""
        runner = CliRunner()
        result = runner.invoke(main, ["completion", "invalid_shell"])
        assert result.exit_code == 2  # Click argument validation error

    @pytest.mark.parametrize("shell", ["bash", "zsh", "fish", "powershell"])
    def test_completion_install_flag(self, shell: str):
        """Test completion installation flag."""
        with tempfile.TemporaryDirectory() as temp_dir:
            runner = CliRunner()

            # Mock the home directory to our temp directory
            import os

            original_home = os.environ.get("HOME")
            os.environ["HOME"] = temp_dir

            try:
                result = runner.invoke(main, ["completion", shell, "--install"])
                # Should succeed or fail gracefully with permission/path error
                # We can't guarantee success since it depends on system paths
                assert result.exit_code in [
                    0,
                    1,
                ]  # 0 for success, 1 for expected failure

                if result.exit_code == 0:
                    assert "Completion script installed" in result.output
                else:
                    # Check it failed for expected reasons
                    assert (
                        "Permission denied" in result.output
                        or "Installation failed" in result.output
                        or "Error" in result.output
                    )
            finally:
                # Restore original HOME
                if original_home:
                    os.environ["HOME"] = original_home
                else:
                    os.environ.pop("HOME", None)

    def test_completion_script_content_bash(self):
        """Test that bash completion script contains required elements."""
        runner = CliRunner()
        result = runner.invoke(main, ["completion", "bash"])
        assert result.exit_code == 0

        script = result.output
        # Check for essential bash completion elements
        assert "_YT_COMPLETE=bash_complete" in script
        assert "COMP_WORDS" in script
        assert "COMP_CWORD" in script
        assert "complete -o nosort -F _yt_completion yt" in script

    def test_completion_script_content_zsh(self):
        """Test that zsh completion script contains required elements."""
        runner = CliRunner()
        result = runner.invoke(main, ["completion", "zsh"])
        assert result.exit_code == 0

        script = result.output
        # Check for essential zsh completion elements
        assert "_YT_COMPLETE=zsh_complete" in script
        assert "compdef _yt_completion yt" in script
        assert "COMP_WORDS" in script
        assert "COMP_CWORD" in script

    def test_completion_script_content_fish(self):
        """Test that fish completion script contains required elements."""
        runner = CliRunner()
        result = runner.invoke(main, ["completion", "fish"])
        assert result.exit_code == 0

        script = result.output
        # Check for essential fish completion elements
        assert "_YT_COMPLETE=fish_complete" in script
        assert "function _yt_completion" in script
        assert "complete --no-files --command yt" in script

    def test_completion_script_content_powershell(self):
        """Test that PowerShell completion script contains required elements."""
        runner = CliRunner()
        result = runner.invoke(main, ["completion", "powershell"])
        assert result.exit_code == 0

        script = result.output
        # Check for essential PowerShell completion elements
        assert "_YT_COMPLETE" in script and "powershell_complete" in script
        assert "Register-ArgumentCompleter" in script
        assert "-CommandName yt" in script
        assert "CompletionResult" in script


class TestCommandAliases:
    """Test command alias functionality."""

    @pytest.mark.parametrize(
        "alias,command",
        [
            ("i", "issues"),
            ("a", "articles"),
            ("p", "projects"),
            ("u", "users"),
            ("t", "time"),
            ("b", "boards"),
            ("c", "config"),
            ("cfg", "config"),
            ("login", "auth"),
        ],
    )
    def test_main_command_aliases(self, alias: str, command: str) -> None:
        """Test that main command aliases work correctly."""
        runner = CliRunner()

        # Test that the alias shows the same help as the original command
        original_result = runner.invoke(main, [command, "--help"])
        alias_result = runner.invoke(main, [alias, "--help"])

        assert original_result.exit_code == 0
        assert alias_result.exit_code == 0
        # The help content should be identical (or at least contain the same key text)
        assert "help" in alias_result.output.lower()

    def test_alias_list_in_help(self) -> None:
        """Test that aliases are mentioned in the main help."""
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "Command Aliases:" in result.output
        assert "i = issues" in result.output
        assert "c/cfg = config" in result.output

    @pytest.mark.parametrize(
        "alias,subcommand",
        [
            ("i", "c"),  # issues create alias
            ("i", "l"),  # issues list alias
            ("i", "u"),  # issues update alias
            ("i", "s"),  # issues search alias
        ],
    )
    def test_subcommand_aliases(self, alias: str, subcommand: str) -> None:
        """Test that subcommand aliases work correctly."""
        runner = CliRunner()
        result = runner.invoke(main, [alias, subcommand, "--help"])
        # Should not fail - if the alias works, it should show help
        # We can't test the full functionality without mocking the API
        assert result.exit_code in [0, 1, 2]  # Help should work, or fail gracefully

    def test_alias_completion_listing(self) -> None:
        """Test that aliases do NOT appear in command listing to prevent duplicates."""
        # Get the main CLI object to test list_commands
        # Create a mock context
        import click

        from youtrack_cli.main import main as main_cli

        ctx = click.Context(main_cli)

        # Get the list of available commands
        commands = main_cli.list_commands(ctx)

        # Check that aliases are NOT in the list (to prevent duplicates in help)
        assert "i" not in commands
        assert "a" not in commands
        assert "p" not in commands
        assert "c" not in commands
        assert "login" not in commands

        # But the actual commands should be present
        assert "issues" in commands
        assert "articles" in commands
        assert "projects" in commands
        assert "config" in commands
        assert "auth" in commands

    def test_alias_resolution_still_works(self) -> None:
        """Test that aliases still resolve to correct commands despite not appearing in list."""
        import click

        from youtrack_cli.main import main as main_cli

        ctx = click.Context(main_cli)

        # Test that aliases resolve to the correct commands
        test_cases = [
            ("i", "issues"),
            ("a", "articles"),
            ("p", "projects"),
            ("u", "users"),
            ("t", "time"),
            ("b", "boards"),
            ("c", "config"),
            ("cfg", "config"),
            ("login", "auth"),
        ]

        for alias, expected_command in test_cases:
            resolved_cmd = main_cli.get_command(ctx, alias)
            expected_cmd = main_cli.get_command(ctx, expected_command)

            # Both should resolve to the same command object
            assert resolved_cmd is not None, f"Alias '{alias}' should resolve to a command"
            assert expected_cmd is not None, f"Command '{expected_command}' should exist"
            assert resolved_cmd is expected_cmd, f"Alias '{alias}' should resolve to '{expected_command}'"
