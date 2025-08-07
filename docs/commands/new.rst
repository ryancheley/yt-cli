New Command
===========

The ``yt new`` command provides a quick shortcut for creating YouTrack issues. This is a global shortcut for the most common create operation, equivalent to ``yt issues create`` but with a more convenient interface that reduces typing and speeds up issue creation workflows.

.. contents:: Table of Contents
   :local:
   :depth: 2

Overview
--------

The new command allows you to:

* Quickly create YouTrack issues with essential information
* Use a streamlined interface for rapid issue creation
* Set common issue properties like type, priority, and assignee
* Add tags and descriptions during issue creation
* Create issues with minimal typing for improved productivity

The ``yt new`` command provides the same functionality as ``yt issues create`` but with a more concise syntax optimized for frequent use.

Base Command
------------

.. code-block:: bash

   yt new PROJECT TITLE [OPTIONS]

Command Arguments and Options
-----------------------------

**Arguments:**
  * ``PROJECT`` - The project ID or key where the issue should be created
  * ``TITLE`` - The issue title or summary

**Options:**
  * ``-d, --description TEXT`` - Issue description
  * ``-t, --type TEXT`` - Issue type (Bug, Feature, Task, etc.)
  * ``-p, --priority TEXT`` - Issue priority
  * ``-a, --assignee TEXT`` - Assign to user
  * ``--tag TEXT`` - Add tags (comma-separated)

**Examples:**

.. code-block:: bash

   # Create a simple issue
   yt new DEMO "Fix login bug"

   # Create a bug with description and assignee
   yt new DEMO "Login fails" --type Bug --assignee john.doe

   # Create a feature with tags
   yt new API "Add user search" --type Feature --tag "enhancement,api"

   # Create a task with description and priority
   yt new WEB "Update documentation" --type Task --priority High --description "Update API documentation for v2.0"

Quick Issue Creation Patterns
-----------------------------

Bug Reporting
~~~~~~~~~~~~~

Rapidly create bug reports with essential information:

.. code-block:: bash

   # Basic bug report
   yt new DEMO "Login button not working" --type Bug

   # Bug with assignee and priority
   yt new WEB "Page crashes on mobile" --type Bug --assignee mobile-dev --priority High

   # Critical bug with description
   yt new API "Data corruption in user profiles" \
       --type Bug \
       --priority Critical \
       --description "User profile data is being corrupted when updated via API endpoint"

Feature Requests
~~~~~~~~~~~~~~~

Create feature requests and enhancement issues:

.. code-block:: bash

   # Simple feature request
   yt new PRODUCT "Add dark mode" --type Feature

   # Feature with detailed description
   yt new MOBILE "Push notifications" \
       --type Feature \
       --description "Implement push notifications for important app events" \
       --assignee feature-team

   # Enhancement with tags
   yt new WEB "Improve search performance" --type Enhancement --tag "performance,search"

Task Management
~~~~~~~~~~~~~~

Create task and maintenance issues:

.. code-block:: bash

   # Documentation task
   yt new PROJECT "Update README" --type Task --assignee tech-writer

   # Maintenance task with priority
   yt new INFRA "Database maintenance" --type Task --priority High

   # Development task with multiple tags
   yt new API "Refactor authentication module" --type Task --tag "refactor,security,tech-debt"

Sprint and Project Planning
~~~~~~~~~~~~~~~~~~~~~~~~~~

Create issues for sprint and project planning activities:

.. code-block:: bash

   # Sprint planning items
   yt new SCRUM "Sprint retrospective" --type Task --assignee scrum-master
   yt new SCRUM "Plan next sprint" --type Task --priority Medium

   # Project milestones
   yt new PROJECT "Release v2.0" --type Epic --description "Major release with new features"
   yt new PROJECT "Security audit" --type Task --priority High --tag "security,compliance"

Integration with Issues Command
-------------------------------

The ``yt new`` command is functionally identical to ``yt issues create``. Both commands provide the same issue creation capabilities:

.. code-block:: bash

   # These commands are equivalent:
   yt new DEMO "Fix bug" --type Bug --assignee john.doe
   yt issues create DEMO "Fix bug" --type Bug --assignee john.doe

   # These commands are equivalent:
   yt new API "Add feature" --priority High --tag "enhancement"
   yt issues create API "Add feature" --priority High --tag "enhancement"

