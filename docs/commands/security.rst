Security Command Group
======================

The ``yt security`` command group provides comprehensive security and audit management capabilities for YouTrack CLI. This command group offers essential security operations including audit log management, token status monitoring, and security maintenance functions.

.. contents:: Table of Contents
   :local:
   :depth: 2

Overview
--------

The security command group offers complete security management including:

* Viewing and managing command audit logs for compliance tracking
* Monitoring authentication token status and expiration
* Clearing audit logs for maintenance and privacy
* Comprehensive security monitoring and reporting capabilities

Base Command
------------

.. code-block:: bash

   yt security [OPTIONS] COMMAND [ARGS]...

Security Management Commands
----------------------------

View Audit Log
~~~~~~~~~~~~~~

View the command audit log to track CLI usage and security events.

.. code-block:: bash

   yt security audit [OPTIONS]

**Options:**
  * ``-l, --limit INTEGER`` - Number of recent entries to show
  * ``--format [table|json]`` - Output format (default: table)

**Examples:**

.. code-block:: bash

   # View recent audit log entries
   yt security audit

   # View last 100 audit entries
   yt security audit --limit 100

   # Export audit log in JSON format for analysis
   yt security audit --format json

   # Get detailed audit information
   yt security audit -l 50 --format json

Clear Audit Log
~~~~~~~~~~~~~~~

Clear the command audit log for maintenance purposes or privacy requirements.

.. code-block:: bash

   yt security clear-audit [OPTIONS]

**Examples:**

.. code-block:: bash

   # Clear the audit log (will prompt for confirmation)
   yt security clear-audit

   # Force clear without confirmation (for automation)
   yt security clear-audit --force

.. warning::
   **Data Loss Warning:**

   Clearing the audit log permanently removes all historical command execution records.
   This action cannot be undone. Consider exporting audit data before clearing if
   you need to retain the information for compliance or analysis purposes.

Check Token Status
~~~~~~~~~~~~~~~~~~

Check the status and expiration information of your authentication token.

.. code-block:: bash

   yt security token-status [OPTIONS]

**Examples:**

.. code-block:: bash

   # Check current token status
   yt security token-status

   # Get detailed token information
   yt security token-status --verbose

Security Monitoring
-------------------

Audit Log Analysis
~~~~~~~~~~~~~~~~~~

The audit log contains comprehensive security and usage information:

**Tracked Information:**
  * Command execution history with timestamps
  * User authentication events and token usage
  * Success/failure status for all operations
  * System and environment context information
  * API calls and data access patterns

**Security Events:**
  * Failed authentication attempts
  * Privilege escalation attempts
  * Unusual command patterns or frequency
  * Access to sensitive data or administrative functions

Token Management
~~~~~~~~~~~~~~~~

Authentication token monitoring helps ensure security:

**Token Information:**
  * Current token validity and expiration status
  * Token permissions and scope limitations
  * Last authentication time and renewal requirements
  * Security flags and enhanced security mode status

**Token Security:**
  * Automatic token expiration monitoring
  * Secure token storage and access controls
  * Token renewal notifications and requirements
  * Enhanced security mode for sensitive environments

Compliance and Governance
--------------------------

Audit Trail Maintenance
~~~~~~~~~~~~~~~~~~~~~~~

Maintain comprehensive audit trails for compliance requirements:

.. code-block:: bash

   # Daily audit export for compliance
   yt security audit --format json --limit 10000 > audit-$(date +%Y%m%d).json

   # Weekly security summary
   yt security audit --format json | jq 'group_by(.date) | map({date: .[0].date, commands: length})'

   # Failed operation analysis
   yt security audit --format json | jq '.[] | select(.status != "Success")'

Regular Security Checks
~~~~~~~~~~~~~~~~~~~~~~~~

Implement regular security monitoring routines:

.. code-block:: bash

   # Check token expiration weekly
   yt security token-status

   # Monitor for authentication issues
   yt security audit --format json | jq '.[] | select(.command | contains("auth")) | select(.status == "Failed")'

   # Review administrative command usage
   yt security audit --format json | jq '.[] | select(.command | contains("admin"))'

Data Protection and Privacy
----------------------------

Sensitive Data Handling
~~~~~~~~~~~~~~~~~~~~~~~

The security subsystem handles sensitive data with care:

