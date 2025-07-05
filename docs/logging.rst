Logging and Debugging
=====================

YouTrack CLI features a comprehensive logging system built with `structlog <https://www.structlog.org/>`_ and
`rich <https://github.com/Textualize/rich>`_ to help with debugging, monitoring, and troubleshooting operations.

Overview
--------

The logging system provides:

- **Structured logging** with contextual information
- **Multiple log levels** for different verbosity needs
- **File-based logging** with automatic rotation
- **Console logging** with rich formatting
- **Sensitive data masking** for security
- **API call tracking** with performance metrics

Log Levels
----------

Control the verbosity of output using these options:

Basic Options
~~~~~~~~~~~~~

.. code-block:: bash

   # Basic verbose output (INFO level)
   yt --verbose issues list

   # Debug output with detailed information
   yt --debug issues list

Advanced Level Control
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Set specific log level
   yt --log-level ERROR issues list
   yt --log-level DEBUG issues list

   # Available levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
   yt --log-level INFO --verbose projects list

Log Level Details
~~~~~~~~~~~~~~~~~

- **DEBUG**: Detailed information, typically only useful for diagnosing problems
- **INFO**: General information about what the program is doing
- **WARNING**: Something unexpected happened, but the software is still working
- **ERROR**: A serious problem occurred, the software was unable to perform a function
- **CRITICAL**: A very serious error occurred, the program may be unable to continue

Log Files
---------

By default, logs are written to both console and file for comprehensive debugging support.

Default Locations
~~~~~~~~~~~~~~~~~

- **Linux/macOS**: ``~/.local/share/youtrack-cli/youtrack-cli.log``
- **Windows**: ``%LOCALAPPDATA%\\youtrack-cli\\youtrack-cli.log``
- **Custom location**: Set ``XDG_DATA_HOME`` environment variable

File Management Options
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Disable file logging (console only)
   yt --no-log-file issues list

   # View current log file location
   yt config get log-file-path

Log File Features
~~~~~~~~~~~~~~~~~

- **Automatic rotation**: Logs rotate when they reach 10MB
- **Backup retention**: Keeps 5 backup files (50MB total)
- **Structured format**: JSON-like structured data with timestamps
- **Cross-session persistence**: Logs persist across CLI sessions

Sensitive Data Protection
-------------------------

The logging system automatically masks sensitive information to protect security:

Automatic Masking
~~~~~~~~~~~~~~~~~

The following patterns are automatically masked in all logs:

- API tokens: ``token=***MASKED***``
- Passwords: ``password=***MASKED***``
- API keys: ``api_key=***MASKED***``
- Authorization headers: ``Authorization: Bearer ***MASKED***``
- Bearer tokens in URLs

Example Protected Output
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

   Original: "Making request to https://youtrack.example.com/api?token=abc123xyz"
   Logged:   "Making request to https://youtrack.example.com/api?token=***MASKED***"

Debugging Common Issues
-----------------------

API Connectivity Problems
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Enable debug logging for detailed API calls
   yt --debug auth login

   # Monitor all API requests and responses
   yt --debug --log-level DEBUG issues list

   # Focus only on errors
   yt --log-level ERROR issues list

Authentication Issues
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Debug authentication flow
   yt --debug auth login

   # Verify token validity with verbose output
   yt --verbose auth token --show

Performance Issues
~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Monitor API response times
   yt --debug --log-level DEBUG issues list

   # Track slow operations
   yt --debug time log ISSUE-123 "2h"

Network Connectivity
~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Debug network issues with full detail
   yt --debug --log-level DEBUG projects list

   # Monitor retry attempts
   yt --verbose issues list

Log Output Examples
-------------------

Console Output
~~~~~~~~~~~~~~

With ``--verbose`` flag:

.. code-block:: text

   [10:30:15] INFO     Starting operation                operation=list_issues project=TEST
   [10:30:15] INFO     API call completed               method=GET status_code=200 duration_ms=245.5

With ``--debug`` flag:

.. code-block:: text

   [10:30:15] DEBUG    Making API request               method=GET url=https://youtrack.example.com/api/issues attempt=1
   [10:30:15] DEBUG    API call completed               method=GET status_code=200 duration_ms=245.5
   [10:30:15] DEBUG    Request successful               status_code=200

File Output
~~~~~~~~~~~

Log files contain structured JSON-like entries:

