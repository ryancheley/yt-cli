================
Custom Fields
================

The YouTrack CLI provides comprehensive support for custom fields through a centralized custom field management system. This documentation covers how custom fields are handled internally and how to work with them effectively.

Overview
========

Custom fields in YouTrack are dynamic fields that can be added to issues and projects beyond the standard built-in fields. The YouTrack CLI has been designed with a centralized :class:`CustomFieldManager` that simplifies custom field operations across all CLI commands.

Core Components
===============

CustomFieldManager
------------------

The :class:`CustomFieldManager` is the central utility class that handles all custom field operations:

.. code-block:: python

    from youtrack_cli.custom_field_manager import CustomFieldManager

    # Create custom field dictionaries
    priority_field = CustomFieldManager.create_single_enum_field("Priority", "High")
    user_field = CustomFieldManager.create_single_user_field("Assignee", "john.doe")

    # Extract field values
    custom_fields = issue.get("customFields", [])
    priority_value = CustomFieldManager.extract_field_value(custom_fields, "Priority")

Custom Field Types
------------------

The CLI defines constants for all YouTrack custom field types:

Issue Custom Field Types
^^^^^^^^^^^^^^^^^^^^^^^^^

- ``SingleEnumIssueCustomField`` - Single-select dropdown fields
- ``MultiEnumIssueCustomField`` - Multi-select dropdown fields
- ``StateIssueCustomField`` - State/workflow fields
- ``SingleUserIssueCustomField`` - Single user assignment fields
- ``MultiUserIssueCustomField`` - Multi-user assignment fields
- ``TextIssueCustomField`` - Text input fields

Project Custom Field Types
^^^^^^^^^^^^^^^^^^^^^^^^^^^

- ``EnumProjectCustomField`` - Project-level enum fields
- ``MultiEnumProjectCustomField`` - Project-level multi-enum fields
- ``StateProjectCustomField`` - Project-level state fields
- ``SingleUserProjectCustomField`` - Project-level single user fields
- ``MultiUserProjectCustomField`` - Project-level multi-user fields

Field Value Types
^^^^^^^^^^^^^^^^^

- ``EnumBundleElement`` - Values for enum fields
- ``StateBundleElement`` - Values for state fields
- ``User`` - User reference values
- ``TextValue`` - Text field values

Working with Custom Fields
==========================

Creating Custom Fields
-----------------------

The ``CustomFieldManager`` provides factory methods for creating custom field dictionaries:

.. code-block:: python

    # Single enum field (Priority, Type, etc.)
    priority_field = CustomFieldManager.create_single_enum_field("Priority", "Critical")

    # Multi enum field (Tags, Labels, etc.)
    tags_field = CustomFieldManager.create_multi_enum_field("Tags", ["bug", "urgent"])

    # State field
    state_field = CustomFieldManager.create_state_field("State", "In Progress")

    # User field
    assignee_field = CustomFieldManager.create_single_user_field("Assignee", "user.login")

    # Text field
    description_field = CustomFieldManager.create_text_field("Description", "Custom description")

Extracting Field Values
------------------------

To extract values from custom fields:

.. code-block:: python

    # Extract single field value
    custom_fields = issue.get("customFields", [])
    priority = CustomFieldManager.extract_field_value(custom_fields, "Priority")

    # Extract field with fallback to built-in fields
    assignee = CustomFieldManager.get_field_with_fallback(
        issue, "assignee", "Assignee"
    )

Field Type Display
------------------

Convert API field types to human-readable names:

.. code-block:: python

    display_name = CustomFieldManager.format_field_type_for_display(
        "SingleEnumIssueCustomField"
    )
    # Returns: "Single Enum"

CLI Commands and Custom Fields
==============================

Issues Commands
---------------

The issues commands automatically handle custom fields for common use cases:

.. code-block:: bash

    # Create issue with custom fields
    yt issues create PROJECT-ID "Issue Summary" --priority High --type Bug

    # Update issue custom fields
    yt issues update ISSUE-ID --priority Critical --assignee john.doe

    # Search issues by custom field values
    yt issues list --project PROJECT-ID --priority High

Projects Commands
-----------------

Manage custom fields at the project level:

.. code-block:: bash

    # List project custom fields
    yt projects fields list PROJECT-ID

    # Attach a custom field to a project
    yt projects fields attach PROJECT-ID FIELD-ID EnumProjectCustomField

    # Update custom field settings
    yt projects fields update PROJECT-ID FIELD-ID --can-be-empty false

Admin Commands
--------------

System-level custom field management:

.. code-block:: bash

    # List all custom fields in the system
    yt admin fields list

    # View custom field details
    yt admin fields show FIELD-ID

Best Practices
==============

1. **Use Constants**: Always use the predefined field type constants instead of hardcoding strings.

2. **Handle Fallbacks**: When extracting field values, consider using ``get_field_with_fallback`` to check both built-in and custom fields.

3. **Validate Field Types**: Use ``is_multi_value_field`` to determine if a field supports multiple values.

4. **Error Handling**: Custom field operations can fail due to permissions or field configuration. Always handle potential errors gracefully.

5. **Performance**: When working with many custom fields, batch operations when possible to reduce API calls.

Advanced Usage
==============

Multi-Value Fields
------------------

Handle fields that can contain multiple values:

.. code-block:: python

    # Check if field is multi-value
    is_multi = CustomFieldManager.is_multi_value_field("MultiEnumIssueCustomField")

    # Create multi-value field
    reviewers = CustomFieldManager.create_multi_user_field(
        "Reviewers", ["user1", "user2", "user3"]
    )

Project Field Configuration
---------------------------

Configure custom fields when attaching to projects:

.. code-block:: python

    # Create field configuration
    config = CustomFieldManager.create_project_enum_field_config(
        field_type="EnumProjectCustomField",
        can_be_empty=False,
        empty_field_text="Required field",
        is_public=True
    )

User Field Information
----------------------

Extract comprehensive user information from user fields:

.. code-block:: python

    user_info = CustomFieldManager.extract_user_field_info(user_field_value)
    # Returns: {"login": "...", "fullName": "...", "email": "...", ...}

Troubleshooting
===============

Common Issues
-------------

**Field Not Found**: If a custom field is not found, check:
- Field name spelling and case sensitivity
- Field permissions and visibility settings
- Whether the field is attached to the current project

**Type Mismatch**: Ensure you're using the correct field type constants for your specific use case.

**Multi-Value Fields**: Remember that multi-value fields return comma-separated strings when extracted.

**Empty Values**: Empty custom field dictionaries return ``None`` when extracted.

Migration Guide
===============

If you're upgrading from a version before the custom field refactoring:

1. **API Compatibility**: All public APIs remain the same - no code changes required.

2. **Improved Performance**: Field extraction is now more efficient and consistent.

3. **Better Error Handling**: Invalid field structures are now handled gracefully.

4. **Enhanced Display**: Field type names are now consistently formatted across all commands.

The refactoring is fully backward-compatible, so existing scripts and workflows will continue to work without modification.
