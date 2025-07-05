Troubleshooting
===============

This guide helps you resolve common issues when using YouTrack CLI.

.. contents:: Table of Contents
   :local:
   :depth: 2

Installation Issues
-------------------

Command Not Found
~~~~~~~~~~~~~~~~~~

**Problem**: ``yt: command not found`` after installation.

**Solutions**:

1. **Check if installation was successful**:

   .. code-block:: bash

      pip list | grep youtrack-cli

2. **Verify PATH configuration**:

   .. code-block:: bash

      # Check where pip installed the package
      pip show -f youtrack-cli

      # Add to PATH if needed (add to ~/.bashrc or ~/.zshrc)
      export PATH="$HOME/.local/bin:$PATH"

3. **Use full path temporarily**:

   .. code-block:: bash

      python -m youtrack_cli --help

Python Version Issues
~~~~~~~~~~~~~~~~~~~~~

**Problem**: Installation fails with Python version errors.

**Solution**: YouTrack CLI requires Python 3.9 or higher.

.. code-block:: bash

   # Check Python version
   python --version

   # If using multiple Python versions
   python3.9 -m pip install youtrack-cli
   python3.9 -m youtrack_cli --help

Virtual Environment Issues
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Problem**: Package not found after installing in virtual environment.

**Solution**:

.. code-block:: bash

   # Activate virtual environment first
   source venv/bin/activate  # Linux/macOS
   # or
   venv\Scripts\activate     # Windows

   # Then install
   pip install youtrack-cli

   # Verify installation
   yt --help

Permission Issues
~~~~~~~~~~~~~~~~~

**Problem**: Permission denied during installation.

**Solutions**:

1. **Install for current user only**:

   .. code-block:: bash

      pip install --user youtrack-cli

2. **Use virtual environment** (recommended):

   .. code-block:: bash

      python -m venv youtrack-env
      source youtrack-env/bin/activate  # Linux/macOS
      pip install youtrack-cli

3. **Use uv** (fastest and recommended):

   .. code-block:: bash

      # Install uv first (if not already installed)
      curl -LsSf https://astral.sh/uv/install.sh | sh

      # Install YouTrack CLI using uv
      uv tool install youtrack-cli

      # Or for development
      git clone https://github.com/ryancheley/yt-cli.git
      cd yt-cli
      uv sync --dev
      uv pip install -e .

Dependency Issues
~~~~~~~~~~~~~~~~~

**Problem**: CLI fails to run due to missing dependencies (e.g., ``ModuleNotFoundError: No module named 'click'``).

**Solutions**:

1. **Verify complete installation**:

   .. code-block:: bash

      # Check if all dependencies are installed
      pip list | grep -E "(click|rich|textual|pydantic|httpx)"

2. **Reinstall with all dependencies**:

   .. code-block:: bash

      pip uninstall youtrack-cli
      pip install --upgrade youtrack-cli

3. **Use uv for reliable dependency management**:

   .. code-block:: bash

      uv tool install youtrack-cli --force

4. **Development installation**:

   .. code-block:: bash

      git clone https://github.com/ryancheley/yt-cli.git
      cd yt-cli
      uv sync --dev
      uv pip install -e .
      yt --version  # Should work without errors

Authentication Issues
---------------------

Login Failed
~~~~~~~~~~~~

**Problem**: ``yt auth login`` fails with authentication error.

**Common Causes & Solutions**:

1. **Wrong YouTrack URL**:

   .. code-block:: bash

      # Ensure URL includes protocol and correct domain
      # ✅ Correct:
      https://yourcompany.youtrack.cloud

      # ❌ Wrong:
      yourcompany.youtrack.cloud
      www.yourcompany.youtrack.cloud

2. **Invalid credentials**:

   - Check username/password in YouTrack web interface
   - Try logging in via browser first
   - Reset password if necessary

3. **Network connectivity**:

   .. code-block:: bash

      # Test connection
      curl https://yourcompany.youtrack.cloud/api/admin/projects

      # Check proxy settings if behind corporate firewall

API Token Issues
~~~~~~~~~~~~~~~~

**Problem**: API token authentication fails.

**Solutions**:

1. **Generate new token**:

   - Go to YouTrack → Profile → Account Security → API Tokens
   - Create new token with appropriate permissions
   - Copy the full token value

2. **Verify token format**:

   .. code-block:: bash

      # Tokens should start with 'perm:'
      # ✅ Correct format:
      perm:cm9vdC5yb290.UGVybWlzc2lvbnM=.1234567890abcdef

      # ❌ Wrong: Missing 'perm:' prefix

