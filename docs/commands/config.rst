Configuration Command Group
============================

The ``yt config`` command group provides comprehensive configuration management for YouTrack CLI. Set default values, manage environment-specific settings, and customize CLI behavior.

.. contents:: Table of Contents
   :local:
   :depth: 2

Overview
--------

YouTrack CLI configuration allows you to customize behavior, set defaults, and manage environment-specific settings. The config command group allows you to:

* Set and retrieve configuration values
* Manage default settings for commands
* Handle environment-specific configurations
* Store frequently used parameters
* Customize CLI behavior and output preferences

Configuration is stored in ``~/.config/youtrack-cli/.env`` by default, or in a custom file specified with the ``--config`` option.

Base Command
------------

.. code-block:: bash

   yt config [OPTIONS] COMMAND [ARGS]...

Configuration Commands
----------------------

set
~~~

Set a configuration value that will be used as a default for CLI commands.

.. code-block:: bash

   yt config set KEY VALUE

**Arguments:**

* ``KEY`` - The configuration key to set (required)
* ``VALUE`` - The value to assign to the key (required)

**Examples:**

.. code-block:: bash

   # Set default project
   yt config set DEFAULT_PROJECT "MY-PROJECT"

   # Set default number of items per page
   yt config set ITEMS_PER_PAGE "25"

   # Set preferred output format
   yt config set DEFAULT_FORMAT "json"

   # Set default assignee
   yt config set DEFAULT_ASSIGNEE "john.doe"

   # Set custom field defaults
   yt config set DEFAULT_PRIORITY "Normal"
   yt config set DEFAULT_TYPE "Task"

get
~~~

Retrieve a specific configuration value.

.. code-block:: bash

   yt config get KEY

**Arguments:**

* ``KEY`` - The configuration key to retrieve (required)

**Examples:**

.. code-block:: bash

   # Get default project setting
   yt config get DEFAULT_PROJECT

   # Get items per page setting
   yt config get ITEMS_PER_PAGE

   # Get output format preference
   yt config get DEFAULT_FORMAT

   # Check if key exists (returns empty if not set)
   yt config get NON_EXISTENT_KEY

list
~~~~

List all current configuration values with sensitive values masked for security.

.. code-block:: bash

   yt config list

**Examples:**

.. code-block:: bash

   # List all configuration values
   yt config list

   # Output shows all key-value pairs with sensitive data masked
   # Sensitive keys (containing 'token', 'password', 'secret') are masked

Common Configuration Keys
------------------------

Project Settings
~~~~~~~~~~~~~~~

.. list-table::
   :widths: 30 20 50
   :header-rows: 1

   * - Key
     - Example Value
     - Description
   * - ``DEFAULT_PROJECT``
     - ``"WEB-PROJECT"``
     - Default project for issue operations
   * - ``DEFAULT_ASSIGNEE``
     - ``"john.doe"``
     - Default assignee for new issues
   * - ``PROJECT_FILTER``
     - ``"project:WEB"``
     - Default project filter for searches

Display Settings
~~~~~~~~~~~~~~~

.. list-table::
   :widths: 30 20 50
   :header-rows: 1

   * - Key
     - Example Value
     - Description
   * - ``DEFAULT_FORMAT``
     - ``"table"``
     - Preferred output format (table, json)
   * - ``ITEMS_PER_PAGE``
     - ``"25"``
     - Default number of items to display
   * - ``COLOR_OUTPUT``
     - ``"true"``
     - Enable colored output
   * - ``TIMEZONE``
     - ``"UTC"``
     - Default timezone for date displays

Issue Management
~~~~~~~~~~~~~~~

.. list-table::
   :widths: 30 20 50
   :header-rows: 1

   * - Key
     - Example Value
     - Description
   * - ``DEFAULT_PRIORITY``
     - ``"Normal"``
     - Default priority for new issues
   * - ``DEFAULT_TYPE``
     - ``"Task"``
     - Default issue type
   * - ``DEFAULT_STATE``
     - ``"Open"``
     - Default state for new issues
   * - ``AUTO_ASSIGN``
     - ``"true"``
     - Auto-assign issues to current user

Time Tracking
~~~~~~~~~~~~~

