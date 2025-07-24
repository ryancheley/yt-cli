"""
Centralized custom field management utilities for YouTrack CLI.

This module provides a unified interface for creating, extracting, and manipulating
custom fields across the YouTrack CLI application, reducing code duplication and
improving maintainability.
"""

from typing import Any, Dict, List, Optional, Union

from .custom_field_types import CustomFieldValueTypes, IssueCustomFieldTypes, ProjectCustomFieldTypes, get_display_name


class CustomFieldManager:
    """Centralized manager for YouTrack custom field operations."""

    @staticmethod
    def create_single_enum_field(name: str, value: str) -> Dict[str, Any]:
        """
        Create a single enum custom field dictionary.

        Args:
            name: The field name
            value: The enum value name

        Returns:
            Dictionary representing the custom field
        """
        return {
            "$type": IssueCustomFieldTypes.SINGLE_ENUM,
            "name": name,
            "value": {"$type": CustomFieldValueTypes.ENUM_BUNDLE_ELEMENT, "name": value},
        }

    @staticmethod
    def create_multi_enum_field(name: str, values: List[str]) -> Dict[str, Any]:
        """
        Create a multi enum custom field dictionary.

        Args:
            name: The field name
            values: List of enum value names

        Returns:
            Dictionary representing the custom field
        """
        return {
            "$type": IssueCustomFieldTypes.MULTI_ENUM,
            "name": name,
            "value": [{"$type": CustomFieldValueTypes.ENUM_BUNDLE_ELEMENT, "name": value} for value in values],
        }

    @staticmethod
    def create_state_field(name: str, value: str) -> Dict[str, Any]:
        """
        Create a state custom field dictionary.

        Args:
            name: The field name
            value: The state value name

        Returns:
            Dictionary representing the custom field
        """
        return {
            "$type": IssueCustomFieldTypes.STATE,
            "name": name,
            "value": {"$type": CustomFieldValueTypes.STATE_BUNDLE_ELEMENT, "name": value},
        }

    @staticmethod
    def create_single_user_field(name: str, user_login: str) -> Dict[str, Any]:
        """
        Create a single user custom field dictionary.

        Args:
            name: The field name
            user_login: The user login/ID

        Returns:
            Dictionary representing the custom field
        """
        return {
            "$type": IssueCustomFieldTypes.SINGLE_USER,
            "name": name,
            "value": {"$type": CustomFieldValueTypes.USER, "login": user_login},
        }

    @staticmethod
    def create_multi_user_field(name: str, user_logins: List[str]) -> Dict[str, Any]:
        """
        Create a multi user custom field dictionary.

        Args:
            name: The field name
            user_logins: List of user logins/IDs

        Returns:
            Dictionary representing the custom field
        """
        return {
            "$type": IssueCustomFieldTypes.MULTI_USER,
            "name": name,
            "value": [{"$type": CustomFieldValueTypes.USER, "login": user_login} for user_login in user_logins],
        }

    @staticmethod
    def create_text_field(name: str, text: str) -> Dict[str, Any]:
        """
        Create a text custom field dictionary.

        Args:
            name: The field name
            text: The text value

        Returns:
            Dictionary representing the custom field
        """
        return {
            "$type": IssueCustomFieldTypes.TEXT,
            "name": name,
            "value": {"$type": CustomFieldValueTypes.TEXT_VALUE, "text": text},
        }

    @staticmethod
    def extract_field_value(custom_fields: List[Dict[str, Any]], field_name: str) -> Any:
        """
        Extract a custom field value by field name.

        Args:
            custom_fields: List of custom field dictionaries
            field_name: Name of the field to extract

        Returns:
            The field value or None if not found
        """
        if not custom_fields:
            return None

        for field in custom_fields:
            # Handle invalid field structures
            if not isinstance(field, dict):
                continue

            if field.get("name") == field_name:
                value = field.get("value")
                if value is None:
                    return None

                # Handle different value types
                return CustomFieldManager._extract_dict_value(value)

        return None

    @staticmethod
    def _extract_dict_value(value: Union[Dict, List, str, int, float]) -> Any:
        """
        Extract value from a custom field value dictionary or list.

        Args:
            value: The value dictionary, list, or primitive value

        Returns:
            Extracted value in appropriate format
        """
        if isinstance(value, list):
            # Multi-value field - extract values and join with comma
            extracted_values = [CustomFieldManager._extract_dict_value(item) for item in value]
            # Filter out None values and join with comma
            valid_values = [str(v) for v in extracted_values if v is not None]
            return ", ".join(valid_values) if valid_values else None

        if not isinstance(value, dict):
            # Primitive value
            return value

        # Handle empty dictionaries
        if not value:
            return None

        # Priority-based extraction following the documented order
        extraction_keys = [
            "presentation",
            "fullName",
            "localizedName",
            "text",
            "name",
            "buildLink",
            "avatarUrl",
            "minutes",
            "isResolved",
            "color",
            "login",
            "id",
        ]

        for key in extraction_keys:
            if key in value and value[key] is not None:
                extracted_value = value[key]
                # Handle nested structures for color(id)
                if key == "color" and isinstance(extracted_value, dict):
                    return extracted_value.get("id", str(extracted_value))
                # Convert boolean and numeric values to strings
                return str(extracted_value)

        # Return the whole dictionary if no specific field found
        return value

    @staticmethod
    def get_field_id(custom_fields: List[Dict[str, Any]], field_name: str) -> Optional[str]:
        """
        Get the ID of a custom field by name.

        Args:
            custom_fields: List of custom field dictionaries
            field_name: Name of the field

        Returns:
            Field ID or None if not found
        """
        if not custom_fields:
            return None

        for field in custom_fields:
            if field.get("name") == field_name:
                return field.get("id")

        return None

    @staticmethod
    def format_field_type_for_display(field_type: str) -> str:
        """
        Format a field type string for display purposes.

        Args:
            field_type: The YouTrack API field type

        Returns:
            Human-readable field type name
        """
        return get_display_name(field_type)

    @staticmethod
    def get_field_with_fallback(issue: Dict[str, Any], primary_field: str, fallback_field: str) -> Any:
        """
        Get a field value with fallback to custom fields.

        Args:
            issue: The issue dictionary
            primary_field: Primary field name to check
            fallback_field: Fallback custom field name

        Returns:
            Field value from primary field or custom fields
        """
        # Try primary field first
        primary_value = issue.get(primary_field)
        if primary_value is not None:
            return primary_value

        # Fallback to custom fields
        custom_fields = issue.get("customFields", [])
        return CustomFieldManager.extract_field_value(custom_fields, fallback_field)

    @staticmethod
    def create_project_enum_field_config(
        field_type: str, can_be_empty: bool = True, empty_field_text: str = "No value", is_public: bool = True
    ) -> Dict[str, Any]:
        """
        Create configuration for attaching an enum field to a project.

        Args:
            field_type: The project custom field type
            can_be_empty: Whether the field can be empty
            empty_field_text: Text to show when field is empty
            is_public: Whether the field is public

        Returns:
            Configuration dictionary for the field
        """
        return {
            "$type": field_type,
            "canBeEmpty": can_be_empty,
            "emptyFieldText": empty_field_text,
            "isPublic": is_public,
        }

    @staticmethod
    def extract_user_field_info(user_value: Dict[str, Any]) -> Dict[str, str]:
        """
        Extract comprehensive user information from a user field value.

        Args:
            user_value: User field value dictionary

        Returns:
            Dictionary with user information (login, fullName, etc.)
        """
        if not isinstance(user_value, dict):
            return {}

        return {
            "login": user_value.get("login", ""),
            "fullName": user_value.get("fullName", ""),
            "name": user_value.get("name", ""),
            "email": user_value.get("email", ""),
            "avatarUrl": user_value.get("avatarUrl", ""),
        }

    @staticmethod
    def is_multi_value_field(field_type: str) -> bool:
        """
        Check if a field type is multi-value.

        Args:
            field_type: The field type string

        Returns:
            True if the field type supports multiple values
        """
        multi_value_types = {
            IssueCustomFieldTypes.MULTI_ENUM,
            IssueCustomFieldTypes.MULTI_USER,
            IssueCustomFieldTypes.MULTI_VERSION,
            IssueCustomFieldTypes.MULTI_BUILD,
            IssueCustomFieldTypes.MULTI_OWN_BUILD,
            ProjectCustomFieldTypes.MULTI_ENUM,
            ProjectCustomFieldTypes.MULTI_USER,
            ProjectCustomFieldTypes.MULTI_VERSION,
            ProjectCustomFieldTypes.MULTI_BUILD,
            ProjectCustomFieldTypes.MULTI_OWN_BUILD,
        }
        return field_type in multi_value_types
