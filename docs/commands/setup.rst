Setup Command
=============

The ``yt setup`` command provides an interactive setup wizard for first-time configuration of YouTrack CLI. This command guides you through configuring your YouTrack URL, authentication, and basic preferences to get you up and running quickly.

.. contents:: Table of Contents
   :local:
   :depth: 2

Overview
--------

The setup command simplifies initial CLI configuration by:

* Guiding you through YouTrack server connection configuration
* Setting up authentication credentials securely
* Configuring basic CLI preferences and defaults
* Validating your configuration to ensure everything works correctly
* Providing helpful tips and best practices for CLI usage

Base Command
------------

.. code-block:: bash

   yt setup [OPTIONS]

Command Options
---------------

**Options:**
  * ``--skip-validation`` - Skip connection validation during setup
  * ``-h, --help`` - Show help message and exit

**Examples:**

.. code-block:: bash

   # Run the interactive setup wizard
   yt setup

   # Setup without validating the connection (useful for offline setup)
   yt setup --skip-validation

Setup Process
-------------

Interactive Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~

The setup wizard will guide you through several configuration steps:

**1. YouTrack Server Configuration:**
   * YouTrack instance URL (e.g., https://youtrack.yourcompany.com)
   * Server connection validation and testing
   * SSL/TLS configuration if required

**2. Authentication Setup:**
   * Authentication method selection (token-based recommended)
   * Credential entry and secure storage
   * Authentication testing and verification

**3. Basic Preferences:**
   * Default output format preferences
   * Color and display options
   * Basic workflow preferences

**4. Validation and Testing:**
   * Connection testing to verify server accessibility
   * Authentication verification
   * Basic API functionality testing

Configuration Validation
~~~~~~~~~~~~~~~~~~~~~~~~~

By default, the setup wizard validates your configuration:

.. code-block:: bash

   # Standard setup with validation
   yt setup

The validation process includes:

* **Network Connectivity:** Testing connection to your YouTrack instance
* **Authentication:** Verifying credentials and permissions
* **API Access:** Testing basic API functionality
* **Configuration:** Ensuring all settings are properly saved

Skipping Validation
~~~~~~~~~~~~~~~~~~~

You can skip validation during setup if needed:

.. code-block:: bash

   # Setup without validation (useful for offline environments)
   yt setup --skip-validation

Use cases for skipping validation:

* **Offline Setup:** Configuring CLI when YouTrack server is temporarily unavailable
* **Network Restrictions:** Setting up in environments with limited connectivity
* **Batch Configuration:** Automated setup scripts where validation is handled separately
* **Testing Configurations:** Setting up test configurations without live connections

First-Time Setup Workflow
--------------------------

Initial Installation
~~~~~~~~~~~~~~~~~~~

After installing YouTrack CLI, start with the setup command:

.. code-block:: bash

   # First-time setup
   yt setup

The wizard will walk you through:

1. **Welcome and Introduction**
   * Overview of the setup process
   * Information about what will be configured

2. **Server Configuration**
   * YouTrack server URL input
   * Connection testing (unless skipped)
   * SSL certificate validation if needed

3. **Authentication Configuration**
   * Token-based authentication setup (recommended)
   * Secure credential storage
   * Authentication testing

4. **Preference Configuration**
   * Default project selection (if applicable)
   * Output format preferences
   * Display and color options

5. **Completion and Verification**
   * Configuration summary
   * Test commands to verify setup
   * Next steps and usage tips

Post-Setup Verification
~~~~~~~~~~~~~~~~~~~~~~~

After completing setup, verify your configuration:

.. code-block:: bash

   # Test authentication
   yt auth status

   # Test basic functionality
   yt projects list

   # Check configuration
   yt config show

Configuration Storage
---------------------

Secure Credential Storage
~~~~~~~~~~~~~~~~~~~~~~~~

The setup wizard ensures secure handling of your credentials:

* **Local Storage:** Credentials are stored locally on your system
* **Encryption:** Sensitive data is encrypted using system-appropriate methods
* **Access Control:** Configuration files have restricted file permissions
* **No Transmission:** Credentials are never transmitted except for authentication

Configuration File Locations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Setup creates configuration files in standard locations:

* **Linux/macOS:** ``~/.config/youtrack-cli/``
* **Windows:** ``%APPDATA%\youtrack-cli\``

The configuration includes:

* **Connection Settings:** Server URL and connection parameters
* **Authentication:** Encrypted credential storage
* **User Preferences:** Default options and display settings
* **Cache Configuration:** Local cache settings for performance

Reconfiguration and Updates
----------------------------

Running Setup Again
~~~~~~~~~~~~~~~~~~~

You can run setup multiple times to update your configuration:

.. code-block:: bash

   # Reconfigure existing setup
   yt setup

The wizard will:

* **Detect Existing Configuration:** Show current settings for reference
* **Allow Updates:** Let you modify any configuration option
* **Preserve Settings:** Keep settings you don't want to change
* **Validate Changes:** Test new configuration before saving

Partial Reconfiguration
~~~~~~~~~~~~~~~~~~~~~~

For specific configuration changes, consider these alternatives to full setup:

.. code-block:: bash

   # Update authentication only
   yt auth login

   # Modify specific configuration settings
   yt config set server.url https://new-youtrack.com

   # Update display preferences
   yt config set output.format json

Integration with Other Commands
-------------------------------

Authentication Integration
~~~~~~~~~~~~~~~~~~~~~~~~~

Setup works seamlessly with authentication commands:

.. code-block:: bash

   # Setup includes authentication configuration
   yt setup

   # Later, you can update authentication separately
   yt auth login --token new-token

   # Check authentication status anytime
   yt auth status

Configuration Management
~~~~~~~~~~~~~~~~~~~~~~~~

Setup integrates with configuration management:

.. code-block:: bash

   # Setup creates initial configuration
   yt setup

   # View and modify configuration later
   yt config show
   yt config set key value

   # Export configuration for backup
   yt config export config-backup.json

Automation and Scripting
-------------------------

Automated Setup
~~~~~~~~~~~~~~~

For automated environments, use non-interactive setup:

.. code-block:: bash

   #!/bin/bash
   # Automated setup script

   # Set environment variables for automated configuration
   export YOUTRACK_URL="https://youtrack.company.com"
   export YOUTRACK_TOKEN="your-api-token"

   # Run setup with validation skipped for automation
   yt setup --skip-validation

   # Verify setup completed successfully
   yt auth status

CI/CD Integration
~~~~~~~~~~~~~~~~~

Integrate setup into CI/CD pipelines:

.. code-block:: yaml

   # GitHub Actions example
   - name: Setup YouTrack CLI
     run: |
       yt setup --skip-validation
       yt auth login --token ${{ secrets.YOUTRACK_TOKEN }} --base-url ${{ vars.YOUTRACK_URL }}

Docker Container Setup
~~~~~~~~~~~~~~~~~~~~~~

For containerized environments:

.. code-block:: dockerfile

   # Dockerfile example
   FROM python:3.11-slim
   RUN pip install youtrack-cli

   # Copy pre-configured setup
   COPY youtrack-config.json /root/.config/youtrack-cli/config.json

   # Verify setup
   RUN yt auth status

Best Practices
--------------

**Initial Setup:**
  * Run setup in a secure environment to protect credential entry
  * Use strong, unique tokens for authentication
  * Test configuration thoroughly after initial setup

**Security Considerations:**
  * Regularly rotate authentication tokens
  * Keep configuration files secure with appropriate permissions
  * Use enhanced security mode for sensitive environments

**Team Environments:**
  * Document your YouTrack server configuration for team members
  * Provide setup instructions specific to your environment
  * Consider creating setup automation for consistent team configuration

**Maintenance:**
  * Review and update configuration periodically
  * Test configuration after YouTrack server updates
  * Keep backup copies of working configurations

Troubleshooting
---------------

Common Setup Issues
~~~~~~~~~~~~~~~~~~~

**Connection Problems:**
  * Verify YouTrack server URL is correct and accessible
  * Check network connectivity and firewall settings
  * Ensure SSL certificates are valid if using HTTPS

**Authentication Issues:**
  * Verify token is valid and has appropriate permissions
  * Check that token hasn't expired
  * Ensure user account associated with token is active

**Configuration Problems:**
  * Check file permissions on configuration directory
  * Ensure sufficient disk space for configuration files
  * Verify environment variables if using automated setup

Setup Validation Failures
~~~~~~~~~~~~~~~~~~~~~~~~~

If setup validation fails:

.. code-block:: bash

   # Run setup with validation skipped to complete configuration
   yt setup --skip-validation

   # Then diagnose issues separately
   yt auth status
   yt projects list --debug

Recovery from Failed Setup
~~~~~~~~~~~~~~~~~~~~~~~~~~

If setup fails or becomes corrupted:

.. code-block:: bash

   # Remove existing configuration
   rm -rf ~/.config/youtrack-cli/

   # Start fresh setup
   yt setup

   # Or restore from backup
   cp backup-config.json ~/.config/youtrack-cli/config.json

See Also
--------

* :doc:`auth` - Authentication management and login
* :doc:`config` - CLI configuration and settings management
* Getting Started guide for complete setup instructions
* :doc:`troubleshooting` - Common issues and solutions
