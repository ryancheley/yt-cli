Development
===========

This guide covers setting up a development environment and contributing to YouTrack CLI.

Development Setup
-----------------

Prerequisites
~~~~~~~~~~~~~

* Python 3.9 or higher
* `uv <https://docs.astral.sh/uv/>`_ package manager
* Git

Clone and Setup
~~~~~~~~~~~~~~~

1. Clone the repository:

   .. code-block:: bash

      git clone https://github.com/ryancheley/yt-cli.git
      cd yt-cli

2. Install development dependencies:

   .. code-block:: bash

      uv sync --dev

3. Install pre-commit hooks:

   .. code-block:: bash

      uv run pre-commit install

4. Verify the setup:

   .. code-block:: bash

      uv run pytest
      uv run ruff check
      uv run ty check

Project Structure
-----------------

.. code-block:: text

   yt-cli/
   ├── youtrack_cli/           # Main package
   │   ├── __init__.py
   │   ├── main.py            # CLI entry point and command definitions
   │   ├── admin.py           # Admin operations manager
   │   ├── articles.py        # Articles management
   │   ├── auth.py            # Authentication manager
   │   ├── boards.py          # Boards management
   │   ├── common.py          # Common CLI options and decorators
   │   ├── config.py          # Configuration management
   │   ├── exceptions.py      # Custom exception classes
   │   ├── issues.py          # Issues management (core functionality)
   │   ├── logging.py         # Logging infrastructure
   │   ├── projects.py        # Projects management
   │   ├── reports.py         # Reports generation
   │   ├── time.py            # Time tracking
   │   ├── users.py           # User management
   │   └── utils.py           # HTTP utilities and error handling
   ├── tests/                 # Comprehensive test suite
   │   ├── test_admin.py      # Admin functionality tests
   │   ├── test_articles.py   # Articles tests
   │   ├── test_auth.py       # Authentication tests
   │   ├── test_boards.py     # Boards tests
   │   ├── test_config.py     # Configuration tests
   │   ├── test_issues.py     # Issues tests (48 test cases)
   │   ├── test_main.py       # CLI interface tests
   │   ├── test_projects.py   # Projects tests
   │   ├── test_reports.py    # Reports tests
   │   ├── test_time.py       # Time tracking tests
   │   └── test_users.py      # User management tests
   ├── docs/                  # Sphinx documentation
   │   ├── commands/          # Command-specific documentation
   │   ├── conf.py            # Sphinx configuration
   │   ├── index.rst          # Documentation index
   │   ├── installation.rst   # Installation guide
   │   ├── quickstart.rst     # Quick start guide
   │   └── development.rst    # This file
   ├── pyproject.toml         # Project configuration and dependencies
   ├── uv.lock                # Dependency lock file
   ├── tox.ini                # Multi-version testing configuration
   ├── justfile               # Task runner configuration
   └── README.md              # Project overview

Dependency Management
---------------------

The project uses PEP 735 dependency groups for managing development dependencies. This provides a standardized way to organize and install different sets of dependencies.

Dependency Groups
~~~~~~~~~~~~~~~~~

The project defines the following dependency groups in ``pyproject.toml``:

* **dev**: Development tools including testing, linting, and type checking
* **docs**: Documentation generation tools

Installing Dependencies
~~~~~~~~~~~~~~~~~~~~~~~

Using uv (recommended):

.. code-block:: bash

   # Install all dependencies including dev group
   uv sync --dev

   # Install only production dependencies
   uv sync

Using pip (requires pip >= 24.0):

.. code-block:: bash

   # Install with dev dependencies
   pip install -e . --group dev

   # Install with docs dependencies
   pip install -e . --group docs

   # Install multiple groups
   pip install -e . --group dev --group docs

Development Workflow
--------------------

Creating Features
~~~~~~~~~~~~~~~~~

1. Create a GitHub issue for the feature
2. Create a feature branch:

   .. code-block:: bash

      git checkout -b feature/issue-123-add-feature

3. Implement the feature with tests
4. Update documentation
5. Submit a pull request

Code Quality
~~~~~~~~~~~~

The project uses several tools to maintain code quality:

* **Ruff**: Linting and code formatting
* **ty**: Type checking (modern replacement for MyPy)
* **Pytest**: Testing framework
* **Pre-commit**: Git hooks for quality checks
* **zizmor**: GitHub Actions security analysis

Run quality checks:

.. code-block:: bash

   # Run all pre-commit hooks
   uv run pre-commit run --all-files

   # Or run individual tools
   uv run ruff check .
   uv run ruff format .
   uv run ty check
   uv run pytest

Pre-commit Hooks
----------------

The project uses comprehensive pre-commit hooks to ensure code quality and consistency. These hooks run automatically before each commit and prevent commits with quality issues.

Hook Categories
~~~~~~~~~~~~~~~

**File Quality Checks:**

* Trailing whitespace removal
* End-of-file fixing
* YAML/TOML/JSON validation
* Large file detection
* Merge conflict detection
* Case conflict detection
* Executable shebang validation

**Code Quality Checks:**

* **Ruff linting** with auto-fix
* **Ruff formatting**
* **ty type checking** (excluding test files)
* **Debug statement detection**

**Testing:**

* **pytest** execution with optimized settings for pre-commit

**Security:**

* **zizmor** GitHub Actions security analysis

Managing Pre-commit Hooks
~~~~~~~~~~~~~~~~~~~~~~~~~~

Install hooks:

.. code-block:: bash

   uv run pre-commit install

Run all hooks manually:

.. code-block:: bash

   uv run pre-commit run --all-files

Run specific hook:

.. code-block:: bash

   uv run pre-commit run pytest
   uv run pre-commit run ruff
   uv run pre-commit run ty

Skip hooks (not recommended):

.. code-block:: bash

   git commit --no-verify

Update hook versions:

.. code-block:: bash

   uv run pre-commit autoupdate

Hook Configuration
~~~~~~~~~~~~~~~~~~

Pre-commit hooks are configured in ``.pre-commit-config.yaml``. The configuration includes:

* **Fast feedback**: Hooks are optimized for speed during development
* **Comprehensive coverage**: All CI checks are replicated locally
* **Auto-fixing**: Many issues are automatically corrected
* **Selective exclusions**: Test files excluded from type checking

Testing
-------

Test Structure
~~~~~~~~~~~~~~

Tests are organized into categories:

* **Unit tests**: Test individual functions and classes
* **Integration tests**: Test interaction with YouTrack API
* **End-to-end tests**: Test complete CLI workflows

Running Tests
~~~~~~~~~~~~~

The project uses pytest with randomized test execution to improve test reliability and catch order-dependent bugs.

Run all tests (automatically randomized order):

.. code-block:: bash

   uv run pytest

Run specific test categories:

.. code-block:: bash

   uv run pytest -m unit
   uv run pytest -m integration

Run with coverage:

.. code-block:: bash

   uv run pytest --cov=youtrack_cli --cov-report=html

**Randomized Testing Options:**

.. code-block:: bash

   # Run with specific random seed for reproducibility
   uv run pytest --randomly-seed=12345

   # Disable randomization if needed
   uv run pytest --randomly-dont-shuffle

   # Show current random seed
   uv run pytest --randomly-seed=last

The test suite uses ``pytest-randomly`` to randomize test execution order. Each test run displays the random seed used, which can be reused to reproduce specific test failures. This helps identify and eliminate order-dependent test bugs.

Multi-version Testing
~~~~~~~~~~~~~~~~~~~~~

Test against multiple Python versions using tox:

.. code-block:: bash

   uv run tox

Writing Tests
~~~~~~~~~~~~~

Example unit test:

.. code-block:: python

   import pytest
   from youtrack_cli.utils import parse_issue_id

   def test_parse_issue_id():
       project, number = parse_issue_id("PROJECT-123")
       assert project == "PROJECT"
       assert number == 123

   def test_parse_issue_id_invalid():
       with pytest.raises(ValueError):
           parse_issue_id("invalid-id")

Example integration test:

.. code-block:: python

   import pytest
   from youtrack_cli.client import YouTrackClient

   @pytest.mark.integration
   def test_list_issues(youtrack_client):
       issues = youtrack_client.issues.list(limit=5)
       assert len(issues) <= 5
       assert all(hasattr(issue, 'id') for issue in issues)

Adding New Commands
-------------------

Command Structure
~~~~~~~~~~~~~~~~~

Commands are organized using Click groups. Each command module follows this pattern:

.. code-block:: python

   import click
   from youtrack_cli.client import get_client

   @click.group()
   def issues():
       """Issue management commands."""
       pass

   @issues.command()
   @click.option('--title', required=True, help='Issue title')
   @click.option('--description', help='Issue description')
   def create(title, description):
       """Create a new issue."""
       client = get_client()
       issue = client.issues.create(title=title, description=description)
       click.echo(f"Created issue: {issue.id}")

