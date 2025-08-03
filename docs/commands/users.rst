Users Command Group
===================

The ``yt users`` command group provides comprehensive user management capabilities in YouTrack. This includes creating, listing, updating users, and managing their permissions and group memberships.

.. contents:: Table of Contents
   :local:
   :depth: 2

Overview
--------

YouTrack user management involves handling user accounts, permissions, and organizational structure. The users command group allows you to:

* List and search for users
* Create new user accounts with various settings
* Update user information and status
* Manage user permissions and group memberships
* Handle user authentication settings
* Control user access and security settings

Base Command
------------

.. code-block:: bash

   yt users [OPTIONS] COMMAND [ARGS]...

User Management Commands
------------------------

list
~~~~

List all users with filtering and search capabilities.

.. code-block:: bash

   yt users list [OPTIONS]

**Options:**

.. list-table::
   :widths: 20 20 60
   :header-rows: 1

   * - Option
     - Type
     - Description
   * - ``--fields, -f``
     - string
     - Comma-separated list of user fields to return
   * - ``--top, -t``
     - integer
     - Maximum number of users to return
   * - ``--query, -q``
     - string
     - Search query to filter users
   * - ``--active-only``
     - flag
     - Show only active (non-banned) users
   * - ``--format``
     - choice
     - Output format: table, json (default: table)

**Examples:**

.. code-block:: bash

   # List all users
   yt users list

   # List only active (non-banned) users
   yt users list --active-only

   # List users in JSON format
   yt users list --format json

   # Search for users by name or username
   yt users list --query "admin"

   # Search for active users with specific criteria
   yt users list --active-only --query "developer"

   # Limit number of users returned
   yt users list --top 20

   # List active users with specific fields
   yt users list --active-only --fields "id,login,fullName,email"

   # Combine active filter with other options
   yt users list --active-only --top 20 --format json

create
~~~~~~

Create a new user account with specified settings.

.. code-block:: bash

   yt users create LOGIN FULL_NAME EMAIL [OPTIONS]

**Arguments:**

* ``LOGIN`` - The username/login for the new user (required)
* ``FULL_NAME`` - The full display name of the user (required)
* ``EMAIL`` - The email address of the user (required)

**Options:**

.. list-table::
   :widths: 20 20 60
   :header-rows: 1

   * - Option
     - Type
     - Description
   * - ``--password, -p``
     - string
     - User password (will prompt securely if not provided; shows warning if provided via command line)
   * - ``--banned``
     - flag
     - Create user as banned (inactive)
   * - ``--force-change-password``
     - flag
     - Force password change on first login

**Examples:**

.. code-block:: bash

   # Create a basic user (will prompt for password)
   yt users create newuser "New User" "newuser@company.com"

   # Create a user with password and additional options
   yt users create johnsmith "John Smith" "john.smith@company.com" \
     --password secretpass --force-change-password

   # Create a banned user
   yt users create spamuser "Spam User" "spam@example.com" --banned

   # Create user with password prompt for security (recommended)
   yt users create secureuser "Secure User" "secure@company.com"

   # Non-interactive creation for automation (shows security warning)
   yt users create autouser "Auto User" "auto@company.com" \
     --password "temp123" --force-change-password

.. warning::
   When using ``--password`` in scripts, the password may be visible in command
   history and process lists. Consider using environment variables or secure
   password prompting for production automation.

update
~~~~~~

Update user information and settings.

.. code-block:: bash

   yt users update USER_ID [OPTIONS]

**Arguments:**

* ``USER_ID`` - The username or user ID to update (required)

**Options:**

.. list-table::
   :widths: 20 20 60
   :header-rows: 1

   * - Option
     - Type
     - Description
   * - ``--full-name, -n``
     - string
     - New full name
   * - ``--email, -e``
     - string
     - New email address
   * - ``--password, -p``
     - string
     - New password
   * - ``--banned/--unbanned``
     - flag
     - Ban or unban the user
   * - ``--force-change-password``
     - flag
     - Force password change on next login
   * - ``--show-details``
     - flag
     - Show detailed user information