3. **Test token manually**:

   .. code-block:: bash

      curl -H "Authorization: Bearer perm:your-token-here" \
           https://yourcompany.youtrack.cloud/api/admin/projects

Configuration File Issues
~~~~~~~~~~~~~~~~~~~~~~~~~

**Problem**: Configuration not found or invalid.

**Solutions**:

1. **Check configuration file location**:

   .. code-block:: bash

      yt config list --show-file

2. **Verify file permissions**:

   .. code-block:: bash

      # Configuration should be readable
      ls -la ~/.config/youtrack-cli/.env
      chmod 600 ~/.config/youtrack-cli/.env

3. **Validate configuration format**:

   .. code-block:: bash

      # .env file format (NOT YAML):
      YOUTRACK_BASE_URL=https://yourcompany.youtrack.cloud
      YOUTRACK_TOKEN=perm:your-token-here
      YOUTRACK_USERNAME=your-username

SSL Certificate Issues
~~~~~~~~~~~~~~~~~~~~~~

**Problem**: SSL certificate verification fails.

**Solutions**:

1. **Update certificates**:

   .. code-block:: bash

      # Linux
      sudo apt-get update && sudo apt-get install ca-certificates

      # macOS
      brew install ca-certificates

2. **Temporary workaround** (not recommended for production):

   .. code-block:: bash

      export PYTHONHTTPSVERIFY=0
      yt --help

Command Execution Issues
------------------------

Permission Denied
~~~~~~~~~~~~~~~~~

**Problem**: ``Permission denied`` when running yt commands.

**Solutions**:

1. **Check YouTrack permissions**:

   - Verify your user has appropriate permissions in YouTrack
   - Contact YouTrack admin to check user roles

2. **Token permissions**:

   - Recreate API token with correct permissions
   - Ensure token has project access rights

Invalid Project or Issue ID
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Problem**: ``Project not found`` or ``Issue not found`` errors.

**Solutions**:

1. **Verify project exists**:

   .. code-block:: bash

      yt projects list

2. **Check project key format**:

   .. code-block:: bash

      # ✅ Correct format:
      yt issues create WEB-FRONTEND "Issue title"

      # ❌ Wrong format:
      yt issues create "Web Frontend" "Issue title"

3. **Verify issue ID format**:

   .. code-block:: bash

      # ✅ Correct:
      yt issues update WEB-123 --state "In Progress"

      # ❌ Wrong:
      yt issues update 123 --state "In Progress"

Network and Connectivity Issues
-------------------------------

Connection Timeout
~~~~~~~~~~~~~~~~~~

**Problem**: Commands hang or timeout.

**Solutions**:

1. **Check network connectivity**:

   .. code-block:: bash

      ping yourcompany.youtrack.cloud

2. **Test YouTrack API directly**:

   .. code-block:: bash

      curl -I https://yourcompany.youtrack.cloud/api/admin/projects

3. **Corporate proxy configuration**:

   .. code-block:: bash

      # Set proxy environment variables
      export HTTP_PROXY=http://proxy.company.com:8080
      export HTTPS_PROXY=http://proxy.company.com:8080
      export NO_PROXY=localhost,127.0.0.1,.company.com

Rate Limiting
~~~~~~~~~~~~~

**Problem**: ``Too many requests`` errors.

**Solutions**:

1. **Add delays between commands**:

   .. code-block:: bash

      # Use in scripts
      yt issues list --limit 10
      sleep 1
      yt issues list --limit 10 --offset 10

2. **Reduce request frequency**:

   - Use ``--limit`` options to fetch smaller batches
   - Implement exponential backoff in scripts

Data and Output Issues
----------------------

Empty Results
~~~~~~~~~~~~~

**Problem**: Commands return no results when data should exist.

**Solutions**:

1. **Check user permissions**:

   .. code-block:: bash

      # You might not have access to see certain projects/issues
      yt projects list  # See what projects you can access

2. **Verify search parameters**:

   .. code-block:: bash

      # Start with broader searches
      yt issues list --limit 5
      yt issues search "created: today"

3. **Check project context**:

   .. code-block:: bash

      # Specify project explicitly
      yt issues list --project PROJECT-KEY

Output Formatting Issues
~~~~~~~~~~~~~~~~~~~~~~~~

**Problem**: Garbled or poorly formatted output.

**Solutions**:

1. **Check terminal encoding**:

   .. code-block:: bash

      export LANG=en_US.UTF-8
      export LC_ALL=en_US.UTF-8

