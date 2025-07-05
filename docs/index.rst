YouTrack CLI Documentation
==========================

YouTrack CLI is a command-line interface for JetBrains YouTrack issue tracking system.
It provides an ergonomic way to interact with YouTrack from the terminal, featuring
rich text output and a comprehensive set of commands for managing issues, projects,
users, and more.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   youtrack-concepts
   quickstart
   configuration
   command-aliases
   security
   logging
   learning-path
   workflows
   troubleshooting
   commands/index
   api/index
   development
   changelog

Features
--------

* **Issue Management**: Create, update, search, and manage issues with full CRUD operations
* **Project Management**: List, create, and configure projects
* **User Management**: Manage users and permissions
* **Time Tracking**: Log work time and generate reports
* **Agile Boards**: View and manage agile boards
* **Knowledge Base**: Manage YouTrack articles and documentation
* **Security Features**: Command audit logging, credential encryption, and token management
* **Rich CLI Interface**: Beautiful terminal output with rich text formatting
* **Command Aliases**: Short aliases for frequently used commands to improve efficiency
* **Flexible Configuration**: Multiple authentication methods and configuration options

Quick Start
-----------

Install YouTrack CLI using pip:

.. code-block:: bash

   pip install youtrack-cli

Authenticate with your YouTrack instance:

.. code-block:: bash

   yt auth login

List your issues:

.. code-block:: bash

   yt issues list

Create a new issue:

.. code-block:: bash

   yt issues create PROJECT-ID "Bug report" --description "Description here"

Command Categories
------------------

* :doc:`commands/issues` - Issue management commands
* :doc:`commands/articles` - Knowledge base article management
* :doc:`commands/projects` - Project management commands
* :doc:`commands/users` - User management commands
* :doc:`commands/time` - Time tracking operations
* :doc:`commands/boards` - Agile board operations
* :doc:`commands/reports` - Report generation
* :doc:`commands/auth` - Authentication management
* :doc:`commands/config` - Configuration management
* :doc:`commands/admin` - Administrative operations

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
