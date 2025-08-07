LS Command
==========

The ``yt ls`` command provides a quick shortcut for listing YouTrack issues. This is a global shortcut for the most common list operation, equivalent to ``yt issues list`` but with a more convenient and familiar interface for users accustomed to Unix-style commands.

.. contents:: Table of Contents
   :local:
   :depth: 2

Overview
--------

The ls command allows you to:

* Quickly list YouTrack issues with common filtering options
* Use familiar Unix-style command patterns for issue discovery
* Apply multiple filters to find specific sets of issues
* Export issue lists in various formats for further processing
* Perform the most common YouTrack CLI operation with minimal typing

The ``yt ls`` command provides the same functionality as ``yt issues list`` but with a more concise syntax that's faster to type and easier to remember.

Base Command
------------

.. code-block:: bash

   yt ls [OPTIONS]

Command Options
---------------

**Options:**
  * ``-a, --assignee TEXT`` - Filter by assignee (use 'me' for current user)
  * ``-p, --project TEXT`` - Filter by project
  * ``-s, --state TEXT`` - Filter by state
  * ``-t, --type TEXT`` - Filter by issue type
  * ``--priority TEXT`` - Filter by priority
  * ``--tag TEXT`` - Filter by tag
  * ``-l, --limit INTEGER`` - Maximum number of issues to display
  * ``-f, --format [table|json|csv]`` - Output format (default: table)

**Examples:**

.. code-block:: bash

   # List all issues
   yt ls

   # List your assigned issues
   yt ls --assignee me

   # List issues in a specific project
   yt ls --project DEMO

   # List open bugs
   yt ls --type Bug --state Open

   # List high priority issues with limit
   yt ls --priority High --limit 20

Common Usage Patterns
---------------------

Personal Issue Management
~~~~~~~~~~~~~~~~~~~~~~~~

Quickly check your assigned work:

.. code-block:: bash

   # Your assigned issues (most common use case)
   yt ls -a me

   # Your open issues
   yt ls --assignee me --state Open

   # Your issues in a specific project
   yt ls -a me -p WEB-PROJECT

   # Your bugs and tasks
   yt ls --assignee me --type Bug
   yt ls --assignee me --type Task

Project Overview
~~~~~~~~~~~~~~~

Get a quick project status overview:

.. code-block:: bash

   # All issues in a project
   yt ls --project DEMO

   # Open issues in project
   yt ls -p DEMO -s Open

   # Bugs in project
   yt ls --project DEMO --type Bug

   # High priority items in project
   yt ls -p DEMO --priority High

Team and Workflow Monitoring
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Monitor team progress and workflow status:

.. code-block:: bash

   # All open issues for team review
   yt ls --state Open

   # Issues by type for sprint planning
   yt ls --type Feature --state "To Do"
   yt ls --type Bug --state "In Progress"

   # Issues with specific tags
   yt ls --tag urgent
   yt ls --tag "needs-review"

Data Export and Integration
~~~~~~~~~~~~~~~~~~~~~~~~~~

Export issue data for reports and analysis:

.. code-block:: bash

   # Export issues in JSON format
   yt ls --format json --limit 100

   # Export project issues to CSV
   yt ls --project DEMO --format csv > demo-issues.csv

   # Export filtered issues for reporting
   yt ls --assignee teamlead --priority High --format json > priority-issues.json

Integration with Issues Command
-------------------------------

The ``yt ls`` command is functionally identical to ``yt issues list``. Both commands provide the same issue listing capabilities:

.. code-block:: bash

   # These commands are equivalent:
   yt ls --assignee me --state Open
   yt issues list --assignee me --state Open

   # These commands are equivalent:
   yt ls --project DEMO --format json
   yt issues list --project DEMO --format json

Choose the command style that fits your workflow:

* Use ``yt ls`` for quick, frequent issue listing operations
* Use ``yt issues list`` when working with other issue management commands
* Use ``yt ls`` when you want familiar Unix-style command patterns

Advanced Filtering and Combinations
-----------------------------------

Multi-Criteria Filtering
~~~~~~~~~~~~~~~~~~~~~~~~

Combine multiple filters for precise issue discovery:

.. code-block:: bash

   # Multiple criteria for targeted searches
   yt ls --project WEB --assignee john.doe --state "In Progress"
   yt ls --type Bug --priority Critical --assignee me
   yt ls --project API --type Feature --state Open --limit 10

   # Tag-based filtering with other criteria
   yt ls --tag "sprint-1" --state Open
   yt ls --project MOBILE --tag "ui" --type Bug

Complex Workflow Scenarios
~~~~~~~~~~~~~~~~~~~~~~~~~~

Address specific workflow and process needs:

.. code-block:: bash

   # Sprint planning scenarios
   yt ls --state "Ready for Development" --limit 20
   yt ls --assignee me --state "In Review"

   # Quality assurance workflows
   yt ls --type Bug --state "Ready for Testing"
   yt ls --assignee qa-team --state "In Testing"

   # Release management
   yt ls --priority High --state Open
   yt ls --tag "release-blocker" --format json

Output Formatting and Processing
--------------------------------

Table Format (Default)
~~~~~~~~~~~~~~~~~~~~~~

The default table format provides human-readable output:

.. code-block:: bash

   # Standard table output
   yt ls --assignee me

