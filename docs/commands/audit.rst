Audit Command
=============

The ``yt audit`` command provides quick access to command audit log viewing functionality. This is a flatter alternative to ``yt security audit`` that offers the same audit log capabilities in a more convenient format.

.. contents:: Table of Contents
   :local:
   :depth: 2

Overview
--------

The audit command allows you to:

* View recent command execution history and audit trail
* Monitor CLI usage patterns and security events
* Track command execution for compliance and debugging purposes
* Export audit data in multiple formats for analysis

Base Command
------------

.. code-block:: bash

   yt audit [OPTIONS]

Command Options
---------------

**Options:**
  * ``-l, --limit INTEGER`` - Number of recent audit entries to show
  * ``--format [table|json]`` - Output format (default: table)

**Examples:**

.. code-block:: bash

   # View recent audit log entries (default limit)
   yt audit

   # View last 50 audit entries
   yt audit --limit 50

   # Export audit log in JSON format
   yt audit --format json

   # View recent entries with custom limit
   yt audit -l 100

Understanding Audit Logs
-------------------------

Audit Information Tracked
~~~~~~~~~~~~~~~~~~~~~~~~~

The audit log captures comprehensive information about CLI usage:

* **Command execution** - Full command text and arguments
* **Timestamps** - Precise execution time for each command
* **User context** - Authentication information and user identity
* **Execution results** - Success/failure status and error information
* **System context** - Environment and configuration details

Log Entry Format
~~~~~~~~~~~~~~~~

Each audit log entry typically includes:

.. code-block:: text

   Timestamp    | User      | Command                    | Status
   2024-01-15   | john.doe  | yt issues list --assignee | Success
   2024-01-15   | john.doe  | yt projects list           | Success
   2024-01-15   | admin     | yt users create newuser    | Failed

Output Formats
--------------

Table Format
~~~~~~~~~~~~

The default table format provides a human-readable view:

.. code-block:: bash

   yt audit --limit 10

Displays results in a formatted table with columns for easy scanning.

JSON Format
~~~~~~~~~~~

JSON format is ideal for programmatic processing:

.. code-block:: bash

   yt audit --format json --limit 100

Returns structured data suitable for:

* Log aggregation systems
* Automated analysis and reporting
* Integration with monitoring tools
* Custom data processing scripts

Use Cases
---------

Security Monitoring
~~~~~~~~~~~~~~~~~~~

Track usage patterns and identify potential security issues:

.. code-block:: bash

   # Monitor recent high-privilege operations
   yt audit --limit 200 --format json | jq '.[] | select(.command | contains("admin"))'

   # Check for failed authentication attempts
   yt audit --format json | jq '.[] | select(.status == "Failed")'

Compliance Auditing
~~~~~~~~~~~~~~~~~~~

Generate reports for compliance and governance:

.. code-block:: bash

   # Daily audit report
   yt audit --limit 1000 --format json > daily-audit-$(date +%Y%m%d).json

   # User activity tracking
   yt audit --format json | jq 'group_by(.user) | map({user: .[0].user, count: length})'

Troubleshooting
~~~~~~~~~~~~~~~

Debug issues and trace command execution:

.. code-block:: bash

   # Find recent failed commands
   yt audit --format json | jq '.[] | select(.status != "Success")'

   # Trace specific command usage
   yt audit --format table | grep "issues create"

Performance Analysis
~~~~~~~~~~~~~~~~~~~~

Analyze CLI usage patterns for optimization:

.. code-block:: bash

   # Most frequently used commands
   yt audit --format json | jq '.[] | .command' | sort | uniq -c | sort -nr

   # Command execution timing analysis
   yt audit --format json | jq '.[] | {command, duration, timestamp}'

Integration with Security Command
----------------------------------

The ``yt audit`` command is functionally identical to ``yt security audit``. Both commands provide the same audit log viewing capabilities:

.. code-block:: bash

   # These commands are equivalent:
   yt audit --limit 50 --format json
   yt security audit --limit 50 --format json

Choose the command style that fits your workflow:

* Use ``yt audit`` for quick, direct access to audit logs
* Use ``yt security audit`` when working with other security-related operations

Data Retention and Privacy
---------------------------

**Log Retention:**
  * Audit logs are stored locally on your system
  * Log retention follows your local system policies
  * No audit data is transmitted to external servers

**Privacy Considerations:**
  * Audit logs may contain sensitive command arguments
  * Logs are stored in your local CLI configuration directory
  * Access is restricted to your user account permissions

Best Practices
--------------

**Regular Monitoring:**
  * Review audit logs regularly for unusual activity
  * Set up automated monitoring for critical environments
  * Export logs for long-term retention and analysis

**Security Analysis:**
  * Monitor for unauthorized access attempts
  * Track usage of administrative commands
  * Identify patterns that may indicate security issues

**Performance Optimization:**
  * Use audit data to identify frequently used commands for alias creation
  * Analyze command patterns to optimize workflows
  * Monitor for performance-impacting operations

Automation and Scripting
-------------------------

**Shell Integration:**

.. code-block:: bash

   #!/bin/bash
   # Daily security check script

   # Check for failed commands in last 24 hours
   FAILED_COUNT=$(yt audit --format json | jq '[.[] | select(.status != "Success")] | length')

   if [ "$FAILED_COUNT" -gt 5 ]; then
       echo "Warning: $FAILED_COUNT failed commands detected"
       yt audit --format table | grep Failed
   fi

**Log Processing:**

.. code-block:: bash

   # Export weekly audit report
   yt audit --format json --limit 10000 | \
     jq 'map(select(.timestamp | strptime("%Y-%m-%d") | mktime > (now - 604800)))' | \
     jq -r '["Date", "User", "Command", "Status"], (.[] | [.timestamp, .user, .command, .status]) | @csv' \
     > weekly-audit.csv

Authentication
--------------

Audit log access requires authentication. Make sure you're logged in:

.. code-block:: bash

   yt auth login

Error Handling
--------------

The CLI provides detailed error messages for common audit issues:

* **Authentication errors** - Ensure you're logged in with appropriate permissions
* **Log access errors** - Check file permissions and disk space
* **Format errors** - Verify output format specifications are correct
* **Limit errors** - Ensure limit values are within acceptable ranges

See Also
--------

* :doc:`security` - Complete security and audit management
* :doc:`config` - CLI configuration and logging settings
* :doc:`auth` - Authentication and user management
