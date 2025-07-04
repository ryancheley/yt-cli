Boards Command Group
====================

The ``yt boards`` command group provides management capabilities for YouTrack agile boards. Agile boards visualize work items and help teams manage their workflow using Kanban or Scrum methodologies.

.. contents:: Table of Contents
   :local:
   :depth: 2

Overview
--------

YouTrack agile boards provide visual workflow management for teams using agile methodologies. The boards command group allows you to:

* List and discover available agile boards
* View detailed board configurations and settings
* Update board properties and settings
* Filter boards by project or other criteria
* Export board data for analysis and reporting

Base Command
------------

.. code-block:: bash

   yt boards [OPTIONS] COMMAND [ARGS]...

Board Management Commands
-------------------------

list
~~~~

List all available agile boards with filtering options.

.. code-block:: bash

   yt boards list [OPTIONS]

**Options:**

.. list-table::
   :widths: 20 20 60
   :header-rows: 1

   * - Option
     - Type
     - Description
   * - ``--project-id, -p``
     - string
     - Filter boards by specific project ID
   * - ``--format``
     - choice
     - Output format: table, json (default: table)

**Examples:**

.. code-block:: bash

   # List all agile boards
   yt boards list

   # List boards for a specific project
   yt boards list --project-id PROJECT-123

   # Export board data in JSON format
   yt boards list --format json

   # Filter and export project-specific boards
   yt boards list --project-id PROJECT-456 --format json

view
~~~~

View detailed information about a specific agile board.

.. code-block:: bash

   yt boards view BOARD_ID [OPTIONS]

**Arguments:**

* ``BOARD_ID`` - The ID of the board to view (required)

**Options:**

.. list-table::
   :widths: 20 20 60
   :header-rows: 1

   * - Option
     - Type
     - Description
   * - ``--format``
     - choice
     - Output format: table, json (default: table)

**Examples:**

.. code-block:: bash

   # View detailed information about a board
   yt boards view BOARD-456

   # Export board details in JSON format
   yt boards view BOARD-456 --format json

   # View multiple boards
   yt boards view BOARD-123
   yt boards view BOARD-456
   yt boards view BOARD-789

update
~~~~~~

Update an agile board's configuration and settings.

.. code-block:: bash

   yt boards update BOARD_ID [OPTIONS]

**Arguments:**

* ``BOARD_ID`` - The ID of the board to update (required)

**Options:**

.. list-table::
   :widths: 20 20 60
   :header-rows: 1

   * - Option
     - Type
     - Description
   * - ``--name, -n``
     - string
     - New name for the board

**Examples:**

.. code-block:: bash

   # Update a board's name
   yt boards update BOARD-456 --name "New Board Name"

   # Rename development board
   yt boards update DEV-BOARD --name "Development Team Board"

   # Update project board name
   yt boards update PROJECT-BOARD-123 --name "Project Alpha Sprint Board"

Board Features and Concepts
---------------------------

Board Types
~~~~~~~~~~~

**Scrum Boards**
  Designed for teams using Scrum methodology with time-boxed sprints:

  * Sprint planning and management
  * Story points and estimation
  * Burndown charts
  * Sprint reviews and retrospectives

**Kanban Boards**
  Designed for continuous flow methodology:

  * Work-in-progress (WIP) limits
  * Cycle time tracking
  * Cumulative flow diagrams
  * Continuous delivery focus

Board Components
~~~~~~~~~~~~~~~

**Columns**
  Represent different stages of work (To Do, In Progress, Done, etc.)

**Swimlanes**
  Horizontal groupings for organizing work by different criteria

**Cards**
  Individual work items (issues) displayed on the board

**Sprints**
  Time-boxed iterations for Scrum boards

**Filters**
  Rules that determine which issues appear on the board

Board Configuration
~~~~~~~~~~~~~~~~~~

**Ownership**
  Boards have owners who can configure settings and permissions

**Project Association**
  Boards are typically associated with one or more projects

**Visibility**
  Board visibility can be controlled for different user groups

**Customization**
  Columns, swimlanes, and appearance can be customized

Common Workflows
----------------

Board Discovery
~~~~~~~~~~~~~~

.. code-block:: bash

   # Discover all available boards
   yt boards list

   # Find boards for a specific project
   yt boards list --project-id WEB-PROJECT

   # Export board inventory for documentation
   yt boards list --format json > board_inventory.json

   # Search for development-related boards
   yt boards list | grep -i "dev"

Board Analysis
~~~~~~~~~~~~~