Command Guidelines
~~~~~~~~~~~~~~~~~~

1. Use consistent option names across commands
2. Provide helpful help text for all options
3. Include examples in docstrings
4. Handle errors gracefully with user-friendly messages
5. Support multiple output formats where appropriate

Error Handling Infrastructure
-----------------------------

Custom Exceptions
~~~~~~~~~~~~~~~~~

The project uses a structured exception hierarchy for better error handling:

.. code-block:: python

   from youtrack_cli.exceptions import (
       YouTrackError,         # Base exception
       AuthenticationError,   # Login/token issues
       ConnectionError,       # Network problems
       NotFoundError,         # Missing resources
       PermissionError,       # Access denied
       ValidationError,       # Invalid input
       RateLimitError,       # Too many requests
   )

   # Example usage
   try:
       result = api_call()
   except AuthenticationError as e:
       console.print(f"[red]Error:[/red] {e.message}")
       if e.suggestion:
           console.print(f"[yellow]Suggestion:[/yellow] {e.suggestion}")

HTTP Utilities
~~~~~~~~~~~~~~

The ``utils.py`` module provides robust HTTP request handling:

.. code-block:: python

   from youtrack_cli.utils import make_request, handle_error, display_error

   # Automatic retry with exponential backoff
   response = await make_request(
       method="GET",
       url="https://youtrack.example.com/api/issues",
       headers={"Authorization": f"Bearer {token}"},
       max_retries=3,
       timeout=30
   )

   # Error handling with user-friendly messages
   try:
       result = risky_operation()
   except Exception as e:
       error_info = handle_error(e, "issue creation")
       display_error(error_info)

Common CLI Components
~~~~~~~~~~~~~~~~~~~~~

The ``common.py`` module provides reusable CLI components:

.. code-block:: python

   from youtrack_cli.common import common_options, async_command, handle_exceptions

   @click.command()
   @common_options  # Adds --format, --verbose, --debug, --no-color
   @async_command   # Handles async functions
   @handle_exceptions  # Catches and displays errors
   async def my_command(format, verbose, debug, console):
       """Example command with common options."""
       if verbose:
           console.print("Starting operation...")

Logging Infrastructure
~~~~~~~~~~~~~~~~~~~~~~

Enhanced logging with Rich formatting:

.. code-block:: python

   from youtrack_cli.logging import setup_logging, get_logger

   # Setup logging (usually in main CLI entry point)
   setup_logging(verbose=True, debug=False)

   # Get logger in any module
   logger = get_logger(__name__)
   logger.info("Operation started")
   logger.debug("Detailed debug information")
   logger.warning("Something to watch out for")

Adding API Endpoints
--------------------

Client Structure
~~~~~~~~~~~~~~~~

API clients are organized by resource type:

.. code-block:: python

   from typing import List, Optional
   from youtrack_cli.models import Issue

   class IssuesClient:
       def __init__(self, http_client):
           self.http = http_client

       def list(self, assignee: Optional[str] = None) -> List[Issue]:
           params = {}
           if assignee:
               params['assignee'] = assignee

           response = self.http.get('/issues', params=params)
           return [Issue.parse_obj(item) for item in response.json()]

       def create(self, **kwargs) -> Issue:
           response = self.http.post('/issues', json=kwargs)
           return Issue.parse_obj(response.json())

Model Definitions
~~~~~~~~~~~~~~~~~

Use Pydantic models for data validation:

.. code-block:: python

   from datetime import datetime
   from typing import Optional
   from pydantic import BaseModel, Field

   class Issue(BaseModel):
       id: str
       title: str = Field(alias='summary')
       description: Optional[str] = None
       state: str
       assignee: Optional[str] = None
       created: datetime
       updated: datetime

       class Config:
           allow_population_by_field_name = True

Documentation
-------------

Writing Documentation
~~~~~~~~~~~~~~~~~~~~~

* Use reStructuredText format
* Include code examples for all features
* Keep documentation up-to-date with code changes
* Add docstrings to all public functions and classes

Building Documentation Locally
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   cd docs
   uv run sphinx-build -b html . _build/html

The documentation will be available at ``docs/_build/html/index.html``.

Release Process
---------------

Version Management
~~~~~~~~~~~~~~~~~~

