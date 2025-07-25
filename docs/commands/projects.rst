Projects Command Group
======================

The ``yt projects`` command group provides comprehensive project management capabilities in YouTrack. Projects are containers for issues, articles, and other resources, and serve as the primary organizational unit.

.. contents:: Table of Contents
   :local:
   :depth: 2

Overview
--------

YouTrack projects organize work and resources. The projects command group allows you to:

* List and discover projects
* Create new projects with templates
* Configure project settings and metadata
* Manage project leadership and ownership
* Archive projects when they're completed
* View detailed project information

Base Command
------------

.. code-block:: bash

   yt projects [OPTIONS] COMMAND [ARGS]...

Project Management Commands
---------------------------

list
~~~~

List all projects with filtering and formatting options.

.. code-block:: bash

   yt projects list [OPTIONS]

**Options:**

.. list-table::
   :widths: 20 20 60
   :header-rows: 1

   * - Option
     - Type
     - Description
   * - ``--fields, -f``
     - string
     - Comma-separated list of project fields to return
   * - ``--top, -t``
     - integer
     - Maximum number of projects to return
   * - ``--show-archived``
     - flag
     - Include archived projects in the list
   * - ``--format``
     - choice
     - Output format: table, json (default: table)

**Examples:**

.. code-block:: bash

   # List all active projects
   yt projects list

   # List projects in JSON format
   yt projects list --format json

   # List projects including archived ones
   yt projects list --show-archived

   # Limit number of projects returned
   yt projects list --top 10

   # List with specific fields
   yt projects list --fields "id,name,shortName,leader,archived"

create
~~~~~~

Create a new project with specified settings.

.. code-block:: bash

   yt projects create NAME SHORT_NAME [OPTIONS]

**Arguments:**

* ``NAME`` - The full name of the project (required)
* ``SHORT_NAME`` - The short identifier/key for the project (required)

**Options:**

.. list-table::
   :widths: 20 20 60
   :header-rows: 1

   * - Option
     - Type
     - Description
   * - ``--leader, -l``
     - string
     - Project leader username (e.g., 'admin', 'john.doe') or user ID (e.g., '2-3') (will prompt if not provided for interactive use)
   * - ``--description, -d``
     - string
     - Project description
   * - ``--template, -t``
     - choice
     - Project template: scrum, kanban

**Examples:**

.. code-block:: bash

   # Create a basic project (using username)
   yt projects create "My New Project" "MNP" --leader john.doe

   # Create a project using user ID
   yt projects create "My New Project" "MNP" --leader 2-3

   # Create a project with description and template
   yt projects create "Scrum Project" "SP" --leader jane.smith \
     --description "A new scrum project" --template scrum

   # Create a Kanban project
   yt projects create "Development Board" "DEV" --leader admin \
     --template kanban --description "Main development tracking"

   # Non-interactive creation for automation
   yt projects create "CI Project" "CI" --leader admin \
     --description "Automated project creation"

.. note::
   For automation scripts and CI/CD pipelines, always provide the ``--leader``
   option to avoid interactive prompts.

configure
~~~~~~~~~

Configure project settings or view detailed project information.

.. code-block:: bash

   yt projects configure PROJECT_ID [OPTIONS]

**Arguments:**

* ``PROJECT_ID`` - The project ID or short name (required)

**Options:**

.. list-table::
   :widths: 20 20 60
   :header-rows: 1

   * - Option
     - Type
     - Description
   * - ``--name, -n``
     - string
     - New project name
   * - ``--description, -d``
     - string
     - New project description
   * - ``--leader, -l``
     - string
     - New project leader username (e.g., 'admin', 'john.doe') or user ID (e.g., '2-3')
   * - ``--show-details``
     - flag
     - Show detailed project information

**Examples:**

.. code-block:: bash

   # View detailed project information
   yt projects configure PROJECT_KEY --show-details

   # Update project settings
   yt projects configure PROJECT_KEY --name "Updated Name"
   yt projects configure PROJECT_KEY --description "New description"
   yt projects configure PROJECT_KEY --leader new.leader

   # Update multiple settings at once
   yt projects configure PROJECT_KEY \
     --name "Updated Project Name" \
     --description "Updated description" \
     --leader new.leader

archive
~~~~~~~

Archive a project to mark it as inactive.

.. code-block:: bash

   yt projects archive PROJECT_ID [OPTIONS]

**Arguments:**

