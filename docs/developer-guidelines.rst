Developer Guidelines
====================

Docstring Standards
-------------------

This project follows Google-style docstrings for all Python code. Consistent documentation is crucial for maintainability and API generation.

Docstring Convention
~~~~~~~~~~~~~~~~~~~~

We use **Google-style docstrings** exclusively. Do not mix with NumPy or other styles.

Basic Structure
~~~~~~~~~~~~~~~

.. code-block:: python

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

Module Docstrings
~~~~~~~~~~~~~~~~~

Every module should have a comprehensive docstring:

.. code-block:: python

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

Class Docstrings
~~~~~~~~~~~~~~~~

Classes should document their purpose, key attributes, and usage:

.. code-block:: python

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

Method and Function Docstrings
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Required Sections
^^^^^^^^^^^^^^^^^

- **Summary**: One-line description
- **Args**: Document all parameters
- **Returns**: Describe return value (if not None)
- **Raises**: List possible exceptions

Optional Sections
^^^^^^^^^^^^^^^^^

- **Example**: Code examples showing usage
- **Note**: Important behavioral notes
- **Warning**: Critical warnings about usage

Parameter Documentation
^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    Args:
        param_name: Simple description for basic parameters.
        complex_param: More detailed description for complex parameters.
            Can span multiple lines when needed. Include type information
            if not obvious from type hints.
        optional_param: Description. Defaults to None.
            Use "Defaults to X" format for default values.

Return Value Documentation
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    Returns:
        Simple description for basic returns.

    Returns:
        dict: More complex returns should specify the type.
            Can include structure information:
            {
                'key1': 'Description of key1',
                'key2': 'Description of key2'
            }

Exception Documentation
^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    Raises:
        ValueError: When input parameters are invalid.
        ConnectionError: When YouTrack API is unreachable.
        AuthenticationError: When credentials are invalid or expired.

Examples in Docstrings
~~~~~~~~~~~~~~~~~~~~~~

Include practical examples for complex functions:

.. code-block:: python

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

Python Doctests in Function Docstrings
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This project uses Python's built-in doctest functionality to ensure that code examples
in function docstrings remain accurate and working. Doctests are automatically run as
part of our test suite.

When to Use Doctests
^^^^^^^^^^^^^^^^^^^^

Use doctests for:

- **Pure functions**: Functions with predictable inputs and outputs
- **Utility functions**: Helper functions that don't require complex setup
- **Data transformation**: Functions that format, convert, or process data
- **Simple validation**: Functions that validate input or perform checks

Avoid doctests for:

- **Async functions**: Unless you can mock them properly
- **Functions requiring external services**: API calls, database operations
- **Functions with complex setup**: Those needing multiple dependencies
- **Functions with unpredictable output**: Current time, random values, etc.

Doctest Examples
^^^^^^^^^^^^^^^^

**Basic function with simple examples:**

.. code-block:: python

    def format_timestamp(timestamp: Union[int, str, None]) -> str:
        """Format a timestamp value for display.

        Args:
            timestamp: Unix timestamp (int), ISO string, or None

        Returns:
            Formatted timestamp string or "N/A" if None/empty

        Examples:
            >>> format_timestamp(None)
            'N/A'
            >>> format_timestamp('')
            'N/A'
            >>> format_timestamp(1640995200000)  # 2022-01-01 00:00:00
            '2022-01-01 00:00:00'
            >>> format_timestamp("1640995200000")
            '2022-01-01 00:00:00'
        """

**Function with multiple test cases:**

.. code-block:: python

    def optimize_fields(base_params=None, fields=None, exclude_fields=None):
        """Optimize API request parameters.

        Examples:
            >>> result = optimize_fields(
            ...     base_params={"project": "PROJ"},
            ...     fields=["id", "summary"]
            ... )
            >>> result["project"]
            'PROJ'
            >>> result["fields"]
            'id,summary'
            >>> optimize_fields()
            {}
        """

**Class method with doctest:**

.. code-block:: python

    class PaginationConfig:
        @classmethod
        def get_pagination_type(cls, endpoint: str) -> PaginationType:
            """Determine pagination type for endpoint.

            Examples:
                >>> result = PaginationConfig.get_pagination_type("/api/issues")
                >>> result.value
                'cursor'
                >>> result = PaginationConfig.get_pagination_type("/unknown")
                >>> result.value
                'offset'
            """

Doctest Best Practices
^^^^^^^^^^^^^^^^^^^^^^

