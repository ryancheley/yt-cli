Authentication Command Group
=============================

The ``yt auth`` command group provides comprehensive authentication management for YouTrack CLI. Handle login, logout, token management, and credential verification.

.. contents:: Table of Contents
   :local:
   :depth: 2

Overview
--------

YouTrack CLI authentication is based on API tokens and manages secure access to your YouTrack instance. The auth command group allows you to:

* Authenticate with YouTrack using API tokens
* Manage and update authentication credentials
* Verify and test authentication status
* Securely store and retrieve credentials
* Handle logout and credential cleanup

All commands in the CLI require proper authentication to access YouTrack resources.

Base Command
------------

.. code-block:: bash

   yt auth [OPTIONS] COMMAND [ARGS]...

Authentication Commands
-----------------------

login
~~~~~

Authenticate with YouTrack and save credentials for subsequent CLI usage.

.. code-block:: bash

   yt auth login [OPTIONS]

**Options:**

.. list-table::
   :widths: 20 20 60
   :header-rows: 1

   * - Option
     - Type
     - Description
   * - ``--base-url, -u``
     - string
     - YouTrack instance URL (will prompt if not provided)
   * - ``--token, -t``
     - string
     - YouTrack API token (will prompt securely if not provided)
   * - ``--username, -n``
     - string
     - Username for reference (optional)
   * - ``--no-verify-ssl``
     - flag
     - Disable SSL certificate verification (use with caution for self-signed certificates)

**Examples:**

.. code-block:: bash

   # Interactive login (prompts for URL and token)
   yt auth login

   # Login with pre-filled URL
   yt auth login --base-url https://yourdomain.youtrack.cloud

   # Login with URL and username
   yt auth login --base-url https://company.youtrack.cloud --username john.doe

   # Completely non-interactive (not recommended for security)
   yt auth login --base-url https://company.youtrack.cloud --token YOUR_API_TOKEN

   # Login with self-signed SSL certificate
   yt auth login --base-url https://internal.youtrack.local --no-verify-ssl

**Security Notes:**

* API tokens are prompted securely and hidden during input
* Sensitive credentials (tokens) are stored in system keyring with encryption
* Non-sensitive configuration (base URL, username, SSL preference) is stored in .env file
* Never include tokens in command history or scripts
* Use environment variables or secure prompts for automation

logout
~~~~~~

Clear stored authentication credentials and log out of YouTrack.

.. code-block:: bash

   yt auth logout

**Examples:**

.. code-block:: bash

   # Logout with confirmation prompt
   yt auth logout

   # The command will ask for confirmation before clearing credentials
   # Responds to "Are you sure you want to logout?" prompt

**Behavior:**

* Removes stored authentication credentials
* Clears cached authentication data
* Requires confirmation to prevent accidental logout
* Safe to run multiple times (no error if already logged out)

token
~~~~~

Manage API tokens including viewing current token (masked) and updating credentials.

.. code-block:: bash

   yt auth token [OPTIONS]

**Options:**

.. list-table::
   :widths: 20 20 60
   :header-rows: 1

   * - Option
     - Type
     - Description
   * - ``--show``
     - flag
     - Show current token (masked for security)
   * - ``--update``
     - flag
     - Update the current API token

**Examples:**

.. code-block:: bash

   # Show current authentication status and masked token
   yt auth token --show

   # Update API token (prompts for new token)
   yt auth token --update

   # Show help for token management
   yt auth token

**Token Display Format:**

When using ``--show``, tokens are displayed in masked format for security:

.. code-block:: text

   Current token: perm:abc12345...xyz789
   Base URL: https://company.youtrack.cloud
   Username: john.doe

Authentication Process
---------------------

Initial Setup
~~~~~~~~~~~~

1. **Obtain API Token**: Generate a permanent token in YouTrack web interface
2. **Run Login Command**: Use ``yt auth login`` to authenticate
3. **Verify Credentials**: CLI automatically verifies token validity
4. **Store Securely**: Credentials are stored in local configuration

Token Generation
~~~~~~~~~~~~~~~

To generate an API token in YouTrack:

1. Login to YouTrack web interface
2. Go to your profile settings
3. Navigate to "Authentication" section
4. Create a new "Permanent Token"
5. Copy the token for CLI authentication

**Token Permissions:**
Ensure your token has appropriate permissions for CLI operations:

* Read access to projects and issues
* Write access for creating/updating resources
* Administrative access for admin commands (if needed)