* **Local Storage:** All audit data is stored locally with appropriate file permissions
* **No Transmission:** Audit logs are never transmitted to external servers
* **Access Control:** Audit data access is restricted to authenticated users
* **Secure Cleanup:** Audit log clearing includes secure data deletion

Privacy Considerations
~~~~~~~~~~~~~~~~~~~~~~

When using audit logs, consider privacy implications:

* **User Privacy:** Audit logs may contain user-specific command arguments
* **Data Sensitivity:** Command arguments might include sensitive project or user information
* **Retention Policies:** Implement appropriate data retention and cleanup schedules
* **Access Restrictions:** Limit audit log access to authorized personnel only

Integration with Other Commands
-------------------------------

Flat Command Alternatives
~~~~~~~~~~~~~~~~~~~~~~~~~

Some security operations have convenient flat command alternatives:

.. code-block:: bash

   # These commands are functionally identical:
   yt security audit --limit 50
   yt audit --limit 50

   # Use the style that fits your workflow
   yt security audit --format json    # Full command path
   yt audit --format json             # Shorter alternative

Authentication Integration
~~~~~~~~~~~~~~~~~~~~~~~~~~

Security commands work seamlessly with authentication:

.. code-block:: bash

   # Check authentication status
   yt auth status

   # Review token details
   yt security token-status

   # Monitor authentication events
   yt security audit --format json | jq '.[] | select(.command | contains("auth"))'

Automation and Scripting
-------------------------

Security Monitoring Scripts
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Automate security monitoring with shell scripts:

.. code-block:: bash

   #!/bin/bash
   # Security monitoring script

   echo "=== Daily Security Check ==="
   echo "Token Status:"
   yt security token-status

   echo -e "\nRecent Failed Commands:"
   yt security audit --format json | jq -r '.[] | select(.status == "Failed") | [.timestamp, .command, .status] | @csv'

   echo -e "\nAdmin Command Usage:"
   ADMIN_COUNT=$(yt security audit --format json | jq '[.[] | select(.command | contains("admin"))] | length')
   echo "Admin commands executed: $ADMIN_COUNT"

Log Rotation and Cleanup
~~~~~~~~~~~~~~~~~~~~~~~~

Implement automated log management:

.. code-block:: bash

   #!/bin/bash
   # Weekly audit log rotation

   # Export current logs
   yt security audit --format json > "audit-backup-$(date +%Y%m%d).json"

   # Clear logs after backup
   if [ -f "audit-backup-$(date +%Y%m%d).json" ]; then
       yt security clear-audit --force
       echo "Audit logs backed up and cleared"
   fi

Best Practices
--------------

**Regular Monitoring:**
  * Review audit logs weekly for security anomalies
  * Monitor token expiration status proactively
  * Set up automated alerts for failed authentication attempts

**Compliance Management:**
  * Export audit logs regularly for compliance requirements
  * Implement data retention policies appropriate for your organization
  * Document security procedures and audit schedules

**Token Security:**
  * Monitor token expiration dates and renew proactively
  * Use enhanced security mode in sensitive environments
  * Rotate tokens regularly according to security policies

**Data Protection:**
  * Secure audit log backups with appropriate encryption
  * Limit access to audit logs to authorized personnel
  * Clear logs regularly to minimize exposure of sensitive data

Troubleshooting
---------------

Common Issues
~~~~~~~~~~~~~

**Audit Log Access Issues:**
  * Verify authentication status: ``yt auth status``
  * Check file permissions on audit log storage directory
  * Ensure sufficient disk space for audit log operations

**Token Status Problems:**
  * Confirm network connectivity to YouTrack instance
  * Verify token has not expired: ``yt security token-status``
  * Re-authenticate if token is invalid: ``yt auth login``

**Performance Issues:**
  * Large audit logs may slow down operations - consider regular cleanup
  * Use ``--limit`` parameter to restrict output size for better performance
  * Export data in JSON format for more efficient processing

Authentication
--------------

All security commands require proper authentication. Ensure you're logged in:

.. code-block:: bash

   yt auth login

See Also
--------

* :doc:`audit` - Quick access to audit log viewing
* :doc:`auth` - Authentication and login management
* :doc:`config` - CLI configuration and security settings
* :doc:`admin` - Administrative operations and security controls
