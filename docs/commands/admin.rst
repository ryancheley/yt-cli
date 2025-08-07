Administrative Command Group
==============================

The ``yt admin`` command group provides comprehensive administrative capabilities for YouTrack system management. These commands require administrative privileges and handle system-wide settings, maintenance, and user management.

.. contents:: Table of Contents
   :local:
   :depth: 2

Overview
--------

YouTrack administrative operations manage system-wide configurations, user groups, custom fields, and system maintenance. The admin command group allows you to:

* Manage global YouTrack settings and configuration
* Handle license information and usage monitoring
* Perform system maintenance operations
* Manage user groups and permissions
* Configure custom fields across projects
* Monitor system health and diagnostics

.. warning::
   Administrative commands require YouTrack administrator privileges. Users without sufficient permissions will receive appropriate error messages.

Base Command
------------

.. code-block:: bash

   yt admin [OPTIONS] COMMAND [ARGS]...

Global Settings Management
--------------------------

.. note::
   The global-settings commands have been deprecated and are no longer available.
   Use the global-settings list command to view settings.

global-settings list
~~~~~~~~~~~~~~~~~~~~

List all global YouTrack settings.

.. code-block:: bash

   yt admin global-settings list

**Examples:**

.. code-block:: bash

   # List all global settings
   yt admin global-settings list

License Management
-----------------

.. note::
   The license show command has been deprecated and is no longer available.

license usage
~~~~~~~~~~~~

Show detailed license usage statistics and capacity information.

.. code-block:: bash

   yt admin license usage

**Examples:**

.. code-block:: bash

   # Show license usage statistics
   yt admin license usage

   # Monitor license utilization
   yt admin license usage

System Maintenance
------------------

maintenance
~~~~~~~~~~~

Perform system maintenance operations and administrative tasks.

.. code-block:: bash

   yt admin maintenance [OPTIONS] COMMAND [ARGS]...

**Description:**

The maintenance command group provides access to system maintenance operations and administrative utilities for YouTrack instances. This command serves as an entry point for various maintenance tasks that may be available depending on your YouTrack version and configuration.

**Examples:**

.. code-block:: bash

   # Access maintenance operations
   yt admin maintenance

   # View available maintenance commands
   yt admin maintenance --help

.. note::
   Specific maintenance operations may vary depending on your YouTrack version and configuration. Use ``yt admin maintenance --help`` to see all available maintenance commands.

.. note::
   The maintenance clear-cache command has been deprecated and is no longer available.
   Cache management must be performed through:

   * The YouTrack administrative UI
   * Server restart procedures
   * Direct server access

   Please consult your YouTrack administrator or the JetBrains support team for cache management.

System Health Monitoring
------------------------

health check
~~~~~~~~~~~

Run comprehensive system health diagnostics and display system status.

.. code-block:: bash

   yt admin health check

**Examples:**

.. code-block:: bash

   # Run health diagnostics
   yt admin health check

   # Regular system health monitoring
   yt admin health check

   # Pre-maintenance health check
   yt admin health check

User Groups Management
---------------------

user-groups list
~~~~~~~~~~~~~~~

List all user groups in the YouTrack system with filtering options.

.. code-block:: bash

   yt admin user-groups list [OPTIONS]

**Options:**

.. list-table::
   :widths: 20 20 60
   :header-rows: 1

   * - Option
     - Type
     - Description
   * - ``--fields, -f``
     - string
     - Comma-separated list of fields to return

**Examples:**

.. code-block:: bash

   # List all user groups
   yt admin user-groups list

   # List groups with specific fields
   yt admin user-groups list --fields "id,name,description,users(login)"

   # List groups with user information
   yt admin user-groups list --fields "id,name,description,users(fullName)"

user-groups create
~~~~~~~~~~~~~~~~~

Create a new user group with specified settings.

.. code-block:: bash

   yt admin user-groups create NAME [OPTIONS]

**Arguments:**

* ``NAME`` - The name of the new user group (required)

**Options:**

.. list-table::
   :widths: 20 20 60
   :header-rows: 1

   * - Option
     - Type
     - Description
   * - ``--description, -d``
     - string
     - Group description

**Examples:**

.. code-block:: bash

   # Create a basic user group
   yt admin user-groups create "DevOps Team"

   # Create a group with description
   yt admin user-groups create "QA Team" --description "Quality Assurance Team"

   # Create project-specific groups
   yt admin user-groups create "Project Alpha Team" --description "Alpha project development team"

Custom Fields Management
------------------------

fields list
~~~~~~~~~~

List all custom fields configured across YouTrack projects.

.. code-block:: bash

   yt admin fields list [OPTIONS]

**Options:**

.. list-table::
   :widths: 20 20 60
   :header-rows: 1

   * - Option
     - Type
     - Description
   * - ``--fields, -f``
     - string
     - Comma-separated list of fields to return

**Examples:**

