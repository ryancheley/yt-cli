Alias Command Group
===================

The ``yt alias`` command group provides command alias management capabilities for YouTrack CLI. This feature allows you to create custom shortcuts for frequently used commands, improving your productivity by reducing repetitive typing.

.. contents:: Table of Contents
   :local:
   :depth: 2

Overview
--------

The alias command group offers complete alias lifecycle management including:

* Creating custom command shortcuts for frequently used operations
* Deleting user-defined aliases when no longer needed
* Listing all available aliases (both built-in and user-defined)
* Showing what command an alias maps to for verification

Base Command
------------

.. code-block:: bash

   yt alias [OPTIONS] COMMAND [ARGS]...

Alias Management Commands
-------------------------

Create Aliases
~~~~~~~~~~~~~~

Create a new user-defined alias for a command.

.. code-block:: bash

   yt alias create NAME COMMAND

**Arguments:**
  * ``NAME`` - The name of the alias to create
  * ``COMMAND`` - The full command that the alias should execute

**Examples:**

.. code-block:: bash

   # Create an alias for listing your assigned issues
   yt alias create myissues "issues list --assignee me"

   # Create an alias for creating bugs quickly
   yt alias create bug "issues create --type Bug"

   # Create a shorter alias for listing issues
   yt alias create il "issues list"

   # Create complex aliases with multiple options
   yt alias create openbugs "issues list --type Bug --state Open --format table"

List Aliases
~~~~~~~~~~~~

List all available command aliases, including both built-in and user-defined aliases.

.. code-block:: bash

   yt alias list [OPTIONS]

**Examples:**

.. code-block:: bash

   # List all available aliases
   yt alias list

Show Alias Definition
~~~~~~~~~~~~~~~~~~~~~

Show what command an alias maps to for verification purposes.

.. code-block:: bash

   yt alias show ALIAS_NAME

**Arguments:**
  * ``ALIAS_NAME`` - The name of the alias to inspect

**Examples:**

.. code-block:: bash

   # Show what the 'myissues' alias does
   yt alias show myissues

   # Verify a built-in alias
   yt alias show i

Delete Aliases
~~~~~~~~~~~~~~

Delete a user-defined alias that is no longer needed.

.. code-block:: bash

   yt alias delete ALIAS_NAME

**Arguments:**
  * ``ALIAS_NAME`` - The name of the user-defined alias to delete

**Examples:**

.. code-block:: bash

   # Delete a user-defined alias
   yt alias delete myissues

   # Remove an outdated alias
   yt alias delete oldshortcut

.. note::
   You can only delete user-defined aliases. Built-in aliases cannot be removed.

Built-in Aliases
----------------

YouTrack CLI comes with several built-in aliases for common operations:

.. list-table::
   :widths: 15 25 60
   :header-rows: 1

   * - Alias
     - Full Command
     - Description
   * - ``i``
     - ``issues``
     - Issue management commands
   * - ``p``
     - ``projects``
     - Project management commands
   * - ``u``
     - ``users``
     - User management commands
   * - ``t``
     - ``time``
     - Time tracking commands
   * - ``a``
     - ``articles``
     - Article management commands
   * - ``b``
     - ``boards``
     - Board management commands

Best Practices
--------------

**Alias Naming:**
  * Use short, memorable names that are easy to type
  * Choose names that clearly indicate the command's purpose
  * Avoid names that conflict with built-in commands or aliases

**Command Construction:**
  * Include commonly used options in your aliases to save time
  * Use descriptive option values that match your typical workflow
  * Test aliases thoroughly before relying on them in automation

**Organization:**
  * Create aliases for your most frequently used command combinations
  * Group related aliases with consistent naming patterns
  * Document your aliases for team sharing and knowledge transfer

Common Use Cases
----------------

**Daily Workflow Shortcuts:**

.. code-block:: bash

   # Personal issue management
   yt alias create my "issues list --assignee me --state Open"
   yt alias create done "issues list --assignee me --state Done"

   # Quick issue creation
   yt alias create newbug "issues create --type Bug --priority High"
   yt alias create task "issues create --type Task"

**Team Workflow Shortcuts:**

.. code-block:: bash

   # Project-specific shortcuts
   yt alias create webissues "issues list --project WEB --format table"
   yt alias create apibugs "issues list --project API --type Bug --state Open"

**Reporting Shortcuts:**

.. code-block:: bash

   # Time tracking shortcuts
   yt alias create timetoday "time list --date today --format table"
   yt alias create mystats "time report --assignee me --format json"

Advanced Usage
--------------

**Complex Command Aliases:**

You can create aliases for complex command combinations:

.. code-block:: bash

   # Multi-option filtering
   yt alias create criticalbugs "issues list --type Bug --priority Critical --state Open --assignee me"

   # Reporting with specific formatting
   yt alias create weekreport "time report --from -7days --format csv --output weekly.csv"

**Integration with Automation:**

Use aliases in scripts and automation workflows:

.. code-block:: bash

   # In shell scripts
   #!/bin/bash
   eval "yt my"  # Use the 'my' alias
   eval "yt newbug PROJECT-123 'Critical issue found'"

Authentication
--------------

All alias commands work with your existing authentication. Make sure you're logged in:

.. code-block:: bash

   yt auth login

Error Handling
--------------

The CLI provides detailed error messages for common alias issues:

* **Duplicate alias names** - Cannot create aliases with names that already exist
* **Invalid command syntax** - The command portion of an alias must be valid CLI syntax
* **Permission errors** - Some commands in aliases may require specific permissions
* **Alias not found** - Attempting to show or delete non-existent aliases

See Also
--------

* :doc:`config` - CLI configuration and settings
* :doc:`auth` - Authentication management
* :doc:`issues` - Issue management commands
* :doc:`projects` - Project management commands