* ``PROJECT_ID`` - The project ID or short name to archive (required)

**Options:**

.. list-table::
   :widths: 20 20 60
   :header-rows: 1

   * - Option
     - Type
     - Description
   * - ``--confirm``
     - flag
     - Skip confirmation prompt

**Examples:**

.. code-block:: bash

   # Archive a project (with confirmation prompt)
   yt projects archive PROJECT_KEY

   # Archive a project without confirmation prompt
   yt projects archive PROJECT_KEY --confirm

Project Features
----------------

**Project Templates**
  YouTrack supports different project templates that configure workflows, fields, and boards:

  * **scrum** - Configured for Scrum methodology with sprints and story points
  * **kanban** - Configured for Kanban workflow with continuous flow

**Project Leadership**
  Each project has a designated leader who has administrative rights over the project.

**Project Archiving**
  Projects can be archived when completed or no longer active, hiding them from default views while preserving data.

**Project Metadata**
  Projects include rich metadata including descriptions, custom fields, and configuration settings.

**Short Names/Keys**
  Projects have both full names and short identifiers used in issue IDs (e.g., PROJECT-123).

Custom Fields Management
------------------------

The ``yt projects fields`` command group provides comprehensive management of custom fields within projects. Custom fields extend the default issue properties and allow you to track additional information specific to your project needs.

fields list
~~~~~~~~~~~

List all custom fields configured for a specific project.

.. code-block:: bash

   yt projects fields list PROJECT_ID [OPTIONS]

**Arguments:**

* ``PROJECT_ID`` - The project ID or short name (required)

**Options:**

.. list-table::
   :widths: 20 20 60
   :header-rows: 1

   * - Option
     - Type
     - Description
   * - ``--fields, -f``
     - text
     - Comma-separated list of custom field attributes to return
   * - ``--top, -t``
     - integer
     - Maximum number of custom fields to return
   * - ``--format``
     - choice
     - Output format: table (default) or json

**Examples:**

.. code-block:: bash

   # List all custom fields for a project
   yt projects fields list FPU


   # List with specific fields and JSON format
   yt projects fields list FPU --fields "id,field(name,fieldType),canBeEmpty" --format json

   # Limit results
   yt projects fields list FPU --top 5

fields attach
~~~~~~~~~~~~~

Attach an existing global custom field to a project.

.. code-block:: bash

   yt projects fields attach PROJECT_ID FIELD_ID [OPTIONS]

**Arguments:**

* ``PROJECT_ID`` - The project ID or short name (required)
* ``FIELD_ID`` - The global custom field ID to attach (required)

**Options:**

.. list-table::
   :widths: 20 20 60
   :header-rows: 1

   * - Option
     - Type
     - Description
   * - ``--type``
     - choice
     - Type of project custom field (required)
   * - ``--required``
     - flag
     - Make the field required (cannot be empty)
   * - ``--empty-text``
     - text
     - Text to display when field is empty
   * - ``--private``
     - flag
     - Make the field private (not visible to all users)

**Field Types:**

* ``EnumProjectCustomField`` - Single-select dropdown
* ``MultiEnumProjectCustomField`` - Multi-select dropdown
* ``SingleUserProjectCustomField`` - Single user selection
* ``MultiUserProjectCustomField`` - Multiple user selection
* ``SimpleProjectCustomField`` - Text/numeric fields
* ``VersionProjectCustomField`` - Version fields
* ``MultiVersionProjectCustomField`` - Multiple version fields
* ``DateProjectCustomField`` - Date fields
* ``IntegerProjectCustomField`` - Integer fields
* ``FloatProjectCustomField`` - Float fields
* ``BooleanProjectCustomField`` - Boolean fields

**Examples:**

.. code-block:: bash

   # Attach a priority field as required
   yt projects fields attach FPU field-priority-123 \
     --type EnumProjectCustomField \
     --required \
     --empty-text "No priority set"

   # Attach a private assignee field
   yt projects fields attach FPU field-assignee-456 \
     --type SingleUserProjectCustomField \
     --private

fields update
~~~~~~~~~~~~~

Update settings of a custom field already attached to a project.

.. code-block:: bash

   yt projects fields update PROJECT_ID FIELD_ID [OPTIONS]

**Arguments:**

* ``PROJECT_ID`` - The project ID or short name (required)
* ``FIELD_ID`` - The project custom field ID to update (required)

