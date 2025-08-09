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
   * - ``--cert-file``
     - path
     - Path to SSL certificate file (.crt or .pem format)
   * - ``--ca-bundle``
     - path
     - Path to CA bundle file for custom certificate authorities
   * - ``--verify-ssl/--no-verify-ssl``
     - flag
     - Enable/disable SSL certificate verification (default: enabled)

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

   # Login with custom SSL certificate file
   yt auth login --base-url https://internal.youtrack.local --cert-file /path/to/cert.pem

   # Login with custom CA bundle
   yt auth login --base-url https://company.youtrack.cloud --ca-bundle /path/to/ca-bundle.crt

   # Login without SSL verification (not recommended)
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

refresh
~~~~~~~

Manually refresh the current token to maintain authentication validity.

.. code-block:: bash

   yt auth refresh

**Description:**

The refresh command manually updates and refreshes your current authentication token. This is useful for maintaining active authentication sessions and ensuring token validity, especially in long-running automation scripts or when working with tokens that have expiration policies.

**Examples:**

.. code-block:: bash

   # Manually refresh current authentication token
   yt auth refresh

   # Use in automation to maintain session
   yt auth refresh && yt issues list

**Use Cases:**

* Maintaining authentication in long-running scripts
* Refreshing tokens before critical operations
* Ensuring token validity in automated workflows
* Troubleshooting authentication issues

status
~~~~~~

Show authentication status and display current token information.

.. code-block:: bash

   yt auth status

**Description:**

The status command provides detailed information about your current authentication state, including token validity, base URL configuration, and user information. This is useful for verifying authentication setup and troubleshooting connection issues.

**Examples:**

.. code-block:: bash

   # Show current authentication status
   yt auth status

   # Check authentication before running other commands
   yt auth status && yt projects list

**Status Information Displayed:**

* Authentication state (authenticated/not authenticated)
* Current token status (valid/invalid/expired)
* Base URL configuration
* Username/user information
* Token type and permissions
* SSL verification settings

**Use Cases:**

* Verifying authentication before running scripts
* Troubleshooting authentication issues
* Checking token validity and configuration
* Auditing authentication setup in team environments

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
----------------------

Initial Setup
~~~~~~~~~~~~~

1. **Obtain API Token**: Generate a permanent token in YouTrack web interface
2. **Run Login Command**: Use ``yt auth login`` to authenticate
3. **Verify Credentials**: CLI automatically verifies token validity
4. **Store Securely**: Credentials are stored in local configuration

Token Generation
~~~~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Step 1: Initial authentication
   yt auth login --base-url https://company.youtrack.cloud

   # Step 2: Verify authentication works
   yt auth token --show

   # Step 3: Test CLI functionality
   yt projects list

   # Step 4: Use CLI normally
   yt issues list --assignee me

SSL Certificate Support
-----------------------

The YouTrack CLI supports custom SSL certificates for environments using self-signed certificates or custom certificate authorities. This enables secure communication with internal YouTrack instances.

Certificate Options
~~~~~~~~~~~~~~~~~~~

* **Certificate File** (``--cert-file``): Provide a specific SSL certificate file for verification
* **CA Bundle** (``--ca-bundle``): Provide a custom CA bundle for certificate authority validation
* **System CA Bundle**: Default behavior uses system's trusted certificate store
* **Disable Verification** (``--no-verify-ssl``): Disable SSL verification entirely (not recommended)

Certificate Formats
~~~~~~~~~~~~~~~~~~~

Supported certificate file formats:

* ``.pem`` - Privacy Enhanced Mail format (most common)
* ``.crt`` - Certificate file format
* CA bundles containing multiple certificates

Certificate Configuration Examples
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Use custom certificate for internal instance
   yt auth login \
     --base-url https://youtrack.internal.company.com \
     --cert-file /etc/ssl/certs/company-cert.pem

   # Use CA bundle for corporate certificate authority
   yt auth login \
     --base-url https://secure.youtrack.cloud \
     --ca-bundle /usr/local/share/ca-certificates/company-ca-bundle.crt

   # Verify certificate is valid
   openssl x509 -in /path/to/cert.pem -text -noout | grep "Subject:"

   # Test certificate with curl
   curl --cacert /path/to/cert.pem https://youtrack.internal.company.com/api/admin/projects

Certificate Storage
~~~~~~~~~~~~~~~~~~~

Certificate paths are stored in the configuration file for persistent use:

.. code-block:: bash

   # Configuration with certificate paths
   YOUTRACK_CERT_FILE=/etc/ssl/certs/company-cert.pem
   YOUTRACK_CA_BUNDLE=/usr/local/share/ca-certificates/company-ca-bundle.crt
   YOUTRACK_VERIFY_SSL=true

Once configured, all subsequent CLI commands will use the specified certificate configuration automatically.

Security Considerations
~~~~~~~~~~~~~~~~~~~~~~~

1. **Certificate Validation**: Always verify certificate authenticity before use
2. **File Permissions**: Ensure certificate files have appropriate read permissions
3. **Path Security**: Use absolute paths for certificate files
4. **Regular Updates**: Keep certificates updated before expiration
5. **Avoid Disabling**: Only disable SSL verification in secure, isolated environments

Troubleshooting Certificate Issues
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Common certificate problems and solutions

   # Problem: Certificate verification failed
   # Solution: Verify certificate is valid and not expired
   openssl x509 -in cert.pem -noout -dates

   # Problem: Certificate file not found
   # Solution: Check file path and permissions
   ls -la /path/to/cert.pem

   # Problem: Wrong certificate format
   # Solution: Convert certificate to PEM format
   openssl x509 -in cert.der -outform PEM -out cert.pem

   # Problem: Certificate chain incomplete
   # Solution: Use CA bundle with full certificate chain
   cat intermediate.crt root.crt > ca-bundle.crt

