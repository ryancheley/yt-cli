"""Enhanced command executor for tutorial system that integrates with Click CLI."""

import asyncio
import asyncio.subprocess
import shlex
from typing import List, Optional

import click
from rich.panel import Panel
from rich.syntax import Syntax

from ..auth import AuthManager
from ..config import ConfigManager
from ..console import get_console


class ClickCommandExecutor:
    """Execute YouTrack CLI commands directly through Click context instead of shell."""

    def __init__(self, config_manager: Optional[ConfigManager] = None):
        """Initialize the executor with configuration.

        Args:
            config_manager: Configuration manager instance. If None, will create default.
        """
        self.console = get_console()
        self.config_manager = config_manager or ConfigManager()
        self.auth_manager = AuthManager()

        # Whitelist of allowed commands for security
        self.allowed_commands = {
            "yt",
            "yt --help",
            "yt --version",
            "yt auth",
            "yt auth login",
            "yt auth logout",
            "yt auth status",
            "yt config",
            "yt config show",
            "yt config init",
            "yt projects",
            "yt projects list",
            "yt projects create",
            "yt projects show",
            "yt issues",
            "yt issues list",
            "yt issues create",
            "yt issues show",
            "yt issues update",
            "yt time",
            "yt time list",
            "yt time add",
            "yt time delete",
            "yt users",
            "yt users list",
            "yt users show",
            "yt boards",
            "yt boards list",
            "yt boards show",
            "yt articles",
            "yt articles list",
            "yt articles show",
            "yt tutorial",
            "yt tutorial list",
            "yt tutorial run",
        }

    def is_command_allowed(self, command: str) -> bool:
        """Check if a command is in the whitelist.

        Args:
            command: Command string to validate

        Returns:
            True if command is allowed, False otherwise
        """
        # Remove any environment variables or source commands
        clean_command = command.strip()
        if clean_command.startswith("source"):
            # Extract the actual yt command after && or ;
            if "&&" in clean_command:
                clean_command = clean_command.split("&&", 1)[1].strip()
            elif ";" in clean_command:
                clean_command = clean_command.split(";", 1)[1].strip()

        # Check against whitelist
        for allowed in self.allowed_commands:
            if clean_command.startswith(allowed):
                return True

        return False

    def parse_command(self, command: str) -> List[str]:
        """Parse command string into arguments.

        Args:
            command: Command string to parse

        Returns:
            List of command arguments
        """
        # Remove environment setup if present
        clean_command = command.strip()
        if clean_command.startswith("source"):
            if "&&" in clean_command:
                clean_command = clean_command.split("&&", 1)[1].strip()
            elif ";" in clean_command:
                clean_command = clean_command.split(";", 1)[1].strip()

        # Parse arguments
        args = shlex.split(clean_command)

        # Remove 'yt' if present as first argument
        if args and args[0] == "yt":
            args = args[1:]

        return args

    async def execute_command(self, command: str, require_confirmation: bool = True) -> bool:
        """Execute a YouTrack CLI command through Click context.

        Args:
            command: The command to execute
            require_confirmation: Whether to ask for confirmation before execution

        Returns:
            True if command executed successfully, False otherwise
        """
        self.console.print(f"\n[blue]⚡ Preparing to execute:[/blue] [green]{command}[/green]")

        # Security check
        if not self.is_command_allowed(command):
            self.console.print(f"[red]❌ Command not allowed for security reasons: {command}[/red]")
            self.console.print("[yellow]Only YouTrack CLI commands are permitted in tutorial mode.[/yellow]")
            return False

        # Show command syntax
        syntax = Syntax(command, "bash", theme="monokai", line_numbers=False)
        self.console.print(Panel(syntax, title="Command", border_style="blue"))

        # Confirmation for potentially destructive commands
        if require_confirmation and self._is_destructive_command(command):
            confirm = click.confirm(f"This command may modify data. Continue with: {command}?")
            if not confirm:
                self.console.print("[yellow]Command execution cancelled.[/yellow]")
                return False

        try:
            # For now, use enhanced subprocess execution
            # TODO: Future enhancement could integrate directly with Click commands
            return await self._execute_via_subprocess(command)

        except Exception as e:
            self.console.print(f"[red]✗ Failed to execute command: {e}[/red]\n")
            return False

    async def _execute_via_subprocess(self, command: str) -> bool:
        """Execute command via subprocess with enhanced integration.

        This is a fallback method that provides better integration than the original
        shell execution while maintaining compatibility.

        Args:
            command: Command to execute

        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure we have environment variables set if needed
            import os

            env = os.environ.copy()

            # Add any necessary environment setup
            # This could include authentication tokens, base URLs, etc.
            if hasattr(self.config_manager, "get_env_vars"):
                env.update(self.config_manager.get_env_vars())

            # Execute the command
            process = await asyncio.create_subprocess_shell(
                command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, shell=True, env=env
            )

            stdout, stderr = await process.communicate()

            # Display output
            if stdout:
                output_text = stdout.decode().strip()
                if output_text:
                    self.console.print(
                        Panel(output_text, title="[green]Output[/green]", border_style="green", expand=False)
                    )

            if stderr:
                error_text = stderr.decode().strip()
                if error_text:
                    self.console.print(
                        Panel(error_text, title="[red]Error Output[/red]", border_style="red", expand=False)
                    )

            if process.returncode == 0:
                self.console.print("[green]✓ Command executed successfully![/green]\n")
                return True
            self.console.print(f"[red]✗ Command failed with exit code {process.returncode}[/red]\n")
            return False

        except Exception as e:
            self.console.print(f"[red]✗ Failed to execute command: {e}[/red]\n")
            return False

    def _is_destructive_command(self, command: str) -> bool:
        """Check if a command is potentially destructive.

        Args:
            command: Command to check

        Returns:
            True if command is destructive, False otherwise
        """
        destructive_patterns = ["delete", "remove", "rm", "update", "modify", "create"]

        command_lower = command.lower()
        return any(pattern in command_lower for pattern in destructive_patterns)

    def add_allowed_command(self, command: str) -> None:
        """Add a command to the whitelist.

        Args:
            command: Command pattern to allow
        """
        self.allowed_commands.add(command)

    def remove_allowed_command(self, command: str) -> None:
        """Remove a command from the whitelist.

        Args:
            command: Command pattern to remove
        """
        self.allowed_commands.discard(command)