Authentication Workflow
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Step 1: Initial authentication
   yt auth login --base-url https://company.youtrack.cloud

   # Step 2: Verify authentication works
   yt auth token --show

   # Step 3: Test CLI functionality
   yt projects list

   # Step 4: Use CLI normally
   yt issues list --assignee me

Security Features
----------------

Credential Storage
~~~~~~~~~~~~~~~~~

* **Dual Storage**: Sensitive tokens stored in system keyring, configuration in ``~/.config/youtrack-cli/.env``
* **Encryption**: Tokens encrypted in keyring using Fernet symmetric encryption
* **Access Control**: Files have restricted permissions, keyring uses OS security
* **No Plaintext**: Tokens never stored in plaintext, .env file shows "[Stored in keyring]" placeholder

Token Masking
~~~~~~~~~~~~

* **Display Security**: Tokens and API keys masked when displayed (``abc123...xyz789``)
* **Log Safety**: Tokens not exposed in command output or logs
* **History Protection**: Tokens not stored in shell history
* **Config List Safety**: API keys shown as masked or "[Stored in keyring]" in config list

Session Management
~~~~~~~~~~~~~~~~~

* **Token Validation**: Automatic verification of token validity
* **Refresh Handling**: Proper handling of token expiration
* **Error Recovery**: Clear error messages for authentication failures

Common Workflows
----------------

Initial Setup Workflow
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # First-time setup
   echo "Setting up YouTrack CLI authentication..."

   # Login interactively
   yt auth login

   # Verify setup
   yt auth token --show

   # Test connection
   yt projects list

   echo "Authentication setup complete!"

Token Rotation Workflow
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Periodic token rotation for security
   echo "Rotating API token..."

   # Generate new token in YouTrack web interface first
   # Then update CLI credentials
   yt auth token --update

   # Verify new token works
   yt auth token --show
   yt projects list

   echo "Token rotation complete!"

Team Setup Workflow
~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Setup script for team members
   #!/bin/bash

   echo "YouTrack CLI Team Setup"
   echo "======================"
   echo "Please have your API token ready"
   echo ""

   # Standard company YouTrack instance
   yt auth login --base-url https://company.youtrack.cloud

   # Verify setup
   if yt projects list > /dev/null 2>&1; then
     echo "✅ Authentication successful!"
     echo "You can now use the YouTrack CLI"
   else
     echo "❌ Authentication failed. Please check your token."
   fi

Troubleshooting Authentication
-----------------------------

Authentication Verification
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Check current authentication status
   yt auth token --show

   # Test authentication with simple command
   yt projects list

   # Verify token has correct permissions
   yt users list

Token Issues
~~~~~~~~~~~

.. code-block:: bash

   # If token expired or invalid
   yt auth token --update

   # If completely broken, re-authenticate
   yt auth logout
   yt auth login

   # Clear any cached credentials
   rm ~/.config/youtrack-cli/.env
   yt auth login

Connection Problems
~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Test basic connectivity
   curl -H "Authorization: Bearer YOUR_TOKEN" \
        "https://company.youtrack.cloud/api/admin/projects"

   # Check YouTrack instance URL
   yt auth token --show

   # Re-authenticate with correct URL
   yt auth logout
   yt auth login --base-url https://correct.youtrack.cloud

SSL Certificate Issues
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # For self-signed certificates or internal CAs
   yt auth login --base-url https://internal.youtrack.local --no-verify-ssl

   # Test connectivity with SSL verification disabled
   curl -k -H "Authorization: Bearer YOUR_TOKEN" \
        "https://internal.youtrack.local/api/admin/projects"

   # Note: SSL verification setting is saved with credentials
   # All subsequent API calls will use the same SSL verification setting

Error Handling
--------------

Common error scenarios and solutions:

**Invalid Token**
  * Regenerate token in YouTrack web interface
  * Update credentials using ``yt auth token --update``

**Expired Token**
  * Create new permanent token
  * Update CLI credentials

**Wrong Base URL**
  * Verify YouTrack instance URL
  * Re-authenticate with correct URL

**Permission Denied**
  * Check token permissions in YouTrack
  * Ensure token has required access levels

**Network Issues**
  * Verify connectivity to YouTrack instance
  * Check firewall and proxy settings

**SSL Certificate Errors**
  * For self-signed certificates: ``yt auth login --no-verify-ssl``
  * For corporate CAs: Add CA certificate to system trust store
  * Warning: Only disable SSL verification on trusted networks

**Corrupted Credentials**
  * Clear stored credentials: ``yt auth logout``
  * Re-authenticate: ``yt auth login``

Configuration Files
------------------

