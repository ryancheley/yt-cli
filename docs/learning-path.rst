Learning Path Guide
==================

This guide provides a structured approach to learning YouTrack CLI, from complete beginner to advanced user.

.. contents:: Table of Contents
   :local:
   :depth: 2

Learning Levels Overview
------------------------

**Beginner (Level 1)**: First-time CLI users, new to YouTrack
- Focus: Basic operations, understanding concepts
- Time: 2-3 hours
- Goal: Create and manage your first issues

**Intermediate (Level 2)**: Comfortable with basics, ready for workflows
- Focus: Team collaboration, automation basics
- Time: 4-6 hours
- Goal: Participate effectively in team workflows

**Advanced (Level 3)**: Power users, automation and integration
- Focus: Scripting, CI/CD integration, advanced features
- Time: 8+ hours
- Goal: Automate workflows and integrate with other tools

Level 1: Beginner (Complete Newcomer)
-------------------------------------

Prerequisites Check
~~~~~~~~~~~~~~~~~~~

Before starting, ensure you have:

- Python 3.9+ installed
- Basic command line familiarity (cd, ls, basic navigation)
- Access to a YouTrack instance
- Your YouTrack credentials or API token

**Time Estimate**: 15 minutes to verify prerequisites

Module 1.1: Installation and Setup (30 minutes)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Learning Objectives**:
- Install YouTrack CLI
- Configure authentication
- Verify setup is working

**Step-by-Step Practice**:

1. **Install YouTrack CLI**:

   .. code-block:: bash

      pip install youtrack-cli
      yt --version

2. **First authentication**:

   .. code-block:: bash

      yt auth login
      # Follow prompts to enter YouTrack URL, username, password

3. **Verify connection**:

   .. code-block:: bash

      yt projects list

**Success Criteria**: You can see a list of projects you have access to.

**Common Issues**: See :doc:`troubleshooting` if you encounter problems.

Module 1.2: Understanding YouTrack Concepts (45 minutes)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Learning Objectives**:
- Understand issues, projects, states, priorities
- Learn how CLI operations map to YouTrack web interface

**Essential Reading**: Complete :doc:`youtrack-concepts` guide

**Hands-On Exercise**:

1. **Explore existing data**:

   .. code-block:: bash

      # See what projects exist
      yt projects list

      # Look at issues in a project (replace PROJECT-KEY with actual project)
      yt issues list --project PROJECT-KEY --limit 5

      # Examine one issue in detail
      yt issues get ISSUE-ID

2. **Understand the data structure**:

   - Note the issue ID format (PROJECT-123)
   - Observe different states (Open, In Progress, Resolved)
   - See priority levels and assignees

**Success Criteria**: You can explain what an issue is and how projects organize them.

Module 1.3: Basic Issue Operations (60 minutes)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Learning Objectives**:
- Create your first issue
- Update issue fields
- Add comments

**Practice Exercises**:

**Exercise 1: Create a Test Issue**

.. code-block:: bash

   # Create a simple test issue
   yt issues create PROJECT-KEY "Learning CLI - Test Issue" \
     --description "This is my first issue created with YouTrack CLI" \
     --type "Task" \
     --priority "Low"

**Exercise 2: Update the Issue**

.. code-block:: bash

   # Update the issue you just created (use the ID from previous command)
   yt issues update ISSUE-ID --state "In Progress" --assignee me

**Exercise 3: Add Comments**

.. code-block:: bash

   # Add a comment to track your progress
   yt issues comments add ISSUE-ID "Learning how to use YouTrack CLI. Making good progress!"

**Exercise 4: Complete the Issue**

.. code-block:: bash

   # Mark the issue as done
   yt issues update ISSUE-ID --state "Resolved"

**Success Criteria**: You've created, updated, and completed your first issue.

Module 1.4: Searching and Filtering (45 minutes)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Learning Objectives**:
- Find issues using search
- Use filters effectively
- Understand search syntax

**Practice Exercises**:

**Exercise 1: Basic Searches**

.. code-block:: bash

   # Find issues assigned to you
   yt issues list --assignee me

   # Find issues in a specific state
   yt issues list --state "Open"

   # Find issues with specific priority
   yt issues list --priority "High"

**Exercise 2: Advanced Search**

.. code-block:: bash

   # Use search query syntax
   yt issues search "assignee:me state:Open"

   # Search by date
   yt issues search "created:today"

   # Search in description text
   yt issues search "login bug"

**Exercise 3: Combining Filters**

.. code-block:: bash

   # Multiple criteria
   yt issues search "assignee:me priority:High state:{Open,\"In Progress\"}"

**Success Criteria**: You can find specific issues using various search criteria.

Level 1 Assessment
~~~~~~~~~~~~~~~~~~~

**Time**: 30 minutes

Complete these tasks to verify your Level 1 skills:

1. Create a bug report issue with appropriate priority and description
2. Assign it to yourself and move it to "In Progress"
3. Add a comment with investigation notes
4. Find all issues assigned to you that are currently open
5. Mark the bug as resolved

**Level 1 Completion Badge**: You understand basic YouTrack CLI operations! 🎉

Level 2: Intermediate (Team Collaborator)
-----------------------------------------

Prerequisites
~~~~~~~~~~~~~

- Completed Level 1 successfully
- Worked with issues for at least a week
- Understanding of basic development workflows

Module 2.1: Team Workflows (60 minutes)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Learning Objectives**:
- Participate in code review processes
- Use tags for organization
- Collaborate through comments

**Practice Exercises**:

**Exercise 1: Code Review Workflow**

.. code-block:: bash

   # Scenario: You've finished coding and need review
   yt issues update YOUR-ISSUE --state "In Review" \
     --assignee "team-lead" \
     --tags "ready-for-review"

   # Add review request
   yt issues comments add YOUR-ISSUE "Ready for review. Changes in payment processing module. Focus on error handling."

**Exercise 2: Bug Triage Participation**

.. code-block:: bash

   # Find bugs needing triage
   yt issues search "type:Bug state:Open priority:Unassigned"

   # Add triage comment
   yt issues comments add BUG-ID "Can reproduce on Chrome 120. Affects checkout flow. Suggest priority: High"

**Success Criteria**: You can effectively communicate with team members through YouTrack.

Module 2.2: Time Tracking and Reporting (45 minutes)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Learning Objectives**:
- Log work time accurately
- Generate time reports
- Understand time tracking best practices

**Practice Exercises**:

**Exercise 1: Time Logging**

.. code-block:: bash

   # Log time for different activities
   yt time log ISSUE-ID "2h 30m" --description "Bug investigation and root cause analysis"
   yt time log ISSUE-ID "1h 15m" --description "Code implementation and unit tests"
   yt time log ISSUE-ID "45m" --description "Documentation updates"

**Exercise 2: Time Reports**

.. code-block:: bash

   # Personal time report
   yt time report --from "2024-01-01" --to "2024-01-07" --assignee me

   # Project time report
   yt time report --project PROJECT-KEY --from "this-week"

**Success Criteria**: You can track and report time spent on development work.

Module 2.3: Advanced Issue Management (75 minutes)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Learning Objectives**:
- Manage issue relationships (links)
- Use tags effectively for organization
- Handle attachments

**Practice Exercises**:

**Exercise 1: Issue Relationships**

.. code-block:: bash

   # Create related issues
   yt issues create PROJECT "Epic: User Authentication System" --type "Epic"
   yt issues create PROJECT "Implement login page" --type "Task"
   yt issues create PROJECT "Add password reset" --type "Task"

   # Link them together
   yt issues links create TASK-1 "subtask of" EPIC-1
   yt issues links create TASK-2 "subtask of" EPIC-1

**Exercise 2: Tag Management**

