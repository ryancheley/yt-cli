================
Command Aliases
================

YouTrack CLI provides convenient aliases for commonly used commands to improve usability and reduce typing. This document describes all available command aliases and how to use them effectively.

Overview
========

Command aliases allow you to use shorter command names for frequently used operations. For example, instead of typing ``yt issues list``, you can simply use ``yt i l``.

Main Command Aliases
====================

The following aliases are available for the main command groups:

.. list-table:: Main Command Aliases
   :header-rows: 1
   :widths: 20 30 50

   * - Alias
     - Full Command
     - Description
   * - ``i``
     - ``issues``
     - Issue management commands
   * - ``a``
     - ``articles``
     - Knowledge base article commands
   * - ``p``
     - ``projects``
     - Project management commands
   * - ``u``
     - ``users``
     - User management commands
   * - ``t``
     - ``time``
     - Time tracking commands
   * - ``b``
     - ``boards``
     - Agile board commands
   * - ``c``, ``cfg``
     - ``config``
     - Configuration management
   * - ``login``
     - ``auth``
     - Authentication commands

Subcommand Aliases
==================

Within the issues command group, additional aliases are available for common operations:

.. list-table:: Issues Subcommand Aliases
   :header-rows: 1
   :widths: 20 30 50

   * - Alias
     - Full Command
     - Description
   * - ``c``, ``new``
     - ``create``
     - Create a new issue
   * - ``l``, ``ls``
     - ``list``
     - List issues
   * - ``u``, ``edit``
     - ``update``
     - Update an existing issue
   * - ``s``, ``find``
     - ``search``
     - Search for issues
   * - ``d``, ``del``, ``rm``
     - ``delete``
     - Delete an issue

Usage Examples
==============

Here are practical examples showing how to use aliases effectively:

Basic Operations
----------------

Create a new issue:

.. code-block:: bash

   # Using full commands
   yt issues create PROJECT-123 "Fix login bug"

   # Using aliases
   yt i c PROJECT-123 "Fix login bug"
   yt i new PROJECT-123 "Fix login bug"

List issues:

.. code-block:: bash

   # Using full commands
   yt issues list --assignee me

   # Using aliases
   yt i l --assignee me
   yt i ls --assignee me

Search for issues:

.. code-block:: bash

   # Using full commands
   yt issues search "priority:Critical"

   # Using aliases
   yt i s "priority:Critical"
   yt i find "priority:Critical"

Configuration Management
------------------------

.. code-block:: bash

   # Using full commands
   yt config set OUTPUT_FORMAT json
   yt config get OUTPUT_FORMAT

   # Using aliases
   yt c set OUTPUT_FORMAT json
   yt cfg get OUTPUT_FORMAT

Authentication
--------------

.. code-block:: bash

   # Using full commands
   yt auth login

   # Using aliases
   yt login

Project Management
------------------

.. code-block:: bash

   # Using full commands
   yt projects list

   # Using aliases
   yt p list

Time Tracking
-------------

.. code-block:: bash

   # Using full commands
   yt time log ISSUE-123 "2h 30m" --description "Fixed the bug"

   # Using aliases
   yt t log ISSUE-123 "2h 30m" --description "Fixed the bug"

Complex Workflows
=================

You can chain aliases for even more efficient workflows:

Daily Issue Management:

.. code-block:: bash

   # Check your assigned issues
   yt i l --assignee me --state Open

   # Create a new bug report
   yt i c WEB-123 "Mobile login issue" --type Bug --priority High

   # Update issue status
   yt i u ISSUE-456 --state "In Progress"

   # Log work time
   yt t log ISSUE-456 "1h 30m" --description "Initial investigation"

Configuration and Setup:

.. code-block:: bash

   # Quick authentication
   yt login

   # Configure output format
   yt c set OUTPUT_FORMAT table

   # List current configuration
   yt c list

Help and Discovery
==================

All aliases work with the ``--help`` flag to show command documentation:

.. code-block:: bash

   # Get help for issues commands
   yt i --help

   # Get help for creating issues
   yt i c --help

   # Get help for configuration
   yt c --help

The main help command also lists all available aliases:

.. code-block:: bash

   yt --help

Best Practices
==============

1. **Start with Full Commands**: When learning, use full command names to understand the structure.

2. **Use Aliases for Frequent Operations**: Once comfortable, switch to aliases for commands you use often.

3. **Mix and Match**: You can combine full commands and aliases as needed:

   .. code-block:: bash

      yt i create PROJECT-123 "Title"  # Mix of alias and full command

4. **Shell Completion**: Aliases work with shell completion, making them even faster to use.

5. **Documentation**: When sharing commands with others, consider using full names for clarity in documentation.

Shell Completion
================

Aliases are fully supported by the shell completion system. After setting up completion for your shell:

.. code-block:: bash

   # Generate completion for bash
   yt completion bash --install

   # Generate completion for zsh
   yt completion zsh --install

   # Generate completion for fish
   yt completion fish --install

You can use tab completion with aliases just like with full commands:

.. code-block:: bash

   yt i <TAB>       # Shows issues subcommands
   yt i c <TAB>     # Shows create command options
   yt c s<TAB>      # Completes to "set"

Migration Guide
===============

If you're upgrading from a version without aliases, your existing commands will continue to work unchanged. Aliases are additive and don't replace existing functionality.

You can gradually adopt aliases at your own pace:

1. Continue using full commands in scripts and documentation
2. Start using aliases for interactive command-line work
3. Update your muscle memory over time

Troubleshooting
===============

If aliases don't work as expected:

1. **Check Version**: Ensure you're using a version that supports aliases (v0.3.0+)

2. **Verify Installation**: Run ``yt --help`` to see if aliases are listed

3. **Clear Cache**: If using shell completion, you may need to restart your shell or reload completion

4. **Conflict Resolution**: If an alias conflicts with another command, the original command takes precedence

For additional help, see the :doc:`troubleshooting` guide or file an issue on GitHub.
