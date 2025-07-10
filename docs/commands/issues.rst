Issues Command Group
====================

The ``yt issues`` command group provides comprehensive issue management capabilities for YouTrack. This is the core functionality for creating, updating, searching, and managing issues in your YouTrack projects.

.. contents:: Table of Contents
   :local:
   :depth: 2

Overview
--------

The issues command group offers complete issue lifecycle management including:

* Creating and updating issues with all custom fields
* Advanced searching and filtering with YouTrack query language
* Managing issue comments and attachments
* Handling issue relationships and links
* Assigning issues and managing workflow states
* Managing issue tags and project transitions

Base Command
------------

.. code-block:: bash

   yt issues [OPTIONS] COMMAND [ARGS]...

Issue Management Commands
-------------------------

Create Issues
~~~~~~~~~~~~~

Create new issues in YouTrack projects.

.. code-block:: bash

   yt issues create PROJECT_ID SUMMARY [OPTIONS]

**Arguments:**
  * ``PROJECT_ID`` - The ID of the project to create the issue in
  * ``SUMMARY`` - Brief description of the issue

**Options:**
  * ``-d, --description TEXT`` - Detailed issue description
  * ``-t, --type TEXT`` - Issue type (e.g., Bug, Feature, Task)
  * ``-p, --priority TEXT`` - Issue priority (e.g., Critical, High, Medium, Low)
  * ``-a, --assignee TEXT`` - Username of the assignee

**Example:**

.. code-block:: bash

   yt issues create PROJ-1 "Fix login bug" -d "Users cannot login with special characters" -t Bug -p High -a john.doe

List Issues
~~~~~~~~~~~

List and filter issues with advanced options.

.. code-block:: bash

   yt issues list [OPTIONS]

**Options:**
  * ``-p, --project-id TEXT`` - Filter by project ID
  * ``-s, --state TEXT`` - Filter by issue state
  * ``-a, --assignee TEXT`` - Filter by assignee
  * ``-f, --fields TEXT`` - Comma-separated list of fields to return
  * ``-t, --top INTEGER`` - Maximum number of issues to return
  * ``-q, --query TEXT`` - Advanced query filter using YouTrack syntax
  * ``--format [table|json]`` - Output format (default: table)

**Examples:**

.. code-block:: bash

   # List all issues in a project
   yt issues list -p PROJ-1

   # List high priority bugs assigned to a user
   yt issues list -p PROJ-1 -a john.doe --query "priority:High type:Bug"

   # List issues in JSON format
   yt issues list --format json -t 10

Update Issues
~~~~~~~~~~~~~

Update existing issues with new field values.

.. code-block:: bash

   yt issues update ISSUE_ID [OPTIONS]

**Arguments:**
  * ``ISSUE_ID`` - The ID of the issue to update

**Options:**
  * ``-s, --summary TEXT`` - New issue summary
  * ``-d, --description TEXT`` - New issue description
  * ``--state TEXT`` - New issue state
  * ``-p, --priority TEXT`` - New issue priority
  * ``-a, --assignee TEXT`` - New assignee username
  * ``-t, --type TEXT`` - New issue type
  * ``--show-details`` - Show current issue details instead of updating

**Examples:**

.. code-block:: bash

   # Update issue priority and assignee
   yt issues update PROJ-123 -p Critical -a jane.smith

   # View current issue details
   yt issues update PROJ-123 --show-details

Delete Issues
~~~~~~~~~~~~~

Delete issues from YouTrack.

.. code-block:: bash

   yt issues delete ISSUE_ID [OPTIONS]

**Arguments:**
  * ``ISSUE_ID`` - The ID of the issue to delete

**Options:**
  * ``--confirm`` - Skip confirmation prompt

**Example:**

.. code-block:: bash

   yt issues delete PROJ-123 --confirm

Search Issues
~~~~~~~~~~~~~

Advanced issue search with YouTrack query language.

.. code-block:: bash

   yt issues search QUERY [OPTIONS]

