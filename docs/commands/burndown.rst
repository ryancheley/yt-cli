Burndown Command
================

The ``yt burndown`` command provides quick access to burndown report generation functionality. This is a flatter alternative to ``yt reports burndown`` that generates burndown reports for projects or sprints in a more convenient format.

.. contents:: Table of Contents
   :local:
   :depth: 2

Overview
--------

The burndown command allows you to:

* Generate burndown reports for projects to track work completion over time
* Create sprint-specific burndown charts for agile workflow monitoring
* Analyze project progress with customizable date ranges
* Export burndown data for further analysis and presentation

A burndown report shows the amount of work remaining over time, helping teams track progress toward sprint or project completion goals.

Base Command
------------

.. code-block:: bash

   yt burndown PROJECT_ID [OPTIONS]

Command Arguments and Options
-----------------------------

**Arguments:**
  * ``PROJECT_ID`` - The ID of the project to generate the burndown report for

**Options:**
  * ``-s, --sprint TEXT`` - Sprint ID or name to filter by (optional)
  * ``--start-date TEXT`` - Start date in YYYY-MM-DD format (optional)
  * ``--end-date TEXT`` - End date in YYYY-MM-DD format (optional)

**Examples:**

.. code-block:: bash

   # Generate burndown report for a project
   yt burndown DEMO

   # Generate report for specific sprint
   yt burndown WEB-PROJECT --sprint "Sprint 1"

   # Generate report for date range
   yt burndown API --start-date 2024-01-01 --end-date 2024-01-31

   # Generate sprint burndown with custom date range
   yt burndown MOBILE --sprint "Sprint 3" --start-date 2024-02-01 --end-date 2024-02-15

Understanding Burndown Reports
------------------------------

What is a Burndown Report?
~~~~~~~~~~~~~~~~~~~~~~~~~~

A burndown report is a visual representation of work completed versus time remaining in a project or sprint. It typically shows:

* **Ideal Burndown Line:** The theoretical perfect pace of work completion
* **Actual Burndown Line:** The real progress being made by the team
* **Remaining Work:** The amount of work (usually in hours or story points) left to complete
* **Time Axis:** The timeframe being analyzed (sprint duration or project timeline)

Report Components
~~~~~~~~~~~~~~~~~

Burndown reports typically include:

**Work Metrics:**
  * Total work planned (initial scope)
  * Work completed each day/period
  * Work remaining at each point in time
  * Work added or removed (scope changes)

**Time Tracking:**
  * Sprint or project start date
  * Current date and progress
  * Sprint or project end date
  * Velocity trends and predictions

**Visual Elements:**
  * Burndown chart showing trend lines
  * Data tables with daily/periodic breakdowns
  * Progress indicators and completion percentages
  * Variance analysis from ideal burndown

Report Types and Filtering
---------------------------

Project-Level Burndown
~~~~~~~~~~~~~~~~~~~~~~

Generate reports for entire projects:

.. code-block:: bash

   # Complete project burndown
   yt burndown PROJECT-123

   # Project burndown for specific period
   yt burndown PROJECT-123 --start-date 2024-01-01 --end-date 2024-03-31

**Use Cases:**
  * Long-term project tracking and milestone management
  * Release planning and scope management
  * Resource allocation and capacity planning
  * Executive reporting and project health monitoring

Sprint-Specific Burndown
~~~~~~~~~~~~~~~~~~~~~~~~

Focus on individual sprint performance:

.. code-block:: bash

   # Current sprint burndown
   yt burndown AGILE-PROJ --sprint "Current Sprint"

   # Historical sprint analysis
   yt burndown AGILE-PROJ --sprint "Sprint 5"

   # Sprint with custom date bounds
   yt burndown SCRUM-TEAM --sprint "Sprint 2" --start-date 2024-02-01

**Use Cases:**
  * Daily standup meeting insights
  * Sprint retrospective analysis
  * Team velocity tracking
  * Agile process improvement

Date Range Filtering
~~~~~~~~~~~~~~~~~~~~

Customize analysis periods:

.. code-block:: bash

   # Quarter analysis
   yt burndown ENTERPRISE --start-date 2024-01-01 --end-date 2024-03-31

   # Month-over-month comparison
   yt burndown PRODUCT --start-date 2024-01-01 --end-date 2024-01-31
   yt burndown PRODUCT --start-date 2024-02-01 --end-date 2024-02-29

**Benefits:**
  * Custom reporting periods for business cycles
  * Flexible analysis windows for different stakeholder needs
  * Historical trend analysis and comparison
  * Seasonal or cyclical pattern identification

Integration with Reports Command
--------------------------------

The ``yt burndown`` command is functionally identical to ``yt reports burndown``. Both commands provide the same burndown report generation capabilities:

.. code-block:: bash

   # These commands are equivalent:
   yt burndown DEMO --sprint "Sprint 1"
   yt reports burndown DEMO --sprint "Sprint 1"

