"""Tests for the main CLI module."""

import pytest
from click.testing import CliRunner

from yt_cli.main import main


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
