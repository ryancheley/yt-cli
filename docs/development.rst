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

Tests are organized into two main categories with proper pytest markers:

* **Unit tests** (``@pytest.mark.unit``): Fast, isolated tests of individual functions and classes with no external dependencies
* **Integration tests** (``@pytest.mark.integration``): End-to-end tests that require real YouTrack API access

Integration Test Categories
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The integration tests are further organized by functionality:

* **Authentication Tests** (``test_auth_integration.py``): Complete authentication workflows including login, logout, session management, and error recovery
* **User Management Tests** (``test_users_integration.py``): User creation, updates, permissions management, and lifecycle workflows
* **Issue Management Tests** (``test_issues_integration.py``): Basic issue CRUD operations, state transitions, and field management
* **Issue Workflow Tests** (``test_issues_workflows.py``): Multi-step issue workflows including collaboration, batch operations, and cross-issue relationships
* **Project Management Tests** (``test_projects_integration.py``): Basic project operations and custom field management
* **Project End-to-End Tests** (``test_projects_e2e.py``): Complex project operations including lifecycle management, templates, and bulk operations
* **Time Tracking Tests** (``test_time_tracking_integration.py``): Complete time tracking workflows including logging, reporting, and analysis

Test Organization:

.. code-block:: text

   tests/
   ├── conftest.py                      # Global test fixtures
   ├── test_*.py                        # Unit tests (marked with @pytest.mark.unit)
   └── integration/                     # Integration tests directory
       ├── conftest.py                  # Integration-specific fixtures
       ├── test_auth_integration.py     # Authentication integration tests
       ├── test_issues_integration.py   # Issue management integration tests
       ├── test_projects_integration.py # Project management integration tests
       ├── test_users_integration.py    # User management workflow tests
       ├── test_projects_e2e.py         # Complex project operations end-to-end tests
       ├── test_issues_workflows.py     # Multi-step issue workflow tests
       └── test_time_tracking_integration.py # Time tracking workflow tests

Running Tests
~~~~~~~~~~~~~

**Quick Test Runner (Recommended):**

Use the included test runner script for easy test execution:

.. code-block:: bash

   # Run only unit tests (fast)
   python test_runner.py unit

   # Run only integration tests
   python test_runner.py integration

   # Run all tests (unit + integration)
   python test_runner.py all

   # Run unit tests with coverage
   python test_runner.py unit --coverage

   # Run tests with verbose output
   python test_runner.py all --verbose

**Direct pytest Commands:**

.. code-block:: bash

   # Run all unit tests (no external dependencies)
   uv run pytest -m unit

   # Run all integration tests (requires YouTrack API access)
   uv run pytest -m integration

   # Run specific integration test categories
   uv run pytest tests/integration/test_auth_integration.py
   uv run pytest tests/integration/test_users_integration.py
   uv run pytest tests/integration/test_issues_workflows.py
   uv run pytest tests/integration/test_time_tracking_integration.py

   # Run all tests
   uv run pytest

   # Run with coverage (unit tests only)
   uv run pytest -m unit --cov=youtrack_cli --cov-report=html

**Integration Test Requirements:**

Integration tests require real YouTrack API access. Set these environment variables:

.. code-block:: bash

   # Required
   export YOUTRACK_BASE_URL="https://your-instance.youtrack.cloud"
   export YOUTRACK_API_KEY="your-api-token"

   # Optional
   export YOUTRACK_TEST_PROJECT="FPU"  # Default project for testing
   export YOUTRACK_USERNAME="your-username"  # For assignment tests

**Integration Test Coverage:**

The integration test suite provides comprehensive end-to-end coverage of YouTrack CLI functionality:

* **Enhanced Authentication Testing**: Login/logout workflows, session persistence, error recovery, and multi-instance support
* **User Management Workflows**: Complete user lifecycle testing from creation to deactivation, including permissions and group management
* **Complex Issue Workflows**: Multi-step operations including batch processing, collaboration workflows, and cross-issue relationships
* **Project Operations**: End-to-end project management including templates, custom fields, and cross-project operations
* **Time Tracking**: Comprehensive time logging, reporting, and analysis workflows with various duration formats and date handling

