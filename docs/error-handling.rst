Error Handling
==============

The YouTrack CLI provides standardized error formatting across all commands with support for both interactive and automation use cases.

Error Format
------------

Standard Error Format
~~~~~~~~~~~~~~~~~~~~~~

In normal mode, errors are displayed with clear visual indicators::

    ❌ Authentication failed [AUTH_001]
    Details: Invalid token format

Quiet Mode Format
~~~~~~~~~~~~~~~~~

In quiet mode (``--quiet`` or ``-q``), errors are displayed in a format suitable for automation::

    AUTH_001: Authentication failed

Error Codes
-----------

The CLI uses a standardized error code system for programmatic handling:

Authentication Errors (AUTH_xxx)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* ``AUTH_001`` - Authentication failed
* ``AUTH_002`` - Authentication expired
* ``AUTH_003`` - Invalid token format
* ``AUTH_004`` - No authentication credentials found

Network Errors (NET_xxx)
~~~~~~~~~~~~~~~~~~~~~~~~~

* ``NET_001`` - Connection failed
* ``NET_002`` - Request timeout
* ``NET_003`` - SSL/TLS error
* ``NET_004`` - DNS resolution error

Validation Errors (VAL_xxx)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* ``VAL_001`` - Invalid input format
* ``VAL_002`` - Missing required field
* ``VAL_003`` - Format validation error
* ``VAL_004`` - Value out of range

Permission Errors (PERM_xxx)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* ``PERM_001`` - Access denied
* ``PERM_002`` - Insufficient privileges
* ``PERM_003`` - Resource forbidden

Configuration Errors (CFG_xxx)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* ``CFG_001`` - Configuration not found
* ``CFG_002`` - Invalid configuration format
* ``CFG_003`` - Configuration save failed
* ``CFG_004`` - Configuration load failed

Resource Errors (RES_xxx)
~~~~~~~~~~~~~~~~~~~~~~~~~~

* ``RES_001`` - Resource not found
* ``RES_002`` - Resource already exists
* ``RES_003`` - Operation failed

System Errors (SYS_xxx)
~~~~~~~~~~~~~~~~~~~~~~~~

* ``SYS_001`` - Internal system error
* ``SYS_002`` - Unsupported operation
* ``SYS_003`` - Filesystem error

Generic Errors (GEN_xxx)
~~~~~~~~~~~~~~~~~~~~~~~~~

* ``GEN_001`` - Unknown error
* ``GEN_002`` - Operation cancelled

Usage Examples
--------------

Interactive Mode
~~~~~~~~~~~~~~~~

For interactive use, run commands normally to see user-friendly error messages::

    $ yt issues list
    ❌ No authentication credentials found [AUTH_004]
    Details: Run 'yt auth login' to authenticate first

Automation Mode
~~~~~~~~~~~~~~~

For automation and scripting, use the ``--quiet`` flag::

    $ yt --quiet issues list
    AUTH_004: No authentication credentials found

Error Handling in Scripts
~~~~~~~~~~~~~~~~~~~~~~~~~~

Parse error codes programmatically::

    #!/bin/bash
    output=$(yt --quiet issues list 2>&1)
    if [[ $? -ne 0 ]]; then
        error_code=$(echo "$output" | cut -d':' -f1)
        case $error_code in
            "AUTH_004")
                echo "Need to authenticate first"
                yt auth login
                ;;
            "NET_001")
                echo "Connection failed, check network"
                ;;
            *)
                echo "Unknown error: $output"
                ;;
        esac
    fi

Global Options
--------------

Quiet Mode
~~~~~~~~~~

Enable quiet mode for automation-friendly output::

    yt --quiet <command>
    yt -q <command>

Quiet mode:

* Removes emojis and styling
* Uses plain text format
* Provides error codes for programmatic handling
* Cannot be used with ``--verbose``

Verbose Mode
~~~~~~~~~~~~

Enable verbose mode for detailed output::

    yt --verbose <command>
    yt -v <command>

Verbose mode:

* Shows detailed error information
* Includes additional context
* Cannot be used with ``--quiet``

Developer Guide
---------------

Using Standardized Errors
~~~~~~~~~~~~~~~~~~~~~~~~~~

When developing commands, use the standardized error system::

    from youtrack_cli.error_formatting import CommonErrors, format_and_print_error

    # Use common error patterns
    format_and_print_error(CommonErrors.authentication_failed(details="Token expired"))

    # Create custom errors
    from youtrack_cli.error_formatting import StandardizedError, ErrorCode

    error = StandardizedError(
        code=ErrorCode.VAL_INVALID_INPUT,
        message="Invalid project ID format",
        details="Project ID must match pattern: [A-Z]{2,}-\\d+"
    )
    format_and_print_error(error)

Error Severity Levels
~~~~~~~~~~~~~~~~~~~~~

Errors support different severity levels::

    from youtrack_cli.error_formatting import ErrorSeverity

    # Warning level
    warning = StandardizedError(
        code=ErrorCode.CFG_INVALID_FORMAT,
        message="Deprecated configuration format",
        severity=ErrorSeverity.WARNING
    )

    # Error level (default)
    error = StandardizedError(
        code=ErrorCode.AUTH_FAILED,
        message="Authentication failed"
    )

Migration Guide
---------------

Legacy Error Patterns
~~~~~~~~~~~~~~~~~~~~~~

Old error patterns::

    console.print(f"❌ Authentication failed: {error}", style="red")

New standardized patterns::

    format_and_print_error(CommonErrors.authentication_failed(details=error))

Backward Compatibility
~~~~~~~~~~~~~~~~~~~~~~~

The system provides backward compatibility through legacy functions::

    from youtrack_cli.error_formatting import print_legacy_error

    # This works but should be migrated
    print_legacy_error("Operation failed")