2. **Try different output formats**:

   .. code-block:: bash

      yt issues list --format json
      yt issues list --format table

3. **Disable colors if needed**:

   .. code-block:: bash

      yt issues list --no-color

Command-Specific Issues
-----------------------

Issue Creation Fails
~~~~~~~~~~~~~~~~~~~~~

**Problem**: ``yt issues create`` fails with validation errors.

**Common Issues**:

1. **Missing required fields**:

   .. code-block:: bash

      # ✅ Include all required fields:
      yt issues create PROJECT-KEY "Issue summary" \
        --description "Detailed description" \
        --type "Bug"

2. **Invalid field values**:

   .. code-block:: bash

      # Check valid values first:
      yt projects list  # For project keys
      yt issues list --limit 1  # To see valid field examples

3. **Special characters in summary**:

   .. code-block:: bash

      # Quote strings with special characters:
      yt issues create PROJECT-KEY "Fix: API returns 500 error"

Time Tracking Issues
~~~~~~~~~~~~~~~~~~~~

**Problem**: Time logging fails or shows unexpected format.

**Solutions**:

1. **Use correct time format**:

   .. code-block:: bash

      # ✅ Correct formats:
      yt time log ISSUE-123 "2h 30m"
      yt time log ISSUE-123 "4h"
      yt time log ISSUE-123 "90m"

      # ❌ Wrong formats:
      yt time log ISSUE-123 "2.5h"
      yt time log ISSUE-123 "2:30"

2. **Check permissions**:

   - Verify you can edit the issue
   - Ensure time tracking is enabled for the project

Getting Help
------------

Debugging and Logging
~~~~~~~~~~~~~~~~~~~~~

YouTrack CLI includes a comprehensive logging system built with structured logging to help troubleshoot issues.

**Quick Debugging**

For immediate troubleshooting, use these flags:

.. code-block:: bash

   # Debug mode shows detailed HTTP requests, responses, and internal operations
   yt --debug issues list
   yt --debug auth login

   # Verbose mode shows progress information and warnings
   yt --verbose projects list
   yt --verbose issues create PROJECT-KEY "New issue"

   # Set specific log levels
   yt --log-level ERROR issues list
   yt --log-level DEBUG auth login

**Comprehensive Logging Documentation**

For detailed information about the logging system, including:

- Advanced log level control
- File-based logging with rotation
- Sensitive data masking
- API call tracking
- Performance monitoring
- Log aggregation for external tools

See the complete :doc:`logging` guide.

**Enhanced Error Messages**

YouTrack CLI provides user-friendly error messages with actionable suggestions:

.. code-block:: bash

   # Example error with suggestion
   $ yt issues list --project INVALID-PROJECT
   Error: Project 'INVALID-PROJECT' not found
   Suggestion: Check if the project exists and you have access to it

**Error Categories**

The CLI categorizes errors to provide better context:

- **AuthenticationError**: Login or token issues
- **ConnectionError**: Network or server connectivity problems
- **NotFoundError**: Missing resources (projects, issues, etc.)
- **PermissionError**: Access rights issues
- **ValidationError**: Invalid input or parameters
- **RateLimitError**: Too many requests (includes retry suggestions)

**Automatic Retry Logic**

Network requests include automatic retry with exponential backoff:

.. code-block:: bash

   # The CLI automatically retries failed requests up to 3 times
   # You'll see warnings like:
   # "Request timed out, retrying in 2s..."
   # "Connection failed, retrying in 4s..."

Log Files
~~~~~~~~~

Check log files for detailed error information:

.. code-block:: bash

   # Default log location (varies by OS)
   # Linux/macOS:
   tail -f ~/.local/share/youtrack-cli/logs/youtrack-cli.log

   # Windows:
   type %APPDATA%\youtrack-cli\logs\youtrack-cli.log

Command Help
~~~~~~~~~~~~

Every command has built-in help:

.. code-block:: bash

   # General help
   yt --help

   # Command group help
   yt issues --help
   yt projects --help

   # Specific command help
   yt issues create --help
   yt time log --help

Testing Configuration
~~~~~~~~~~~~~~~~~~~~~

Verify your setup is working:

.. code-block:: bash

   # Test authentication
   yt auth login --test

   # Test basic operations
   yt projects list --limit 1
   yt issues list --limit 1

Common Error Messages
---------------------

"Module not found"
~~~~~~~~~~~~~~~~~~

