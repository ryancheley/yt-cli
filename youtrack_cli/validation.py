"""Command validation and suggestion utilities for YouTrack CLI.

This module provides utilities for validating commands, suggesting corrections
for typos and mistakes, and providing helpful error messages with usage examples.
"""

import difflib
from typing import Any, Dict, List, Optional, Tuple

import click

from .exceptions import CommandValidationError, ParameterError, UsageError

__all__ = [
    "CommandValidator",
    "suggest_similar_commands",
    "validate_parameter_combination",
    "create_usage_error",
    "get_command_suggestions",
]


class CommandValidator:
    """Validates commands and provides helpful suggestions for corrections."""

    def __init__(self):
        self._command_registry: Dict[str, Dict[str, str]] = {}
        self._common_mistakes: Dict[str, str] = {
            "version": "--version",
            "help": "--help",
            "issues comments create": "issues comments add",
            "issues comment create": "issues comments add",
            "issue create": "issues create",
            "issue list": "issues list",
            "project list": "projects list",
            "user list": "users list",
        }
        self._parameter_patterns: Dict[str, List[str]] = {
            "assignee_options": ["--assignee", "-a"],
            "project_options": ["--project", "--project-id", "-p"],
            "type_options": ["--type", "-t"],
            "priority_options": ["--priority", "-p"],
            "state_options": ["--state", "-s"],
        }

    def register_command(self, command_path: str, usage_syntax: str, description: str = "") -> None:
        """Register a command for validation and suggestions."""
        self._command_registry[command_path] = {
            "usage": usage_syntax,
            "description": description,
        }

    def suggest_similar_command(self, attempted_command: str, max_suggestions: int = 3) -> List[str]:
        """Suggest similar commands based on string similarity."""
        if attempted_command in self._common_mistakes:
            return [self._common_mistakes[attempted_command]]

        suggestions = []
        all_commands = list(self._command_registry.keys()) + list(self._common_mistakes.values())

        # Get close matches using difflib
        close_matches = difflib.get_close_matches(attempted_command, all_commands, n=max_suggestions, cutoff=0.6)
        suggestions.extend(close_matches)

        # Check for partial matches (substrings)
        words = attempted_command.split()
        if len(words) > 1:
            for command in all_commands:
                if any(word in command for word in words) and command not in suggestions:
                    suggestions.append(command)
                    if len(suggestions) >= max_suggestions:
                        break

        return suggestions[:max_suggestions]

    def validate_command_structure(self, command_path: str) -> Optional[CommandValidationError]:
        """Validate command structure and return error if invalid."""
        if command_path in self._command_registry:
            return None

        similar_commands = self.suggest_similar_command(command_path)

        if similar_commands:
            return CommandValidationError(
                f"Unknown command: '{command_path}'",
                command_path=command_path,
                similar_commands=similar_commands,
            )

        return CommandValidationError(
            f"Unknown command: '{command_path}'",
            command_path=command_path,
            usage_example="Run 'yt --help' to see available commands",
        )

    def validate_parameter(
        self,
        param_name: str,
        param_value: str,
        valid_choices: Optional[List[str]] = None,
        expected_type: Optional[str] = None,
    ) -> Optional[ParameterError]:
        """Validate a parameter value and return error if invalid."""
        if valid_choices and param_value not in valid_choices:
            # Suggest similar valid choices
            similar_choices = difflib.get_close_matches(param_value, valid_choices, n=3, cutoff=0.6)

            return ParameterError(
                f"Invalid value '{param_value}' for parameter '{param_name}'",
                parameter_name=param_name,
                valid_choices=similar_choices if similar_choices else valid_choices[:5],
                usage_example=f"--{param_name} {valid_choices[0]}" if valid_choices else None,
            )

        return None


def suggest_similar_commands(attempted_command: str, available_commands: List[str]) -> List[str]:
    """Suggest similar commands from a list of available commands."""
    return difflib.get_close_matches(attempted_command, available_commands, n=3, cutoff=0.6)


def validate_parameter_combination(
    params: Dict[str, Any],
    mutually_exclusive: Optional[List[Tuple[str, ...]]] = None,
    required_together: Optional[List[Tuple[str, ...]]] = None,
) -> Optional[ParameterError]:
    """Validate parameter combinations for mutual exclusion and required together constraints."""
    if mutually_exclusive:
        for exclusive_group in mutually_exclusive:
            provided = [param for param in exclusive_group if params.get(param) is not None]
            if len(provided) > 1:
                return ParameterError(
                    f"Parameters {', '.join(provided)} are mutually exclusive",
                    usage_example=f"Use only one of: {', '.join(exclusive_group)}",
                )

    if required_together:
        for required_group in required_together:
            provided = [param for param in required_group if params.get(param) is not None]
            if provided and len(provided) != len(required_group):
                missing = [param for param in required_group if param not in provided]
                return ParameterError(
                    f"When using {', '.join(provided)}, you must also provide: {', '.join(missing)}",
                    usage_example=f"Use together: {', '.join(required_group)}",
                )

    return None


def create_usage_error(
    message: str,
    command_path: str,
    usage_syntax: str,
    examples: Optional[List[str]] = None,
    common_mistakes: Optional[List[str]] = None,
) -> UsageError:
    """Create a comprehensive usage error with examples and guidance."""
    return UsageError(
        message=message,
        command_path=command_path,
        usage_syntax=usage_syntax,
        examples=examples,
        common_mistakes=common_mistakes,
    )


def get_command_suggestions(ctx: click.Context) -> List[str]:
    """Get command suggestions based on the current Click context."""
    suggestions = []

    # Get available commands from current group
    if hasattr(ctx.command, "commands"):
        commands_dict = getattr(ctx.command, "commands", {})
        if hasattr(commands_dict, "keys"):
            commands = list(commands_dict.keys())
            suggestions.extend(commands)

    # Add common aliases
    aliases = {
        "i": "issues",
        "p": "projects",
        "u": "users",
        "a": "articles",
        "t": "time",
        "b": "boards",
        "c": "config",
        "cfg": "config",
    }

    suggestions.extend(aliases.values())

    return list(set(suggestions))


# Initialize global command validator
_validator = CommandValidator()

# Register common commands (this would be expanded with all actual commands)
_validator.register_command("issues create", "yt issues create PROJECT_ID SUMMARY [OPTIONS]")
_validator.register_command("issues list", "yt issues list [OPTIONS]")
_validator.register_command("issues comments add", "yt issues comments add ISSUE_ID COMMENT [OPTIONS]")
_validator.register_command("projects list", "yt projects list [OPTIONS]")
_validator.register_command("users list", "yt users list [OPTIONS]")


def get_global_validator() -> CommandValidator:
    """Get the global command validator instance."""
    return _validator