.. code-block:: bash

   # Analyze board configuration
   yt boards view SCRUM-BOARD-123

   # Compare multiple board configurations
   yt boards view BOARD-A --format json > board_a.json
   yt boards view BOARD-B --format json > board_b.json

   # Export board details for reporting
   yt boards view PROJECT-BOARD --format json

Board Maintenance
~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Update board names for clarity
   yt boards update OLD-BOARD --name "Legacy Project Board"
   yt boards update NEW-BOARD --name "Current Development Board"

   # Rename boards for organizational changes
   yt boards update TEAM-A-BOARD --name "Platform Team Board"
   yt boards update TEAM-B-BOARD --name "Feature Team Board"

Project Board Management
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # List all boards for project organization
   yt boards list --project-id PROJECT-ALPHA
   yt boards list --project-id PROJECT-BETA

   # Document board configurations
   for board in BOARD-1 BOARD-2 BOARD-3; do
     yt boards view "$board" --format json > "board_${board}.json"
   done

   # Update board names for project phases
   yt boards update ALPHA-BOARD --name "Project Alpha - Phase 1"

Best Practices
--------------

1. **Clear Naming**: Use descriptive board names that reflect their purpose and scope.

2. **Project Association**: Ensure boards are properly associated with relevant projects.

3. **Regular Review**: Periodically review board configurations for effectiveness.

4. **Team Ownership**: Assign clear ownership for board maintenance and configuration.

5. **Documentation**: Document board purpose, rules, and workflow for team reference.

6. **Consistency**: Maintain consistent naming and organization across related boards.

7. **Access Control**: Ensure appropriate visibility and permissions for different teams.

8. **Performance**: Monitor board performance and adjust configurations as needed.

9. **Evolution**: Allow boards to evolve with team processes and project needs.

10. **Integration**: Leverage board data for reporting and process improvement.

Board Reporting and Analytics
-----------------------------

Board Inventory
~~~~~~~~~~~~~~

.. code-block:: bash

   # Generate complete board inventory
   yt boards list --format json | jq '.[] | {name: .name, id: .id, project: .project}'

   # Count boards by project
   yt boards list --format json | jq 'group_by(.project) | map({project: .[0].project, count: length})'

   # Export board metadata
   yt boards list --format json > boards_metadata.json

Configuration Analysis
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Analyze board configurations
   yt boards view BOARD-123 --format json | jq '.columns | length'

   # Compare board settings
   diff <(yt boards view BOARD-A --format json) <(yt boards view BOARD-B --format json)

   # Extract board ownership information
   yt boards list --format json | jq '.[] | {name: .name, owner: .owner}'

Performance Monitoring
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Monitor board usage patterns
   yt boards list --format json | jq '.[] | {name: .name, lastModified: .lastModified}'

   # Track board changes over time
   yt boards view ACTIVE-BOARD --format json > "board_snapshot_$(date +%Y%m%d).json"

Output Formats
--------------

Table Format (Default)
~~~~~~~~~~~~~~~~~~~~~~

The default table format provides a clean overview of board information:

.. code-block:: text

   ┌─────────────────────┬──────────────┬─────────────────┬────────────┬─────────────────┐
   │ Name                │ ID           │ Owner           │ Project    │ Columns         │
   ├─────────────────────┼──────────────┼─────────────────┼────────────┼─────────────────┤
   │ Development Board   │ BOARD-123    │ John Doe        │ WEB-PROJ   │ 4               │
   │ Sprint Planning     │ BOARD-456    │ Jane Smith      │ API-PROJ   │ 5               │
   │ Kanban Flow         │ BOARD-789    │ Bob Wilson      │ MOBILE     │ 3               │
   └─────────────────────┴──────────────┴─────────────────┴────────────┴─────────────────┘

JSON Format
~~~~~~~~~~~

JSON format provides structured data for automation and integration:

.. code-block:: json

   [
     {
       "id": "BOARD-123",
       "name": "Development Board",
       "owner": {
         "id": "user-1",
         "login": "john.doe",
         "fullName": "John Doe"
       },
       "project": {
         "id": "WEB-PROJ",
         "name": "Web Project",
         "shortName": "WEB"
       },
       "columns": [
         {"name": "To Do", "id": "col-1"},
         {"name": "In Progress", "id": "col-2"},
         {"name": "Review", "id": "col-3"},
         {"name": "Done", "id": "col-4"}
       ],
       "sprints": [
         {"name": "Sprint 1", "id": "sprint-1", "state": "active"}
       ]
     }
   ]

