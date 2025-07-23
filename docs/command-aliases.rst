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

Global Shortcuts
================

YouTrack CLI provides global shortcuts for the most common operations (Issue #345):

.. list-table:: Global Shortcuts
   :header-rows: 1
   :widths: 20 30 50

   * - Shortcut
     - Equivalent Command
     - Description
   * - ``ls``
     - ``issues list``
     - List issues (most common operation)
   * - ``new``
     - ``issues create``
     - Create a new issue (most common creation)

**Usage Examples:**

.. code-block:: bash

   # List all issues
   yt ls

   # List your assigned issues
   yt ls --assignee me

   # List issues in a specific project
   yt ls --project DEMO

   # Create a new issue
   yt new DEMO "Fix login bug"

   # Create a bug with details
   yt new DEMO "Login fails" --type Bug --assignee john.doe

User-Defined Aliases
====================

In addition to built-in aliases, you can create your own custom aliases for frequently used commands (Issue #345).

Managing Custom Aliases
------------------------

Use the ``yt alias`` command group to manage your custom aliases:

.. code-block:: bash

   # List all aliases (built-in and custom)
   yt alias list

   # Add a custom alias
   yt alias add myissues "issues list --assignee me"

   # Show what an alias does
   yt alias show myissues

   # Remove a custom alias
   yt alias remove myissues

**Custom Alias Examples:**

.. code-block:: bash

   # Create shortcuts for common workflows
   yt alias add bugs "issues list --type Bug --state Open"
   yt alias add mybugs "issues list --type Bug --assignee me"
   yt alias add quickbug "issues create --type Bug"

   # Use your custom aliases
   yt bugs                    # List all open bugs
   yt mybugs                  # List bugs assigned to you
   yt quickbug DEMO "Title"   # Create a bug quickly

**Alias Rules:**

- Custom aliases take precedence over built-in aliases
- Aliases cannot conflict with existing command names
- Aliases are stored in your configuration file
- Complex commands with arguments and options are supported

Flatter Command Alternatives
============================

YouTrack CLI provides flatter alternatives to deeply nested commands for improved usability. These commands reduce the number of levels you need to type while maintaining full backward compatibility.

.. list-table:: Flatter Command Alternatives
   :header-rows: 1
   :widths: 25 35 40

   * - Flatter Command
     - Original Nested Command
     - Description
   * - ``burndown``
     - ``reports burndown``
     - Generate burndown reports
   * - ``velocity``
     - ``reports velocity``
     - Generate velocity reports
   * - ``groups``
     - ``admin user-groups``
     - Manage user groups and permissions
   * - ``settings``
     - ``admin global-settings``
     - Manage global YouTrack settings
   * - ``audit``
     - ``security audit``
     - View command audit log

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

   # Using global shortcut (new in Issue #345)
   yt new PROJECT-123 "Fix login bug"

   # Using command group aliases
   yt i c PROJECT-123 "Fix login bug"
   yt i new PROJECT-123 "Fix login bug"

List issues:

.. code-block:: bash

   # Using full commands
   yt issues list --assignee me

   # Using global shortcut (new in Issue #345)
   yt ls --assignee me

   # Using command group aliases
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

Flatter Commands
----------------

.. code-block:: bash

   # Reports - Traditional vs Flatter
   yt reports burndown PROJECT-123 --sprint "Sprint 1"
   yt burndown PROJECT-123 --sprint "Sprint 1"

   yt reports velocity PROJECT-123 --sprints 5
   yt velocity PROJECT-123 --sprints 5

   # User Groups - Traditional vs Flatter
   yt admin user-groups create "Team Lead" --description "Team leadership role"
   yt groups create "Team Lead" --description "Team leadership role"

   yt admin user-groups list
   yt groups list

   # Settings - Traditional vs Flatter
   yt admin global-settings get --name system.timeZone
   yt settings get --name system.timeZone

   yt admin global-settings set timeout 30
   yt settings set timeout 30

   # Audit Log - Traditional vs Flatter
   yt security audit --limit 25 --format json
   yt audit --limit 25 --format json

Complex Workflows
=================

You can chain aliases for even more efficient workflows:

Daily Issue Management:

.. code-block:: bash

   # Check your assigned issues (using global shortcut)
   yt ls --assignee me --state Open

   # Or using command group alias
   yt i l --assignee me --state Open

   # Create a new bug report (using global shortcut)
   yt new WEB-123 "Mobile login issue" --type Bug --priority High

   # Or using command group alias
   yt i c WEB-123 "Mobile login issue" --type Bug --priority High

   # Update issue status
   yt i u ISSUE-456 --state "In Progress"

   # Log work time
   yt t log ISSUE-456 "1h 30m" --description "Initial investigation"

Custom Alias Workflows:

.. code-block:: bash

   # Set up custom aliases for your workflow
   yt alias add mywork "issues list --assignee me --state Open"
   yt alias add sprint "issues list --project DEMO --sprint current"
   yt alias add bug "issues create --type Bug"

   # Use your custom aliases
   yt mywork                           # Check your work
   yt sprint                           # Check current sprint
   yt bug PROJECT-123 "Title"          # Create a bug quickly

Configuration and Setup:

.. code-block:: bash

   # Quick authentication
   yt login

   # Configure output format
   yt c set OUTPUT_FORMAT table

   # List current configuration
   yt c list

Flatter Command Workflows:

.. code-block:: bash

   # Daily reporting workflow
   yt burndown PROJECT-123                    # Quick burndown check
   yt velocity PROJECT-123 --sprints 3        # Check team velocity

   # Administrative tasks
   yt groups create "QA Team"                 # Create user group
   yt settings get --name system.timeZone     # Check timezone setting
   yt audit --limit 10                       # Review recent actions

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

If you're upgrading from a version without aliases or flatter commands, your existing commands will continue to work unchanged. All enhancements are additive and don't replace existing functionality.

You can gradually adopt new command patterns at your own pace:

1. Continue using full commands in scripts and documentation
2. Start using aliases for interactive command-line work
3. Try flatter commands for frequently used nested operations
4. Update your muscle memory over time

**Flatter Command Migration Examples:**

.. code-block:: bash

   # Old (still works)              # New flatter alternative
   yt reports burndown PROJECT      yt burndown PROJECT
   yt admin user-groups create      yt groups create
   yt security audit               yt audit

Troubleshooting
===============

If aliases don't work as expected:

1. **Check Version**: Ensure you're using a version that supports aliases (v0.3.0+) and user-defined aliases (v0.10.0+)

2. **Verify Installation**: Run ``yt --help`` to see if aliases are listed

3. **Clear Cache**: If using shell completion, you may need to restart your shell or reload completion

4. **Conflict Resolution**: If an alias conflicts with another command, the original command takes precedence

5. **Custom Alias Issues**:

   - Run ``yt alias list`` to see all available aliases
   - Check if your custom alias conflicts with existing commands
   - Verify alias syntax with ``yt alias show <alias-name>``
   - Custom aliases are stored in ``~/.config/youtrack-cli/.env`` as ``ALIAS_<name>=<command>``

6. **Alias Not Found**: If a custom alias isn't working, it may have been removed or the configuration file may be corrupted. Use ``yt alias add`` to recreate it.

For additional help, see the :doc:`troubleshooting` guide or file an issue on GitHub.
