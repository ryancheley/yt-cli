Quick Start Guide
=================

This guide will help you get started with YouTrack CLI quickly.

1. Authentication
-----------------

First, authenticate with your YouTrack instance:

.. code-block:: bash

   yt auth login

You'll be prompted to enter:
- YouTrack URL (e.g., https://your-company.myjetbrains.com/youtrack)
- Username
- Password or API token

2. Basic Commands
-----------------

List Issues
~~~~~~~~~~~

View all issues assigned to you:

.. code-block:: bash

   yt issues list

Search for specific issues:

.. code-block:: bash

   yt issues search --query "assignee:me state:open"

Create an Issue
~~~~~~~~~~~~~~~

Create a new issue:

.. code-block:: bash

   yt issues create --title "Fix login bug" --description "Users cannot log in"

With additional fields:

.. code-block:: bash

   yt issues create \
     --title "Implement feature X" \
     --description "Add new feature X to improve user experience" \
     --project "PROJECT-ID" \
     --assignee "john.doe" \
     --priority "Major"

Update an Issue
~~~~~~~~~~~~~~~

Update issue fields:

.. code-block:: bash

   yt issues update ISSUE-123 --state "In Progress" --assignee "jane.doe"

Add a comment:

.. code-block:: bash

   yt issues comments add ISSUE-123 --text "Working on this issue"

3. Project Management
---------------------

List Projects
~~~~~~~~~~~~~

View all available projects:

.. code-block:: bash

   yt projects list

Create a Project
~~~~~~~~~~~~~~~~

.. code-block:: bash

   yt projects create --name "New Project" --key "NP" --description "Project description"

4. Time Tracking
----------------

Log Work Time
~~~~~~~~~~~~~

Log time spent on an issue:

.. code-block:: bash

   yt time log ISSUE-123 --duration "2h 30m" --description "Fixed the bug"

View Time Reports
~~~~~~~~~~~~~~~~~

Generate time reports:

.. code-block:: bash

   yt time report --from "2024-01-01" --to "2024-01-31" --assignee "me"

5. Configuration
----------------

View Current Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   yt config list

Set Configuration Values
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   yt config set default_project "PROJECT-ID"
   yt config set output_format "table"

6. Common Workflows
-------------------

Daily Workflow
~~~~~~~~~~~~~~

1. Check your assigned issues:

   .. code-block:: bash

      yt issues list --assignee me --state open

2. Update issue status as you work:

   .. code-block:: bash

      yt issues update ISSUE-123 --state "In Progress"

3. Log time when you're done:

   .. code-block:: bash

      yt time log ISSUE-123 --duration "4h" --description "Completed implementation"

4. Mark issue as resolved:

   .. code-block:: bash

      yt issues update ISSUE-123 --state "Fixed"

Getting Help
------------

Get help for any command:

.. code-block:: bash

   yt --help
   yt issues --help
   yt issues create --help

Next Steps
----------

- Read the :doc:`configuration` guide for advanced setup options
- Explore the full :doc:`commands/index` reference
- Check out :doc:`development` if you want to contribute