.. code-block:: bash

   # Add organization tags
   yt issues update ISSUE-ID --tags "frontend,sprint-15,critical-path"

   # Search by tags
   yt issues search "tag:{frontend,urgent}"

**Exercise 3: File Attachments**

.. code-block:: bash

   # Upload screenshot of bug
   yt issues attach upload ISSUE-ID ~/Desktop/bug-screenshot.png

   # List attachments
   yt issues attach list ISSUE-ID

**Success Criteria**: You can manage complex issue relationships and organization.

Module 2.4: Project Management Basics (60 minutes)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Learning Objectives**:
- Understand project settings
- Manage user assignments
- Use boards for workflow visualization

**Practice Exercises**:

**Exercise 1: Project Exploration**

.. code-block:: bash

   # List project details
   yt projects list --detailed

   # View project configuration
   yt projects configure PROJECT-KEY --show

**Exercise 2: Board Operations**

.. code-block:: bash

   # List agile boards
   yt boards list

   # View board details
   yt boards view BOARD-ID

**Success Criteria**: You understand how projects organize work and teams.

Level 2 Assessment
~~~~~~~~~~~~~~~~~~~

**Time**: 45 minutes

Complete a realistic team scenario:

1. **Bug Report Scenario**: Create a bug report from a user complaint
2. **Investigation**: Add comments tracking your investigation
3. **Code Review**: Move to review state and request specific reviewer
4. **Time Tracking**: Log realistic time for each activity
5. **Collaboration**: Link to related issues and add appropriate tags

**Level 2 Completion Badge**: You're an effective team collaborator! 🚀

Level 3: Advanced (Power User)
------------------------------

Prerequisites
~~~~~~~~~~~~~

- Completed Level 2 successfully
- Regular YouTrack CLI user for 1+ months
- Comfortable with command line scripting
- Understanding of CI/CD concepts

Module 3.1: Automation and Scripting (90 minutes)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Learning Objectives**:
- Write shell scripts for bulk operations
- Implement error handling and rate limiting
- Create reusable automation patterns

**Practice Exercises**:

**Exercise 1: Bulk Update Script**

.. code-block:: bash

   #!/bin/bash
   # Script to update multiple issues

   set -e  # Exit on error

   # Find issues to update
   ISSUES=$(yt issues search "tag:legacy-code state:Open" --format json)

   # Process each issue
   echo "$ISSUES" | jq -r '.[].id' | while read issue_id; do
     echo "Updating $issue_id..."

     # Update with error handling
     if yt issues update "$issue_id" --tags "technical-debt" --priority "Medium"; then
       echo "✅ Updated $issue_id"
     else
       echo "❌ Failed to update $issue_id"
     fi

     sleep 1  # Rate limiting
   done

**Exercise 2: Daily Report Generator**

.. code-block:: bash

   #!/bin/bash
   # Generate daily team report

   DATE=$(date +%Y-%m-%d)
   REPORT_FILE="daily-report-$DATE.md"

   cat << EOF > "$REPORT_FILE"
   # Daily Report - $DATE

   ## Issues Completed
   $(yt issues search "resolved:today" --format json | jq 'length') issues

   ## Active Issues
   $(yt issues search "state:\"In Progress\" updated:today" --format json | jq 'length') issues

   ## Time Logged
   $(yt time report --from today --to today --format json | jq '[.[] | .duration] | add // 0') hours
   EOF

   echo "Report generated: $REPORT_FILE"

**Success Criteria**: You can automate repetitive YouTrack operations.

Module 3.2: CI/CD Integration (120 minutes)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Learning Objectives**:
- Integrate YouTrack CLI with GitHub Actions
- Automate issue updates from deployment pipelines
- Handle branch-to-issue mapping

**Practice Exercises**:

**Exercise 1: GitHub Actions Integration**

Create `.github/workflows/youtrack.yml`:

.. code-block:: yaml

   name: YouTrack Integration

   on:
     pull_request:
       types: [opened, synchronize, closed]
     push:
       branches: [main]

   jobs:
     youtrack-update:
       runs-on: ubuntu-latest
       if: contains(github.head_ref, 'WEB-') || contains(github.head_ref, 'API-')

       steps:
         - name: Extract Issue ID
           run: |
             ISSUE_ID=$(echo "${{ github.head_ref }}" | grep -oE '[A-Z]+-[0-9]+')
             echo "ISSUE_ID=$ISSUE_ID" >> $GITHUB_ENV

         - name: Install YouTrack CLI
           run: pip install youtrack-cli

         - name: Configure YouTrack CLI
           run: |
             mkdir -p ~/.config/youtrack-cli
             echo "YOUTRACK_BASE_URL=${{ secrets.YOUTRACK_URL }}" >> ~/.config/youtrack-cli/.env
             echo "YOUTRACK_TOKEN=${{ secrets.YOUTRACK_TOKEN }}" >> ~/.config/youtrack-cli/.env

         - name: Update Issue on PR
           if: github.event.action == 'opened'
           run: |
             yt issues update $ISSUE_ID --state "In Review"
             yt issues comments add $ISSUE_ID "🔄 PR opened: ${{ github.event.pull_request.html_url }}"

         - name: Update Issue on Merge
           if: github.event.action == 'closed' && github.event.pull_request.merged
           run: |
             yt issues update $ISSUE_ID --state "Testing"
             yt issues comments add $ISSUE_ID "✅ Merged to main - deployed to staging"

**Exercise 2: Deployment Integration**

.. code-block:: bash

   # deployment-script.sh
   #!/bin/bash

   VERSION=$1
   ENVIRONMENT=$2

   # Get issues included in this deployment
   ISSUES=$(git log --oneline "$PREVIOUS_VERSION..$VERSION" | grep -oE '[A-Z]+-[0-9]+' | sort -u)

   # Update each issue
   for issue in $ISSUES; do
     if [[ "$ENVIRONMENT" == "production" ]]; then
       yt issues update "$issue" --state "Done"
       yt issues comments add "$issue" "🚀 Deployed to production in version $VERSION"
     else
       yt issues comments add "$issue" "📦 Deployed to $ENVIRONMENT in version $VERSION"
     fi
   done

**Success Criteria**: Your CI/CD pipeline automatically updates YouTrack issues.

Module 3.3: Advanced Reporting and Analytics (90 minutes)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Learning Objectives**:
- Create custom reports using JSON output
- Generate charts and visualizations
- Build team dashboard data

**Practice Exercises**:

**Exercise 1: Velocity Analysis**

.. code-block:: bash

   #!/bin/bash
   # Calculate team velocity over last 4 sprints

   for sprint in {12..15}; do
     COMPLETED=$(yt issues search "tag:sprint-$sprint state:{Done,Resolved}" --format json | jq 'length')
     POINTS=$(yt issues search "tag:sprint-$sprint state:{Done,Resolved}" --format json | \
              jq '[.[] | .storyPoints // 1] | add')

     echo "Sprint $sprint: $COMPLETED issues, $POINTS points"
   done

**Exercise 2: Bug Trend Analysis**

.. code-block:: bash

   #!/bin/bash
   # Generate bug trend data for last 30 days

   echo "Date,Created,Resolved,Open" > bug-trends.csv

   for i in {30..0}; do
     DATE=$(date -d "$i days ago" +%Y-%m-%d)

     CREATED=$(yt issues search "type:Bug created:$DATE" --format json | jq 'length')
     RESOLVED=$(yt issues search "type:Bug resolved:$DATE" --format json | jq 'length')
     OPEN=$(yt issues search "type:Bug state:Open created:..$DATE" --format json | jq 'length')

     echo "$DATE,$CREATED,$RESOLVED,$OPEN" >> bug-trends.csv
   done

**Success Criteria**: You can generate custom analytics from YouTrack data.

Module 3.4: Integration with External Tools (120 minutes)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Learning Objectives**:
- Connect YouTrack with Slack/Teams
- Integrate with monitoring systems
- Build custom webhooks and notifications