Displays issues in a formatted table with columns for key information like ID, summary, assignee, state, and priority.

JSON Format
~~~~~~~~~~~

JSON format enables programmatic processing and integration:

.. code-block:: bash

   # JSON output for automation
   yt ls --project DEMO --format json

   # Process JSON with jq for custom analysis
   yt ls --format json | jq '.[] | select(.priority.name == "High")'

   # Extract specific fields
   yt ls --format json | jq '.[] | {id, summary, assignee: .assignee.name}'

CSV Format
~~~~~~~~~~

CSV format is ideal for spreadsheet analysis and reporting:

.. code-block:: bash

   # CSV export for spreadsheet analysis
   yt ls --format csv > issues-export.csv

   # Project-specific CSV reports
   yt ls --project WEB --format csv > web-project-issues.csv

   # Filtered CSV for specific analysis
   yt ls --state Open --priority High --format csv > priority-open-issues.csv

Automation and Scripting
-------------------------

Daily Workflow Automation
~~~~~~~~~~~~~~~~~~~~~~~~~

Create scripts for regular issue monitoring:

.. code-block:: bash

   #!/bin/bash
   # Daily issue check script

   echo "=== Your Daily Issue Summary ==="
   echo "Your assigned open issues:"
   yt ls -a me -s Open

   echo -e "\nHigh priority issues requiring attention:"
   yt ls --priority High --state Open --limit 10

   echo -e "\nIssues ready for review:"
   yt ls --state "Ready for Review" --limit 5

Team Status Reports
~~~~~~~~~~~~~~~~~~~

Generate team-level status reports:

.. code-block:: bash

   #!/bin/bash
   # Team status report generator

   PROJECTS=("WEB" "API" "MOBILE")

   echo "=== Team Status Report - $(date) ==="

   for project in "${PROJECTS[@]}"; do
       echo "--- $project Project ---"
       echo "Open issues: $(yt ls -p $project -s Open --format json | jq length)"
       echo "In Progress: $(yt ls -p $project -s "In Progress" --format json | jq length)"
       echo "Ready for Review: $(yt ls -p $project -s "Ready for Review" --format json | jq length)"
       echo
   done

CI/CD Integration
~~~~~~~~~~~~~~~~

Integrate issue checking into development workflows:

.. code-block:: bash

   # Check for blocking issues before deployment
   BLOCKERS=$(yt ls --tag "release-blocker" --state Open --format json | jq length)

   if [ "$BLOCKERS" -gt 0 ]; then
       echo "Warning: $BLOCKERS release blocking issues found"
       yt ls --tag "release-blocker" --state Open
       exit 1
   fi

Performance and Efficiency Tips
-------------------------------

Optimizing List Operations
~~~~~~~~~~~~~~~~~~~~~~~~~

Make listing operations faster and more efficient:

**Use Limits:**
  * Apply reasonable limits to avoid loading excessive data
  * Use ``--limit`` for quick status checks and overviews
  * Increase limits only when comprehensive data is needed

**Specific Filtering:**
  * Use the most specific filters available to reduce result sets
  * Combine filters to narrow results precisely
  * Avoid broad queries when specific information is needed

**Format Selection:**
  * Use table format for human consumption and quick scanning
  * Use JSON format for automated processing and integration
  * Use CSV format for data analysis and reporting

Alias and Shortcut Strategies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create even shorter shortcuts for frequent operations:

.. code-block:: bash

   # Create shell aliases for super quick access
   alias my="yt ls -a me"
   alias myopen="yt ls -a me -s Open"
   alias bugs="yt ls --type Bug --state Open"
   alias priority="yt ls --priority High --state Open"

**Common Alias Patterns:**
  * Personal issue shortcuts (``my``, ``mybugs``, ``mytasks``)
  * Project shortcuts (``webissues``, ``apibugs``)
  * Workflow shortcuts (``review``, ``testing``, ``blocked``)

Best Practices
--------------

**Efficient Filtering:**
  * Start with broader filters and narrow down as needed
  * Use project filters to focus on relevant work areas
  * Combine assignee filters with status for personal productivity

**Regular Monitoring:**
  * Check your assigned issues regularly with ``yt ls -a me``
  * Monitor project status with ``yt ls -p PROJECT-NAME``
  * Keep track of high priority items with ``yt ls --priority High``

**Data Export:**
  * Export filtered results for analysis and reporting
  * Use JSON format for integration with other tools
  * Create regular CSV exports for trend analysis

Troubleshooting
---------------

Common Issues
~~~~~~~~~~~~~

**No Results Returned:**
  * Verify filter criteria are correct and realistic
  * Check that you have access to the specified project
  * Ensure issue states and types exist in your YouTrack configuration

**Performance Issues:**
  * Add ``--limit`` parameter to restrict result set size
  * Use more specific filters to reduce query complexity
  * Check network connectivity to YouTrack instance

**Permission Errors:**
  * Verify you have read access to the specified projects
  * Check that your authentication token is valid
  * Ensure you have appropriate permissions for the requested data

Authentication
--------------

The ls command requires authentication and appropriate permissions. Make sure you're logged in:

.. code-block:: bash

   yt auth login

See Also
--------

* :doc:`issues` - Complete issue management functionality including advanced search
* :doc:`new` - Quick issue creation shortcut
* :doc:`projects` - Project management and configuration
* :doc:`users` - User management for assignee filtering
