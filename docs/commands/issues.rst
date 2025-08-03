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
* Batch operations for creating and updating multiple issues from files
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
  * ``-t, --top INTEGER`` - Maximum number of issues to return (legacy)
  * ``--max-results INTEGER`` - Maximum number of results to fetch (default: 10,000)
  * ``--after-cursor TEXT`` - Start listing after this cursor position
  * ``--before-cursor TEXT`` - Start listing before this cursor position
  * ``--paginated`` - Display results with interactive pagination
  * ``--display-page-size INTEGER`` - Items per page for interactive display (default: 50)
  * ``--all`` - Fetch all results automatically (respects max-results limit)
  * ``-q, --query TEXT`` - Advanced query filter using YouTrack syntax
  * ``--format [table|json|csv]`` - Output format (default: table)

**Examples:**

.. code-block:: bash

   # List all issues in a project with interactive pagination
   yt issues list -p PROJ-1 --paginated

   # List high priority bugs assigned to a user
   yt issues list -p PROJ-1 -a john.doe --query "priority:High type:Bug"

   # List issues in JSON format with cursor pagination
   yt issues list --format json --max-results 50

   # Export issues to CSV format for spreadsheet analysis
   yt issues list --format csv --limit 100

   # Navigate through pages using cursors
   yt issues list -p PROJ-1 --after-cursor "cursor_token_here"

   # Fetch all issues automatically (up to 10,000)
   yt issues list -p PROJ-1 --all

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
  * ``--force`` - Skip confirmation prompt

**Examples:**

.. code-block:: bash

   # Interactive deletion (will prompt for confirmation)
   yt issues delete PROJ-123

   # Non-interactive deletion for automation
   yt issues delete PROJ-123 --force

.. note::
   Use the ``--force`` flag for automation scripts and CI/CD pipelines to skip
   the interactive confirmation prompt.

Search Issues
~~~~~~~~~~~~~

Advanced issue search with YouTrack query language.

.. code-block:: bash

   yt issues search QUERY [OPTIONS]

**Arguments:**
  * ``QUERY`` - Search query using YouTrack syntax

**Options:**
  * ``-p, --project-id TEXT`` - Filter by project ID
  * ``-t, --top INTEGER`` - Maximum number of results (legacy)
  * ``--max-results INTEGER`` - Maximum number of results to fetch (default: 10,000)
  * ``--after-cursor TEXT`` - Start searching after this cursor position
  * ``--before-cursor TEXT`` - Start searching before this cursor position
  * ``--paginated`` - Display results with interactive pagination
  * ``--display-page-size INTEGER`` - Items per page for interactive display (default: 50)
  * ``--all`` - Fetch all results automatically (respects max-results limit)
  * ``--format [table|json|csv]`` - Output format

**Examples:**

.. code-block:: bash

   # Search for bugs with specific text
   yt issues search "login error" -p PROJ-1

   # Complex query with multiple conditions and pagination
   yt issues search "priority:Critical state:Open assignee:me" --paginated

   # Search with cursor navigation
   yt issues search "bug" --after-cursor "search_cursor_token"

   # Get all search results automatically
   yt issues search "type:Bug state:Open" --all

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

Move issues between states within the same project, or transfer issues to different projects entirely.

.. code-block:: bash

   yt issues move ISSUE_ID [OPTIONS]

**Arguments:**
  * ``ISSUE_ID`` - The ID of the issue to move

**Options:**
  * ``-s, --state TEXT`` - New state for the issue
  * ``-p, --project-id TEXT`` - Move to different project (short name or ID)

**State Moves (Within Project):**

.. code-block:: bash

   # Move issue to different state
   yt issues move PROJ-123 -s "In Progress"
   yt issues move PROJ-123 --state "Done"

**Project Moves (Between Projects):**

.. code-block:: bash

   # Move issue to different project
   yt issues move PROJ-123 -p WEB
   yt issues move DEMO-456 --project-id TEST

**Advanced Examples:**

.. code-block:: bash

   # Check available projects first
   yt projects list

   # Move issue with validation
   yt issues show PROJ-123  # Verify source issue
   yt issues move PROJ-123 -p TARGET-PROJ
   yt issues list -p TARGET-PROJ  # Verify move

.. warning::
   **Project Move Considerations:**

   * Ensure you have appropriate permissions in both source and target projects
   * Custom fields that exist in the source project but not in the target may be lost
   * Issue numbering will change to match the target project's scheme
   * All issue data (description, comments, attachments) will be preserved
   * Verify the move completed successfully by checking the target project

.. note::
   **State Changes:**

   State changes use YouTrack's custom field format to ensure reliable transitions.
   The CLI will report success only when the state change is actually applied.
   Use exact state names as they appear in your YouTrack workflow.

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
  * ``--format [table|json|csv]`` - Output format

Update Comments
~~~~~~~~~~~~~~~

.. code-block:: bash

   yt issues comments update ISSUE_ID COMMENT_ID TEXT

Delete Comments
~~~~~~~~~~~~~~~

.. code-block:: bash

   yt issues comments delete ISSUE_ID COMMENT_ID [OPTIONS]

**Options:**
  * ``--force`` - Skip confirmation prompt

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
  * ``--format [table|json|csv]`` - Output format

Delete Attachments
~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   yt issues attach delete ISSUE_ID ATTACHMENT_ID [OPTIONS]

**Options:**
  * ``--force`` - Skip confirmation prompt

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
  * ``--format [table|json|csv]`` - Output format

Delete Links
~~~~~~~~~~~~

.. code-block:: bash

   yt issues links delete SOURCE_ISSUE_ID LINK_ID [OPTIONS]

**Options:**
  * ``--force`` - Skip confirmation prompt

List Link Types
~~~~~~~~~~~~~~~

