Reports Command Group
=====================

The ``yt reports`` command group provides comprehensive reporting capabilities for generating analytics and insights across YouTrack projects. Generate burndown charts, velocity reports, and other project metrics.

.. contents:: Table of Contents
   :local:
   :depth: 2

Overview
--------

YouTrack reporting helps teams analyze project progress, team performance, and process effectiveness. The reports command group allows you to:

* Generate burndown reports for projects and sprints
* Create velocity reports for team performance analysis
* Filter reports by date ranges and specific criteria
* Export report data for further analysis
* Track project completion rates and effort metrics
* Analyze team productivity trends over time

Base Command
------------

.. code-block:: bash

   yt reports [OPTIONS] COMMAND [ARGS]...

Report Types
------------

burndown
~~~~~~~~

Generate burndown reports showing project or sprint progress over time.

.. code-block:: bash

   yt reports burndown PROJECT_ID [OPTIONS]

**Arguments:**

* ``PROJECT_ID`` - The project ID to generate the burndown report for (required)

**Options:**

.. list-table::
   :widths: 20 20 60
   :header-rows: 1

   * - Option
     - Type
     - Description
   * - ``--sprint, -s``
     - string
     - Sprint ID or name to filter by
   * - ``--start-date``
     - string
     - Start date in YYYY-MM-DD format
   * - ``--end-date``
     - string
     - End date in YYYY-MM-DD format

**Examples:**

.. code-block:: bash

   # Generate a burndown report for a project
   yt reports burndown PROJECT-123

   # Generate a burndown report for a specific sprint
   yt reports burndown PROJECT-123 --sprint "Sprint 1"

   # Generate a burndown report for a date range
   yt reports burndown PROJECT-123 --start-date "2024-01-01" --end-date "2024-01-31"

   # Generate a burndown report with all filters combined
   yt reports burndown PROJECT-123 --sprint "Sprint 2" --start-date "2024-02-01" --end-date "2024-02-15"

velocity
~~~~~~~~

Generate velocity reports analyzing team performance across recent sprints.

.. code-block:: bash

   yt reports velocity PROJECT_ID [OPTIONS]

**Arguments:**

* ``PROJECT_ID`` - The project ID to generate the velocity report for (required)

**Options:**

.. list-table::
   :widths: 20 20 60
   :header-rows: 1

   * - Option
     - Type
     - Description
   * - ``--sprints, -n``
     - integer
     - Number of recent sprints to analyze (default: 5)

**Examples:**

.. code-block:: bash

   # Generate a velocity report for the last 5 sprints (default)
   yt reports velocity PROJECT-123

   # Generate a velocity report for the last 10 sprints
   yt reports velocity PROJECT-123 --sprints 10

   # Generate a velocity report for fewer sprints
   yt reports velocity PROJECT-123 --sprints 3

   # Generate velocity reports for multiple projects
   yt reports velocity PROJECT-ALPHA --sprints 5
   yt reports velocity PROJECT-BETA --sprints 5

Report Features and Concepts
---------------------------

Burndown Reports
~~~~~~~~~~~~~~~

**Purpose**
  Track project or sprint progress by showing how work is being completed over time.

**Key Metrics**
  * Total issues in scope
  * Resolved issues over time
  * Remaining issues
  * Completion rate percentage
  * Effort tracking (story points, hours)

**Visual Elements**
  * Progress bars showing completion percentage
  * Trend analysis over the reporting period
  * Comparison against planned timeline

**Use Cases**
  * Sprint progress monitoring
  * Project milestone tracking
  * Team performance assessment
  * Stakeholder reporting

Velocity Reports
~~~~~~~~~~~~~~~

**Purpose**
  Analyze team performance and capacity across multiple sprints for planning.

**Key Metrics**
  * Issues completed per sprint
  * Story points or effort delivered
  * Average velocity over time
  * Velocity trends and patterns
  * Team capacity analysis

**Planning Benefits**
  * Sprint capacity estimation
  * Resource allocation decisions
  * Team performance trends
  * Process improvement insights

**Historical Analysis**
  * Performance consistency
  * Improvement tracking
  * Capacity changes over time
  * Seasonal or cyclical patterns

Report Output and Visualization
------------------------------

