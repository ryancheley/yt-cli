Time Tracking Command Group
============================

The ``yt time`` command group provides comprehensive time tracking capabilities for YouTrack issues. Track work hours, generate reports, and analyze productivity across projects and teams.

.. contents:: Table of Contents
   :local:
   :depth: 2

Overview
--------

YouTrack time tracking helps teams monitor effort, generate reports, and understand project progress. The time command group allows you to:

* Log work time on issues with flexible duration formats
* Track different types of work (Development, Testing, etc.)
* Generate detailed time reports with filtering
* View time summaries grouped by various criteria
* Export time data for analysis and billing
* Support for historical time entries and date flexibility

Base Command
------------

.. code-block:: bash

   yt time [OPTIONS] COMMAND [ARGS]...

Time Tracking Commands
----------------------

log
~~~

Log work time to a specific issue.

.. code-block:: bash

   yt time log ISSUE_ID DURATION [OPTIONS]

**Arguments:**

* ``ISSUE_ID`` - The issue ID to log time against (required)
* ``DURATION`` - Duration of work in various formats (required)

**Options:**

.. list-table::
   :widths: 20 20 60
   :header-rows: 1

   * - Option
     - Type
     - Description
   * - ``--date, -d``
     - string
     - Date for the work entry (YYYY-MM-DD, 'today', 'yesterday')
   * - ``--description, -desc``
     - string
     - Description of the work performed
   * - ``--work-type, -t``
     - string
     - Type of work (Development, Testing, Documentation, etc.)

**Examples:**

.. code-block:: bash

   # Log time to an issue
   yt time log ISSUE-123 "2h" --description "Implemented new feature"

   # Log time with work type
   yt time log ISSUE-123 "1h 30m" --work-type "Development" --description "Code review"

   # Log time for a specific date
   yt time log ISSUE-123 "45m" --date "2024-01-15" --description "Bug fixing"

   # Log time for yesterday
   yt time log ISSUE-123 "2h" --date "yesterday" --description "Testing"

   # Log time with combined duration format
   yt time log ISSUE-456 "2h 30m" --work-type "Documentation" --description "API docs"

report
~~~~~~

Generate detailed time reports with filtering options.

.. code-block:: bash

   yt time report [OPTIONS]

**Options:**

.. list-table::
   :widths: 20 20 60
   :header-rows: 1

   * - Option
     - Type
     - Description
   * - ``--issue-id, -i``
     - string
     - Filter by specific issue ID
   * - ``--user-id, -u``
     - string
     - Filter by specific user ID
   * - ``--start-date, -s``
     - string
     - Start date for filtering (YYYY-MM-DD)
   * - ``--end-date, -e``
     - string
     - End date for filtering (YYYY-MM-DD)
   * - ``--format, -f``
     - choice
     - Output format: table, json (default: table)

**Examples:**

.. code-block:: bash

   # Generate time reports for specific issues
   yt time report --issue-id ISSUE-123

   # Generate time reports for a user
   yt time report --user-id USER-456

   # Generate time reports for a date range
   yt time report --start-date "2024-01-01" --end-date "2024-01-31"

   # Generate comprehensive report with multiple filters
   yt time report --user-id USER-123 --start-date "2024-01-01" --end-date "2024-01-31"

   # Export reports in JSON format
   yt time report --format json --start-date "2024-01-01"

summary
~~~~~~~

View time summaries with aggregation and grouping options.

.. code-block:: bash

   yt time summary [OPTIONS]

**Options:**

.. list-table::
   :widths: 20 20 60
   :header-rows: 1

   * - Option
     - Type
     - Description
   * - ``--user-id, -u``
     - string
     - Filter by specific user ID
   * - ``--start-date, -s``
     - string
     - Start date for filtering (YYYY-MM-DD)
   * - ``--end-date, -e``
     - string
     - End date for filtering (YYYY-MM-DD)
   * - ``--group-by, -g``
     - choice
     - Group summary by: user, issue, type (default: user)
   * - ``--format, -f``
     - choice
     - Output format: table, json (default: table)

**Examples:**

.. code-block:: bash

   # View time summary grouped by user (default)
   yt time summary

   # View time summary grouped by issue
   yt time summary --group-by issue

   # View time summary grouped by work type
   yt time summary --group-by type

   # Filter summary by date range
   yt time summary --start-date "2024-01-01" --end-date "2024-01-31"

   # Export summary in JSON format
   yt time summary --format json --group-by issue

   # User-specific summary for performance review
   yt time summary --user-id USER-123 --start-date "2024-01-01" --end-date "2024-03-31"

Duration Formats
----------------

The time tracking system supports flexible duration input formats:

Hours Format
~~~~~~~~~~~

.. code-block:: bash

   # Hours with decimal
   yt time log ISSUE-123 "2h"        # 2 hours
   yt time log ISSUE-123 "1.5h"      # 1.5 hours
   yt time log ISSUE-123 "0.25h"     # 15 minutes

Minutes Format
~~~~~~~~~~~~~

