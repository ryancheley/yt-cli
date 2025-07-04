Workflow Examples
=================

This guide provides complete real-world scenarios showing how to use YouTrack CLI in different development workflows.

.. contents:: Table of Contents
   :local:
   :depth: 2

Daily Developer Workflows
-------------------------

Morning Standup Workflow
~~~~~~~~~~~~~~~~~~~~~~~~~

**Scenario**: Check your work status for daily standup meeting.

.. code-block:: bash

   # 1. Check issues assigned to you that are in progress
   yt issues list --assignee me --state "In Progress"

   # 2. Check recently completed issues (last 7 days)
   yt issues search "assignee:me resolved:today .. -7d"

   # 3. View time spent yesterday
   yt time report --from yesterday --to today --assignee me

   # 4. Check upcoming deadlines
   yt issues search "assignee:me has:due-date due:today .. +7d"

**Expected Output**:

.. code-block:: text

   📋 Issues In Progress (2):
   ┌─────────────┬──────────────────────────────────┬──────────┬─────────────┐
   │ ID          │ Summary                          │ Priority │ Due Date    │
   ├─────────────┼──────────────────────────────────┼──────────┼─────────────┤
   │ WEB-456     │ Fix login button on mobile       │ High     │ 2024-01-15  │
   │ API-789     │ Add user profile endpoint        │ Medium   │ 2024-01-17  │
   └─────────────┴──────────────────────────────────┴──────────┴─────────────┘

Bug Fix Workflow
~~~~~~~~~~~~~~~~

**Scenario**: Complete workflow for fixing a bug from discovery to resolution.

.. code-block:: bash

   # 1. Create bug report
   yt issues create WEB-FRONTEND "Cart total calculation incorrect" \
     --description "Shopping cart shows wrong total when discount codes are applied. Tax calculation appears to be doubled." \
     --type "Bug" \
     --priority "High" \
     --tags "urgent,checkout"

   # 2. Start working on the bug
   yt issues update WEB-567 --state "In Progress" --assignee me

   # 3. Add investigation notes
   yt issues comments add WEB-567 "Investigating: Found issue in discount.js line 45. Tax is being calculated twice when discount > 20%."

   # 4. Log time spent investigating
   yt time log WEB-567 "1h 30m" --description "Root cause analysis and debugging"

   # 5. Add code fix details
   yt issues comments add WEB-567 "Fixed: Modified calculateTotal() function to apply tax calculation only once. Updated unit tests."

   # 6. Log development time
   yt time log WEB-567 "2h 45m" --description "Implementation and testing"

   # 7. Mark as resolved and ready for QA
   yt issues update WEB-567 --state "Fixed" --assignee "qa-lead"

   # 8. Generate time report for the bug
   yt time report --issue WEB-567

Feature Development Workflow
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Scenario**: Develop a new feature from planning to deployment.

.. code-block:: bash

   # 1. Create epic for the feature
   yt issues create API-BACKEND "User Profile Management API" \
     --description "Complete user profile CRUD operations with avatar upload, privacy settings, and audit trail." \
     --type "Epic" \
     --priority "Medium"

   # 2. Break down into tasks
   yt issues create API-BACKEND "Create user profile data model" \
     --description "Design and implement User Profile schema with validation" \
     --type "Task" \
     --priority "High" \
     --assignee "backend-dev"

   yt issues create API-BACKEND "Implement profile CRUD endpoints" \
     --description "REST API endpoints for create, read, update, delete user profiles" \
     --type "Task" \
     --priority "High" \
     --assignee "backend-dev"

   yt issues create API-BACKEND "Add avatar upload functionality" \
     --description "File upload endpoint with image validation and thumbnail generation" \
     --type "Task" \
     --priority "Medium" \
     --assignee "backend-dev"

   # 3. Link tasks to epic
   yt issues links create API-890 "subtask of" API-888
   yt issues links create API-891 "subtask of" API-888
   yt issues links create API-892 "subtask of" API-888

   # 4. Start development workflow for first task
   yt issues update API-890 --state "In Progress"

   # 5. Track progress with regular updates
   yt issues comments add API-890 "Created User model with fields: email, firstName, lastName, bio, avatar_url, privacy_settings"
   yt time log API-890 "3h" --description "Data model design and implementation"

   # 6. Move through development stages
   yt issues update API-890 --state "In Review"
   yt issues assign API-890 "senior-dev"  # Code review

   # 7. After review approval
   yt issues update API-890 --state "Testing"
   yt issues assign API-890 "qa-team"

   # 8. Final deployment
   yt issues update API-890 --state "Done"

Team Collaboration Workflows
-----------------------------

Code Review Workflow
~~~~~~~~~~~~~~~~~~~~~

**Scenario**: Manage code review process through YouTrack.

