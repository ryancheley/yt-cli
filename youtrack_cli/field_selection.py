"""Field selection optimization for YouTrack API calls.

This module provides utilities for dynamic field selection to optimize API performance
by only requesting needed fields based on the command context and user preferences.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Union, cast

from .logging import get_logger

__all__ = [
    "FieldProfile",
    "FieldSelector",
    "get_field_selector",
    "FIELD_PROFILES",
]

logger = get_logger(__name__)


# Predefined field profiles for common use cases
FIELD_PROFILES: Dict[str, Dict[str, List[str]]] = {
    "issues": {
        "minimal": [
            "id",
            "numberInProject",
            "summary",
            "state(name,id)",
        ],
        "standard": [
            "id",
            "numberInProject",
            "summary",
            "description",
            "state(name,id)",
            "priority(name,id)",
            "type(name,id)",
            "assignee(login,fullName,id)",
            "reporter(login,fullName,id)",
            "project(id,name,shortName)",
            "created",
            "updated",
            "customFields(name,value(name,id,login,fullName,text,presentation))",
        ],
        "full": [
            "id",
            "numberInProject",
            "summary",
            "description",
            "state(name,id)",
            "priority(name,id)",
            "type(name,id)",
            "assignee(login,fullName,id)",
            "reporter(login,fullName,id)",
            "project(id,name,shortName)",
            "created",
            "updated",
            "resolved",
            "tags(name,id)",
            "customFields(name,value(name,id,login,fullName,text,presentation))",
            "attachments(name,size,url)",
            "comments(text,author(login,fullName),created)",
            "links(linkType(name),issues(id,summary))",
        ],
    },
    "projects": {
        "minimal": [
            "id",
            "shortName",
            "name",
        ],
        "standard": [
            "id",
            "shortName",
            "name",
            "description",
            "leader(login,fullName)",
            "createdBy(login,fullName)",
            "archived",
        ],
        "full": [
            "id",
            "shortName",
            "name",
            "description",
            "leader(login,fullName)",
            "leader(id)",
            "createdBy(login,fullName)",
            "createdBy(id)",
            "archived",
            "template",
            "customFields(field(name,fieldType),canBeEmpty,emptyFieldText)",
            "team(users(login,fullName,email))",
        ],
    },
    "users": {
        "minimal": [
            "id",
            "login",
            "fullName",
        ],
        "standard": [
            "id",
            "login",
            "fullName",
            "email",
            "online",
            "lastAccessTime",
        ],
        "full": [
            "id",
            "login",
            "fullName",
            "email",
            "online",
            "lastAccessTime",
            "avatarUrl",
            "profiles(general(locale,timezone))",
            "groups(name,id)",
            "savedQueries(name,query)",
        ],
    },
    "time_entries": {
        "minimal": [
            "id",
            "duration",
            "date",
        ],
        "standard": [
            "id",
            "duration",
            "date",
            "description",
            "author(id,fullName)",
            "issue(id,summary)",
            "type(name)",
        ],
        "full": [
            "id",
            "duration",
            "date",
            "description",
            "author(id,fullName)",
            "author(login)",
            "issue(id,summary)",
            "issue(numberInProject)",
            "issue(project(shortName))",
            "type(name)",
            "type(id)",
            "workItem(name,id)",
        ],
    },
    "articles": {
        "minimal": [
            "id",
            "summary",
            "idReadable",
        ],
        "standard": [
            "id",
            "summary",
            "idReadable",
            "content",
            "updated",
            "project(id,shortName)",
            "reporter(login,fullName)",
        ],
        "full": [
            "id",
            "summary",
            "idReadable",
            "content",
            "updated",
            "created",
            "project(id,shortName)",
            "project(name)",
            "reporter(login,fullName)",
            "reporter(id)",
            "updater(login,fullName,id)",
            "visibility(permittedGroups(name),permittedUsers(login))",
            "attachments(name,size,url)",
            "comments(text,author(login,fullName),created)",
        ],
    },
}


class FieldProfile:
    """Represents a field selection profile for a specific entity type."""

    def __init__(self, entity_type: str, profile_name: str, fields: List[str]):
        self.entity_type = entity_type
        self.profile_name = profile_name
        self.fields = fields

    def get_fields_string(self) -> str:
        """Get the fields as a comma-separated string for API calls."""
        return ",".join(self.fields)

    def get_fields_list(self) -> List[str]:
        """Get the fields as a list."""
        return self.fields.copy()

    def __str__(self) -> str:
        return f"{self.entity_type}:{self.profile_name}"


class FieldSelector:
    """Manages field selection optimization for YouTrack API calls."""

    def __init__(self, config_manager=None):
        self._profiles = FIELD_PROFILES
        self._config_manager = config_manager
        self._default_profiles = {
            "issues": "standard",
            "projects": "standard",
            "users": "standard",
            "time_entries": "standard",
            "articles": "standard",
        }
        self._load_config_defaults()

    def _load_config_defaults(self) -> None:
        """Load default field profiles from configuration."""
        if self._config_manager is None:
            return

        try:
            for entity_type in self._default_profiles:
                config_key = f"FIELD_PROFILE_{entity_type.upper()}"
                configured_profile = self._config_manager.get_config(config_key)
                if configured_profile and configured_profile in self.get_available_profiles(entity_type):
                    self._default_profiles[entity_type] = configured_profile
                    logger.debug(
                        "Loaded default profile from config", entity_type=entity_type, profile=configured_profile
                    )
        except Exception as e:
            logger.warning("Failed to load field profile defaults from config", error=str(e))

    def save_default_to_config(self, entity_type: str, profile_name: str) -> bool:
        """Save default profile preference to configuration.

        Args:
            entity_type: Type of entity
            profile_name: Profile name to save as default

        Returns:
            True if saved successfully, False otherwise
        """
        if self._config_manager is None:
            logger.warning("No config manager available to save defaults")
            return False

        if not self.set_default_profile(entity_type, profile_name):
            return False

        try:
            config_key = f"FIELD_PROFILE_{entity_type.upper()}"
            self._config_manager.set_config(config_key, profile_name)
            logger.info(
                "Saved default profile to config", entity_type=entity_type, profile=profile_name, config_key=config_key
            )
            return True
        except Exception as e:
            logger.error("Failed to save default profile to config", error=str(e))
            return False

    def get_profile(self, entity_type: str, profile_name: str) -> Optional[FieldProfile]:
        """Get a specific field profile.

        Args:
            entity_type: Type of entity (issues, projects, users, etc.)
            profile_name: Name of profile (minimal, standard, full)

        Returns:
            FieldProfile if found, None otherwise
        """
        if entity_type not in self._profiles:
            logger.warning("Unknown entity type for field selection", entity_type=entity_type)
            return None

        profiles = self._profiles[entity_type]
        if profile_name not in profiles:
            logger.warning(
                "Unknown profile for entity type",
                entity_type=entity_type,
                profile_name=profile_name,
                available_profiles=list(profiles.keys()),
            )
            return None

        return FieldProfile(entity_type, profile_name, profiles[profile_name])

    def get_fields(
        self,
        entity_type: str,
        profile: Optional[str] = None,
        custom_fields: Optional[Union[str, List[str]]] = None,
        exclude_fields: Optional[List[str]] = None,
    ) -> str:
        """Get optimized field selection for an entity type.

        Args:
            entity_type: Type of entity (issues, projects, users, etc.)
            profile: Profile name (minimal, standard, full) or None for default
            custom_fields: Custom field specification (string or list)
            exclude_fields: Fields to exclude from the selection

        Returns:
            Comma-separated field string for API calls
        """
        # Use default profile if none specified
        if profile is None:
            profile = self._default_profiles.get(entity_type, "standard")

        # Get the base profile
        field_profile = self.get_profile(entity_type, profile)
        if not field_profile:
            # Fallback to full profile for unknown entity/profile
            logger.warning("Falling back to full profile", entity_type=entity_type, requested_profile=profile)
            field_profile = self.get_profile(entity_type, "full")
            if not field_profile:
                # Last resort - return basic fields
                return "id,summary" if entity_type != "users" else "id,login,fullName"

        fields_set = set(field_profile.get_fields_list())

        # Add custom fields if specified
        if custom_fields:
            if isinstance(custom_fields, str):
                custom_fields = [f.strip() for f in custom_fields.split(",")]
            fields_set.update(custom_fields)

        # Remove excluded fields
        if exclude_fields:
            fields_set -= set(exclude_fields)

        # Ensure we always have at least an ID field
        if entity_type == "users":
            fields_set.add("id")
            fields_set.add("login")
        else:
            fields_set.add("id")

        result = ",".join(sorted(fields_set))

        logger.debug(
            "Generated field selection",
            entity_type=entity_type,
            profile=profile,
            field_count=len(fields_set),
            fields=result[:100] + "..." if len(result) > 100 else result,
        )

        return result

    def get_available_profiles(self, entity_type: str) -> List[str]:
        """Get available profiles for an entity type."""
        return list(self._profiles.get(entity_type, {}).keys())

    def get_supported_entities(self) -> List[str]:
        """Get list of supported entity types."""
        return list(self._profiles.keys())

    def set_default_profile(self, entity_type: str, profile_name: str) -> bool:
        """Set the default profile for an entity type.

        Args:
            entity_type: Type of entity
            profile_name: Name of profile to set as default

        Returns:
            True if successful, False if entity type or profile doesn't exist
        """
        if entity_type not in self._profiles:
            return False
        if profile_name not in self._profiles[entity_type]:
            return False

        self._default_profiles[entity_type] = profile_name
        logger.info("Default profile updated", entity_type=entity_type, profile=profile_name)
        return True

    def validate_fields(self, fields: str, entity_type: str) -> bool:
        """Validate that field specification is syntactically correct.

        Args:
            fields: Comma-separated field specification
            entity_type: Type of entity for context

        Returns:
            True if fields appear valid, False otherwise
        """
        if not fields or not fields.strip():
            return False

        try:
            # Check overall parentheses balance first
            open_parens = fields.count("(")
            close_parens = fields.count(")")
            if open_parens != close_parens:
                logger.warning("Unbalanced parentheses in field specification", fields=fields)
                return False

            # Check for valid characters
            allowed_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789().,_ ")
            if not all(c in allowed_chars for c in fields):
                logger.warning("Invalid characters in field specification", fields=fields)
                return False

            # Basic field name validation - ensure we have at least one alphanumeric character
            cleaned = fields.replace("(", "").replace(")", "").replace(",", "").replace(".", "").replace(" ", "")
            if not cleaned or not any(c.isalnum() for c in cleaned):
                logger.warning("No valid field names found", fields=fields)
                return False

            return True

        except Exception as e:
            logger.warning("Field validation error", fields=fields, error=str(e))
            return False


# Global field selector instance
_field_selector: Optional[FieldSelector] = None


def get_field_selector(config_manager=None) -> FieldSelector:
    """Get the global field selector instance.

    Args:
        config_manager: Optional config manager for loading/saving preferences

    Returns:
        FieldSelector instance
    """
    global _field_selector
    if _field_selector is None:
        _field_selector = FieldSelector(config_manager)
    # Type assertion: _field_selector is guaranteed not None after initialization
    return cast(FieldSelector, _field_selector)