**Arguments:**
  * ``QUERY`` - Search query using YouTrack syntax

**Options:**
  * ``-p, --project-id TEXT`` - Filter by project ID
  * ``-t, --top INTEGER`` - Maximum number of results
  * ``--format [table|json]`` - Output format

**Examples:**

.. code-block:: bash

   # Search for bugs with specific text
   yt issues search "login error" -p PROJ-1

   # Complex query with multiple conditions
   yt issues search "priority:Critical state:Open assignee:me"

Assign Issues
~~~~~~~~~~~~~

Assign issues to users.

.. code-block:: bash

   yt issues assign ISSUE_ID ASSIGNEE

**Arguments:**
  * ``ISSUE_ID`` - The ID of the issue
  * ``ASSIGNEE`` - Username of the new assignee

**Example:**

.. code-block:: bash

   yt issues assign PROJ-123 john.doe

Move Issues
~~~~~~~~~~~

Move issues between states or projects.

.. code-block:: bash

   yt issues move ISSUE_ID [OPTIONS]

**Arguments:**
  * ``ISSUE_ID`` - The ID of the issue to move

**Options:**
  * ``-s, --state TEXT`` - New state for the issue
  * ``-p, --project-id TEXT`` - Move to different project

**Examples:**

.. code-block:: bash

   # Move issue to different state
   yt issues move PROJ-123 -s "In Progress"

   # Move issue to different project
   yt issues move PROJ-123 -p OTHER-PROJ

.. note::
   State changes are implemented using YouTrack's custom field format to ensure
   reliable state transitions. The CLI will report success only when the state
   change is actually applied in YouTrack. Use exact state names as they appear
   in your YouTrack workflow.

Tag Management
~~~~~~~~~~~~~~

Manage issue tags.

**Add Tags:**

.. code-block:: bash

   yt issues tag add ISSUE_ID TAG_NAME

**Remove Tags:**

.. code-block:: bash

   yt issues tag remove ISSUE_ID TAG_NAME

**List Tags:**

.. code-block:: bash

   yt issues tag list ISSUE_ID

**Examples:**

.. code-block:: bash

   # Add a tag
   yt issues tag add PROJ-123 urgent

   # Remove a tag
   yt issues tag remove PROJ-123 outdated

   # List all tags on an issue
   yt issues tag list PROJ-123

Comment Management
------------------

Manage comments on issues.

Add Comments
~~~~~~~~~~~~

.. code-block:: bash

   yt issues comments add ISSUE_ID TEXT

**Example:**

.. code-block:: bash

   yt issues comments add PROJ-123 "Fixed in latest build"

List Comments
~~~~~~~~~~~~~

.. code-block:: bash

   yt issues comments list ISSUE_ID [OPTIONS]

**Options:**
  * ``--format [table|json]`` - Output format

Update Comments
~~~~~~~~~~~~~~~

.. code-block:: bash

   yt issues comments update ISSUE_ID COMMENT_ID TEXT

Delete Comments
~~~~~~~~~~~~~~~

.. code-block:: bash

   yt issues comments delete ISSUE_ID COMMENT_ID [OPTIONS]

**Options:**
  * ``--confirm`` - Skip confirmation prompt

Attachment Management
---------------------

Manage file attachments on issues.

Upload Attachments
~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   yt issues attach upload ISSUE_ID FILE_PATH

**Example:**

.. code-block:: bash

   yt issues attach upload PROJ-123 /path/to/screenshot.png

Download Attachments
~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   yt issues attach download ISSUE_ID ATTACHMENT_ID [OPTIONS]

**Options:**
  * ``-o, --output PATH`` - Output file path

List Attachments
~~~~~~~~~~~~~~~~

.. code-block:: bash

   yt issues attach list ISSUE_ID [OPTIONS]

**Options:**
  * ``--format [table|json]`` - Output format

Delete Attachments
~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   yt issues attach delete ISSUE_ID ATTACHMENT_ID [OPTIONS]

