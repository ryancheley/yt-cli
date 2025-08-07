Velocity Command
================

The ``yt velocity`` command provides quick access to velocity report generation functionality. This is a flatter alternative to ``yt reports velocity`` that generates velocity reports for recent sprints to help teams understand their delivery capacity and performance trends.

.. contents:: Table of Contents
   :local:
   :depth: 2

Overview
--------

The velocity command allows you to:

* Generate velocity reports analyzing team performance across multiple sprints
* Track team delivery capacity and consistency over time
* Identify trends in team productivity and sprint completion rates
* Make data-driven decisions for sprint planning and capacity estimation

Velocity reports show how much work a team completes in each sprint, helping predict future capacity and improve sprint planning accuracy.

Base Command
------------

.. code-block:: bash

   yt velocity PROJECT_ID [OPTIONS]

Command Arguments and Options
-----------------------------

**Arguments:**
  * ``PROJECT_ID`` - The ID of the project to generate the velocity report for

**Options:**
  * ``-n, --sprints INTEGER`` - Number of recent sprints to analyze (default: 5)

**Examples:**

.. code-block:: bash

   # Generate velocity report for last 5 sprints (default)
   yt velocity PROJECT-123

   # Generate velocity report for last 10 sprints
   yt velocity PROJECT-123 --sprints 10

   # Analyze recent sprint performance with shorter history
   yt velocity AGILE-TEAM --sprints 3

   # Long-term velocity analysis
   yt velocity ENTERPRISE -n 20

Understanding Velocity Reports
------------------------------

What is Team Velocity?
~~~~~~~~~~~~~~~~~~~~~~

Team velocity measures the amount of work a development team completes in a given sprint, typically measured in:

* **Story Points:** Abstract units representing work complexity and effort
* **Hours:** Actual time spent on completed work items
* **Issue Count:** Number of issues or tickets completed per sprint
* **Custom Metrics:** Project-specific measurements of work completion

**Key Velocity Metrics:**
  * **Average Velocity:** Mean work completion across analyzed sprints
  * **Velocity Trend:** Whether team velocity is increasing, decreasing, or stable
  * **Velocity Consistency:** How much velocity varies between sprints
  * **Capacity Utilization:** How much of planned work is actually completed

Velocity Report Components
~~~~~~~~~~~~~~~~~~~~~~~~~

A comprehensive velocity report typically includes:

**Sprint-by-Sprint Breakdown:**
  * Individual sprint performance data
  * Work planned vs. work completed for each sprint
  * Sprint goal achievement rates
  * Notable events or impediments affecting velocity

**Statistical Analysis:**
  * Average velocity across the analyzed period
  * Velocity range (minimum and maximum values)
  * Standard deviation and consistency metrics
  * Trend analysis and velocity trajectory

**Predictive Insights:**
  * Recommended sprint capacity for future planning
  * Confidence intervals for delivery predictions
  * Risk factors and capacity planning considerations

Report Analysis and Interpretation
-----------------------------------

Sprint Count Selection
~~~~~~~~~~~~~~~~~~~~~

Choose the appropriate number of sprints to analyze based on your needs:

**Short-term Analysis (3-5 sprints):**

.. code-block:: bash

   # Recent performance for immediate planning
   yt velocity CURRENT-TEAM --sprints 5

**Benefits:**
  * Reflects current team composition and processes
  * More relevant for immediate sprint planning decisions
  * Less influenced by historical changes in team or process

**Medium-term Analysis (6-12 sprints):**

.. code-block:: bash

   # Balanced view for quarterly planning
   yt velocity STABLE-TEAM --sprints 10

**Benefits:**
  * Balances recent performance with historical context
  * Good for quarterly and release planning
  * Provides statistical significance while remaining current

**Long-term Analysis (13+ sprints):**

.. code-block:: bash

   # Historical trends for strategic planning
   yt velocity MATURE-TEAM --sprints 20

**Benefits:**
  * Identifies long-term trends and patterns
  * Useful for annual planning and capacity modeling
  * Provides statistically significant data for predictions

Velocity Trend Analysis
~~~~~~~~~~~~~~~~~~~~~~