.. code-block:: bash

   # Developer perspective:
   # 1. Mark issue ready for review
   yt issues update WEB-234 --state "In Review" \
     --assignee "senior-dev" \
     --tags "ready-for-review"

   # 2. Add review request comment
   yt issues comments add WEB-234 "Ready for review. PR: https://github.com/company/app/pull/456. Focus on error handling in payment.js"

   # Reviewer perspective:
   # 3. Add review feedback
   yt issues comments add WEB-234 "Code Review: Generally good approach. Please address: 1) Add input validation, 2) Handle edge case when amount = 0, 3) Update error messages for clarity."

   # 4. Request changes
   yt issues update WEB-234 --state "In Progress" \
     --assignee "original-developer" \
     --tags "changes-requested"

   # Developer fixes and resubmits:
   # 5. Address feedback
   yt issues comments add WEB-234 "Addressed all review comments: Added validation, fixed edge case, updated error messages. Ready for re-review."
   yt issues update WEB-234 --state "In Review" --assignee "senior-dev"

   # 6. Final approval
   yt issues comments add WEB-234 "LGTM - Approved for merge"
   yt issues update WEB-234 --state "Resolved"

Sprint Planning Workflow
~~~~~~~~~~~~~~~~~~~~~~~~~

**Scenario**: Plan and track a 2-week sprint.

.. code-block:: bash

   # Sprint setup:
   # 1. List backlog issues for planning
   yt issues search "project:WEB-FRONTEND state:Open priority:{High,Medium}" \
     --sort "priority,created" --limit 20

   # 2. Assign issues to sprint (using tags)
   yt issues update WEB-123 --tags "sprint-15,frontend"
   yt issues update WEB-124 --tags "sprint-15,frontend"
   yt issues update API-456 --tags "sprint-15,backend"

   # 3. Assign team members
   yt issues assign WEB-123 "frontend-dev-1"
   yt issues assign WEB-124 "frontend-dev-2"
   yt issues assign API-456 "backend-dev-1"

   # Daily sprint tracking:
   # 4. Check sprint progress
   yt issues search "tag:sprint-15 state:{\"In Progress\",Open,\"In Review\"}"

   # 5. Generate sprint burndown data
   yt time report --from "2024-01-01" --to "2024-01-14" \
     --project WEB-FRONTEND --format json

   # Sprint retrospective:
   # 6. Review completed vs planned
   yt issues search "tag:sprint-15 state:{Done,Resolved}"
   yt issues search "tag:sprint-15 state:{Open,\"In Progress\"}"

   # 7. Move incomplete items to next sprint
   yt issues update WEB-125 --tags "sprint-16" --tags "-sprint-15"

Bug Triage Workflow
~~~~~~~~~~~~~~~~~~~~

**Scenario**: Weekly bug triage meeting process.

.. code-block:: bash

   # 1. List all new bugs
   yt issues search "type:Bug state:Open created:this-week" \
     --sort "priority,created"

   # 2. Review critical bugs first
   yt issues search "type:Bug priority:Critical state:Open" \
     --sort "created"

   # 3. Assign severity and priority during triage
   yt issues update BUG-789 --priority "High" \
     --assignee "senior-dev" \
     --tags "data-loss,regression"

   # 4. Add triage notes
   yt issues comments add BUG-789 "Triage: Confirmed data loss issue. Affects users on premium plans. Regression from v2.3.1 deployment. High priority for hotfix."

   # 5. Create hotfix epic if needed
   yt issues create INFRA "Hotfix v2.3.2 - Critical Bug Fixes" \
     --type "Epic" \
     --priority "Critical" \
     --assignee "release-manager"

   # 6. Link bugs to hotfix
   yt issues links create BUG-789 "fixed by" INFRA-445

   # 7. Schedule bugs for upcoming sprints
   yt issues update BUG-790 --tags "sprint-15,bug-fix"
   yt issues update BUG-791 --tags "sprint-16,enhancement"

DevOps and Deployment Workflows
-------------------------------

CI/CD Integration Workflow
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Scenario**: Integrate YouTrack CLI with CI/CD pipeline.

**GitHub Actions Example** (`.github/workflows/youtrack-integration.yml`):

.. code-block:: yaml

   name: YouTrack Integration
   on:
     pull_request:
       types: [opened, closed]
     push:
       branches: [main]

   jobs:
     youtrack-update:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v3

         - name: Setup YouTrack CLI
           run: |
             pip install youtrack-cli
             echo "YOUTRACK_BASE_URL=${{ secrets.YOUTRACK_URL }}" >> ~/.config/youtrack-cli/.env
             echo "YOUTRACK_TOKEN=${{ secrets.YOUTRACK_TOKEN }}" >> ~/.config/youtrack-cli/.env

         - name: Extract issue ID from branch
           run: |
             ISSUE_ID=$(echo ${{ github.head_ref }} | grep -oE '[A-Z]+-[0-9]+')
             echo "ISSUE_ID=$ISSUE_ID" >> $GITHUB_ENV

         - name: Update issue on PR open
           if: github.event.action == 'opened'
           run: |
             yt issues update $ISSUE_ID --state "In Review"
             yt issues comments add $ISSUE_ID "Pull Request created: ${{ github.event.pull_request.html_url }}"

         - name: Update issue on merge
           if: github.event.action == 'closed' && github.event.pull_request.merged
           run: |
             yt issues update $ISSUE_ID --state "Testing"
             yt issues comments add $ISSUE_ID "Merged to main. Deployed to staging environment."

