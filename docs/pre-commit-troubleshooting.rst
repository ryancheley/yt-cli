Pre-commit Troubleshooting Guide
=================================

This guide helps you diagnose and fix common pre-commit hook failures in the YouTrack CLI project.

.. contents::
   :local:
   :depth: 2

Quick Diagnosis
---------------

If you're experiencing pre-commit failures, start with our diagnostic tool:

.. code-block:: bash

   # Run the pre-commit doctor to diagnose issues
   ./scripts/pre-commit-doctor.sh

For quick fixes of common issues:

.. code-block:: bash

   # Auto-fix most common formatting and linting issues
   ./scripts/pre-commit-quick-fix.sh

For faster feedback during development:

.. code-block:: bash

   # Run checks only on staged files
   ./scripts/pre-commit-fast.sh

Top 10 Pre-commit Failure Categories
------------------------------------

1. Code Formatting Issues (Most Common)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Symptoms:**
- ``ruff-format`` hook fails
- "would reformat" messages
- Line length violations
- Inconsistent indentation

**Quick Fix:**

.. code-block:: bash

   # Auto-format all code
   uv run ruff format .

   # Check formatting without changes
   uv run ruff format --check .

**Prevention:**
- Set up your editor to format on save
- Use the ``ruff-format`` pre-commit hook
- Configure your editor to show the 120-character line limit

2. Linting and Code Quality Issues
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Symptoms:**
- ``ruff`` hook fails with style violations
- Unused imports or variables
- Undefined variables
- Import sorting issues

**Quick Fix:**

.. code-block:: bash

   # Auto-fix linting issues
   uv run ruff check --fix .

   # Check without fixing
   uv run ruff check .

**Common Issues:**

.. code-block:: bash

   # Fix import sorting specifically
   uv run ruff check --select I --fix .

   # Remove unused imports
   uv run ruff check --select F401 --fix .

**Prevention:**
- Use type hints consistently
- Remove unused imports and variables
- Follow PEP 8 naming conventions

3. Type Checking Failures
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Symptoms:**
- ``ty`` hook fails
- Missing type annotations
- Type compatibility issues
- Unresolved attributes

**Quick Fix:**

.. code-block:: bash

   # Run type checking
   uv run ty check --project youtrack_cli

   # Get more detailed output
   uv run ty check --project youtrack_cli --verbose

**Common Solutions:**
- Add missing type annotations
- Import types from ``typing`` module
- Use ``# type: ignore`` for complex cases (sparingly)
- Check if external library types are available

**Example Fixes:**

.. code-block:: python

   # Before: Missing type annotations
   def process_data(data):
       return data.upper()

   # After: With type annotations
   def process_data(data: str) -> str:
       return data.upper()

4. Testing Requirement Failures
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Symptoms:**
- ``pytest`` hook fails
- Test failures
- Coverage below threshold (80%)
- Import errors in tests

**Quick Fix:**

.. code-block:: bash

   # Run tests with coverage
   uv run pytest --cov=youtrack_cli --cov-fail-under=80

   # Run only failing tests
   uv run pytest --lf

   # Run tests in parallel for speed
   uv run pytest -n auto

**Common Issues:**

.. code-block:: bash

   # Check coverage report
   uv run pytest --cov=youtrack_cli --cov-report=html
   # Open htmlcov/index.html to see detailed coverage

   # Run specific test file
   uv run pytest tests/test_specific.py -v

5. File Format and Structure Issues
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Symptoms:**
- ``check-yaml``, ``check-toml``, ``check-json`` hooks fail
- Missing newlines at end of files
- Invalid configuration syntax

**Quick Fix:**

.. code-block:: bash

   # Fix end-of-file issues
   find . -name "*.py" -exec sh -c 'if [ -s "$1" ] && [ "$(tail -c1 "$1")" != "" ]; then echo "" >> "$1"; fi' _ {} \;

   # Validate TOML files
   uv run python -c "import tomllib; tomllib.load(open('pyproject.toml', 'rb'))"

   # Validate YAML files
   uv run python -c "import yaml; yaml.safe_load(open('.pre-commit-config.yaml'))"

6. Security and Safety Checks
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Symptoms:**
- ``zizmor`` hook fails
- GitHub Actions security issues
- Hardcoded secrets detected

**Quick Fix:**

.. code-block:: bash

   # Run security checks
   uv run zizmor .github/workflows/

   # Check for secrets in code
   grep -r "password\|secret\|token" youtrack_cli/ --include="*.py"

**Prevention:**
- Use environment variables for secrets
- Review GitHub Actions for security issues
- Use trusted, pinned action versions

7. Documentation and Docstring Issues
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Symptoms:**
- ``pydocstyle`` hook fails
- Missing or malformed docstrings
- Documentation build failures

**Quick Fix:**

.. code-block:: bash

   # Check docstring style
   uv run pydocstyle youtrack_cli/

   # Build documentation to test
   cd docs && uv run make html

**Common Fixes:**