.. list-table::
   :widths: 30 20 50
   :header-rows: 1

   * - Key
     - Example Value
     - Description
   * - ``DEFAULT_WORK_TYPE``
     - ``"Development"``
     - Default work type for time logging
   * - ``TIME_FORMAT``
     - ``"hours"``
     - Preferred time format (hours, minutes)
   * - ``ROUND_TIME``
     - ``"15"``
     - Round time entries to nearest X minutes

Connection Settings
~~~~~~~~~~~~~~~~~~

.. list-table::
   :widths: 30 20 50
   :header-rows: 1

   * - Key
     - Example Value
     - Description
   * - ``REQUEST_TIMEOUT``
     - ``"30"``
     - API request timeout in seconds
   * - ``RETRY_COUNT``
     - ``"3"``
     - Number of retry attempts for failed requests
   * - ``CACHE_ENABLED``
     - ``"true"``
     - Enable response caching

Configuration Examples
---------------------

Basic Setup
~~~~~~~~~~

.. code-block:: bash

   # Set up basic configuration for daily use
   yt config set DEFAULT_PROJECT "WEB-DEVELOPMENT"
   yt config set DEFAULT_ASSIGNEE "john.doe"
   yt config set ITEMS_PER_PAGE "20"
   yt config set DEFAULT_FORMAT "table"

   # Verify configuration
   yt config list

Development Environment
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Development-specific settings
   yt config set DEFAULT_PROJECT "DEV-PROJECT"
   yt config set DEFAULT_PRIORITY "High"
   yt config set DEFAULT_TYPE "Bug"
   yt config set AUTO_ASSIGN "true"

   # Development workflow preferences
   yt config set DEFAULT_WORK_TYPE "Development"
   yt config set TIME_FORMAT "hours"
   yt config set ROUND_TIME "15"

Team Lead Configuration
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Configuration for team lead responsibilities
   yt config set ITEMS_PER_PAGE "50"
   yt config set DEFAULT_FORMAT "json"
   yt config set SHOW_ARCHIVED "true"

   # Reporting preferences
   yt config set REPORT_PERIOD "weekly"
   yt config set INCLUDE_COMPLETED "true"
   yt config set GROUP_BY_ASSIGNEE "true"

Project Manager Setup
~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Project manager configuration
   yt config set DEFAULT_VIEW "summary"
   yt config set SHOW_ESTIMATES "true"
   yt config set INCLUDE_SUBTASKS "true"
   yt config set DEFAULT_TIMEFRAME "sprint"

   # Stakeholder reporting
   yt config set EXECUTIVE_FORMAT "summary"
   yt config set HIDE_TECHNICAL_DETAILS "true"

Environment-Specific Configuration
----------------------------------

Multiple Environments
~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Development environment
   yt --config ~/.config/yt-dev.env config set DEFAULT_PROJECT "DEV-PROJECT"
   yt --config ~/.config/yt-dev.env config set BASE_URL "https://dev.youtrack.company.com"

   # Staging environment
   yt --config ~/.config/yt-staging.env config set DEFAULT_PROJECT "STAGING-PROJECT"
   yt --config ~/.config/yt-staging.env config set BASE_URL "https://staging.youtrack.company.com"

   # Production environment
   yt --config ~/.config/yt-prod.env config set DEFAULT_PROJECT "PROD-PROJECT"
   yt --config ~/.config/yt-prod.env config set BASE_URL "https://youtrack.company.com"

Project-Specific Settings
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Web project configuration
   yt --config ~/.config/yt-web.env config set DEFAULT_PROJECT "WEB-PROJECT"
   yt --config ~/.config/yt-web.env config set DEFAULT_TYPE "Story"
   yt --config ~/.config/yt-web.env config set DEFAULT_PRIORITY "Medium"

   # API project configuration
   yt --config ~/.config/yt-api.env config set DEFAULT_PROJECT "API-PROJECT"
   yt --config ~/.config/yt-api.env config set DEFAULT_TYPE "Epic"
   yt --config ~/.config/yt-api.env config set DEFAULT_PRIORITY "High"

Configuration Workflows
-----------------------

Initial Setup
~~~~~~~~~~~~