Credential Storage Location
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Default credential storage
   ~/.config/youtrack-cli/.env

   # Custom config file location
   yt --config /path/to/custom.env auth login

Configuration Format
~~~~~~~~~~~~~~~~~~~

The configuration file contains non-sensitive authentication data:

.. code-block:: bash

   # Example structure (token stored separately in keyring)
   YOUTRACK_BASE_URL=https://company.youtrack.cloud
   YOUTRACK_API_KEY=[Stored in keyring]
   YOUTRACK_USERNAME=john.doe
   YOUTRACK_VERIFY_SSL=true

Custom Configuration
~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Use custom configuration file
   yt --config /path/to/project.env auth login

   # Environment-specific authentication
   yt --config ~/.config/yt-dev.env auth login    # Development
   yt --config ~/.config/yt-prod.env auth login   # Production

Security Best Practices
-----------------------

Token Management
~~~~~~~~~~~~~~~

1. **Regular Rotation**: Rotate tokens periodically for security
2. **Minimal Permissions**: Use tokens with minimal required permissions
3. **Secure Generation**: Generate tokens securely in YouTrack web interface
4. **No Sharing**: Never share tokens between users or systems

Storage Security
~~~~~~~~~~~~~~~

1. **File Permissions**: Ensure config files have restricted permissions
2. **Backup Security**: Exclude credential files from backups
3. **Access Control**: Limit access to credential storage locations

Operational Security
~~~~~~~~~~~~~~~~~~~

1. **Environment Separation**: Use different tokens for different environments
2. **Audit Trail**: Monitor token usage and access patterns
3. **Incident Response**: Have procedures for token compromise
4. **Team Guidelines**: Establish team standards for authentication

Automation and CI/CD
-------------------

Environment Variables
~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Set environment variables for automation
   export YOUTRACK_BASE_URL="https://company.youtrack.cloud"
   export YOUTRACK_TOKEN="perm:your_token_here"

   # Use in scripts
   yt --config <(echo "YOUTRACK_BASE_URL=$YOUTRACK_BASE_URL"; echo "YOUTRACK_TOKEN=$YOUTRACK_TOKEN") projects list

CI/CD Integration
~~~~~~~~~~~~~~~~

.. code-block:: yaml

   # GitHub Actions example
   - name: Setup YouTrack CLI
     env:
       YOUTRACK_TOKEN: ${{ secrets.YOUTRACK_TOKEN }}
       YOUTRACK_BASE_URL: ${{ secrets.YOUTRACK_BASE_URL }}
     run: |
       echo "YOUTRACK_TOKEN=$YOUTRACK_TOKEN" > ~/.youtrack-cli.env
       echo "YOUTRACK_BASE_URL=$YOUTRACK_BASE_URL" >> ~/.youtrack-cli.env
       yt --config ~/.youtrack-cli.env projects list

Service Account Setup
~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Create service account token in YouTrack
   # Use for automated systems and CI/CD

   # Setup service account authentication
   yt auth login \
     --base-url https://company.youtrack.cloud \
     --username service-account

   # Test service account access
   yt projects list

Integration Examples
-------------------

Script Authentication
~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   #!/bin/bash
   # Automated script with authentication check

   # Check if authenticated
   if ! yt auth token --show > /dev/null 2>&1; then
     echo "Please authenticate first:"
     yt auth login
   fi

   # Continue with script logic
   echo "Running automated tasks..."
   yt projects list

Multi-Environment Setup
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   #!/bin/bash
   # Setup for multiple environments

   ENVIRONMENTS=("dev" "staging" "prod")

   for env in "${ENVIRONMENTS[@]}"; do
     echo "Setting up $env environment..."
     yt --config ~/.config/yt-${env}.env auth login \
       --base-url "https://${env}.youtrack.company.com"
   done

Credential Backup
~~~~~~~~~~~~~~~~

.. code-block:: bash

   #!/bin/bash
   # Backup authentication configuration (be careful with security)

   BACKUP_DIR="~/.youtrack-cli-backup"
   mkdir -p "$BACKUP_DIR"

   # Copy configuration (ensure secure storage)
   cp ~/.config/youtrack-cli/.env "$BACKUP_DIR/auth-backup-$(date +%Y%m%d).env"

   echo "Credentials backed up to $BACKUP_DIR"

See Also
--------

* :doc:`config` - Configuration management and environment setup
* :doc:`admin` - Administrative operations requiring elevated permissions
* :doc:`projects` - Project access and permissions
* :doc:`users` - User management and authentication
* YouTrack API documentation for token generation