**Use predictable data:**

.. code-block:: python

    # Good - predictable output
    >>> len(['a', 'b', 'c'])
    3

    # Avoid - unpredictable output
    >>> import datetime
    >>> datetime.datetime.now()  # Changes every time

**Handle complex objects:**

.. code-block:: python

    # Good - test specific attributes
    >>> result = create_user("john")
    >>> result.name
    'john'
    >>> result.active
    True

    # Avoid - complex object representation
    >>> create_user("john")  # __repr__ may be unstable

**Use ellipsis for partial matches:**

.. code-block:: python

    >>> big_dict = {"key": "value", "items": [1, 2, 3]}
    >>> print(big_dict)  # doctest: +ELLIPSIS
    {'key': 'value', ...}

**Skip problematic examples:**

.. code-block:: python

    >>> complex_async_operation()  # doctest: +SKIP
    <ComplexResult object at 0x...>

Running Doctests
^^^^^^^^^^^^^^^^

Doctests run automatically with pytest:

.. code-block:: bash

    # Run all tests including doctests
    uv run pytest

    # Run only doctests
    uv run python -m doctest youtrack_cli/utils.py

    # Run doctests with verbose output
    uv run python -m doctest -v youtrack_cli/utils.py

Configuration
^^^^^^^^^^^^^

Doctest configuration is set in ``pyproject.toml``:

.. code-block:: toml

    [tool.pytest.ini_options]
    addopts = [
        # ... other options ...
        "--doctest-modules",  # Enable doctest discovery
    ]
    doctest_optionflags = [
        "NORMALIZE_WHITESPACE",      # Ignore whitespace differences
        "ELLIPSIS",                  # Allow ... in expected output
        "IGNORE_EXCEPTION_DETAIL",   # Ignore exception detail differences
    ]

Integration with CI/CD
^^^^^^^^^^^^^^^^^^^^^^

Doctests run automatically in our CI pipeline:

- **Pull requests**: All doctests must pass before merging
- **Main branch**: Doctests run on every commit
- **Release**: Doctests are part of the release verification

Quality Requirements
^^^^^^^^^^^^^^^^^^^^

For functions with doctests:

- All examples must be runnable and produce expected output
- Examples should demonstrate typical use cases
- Edge cases should be covered when relevant
- Output should be predictable across different environments

Troubleshooting Common Issues
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Import errors in doctests:**

.. code-block:: python

    # Add necessary imports to the module
    from typing import Union, Optional
    from .exceptions import ValidationError

**Whitespace issues:**

.. code-block:: python

    # Use NORMALIZE_WHITESPACE flag (already configured)
    >>> format_list([1, 2, 3])
    '1, 2, 3'

**Platform-specific differences:**

.. code-block:: python

    # Use ellipsis for platform-specific parts
    >>> get_file_path()  # doctest: +ELLIPSIS
    '/...user/.../config'

**Async function testing:**

.. code-block:: python

    # Generally avoid, but if needed:
    >>> import asyncio
    >>> asyncio.run(my_async_function())  # doctest: +SKIP
    'expected result'

Type Hints Integration
~~~~~~~~~~~~~~~~~~~~~~

Docstrings should complement, not duplicate, type hints:

.. code-block:: python

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

CLI Command Docstrings
~~~~~~~~~~~~~~~~~~~~~~

CLI commands need special attention for help text:

.. code-block:: python

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

Quality Standards
-----------------

Docstring Linting
~~~~~~~~~~~~~~~~~

We use ``pydocstyle`` with Google convention:

.. code-block:: bash

    # Check docstring compliance
    uv run pydocstyle youtrack_cli/

    # Run as part of pre-commit
    pre-commit run pydocstyle

Configuration
~~~~~~~~~~~~~

See ``pyproject.toml`` for pydocstyle configuration:

.. code-block:: toml

    [tool.pydocstyle]
    convention = "google"
    add_ignore = ["D100", "D104", "D105", "D107"]
    match_dir = "youtrack_cli"
    match = "(?!test_).*\.py"

Sphinx Integration
~~~~~~~~~~~~~~~~~~

Docstrings are automatically processed by Sphinx with Napoleon extension:

.. code-block:: python

    # Generate documentation
    cd docs/
    sphinx-build -b html . _build/html

Best Practices
--------------

1. Keep It Practical
~~~~~~~~~~~~~~~~~~~~

Focus on what developers need to know:

- **Purpose**: What does this do?
- **Usage**: How do I use it?
- **Parameters**: What do I pass in?
- **Returns**: What do I get back?
- **Exceptions**: What can go wrong?

2. Use Examples Generously
~~~~~~~~~~~~~~~~~~~~~~~~~~

Good examples are worth more than lengthy descriptions:

.. code-block:: python

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

3. Document Edge Cases
~~~~~~~~~~~~~~~~~~~~~

Mention important behavioral details:

.. code-block:: python

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

4. Link Related Functions
~~~~~~~~~~~~~~~~~~~~~~~~~

Reference related functionality:

.. code-block:: python

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

5. Update Documentation with Code
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When changing function behavior:

1. Update the docstring first
2. Update examples if needed
3. Update type hints if needed
4. Update tests
5. Update user documentation if public API

6. Review Checklist
~~~~~~~~~~~~~~~~~~~

Before committing, verify:

- [ ] Module has comprehensive docstring
- [ ] All public classes have docstrings
- [ ] All public methods have docstrings
- [ ] Parameters and returns are documented
- [ ] Exceptions are documented
- [ ] Examples are provided for complex functions
- [ ] ``pydocstyle`` passes without warnings
- [ ] Sphinx can generate docs without errors

Tools and Automation
--------------------

Pre-commit Integration
~~~~~~~~~~~~~~~~~~~~~~

Docstring quality is enforced via pre-commit hooks:

.. code-block:: yaml

    - id: pydocstyle
      name: pydocstyle
      entry: uv run pydocstyle
      language: system
      types: [python]
      exclude: ^tests/

Sphinx Configuration
~~~~~~~~~~~~~~~~~~~~

API documentation is generated automatically from docstrings:

.. code-block:: python

    # docs/conf.py
    extensions = [
        "sphinx.ext.autodoc",
        "sphinx.ext.napoleon",
        "sphinx_autodoc_typehints",
    ]

    napoleon_google_docstring = True
    napoleon_include_init_with_doc = True

IDE Integration
~~~~~~~~~~~~~~~

Configure your IDE for Google-style docstrings:

- **PyCharm**: Settings → Tools → Python Integrated Tools → Docstring format: Google
- **VS Code**: Python Docstring Generator extension with Google style
- **Vim**: Use vim-pydocstring with Google template

Remember: Good documentation is a gift to your future self and your teammates. Take the time to write clear, helpful docstrings that explain not just what the code does, but why and how to use it effectively.

Documentation Testing
----------------------

This project implements comprehensive documentation testing to ensure code examples stay current and links remain valid.

Overview
~~~~~~~~

Documentation testing includes:

- **Doctest verification**: Code examples in documentation are automatically tested
- **Link checking**: External and internal links are validated
- **Build verification**: Documentation builds without warnings or errors
- **Pre-commit integration**: Documentation quality checks run before commits
- **CI/CD enforcement**: Documentation tests must pass for all pull requests

Configuration
~~~~~~~~~~~~~

Doctest configuration in ``pyproject.toml``:

.. code-block:: toml

    [tool.pytest.ini_options]
    addopts = "-v --tb=short --strict-markers --doctest-glob='*.rst'"
    doctest_optionflags = ["NORMALIZE_WHITESPACE", "ELLIPSIS", "IGNORE_EXCEPTION_DETAIL"]
    markers = [
        "doctest: marks tests as doctests (documentation code examples)",
    ]

Sphinx configuration in ``docs/conf.py``:

.. code-block:: python

    extensions = [
        "sphinx.ext.doctest",      # Enable doctest support
        "sphinx.ext.linkcheck",    # Enable link checking
        # ... other extensions
    ]

    # Doctest global setup for consistent testing environment
    doctest_global_setup = """
    import asyncio
    import os
    from unittest.mock import AsyncMock, MagicMock

    # Mock environment for consistent testing
    os.environ.setdefault('YOUTRACK_BASE_URL', 'https://youtrack.example.com')
    os.environ.setdefault('YOUTRACK_TOKEN', 'test-token')
    """

    # Link checking configuration
    linkcheck_ignore = [
        r'http://localhost.*',
        r'https://youtrack\.example\.com.*',
    ]
    linkcheck_timeout = 30
    linkcheck_retries = 2

Running Documentation Tests
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Local testing commands:

.. code-block:: bash

    # Test RST-based doctests
    uv run pytest --doctest-glob='*.rst' docs/ -v

    # Build documentation with error checking
    uv run sphinx-build -b html docs docs/_build/html -W

    # Run Sphinx doctests
    uv run sphinx-build -b doctest docs docs/_build/doctest

    # Check documentation links
    uv run sphinx-build -b linkcheck docs docs/_build/linkcheck

    # Run pre-commit documentation hooks
    pre-commit run doctests
    pre-commit run sphinx-build

CI/CD Integration
~~~~~~~~~~~~~~~~~

Documentation testing is integrated into the CI pipeline with a dedicated job:

.. code-block:: yaml

    documentation:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v4
        - name: Install dependencies
          run: uv sync --dev --group docs
        - name: Build documentation
          run: uv run sphinx-build -b html docs docs/_build/html -W --keep-going
        - name: Run doctests
          run: uv run sphinx-build -b doctest docs docs/_build/doctest
        - name: Check documentation links
          run: uv run sphinx-build -b linkcheck docs docs/_build/linkcheck
        - name: Run pytest doctests
          run: uv run pytest --doctest-glob='*.rst' docs/ -v

The documentation job is required for all pull requests and must pass before merging.

Pre-commit Hooks
~~~~~~~~~~~~~~~~

Documentation testing is integrated into pre-commit workflow:

.. code-block:: yaml

    - id: doctests
      name: doctests
      entry: uv run pytest --doctest-glob='*.rst' docs/
      language: system
      files: ^docs/.*\.rst$

    - id: sphinx-build
      name: sphinx-build
      entry: uv run sphinx-build -b html docs docs/_build/html -W
      language: system
      files: ^docs/.*\.rst$

These hooks run automatically when documentation files are modified.

Writing Testable Documentation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Best practices for documentation examples:

**Use realistic but simple examples:**

.. code-block:: rst

    Basic usage example:

    .. code-block:: python

        # Create a configuration manager
        config = ConfigManager()
        config.set_config('BASE_URL', 'https://youtrack.example.com')

        # Retrieve configuration
        url = config.get_config('BASE_URL')
        print(f"Using YouTrack at: {url}")

**Avoid examples that require external dependencies:**

.. code-block:: rst

    Good - uses mocked responses:

    .. code-block:: python

        # Example with predictable output
        result = process_data(['item1', 'item2'])
        print(len(result))  # Output: 2

    Avoid - requires real API:

    .. code-block:: python

        # This would fail in testing
        api = YouTrackAPI('https://real-server.com')
        issues = api.get_issues()  # Unpredictable/fails

**Use doctest directives when needed:**

.. code-block:: rst

    Example with output normalization:

    .. code-block:: python

        >>> result = {'key': 'value', 'items': [1, 2, 3]}
        >>> print(result)  # doctest: +SKIP
        {'key': 'value', 'items': [1, 2, 3]}

Troubleshooting
~~~~~~~~~~~~~~~

**Common doctest failures:**

1. **Inconsistent whitespace**: Use ``NORMALIZE_WHITESPACE`` flag
2. **Unpredictable output**: Use ``ELLIPSIS`` or ``+SKIP`` directive
3. **Async code**: Ensure proper async/await handling in examples
4. **Environment differences**: Use consistent mock data

**Link checking issues:**

1. **Temporary failures**: Links may be temporarily unavailable
2. **Rate limiting**: External sites may rate-limit requests
3. **Authentication required**: Some links require login
4. **Local development**: localhost URLs should be excluded

**Build failures:**

1. **Missing dependencies**: Ensure all Sphinx extensions are installed
2. **Circular imports**: Check for import issues in documented modules
3. **Malformed RST**: Validate RST syntax with sphinx-build warnings

Maintenance
~~~~~~~~~~~

Regular maintenance tasks:

1. **Weekly link checking**: Review and update broken links
2. **Quarterly example review**: Ensure examples reflect current API
3. **Version updates**: Update examples when API changes
4. **Performance monitoring**: Track documentation build times

Quality Gates
~~~~~~~~~~~~~

Documentation quality requirements:

- All documentation builds without warnings
- All doctests pass in CI
- External links are validated (with exceptions for known issues)
- Pre-commit hooks pass for all documentation changes
- RST syntax is valid and consistent

The documentation testing system ensures that:

- Code examples in documentation remain accurate
- Links to external resources stay valid
- Documentation builds successfully in all environments
- Contributors receive immediate feedback on documentation quality
- Documentation stays synchronized with code changes