The project uses semantic versioning (MAJOR.MINOR.PATCH):

* **MAJOR**: Breaking changes
* **MINOR**: New features (backward compatible)
* **PATCH**: Bug fixes (backward compatible)

Release Workflow
~~~~~~~~~~~~~~~~

The project uses an automated release process via ``justfile`` recipes that handle all aspects of releasing.

**Step 1: Pre-Release Validation**

Before creating a release, validate your intended version:

.. code-block:: bash

   # Check if version is valid and ready for release
   just release-check 0.2.3

   # Check current project status
   just release-status

**Step 2: Automated Release**

Create a complete release with safety checks:

.. code-block:: bash

   # Full automated release process
   just release 0.2.3

This command will:

1. **Pre-flight checks**: Verify you're on main branch, working directory is clean, and up-to-date with remote
2. **Quality checks**: Run all linting, formatting, type checking, and tests
3. **Version bump**: Update ``pyproject.toml`` and ``uv.lock``
4. **Commit and push**: Create version bump commit and push to main
5. **Tag creation**: Create and push the release tag
6. **Trigger automation**: GitHub Actions automatically builds and publishes to PyPI

**Step 3: Monitor Release**

The release process provides helpful links:

.. code-block:: text

   ✅ Release 0.2.3 created and published!
   🔗 Monitor release progress: https://github.com/ryancheley/yt-cli/actions
   📦 Package will be available at: https://pypi.org/project/youtrack-cli/0.2.3/

Emergency Rollback
~~~~~~~~~~~~~~~~~~

If a release needs to be rolled back (before PyPI publication):

.. code-block:: bash

   # Emergency rollback - deletes tag and reverts version commit
   just rollback-release 0.2.3

.. warning::
   Rollback is only effective before the package is published to PyPI. Once published, you must create a new version.

Release Safety Features
~~~~~~~~~~~~~~~~~~~~~~~

The release process includes multiple safety checks:

**Branch Protection**:
  * Must be on ``main`` branch
  * Working directory must be clean
  * Must be up-to-date with ``origin/main``

**Version Validation**:
  * Semantic versioning format (e.g., ``1.2.3``)
  * Version must not already exist as a tag
  * Must be a proper version increment

**Quality Gates**:
  * All tests must pass
  * Code must pass linting
  * Type checking must succeed
  * No security issues detected

Manual Release Steps (Advanced)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For advanced users who need manual control:

.. code-block:: bash

   # Individual steps
   just version-bump 0.2.3    # Update pyproject.toml only
   just tag 0.2.3             # Create and push tag only

   # Quality checks
   just check                  # Run all quality checks

Release Troubleshooting
~~~~~~~~~~~~~~~~~~~~~~~

**Common Issues and Solutions**:

*Working directory not clean*:
  .. code-block:: bash

     # Check what files are uncommitted
     git status

     # Commit or stash changes
     git add . && git commit -m "commit message"
     # or
     git stash

*Not up-to-date with remote*:
  .. code-block:: bash

     git pull origin main

*Quality checks failing*:
  .. code-block:: bash

     # Run individual checks to identify issues
     just lint           # Fix linting issues
     just format         # Fix formatting
     just typecheck      # Fix type issues
     just test          # Fix failing tests

*Tag already exists*:
  .. code-block:: bash

     # List existing tags
     git tag -l

     # Use the next appropriate version number

GitHub Actions Integration
~~~~~~~~~~~~~~~~~~~~~~~~~~

The release process automatically triggers GitHub Actions workflows:

1. **Test PyPI Deployment**: Validates package and publishes to Test PyPI
2. **PyPI Deployment**: After Test PyPI succeeds, publishes to main PyPI
3. **GitHub Release**: Creates GitHub release with assets and attestations
4. **Security Attestations**: Generates digital attestations for packages

Contributing Guidelines
-----------------------

Pull Request Process
~~~~~~~~~~~~~~~~~~~~

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Update documentation
5. Ensure all quality checks pass
6. Submit a pull request

Code Style
~~~~~~~~~~

* Follow PEP 8
* Use type hints for all function signatures
* Write descriptive commit messages
* Keep functions focused and small
* Add docstrings to public interfaces

Getting Help
~~~~~~~~~~~~

* Open an issue for bugs or feature requests
* Join discussions in GitHub Discussions
* Check existing issues before creating new ones
* Provide minimal reproducible examples for bugs