Board Detail View
~~~~~~~~~~~~~~~~

When viewing a specific board, detailed information is displayed:

.. code-block:: text

   Board: Development Board (BOARD-123)
   =====================================

   Owner: John Doe (john.doe)
   Project: Web Project (WEB-PROJ)
   Type: Scrum
   Created: 2024-01-15

   Columns:
   ┌─────────────┬─────────────────┬─────────────────┐
   │ Name        │ ID              │ WIP Limit       │
   ├─────────────┼─────────────────┼─────────────────┤
   │ To Do       │ col-todo        │ None            │
   │ In Progress │ col-progress    │ 3               │
   │ Review      │ col-review      │ 2               │
   │ Done        │ col-done        │ None            │
   └─────────────┴─────────────────┴─────────────────┘

   Active Sprint: Sprint 3 (2024-01-15 - 2024-01-29)

Error Handling
--------------

Common error scenarios and solutions:

**Board Not Found**
  Verify the board ID exists and you have access to view it.

**Permission Denied**
  Ensure you have appropriate permissions to view or modify the board.

**Invalid Board ID**
  Check that the board ID format is correct and matches existing boards.

**Update Restrictions**
  Some board properties may be restricted based on permissions or board state.

**Project Access**
  Ensure you have access to the project associated with the board.

**Network Issues**
  Check connectivity if boards fail to load or update.

Integration Examples
-------------------

Board Monitoring Script
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   #!/bin/bash
   # Monitor board health and configuration

   echo "Board Health Report - $(date)"
   echo "=============================="

   # List all boards
   BOARDS=$(yt boards list --format json | jq -r '.[].id')

   for board in $BOARDS; do
     echo "Checking board: $board"
     yt boards view "$board" --format json > "/tmp/board_${board}.json"

     # Check for empty boards or configuration issues
     COLUMNS=$(jq '.columns | length' "/tmp/board_${board}.json")
     echo "  Columns: $COLUMNS"
   done

Board Backup Script
~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   #!/bin/bash
   # Backup board configurations

   BACKUP_DIR="board_backups_$(date +%Y%m%d)"
   mkdir -p "$BACKUP_DIR"

   # Export all board configurations
   yt boards list --format json > "$BACKUP_DIR/boards_list.json"

   # Export individual board details
   yt boards list --format json | jq -r '.[].id' | while read board_id; do
     yt boards view "$board_id" --format json > "$BACKUP_DIR/board_${board_id}.json"
   done

   echo "Board backup completed in $BACKUP_DIR"

Project Board Analysis
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   #!/bin/bash
   # Analyze boards by project

   PROJECT_ID="$1"
   if [ -z "$PROJECT_ID" ]; then
     echo "Usage: $0 PROJECT_ID"
     exit 1
   fi

   echo "Board Analysis for Project: $PROJECT_ID"
   echo "======================================="

   # List project boards
   yt boards list --project-id "$PROJECT_ID" --format json > project_boards.json

   # Count boards
   BOARD_COUNT=$(jq '. | length' project_boards.json)
   echo "Total boards: $BOARD_COUNT"

   # List board owners
   echo "Board owners:"
   jq -r '.[] | "\(.name): \(.owner.fullName)"' project_boards.json

Use Cases
---------

Team Organization
~~~~~~~~~~~~~~~~

* **Multi-team Projects**: Use separate boards for different teams working on the same project
* **Feature Teams**: Create boards for specific feature development streams
* **Cross-functional Work**: Set up boards that span multiple projects or components

Workflow Management
~~~~~~~~~~~~~~~~~

* **Process Improvement**: Analyze board configurations to optimize team workflows
* **Standardization**: Ensure consistent board setup across similar teams
* **Compliance**: Monitor board usage for process compliance requirements

Project Management
~~~~~~~~~~~~~~~~~

* **Portfolio View**: Track multiple projects through their associated boards
* **Resource Planning**: Use board data for capacity and resource allocation
* **Progress Tracking**: Monitor project progress through board state changes

Limitations
-----------

* Board creation is not currently supported via CLI
* Advanced board configuration requires web interface access
* Some board features may not be exposed through the API
* Board permissions management is limited through CLI

See Also
--------

* :doc:`projects` - Project management and board association
* :doc:`issues` - Issue management and board workflow
* :doc:`reports` - Reporting capabilities for board analytics
* :doc:`time` - Time tracking integration with board workflow
* :doc:`admin` - Administrative operations for board management
