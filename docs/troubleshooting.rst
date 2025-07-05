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

YouTrack CLI includes enhanced logging and debugging capabilities to help troubleshoot issues:

**Debug Mode**

Enable detailed debug output to see what's happening under the hood:

.. code-block:: bash

   # Debug mode shows detailed HTTP requests, responses, and internal operations
   yt --debug issues list
   yt --debug auth login

**Verbose Mode**

Enable verbose output for more information without full debug details:

.. code-block:: bash

   # Verbose mode shows progress information and warnings
   yt --verbose projects list
   yt --verbose issues create PROJECT-KEY "New issue"

**Enhanced Error Messages**

YouTrack CLI now provides user-friendly error messages with actionable suggestions:

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

Network requests now include automatic retry with exponential backoff:

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

   # Error output with debug flag
   yt --debug [your-command-here]