.. code-block:: bash

   # Initial configuration setup workflow
   echo "Setting up YouTrack CLI configuration..."

   # Basic settings
   yt config set DEFAULT_PROJECT "$(read -p 'Default project: ' && echo $REPLY)"
   yt config set DEFAULT_ASSIGNEE "$(whoami)"
   yt config set ITEMS_PER_PAGE "25"

   # Display preferences
   yt config set DEFAULT_FORMAT "table"
   yt config set COLOR_OUTPUT "true"

   # Time tracking defaults
   yt config set DEFAULT_WORK_TYPE "Development"
   yt config set TIME_FORMAT "hours"

   echo "Configuration complete!"
   yt config list

Team Onboarding
~~~~~~~~~~~~~~

.. code-block:: bash

   #!/bin/bash
   # Team member onboarding configuration script

   echo "YouTrack CLI Team Configuration"
   echo "==============================="

   # Get user information
   read -p "Enter your username: " USERNAME
   read -p "Enter default project: " PROJECT
   read -p "Enter preferred items per page (default 25): " ITEMS
   ITEMS=${ITEMS:-25}

   # Set standard team configuration
   yt config set DEFAULT_ASSIGNEE "$USERNAME"
   yt config set DEFAULT_PROJECT "$PROJECT"
   yt config set ITEMS_PER_PAGE "$ITEMS"

   # Team standards
   yt config set DEFAULT_FORMAT "table"
   yt config set DEFAULT_WORK_TYPE "Development"
   yt config set TIME_FORMAT "hours"
   yt config set ROUND_TIME "15"

   echo "Team configuration applied!"

Configuration Migration
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   #!/bin/bash
   # Migrate configuration between environments

   SOURCE_CONFIG="$1"
   TARGET_CONFIG="$2"

   if [ -z "$SOURCE_CONFIG" ] || [ -z "$TARGET_CONFIG" ]; then
     echo "Usage: $0 <source-config> <target-config>"
     exit 1
   fi

   # Export configuration from source
   yt --config "$SOURCE_CONFIG" config list > source_config.txt

   # Parse and apply to target (simplified example)
   # Note: This would need proper parsing in practice
   grep -v "token\|password\|secret" source_config.txt | while IFS='=' read key value; do
     yt --config "$TARGET_CONFIG" config set "$key" "$value"
   done

   echo "Configuration migrated from $SOURCE_CONFIG to $TARGET_CONFIG"

Best Practices
--------------

1. **Environment Separation**: Use separate config files for different environments.

2. **Security**: Never store sensitive data in configuration files.

3. **Documentation**: Document custom configuration keys and their purposes.

4. **Team Standards**: Establish team-wide configuration standards for consistency.

5. **Backup**: Backup important configuration files.

6. **Validation**: Validate configuration values for correctness.

7. **Defaults**: Set sensible defaults that improve daily workflow efficiency.

8. **Version Control**: Consider versioning team configuration templates.

9. **Regular Review**: Periodically review and update configuration settings.

10. **Testing**: Test configuration changes in non-production environments first.

Configuration File Management
----------------------------

File Locations
~~~~~~~~~~~~~

.. code-block:: bash

   # Default configuration file
   ~/.config/youtrack-cli/.env

   # Custom configuration file
   yt --config /path/to/custom.env config set KEY VALUE

   # Environment-specific configurations
   ~/.config/youtrack-cli/dev.env
   ~/.config/youtrack-cli/staging.env
   ~/.config/youtrack-cli/production.env

File Format
~~~~~~~~~~

Configuration files use environment variable format:

.. code-block:: bash

   # YouTrack CLI Configuration File
   DEFAULT_PROJECT=WEB-PROJECT
   DEFAULT_ASSIGNEE=john.doe
   ITEMS_PER_PAGE=25
   DEFAULT_FORMAT=table
   COLOR_OUTPUT=true
   DEFAULT_WORK_TYPE=Development

Backup and Restore
~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Backup configuration
   cp ~/.config/youtrack-cli/.env ~/.config/youtrack-cli/.env.backup

   # Restore configuration
   cp ~/.config/youtrack-cli/.env.backup ~/.config/youtrack-cli/.env

   # Export configuration for sharing (excluding sensitive data)
   yt config list | grep -v "token\|password\|secret" > team_config.txt

Advanced Configuration
---------------------