.. code-block:: bash

   # List all custom fields
   yt admin fields list

   # List fields with specific information
   yt admin fields list --fields "id,name,fieldType(presentation),isPrivate"

   # List field types and usage
   yt admin fields list --fields "name,fieldType(presentation),projects(name)"

Internationalization (i18n) Management
--------------------------------------

i18n list
~~~~~~~~~

List available locales for internationalization. This command is an alias for ``yt admin locale list``.

.. code-block:: bash

   yt admin i18n list

**Examples:**

.. code-block:: bash

   # List all available locales
   yt admin i18n list

   # Same functionality as locale list
   yt admin locale list

.. note::
   This command provides the same functionality as ``yt admin locale list`` for consistency with other i18n commands.

Administrative Features
----------------------

Global Settings
~~~~~~~~~~~~~~

**System Configuration**
  Manage server-wide settings including performance, security, and feature configurations.

**Authentication Settings**
  Configure authentication methods, session timeouts, and security policies.

**Email Configuration**
  Set up email servers, notification templates, and delivery settings.

**Performance Tuning**
  Adjust system performance parameters and resource limits.

License Management
~~~~~~~~~~~~~~~~~

**License Information**
  View license details including expiration dates, feature limits, and user capacity.

**Usage Monitoring**
  Track license utilization and capacity planning.

**Compliance Tracking**
  Monitor license compliance and usage patterns.

System Maintenance
~~~~~~~~~~~~~~~~~

**Cache Management**
  Note: Cache clearing is not available through the REST API. Use the YouTrack administrative UI or server-side tools for cache management.

**Health Monitoring**
  Comprehensive system health checks and diagnostics.

**Performance Optimization**
  Tools for system performance analysis and optimization.

User and Group Management
~~~~~~~~~~~~~~~~~~~~~~~~

**User Groups**
  Create and manage user groups for permission and access control.

**Permission Management**
  Configure group-based permissions and access rights.

**Organizational Structure**
  Set up user groups that reflect organizational hierarchy.

Custom Fields
~~~~~~~~~~~~

**Field Management**
  View and manage custom fields across all projects.

**Field Configuration**
  Monitor field usage and configuration across the system.

**Data Consistency**
  Ensure custom field consistency across projects.

Common Administrative Workflows
------------------------------

System Health Monitoring
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Daily health check routine
   echo "=== Daily YouTrack Health Check ==="
   echo "Date: $(date)"
   echo ""

   # Check system health
   yt admin health check

   # Check license status
   echo ""
   echo "=== License Status ==="
   yt admin license usage

   # Check license usage
   echo ""
   echo "=== License Usage ==="
   yt admin license usage

Regular Maintenance
~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Weekly maintenance routine
   echo "=== Weekly YouTrack Maintenance ==="

   # Note: Cache clearing is not available through the REST API
   echo "Cache clearing must be done through the YouTrack UI or server tools"
   # Cache clearing commands have been deprecated

   # Health check after maintenance
   echo "Post-maintenance health check..."
   yt admin health check

   echo "Maintenance completed at $(date)"

User Group Management
~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Set up new project team
   PROJECT_NAME="Alpha"

   # Create project-specific groups
   yt admin user-groups create "${PROJECT_NAME} Developers" \
     --description "Development team for ${PROJECT_NAME} project"

   yt admin user-groups create "${PROJECT_NAME} Testers" \
     --description "QA team for ${PROJECT_NAME} project"

   yt admin user-groups create "${PROJECT_NAME} Managers" \
     --description "Project managers for ${PROJECT_NAME} project"

   # List created groups
   yt admin user-groups list --fields "name,description"

System Configuration
~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Configure system settings for new installation
   echo "Configuring YouTrack system settings..."

   # Note: Global settings configuration commands have been deprecated
   echo "System settings must be configured through the YouTrack web interface"

   # Verify configuration
   echo "Verifying configuration..."
   yt admin global-settings list

License Monitoring
~~~~~~~~~~~~~~~~~

.. code-block:: bash

   #!/bin/bash
   # License monitoring and alerting script

   echo "=== License Monitoring Report ==="
   echo "Generated: $(date)"
   echo ""

   # Get license information
   USAGE_INFO=$(yt admin license usage)

   echo "$USAGE_INFO"

   # Alert if usage is high (example threshold: 80%)
   # This would need proper parsing of the actual output format
   echo ""
   echo "=== Usage Analysis ==="
   echo "License monitoring completed"

Best Practices
--------------

1. **Regular Monitoring**: Perform regular health checks and license monitoring.

2. **Maintenance Scheduling**: Schedule maintenance operations during low-usage periods.

3. **Permission Management**: Use groups for permission management rather than individual assignments.

4. **Documentation**: Document all administrative changes and configurations.

5. **Backup Before Changes**: Always backup configurations before making changes.

6. **Testing**: Test administrative changes in non-production environments first.

7. **Monitoring**: Set up monitoring for license usage and system health.

8. **Security**: Follow security best practices for administrative access.

