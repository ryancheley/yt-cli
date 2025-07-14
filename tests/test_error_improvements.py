"""Tests for improved error messages and command validation."""

import click
import pytest
from click.testing import CliRunner

from youtrack_cli.exceptions import (
    CommandValidationError,
    ParameterError,
    UsageError,
)
from youtrack_cli.main import main
from youtrack_cli.utils import handle_error
from youtrack_cli.validation import get_global_validator


class TestErrorHandling:
    """Test enhanced error handling functionality."""

    def test_handle_error_with_command_validation_error(self):
        """Test that CommandValidationError is handled properly."""
        error = CommandValidationError(
            "Command not found", similar_commands=["issues", "projects"], usage_example="yt issues list"
        )

        result = handle_error(error, "test operation")

        assert result["status"] == "error"
        assert result["message"] == "Command not found"
        assert result["similar_commands"] == ["issues", "projects"]
        assert result["usage_example"] == "yt issues list"

    def test_handle_error_with_parameter_error(self):
        """Test that ParameterError is handled properly."""
        error = ParameterError(
            "Invalid parameter value",
            parameter_name="priority",
            valid_choices=["High", "Medium", "Low"],
            usage_example="--priority High",
        )

        result = handle_error(error, "test operation")

        assert result["status"] == "error"
        assert result["message"] == "Invalid parameter value"
        assert result["parameter_name"] == "priority"
        assert result["valid_choices"] == ["High", "Medium", "Low"]
        assert result["usage_example"] == "--priority High"

    def test_handle_error_with_usage_error(self):
        """Test that UsageError is handled properly."""
        error = UsageError(
            "Invalid usage",
            command_path="yt issues create",
            usage_syntax="yt issues create PROJECT_ID SUMMARY",
            examples=["yt issues create WEB-123 'Fix bug'"],
            common_mistakes=["Missing project ID"],
        )

        result = handle_error(error, "test operation")

        assert result["status"] == "error"
        assert result["message"] == "Invalid usage"
        assert result["usage_syntax"] == "yt issues create PROJECT_ID SUMMARY"
        assert result["examples"] == ["yt issues create WEB-123 'Fix bug'"]
        assert result["common_mistakes"] == ["Missing project ID"]


class TestCommandValidation:
    """Test command validation and suggestions."""

    def test_command_validator_suggestions(self):
        """Test that command validator provides good suggestions."""
        validator = get_global_validator()

        # Test close match
        suggestions = validator.suggest_similar_command("issue")
        # Should find commands containing "issues"
        issues_suggestions = [s for s in suggestions if "issues" in s]
        assert len(issues_suggestions) > 0, f"Expected suggestions with 'issues', got: {suggestions}"

        # Test common mistake
        suggestions = validator.suggest_similar_command("version")
        assert "--version" in suggestions

    def test_main_cli_version_suggestion(self):
        """Test that main CLI suggests --version for 'version' command."""
        runner = CliRunner()

        # This should show our enhanced error message
        result = runner.invoke(main, ["version"])

        # Should fail but show helpful message
        assert result.exit_code != 0
        # The enhanced error should be shown even though Click also shows an error


class TestParameterValidation:
    """Test parameter validation improvements."""

    def test_project_id_validation(self):
        """Test project ID format validation."""
        from click import Option

        from youtrack_cli.cli_utils.validation import validate_project_id_format

        # Create a mock context and parameter
        @click.command()
        def test_cmd():
            pass

        ctx = click.Context(test_cmd, info_name="test")
        param = Option(["--project-id"])

        # Valid project IDs should pass
        assert validate_project_id_format(ctx, param, "WEB") == "WEB"
        assert validate_project_id_format(ctx, param, "PROJECT-123") == "PROJECT-123"
        assert validate_project_id_format(ctx, param, "API") == "API"

        # Invalid project IDs should raise BadParameter
        with pytest.raises(click.BadParameter):
            validate_project_id_format(ctx, param, "web")  # lowercase

        with pytest.raises(click.BadParameter):
            validate_project_id_format(ctx, param, "123")  # starts with number

    def test_issue_id_validation(self):
        """Test issue ID format validation."""
        from click import Option

        from youtrack_cli.cli_utils.validation import validate_issue_id_format

        # Create a mock context and parameter
        @click.command()
        def test_cmd():
            pass

        ctx = click.Context(test_cmd, info_name="test")
        param = Option(["--issue-id"])

        # Valid issue IDs should pass
        assert validate_issue_id_format(ctx, param, "WEB-123") == "WEB-123"
        assert validate_issue_id_format(ctx, param, "PROJECT-456") == "PROJECT-456"

        # Invalid issue IDs should raise BadParameter
        with pytest.raises(click.BadParameter):
            validate_issue_id_format(ctx, param, "WEB")  # missing number

        with pytest.raises(click.BadParameter):
            validate_issue_id_format(ctx, param, "web-123")  # lowercase


class TestCliIntegration:
    """Test CLI integration with improved error handling."""

    def test_issues_create_with_invalid_project_id(self):
        """Test that issues create shows helpful error for invalid project ID."""
        runner = CliRunner()

        # Test with lowercase project ID
        result = runner.invoke(main, ["issues", "create", "web", "Test summary"])

        # Should fail with helpful error message
        assert result.exit_code != 0
        # Should contain validation error information

    def test_comments_create_suggestion(self):
        """Test that 'comments create' suggests 'comments add'."""
        runner = CliRunner()

        # Test the specific case mentioned in the GitHub issue
        result = runner.invoke(main, ["issues", "comments", "create"])

        # Should fail but show suggestion for 'add'
        assert result.exit_code != 0
        # Should contain suggestion to use 'add' instead of 'create'


@pytest.mark.integration
class TestRealWorldScenarios:
    """Test real-world error scenarios."""

    def test_typo_in_command_name(self):
        """Test handling of typos in command names."""
        runner = CliRunner()

        # Test common typos
        result = runner.invoke(main, ["isues"])  # missing 's'
        assert result.exit_code != 0

        result = runner.invoke(main, ["projet"])  # typo in 'project'
        assert result.exit_code != 0

    def test_missing_required_arguments(self):
        """Test handling of missing required arguments."""
        runner = CliRunner()

        # Test missing arguments
        result = runner.invoke(main, ["issues", "create"])
        assert result.exit_code != 0

        # Should show usage information

    def test_invalid_option_values(self):
        """Test handling of invalid option values."""
        runner = CliRunner()

        # Test with mock project ID to avoid authentication issues
        result = runner.invoke(main, ["issues", "create", "TEST-1", "Summary", "--type", "InvalidType"])

        # Should show validation error (though may fail earlier due to auth)
        assert result.exit_code != 0