**Practice Exercises**:

**Exercise 1: Slack Integration**

.. code-block:: bash

   #!/bin/bash
   # Send daily summary to Slack

   SLACK_WEBHOOK="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"

   # Get today's stats
   CREATED_TODAY=$(yt issues search "created:today" --format json | jq 'length')
   COMPLETED_TODAY=$(yt issues search "resolved:today" --format json | jq 'length')
   IN_PROGRESS=$(yt issues search "state:\"In Progress\"" --format json | jq 'length')

   # Format Slack message
   MESSAGE=$(cat << EOF
   {
     "text": "📊 Daily YouTrack Summary",
     "attachments": [{
       "color": "good",
       "fields": [
         {"title": "Issues Created", "value": "$CREATED_TODAY", "short": true},
         {"title": "Issues Completed", "value": "$COMPLETED_TODAY", "short": true},
         {"title": "In Progress", "value": "$IN_PROGRESS", "short": true}
       ]
     }]
   }
   EOF
   )

   # Send to Slack
   curl -X POST -H 'Content-type: application/json' \
        --data "$MESSAGE" "$SLACK_WEBHOOK"

**Exercise 2: Monitoring Integration**

.. code-block:: bash

   #!/bin/bash
   # Create incidents from monitoring alerts

   # Read alert from monitoring system (example)
   ALERT_DATA=$(cat /tmp/alert.json)

   # Parse alert details
   SERVICE=$(echo "$ALERT_DATA" | jq -r '.service')
   SEVERITY=$(echo "$ALERT_DATA" | jq -r '.severity')
   MESSAGE=$(echo "$ALERT_DATA" | jq -r '.message')

   # Create incident in YouTrack
   INCIDENT_ID=$(yt issues create INFRA "Service Alert: $SERVICE" \
     --description "Automated incident from monitoring: $MESSAGE" \
     --type "Incident" \
     --priority "$SEVERITY" \
     --assignee "oncall-engineer" \
     --tags "auto-created,monitoring" \
     --format json | jq -r '.id')

   # Add monitoring data as comment
   yt issues comments add "$INCIDENT_ID" "$(echo "$ALERT_DATA" | jq .)"

**Success Criteria**: YouTrack integrates seamlessly with your development ecosystem.

Level 3 Assessment
~~~~~~~~~~~~~~~~~~~

**Time**: 2 hours

Build a complete automation solution:

1. **Monitoring Integration**: Create a script that monitors for high-priority bugs and automatically escalates them
2. **CI/CD Pipeline**: Set up branch-to-issue automation in your preferred CI system
3. **Custom Reporting**: Build a dashboard script that generates team metrics
4. **External Integration**: Connect YouTrack updates to your team chat system

**Level 3 Completion Badge**: You're a YouTrack CLI power user! 🏆

Beyond Level 3: Mastery Path
----------------------------

API Development
~~~~~~~~~~~~~~~

- Learn YouTrack REST API directly
- Build custom applications using YouTrack data
- Contribute to YouTrack CLI development

Team Leadership
~~~~~~~~~~~~~~~

- Design workflow standards for your team
- Create training materials for new team members
- Optimize team processes using YouTrack automation

System Architecture
~~~~~~~~~~~~~~~~~~~

- Design enterprise-scale YouTrack integrations
- Build microservices that interact with YouTrack
- Implement custom authentication and security

Common Learning Patterns
-------------------------

Learning Styles
~~~~~~~~~~~~~~~

**Visual Learners**:
- Use ``--format table`` for clear data display
- Examine YouTrack web interface alongside CLI commands
- Draw workflow diagrams mapping CLI commands to processes

**Hands-On Learners**:
- Start with real work issues, not test data
- Experiment with variations of each command
- Build personal automation scripts for daily tasks

**Analytical Learners**:
- Study the :doc:`commands/index` reference thoroughly
- Understand the data model and relationships
- Focus on JSON output and data transformation

