Quick Start Guide
=================

This guide will help you get started with YouTrack CLI quickly.

Before You Begin
----------------

**What is YouTrack?**

YouTrack is an issue tracking and project management tool by JetBrains. If you're new to YouTrack, we recommend reading the :doc:`youtrack-concepts` guide first for a comprehensive understanding.

**Key Concepts (Quick Reference):**

* **Issues**: Work items like bugs, features, or tasks that need to be tracked
* **Projects**: Containers that organize related issues (e.g., "WEB-FRONTEND", "MOBILE-APP")
* **States**: Issue statuses like "Open", "In Progress", "Resolved", "Closed"
* **Assignee**: The person responsible for working on an issue
* **Priority**: Importance level (Critical, High, Medium, Low)
* **Types**: Category of work (Bug, Feature, Task, Epic)

**Prerequisites**

* A YouTrack instance URL (ask your team lead or admin)
* API token or login credentials (see Authentication section below)
* Basic command line familiarity
* Python 3.9+ installed on your system

1. Authentication
-----------------

First, authenticate with your YouTrack instance:

.. code-block:: bash

   yt auth login

You'll be prompted to enter:
- YouTrack URL (e.g., https://yourcompany.youtrack.cloud)
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

   yt issues search "assignee:me state:open"

Create an Issue
~~~~~~~~~~~~~~~

Create a bug report for a login issue:

.. code-block:: bash

   yt issues create WEB-FRONTEND "Login button not responding on mobile Safari" \
     --description "Users on iPhone 12 and 13 cannot tap login button. Error occurs on iOS Safari only." \
     --priority "High" \
     --type "Bug" \
     --assignee "mobile-team-lead"

**Expected output:**

.. code-block:: text

   🐛 Creating issue 'Login button not responding on mobile Safari' in project 'WEB-FRONTEND'...
   ✅ Issue 'Login button not responding on mobile Safari' created successfully

Create a feature request:

.. code-block:: bash

   yt issues create API-BACKEND "Add user profile API endpoint" \
     --description "Create REST API endpoint for user profile management with CRUD operations" \
     --priority "Medium" \
     --type "Feature" \
     --assignee "backend-dev"

Update an Issue
~~~~~~~~~~~~~~~

Update issue fields:

.. code-block:: bash

   yt issues update ISSUE-123 --state "In Progress" --assignee "jane.doe"

Add a comment:

.. code-block:: bash

   yt issues comments add ISSUE-123 "Working on this issue"

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

   yt time log ISSUE-123 "2h 30m" --description "Fixed the bug"

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

      yt time log ISSUE-123 "4h" --description "Completed implementation"

4. Mark issue as resolved:

   .. code-block:: bash

      yt issues update ISSUE-123 --state "Fixed"

Getting Help and Debugging
--------------------------

Get help for any command:

.. code-block:: bash

   yt --help
   yt issues --help
   yt issues create --help

Troubleshooting Commands
~~~~~~~~~~~~~~~~~~~~~~~~

If you encounter issues, YouTrack CLI provides enhanced debugging capabilities:

**Verbose Mode** - Shows progress and additional information:

.. code-block:: bash

   yt --verbose issues list
   yt --verbose projects create --name "New Project" --key "NP"

**Debug Mode** - Shows detailed information for troubleshooting:

.. code-block:: bash

   yt --debug auth login
   yt --debug issues create PROJECT-KEY "Test issue"

**Error Examples with Suggestions**

YouTrack CLI now provides helpful error messages with actionable suggestions:

.. code-block:: bash

   # Example: Authentication error
   $ yt issues list
   Error: Authentication failed
   Suggestion: Run 'yt auth login' to authenticate with YouTrack

   # Example: Project not found
   $ yt issues create INVALID-PROJECT "Test issue"
   Error: Project 'INVALID-PROJECT' not found
   Suggestion: Check if the project exists and you have access to it

**Output Formatting Options**

Control how results are displayed:

.. code-block:: bash

   # Table format (default)
   yt issues list --format table

   # JSON format for automation
   yt issues list --format json

   # Disable colors for plain text
   yt issues list --no-color

Next Steps
----------

- Read the :doc:`configuration` guide for advanced setup options
- Explore the full :doc:`commands/index` reference
- Check out :doc:`development` if you want to contribute