Understanding velocity trends helps inform planning decisions:

**Increasing Velocity:**
  * Team maturity and process improvements
  * Better estimation accuracy over time
  * Improved collaboration and efficiency
  * Technology or tooling improvements

**Decreasing Velocity:**
  * Team changes or skill gaps
  * Increasing technical debt impact
  * Process or tooling impediments
  * Scope complexity increases

**Stable Velocity:**
  * Mature team with consistent processes
  * Reliable capacity for predictable planning
  * Well-established estimation practices
  * Balanced workload and sustainable pace

Integration with Reports Command
--------------------------------

The ``yt velocity`` command is functionally identical to ``yt reports velocity``. Both commands provide the same velocity report generation capabilities:

.. code-block:: bash

   # These commands are equivalent:
   yt velocity PROJECT-123 --sprints 8
   yt reports velocity PROJECT-123 --sprints 8

Choose the command style that fits your workflow:

* Use ``yt velocity`` for quick, direct access to velocity reports
* Use ``yt reports velocity`` when working with other reporting operations

Use Cases and Applications
--------------------------

Sprint Planning and Capacity Management
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use velocity data to inform sprint planning decisions:

.. code-block:: bash

   # Check team velocity before sprint planning
   yt velocity SCRUM-TEAM --sprints 6

**Planning Applications:**
  * Determine realistic sprint capacity based on historical performance
  * Adjust sprint scope based on velocity trends and team changes
  * Set achievable sprint goals and manage stakeholder expectations
  * Plan release timelines based on predictable velocity patterns

Team Performance Monitoring
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Track team performance and identify improvement opportunities:

.. code-block:: bash

   # Monthly team performance review
   yt velocity DEVELOPMENT-TEAM --sprints 4

**Monitoring Benefits:**
  * Identify when team changes affect productivity
  * Measure impact of process improvements or tool changes
  * Recognize and address performance impediments early
  * Celebrate team growth and increasing effectiveness

Release and Portfolio Planning
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use velocity data for higher-level planning activities:

.. code-block:: bash

   # Portfolio planning with multiple teams
   for team in TEAM-A TEAM-B TEAM-C; do
       echo "=== $team Velocity ==="
       yt velocity $team --sprints 8
   done

**Strategic Applications:**
  * Allocate work across multiple teams based on capacity
  * Plan feature delivery timelines for product roadmaps
  * Make informed decisions about resource allocation
  * Manage portfolio risk with velocity-based predictions

Process Improvement and Retrospectives
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Support continuous improvement with velocity insights:

.. code-block:: bash

   # Retrospective preparation with velocity context
   yt velocity AGILE-TEAM --sprints 3

**Improvement Areas:**
  * Identify sprints with velocity outliers for deeper analysis
  * Correlate velocity changes with process or team changes
  * Use velocity data to validate improvement hypotheses
  * Track the impact of retrospective action items on team performance

Best Practices
--------------

**Data Quality and Consistency:**
  * Ensure consistent sprint boundaries and duration
  * Maintain consistent estimation practices across sprints
  * Update issue status and completion data promptly
  * Use the same velocity metrics consistently over time

**Analysis and Interpretation:**
  * Consider context when interpreting velocity changes
  * Look for patterns over multiple sprints rather than single-sprint variations
  * Factor in team composition changes, holidays, and external factors
  * Use velocity as one input among many for planning decisions

**Communication and Action:**
  * Share velocity reports with the entire team during planning
  * Discuss velocity trends during retrospectives
  * Use velocity data to have data-driven conversations about capacity
  * Avoid using velocity as a performance measurement tool for individuals

**Continuous Improvement:**
  * Regularly review and adjust the number of sprints in your analysis
  * Correlate velocity changes with process improvements or impediments
  * Use velocity trends to inform experiments and process changes
  * Track the impact of team development and training on velocity

Automation and Integration
--------------------------

Automated Velocity Tracking
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create automated velocity monitoring for regular team insights:

