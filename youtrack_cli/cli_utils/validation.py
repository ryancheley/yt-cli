"""Click validation utilities for better error messages."""

import functools
from typing import Any, Callable, List, Optional

import click

from ..exceptions import ParameterError, UsageError
from ..utils import display_error, handle_error


def validate_choices_with_suggestions(choices: List[str], case_sensitive: bool = False, suggestion_cutoff: float = 0.6):
    """Create a Click option validator that suggests similar choices on error."""

    def validator(ctx: click.Context, param: click.Parameter, value: str) -> str:
        if value is None:
            return value

        # Check if value is valid
        comparison_choices = choices if case_sensitive else [c.lower() for c in choices]
        comparison_value = value if case_sensitive else value.lower()

        if comparison_value in comparison_choices:
            # Return original case from choices if case insensitive match
            if not case_sensitive:
                for choice in choices:
                    if choice.lower() == comparison_value:
                        return choice
            return value

        # Value is invalid, suggest similar choices
        import difflib

        suggestions = difflib.get_close_matches(comparison_value, comparison_choices, n=3, cutoff=suggestion_cutoff)

        # Map back to original case
        if not case_sensitive:
            original_suggestions = []
            for suggestion in suggestions:
                for choice in choices:
                    if choice.lower() == suggestion:
                        original_suggestions.append(choice)
                        break
            suggestions = original_suggestions

        error = ParameterError(
            f"Invalid value '{value}' for parameter '{param.name}'",
            parameter_name=param.name,
            valid_choices=suggestions if suggestions else choices[:5],
            usage_example=f"--{param.name} {suggestions[0] if suggestions else choices[0]}",
        )

        error_result = handle_error(error, f"parameter validation for {param.name}")
        display_error(error_result)

        # Still raise the Click exception for normal flow
        raise click.BadParameter(f"Invalid choice '{value}'. {error.suggestion}")

    return validator


def require_one_of(*params: str):
    """Decorator to ensure at least one of the specified parameters is provided."""

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Check if at least one required parameter is provided
            provided_params = [param for param in params if kwargs.get(param) is not None]

            if not provided_params:
                # Get the Click context to determine command info
                ctx = click.get_current_context()

                error = UsageError(
                    f"At least one of the following parameters is required: {', '.join(params)}",
                    command_path=ctx.info_name or "yt",
                    usage_syntax=f"{ctx.info_name} --{params[0]} VALUE [OTHER_OPTIONS]",
                    examples=[f"{ctx.info_name} --{param} example_value" for param in params[:2]],
                    common_mistakes=[f"Forgetting to specify any of: {', '.join(params)}"],
                )

                error_result = handle_error(error, "parameter validation")
                display_error(error_result)
                raise click.ClickException(f"Missing required parameter. {error.suggestion}")

            return func(*args, **kwargs)

        return wrapper

    return decorator


def mutually_exclusive(*params: str):
    """Decorator to ensure parameters are mutually exclusive."""

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            provided_params = [param for param in params if kwargs.get(param) is not None]

            if len(provided_params) > 1:
                error = ParameterError(
                    f"Parameters {', '.join(provided_params)} are mutually exclusive",
                    usage_example=f"Use only one of: --{params[0]} or --{params[1]}",
                )

                error_result = handle_error(error, "parameter validation")
                display_error(error_result)
                raise click.ClickException(f"Conflicting parameters. {error.suggestion}")

            return func(*args, **kwargs)

        return wrapper

    return decorator


def validate_project_id_format(ctx: click.Context, param: click.Parameter, value: str) -> str:
    """Validate YouTrack project ID format."""
    if value is None:
        return value

    # YouTrack project IDs are typically uppercase letters and numbers, sometimes with hyphens
    import re

    if not re.match(r"^[A-Z][A-Z0-9]*(-[A-Z0-9]+)*$", value):
        error = ParameterError(
            f"Invalid project ID format: '{value}'",
            parameter_name=param.name,
            expected_type="uppercase letters and numbers (e.g., 'PROJECT', 'WEB-API')",
            usage_example=f"--{param.name} PROJECT-123",
        )

        error_result = handle_error(error, "project ID validation")
        display_error(error_result)
        raise click.BadParameter(f"Invalid project ID format. {error.suggestion}")

    return value


def validate_issue_id_format(ctx: click.Context, param: click.Parameter, value: str) -> str:
    """Validate YouTrack issue ID format."""
    if value is None:
        return value

    # YouTrack issue IDs are typically PROJECT-NUMBER format
    import re

    if not re.match(r"^[A-Z][A-Z0-9]*(-[A-Z0-9]+)*-\d+$", value):
        error = ParameterError(
            f"Invalid issue ID format: '{value}'",
            parameter_name=param.name,
            expected_type="format: PROJECT-NUMBER (e.g., 'WEB-123', 'API-456')",
            usage_example=f"{param.name} PROJECT-123",
        )

        error_result = handle_error(error, "issue ID validation")
        display_error(error_result)
        raise click.BadParameter(f"Invalid issue ID format. {error.suggestion}")

    return value


class EnhancedOption(click.Option):
    """Enhanced Click option with better error messages."""

    def __init__(
        self, *args, suggestions: Optional[List[str]] = None, usage_examples: Optional[List[str]] = None, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.suggestions = suggestions or []
        self.usage_examples = usage_examples or []

    def full_process_value(self, ctx: click.Context, param: click.Parameter, value: Any) -> Any:
        """Process and validate parameter value with enhanced error handling."""
        try:
            return super().full_process_value(ctx, param, value)
        except click.BadParameter as e:
            # Enhance the error message
            enhanced_error = ParameterError(
                str(e),
                parameter_name=self.name,
                usage_example=self.usage_examples[0] if self.usage_examples else None,
                valid_choices=self.suggestions if self.suggestions else None,
            )

            error_result = handle_error(enhanced_error, f"parameter {self.name}")
            display_error(error_result)
            raise


def enhanced_option(*args, **kwargs):
    """Create an enhanced option with better error messages."""
    return click.option(*args, cls=EnhancedOption, **kwargs)