Choose the command style that fits your workflow:

* Use ``yt burndown`` for quick, direct access to burndown reports
* Use ``yt reports burndown`` when working with other reporting operations

Use Cases and Applications
--------------------------

Agile Team Management
~~~~~~~~~~~~~~~~~~~~~

Daily and sprint-level insights for agile teams:

.. code-block:: bash

   # Daily standup burndown check
   yt burndown SCRUM-TEAM --sprint "Current Sprint"

   # End-of-sprint retrospective analysis
   yt burndown SCRUM-TEAM --sprint "Sprint 3"

**Benefits:**
  * Identify scope creep and changing requirements
  * Track team velocity and capacity
  * Predict sprint completion likelihood
  * Facilitate data-driven sprint planning

Project Portfolio Management
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

High-level project tracking for managers:

.. code-block:: bash

   # Quarterly project review
   for project in WEB API MOBILE; do
       echo "=== $project Burndown ==="
       yt burndown $project --start-date 2024-01-01 --end-date 2024-03-31
   done

**Applications:**
  * Resource allocation and capacity planning
  * Project timeline and milestone tracking
  * Risk identification and mitigation planning
  * Stakeholder communication and reporting

Performance Analysis and Optimization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Understanding team and project performance patterns:

.. code-block:: bash

   # Sprint velocity comparison
   yt burndown TEAM-A --sprint "Sprint 1"
   yt burndown TEAM-A --sprint "Sprint 2"
   yt burndown TEAM-A --sprint "Sprint 3"

**Insights:**
  * Team productivity trends over time
  * Impact of process changes on velocity
  * Seasonal or cyclical performance patterns
  * Capacity planning for future sprints

Best Practices
--------------

**Regular Monitoring:**
  * Review burndown reports daily during active sprints
  * Generate weekly project-level burndown reports for ongoing projects
  * Create monthly burndown summaries for stakeholder communications

**Data Accuracy:**
  * Ensure work items are properly estimated and tracked
  * Update issue status and time tracking consistently
  * Maintain accurate sprint boundaries and scope definitions

**Analysis and Action:**
  * Look for trends and patterns rather than daily fluctuations
  * Identify bottlenecks and impediments early in the sprint
  * Use burndown data to inform future sprint planning and capacity decisions

**Reporting and Communication:**
  * Share burndown reports with stakeholders regularly
  * Use burndown trends to facilitate retrospective discussions
  * Combine burndown data with other metrics for comprehensive project health assessment

Automation and Integration
--------------------------

Automated Reporting
~~~~~~~~~~~~~~~~~~~

Create automated burndown reports for regular distribution:

.. code-block:: bash

   #!/bin/bash
   # Daily burndown report automation

   DATE=$(date +%Y-%m-%d)
   PROJECTS=("WEB" "API" "MOBILE")

   echo "=== Daily Burndown Report - $DATE ==="
   for project in "${PROJECTS[@]}"; do
       echo "--- $project ---"
       yt burndown $project --sprint "Current Sprint"
       echo
   done

CI/CD Integration
~~~~~~~~~~~~~~~~~

Integrate burndown monitoring into development workflows:

.. code-block:: bash

   # Sprint health check in CI pipeline
   BURNDOWN_STATUS=$(yt burndown PROJECT-123 --sprint "Current Sprint" --format json)
   REMAINING_WORK=$(echo $BURNDOWN_STATUS | jq '.remaining_work')

   if [ "$REMAINING_WORK" -gt 100 ]; then
       echo "Warning: Sprint burndown shows high remaining work"
   fi

Dashboard and Visualization
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Export burndown data for custom dashboards:

.. code-block:: bash

   # Export burndown data for visualization tools
   yt burndown PROJECT-123 --format json > burndown-data.json

   # Process data for dashboard consumption
   cat burndown-data.json | jq '.daily_progress[] | {date, remaining, completed}' > dashboard-input.json

Troubleshooting
---------------

Common Issues
~~~~~~~~~~~~~

**Missing Data:**
  * Verify project ID exists and is accessible
  * Check that issues in the project have proper time tracking
  * Ensure sprint names match exactly (case-sensitive)

**Date Range Problems:**
  * Use YYYY-MM-DD format for all date parameters
  * Ensure start date is before end date
  * Verify date ranges include actual work periods

**Permission Issues:**
  * Confirm you have read access to the specified project
  * Verify you can view issues and time tracking data
  * Check that reporting permissions are enabled for your account

Authentication
--------------

Burndown reports require authentication and appropriate permissions. Make sure you're logged in:

.. code-block:: bash

   yt auth login

See Also
--------

* :doc:`reports` - Complete reporting functionality including other report types
* :doc:`velocity` - Sprint velocity analysis and reporting
* :doc:`time` - Time tracking operations that feed burndown calculations
* :doc:`projects` - Project management and configuration