**Options:**
  * ``--confirm`` - Skip confirmation prompt

Issue Relationships
-------------------

Manage links and relationships between issues.

Create Links
~~~~~~~~~~~~

.. code-block:: bash

   yt issues links create SOURCE_ISSUE_ID TARGET_ISSUE_ID LINK_TYPE

**Arguments:**
  * ``SOURCE_ISSUE_ID`` - The ID of the source issue
  * ``TARGET_ISSUE_ID`` - The ID of the target issue
  * ``LINK_TYPE`` - Type of link (e.g., "relates", "depends on", "duplicates", "subtask of")

**Examples:**

.. code-block:: bash

   # Create a dependency link
   yt issues links create PROJ-123 PROJ-124 "depends on"

   # Create a relation link
   yt issues links create PROJ-123 PROJ-125 relates

   # Create a duplicate link
   yt issues links create PROJ-123 PROJ-126 duplicates

.. note::
   The CLI automatically resolves link type names to their internal IDs and handles
   directed vs undirected link types. Use ``yt issues links types`` to see all
   available link types in your YouTrack instance.

List Links
~~~~~~~~~~

.. code-block:: bash

   yt issues links list ISSUE_ID [OPTIONS]

**Options:**
  * ``--format [table|json]`` - Output format

Delete Links
~~~~~~~~~~~~

.. code-block:: bash

   yt issues links delete SOURCE_ISSUE_ID LINK_ID [OPTIONS]

**Options:**
  * ``--confirm`` - Skip confirmation prompt

List Link Types
~~~~~~~~~~~~~~~

Display available link types in your YouTrack instance.

.. code-block:: bash

   yt issues links types [OPTIONS]

**Options:**
  * ``--format [table|json]`` - Output format

Authentication
--------------

All issue commands require authentication. Make sure you're logged in:

.. code-block:: bash

   yt auth login

Error Handling
--------------

The CLI provides detailed error messages for common issues:

* **Authentication errors** - Check your login status with ``yt auth token --show``
* **Permission errors** - Verify you have access to the project and required permissions
* **Invalid issue IDs** - Ensure the issue exists and you have access to view it
* **API errors** - Network issues or YouTrack server problems

Best Practices
--------------

**Issue Creation:**
  * Use descriptive summaries that clearly identify the problem or request
  * Include detailed descriptions with steps to reproduce for bugs
  * Set appropriate priority and type to help with organization

**Searching:**
  * Use YouTrack's query language for complex searches
  * Combine multiple filters for precise results
  * Save frequently used queries as project saved searches in the web interface

**Comments:**
  * Use comments to track progress and communicate with team members
  * Include relevant context and links to related information
  * Update issue status when commenting on resolution

**Attachments:**
  * Upload screenshots, logs, and relevant files to provide context
  * Use descriptive filenames for easier identification
  * Consider file size limits and compress large files when necessary

Advanced Usage
--------------

**Bulk Operations:**
For bulk operations, combine CLI commands with shell scripting:

.. code-block:: bash

   # Update multiple issues
   for issue in PROJ-123 PROJ-124 PROJ-125; do
       yt issues update $issue -s "Resolved"
   done

**Integration with Scripts:**
Use JSON output for integration with other tools:

.. code-block:: bash

   # Get issue data for processing
   yt issues list -p PROJ-1 --format json | jq '.[] | select(.priority.name == "High")'

**Automation:**
Combine with CI/CD pipelines for automated issue management:

.. code-block:: bash

   # Create issue from build failure
   yt issues create PROJ-1 "Build failed in $BRANCH" -d "Build log: $BUILD_LOG" -t Bug -p High

See Also
--------

* :doc:`projects` - Project management and organization
* :doc:`users` - User management for issue assignment
* :doc:`time` - Time tracking on issues
* :doc:`boards` - Agile board workflow with issues
* :doc:`reports` - Issue-based reporting and analytics
* YouTrack Query Language documentation for advanced search syntax
