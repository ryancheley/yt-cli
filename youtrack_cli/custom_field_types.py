"""
Custom field type constants for YouTrack API.

This module defines constants for all YouTrack custom field types to eliminate
hardcoded strings throughout the codebase and provide a centralized reference.
"""


class IssueCustomFieldTypes:
    """Custom field types for issues."""

    SINGLE_ENUM = "SingleEnumIssueCustomField"
    MULTI_ENUM = "MultiEnumIssueCustomField"
    STATE = "StateIssueCustomField"
    SINGLE_USER = "SingleUserIssueCustomField"
    MULTI_USER = "MultiUserIssueCustomField"
    SINGLE_VERSION = "SingleVersionIssueCustomField"
    MULTI_VERSION = "MultiVersionIssueCustomField"
    SINGLE_BUILD = "SingleBuildIssueCustomField"
    MULTI_BUILD = "MultiBuildIssueCustomField"
    SINGLE_OWN_BUILD = "SingleOwnedIssueCustomField"
    MULTI_OWN_BUILD = "MultiOwnedIssueCustomField"
    TEXT = "TextIssueCustomField"
    PERIOD = "PeriodIssueCustomField"
    DATE = "DateIssueCustomField"
    DATE_TIME = "DateTimeIssueCustomField"
    INTEGER = "SimpleIssueCustomField"
    FLOAT = "SimpleIssueCustomField"


class ProjectCustomFieldTypes:
    """Custom field types for projects."""

    ENUM = "EnumProjectCustomField"
    MULTI_ENUM = "MultiEnumProjectCustomField"
    STATE = "StateProjectCustomField"
    SINGLE_USER = "SingleUserProjectCustomField"
    MULTI_USER = "MultiUserProjectCustomField"
    SINGLE_VERSION = "SingleVersionProjectCustomField"
    MULTI_VERSION = "MultiVersionProjectCustomField"
    SINGLE_BUILD = "SingleBuildProjectCustomField"
    MULTI_BUILD = "MultiBuildProjectCustomField"
    SINGLE_OWN_BUILD = "SingleOwnedProjectCustomField"
    MULTI_OWN_BUILD = "MultiOwnedProjectCustomField"
    TEXT = "TextProjectCustomField"
    PERIOD = "PeriodProjectCustomField"
    DATE = "DateProjectCustomField"
    DATE_TIME = "DateTimeProjectCustomField"
    INTEGER = "SimpleProjectCustomField"
    FLOAT = "SimpleProjectCustomField"


class CustomFieldValueTypes:
    """Custom field value types."""

    ENUM_BUNDLE_ELEMENT = "EnumBundleElement"
    STATE_BUNDLE_ELEMENT = "StateBundleElement"
    VERSION_BUNDLE_ELEMENT = "VersionBundleElement"
    BUILD_BUNDLE_ELEMENT = "BuildBundleElement"
    OWN_BUILD_BUNDLE_ELEMENT = "OwnedBundleElement"
    USER = "User"
    PERIOD_VALUE = "PeriodValue"
    DATE_VALUE = "DateValue"
    INTEGER_VALUE = "IntegerValue"
    FLOAT_VALUE = "FloatValue"
    TEXT_VALUE = "TextValue"


class VisibilityTypes:
    """Visibility types for articles and other content."""

    UNLIMITED = "UnlimitedVisibility"
    LIMITED = "LimitedVisibility"


# Mapping for display purposes - converts API types to human-readable names
FIELD_TYPE_DISPLAY_MAP = {
    # Issue field types
    IssueCustomFieldTypes.SINGLE_ENUM: "Single Enum",
    IssueCustomFieldTypes.MULTI_ENUM: "Multi Enum",
    IssueCustomFieldTypes.STATE: "State",
    IssueCustomFieldTypes.SINGLE_USER: "Single User",
    IssueCustomFieldTypes.MULTI_USER: "Multi User",
    IssueCustomFieldTypes.SINGLE_VERSION: "Single Version",
    IssueCustomFieldTypes.MULTI_VERSION: "Multi Version",
    IssueCustomFieldTypes.SINGLE_BUILD: "Single Build",
    IssueCustomFieldTypes.MULTI_BUILD: "Multi Build",
    IssueCustomFieldTypes.SINGLE_OWN_BUILD: "Single Owned Build",
    IssueCustomFieldTypes.MULTI_OWN_BUILD: "Multi Owned Build",
    IssueCustomFieldTypes.TEXT: "Text",
    IssueCustomFieldTypes.PERIOD: "Period",
    IssueCustomFieldTypes.DATE: "Date",
    IssueCustomFieldTypes.DATE_TIME: "Date Time",
    IssueCustomFieldTypes.INTEGER: "Integer",
    IssueCustomFieldTypes.FLOAT: "Float",
    # Project field types
    ProjectCustomFieldTypes.ENUM: "Enum",
    ProjectCustomFieldTypes.MULTI_ENUM: "Multi Enum",
    ProjectCustomFieldTypes.STATE: "State",
    ProjectCustomFieldTypes.SINGLE_USER: "Single User",
    ProjectCustomFieldTypes.MULTI_USER: "Multi User",
    ProjectCustomFieldTypes.SINGLE_VERSION: "Single Version",
    ProjectCustomFieldTypes.MULTI_VERSION: "Multi Version",
    ProjectCustomFieldTypes.SINGLE_BUILD: "Single Build",
    ProjectCustomFieldTypes.MULTI_BUILD: "Multi Build",
    ProjectCustomFieldTypes.SINGLE_OWN_BUILD: "Single Owned Build",
    ProjectCustomFieldTypes.MULTI_OWN_BUILD: "Multi Owned Build",
    ProjectCustomFieldTypes.TEXT: "Text",
    ProjectCustomFieldTypes.PERIOD: "Period",
    ProjectCustomFieldTypes.DATE: "Date",
    ProjectCustomFieldTypes.DATE_TIME: "Date Time",
    ProjectCustomFieldTypes.INTEGER: "Integer",
    ProjectCustomFieldTypes.FLOAT: "Float",
}


def get_display_name(field_type: str) -> str:
    """
    Convert a YouTrack API field type to a human-readable display name.

    Args:
        field_type: The YouTrack API field type string

    Returns:
        Human-readable display name for the field type
    """
    return FIELD_TYPE_DISPLAY_MAP.get(field_type, field_type)
