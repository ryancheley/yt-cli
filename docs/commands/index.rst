Command Reference
=================

YouTrack CLI provides a comprehensive set of commands for managing your YouTrack instance.
All commands follow a consistent structure and support common options.

.. toctree::
   :maxdepth: 2

   issues
   articles
   projects
   users
   time
   boards
   reports
   auth
   config
   admin
   alias
   audit
   security
   setup
   burndown
   velocity
   completion
   groups
   ls
   new
   tutorial

Global Options
--------------

These options are available for all commands:

.. list-table::
   :widths: 20 20 60
   :header-rows: 1

   * - Option
     - Type
     - Description
   * - ``--help, -h``
     - flag
     - Show help message and exit
   * - ``--verbose, -v``
     - flag
     - Enable verbose output
   * - ``--quiet, -q``
     - flag
     - Suppress all output except errors
   * - ``--config, -c``
     - path
     - Path to configuration file
   * - ``--debug``
     - flag
     - Enable debug output
   * - ``--format``
     - choice
     - Output format: table, json, yaml (default: table)
   * - ``--help-verbose``
     - flag
     - Show detailed help information with all options and examples
   * - ``--no-progress``
     - flag
     - Disable progress indicators
   * - ``--secure``
     - flag
     - Enable enhanced security mode (prevents credential logging)
   * - ``--version``
     - flag
     - Show the version and exit
   * - ``--no-color``
     - flag
     - Disable colored output
   * - ``--dry-run``
     - flag
     - Show what would be done without making changes

Command Categories
------------------

Issue Management
~~~~~~~~~~~~~~~~

The :doc:`issues` command group provides comprehensive issue management capabilities:

* Create, update, and delete issues
* Search and filter issues
* Manage issue comments and attachments
* Handle issue relationships and links
* Assign issues and manage workflow states

Knowledge Base
~~~~~~~~~~~~~~

The :doc:`articles` command group manages YouTrack's knowledge base:

* Create and edit articles
* Manage article hierarchy and organization
* Handle article comments and attachments
* Control article publishing and drafts

Project Management
~~~~~~~~~~~~~~~~~~

The :doc:`projects` command group handles project administration:

* List and create projects
* Configure project settings
* Manage project permissions
* Archive and restore projects

User Management
~~~~~~~~~~~~~~~

The :doc:`users` command group provides user administration:

* List and create users
* Update user information
* Manage user permissions and groups
* Handle user authentication settings

Time Tracking
~~~~~~~~~~~~~

The :doc:`time` command group handles time tracking operations:

* Log work time on issues
* Generate time reports
* View time summaries and statistics
* Export time data

Agile Boards
~~~~~~~~~~~~

The :doc:`boards` command group manages agile boards:

* List available boards
* View board configurations
* Update board settings
* Manage board columns and swimlanes

Reporting
~~~~~~~~~

The :doc:`reports` command group generates various reports:

* Burndown charts
* Velocity reports
* Custom report generation
* Export capabilities

Authentication
~~~~~~~~~~~~~~

The :doc:`auth` command group handles authentication:

* Login and logout operations
* Token management
* Authentication testing
* Session management

Configuration
~~~~~~~~~~~~~

The :doc:`config` command group manages CLI configuration:

* View and set configuration options
* Manage connection settings
* Handle default values
* Export and import configurations

Administration
~~~~~~~~~~~~~~

The :doc:`admin` command group provides administrative functions:

* System settings management
* User and group administration
* Workflow and field management
* System maintenance operations

Command Shortcuts and Aliases
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The :doc:`alias` command group manages command aliases:

* Create custom shortcuts for frequently used commands
* List built-in and user-defined aliases
* Delete user-defined aliases
* Show alias definitions and mappings

The :doc:`ls` command provides a quick shortcut for listing issues:

* Shortcut for the most common list operation
* Familiar Unix-style command interface
* Multiple filtering options for issue discovery
* Support for various output formats

The :doc:`new` command provides a quick shortcut for creating issues:

* Streamlined interface for rapid issue creation
* Essential options for type, priority, and assignment
* Tag support and description capabilities
* Minimal typing for improved productivity

Security and Audit Management
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The :doc:`audit` command provides quick access to audit logs:

* View command execution history and audit trail
* Monitor CLI usage patterns and security events
* Export audit data in multiple formats
* Track commands for compliance and debugging

The :doc:`security` command group offers comprehensive security management:

* Complete audit log management capabilities
* Authentication token status monitoring
* Security maintenance and cleanup functions
* Comprehensive security reporting features

Setup and Configuration
~~~~~~~~~~~~~~~~~~~~~~~

The :doc:`setup` command provides interactive first-time configuration:

* Guided setup wizard for new installations
* YouTrack server connection configuration
* Authentication setup and credential management
* Basic preferences and default value configuration

The :doc:`completion` command generates shell completion scripts:

* Tab completion for commands and options
* Support for bash, zsh, fish, and PowerShell
* Automatic installation to system locations
* Enhanced CLI usability and productivity

Reporting and Analytics
~~~~~~~~~~~~~~~~~~~~~~~

The :doc:`burndown` command generates burndown reports:

* Project and sprint burndown analysis
* Work completion tracking over time
* Sprint goal achievement monitoring
* Customizable date range analysis

The :doc:`velocity` command generates velocity reports:

* Team performance analysis across sprints
* Delivery capacity and consistency tracking
* Trend analysis for sprint planning
* Predictive insights for future capacity

User and Group Management
~~~~~~~~~~~~~~~~~~~~~~~~~

The :doc:`groups` command manages user groups and permissions:

* Create and list user groups
* Organize team members by roles and projects
* Simplify permission management at scale
* Support role-based and project-based access control

Learning and Training
~~~~~~~~~~~~~~~~~~~~~

The :doc:`tutorial` command provides interactive learning experiences:

* Step-by-step guided tutorials for CLI features
* Progress tracking and resume capabilities
* Real-world examples and best practices
* Beginner-friendly explanations and workflows

Common Patterns
---------------

Filtering and Searching
~~~~~~~~~~~~~~~~~~~~~~~

Most list commands support filtering and searching:

.. code-block:: bash

   yt issues list --assignee me --state open
   yt issues search --query "project:PROJECT and state:open"

Output Formatting
~~~~~~~~~~~~~~~~~

All commands support multiple output formats:

.. code-block:: bash

   yt issues list --format json
   yt projects list --format yaml
   yt users list --format table

Batch Operations
~~~~~~~~~~~~~~~~

Many commands support batch operations:

.. code-block:: bash

   yt issues update ISSUE-1 ISSUE-2 ISSUE-3 --state "Fixed"
   yt users create --from-file users.csv

Interactive Mode
~~~~~~~~~~~~~~~~

Some commands provide interactive prompts:

.. code-block:: bash

   yt issues create --interactive
   yt projects configure PROJECT-ID --interactive

Examples
--------

Common command combinations and workflows:

.. code-block:: bash

   # Daily workflow
   yt issues list --assignee me --state open
   yt issues update ISSUE-123 --state "In Progress"
   yt time log ISSUE-123 --duration "2h" --description "Fixed bug"

   # Project setup
   yt projects create --name "New Project" --key "NP"
   yt users create --username "john.doe" --email "john@example.com"
   yt projects configure NP --add-user "john.doe"

   # Reporting
   yt time report --project "PROJECT-ID" --from "2024-01-01"
   yt reports generate burndown --project "PROJECT-ID" --sprint "Sprint-1"