**Options:**

.. list-table::
   :widths: 20 20 60
   :header-rows: 1

   * - Option
     - Type
     - Description
   * - ``--required/--optional``
     - boolean
     - Make the field required or optional
   * - ``--empty-text``
     - text
     - Text to display when field is empty
   * - ``--public/--private``
     - boolean
     - Make the field public or private

**Examples:**

.. code-block:: bash

   # Make a field required
   yt projects fields update FPU project-field-123 --required

   # Update empty text and make private
   yt projects fields update FPU project-field-123 \
     --empty-text "Please specify" \
     --private

   # Make field optional
   yt projects fields update FPU project-field-123 --optional

fields detach
~~~~~~~~~~~~~

Remove a custom field from a project.

.. code-block:: bash

   yt projects fields detach PROJECT_ID FIELD_ID [OPTIONS]

**Arguments:**

* ``PROJECT_ID`` - The project ID or short name (required)
* ``FIELD_ID`` - The project custom field ID to remove (required)

**Options:**

.. list-table::
   :widths: 20 20 60
   :header-rows: 1

   * - Option
     - Type
     - Description
   * - ``--force``
     - flag
     - Skip confirmation prompt

**Examples:**

.. code-block:: bash

   # Remove a custom field (with confirmation)
   yt projects fields detach FPU project-field-123

   # Remove without confirmation
   yt projects fields detach FPU project-field-123 --force

Custom Fields Workflows
~~~~~~~~~~~~~~~~~~~~~~~

**Project Setup with Custom Fields:**

.. code-block:: bash

   # 1. List current custom fields
   yt projects fields list FPU

   # 2. Attach required fields for project workflow
   yt projects fields attach FPU priority-field-id \
     --type EnumProjectCustomField \
     --required \
     --empty-text "Priority not set"

   yt projects fields attach FPU assignee-field-id \
     --type SingleUserProjectCustomField \
     --empty-text "Unassigned"

   # 3. Verify configuration
   yt projects fields list FPU

**Custom Fields Maintenance:**

.. code-block:: bash

   # Update field visibility
   yt projects fields update FPU project-field-123 --private

   # Change requirement status
   yt projects fields update FPU project-field-456 --optional

   # Update empty text for better UX
   yt projects fields update FPU project-field-789 \
     --empty-text "Please select a priority level"

**Custom Fields Discovery:**

.. code-block:: bash

   # Export custom fields configuration
   yt projects fields list FPU --format json > project_fields.json

   # List only specific field attributes
   yt projects fields list FPU \
     --fields "field(name,fieldType),canBeEmpty,isPublic"

Common Workflows
----------------

Project Setup
~~~~~~~~~~~~~

.. code-block:: bash

   # Create a new development project
   yt projects create "Web Application Development" "WEB" \
     --leader john.doe \
     --description "Main web application development project" \
     --template scrum

   # Verify project creation
   yt projects configure WEB --show-details

   # List all projects to confirm
   yt projects list

Project Maintenance
~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Update project information
   yt projects configure PROJECT_KEY --name "Updated Project Name"

   # Change project leader
   yt projects configure PROJECT_KEY --leader new.leader

   # View current project settings
   yt projects configure PROJECT_KEY --show-details

Project Lifecycle Management
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # List active projects
   yt projects list

   # Archive completed projects
   yt projects archive OLD_PROJECT --confirm

   # View all projects including archived
   yt projects list --show-archived

   # Export project list for reporting
   yt projects list --format json > projects_report.json

Project Discovery and Reporting
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # List all projects with leadership information
   yt projects list --fields "id,name,shortName,leader(fullName),created"

   # Find projects by specific criteria
   yt projects list --show-archived | grep "archived"

   # Generate project summary report
   yt projects list --format json --fields "name,shortName,leader,created,archived"

Best Practices
--------------

1. **Meaningful Names**: Use clear, descriptive project names that reflect the project's purpose.

2. **Consistent Naming**: Establish naming conventions for both full names and short names/keys.

3. **Short Name Strategy**: Use short, memorable keys (2-5 characters) for issue prefixes.

4. **Template Selection**: Choose appropriate templates (Scrum vs Kanban) based on your team's workflow.

5. **Project Leadership**: Assign appropriate project leaders with necessary permissions.

6. **Regular Maintenance**: Periodically review and update project settings as needs evolve.

7. **Archive Management**: Archive completed projects to keep active project lists clean.