.. code-block:: bash

   #!/bin/bash
   # Sprint planning velocity check

   TEAM_PROJECTS=("SCRUM-A" "SCRUM-B" "KANBAN-C")

   echo "=== Team Velocity Report ==="
   echo "Generated: $(date)"

   for project in "${TEAM_PROJECTS[@]}"; do
       echo "--- $project Team ---"
       yt velocity $project --sprints 6
       echo
   done

Sprint Planning Integration
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Integrate velocity data into sprint planning workflows:

.. code-block:: bash

   # Pre-planning velocity analysis
   CURRENT_VELOCITY=$(yt velocity PROJECT-123 --sprints 3 --format json | jq '.average_velocity')

   echo "Team average velocity: $CURRENT_VELOCITY"
   echo "Recommended sprint capacity: $(echo "$CURRENT_VELOCITY * 0.8" | bc)"

Performance Dashboard Creation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Export velocity data for team dashboards and visualization:

.. code-block:: bash

   # Export velocity data for dashboard
   yt velocity TEAM-PROJECT --sprints 12 --format json > velocity-dashboard-data.json

   # Create summary metrics
   cat velocity-dashboard-data.json | jq '{
       average: .average_velocity,
       trend: .velocity_trend,
       last_sprint: .recent_sprints[0].velocity,
       consistency: .velocity_consistency
   }' > team-metrics.json

Comparative Analysis
--------------------

Multi-Team Velocity Comparison
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Compare velocity across multiple teams:

.. code-block:: bash

   #!/bin/bash
   # Multi-team velocity comparison

   TEAMS=("FRONTEND" "BACKEND" "MOBILE" "QA")

   echo "Team Velocity Comparison"
   printf "%-12s %-15s %-15s %-15s\n" "Team" "Avg Velocity" "Last Sprint" "Trend"
   echo "--------------------------------------------------------"

   for team in "${TEAMS[@]}"; do
       VELOCITY_DATA=$(yt velocity $team --sprints 5 --format json)
       AVG=$(echo $VELOCITY_DATA | jq -r '.average_velocity')
       LAST=$(echo $VELOCITY_DATA | jq -r '.recent_sprints[0].velocity')
       TREND=$(echo $VELOCITY_DATA | jq -r '.trend')
       printf "%-12s %-15s %-15s %-15s\n" "$team" "$AVG" "$LAST" "$TREND"
   done

Historical Velocity Analysis
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Track velocity changes over different time periods:

.. code-block:: bash

   # Quarterly velocity comparison
   echo "=== Q1 Velocity (Sprints 1-6) ==="
   yt velocity PROJECT --sprints 6

   echo "=== Q2 Velocity (Sprints 7-12) ==="
   # Note: This would require date-based filtering in actual implementation
   yt velocity PROJECT --sprints 6 --offset 6

Troubleshooting
---------------

Common Issues
~~~~~~~~~~~~~

**Insufficient Data:**
  * Verify the project has completed sprints with tracked work
  * Check that sprints are properly defined and closed
  * Ensure work items have appropriate estimation data

**Inconsistent Results:**
  * Verify sprint boundaries are consistently defined
  * Check for changes in estimation practices over time
  * Ensure completed work is properly marked and tracked

**Performance Issues:**
  * Reduce the number of sprints analyzed if reports are slow
  * Check network connectivity to YouTrack instance
  * Verify you have appropriate read permissions for project data

Data Quality Issues
~~~~~~~~~~~~~~~~~~

**Velocity Anomalies:**
  * Review sprint scope changes and mid-sprint adjustments
  * Check for holidays, team changes, or external factors
  * Verify that completed work is properly tracked and estimated

**Missing Velocity Data:**
  * Confirm sprints have associated work items with estimates
  * Check that work items are marked as completed within sprint boundaries
  * Verify time tracking and estimation data is complete

Authentication
--------------

Velocity reports require authentication and appropriate permissions. Make sure you're logged in:

.. code-block:: bash

   yt auth login

See Also
--------

* :doc:`reports` - Complete reporting functionality including other report types
* :doc:`burndown` - Sprint burndown analysis and tracking
* :doc:`boards` - Agile board management and sprint configuration
* :doc:`projects` - Project management and configuration