**Examples:**

.. code-block:: bash

   # View detailed user information
   yt users update USERNAME --show-details

   # Update user information
   yt users update USERNAME --full-name "Updated Name"
   yt users update USERNAME --email "newemail@company.com"
   yt users update USERNAME --password "newpassword"

   # Ban or unban a user
   yt users update USERNAME --banned
   yt users update USERNAME --unbanned

   # Force password change on next login
   yt users update USERNAME --force-change-password

   # Update multiple fields at once
   yt users update USERNAME \
     --full-name "New Full Name" \
     --email "new@email.com" \
     --force-change-password

.. note::
   User updates (email, full name, etc.) require proper Hub API configuration.
   On local or test YouTrack instances, these updates may not persist due to
   Hub API limitations. This is a known limitation of test environments.

permissions
~~~~~~~~~~~

Manage user permissions and group memberships.

.. code-block:: bash

   yt users permissions USER_ID [OPTIONS]

**Arguments:**

* ``USER_ID`` - The username or user ID (required)

**Options:**

.. list-table::
   :widths: 20 20 60
   :header-rows: 1

   * - Option
     - Type
     - Description
   * - ``--action, -a``
     - choice
     - Permission action: add_to_group, remove_from_group (required)
   * - ``--group-id, -g``
     - string
     - Group ID for group operations

**Examples:**

.. code-block:: bash

   # Add user to a group
   yt users permissions USERNAME --action add_to_group --group-id developers

   # Remove user from a group
   yt users permissions USERNAME --action remove_from_group --group-id admins

   # Manage multiple group memberships
   yt users permissions USERNAME --action add_to_group --group-id testers
   yt users permissions USERNAME --action add_to_group --group-id reviewers

groups
~~~~~~

Display groups that a user belongs to.

.. code-block:: bash

   yt users groups USER_ID [OPTIONS]

**Arguments:**

* ``USER_ID`` - The username or user ID to query (required)

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

   # View user's groups in table format
   yt users groups john.doe

   # View user's groups in JSON format
   yt users groups admin --format json

   # Check group memberships for a specific user
   yt users groups project.manager

   # Export user group data for reporting
   yt users groups team.lead --format json > user_groups.json

roles
~~~~~

Display roles assigned to a user.

.. code-block:: bash

   yt users roles USER_ID [OPTIONS]

**Arguments:**

* ``USER_ID`` - The username or user ID to query (required)

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

   # View user's roles in table format
   yt users roles john.doe

   # View user's roles in JSON format
   yt users roles admin --format json

   # Check role assignments for project lead
   yt users roles project.lead

   # Export role data for audit purposes
   yt users roles security.admin --format json > user_roles.json

teams
~~~~~

Display teams that a user is a member of.

.. code-block:: bash

   yt users teams USER_ID [OPTIONS]

**Arguments:**

* ``USER_ID`` - The username or user ID to query (required)

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

   # View user's teams in table format
   yt users teams john.doe

   # View user's teams in JSON format
   yt users teams jane.smith --format json

   # Check team memberships for developer
   yt users teams developer.user

   # Export team data for organizational chart
   yt users teams manager.user --format json > user_teams.json

User Management Features
------------------------

**User Account Management**
  Complete lifecycle management of user accounts including creation, updates, and status changes.

**Security Controls**
  Password management, forced password changes, and account banning capabilities.

**Group Membership**
  Manage user permissions through group memberships and role assignments.

**Search and Discovery**
  Powerful search capabilities to find users by various criteria, including filtering by user status (active vs banned).

**Bulk Operations**
  Support for managing multiple users efficiently.

**Status Management**
  Control user account status including active, banned, and password change requirements.

User Account States
-------------------

**Active Users**
  Normal user accounts with full access based on their permissions.