8. **Documentation**: Use project descriptions to document project purpose and scope.

9. **Lifecycle Planning**: Plan for project phases including creation, active development, and archival.

Project Templates
----------------

Scrum Template
~~~~~~~~~~~~~

The Scrum template configures projects for Scrum methodology:

* Sprint-based workflow
* Story points estimation
* Backlog management
* Sprint planning capabilities
* Burndown charts
* Velocity tracking

.. code-block:: bash

   yt projects create "Scrum Project" "SCRUM" \
     --leader scrum.master \
     --template scrum \
     --description "Agile development using Scrum methodology"

Kanban Template
~~~~~~~~~~~~~~

The Kanban template configures projects for Kanban workflow:

* Continuous flow workflow
* Board-based visualization
* Work-in-progress limits
* Cycle time tracking
* Cumulative flow diagrams

.. code-block:: bash

   yt projects create "Kanban Board" "KANBAN" \
     --leader team.lead \
     --template kanban \
     --description "Continuous flow development using Kanban"

Output Formats
--------------

Table Format (Default)
~~~~~~~~~~~~~~~~~~~~~~

The default table format provides a clean, readable view of project information:

.. code-block:: text

   ┌────────────┬──────────────────────┬─────────────┬─────────────────┬──────────┐
   │ Short Name │ Name                 │ Leader      │ Created         │ Archived │
   ├────────────┼──────────────────────┼─────────────┼─────────────────┼──────────┤
   │ WEB        │ Web Development      │ John Doe    │ 2024-01-15      │ No       │
   │ API        │ API Development      │ Jane Smith  │ 2024-01-20      │ No       │
   │ OLD        │ Legacy Project       │ Bob Wilson  │ 2023-12-01      │ Yes      │
   └────────────┴──────────────────────┴─────────────┴─────────────────┴──────────┘

JSON Format
~~~~~~~~~~~

JSON format provides structured data suitable for automation and integration:

.. code-block:: json

   [
     {
       "id": "0-0",
       "name": "Web Development",
       "shortName": "WEB",
       "description": "Main web application project",
       "leader": {
         "id": "1-1",
         "login": "john.doe",
         "fullName": "John Doe"
       },
       "created": "2024-01-15T10:00:00.000Z",
       "archived": false
     }
   ]

Error Handling
--------------

Common error scenarios and solutions:

**Permission Denied**
  Ensure you have administrative privileges to create, modify, or archive projects.

**Project Already Exists**
  Check if a project with the same short name already exists. Short names must be unique.

**Invalid Leader**
  Verify the specified leader username (e.g., 'admin', 'john.doe') or user ID (e.g., '2-3') exists and is a valid user. Use ``yt users list`` to see available users.

**Project Not Found**
  Confirm the project ID or short name is correct and you have access to the project.

**Invalid Template**
  Ensure the specified template (scrum, kanban) is supported and available.

**Archive Restrictions**
  Some projects may have restrictions preventing archival. Check project dependencies.

Integration Examples
-------------------

Scripting and Automation
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   #!/bin/bash
   # Project setup script

   PROJECT_NAME="New Development Project"
   PROJECT_KEY="NDP"
   LEADER="project.manager"

   # Create project
   yt projects create "$PROJECT_NAME" "$PROJECT_KEY" \
     --leader "$LEADER" \
     --template scrum \
     --description "Automated project creation"

   # Verify creation
   yt projects configure "$PROJECT_KEY" --show-details

Project Reporting
~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Generate project inventory report
   yt projects list --format json \
     --fields "name,shortName,leader(fullName),created,archived" \
     > project_inventory.json

   # List only archived projects
   yt projects list --show-archived --format json | \
     jq '.[] | select(.archived == true)'

Bulk Operations
~~~~~~~~~~~~~~

.. code-block:: bash

   # Archive multiple old projects
   for project in OLD1 OLD2 OLD3; do
     yt projects archive "$project" --confirm
   done

   # Update descriptions for multiple projects
   while read -r project desc; do
     yt projects configure "$project" --description "$desc"
   done < project_updates.txt

See Also
--------

* :doc:`issues` - Issue management within projects
* :doc:`articles` - Project documentation and knowledge base
* :doc:`users` - User management and project membership
* :doc:`boards` - Agile board management for projects
* :doc:`auth` - Authentication setup
* :doc:`admin` - Administrative operations for project management