**Error**: ``ModuleNotFoundError: No module named 'youtrack_cli'``

**Solution**: Reinstall the package:

.. code-block:: bash

   pip uninstall youtrack-cli
   pip install youtrack-cli

"Invalid token format"
~~~~~~~~~~~~~~~~~~~~~~

**Error**: ``AuthenticationError: Invalid token format``

**Solution**: Ensure token includes ``perm:`` prefix:

.. code-block:: bash

   # Correct format
   YOUTRACK_TOKEN=perm:cm9vdC5yb290.UGVybWlzc2lvbnM=.1234567890abcdef

"Connection refused"
~~~~~~~~~~~~~~~~~~~~

**Error**: ``ConnectionError: Connection refused``

**Solutions**:

1. Check YouTrack URL is correct and accessible
2. Verify network connectivity
3. Check if YouTrack service is running

"Project not found"
~~~~~~~~~~~~~~~~~~~

**Error**: ``NotFoundError: Project 'PROJECT-KEY' not found``

**Solutions**:

1. List available projects: ``yt projects list``
2. Check project key spelling and case
3. Verify you have access to the project

"Unauthorized"
~~~~~~~~~~~~~~

**Error**: ``AuthenticationError: 401 Unauthorized``

**Solutions**:

1. Verify credentials are correct
2. Check API token permissions
3. Test login in YouTrack web interface

Release and Development Issues
-------------------------------

Release Creation Problems
~~~~~~~~~~~~~~~~~~~~~~~~~

**Problem**: ``just release`` command fails during pre-flight checks.

**Common Issues and Solutions**:

*Not on main branch*:
  .. code-block:: bash

     # Check current branch
     git branch --show-current

     # Switch to main
     git checkout main

*Working directory not clean*:
  .. code-block:: bash

     # Check what files are uncommitted
     git status --short

     # Commit changes or stash them
     git add . && git commit -m "Pre-release cleanup"
     # or
     git stash

*Local branch not up-to-date*:
  .. code-block:: bash

     # Pull latest changes
     git pull origin main

*Quality checks failing*:
  .. code-block:: bash

     # Run checks individually to identify issues
     just lint          # Fix linting issues
     just format        # Fix formatting
     just typecheck     # Fix type issues
     just test         # Fix failing tests
     just security     # Fix security issues

**Problem**: Version validation fails.

**Solutions**:

*Invalid version format*:
  .. code-block:: bash

     # ✅ Correct semantic versioning:
     just release 0.2.3
     just release 1.0.0

     # ❌ Wrong formats:
     just release 0.2    # Missing patch version
     just release v0.2.3 # Don't include 'v' prefix
     just release 0.2.3-beta # Pre-release versions not supported

*Version already exists*:
  .. code-block:: bash

     # Check existing tags
     git tag -l | sort -V

     # Use next appropriate version
     just release 0.2.4

*Not a proper version increment*:
  .. code-block:: bash

     # Check current version
     just release-status

     # Use proper increment (patch, minor, or major)
     just release-check 0.2.3  # Validate before running

GitHub Actions Failures
~~~~~~~~~~~~~~~~~~~~~~~~

**Problem**: Release workflow fails after tag is pushed.

**Diagnostic Steps**:

1. **Check workflow status**:

   .. code-block:: bash

      # View recent workflow runs
      gh run list --limit 5

      # View specific run details
      gh run view <run-id>

      # View failed job logs
      gh run view <run-id> --log-failed

2. **Common failure causes**:

   *Tests failing in CI*:
     - Tests may pass locally but fail in CI due to environment differences
     - Check the test logs in GitHub Actions
     - Run tests locally with exact CI conditions

   *Build failures*:
     - Missing dependencies in CI environment
     - Check ``pyproject.toml`` for correct dependency versions

   *PyPI publishing failures*:
     - API token permissions or expiration
     - Package name conflicts
     - Missing repository secrets (``PYPI_TOKEN``)

**Problem**: Package published to Test PyPI but not main PyPI.

**Solutions**:

1. **Check Test PyPI results**:

   .. code-block:: bash

      # View Test PyPI package
      # https://test.pypi.org/project/youtrack-cli/

2. **Manual PyPI troubleshooting**:

   .. code-block:: bash

      # Check if package exists on main PyPI
      pip index versions youtrack-cli

      # Test installation from Test PyPI
      pip install -i https://test.pypi.org/simple/ youtrack-cli

Release Rollback Issues
~~~~~~~~~~~~~~~~~~~~~~~

**Problem**: Need to rollback a failed release.