.. code-block:: python

   # Google-style docstring example
   def create_issue(title: str, description: str) -> Issue:
       """Create a new YouTrack issue.

       Args:
           title: The issue title.
           description: The issue description.

       Returns:
           The created issue object.

       Raises:
           YouTrackError: If issue creation fails.
       """
       pass

8. Dependency and Configuration Issues
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Symptoms:**
- Import errors during hooks
- Missing development dependencies
- Version compatibility issues

**Quick Fix:**

.. code-block:: bash

   # Reinstall all dependencies
   uv sync --dev

   # Check for dependency conflicts
   uv pip check

   # Update lock file
   uv lock --upgrade

9. Git Hook Configuration Problems
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Symptoms:**
- Hooks not running
- Permission errors
- Hook installation failures

**Quick Fix:**

.. code-block:: bash

   # Reinstall pre-commit hooks
   uv run pre-commit uninstall
   uv run pre-commit install

   # Update hook versions
   uv run pre-commit autoupdate

   # Clean hook cache
   uv run pre-commit clean

10. Build and Integration Issues
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Symptoms:**
- Package build failures
- CI/CD mismatches with local checks
- Platform-specific issues

**Quick Fix:**

.. code-block:: bash

   # Test package build
   uv build

   # Check package metadata
   uv run twine check dist/*

   # Run all checks as CI would
   uv run pre-commit run --all-files

Advanced Troubleshooting
------------------------

Debugging Hook Execution
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Run hooks in verbose mode
   uv run pre-commit run --verbose

   # Run specific hook only
   uv run pre-commit run ruff

   # Skip specific hooks
   SKIP=pytest uv run pre-commit run

Performance Issues
~~~~~~~~~~~~~~~~~~

If pre-commit is too slow:

.. code-block:: bash

   # Run on staged files only
   ./scripts/pre-commit-fast.sh

   # Parallel execution (if supported)
   uv run pre-commit run --parallel

   # Skip slow hooks during development
   SKIP=pytest,docs-build-check git commit -m "WIP: quick commit"

Environment Issues
~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Check environment
   ./scripts/pre-commit-doctor.sh

   # Reset virtual environment
   rm -rf .venv
   uv sync --dev

   # Check tool versions
   uv run ruff --version
   uv run pytest --version
   uv run ty --version

Bypassing Hooks (Emergency Only)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**⚠️ Warning:** Only use these in emergencies. Fix issues properly instead.

.. code-block:: bash

   # Skip all hooks (NOT RECOMMENDED)
   git commit --no-verify -m "Emergency commit"

   # Skip specific hooks
   SKIP=pytest git commit -m "Skip tests temporarily"

Common Error Messages and Solutions
-----------------------------------

"ruff would reformat"
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Solution: Let ruff format the code
   uv run ruff format .
   git add .

"ty found type errors"
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # See specific errors
   uv run ty check --project youtrack_cli

   # Add type annotations or ignores as needed

"pytest coverage below 80%"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # See coverage report
   uv run pytest --cov=youtrack_cli --cov-report=term-missing

   # Write tests for uncovered code or adjust threshold

"trailing whitespace found"
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Auto-fix
   find . -name "*.py" -exec sed -i '' 's/[[:space:]]*$//' {} \;

"large files detected"
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Check file sizes
   find . -type f -size +1M -not -path "./.git/*"

   # Use Git LFS for large files or remove them

Best Practices
--------------

Development Workflow
~~~~~~~~~~~~~~~~~~~~

1. **Before making changes:**

   .. code-block:: bash

      # Check current state
      ./scripts/pre-commit-doctor.sh

2. **During development:**

   .. code-block:: bash

      # Quick check on changes
      ./scripts/pre-commit-fast.sh

3. **Before committing:**

   .. code-block:: bash

      # Full pre-commit run
      uv run pre-commit run --all-files

4. **If hooks fail:**

   .. code-block:: bash

      # Try auto-fixes first
      ./scripts/pre-commit-quick-fix.sh

      # Then fix remaining issues manually

Editor Setup
~~~~~~~~~~~~

Configure your editor for better pre-commit success:

**VS Code:**

.. code-block:: json

   {
     "python.formatting.provider": "none",
     "python.linting.enabled": true,
     "python.linting.ruffEnabled": true,
     "[python]": {
       "editor.formatOnSave": true,
       "editor.codeActionsOnSave": {
         "source.fixAll": true,
         "source.organizeImports": true
       }
     },
     "editor.rulers": [120]
   }

**PyCharm/IntelliJ:**

- Install the Ruff plugin
- Set line length to 120 characters
- Enable format on save
- Configure type checking with ty

Continuous Integration Alignment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Ensure your local pre-commit matches CI:

.. code-block:: bash

   # Update pre-commit hooks to latest versions
   uv run pre-commit autoupdate

   # Test against multiple Python versions locally
   uv run tox

Getting Help
------------

If you're still having issues:

1. Run the diagnostic tool: ``./scripts/pre-commit-doctor.sh``
2. Check the `troubleshooting documentation <troubleshooting.rst>`_
3. Review recent commits to see working examples
4. Ask for help in GitHub issues or discussions

Remember: Pre-commit hooks are there to help maintain code quality. Taking time to fix issues properly will benefit the entire project and team.