Security Features
----------------

Credential Storage
~~~~~~~~~~~~~~~~~~

* **Dual Storage**: Sensitive tokens stored in system keyring, configuration in ``~/.config/youtrack-cli/.env``
* **Encryption**: Tokens encrypted in keyring using Fernet symmetric encryption
* **Access Control**: Files have restricted permissions, keyring uses OS security
* **No Plaintext**: Tokens never stored in plaintext, .env file shows "[Stored in keyring]" placeholder

Token Masking
~~~~~~~~~~~~~

* **Display Security**: Tokens and API keys masked when displayed (``abc123...xyz789``)
* **Log Safety**: Tokens not exposed in command output or logs
* **History Protection**: Tokens not stored in shell history
* **Config List Safety**: API keys shown as masked or "[Stored in keyring]" in config list

Session Management
~~~~~~~~~~~~~~~~~~

* **Token Validation**: Automatic verification of token validity
* **Refresh Handling**: Proper handling of token expiration
* **Error Recovery**: Clear error messages for authentication failures

Common Workflows
----------------

Initial Setup Workflow
~~~~~~~~~~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~~~~~

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
-------------------------------

Authentication Verification
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Check current authentication status
   yt auth token --show

   # Test authentication with simple command
   yt projects list

   # Verify token has correct permissions
   yt users list

Token Issues
~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # For self-signed certificates - provide certificate file
   yt auth login --base-url https://internal.youtrack.local --cert-file /path/to/cert.pem

   # For custom CA certificates - provide CA bundle
   yt auth login --base-url https://company.youtrack.cloud --ca-bundle /path/to/ca-bundle.crt

   # Verify certificate file exists and is readable
   ls -la /path/to/cert.pem
   openssl x509 -in /path/to/cert.pem -text -noout

   # For testing only - disable SSL verification (NOT RECOMMENDED)
   yt auth login --base-url https://internal.youtrack.local --no-verify-ssl

   # Test connectivity with certificate
   curl --cacert /path/to/cert.pem -H "Authorization: Bearer YOUR_TOKEN" \
        "https://internal.youtrack.local/api/admin/projects"

   # Note: SSL settings (certificate paths or verification status) are saved with credentials
   # All subsequent API calls will use the same SSL configuration

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
  * For self-signed certificates: ``yt auth login --cert-file /path/to/cert.pem``
  * For corporate CAs: ``yt auth login --ca-bundle /path/to/ca-bundle.crt``
  * For testing only: ``yt auth login --no-verify-ssl`` (insecure)
  * Certificate formats supported: .pem, .crt
  * Warning: Only disable SSL verification on trusted networks
  * For detailed SSL troubleshooting, see: :doc:`../ssl-troubleshooting`

**Corrupted Credentials**
  * Clear stored credentials: ``yt auth logout``
  * Re-authenticate: ``yt auth login``

Configuration Files
------------------

Credential Storage Location
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Default credential storage
   ~/.config/youtrack-cli/.env

   # Custom config file location
   yt --config /path/to/custom.env auth login

Configuration Format
~~~~~~~~~~~~~~~~~~~~

The configuration file contains non-sensitive authentication data:

.. code-block:: bash

   # Example structure (token stored separately in keyring)
   YOUTRACK_BASE_URL=https://company.youtrack.cloud
   YOUTRACK_API_KEY=[Stored in keyring]
   YOUTRACK_USERNAME=john.doe
   YOUTRACK_VERIFY_SSL=true
   YOUTRACK_CERT_FILE=/path/to/cert.pem  # Optional: custom certificate
   YOUTRACK_CA_BUNDLE=/path/to/ca-bundle.crt  # Optional: CA bundle

Custom Configuration
~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Use custom configuration file
   yt --config /path/to/project.env auth login

   # Environment-specific authentication
   yt --config ~/.config/yt-dev.env auth login    # Development
   yt --config ~/.config/yt-prod.env auth login   # Production

Security Best Practices
-----------------------

Token Management
~~~~~~~~~~~~~~~~

1. **Regular Rotation**: Rotate tokens periodically for security
2. **Minimal Permissions**: Use tokens with minimal required permissions
3. **Secure Generation**: Generate tokens securely in YouTrack web interface
4. **No Sharing**: Never share tokens between users or systems

Storage Security
~~~~~~~~~~~~~~~~

1. **File Permissions**: Ensure config files have restricted permissions
2. **Backup Security**: Exclude credential files from backups
3. **Access Control**: Limit access to credential storage locations

Operational Security
~~~~~~~~~~~~~~~~~~~~

1. **Environment Separation**: Use different tokens for different environments
2. **Audit Trail**: Monitor token usage and access patterns
3. **Incident Response**: Have procedures for token compromise
4. **Team Guidelines**: Establish team standards for authentication

Automation and CI/CD
-------------------

Environment Variables
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Set environment variables for automation
   export YOUTRACK_BASE_URL="https://company.youtrack.cloud"
   export YOUTRACK_TOKEN="perm:your_token_here"

   # Use in scripts
   yt --config <(echo "YOUTRACK_BASE_URL=$YOUTRACK_BASE_URL"; echo "YOUTRACK_TOKEN=$YOUTRACK_TOKEN") projects list

CI/CD Integration
~~~~~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~~~

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