Release Management Workflow
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Scenario**: Manage release process with automatic issue updates.

.. code-block:: bash

   # 1. Create release epic
   yt issues create RELEASE "Version 2.4.0 Release" \
     --description "Q1 2024 major release with user profile features and performance improvements" \
     --type "Epic" \
     --priority "High" \
     --assignee "release-manager"

   # 2. Gather issues for release
   yt issues search "state:Resolved project:{WEB-FRONTEND,API-BACKEND} \
     resolved:2024-01-01..2024-01-31" --format json > release-issues.json

   # 3. Link issues to release
   # Script to process release-issues.json and link them
   for issue in $(jq -r '.[].id' release-issues.json); do
     yt issues links create $issue "included in" RELEASE-890
   done

   # 4. Pre-release testing
   yt issues create RELEASE "Pre-release testing checklist" \
     --description "Complete QA testing before v2.4.0 release" \
     --type "Task" \
     --assignee "qa-lead" \
     --tags "release-blocker"

   # 5. During deployment
   yt issues comments add RELEASE-890 "Deployment started: v2.4.0 rolling out to production"

   # 6. Post-deployment
   yt issues update RELEASE-890 --state "Done"
   yt issues comments add RELEASE-890 "✅ v2.4.0 successfully deployed. All systems operational."

   # 7. Generate release notes
   yt issues search "fixed-in:2.4.0" --format json | \
     jq -r '.[] | "- " + .summary + " (" + .id + ")"' > release-notes.txt

Performance Monitoring Workflow
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Scenario**: Monitor and respond to performance issues.