Display available link types in your YouTrack instance.

.. code-block:: bash

   yt issues links types [OPTIONS]

**Options:**
  * ``--format [table|json|csv]`` - Output format

Batch Operations
----------------

The ``yt issues batch`` command group provides efficient bulk operations for creating and updating multiple issues from CSV or JSON files. This is ideal for migrating issues, bulk updates, or data imports.

Batch Create Issues
~~~~~~~~~~~~~~~~~~~

Create multiple issues from a CSV or JSON file.

.. code-block:: bash

   yt issues batch create --file INPUT_FILE [OPTIONS]

**Options:**
  * ``-f, --file PATH`` - Path to CSV or JSON file containing issue data (required)
  * ``--dry-run`` - Validate and preview operations without executing them
  * ``--continue-on-error`` - Continue processing after errors (default: true)
  * ``--save-failed PATH`` - Save failed operations to specified file for retry
  * ``--rollback-on-error`` - Rollback (delete) created issues if any operation fails

**CSV File Format:**
The CSV file should have the following columns:

.. code-block:: csv

   project_id,summary,description,type,priority,assignee
   FPU,Fix login bug,Login fails on mobile devices,Bug,High,john.doe
   FPU,Add user dashboard,Create dashboard with user metrics,Feature,Medium,jane.smith

**JSON File Format:**
The JSON file should contain an array of issue objects:

.. code-block:: json

   [
     {
       "project_id": "FPU",
       "summary": "Fix login bug",
       "description": "Login fails on mobile devices",
       "type": "Bug",
       "priority": "High",
       "assignee": "john.doe"
     },
     {
       "project_id": "FPU",
       "summary": "Add user dashboard",
       "description": "Create dashboard with user metrics",
       "type": "Feature",
       "priority": "Medium",
       "assignee": "jane.smith"
     }
   ]

**Examples:**

.. code-block:: bash

   # Create issues from CSV file
   yt issues batch create --file issues.csv

   # Dry run to preview operations
   yt issues batch create --file issues.csv --dry-run

   # Create with error handling and save failed operations
   yt issues batch create --file issues.csv --save-failed failed.csv

   # Create with automatic rollback on errors
   yt issues batch create --file issues.csv --rollback-on-error

Batch Update Issues
~~~~~~~~~~~~~~~~~~~

Update multiple issues from a CSV or JSON file.

.. code-block:: bash

   yt issues batch update --file INPUT_FILE [OPTIONS]

**Options:**
  * ``-f, --file PATH`` - Path to CSV or JSON file containing update data (required)
  * ``--dry-run`` - Validate and preview operations without executing them
  * ``--continue-on-error`` - Continue processing after errors (default: true)
  * ``--save-failed PATH`` - Save failed operations to specified file for retry

**CSV File Format:**
The CSV file should include ``issue_id`` and any fields to update:

.. code-block:: csv

   issue_id,summary,description,state,type,priority,assignee
   FPU-1,Updated summary,,In Progress,,High,
   FPU-2,,Updated description text,Done,,,john.doe

**JSON File Format:**
The JSON file should contain an array of update objects:

.. code-block:: json

   [
     {
       "issue_id": "FPU-1",
       "summary": "Updated summary",
       "state": "In Progress",
       "priority": "High"
     },
     {
       "issue_id": "FPU-2",
       "description": "Updated description text",
       "state": "Done",
       "assignee": "john.doe"
     }
   ]

**Examples:**

.. code-block:: bash

   # Update issues from CSV file
   yt issues batch update --file updates.csv

   # Dry run to preview updates
   yt issues batch update --file updates.csv --dry-run

   # Update with error handling
   yt issues batch update --file updates.csv --save-failed failed.csv

Validate Batch Files
~~~~~~~~~~~~~~~~~~~~~

Validate a batch operation file without executing operations.

.. code-block:: bash

   yt issues batch validate --file INPUT_FILE --operation OPERATION

**Arguments:**
  * ``--file PATH`` - Path to CSV or JSON file to validate (required)
  * ``--operation [create|update]`` - Type of operation to validate for (required)

**Examples:**

.. code-block:: bash

   # Validate a file for batch create
   yt issues batch validate --file issues.csv --operation create

   # Validate a file for batch update
   yt issues batch validate --file updates.json --operation update

Generate Template Files
~~~~~~~~~~~~~~~~~~~~~~~~

Generate template files for batch operations.

.. code-block:: bash

   yt issues batch templates [OPTIONS]

**Options:**
  * ``--format [csv|json]`` - Template format to generate (default: csv)
  * ``-o, --output-dir PATH`` - Directory to save template files (default: current directory)

**Examples:**

.. code-block:: bash

   # Generate CSV templates in current directory
   yt issues batch templates

   # Generate JSON templates in specific directory
   yt issues batch templates --format json --output-dir ./templates

Batch Operations Best Practices
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**File Preparation:**
  * Always validate your files before running batch operations
  * Use dry-run mode to preview operations and catch potential issues
  * Keep backup copies of your data files

**Error Handling:**
  * Use ``--save-failed`` to capture failed operations for retry
  * Review error messages to understand why operations failed
  * Consider using ``--rollback-on-error`` for create operations when consistency is critical

**Performance:**
  * Batch operations are faster than individual commands for large datasets
  * Progress bars show real-time status and estimated completion time
  * Operations are logged for audit trail and troubleshooting

**Data Quality:**
  * Ensure project IDs, usernames, and field values are valid before processing
  * Use consistent formatting for dates, priorities, and other field values
  * Remove empty rows and columns from CSV files to avoid validation errors

**Workflow Integration:**
  * Generate templates to ensure consistent field mapping
  * Use validation commands in CI/CD pipelines for automated quality checks
  * Combine with scripts for complex data transformations before import

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