Custom Configuration Templates
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   #!/bin/bash
   # Configuration template for new team members

   TEMPLATE_FILE="team_config_template.env"

   cat > "$TEMPLATE_FILE" << 'EOF'
   # Team Configuration Template
   DEFAULT_PROJECT=TEAM-PROJECT
   ITEMS_PER_PAGE=25
   DEFAULT_FORMAT=table
   COLOR_OUTPUT=true
   DEFAULT_WORK_TYPE=Development
   TIME_FORMAT=hours
   ROUND_TIME=15
   AUTO_ASSIGN=true
   EOF

   echo "Configuration template created: $TEMPLATE_FILE"

Configuration Validation
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   #!/bin/bash
   # Validate configuration settings

   echo "Validating YouTrack CLI configuration..."

   # Check required settings
   REQUIRED_SETTINGS=("DEFAULT_PROJECT" "DEFAULT_ASSIGNEE")

   for setting in "${REQUIRED_SETTINGS[@]}"; do
     value=$(yt config get "$setting")
     if [ -z "$value" ]; then
       echo "❌ Missing required setting: $setting"
     else
       echo "✅ $setting: $value"
     fi
   done

   # Test configuration by running a simple command
   if yt projects list > /dev/null 2>&1; then
     echo "✅ Configuration is valid and working"
   else
     echo "❌ Configuration test failed"
   fi

Dynamic Configuration
~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   #!/bin/bash
   # Dynamic configuration based on current context

   # Detect current directory for project-specific settings
   if [[ "$PWD" == *"/web-project"* ]]; then
     export YT_CONFIG="$HOME/.config/yt-web.env"
   elif [[ "$PWD" == *"/api-project"* ]]; then
     export YT_CONFIG="$HOME/.config/yt-api.env"
   else
     export YT_CONFIG="$HOME/.config/youtrack-cli/.env"
   fi

   # Use detected configuration
   yt --config "$YT_CONFIG" "$@"

Error Handling
--------------

Common error scenarios and solutions:

**Configuration Key Not Found**
  Returns empty value; check key spelling and case sensitivity.

**Invalid Configuration Value**
  Validate values match expected formats (numbers, booleans, etc.).

**Permission Denied**
  Check file permissions on configuration directory and files.

**Configuration File Corruption**
  Restore from backup or recreate configuration settings.

**Environment Conflicts**
  Ensure environment variables don't conflict with configuration files.

**Missing Configuration Directory**
  CLI will create directory automatically on first use.

Integration Examples
-------------------

Shell Integration
~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Add to ~/.bashrc or ~/.zshrc
   alias yt-dev='yt --config ~/.config/yt-dev.env'
   alias yt-staging='yt --config ~/.config/yt-staging.env'
   alias yt-prod='yt --config ~/.config/yt-prod.env'

   # Function for dynamic config selection
   yt-project() {
     local project="$1"
     shift
     yt --config "$HOME/.config/yt-${project}.env" "$@"
   }

Configuration Scripts
~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   #!/bin/bash
   # Automated configuration deployment

   CONFIGS_DIR="/shared/youtrack-configs"
   LOCAL_CONFIG_DIR="$HOME/.config/youtrack-cli"

   # Deploy team configurations
   for config in dev staging prod; do
     cp "$CONFIGS_DIR/${config}.env" "$LOCAL_CONFIG_DIR/${config}.env"
     echo "Deployed $config configuration"
   done

   # Set appropriate permissions
   chmod 600 "$LOCAL_CONFIG_DIR"/*.env

   echo "Configuration deployment complete"

Monitoring and Auditing
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   #!/bin/bash
   # Audit configuration compliance

   echo "Configuration Compliance Report"
   echo "==============================="

   # Check for required settings
   COMPLIANCE_CHECKS=(
     "DEFAULT_PROJECT:required"
     "DEFAULT_ASSIGNEE:required"
     "ITEMS_PER_PAGE:numeric"
     "COLOR_OUTPUT:boolean"
   )

   for check in "${COMPLIANCE_CHECKS[@]}"; do
     IFS=':' read key requirement <<< "$check"
     value=$(yt config get "$key")

     if [ "$requirement" = "required" ] && [ -z "$value" ]; then
       echo "❌ $key: Missing (required)"
     else
       echo "✅ $key: $value"
     fi
   done

See Also
--------

* :doc:`auth` - Authentication configuration and token management
* :doc:`projects` - Project-specific configuration settings
* :doc:`users` - User preferences and default assignments
* :doc:`time` - Time tracking configuration and defaults
* :doc:`admin` - Administrative configuration options