Study Schedule Recommendations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Part-Time Learning** (30 minutes/day):
- Week 1-2: Level 1 (Beginner)
- Week 3-5: Level 2 (Intermediate)
- Week 6-10: Level 3 (Advanced)

**Intensive Learning** (2 hours/day):
- Day 1-2: Level 1 (Beginner)
- Day 3-5: Level 2 (Intermediate)
- Day 6-10: Level 3 (Advanced)

**Weekend Workshop** (8 hours total):
- Saturday Morning: Level 1 (4 hours)
- Saturday Afternoon: Level 2 (4 hours)
- Sunday: Level 3 (8 hours) or review and practice

Practice Projects
~~~~~~~~~~~~~~~~~

**Beginner Projects**:
1. Personal task tracker using YouTrack CLI
2. Daily standup preparation script
3. Simple bug report automation

**Intermediate Projects**:
1. Team sprint dashboard
2. Code review workflow automation
3. Time tracking analysis tool

**Advanced Projects**:
1. Complete CI/CD integration suite
2. Multi-project reporting system
3. Custom YouTrack CLI extension

Troubleshooting Learning Issues
-------------------------------

"Commands Don't Work"
~~~~~~~~~~~~~~~~~~~~~

**Problem**: Examples from documentation fail.

**Solutions**:
1. Check your YouTrack CLI version: ``yt --version``
2. Verify authentication: ``yt auth login --test``
3. Use ``--debug`` flag to see detailed error messages
4. Consult :doc:`troubleshooting` guide

"Too Overwhelming"
~~~~~~~~~~~~~~~~~~

**Problem**: CLI seems too complex.

**Solutions**:
1. Start with Level 1 only, master basics first
2. Use YouTrack web interface alongside CLI to understand concepts
3. Practice with test data before real projects
4. Join community discussions for support

"Can't Remember Commands"
~~~~~~~~~~~~~~~~~~~~~~~~~

**Problem**: Forgetting command syntax.

**Solutions**:
1. Create personal cheat sheet of frequently used commands
2. Use ``--help`` extensively: ``yt issues create --help``
3. Set up shell aliases for common operations
4. Practice daily with small tasks

Certification and Recognition
-----------------------------

Self-Assessment Checklist
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Level 1 Mastery**:
- [ ] Can install and configure YouTrack CLI
- [ ] Understands basic YouTrack concepts
- [ ] Can create, update, and search issues
- [ ] Uses CLI for daily issue management

**Level 2 Mastery**:
- [ ] Participates effectively in team workflows
- [ ] Tracks time and generates reports
- [ ] Manages issue relationships and organization
- [ ] Collaborates through comments and assignments

**Level 3 Mastery**:
- [ ] Writes automation scripts for bulk operations
- [ ] Integrates CLI with CI/CD pipelines
- [ ] Creates custom reports and analytics
- [ ] Builds integrations with external tools

Portfolio Projects
~~~~~~~~~~~~~~~~~~

Document your learning with these portfolio pieces:

1. **Personal Workflow Documentation**: Document how you use YouTrack CLI daily
2. **Team Integration Guide**: Create team-specific workflow documentation
3. **Automation Gallery**: Collection of useful scripts you've written
4. **Integration Showcase**: Examples of CI/CD and external tool integrations

Next Steps
----------

After completing this learning path:

1. **Contribute to Community**: Share scripts and tips with other users
2. **Mentor Others**: Help new team members learn YouTrack CLI
3. **Extend Functionality**: Consider contributing to the YouTrack CLI project
4. **Stay Updated**: Follow project updates and new feature releases

See Also
--------

- :doc:`youtrack-concepts` - Essential YouTrack concepts
- :doc:`quickstart` - Getting started guide
- :doc:`workflows` - Real-world workflow examples
- :doc:`troubleshooting` - Problem-solving guide
- :doc:`commands/index` - Complete command reference