**Solutions**:

1. **Before PyPI publication** (tag exists but package not published):

   .. code-block:: bash

      # Use automated rollback
      just rollback-release 0.2.3

2. **After PyPI publication** (package already live):

   .. code-block:: bash

      # PyPI doesn't allow deletion - create new version
      just release-check 0.2.4  # Validate next version
      just release 0.2.4        # Create hotfix release

3. **Manual rollback steps** (if automated rollback fails):

   .. code-block:: bash

      # Delete remote tag
      git push origin :refs/tags/v0.2.3

      # Delete local tag
      git tag -d v0.2.3

      # Revert version commit (if it's the last commit)
      git reset --hard HEAD~1
      git push --force-with-lease origin main

Development Environment Issues
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Problem**: ``just`` command not found.

**Solutions**:

1. **Install just**:

   .. code-block:: bash

      # macOS
      brew install just

      # Linux
      curl --proto '=https' --tlsv1.2 -sSf https://just.systems/install.sh | bash -s -- --to ~/bin

      # Windows (using cargo)
      cargo install just

2. **Alternative - use make**:

   .. code-block:: bash

      # Manual commands instead of just recipes
      uv sync --dev
      uv run pytest
      uv run ruff check

**Problem**: Pre-commit hooks failing.

**Solutions**:

1. **Install pre-commit hooks**:

   .. code-block:: bash

      uv run pre-commit install

2. **Run hooks manually**:

   .. code-block:: bash

      # Run all hooks
      uv run pre-commit run --all-files

      # Run specific hook
      uv run pre-commit run ruff

3. **Skip hooks temporarily** (not recommended):

   .. code-block:: bash

      git commit --no-verify -m "message"

**Problem**: Type checking failures with ``ty``.

**Solutions**:

1. **Install correct type checker**:

   .. code-block:: bash

      # Project uses 'ty', not 'mypy'
      uv sync --dev
      uv run ty check

2. **Common type issues**:

   .. code-block:: bash

      # Ignore specific issues during development
      uv run ty check --ignore call-non-callable --ignore unresolved-attribute

Version Management Issues
~~~~~~~~~~~~~~~~~~~~~~~~~

**Problem**: Version mismatch between files.

**Solutions**:

1. **Check version consistency**:

   .. code-block:: bash

      # Check pyproject.toml version
      grep '^version =' pyproject.toml

      # Check package version
      python -c "import youtrack_cli; print(youtrack_cli.__version__)"

2. **Fix version inconsistencies**:

   .. code-block:: bash

      # Use justfile version bump
      just version-bump 0.2.3

      # This updates pyproject.toml correctly

**Problem**: uv.lock file out of sync.

**Solutions**:

.. code-block:: bash

   # Update lock file
   uv sync

   # Or regenerate completely
   rm uv.lock
   uv sync --dev

CI/CD Integration Issues
~~~~~~~~~~~~~~~~~~~~~~~

**Problem**: GitHub Actions workflow not triggering.

**Solutions**:

1. **Check workflow triggers**:

   .. code-block:: bash

      # Ensure tag was pushed correctly
      git ls-remote --tags origin

      # Check if tag follows correct format
      git tag -l | grep "^v[0-9]"

2. **Verify workflow files**:

   .. code-block:: bash

      # Check workflow syntax
      cat .github/workflows/release.yml

      # Test with GitHub CLI
      gh workflow list

**Problem**: Secrets not available in workflow.

**Solutions**:

1. **Check repository secrets**:

   - Go to GitHub repo → Settings → Secrets and variables → Actions
   - Ensure ``PYPI_TOKEN`` exists and is valid
   - Verify environment protection rules

2. **Test secrets locally** (for debugging):

   .. code-block:: bash

      # Test PyPI token manually
      twine check dist/*
      twine upload --repository testpypi dist/*

Still Need Help?
----------------

If this guide doesn't resolve your issue:

1. **Check existing issues**: `GitHub Issues <https://github.com/ryancheley/yt-cli/issues>`_
2. **Create new issue**: Include error messages, command used, and system info
3. **Join discussions**: `GitHub Discussions <https://github.com/ryancheley/yt-cli/discussions>`_

When reporting issues, include:

.. code-block:: bash

   # System information
   yt --version
   python --version
   pip list | grep youtrack-cli

   # Development environment info (if relevant)
   just --version
   uv --version
   git --version

   # Error output with debug flag
   yt --debug [your-command-here]

   # Release-specific debugging
   just release-status
   git status
   git log --oneline -5