9. **Change Management**: Use proper change management processes for system modifications.

10. **Capacity Planning**: Monitor usage trends for capacity planning and license management.

Security Considerations
----------------------

Administrative Access
~~~~~~~~~~~~~~~~~~~~

* **Limited Access**: Restrict administrative access to authorized personnel only
* **Audit Trail**: Maintain audit logs of administrative actions
* **Role Separation**: Separate development and administrative responsibilities
* **Regular Review**: Regularly review and update administrative permissions

System Security
~~~~~~~~~~~~~~

* **Setting Validation**: Validate all configuration changes for security implications
* **Secure Defaults**: Use secure default values for system settings
* **Regular Updates**: Keep system configurations current with security best practices
* **Access Monitoring**: Monitor administrative access and actions

Troubleshooting
--------------

Common Issues and Solutions
~~~~~~~~~~~~~~~~~~~~~~~~~

**Permission Denied Errors**
  Verify administrative privileges and check authentication status.

**Setting Not Found**
  Check setting key spelling and availability in your YouTrack version.

**Cache Clear Not Available**
  The clear-cache command returns an error explaining that cache clearing is not available through the YouTrack REST API. Use the administrative UI or server-side tools instead.

**Group Creation Failures**
  Check for naming conflicts and permission requirements.

**Health Check Issues**
  Review system logs and resource availability.

**Health Check 404 Errors**
  If the health check command returns a 404 error, this may indicate:

  * Your YouTrack version doesn't support the system settings endpoint
  * The API endpoint has changed in your YouTrack version
  * Your YouTrack instance has a different API configuration

  The command will automatically try fallback endpoints and provide specific guidance based on the error type.

System Diagnostics
~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Administrative troubleshooting workflow
   echo "=== YouTrack Administrative Diagnostics ==="

   # Check authentication and permissions
   echo "1. Authentication check..."
   if yt admin health check > /dev/null 2>&1; then
     echo "✅ Administrative access verified"
   else
     echo "❌ Administrative access failed"
     exit 1
   fi

   # Check system health
   echo "2. System health check..."
   yt admin health check

   # Check license status
   echo "3. License status..."
   yt admin license usage

   echo "Diagnostics completed"

Error Recovery
~~~~~~~~~~~~~

.. code-block:: bash

   # Error recovery procedures
   echo "=== Administrative Error Recovery ==="

   # Note: Cache clearing is not available through the REST API
   echo "Cache management must be done through YouTrack UI or server tools"
   # Manual intervention required for cache clearing

   # Verify system health after recovery
   echo "Verifying system health..."
   yt admin health check

   # Check critical settings
   echo "Verifying critical settings..."
   yt admin global-settings list

Integration Examples
-------------------

Monitoring Integration
~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   #!/bin/bash
   # Integration with monitoring systems

   # Health check for monitoring system
   if yt admin health check > /dev/null 2>&1; then
     echo "youtrack_health_status 1"
   else
     echo "youtrack_health_status 0"
   fi

   # License usage metrics
   # This would need proper parsing of actual output
   echo "youtrack_license_usage_percent 75"

Backup Integration
~~~~~~~~~~~~~~~~

.. code-block:: bash

   #!/bin/bash
   # Backup administrative configurations

   BACKUP_DIR="/backup/youtrack/$(date +%Y%m%d)"
   mkdir -p "$BACKUP_DIR"

   # Export global settings
   yt admin global-settings list > "$BACKUP_DIR/global_settings.txt"

   # Export user groups
   yt admin user-groups list --fields "id,name,description" > "$BACKUP_DIR/user_groups.txt"

   # Export custom fields
   yt admin fields list > "$BACKUP_DIR/custom_fields.txt"

   echo "Administrative backup completed: $BACKUP_DIR"

Automation Scripts
~~~~~~~~~~~~~~~~~

.. code-block:: bash

   #!/bin/bash
   # Automated administrative maintenance

   LOG_FILE="/var/log/youtrack_admin.log"

   log() {
     echo "$(date): $1" | tee -a "$LOG_FILE"
   }

   log "Starting automated maintenance"

   # Note: Cache clearing is not available through the REST API
   log "Cache clearing must be done through YouTrack UI or server tools"
   # Manual cache management required

   # Health check
   log "Running health check"
   if yt admin health check > /dev/null 2>&1; then
     log "Health check passed"
   else
     log "Health check failed - alerting administrators"
     # Send alert to administrators
   fi

   log "Automated maintenance completed"

Limitations
-----------

* Some administrative operations may require web interface access
* Complex permission configurations may not be fully exposed via CLI
* Advanced system configurations may require direct database access
* Certain maintenance operations may require system restart

See Also
--------

* :doc:`auth` - Authentication and credential management
* :doc:`users` - User management and group membership
* :doc:`projects` - Project administration and configuration
* :doc:`config` - CLI configuration and environment management
* YouTrack Administration Guide for advanced system management