Choose the command style that fits your workflow:

* Use ``yt new`` for quick, frequent issue creation operations
* Use ``yt issues create`` when working with other issue management commands
* Use ``yt new`` when you want minimal typing and maximum speed

Advanced Issue Creation
-----------------------

Complex Issue Setup
~~~~~~~~~~~~~~~~~~~

Create issues with comprehensive information:

.. code-block:: bash

   # Comprehensive bug report
   yt new WEBAPP "User session expires unexpectedly" \
       --type Bug \
       --priority High \
       --assignee backend-team \
       --description "Users are being logged out after 5 minutes instead of the configured 30 minutes. This affects user experience and productivity." \
       --tag "session,authentication,urgent"

   # Feature with detailed planning
   yt new MOBILE "Implement biometric authentication" \
       --type Feature \
       --priority Medium \
       --assignee security-team \
       --description "Add fingerprint and face recognition authentication options for improved security and user convenience" \
       --tag "security,biometric,enhancement"

Batch Issue Creation
~~~~~~~~~~~~~~~~~~~

While not directly supported, combine with shell scripting for batch creation:

.. code-block:: bash

   # Create multiple related issues
   ISSUES=(
       "Update user interface|Feature|ui-team"
       "Fix data validation|Bug|backend-team"
       "Write test cases|Task|qa-team"
   )

   for issue in "${ISSUES[@]}"; do
       IFS='|' read -r title type assignee <<< "$issue"
       yt new PROJECT "$title" --type "$type" --assignee "$assignee"
   done

Template-Based Creation
~~~~~~~~~~~~~~~~~~~~~~

Create standardized issues using templates:

.. code-block:: bash

   # Bug report template
   create_bug() {
       local project="$1"
       local title="$2"
       local description="$3"

       yt new "$project" "$title" \
           --type Bug \
           --priority High \
           --description "$description" \
           --tag "needs-investigation"
   }

   # Feature request template
   create_feature() {
       local project="$1"
       local title="$2"
       local assignee="$3"

       yt new "$project" "$title" \
           --type Feature \
           --assignee "$assignee" \
           --tag "enhancement,planning-needed"
   }

Workflow Integration
--------------------

Development Workflow
~~~~~~~~~~~~~~~~~~~

Integrate issue creation into development processes:

.. code-block:: bash

   # Create bug from failed test
   yt new TEST-PROJECT "Test failure in user authentication" \
       --type Bug \
       --description "Unit test AuthServiceTest.testLoginValidation is failing consistently" \
       --assignee current-developer \
       --tag "test-failure,urgent"

   # Create feature branch issue
   yt new FEATURE-PROJ "Implement new dashboard widget" \
       --type Feature \
       --assignee developer-name \
       --description "Create configurable dashboard widget for user metrics" \
       --tag "dashboard,widget,ui"

Customer Support Integration
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create issues from customer feedback and support requests:

.. code-block:: bash

   # Customer-reported bug
   yt new SUPPORT "Customer reports slow search performance" \
       --type Bug \
       --priority High \
       --description "Customer #12345 reports search taking over 10 seconds to return results" \
       --tag "customer-issue,performance"

   # Feature request from customer
   yt new PRODUCT "Customer requests export functionality" \
       --type Feature \
       --priority Medium \
       --description "Multiple customers have requested ability to export reports to PDF format" \
       --tag "customer-request,export"

CI/CD and Automation
~~~~~~~~~~~~~~~~~~~

Integrate issue creation into automated workflows:

.. code-block:: bash

   # Create issue from build failure
   if [ $BUILD_STATUS == "failed" ]; then
       yt new CI-PROJECT "Build failure in $BRANCH_NAME" \
           --type Bug \
           --priority High \
           --assignee "$COMMIT_AUTHOR" \
           --description "Build failed on commit $COMMIT_SHA in branch $BRANCH_NAME" \
           --tag "build-failure,ci"
   fi

   # Create security issue from vulnerability scan
   yt new SECURITY "Vulnerability detected in dependencies" \
       --type Bug \
       --priority Critical \
       --assignee security-team \
       --description "Security scan detected high-severity vulnerability in library X" \
       --tag "security,vulnerability,dependencies"

Best Practices
--------------

