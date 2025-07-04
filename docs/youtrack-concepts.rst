YouTrack Concepts
=================

This guide explains key YouTrack concepts to help new users understand how to effectively use the YouTrack CLI.

Understanding YouTrack
-----------------------

YouTrack is a comprehensive issue tracking and project management platform developed by JetBrains. It provides powerful tools for tracking bugs, managing features, planning sprints, and coordinating team work.

Core Concepts
-------------

Issues
~~~~~~

**Issues** are the fundamental work items in YouTrack. They represent:

* **Bugs** - Software defects that need to be fixed
* **Features** - New functionality to be implemented
* **Tasks** - General work items or to-do items
* **Epics** - Large features broken down into smaller issues

Each issue has:

* **ID** - Unique identifier (e.g., ``WEB-123``, ``API-456``)
* **Summary** - Brief description of the issue
* **Description** - Detailed explanation of the issue
* **State** - Current status of the issue
* **Priority** - Importance level
* **Assignee** - Person responsible for the issue

Projects
~~~~~~~~

**Projects** are containers that organize related issues. Examples:

* ``WEB-FRONTEND`` - Issues related to the web application UI
* ``API-BACKEND`` - Issues for backend API development
* ``MOBILE-APP`` - Mobile application issues
* ``INFRA`` - Infrastructure and DevOps issues

Project IDs are used as prefixes for issue IDs (e.g., issues in ``WEB-FRONTEND`` have IDs like ``WEB-123``).

States and Workflow
~~~~~~~~~~~~~~~~~~~

**States** represent the current status of an issue in its lifecycle:

**Common States:**
* ``Open`` - Issue has been created but work hasn't started
* ``In Progress`` - Someone is actively working on the issue
* ``In Review`` - Work is complete and under review
* ``Resolved`` - Issue has been fixed/completed
* ``Closed`` - Issue is finalized and verified
* ``Rejected`` - Issue was deemed invalid or won't be fixed

**Workflow** defines how issues move between states. For example:
``Open`` → ``In Progress`` → ``In Review`` → ``Resolved`` → ``Closed``

Priority Levels
~~~~~~~~~~~~~~~

**Priority** indicates how urgent or important an issue is:

* ``Critical`` - System is broken, immediate attention required
* ``High`` - Important issue that should be addressed soon
* ``Medium`` - Normal priority issue
* ``Low`` - Nice-to-have or minor issue

Users and Assignments
~~~~~~~~~~~~~~~~~~~~~

**Users** are people who work with issues:

* **Assignee** - Person responsible for working on the issue
* **Reporter** - Person who created the issue
* **Watchers** - People following the issue for updates

**Assignment** means giving responsibility for an issue to a specific person.

Tags and Labels
~~~~~~~~~~~~~~~

**Tags** are labels you can attach to issues for organization:

* ``urgent`` - Needs immediate attention
* ``bug`` - Software defect
* ``enhancement`` - Improvement to existing feature
* ``documentation`` - Related to docs
* ``frontend``, ``backend`` - Component-specific tags

Comments and Communication
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Comments** allow team members to:

* Ask questions about the issue
* Provide updates on progress
* Share solutions or workarounds
* Discuss implementation approaches

Attachments and Files
~~~~~~~~~~~~~~~~~~~~~

**Attachments** let you add files to issues:

* Screenshots of bugs
* Log files for debugging
* Design mockups for features
* Documentation or specifications

Issue Relationships
~~~~~~~~~~~~~~~~~~~

**Links** connect related issues:

* ``depends on`` - This issue cannot be completed until another is done
* ``duplicates`` - This issue is the same as another issue
* ``relates to`` - This issue is related to another issue
* ``blocks`` - This issue prevents another from being completed

Time Tracking
~~~~~~~~~~~~~

**Time tracking** helps monitor work effort:

* **Work time** - How long was spent working on the issue
* **Estimates** - How long the work is expected to take
* **Time reports** - Summary of time spent across issues/projects

CLI Mapping
-----------

Here's how YouTrack concepts map to CLI commands:

**Issues Management:**

.. code-block:: bash

   # Create an issue
   yt issues create PROJECT-ID "Issue summary" --type Bug --priority High

   # List issues in a project
   yt issues list --project PROJECT-ID

   # Update issue state
   yt issues update ISSUE-ID --state "In Progress"

   # Assign issue to someone
   yt issues assign ISSUE-ID username

**Project Operations:**

.. code-block:: bash

   # List all projects
   yt projects list

   # Create a new project
   yt projects create --name "My Project" --key "MP"

**Comments and Communication:**

.. code-block:: bash

   # Add a comment
   yt issues comments add ISSUE-ID "Comment text"

   # List comments
   yt issues comments list ISSUE-ID

**Time Tracking:**

.. code-block:: bash

   # Log work time
   yt time log ISSUE-ID "2h 30m" --description "Fixed the bug"

   # Generate time report
   yt time report --from "2024-01-01" --to "2024-01-31"

Getting Started Tips
--------------------

For New YouTrack Users
~~~~~~~~~~~~~~~~~~~~~~

1. **Start with browsing** - Use ``yt projects list`` to see available projects
2. **Explore issues** - Try ``yt issues list --project PROJECT-ID`` to see existing issues
3. **Understand the workflow** - Ask your team about the typical issue states
4. **Practice with test issues** - Create a few test issues to get comfortable

For CLI Beginners
~~~~~~~~~~~~~~~~~

1. **Use help** - Every command has help: ``yt issues --help``
2. **Start simple** - Begin with list and search commands before creating
3. **Check twice** - Use ``--dry-run`` options when available
4. **Learn incrementally** - Master basic commands before advanced features

Common Workflows
~~~~~~~~~~~~~~~~

**Daily Developer Workflow:**

1. Check assigned issues: ``yt issues list --assignee me --state open``
2. Start work: ``yt issues update ISSUE-ID --state "In Progress"``
3. Add progress comments: ``yt issues comments add ISSUE-ID "Working on the fix"``
4. Log time: ``yt time log ISSUE-ID "4h" --description "Implemented solution"``
5. Mark complete: ``yt issues update ISSUE-ID --state "Resolved"``

**Bug Triage Workflow:**

1. Search for similar issues: ``yt issues search "error message"``.
2. Create bug report: ``yt issues create PROJECT "Bug summary" --type Bug``
3. Add details: ``yt issues comments add ISSUE-ID "Steps to reproduce..."``.
4. Set priority: ``yt issues update ISSUE-ID --priority High``
5. Assign to developer: ``yt issues assign ISSUE-ID developer-username``

Next Steps
----------

Now that you understand YouTrack concepts, you can:

* Follow the :doc:`quickstart` guide to start using the CLI
* Explore the :doc:`commands/index` for detailed command reference
* Check :doc:`configuration` for setting up your environment
