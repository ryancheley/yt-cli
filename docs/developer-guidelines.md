# Developer Guidelines

## Docstring Standards

This project follows Google-style docstrings for all Python code. Consistent documentation is crucial for maintainability and API generation.

### Docstring Convention

We use **Google-style docstrings** exclusively. Do not mix with NumPy or other styles.

### Basic Structure

```python
def function_name(param1: str, param2: int = 0) -> bool:
    """One-line summary of what the function does.

    Longer description if needed, explaining behavior, algorithm,
    or providing additional context. This can span multiple lines
    and include implementation details.

    Args:
        param1: Description of param1.
        param2: Description of param2. Defaults to 0.

    Returns:
        Description of return value.

    Raises:
        ExceptionType: Description of when this exception is raised.
        AnotherException: Description of another exception condition.

    Example:
        >>> result = function_name("hello", 5)
        >>> print(result)
        True

    Note:
        Additional notes about usage, performance, or behavior.
    """
```

### Module Docstrings

Every module should have a comprehensive docstring:

```python
"""Module title - brief description.

Longer description explaining the module's purpose, main functionality,
and how it fits into the overall application architecture.

This module provides [key functionality] including [list main features].
It integrates with [other components] to [explain integration].

Example:
    >>> from youtrack_cli import auth
    >>> auth_manager = auth.AuthManager()
    >>> result = await auth_manager.verify_credentials()
"""
```

### Class Docstrings

Classes should document their purpose, key attributes, and usage:

```python
class ExampleClass:
    """Brief description of the class purpose.

    Detailed explanation of what the class does, its main responsibilities,
    and how it should be used. Include information about state management,
    threading safety, or other important behavioral characteristics.

    Attributes:
        attribute1: Description of public attribute.
        attribute2: Description of another attribute.

    Example:
        >>> instance = ExampleClass("config")
        >>> result = instance.do_something()
    """
```

### Method and Function Docstrings

#### Required Sections

- **Summary**: One-line description
- **Args**: Document all parameters
- **Returns**: Describe return value (if not None)
- **Raises**: List possible exceptions

#### Optional Sections

- **Example**: Code examples showing usage
- **Note**: Important behavioral notes
- **Warning**: Critical warnings about usage

#### Parameter Documentation

```python
Args:
    param_name: Simple description for basic parameters.
    complex_param: More detailed description for complex parameters.
        Can span multiple lines when needed. Include type information
        if not obvious from type hints.
    optional_param: Description. Defaults to None.
        Use "Defaults to X" format for default values.
```

#### Return Value Documentation

```python
Returns:
    Simple description for basic returns.

Returns:
    dict: More complex returns should specify the type.
        Can include structure information:
        {
            'key1': 'Description of key1',
            'key2': 'Description of key2'
        }
```

#### Exception Documentation

```python
Raises:
    ValueError: When input parameters are invalid.
    ConnectionError: When YouTrack API is unreachable.
    AuthenticationError: When credentials are invalid or expired.
```

### Examples in Docstrings

Include practical examples for complex functions:

```python
Example:
    Basic usage:

    >>> manager = AuthManager()
    >>> config = AuthConfig(
    ...     base_url="https://youtrack.example.com",
    ...     token="your-api-token"
    ... )
    >>> result = await manager.verify_credentials(config)
    >>> print(result.status)
    'success'

    Error handling:

    >>> try:
    ...     result = await manager.verify_credentials(bad_config)
    ... except AuthenticationError as e:
    ...     print(f"Auth failed: {e}")
```

### Type Hints Integration

Docstrings should complement, not duplicate, type hints:

```python
def process_data(
    items: list[dict[str, Any]],
    filter_func: Optional[Callable[[dict], bool]] = None
) -> dict[str, int]:
    """Process a list of data items with optional filtering.

    Args:
        items: List of data dictionaries to process.
        filter_func: Optional function to filter items. If None,
            all items are processed.

    Returns:
        Dictionary mapping item types to counts.
    """
```

### CLI Command Docstrings

CLI commands need special attention for help text:

```python
@click.command()
@click.argument("project_id")
@click.option("--assignee", help="Assign issue to user")
def create_issue(project_id: str, assignee: Optional[str]) -> None:
    """Create a new issue in the specified project.

    Creates a new YouTrack issue with the provided details. The issue
    will be created in the specified project and can optionally be
    assigned to a user.

    Args:
        project_id: Target project identifier (e.g., 'PROJ').
        assignee: Optional username to assign the issue to.

    Example:
        Create a basic issue:

        $ yt issues create PROJ "Fix login bug"

        Create and assign an issue:

        $ yt issues create PROJ "Add feature" --assignee john.doe
    """
```

## Quality Standards

### Docstring Linting

We use `pydocstyle` with Google convention:

```bash
# Check docstring compliance
uv run pydocstyle youtrack_cli/

# Run as part of pre-commit
pre-commit run pydocstyle
```

### Configuration

See `pyproject.toml` for pydocstyle configuration:

```toml
[tool.pydocstyle]
convention = "google"
add_ignore = ["D100", "D104", "D105", "D107"]
match_dir = "youtrack_cli"
match = "(?!test_).*\.py"
```

### Sphinx Integration

Docstrings are automatically processed by Sphinx with Napoleon extension:

```python
# Generate documentation
cd docs/
sphinx-build -b html . _build/html
```

## Best Practices

### 1. Keep It Practical

Focus on what developers need to know:

- **Purpose**: What does this do?
- **Usage**: How do I use it?
- **Parameters**: What do I pass in?
- **Returns**: What do I get back?
- **Exceptions**: What can go wrong?

### 2. Use Examples Generously

Good examples are worth more than lengthy descriptions:

```python
def search_issues(query: str, project: Optional[str] = None) -> list[Issue]:
    """Search for issues using YouTrack query syntax.

    Args:
        query: YouTrack search query.
        project: Optional project to limit search to.

    Returns:
        List of matching issues.

    Example:
        >>> # Find high-priority bugs
        >>> issues = search_issues("Type: Bug Priority: High")
        >>>
        >>> # Find your assigned issues in a project
        >>> my_issues = search_issues("assignee: me", project="PROJ")
    """
```

### 3. Document Edge Cases

Mention important behavioral details:

```python
def paginate_results(items: list, page_size: int = 50) -> Iterator[list]:
    """Split items into pages for display.

    Args:
        items: Items to paginate.
        page_size: Items per page. Must be positive.

    Yields:
        Pages of items as lists.

    Note:
        Empty input returns no pages. Last page may contain fewer
        than page_size items.

    Raises:
        ValueError: When page_size is not positive.
    """
```

### 4. Link Related Functions

Reference related functionality:

```python
def authenticate(token: str) -> AuthResult:
    """Authenticate with YouTrack API.

    Args:
        token: API token from YouTrack settings.

    Returns:
        Authentication result with user info.

    See Also:
        verify_credentials(): Check existing authentication.
        logout(): Clear stored credentials.
    """
```

### 5. Update Documentation with Code

When changing function behavior:

1. Update the docstring first
2. Update examples if needed
3. Update type hints if needed
4. Update tests
5. Update user documentation if public API

### 6. Review Checklist

Before committing, verify:

- [ ] Module has comprehensive docstring
- [ ] All public classes have docstrings
- [ ] All public methods have docstrings
- [ ] Parameters and returns are documented
- [ ] Exceptions are documented
- [ ] Examples are provided for complex functions
- [ ] `pydocstyle` passes without warnings
- [ ] Sphinx can generate docs without errors

## Tools and Automation

### Pre-commit Integration

Docstring quality is enforced via pre-commit hooks:

```yaml
- id: pydocstyle
  name: pydocstyle
  entry: uv run pydocstyle
  language: system
  types: [python]
  exclude: ^tests/
```

### Sphinx Configuration

API documentation is generated automatically from docstrings:

```python
# docs/conf.py
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx_autodoc_typehints",
]

napoleon_google_docstring = True
napoleon_include_init_with_doc = True
```

### IDE Integration

Configure your IDE for Google-style docstrings:

- **PyCharm**: Settings → Tools → Python Integrated Tools → Docstring format: Google
- **VS Code**: Python Docstring Generator extension with Google style
- **Vim**: Use vim-pydocstring with Google template

Remember: Good documentation is a gift to your future self and your teammates. Take the time to write clear, helpful docstrings that explain not just what the code does, but why and how to use it effectively.