Burndown Report Format
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

   Burndown Report: PROJECT-123 (Sprint 1)
   =======================================
   Period: 2024-01-15 to 2024-01-29

   Progress Overview:
   ┌─────────────────┬─────────┬─────────────┬─────────────────┐
   │ Metric          │ Value   │ Target      │ Status          │
   ├─────────────────┼─────────┼─────────────┼─────────────────┤
   │ Total Issues    │ 25      │ 25          │ ✓ On Track      │
   │ Resolved        │ 20      │ 25          │ ⚠ Behind       │
   │ Remaining       │ 5       │ 0           │ ⚠ 5 remaining  │
   │ Completion      │ 80%     │ 100%        │ ⚠ 80% complete │
   └─────────────────┴─────────┴─────────────┴─────────────────┘

   Daily Progress:
   ┌────────────┬─────────────┬─────────────┬─────────────────┐
   │ Date       │ Resolved    │ Remaining   │ Progress Bar    │
   ├────────────┼─────────────┼─────────────┼─────────────────┤
   │ 2024-01-15 │ 0           │ 25          │ ░░░░░░░░░░ 0%   │
   │ 2024-01-18 │ 5           │ 20          │ ██░░░░░░░░ 20%  │
   │ 2024-01-22 │ 12          │ 13          │ ████░░░░░░ 48%  │
   │ 2024-01-25 │ 18          │ 7           │ ███████░░░ 72%  │
   │ 2024-01-29 │ 20          │ 5           │ ████████░░ 80%  │
   └────────────┴─────────────┴─────────────┴─────────────────┘

Velocity Report Format
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

   Velocity Report: PROJECT-123 (Last 5 Sprints)
   =============================================

   Sprint Performance:
   ┌─────────────────┬─────────────┬─────────────┬─────────────────┐
   │ Sprint          │ Completed   │ Planned     │ Velocity        │
   ├─────────────────┼─────────────┼─────────────┼─────────────────┤
   │ Sprint 1        │ 23 issues   │ 25 issues   │ 92% (Good)      │
   │ Sprint 2        │ 27 issues   │ 25 issues   │ 108% (Excellent)│
   │ Sprint 3        │ 22 issues   │ 25 issues   │ 88% (Good)      │
   │ Sprint 4        │ 25 issues   │ 25 issues   │ 100% (Perfect)  │
   │ Sprint 5        │ 24 issues   │ 25 issues   │ 96% (Excellent) │
   └─────────────────┴─────────────┴─────────────┴─────────────────┘

   Summary Metrics:
   ┌─────────────────────┬─────────────────┐
   │ Metric              │ Value           │
   ├─────────────────────┼─────────────────┤
   │ Average Velocity    │ 24.2 issues     │
   │ Best Sprint         │ Sprint 2 (27)   │
   │ Consistency Rating  │ High (94%)      │
   │ Trend               │ ↗ Improving     │
   └─────────────────────┴─────────────────┘

Common Workflows
----------------

Sprint Monitoring
~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Daily sprint burndown check
   yt reports burndown PROJECT-WEB --sprint "Sprint 3"

   # Weekly sprint progress review
   yt reports burndown PROJECT-API --sprint "Current Sprint" \
     --start-date "2024-01-15" --end-date "2024-01-21"

   # End-of-sprint analysis
   yt reports burndown PROJECT-MOBILE --sprint "Sprint 2" \
     --start-date "2024-01-01" --end-date "2024-01-14"

Project Tracking
~~~~~~~~~~~~~~~

.. code-block:: bash

   # Monthly project progress
   yt reports burndown PROJECT-ALPHA --start-date "2024-01-01" --end-date "2024-01-31"

   # Quarterly project review
   yt reports burndown PROJECT-BETA --start-date "2024-01-01" --end-date "2024-03-31"

   # Custom date range analysis
   yt reports burndown PROJECT-GAMMA --start-date "2024-02-15" --end-date "2024-03-15"

Team Performance Analysis
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Standard velocity analysis (5 sprints)
   yt reports velocity PROJECT-DEV

   # Extended velocity trend (10 sprints)
   yt reports velocity PROJECT-QA --sprints 10

   # Short-term velocity check (3 sprints)
   yt reports velocity PROJECT-OPS --sprints 3

   # Compare multiple team velocities
   yt reports velocity TEAM-A-PROJECT --sprints 5
   yt reports velocity TEAM-B-PROJECT --sprints 5

Release Planning
~~~~~~~~~~~~~~~

.. code-block:: bash

   # Pre-release burndown analysis
   yt reports burndown RELEASE-PROJECT --start-date "2024-01-01" --end-date "2024-03-31"

   # Sprint planning using velocity data
   yt reports velocity PLANNING-PROJECT --sprints 8

   # Milestone progress tracking
   yt reports burndown MILESTONE-PROJECT --sprint "Milestone 1"

Stakeholder Reporting
~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Weekly stakeholder update
   yt reports burndown STAKEHOLDER-PROJECT --start-date "$(date -d '7 days ago' +%Y-%m-%d)" --end-date "$(date +%Y-%m-%d)"

   # Monthly executive summary
   yt reports velocity EXECUTIVE-PROJECT --sprints 6

   # Quarterly business review
   yt reports burndown QBR-PROJECT --start-date "2024-01-01" --end-date "2024-03-31"

Best Practices
--------------

1. **Regular Monitoring**: Generate reports regularly to identify trends and issues early.

2. **Consistent Timeframes**: Use consistent reporting periods for meaningful comparisons.

3. **Multiple Perspectives**: Combine burndown and velocity reports for comprehensive insights.

4. **Historical Context**: Keep historical reports for trend analysis and process improvement.