.. code-block:: bash

   # Automated monitoring script (runs every 15 minutes)
   #!/bin/bash

   # 1. Check for performance alerts
   if [[ $(curl -s https://monitoring.company.com/api/alerts | jq '.critical | length') -gt 0 ]]; then

     # 2. Create incident ticket
     INCIDENT_ID=$(yt issues create INFRA "Performance Alert: High Response Time" \
       --description "Automated alert: API response time >2s detected at $(date)" \
       --type "Incident" \
       --priority "Critical" \
       --assignee "devops-oncall" \
       --tags "performance,auto-created" \
       --format json | jq -r '.id')

     # 3. Add monitoring data
     yt issues comments add $INCIDENT_ID "$(curl -s https://monitoring.company.com/api/metrics)"

     # 4. Notify team
     yt issues comments add $INCIDENT_ID "@devops-team @backend-team Performance incident requires immediate attention"
   fi

   # Manual incident response:
   # 5. Investigate and update
   yt issues update INFRA-456 --state "In Progress"
   yt issues comments add INFRA-456 "Investigation: Database query optimization needed. Identified slow query in user_analytics table."

   # 6. Track resolution
   yt time log INFRA-456 "45m" --description "Performance investigation and database optimization"
   yt issues update INFRA-456 --state "Resolved"
   yt issues comments add INFRA-456 "✅ Resolved: Added database index, response time back to <500ms"

Automation and Scripting Workflows
-----------------------------------

Bulk Operations Workflow
~~~~~~~~~~~~~~~~~~~~~~~~~

**Scenario**: Update multiple issues based on common criteria.

.. code-block:: bash

   # 1. Find all issues with specific criteria
   yt issues search "tag:legacy priority:Low state:Open" \
     --format json > legacy-issues.json

   # 2. Bulk update priority
   for issue in $(jq -r '.[].id' legacy-issues.json); do
     yt issues update $issue --priority "Medium" \
       --tags "technical-debt" --tags "-legacy"
     echo "Updated $issue"
     sleep 1  # Rate limiting
   done

   # 3. Add bulk comment
   for issue in $(jq -r '.[].id' legacy-issues.json); do
     yt issues comments add $issue "Priority updated as part of technical debt review. Scheduled for Q2 cleanup sprint."
     sleep 1
   done

Reporting and Analytics Workflow
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Scenario**: Generate comprehensive project reports.

.. code-block:: bash

   # 1. Team productivity report
   yt time report --from "2024-01-01" --to "2024-01-31" \
     --project WEB-FRONTEND --format json > team-time.json

   # 2. Issue velocity analysis
   yt issues search "project:WEB-FRONTEND resolved:this-month" \
     --format json > resolved-issues.json

   # 3. Bug trend analysis
   yt issues search "type:Bug created:this-quarter" \
     --format json > bug-trends.json

   # 4. Generate summary report
   cat << EOF > monthly-report.md
   # Monthly Project Report - $(date +'%B %Y')

   ## Issues Resolved
   $(jq 'length' resolved-issues.json) issues completed

   ## Time Tracking
   Total hours: $(jq '[.[] | .duration] | add' team-time.json)

   ## Bug Analysis
   New bugs: $(jq 'length' bug-trends.json)
   EOF

Integration with External Tools
-------------------------------

Slack Integration Workflow
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Scenario**: Send YouTrack updates to Slack channels.

.. code-block:: bash

   # Script to send daily standup summary to Slack
   #!/bin/bash

   SLACK_WEBHOOK="https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"

   # 1. Get today's activity
   COMPLETED=$(yt issues search "resolved:today" --format json | jq 'length')
   IN_PROGRESS=$(yt issues search "state:\"In Progress\" updated:today" --format json | jq 'length')

   # 2. Format Slack message
   MESSAGE="{
     \"text\": \"Daily YouTrack Summary\",
     \"attachments\": [{
       \"color\": \"good\",
       \"fields\": [
         {\"title\": \"Issues Completed Today\", \"value\": \"$COMPLETED\", \"short\": true},
         {\"title\": \"Issues In Progress\", \"value\": \"$IN_PROGRESS\", \"short\": true}
       ]
     }]
   }"

   # 3. Send to Slack
   curl -X POST -H 'Content-type: application/json' \
     --data "$MESSAGE" $SLACK_WEBHOOK

JIRA Migration Workflow
~~~~~~~~~~~~~~~~~~~~~~~~

**Scenario**: Migrate issues from JIRA to YouTrack.

.. code-block:: bash

   # 1. Export JIRA data (requires JIRA CLI or API)
   # This is a simplified example

   # 2. Create corresponding projects in YouTrack
   yt projects create --name "Web Frontend" --key "WEB" \
     --description "Migrated from JIRA project WEBFRONT"

   # 3. Process JIRA export file
   while IFS=',' read -r jira_id summary description priority assignee; do
     # Create issue in YouTrack
     YT_ID=$(yt issues create WEB "$summary" \
       --description "$description" \
       --priority "$priority" \
       --assignee "$assignee" \
       --tags "migrated-from-jira" \
       --format json | jq -r '.id')

     # Track migration mapping
     echo "$jira_id,$YT_ID" >> migration-mapping.csv

     echo "Migrated $jira_id -> $YT_ID"
     sleep 2  # Rate limiting
   done < jira-export.csv

   # 4. Add migration notes
   for yt_id in $(cut -d',' -f2 migration-mapping.csv); do
     yt issues comments add $yt_id "Migrated from JIRA. Original creation date and history preserved in description."
   done

Best Practices for Workflows
-----------------------------

Script Safety Tips
~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # 1. Always use error handling
   set -e  # Exit on any error

   # 2. Test with limited scope first
   yt issues search "project:TEST-PROJECT" --limit 5

   # 3. Use dry-run when available
   echo "Would update: $(yt issues search 'tag:to-update' --format json | jq 'length') issues"

   # 4. Add rate limiting
   sleep 1  # Between API calls

   # 5. Log all operations
   exec > >(tee -a script.log)
   exec 2>&1

Performance Optimization
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # 1. Use specific filters to reduce data transfer
   yt issues search "project:WEB created:today" --limit 50

   # 2. Batch operations when possible
   # Instead of individual updates, use bulk patterns

   # 3. Cache frequently accessed data
   yt projects list --format json > projects-cache.json

   # 4. Use appropriate output formats
   yt issues list --format json | jq '.[] | {id, summary}'  # Extract only needed fields

Error Handling Patterns
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # 1. Check if issue exists before updating
   if yt issues get WEB-123 >/dev/null 2>&1; then
     yt issues update WEB-123 --state "In Progress"
   else
     echo "Issue WEB-123 not found"
   fi

   # 2. Validate inputs
   if [[ ! "$ISSUE_ID" =~ ^[A-Z]+-[0-9]+$ ]]; then
     echo "Invalid issue ID format: $ISSUE_ID"
     exit 1
   fi

   # 3. Retry on failures
   for i in {1..3}; do
     if yt issues create PROJECT "Issue" --description "Desc"; then
       break
     else
       echo "Attempt $i failed, retrying in 5 seconds..."
       sleep 5
     fi
   done

See Also
--------

- :doc:`quickstart` - Basic CLI usage
- :doc:`configuration` - Setting up your environment
- :doc:`troubleshooting` - Resolving common issues
- :doc:`commands/index` - Complete command reference