.. code-block:: bash

   # Minutes only
   yt time log ISSUE-123 "30m"       # 30 minutes
   yt time log ISSUE-123 "45m"       # 45 minutes
   yt time log ISSUE-123 "120m"      # 2 hours

Combined Format
~~~~~~~~~~~~~~

.. code-block:: bash

   # Hours and minutes combined
   yt time log ISSUE-123 "2h 30m"    # 2 hours 30 minutes
   yt time log ISSUE-123 "1h 15m"    # 1 hour 15 minutes
   yt time log ISSUE-123 "0h 45m"    # 45 minutes

Numeric Format
~~~~~~~~~~~~~

.. code-block:: bash

   # Numeric values (assumed to be minutes)
   yt time log ISSUE-123 "90"        # 90 minutes (1.5 hours)
   yt time log ISSUE-123 "120"       # 120 minutes (2 hours)

Date Formats
------------

Flexible date input supports various formats for logging historical time:

ISO Format
~~~~~~~~~~

.. code-block:: bash

   # Standard ISO date format
   yt time log ISSUE-123 "2h" --date "2024-01-15"
   yt time log ISSUE-123 "1h" --date "2024-12-31"

US Format
~~~~~~~~

.. code-block:: bash

   # US date format
   yt time log ISSUE-123 "2h" --date "01/15/2024"
   yt time log ISSUE-123 "1h" --date "12/31/2024"

European Format
~~~~~~~~~~~~~~

.. code-block:: bash

   # European date format
   yt time log ISSUE-123 "2h" --date "15.01.2024"
   yt time log ISSUE-123 "1h" --date "31.12.2024"

Relative Dates
~~~~~~~~~~~~~

.. code-block:: bash

   # Relative date keywords
   yt time log ISSUE-123 "2h" --date "today"
   yt time log ISSUE-123 "1h" --date "yesterday"

Work Types
----------

Common work type classifications for better time categorization:

Development Work
~~~~~~~~~~~~~~~

.. code-block:: bash

   # Development-related activities
   yt time log ISSUE-123 "4h" --work-type "Development" --description "Feature implementation"
   yt time log ISSUE-123 "2h" --work-type "Coding" --description "Bug fixes"
   yt time log ISSUE-123 "1h" --work-type "Code Review" --description "PR review"

Testing Activities
~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Testing and QA work
   yt time log ISSUE-123 "2h" --work-type "Testing" --description "Manual testing"
   yt time log ISSUE-123 "1h" --work-type "QA" --description "Test case creation"
   yt time log ISSUE-123 "30m" --work-type "Automation" --description "Test automation"

Documentation
~~~~~~~~~~~~

.. code-block:: bash

   # Documentation activities
   yt time log ISSUE-123 "1h" --work-type "Documentation" --description "API documentation"
   yt time log ISSUE-123 "45m" --work-type "Writing" --description "User guide updates"

Analysis and Planning
~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Analysis and planning activities
   yt time log ISSUE-123 "2h" --work-type "Analysis" --description "Requirements analysis"
   yt time log ISSUE-123 "1h" --work-type "Planning" --description "Sprint planning"
   yt time log ISSUE-123 "30m" --work-type "Research" --description "Technology research"

Common Workflows
----------------

Daily Time Logging
~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Morning time logging routine
   yt time log ISSUE-123 "2h" --description "Feature development" --work-type "Development"
   yt time log ISSUE-456 "1h" --description "Bug investigation" --work-type "Analysis"
   yt time log ISSUE-789 "30m" --description "Code review" --work-type "Review"

   # Log time for yesterday if forgotten
   yt time log ISSUE-123 "4h" --date "yesterday" --description "Feature completion"

Historical Time Entry
~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Log time for previous dates
   yt time log ISSUE-123 "8h" --date "2024-01-15" --description "Major feature work"
   yt time log ISSUE-123 "4h" --date "2024-01-16" --description "Testing and fixes"
   yt time log ISSUE-123 "2h" --date "2024-01-17" --description "Documentation"

Time Reporting and Analysis
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Weekly time report
   yt time report --start-date "2024-01-15" --end-date "2024-01-21"

   # Monthly summary by user
   yt time summary --start-date "2024-01-01" --end-date "2024-01-31" --group-by user

   # Project time analysis
   yt time report --issue-id PROJECT-* --format json > project_time.json

   # Individual productivity report
   yt time summary --user-id john.doe --group-by type --start-date "2024-01-01"

Sprint Time Tracking
~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Track time during sprint
   yt time log SPRINT-ISSUE-1 "6h" --work-type "Development" --description "Story implementation"
   yt time log SPRINT-ISSUE-2 "2h" --work-type "Testing" --description "Acceptance testing"

   # Sprint summary report
   yt time summary --start-date "2024-01-15" --end-date "2024-01-29" --group-by issue

   # Team sprint velocity analysis
   yt time report --start-date "2024-01-15" --end-date "2024-01-29" --format json

Billing and Client Reporting
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Client-specific time tracking
   yt time log CLIENT-ISSUE-123 "4h" --work-type "Consulting" --description "Requirements gathering"

   # Generate billable hours report
   yt time report --start-date "2024-01-01" --end-date "2024-01-31" --format json

   # Export for billing system
   yt time summary --group-by user --format json > billing_report.json