5. **Team Collaboration**: Share reports with team members for transparency and accountability.

6. **Data Quality**: Ensure issue tracking and sprint management is accurate for reliable reports.

7. **Action-Oriented**: Use reports to drive decisions and process improvements.

8. **Stakeholder Communication**: Tailor report frequency and detail to audience needs.

9. **Continuous Improvement**: Use velocity trends to optimize team processes and capacity.

10. **Documentation**: Document report methodology and interpretation guidelines.

Report Analysis Guidelines
--------------------------

Burndown Analysis
~~~~~~~~~~~~~~~

**Healthy Patterns**
  * Steady, consistent progress toward completion
  * Remaining work decreases predictably over time
  * Completion rate aligns with planned timeline

**Warning Signs**
  * Flat or increasing remaining work
  * Large jumps in completion without corresponding work
  * Significant deviation from planned burn rate

**Action Items**
  * Investigate blockers and impediments
  * Reassess scope and priorities
  * Adjust resources or timeline if needed

Velocity Analysis
~~~~~~~~~~~~~~~

**Positive Indicators**
  * Consistent delivery across sprints
  * Gradual improvement in velocity over time
  * Predictable capacity for planning

**Concerning Trends**
  * Declining velocity over multiple sprints
  * High variability between sprints
  * Consistently missing planned capacity

**Improvement Actions**
  * Identify and remove impediments
  * Optimize team processes and workflows
  * Adjust sprint planning based on actual capacity

Performance Metrics
------------------

Burndown Metrics
~~~~~~~~~~~~~~

**Completion Rate**
  Percentage of planned work completed within the timeframe.

**Burn Rate**
  Average rate of work completion per day or sprint.

**Scope Changes**
  Track additions or removals from original scope.

**Time to Completion**
  Projected completion date based on current progress.

Velocity Metrics
~~~~~~~~~~~~~~

**Average Velocity**
  Mean completion rate across analyzed sprints.

**Velocity Trend**
  Direction and magnitude of velocity changes over time.

**Consistency Score**
  Measure of velocity predictability and stability.

**Capacity Utilization**
  Ratio of actual to planned delivery capacity.

Error Handling
--------------

Common error scenarios and solutions:

**Project Not Found**
  Verify the project ID exists and you have access to view project data.

**Insufficient Data**
  Ensure the project has enough historical data for meaningful reports.

**Date Range Issues**
  Check that start dates are before end dates and within valid ranges.

**Sprint Not Found**
  Verify sprint names or IDs exist within the specified project.

**Permission Denied**
  Ensure you have appropriate permissions to view project reporting data.

**No Data Available**
  Check that the project has issues and activity within the specified timeframe.

Integration and Automation
--------------------------

Automated Reporting
~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   #!/bin/bash
   # Daily burndown report automation

   PROJECT_ID="PROJECT-123"
   CURRENT_SPRINT="Sprint 3"

   # Generate daily burndown
   yt reports burndown "$PROJECT_ID" --sprint "$CURRENT_SPRINT" > daily_burndown.txt

   # Email to stakeholders
   mail -s "Daily Burndown Report" stakeholders@company.com < daily_burndown.txt

Weekly Reporting
~~~~~~~~~~~~~~~

.. code-block:: bash

   #!/bin/bash
   # Weekly velocity and burndown summary

   PROJECTS=("PROJECT-A" "PROJECT-B" "PROJECT-C")

   for project in "${PROJECTS[@]}"; do
     echo "=== $project Report ===" >> weekly_report.txt
     yt reports velocity "$project" --sprints 3 >> weekly_report.txt
     yt reports burndown "$project" --start-date "$(date -d '7 days ago' +%Y-%m-%d)" >> weekly_report.txt
     echo "" >> weekly_report.txt
   done

Data Export for Analysis
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Export report data for external analysis
   PROJECT="ANALYSIS-PROJECT"

   # Generate multiple report types
   yt reports burndown "$PROJECT" --start-date "2024-01-01" --end-date "2024-03-31" > burndown_q1.txt
   yt reports velocity "$PROJECT" --sprints 12 > velocity_annual.txt

   # Process for dashboard systems
   # (Additional processing scripts would parse the output for BI tools)

Limitations
-----------

* Report generation depends on proper issue tracking and sprint setup
* Historical data availability may limit report scope
* Complex custom reports may require additional tools
* Real-time reporting may have data refresh delays

Future Enhancements
------------------

* Additional report types (cycle time, lead time, etc.)
* Custom report templates and configurations
* Export to common formats (PDF, Excel, etc.)
* Integration with external analytics platforms
* Automated report scheduling and distribution

See Also
--------

* :doc:`projects` - Project management and organization
* :doc:`issues` - Issue tracking for accurate reporting
* :doc:`time` - Time tracking integration with reports
* :doc:`boards` - Agile board workflow and sprint management
* :doc:`admin` - Administrative settings affecting reporting