**Banned Users**
  User accounts that are temporarily or permanently restricted from access.

**Password Change Required**
  Users who must change their password on next login for security reasons.

**New Users**
  Recently created accounts that may need initial setup or verification.

Common Workflows
----------------

User Onboarding
~~~~~~~~~~~~~~~

.. code-block:: bash

   # Create new employee account
   yt users create john.doe "John Doe" "john.doe@company.com" \
     --force-change-password

   # Add to appropriate groups
   yt users permissions john.doe --action add_to_group --group-id employees
   yt users permissions john.doe --action add_to_group --group-id developers

   # Verify user creation
   yt users update john.doe --show-details

User Maintenance
~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Update user information
   yt users update john.doe --full-name "John A. Doe"
   yt users update john.doe --email "john.a.doe@company.com"

   # Force password reset for security
   yt users update john.doe --force-change-password

   # View current user settings
   yt users update john.doe --show-details

Security Management
~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Ban suspicious user account
   yt users update suspicious.user --banned

   # Force password change for security incident
   yt users update affected.user --force-change-password

   # Unban user after investigation
   yt users update suspicious.user --unbanned

User Discovery and Reporting
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Search for administrators
   yt users list --query "admin"

   # Find users by department or role
   yt users list --query "developer"

   # List only active users for current operations
   yt users list --active-only

   # Find active developers for team management
   yt users list --active-only --query "developer"

   # Export active user list for reporting
   yt users list --active-only --format json --fields "login,fullName,email" > active_users.json

   # Export all users with status for audit
   yt users list --format json --fields "login,fullName,email,banned" > user_report.json

   # List all users with detailed information
   yt users list --fields "id,login,fullName,email,created,lastAccess,banned"

Permission Management
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Add user to development team
   yt users permissions developer.user --action add_to_group --group-id developers
   yt users permissions developer.user --action add_to_group --group-id code-reviewers

   # Remove user from administrative groups
   yt users permissions former.admin --action remove_from_group --group-id administrators

   # Manage project-specific permissions
   yt users permissions project.lead --action add_to_group --group-id project-managers

Permission Analysis
~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Analyze user's current permissions
   yt users groups john.doe
   yt users roles john.doe
   yt users teams john.doe

   # Export complete permission audit for a user
   yt users groups john.doe --format json > john_groups.json
   yt users roles john.doe --format json > john_roles.json
   yt users teams john.doe --format json > john_teams.json

   # Quick permission check for multiple users
   for user in alice bob charlie; do
     echo "=== Permissions for $user ==="
     yt users groups $user
     echo
   done

   # Verify user has required permissions before project assignment
   yt users roles project.candidate
   yt users groups project.candidate

Best Practices
--------------

1. **Secure Password Policies**: Always use strong passwords and force password changes for new accounts.

2. **Principle of Least Privilege**: Grant users only the minimum permissions needed for their role.

3. **Regular Audits**: Periodically review user accounts and permissions for security compliance.

4. **Group-Based Permissions**: Use groups to manage permissions rather than individual assignments.

5. **Account Lifecycle**: Properly manage the full lifecycle from creation to deactivation.

6. **Documentation**: Maintain clear documentation of user roles and permission structures.

7. **Security Monitoring**: Monitor for suspicious activity and respond appropriately.

8. **Consistent Naming**: Use consistent naming conventions for usernames and groups.

9. **Email Verification**: Ensure email addresses are accurate for communication and password resets.

10. **Deactivation Process**: Have a clear process for handling user departures and account cleanup.

Security Considerations
-----------------------

Password Management
~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Force password change for security
   yt users update USERNAME --force-change-password

   # Update password directly (use with caution)
   yt users update USERNAME --password "new-secure-password"

Account Security
~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Temporarily ban suspicious account
   yt users update SUSPICIOUS_USER --banned

   # Investigate and then reactivate if appropriate
   yt users update SUSPICIOUS_USER --unbanned

   # Force password change after security incident
   yt users update AFFECTED_USER --force-change-password