The test suite now includes over 40 integration test scenarios covering key user workflows that were previously limited to basic CRUD operations.

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

**Unit Test Guidelines:**

All unit tests should be marked with ``@pytest.mark.unit`` and should:

* Test individual functions/classes in isolation
* Use mocks for external dependencies
* Be fast and deterministic
* Not require network access or external services

Example unit test:

.. code-block:: python

   import pytest
   from unittest.mock import Mock, patch
   from youtrack_cli.issues import IssueManager

   @pytest.mark.unit
   class TestIssueManager:
       def test_parse_issue_id(self):
           project, number = IssueManager.parse_issue_id("PROJECT-123")
           assert project == "PROJECT"
           assert number == 123

       def test_parse_issue_id_invalid(self):
           with pytest.raises(ValueError):
               IssueManager.parse_issue_id("invalid-id")

       @patch('youtrack_cli.issues.YouTrackClient')
       def test_create_issue(self, mock_client):
           mock_client.return_value.create_issue.return_value = {"id": "PROJ-1"}
           manager = IssueManager(mock_client)
           result = manager.create_issue("PROJ", "Test", "Description")
           assert result["id"] == "PROJ-1"

**Integration Test Guidelines:**

All integration tests should be marked with ``@pytest.mark.integration`` and should:

* Test real API interactions with YouTrack
* Use the FPU project for testing by default
* Clean up any created test data
* Be resilient to varying YouTrack configurations

Example integration test:

.. code-block:: python

   import pytest

   @pytest.mark.integration
   class TestIssuesIntegration:
       def test_create_and_delete_issue_workflow(
           self,
           integration_issue_manager,
           test_issue_data,
           cleanup_test_issues
       ):
           """Test complete create and delete issue workflow."""
           # Create issue
           created_issue = integration_issue_manager.create_issue(
               project_id=test_issue_data["project"]["id"],
               summary=test_issue_data["summary"],
               description=test_issue_data["description"]
           )

           assert created_issue is not None
           issue_id = created_issue["id"]
           cleanup_test_issues(issue_id)  # Schedule cleanup

           # Verify issue was created
           retrieved_issue = integration_issue_manager.get_issue(issue_id)
           assert retrieved_issue["summary"] == test_issue_data["summary"]

**Test Data Management:**

Integration tests include automatic cleanup of test data:

* Use ``cleanup_test_issues`` fixture to track created issues
* Use ``integration_test_data`` fixture for unique test identifiers
* Test data is automatically cleaned up after each test

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

.. toctree::
   :maxdepth: 1

   pre-commit-troubleshooting

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

Documentation Builds
~~~~~~~~~~~~~~~~~~~~~

The project uses ReadTheDocs for automatic documentation building and hosting. The documentation builds are configured to trigger only when version tags are pushed, aligning with our release strategy.

**ReadTheDocs Configuration:**

The ``.readthedocs.yaml`` file in the project root configures the build environment and specifies that documentation should only be built for version releases, not on every commit to main.

**Manual ReadTheDocs Setup Required:**

To complete the setup for version-only builds, the following must be configured in the ReadTheDocs admin interface:

1. **Navigate to ReadTheDocs Admin**: Go to your project's admin page on ReadTheDocs
2. **Configure Automation Rules**: Under "Automation Rules", configure builds to trigger only on:

   - Version tags matching pattern ``v*`` (e.g., ``v1.0.0``, ``v2.1.3``)
   - Manual builds when needed

3. **Disable Branch Builds**: Ensure that automatic builds on ``main`` branch commits are disabled

**Verification:**

After configuring ReadTheDocs automation rules:

- Documentation builds should only occur when version tags are pushed via the release process
- No builds should trigger on regular commits to the main branch
- Documentation will be automatically updated when new versions are released to PyPI

This approach ensures that documentation stays synchronized with released versions while avoiding unnecessary builds on development commits.

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