.. code-block:: text

   2024-07-05 10:30:15 - youtrack_cli.api - DEBUG - API call completed {
     "method": "GET",
     "url": "https://youtrack.example.com/api/issues?token=***MASKED***",
     "status_code": 200,
     "duration_ms": 245.5,
     "attempt": 1
   }

Error Logging
~~~~~~~~~~~~~

Errors include contextual information:

.. code-block:: text

   2024-07-05 10:30:15 - youtrack_cli.operations - ERROR - YouTrack operation failed {
     "operation": "create_issue",
     "error_type": "AuthenticationError",
     "message": "Invalid credentials or token expired",
     "url": "https://youtrack.example.com/api/issues"
   }

Structured Logging for Developers
----------------------------------

The CLI uses structured logging throughout for better debugging and monitoring.

Operation Tracking
~~~~~~~~~~~~~~~~~~

High-level operations are logged with context:

.. code-block:: python

   from youtrack_cli.logging import log_operation

   log_operation("create_issue", project="TEST", issue_type="Bug", user="john.doe")

API Call Tracking
~~~~~~~~~~~~~~~~~

All API calls are automatically logged with performance metrics:

.. code-block:: python

   from youtrack_cli.logging import log_api_call

   log_api_call(
       method="POST",
       url="https://youtrack.example.com/api/issues",
       status_code=201,
       duration=0.5,
       issue_id="TEST-123"
   )

Custom Logger Usage
~~~~~~~~~~~~~~~~~~~

For custom logging in extensions or plugins:

.. code-block:: python

   from youtrack_cli.logging import get_logger

   logger = get_logger("my_extension")
   logger.info("Extension operation", action="process_data", count=42)

Configuration
-------------

Environment Variables
~~~~~~~~~~~~~~~~~~~~~

- ``XDG_DATA_HOME``: Override default log file location
- ``YT_LOG_LEVEL``: Set default log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- ``YT_NO_LOG_FILE``: Disable file logging (set to "1" or "true")

Log Rotation Settings
~~~~~~~~~~~~~~~~~~~~~

Current settings (not user-configurable):

- **Maximum file size**: 10MB per log file
- **Backup count**: 5 files retained
- **Total disk usage**: ~50MB maximum
- **Rotation behavior**: Automatic when size limit reached

Performance Considerations
~~~~~~~~~~~~~~~~~~~~~~~~~~

- **File logging impact**: Minimal performance overhead
- **Debug logging**: May slow operations by 10-20% due to detailed output
- **Console logging**: Rich formatting has minimal impact
- **Log rotation**: Happens automatically in background

Best Practices
--------------

Development and Testing
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Use debug mode during development
   yt --debug config set default-project TEST

   # Monitor API calls for new integrations
   yt --log-level DEBUG --verbose issues create "Test Issue"

Production Usage
~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Use warning level for automated scripts
   yt --log-level WARNING issues list --format json > issues.json

   # Enable info level for monitoring
   yt --log-level INFO time report --format json

Troubleshooting Steps
~~~~~~~~~~~~~~~~~~~~~

1. **Start with verbose mode**: ``yt --verbose <command>``
2. **Enable debug for API issues**: ``yt --debug <command>``
3. **Check log files**: Review ``~/.local/share/youtrack-cli/youtrack-cli.log``
4. **Focus on errors**: ``yt --log-level ERROR <command>``
5. **Report issues**: Include relevant log excerpts when reporting bugs

Integration with External Tools
--------------------------------

Log Aggregation
~~~~~~~~~~~~~~~

The structured JSON format makes logs suitable for aggregation tools:

- **ELK Stack**: Parse JSON logs with Logstash
- **Fluentd**: Direct JSON ingestion
- **Splunk**: Index structured log data
- **Datadog**: Log forwarding and analysis

Monitoring and Alerting
~~~~~~~~~~~~~~~~~~~~~~~

Set up alerts based on log patterns:

- **Error rates**: Monitor ERROR and CRITICAL level messages
- **API performance**: Track ``duration_ms`` fields
- **Authentication failures**: Alert on ``AuthenticationError`` events
- **Rate limiting**: Monitor ``RateLimitError`` occurrences

See Also
--------

- :doc:`troubleshooting` - General troubleshooting guide
- :doc:`configuration` - CLI configuration options
- :doc:`development` - Development and debugging guide