Access Control
~~~~~~~~~~~~~~

.. code-block:: bash

   # Remove from sensitive groups
   yt users permissions USERNAME --action remove_from_group --group-id administrators
   yt users permissions USERNAME --action remove_from_group --group-id sensitive-project

   # Add to restricted group
   yt users permissions USERNAME --action add_to_group --group-id restricted-users

Output Formats
--------------

Table Format (Default)
~~~~~~~~~~~~~~~~~~~~~~

The default table format provides a clean view of user information:

.. code-block:: text

   ┌──────────────┬─────────────────┬────────────────────────┬─────────┬─────────────────┐
   │ Login        │ Full Name       │ Email                  │ Banned  │ Last Access     │
   ├──────────────┼─────────────────┼────────────────────────┼─────────┼─────────────────┤
   │ john.doe     │ John Doe        │ john.doe@company.com   │ No      │ 2024-01-15      │
   │ jane.smith   │ Jane Smith      │ jane.smith@company.com │ No      │ 2024-01-14      │
   │ admin.user   │ Administrator   │ admin@company.com      │ No      │ 2024-01-15      │
   └──────────────┴─────────────────┴────────────────────────┴─────────┴─────────────────┘

JSON Format
~~~~~~~~~~~

JSON format provides structured data for automation:

.. code-block:: json

   [
     {
       "id": "1-1",
       "login": "john.doe",
       "fullName": "John Doe",
       "email": "john.doe@company.com",
       "banned": false,
       "created": "2024-01-01T10:00:00.000Z",
       "lastAccess": "2024-01-15T09:30:00.000Z",
       "forcePasswordChange": false
     }
   ]

Error Handling
--------------

Common error scenarios and solutions:

**Permission Denied**
  Ensure you have administrative privileges to manage users and permissions.

**User Already Exists**
  Check if a user with the same login or email already exists in the system.

**Invalid Email Format**
  Verify the email address follows proper email format standards.

**Weak Password**
  Ensure passwords meet your organization's security requirements.

**Group Not Found**
  Verify the group ID exists and is accessible for permission management.

**User Not Found**
  Confirm the username or user ID is correct and the user exists.

**Banned User Operations**
  Some operations may be restricted on banned user accounts.

Integration Examples
--------------------

Bulk User Management
~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   #!/bin/bash
   # Bulk user creation from CSV

   while IFS=',' read -r login fullname email; do
     yt users create "$login" "$fullname" "$email" --force-change-password
     yt users permissions "$login" --action add_to_group --group-id employees
   done < new_users.csv

User Audit Script
~~~~~~~~~~~~~~~~~

.. code-block:: bash

   #!/bin/bash
   # Generate user audit report

   echo "User Audit Report - $(date)"
   echo "================================"

   # List all users
   yt users list --format json > users_audit.json

   # Count active vs banned users
   echo "Active users: $(jq '[.[] | select(.banned == false)] | length' users_audit.json)"
   echo "Banned users: $(jq '[.[] | select(.banned == true)] | length' users_audit.json)"

   # Users requiring password change
   echo "Users requiring password change:"
   jq -r '.[] | select(.forcePasswordChange == true) | .login' users_audit.json

Permission Cleanup
~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Remove departed employee from all sensitive groups
   DEPARTED_USER="former.employee"

   # Remove from administrative groups
   yt users permissions "$DEPARTED_USER" --action remove_from_group --group-id administrators
   yt users permissions "$DEPARTED_USER" --action remove_from_group --group-id project-managers

   # Ban the account
   yt users update "$DEPARTED_USER" --banned

See Also
--------

* :doc:`admin` - Administrative operations including user group management
* :doc:`projects` - Project management and user assignments
* :doc:`auth` - Authentication and login management
* :doc:`config` - Configuration management
* :doc:`issues` - Issue assignment and user workflow