Issue Quality
~~~~~~~~~~~~~

Create high-quality issues that provide value to the team:

**Clear Titles:**
  * Use descriptive, specific titles that clearly identify the issue
  * Include key context like component, feature, or error type
  * Avoid vague titles like "fix bug" or "add feature"

**Comprehensive Descriptions:**
  * Include steps to reproduce for bugs
  * Provide acceptance criteria for features
  * Add relevant context and background information

**Appropriate Metadata:**
  * Set realistic priority levels based on actual impact
  * Assign to appropriate team members or leave unassigned for triage
  * Use consistent and meaningful tags for categorization

Efficient Workflows
~~~~~~~~~~~~~~~~~~~

Optimize issue creation for productivity:

**Command Shortcuts:**
  * Create shell aliases for frequently used patterns
  * Use command history and tab completion for faster typing
  * Save common issue templates as shell functions

**Consistent Tagging:**
  * Establish team conventions for tag usage
  * Use tags to support filtering and reporting needs
  * Include tags that help with automated processing and routing

**Project Organization:**
  * Understand project structures and naming conventions
  * Use appropriate project IDs for different types of work
  * Consider issue categorization and workflow requirements

Automation and Integration
--------------------------

Shell Integration
~~~~~~~~~~~~~~~~

Create shell functions for common issue creation patterns:

.. code-block:: bash

   # Add to ~/.bashrc or ~/.zshrc

   # Quick bug creation
   bug() {
       local project="$1"
       local title="$2"
       shift 2
       yt new "$project" "$title" --type Bug --priority High "$@"
   }

   # Quick feature creation
   feature() {
       local project="$1"
       local title="$2"
       shift 2
       yt new "$project" "$title" --type Feature --priority Medium "$@"
   }

   # Quick task creation
   task() {
       local project="$1"
       local title="$2"
       shift 2
       yt new "$project" "$title" --type Task "$@"
   }

Git Integration
~~~~~~~~~~~~~~

Integrate issue creation with git workflows:

.. code-block:: bash

   # Create issue and branch together
   create_feature_issue() {
       local project="$1"
       local title="$2"
       local branch_name=$(echo "$title" | tr '[:upper:]' '[:lower:]' | tr ' ' '-')

       # Create the issue
       ISSUE_ID=$(yt new "$project" "$title" --type Feature --format json | jq -r '.id')

       # Create feature branch
       git checkout -b "feature/$ISSUE_ID-$branch_name"

       echo "Created issue $ISSUE_ID and branch feature/$ISSUE_ID-$branch_name"
   }

IDE and Editor Integration
~~~~~~~~~~~~~~~~~~~~~~~~~

Integrate with development tools:

.. code-block:: bash

   # VS Code integration example
   create_issue_from_selection() {
       local project="$1"
       local selected_text="$2"

       yt new "$project" "Issue with: $selected_text" \
           --type Bug \
           --description "Found issue in code: $selected_text" \
           --tag "code-review,needs-investigation"
   }

Troubleshooting
---------------

Common Issues
~~~~~~~~~~~~~

**Project Not Found:**
  * Verify the project ID or key is correct
  * Check that you have access to create issues in the project
  * Ensure the project exists and is not archived

**Invalid Field Values:**
  * Verify issue types exist in the project configuration
  * Check that priority values match YouTrack settings
  * Ensure assignee usernames are correct and active

**Permission Denied:**
  * Confirm you have issue creation permissions in the project
  * Verify your authentication token is valid and has appropriate scope
  * Check project-specific permission settings

Validation Errors
~~~~~~~~~~~~~~~~~

**Required Fields Missing:**
  * Some projects may require additional fields beyond title
  * Check project configuration for mandatory custom fields
  * Provide all required information for successful issue creation

**Invalid Characters or Format:**
  * Avoid special characters that might cause parsing issues
  * Use appropriate encoding for international characters
  * Verify tag format meets system requirements

Authentication
--------------

Issue creation requires authentication and appropriate permissions. Make sure you're logged in:

.. code-block:: bash

   yt auth login

See Also
--------

* :doc:`issues` - Complete issue management functionality including advanced creation options
* :doc:`ls` - Quick issue listing shortcut
* :doc:`projects` - Project management and configuration
* :doc:`users` - User management for assignee configuration