Best Practices
--------------

1. **Regular Logging**: Log time daily to ensure accuracy and completeness.

2. **Descriptive Entries**: Use clear, meaningful descriptions for time entries.

3. **Consistent Work Types**: Use standardized work type categories across the team.

4. **Accurate Duration**: Be honest and accurate with time duration estimates.

5. **Historical Accuracy**: Log time for the actual date work was performed.

6. **Granular Tracking**: Break down large tasks into smaller, trackable components.

7. **Team Standards**: Establish team conventions for work types and descriptions.

8. **Regular Reviews**: Review time entries for accuracy and completeness.

9. **Reporting Cadence**: Generate regular reports for project and team insights.

10. **Integration**: Use time data for sprint planning and capacity estimation.

Reporting and Analytics
----------------------

Time Summary Reports
~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Team productivity overview
   yt time summary --group-by user --start-date "2024-01-01" --end-date "2024-01-31"

   # Project effort analysis
   yt time summary --group-by issue --start-date "2024-01-01" --end-date "2024-01-31"

   # Work type distribution
   yt time summary --group-by type --start-date "2024-01-01" --end-date "2024-01-31"

Detailed Time Reports
~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Individual performance report
   yt time report --user-id john.doe --start-date "2024-01-01" --end-date "2024-03-31"

   # Issue-specific time tracking
   yt time report --issue-id MAJOR-FEATURE-123

   # Team time allocation
   yt time report --start-date "2024-01-15" --end-date "2024-01-21" --format json

Export and Integration
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Export for external systems
   yt time report --format json --start-date "2024-01-01" > time_export.json

   # Generate CSV-compatible data
   yt time summary --format json | jq -r '.[] | [.user, .duration, .count] | @csv'

   # Billing system integration
   yt time report --user-id contractor --format json > contractor_hours.json

Output Formats
--------------

Table Format (Default)
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

   ┌─────────────┬──────────┬────────────┬─────────────────┬─────────────────────┐
   │ Issue       │ Duration │ Work Type  │ Author          │ Description         │
   ├─────────────┼──────────┼────────────┼─────────────────┼─────────────────────┤
   │ ISSUE-123   │ 2h       │ Development│ John Doe        │ Feature impl        │
   │ ISSUE-456   │ 1h 30m   │ Testing    │ Jane Smith      │ Manual testing      │
   │ ISSUE-789   │ 45m      │ Review     │ Bob Wilson      │ Code review         │
   └─────────────┴──────────┴────────────┴─────────────────┴─────────────────────┘

JSON Format
~~~~~~~~~~~

.. code-block:: json

   [
     {
       "id": "time-entry-1",
       "duration": 120,
       "date": "2024-01-15",
       "description": "Feature implementation",
       "author": {
         "id": "user-1",
         "fullName": "John Doe"
       },
       "issue": {
         "id": "ISSUE-123",
         "summary": "Implement new feature"
       },
       "type": {
         "name": "Development"
       }
     }
   ]

Summary Format
~~~~~~~~~~~~~

.. code-block:: text

   Time Summary (Grouped by User)
   ┌─────────────────┬───────────────┬─────────────┬─────────────────┐
   │ User            │ Total Time    │ Entries     │ Average/Entry   │
   ├─────────────────┼───────────────┼─────────────┼─────────────────┤
   │ John Doe        │ 40h 30m       │ 23          │ 1h 45m          │
   │ Jane Smith      │ 35h 15m       │ 19          │ 1h 51m          │
   │ Bob Wilson      │ 28h 45m       │ 15          │ 1h 55m          │
   └─────────────────┴───────────────┴─────────────┴─────────────────┘

Error Handling
--------------

Common error scenarios and solutions:

**Invalid Duration Format**
  Ensure duration follows supported formats (2h, 1h 30m, 90m, etc.).

**Issue Not Found**
  Verify the issue ID exists and you have access to log time against it.

**Invalid Date Format**
  Use supported date formats (YYYY-MM-DD, MM/DD/YYYY, DD.MM.YYYY, etc.).

**Permission Denied**
  Ensure you have permission to log time on the specified issue.

**Future Date Entry**
  Some organizations may restrict logging time for future dates.

**Duplicate Entries**
  Be careful not to log duplicate time entries for the same work.

**Invalid Work Type**
  Verify work type names match your organization's standards.

Performance Optimization
-----------------------

.. code-block:: bash

   # Limit report scope for better performance
   yt time report --start-date "2024-01-01" --end-date "2024-01-31" --top 100

   # Use specific filters to reduce data volume
   yt time report --user-id specific.user --issue-id ISSUE-123

   # Export large datasets in JSON for processing
   yt time report --format json --start-date "2024-01-01" > large_export.json

See Also
--------

* :doc:`issues` - Issue management and workflow
* :doc:`projects` - Project management and organization
* :doc:`reports` - Additional reporting capabilities
* :doc:`users` - User management for time tracking
* :doc:`boards` - Agile board integration with time tracking
