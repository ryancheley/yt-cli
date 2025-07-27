"""Tests for CustomFieldManager and custom field utilities."""

from youtrack_cli.custom_field_manager import CustomFieldManager
from youtrack_cli.custom_field_types import (
    FIELD_TYPE_DISPLAY_MAP,
    CustomFieldValueTypes,
    IssueCustomFieldTypes,
    ProjectCustomFieldTypes,
    get_display_name,
)


class TestCustomFieldTypes:
    """Test custom field type constants."""

    def test_issue_custom_field_types(self):
        """Test issue custom field type constants."""
        assert IssueCustomFieldTypes.SINGLE_ENUM == "SingleEnumIssueCustomField"
        assert IssueCustomFieldTypes.MULTI_ENUM == "MultiEnumIssueCustomField"
        assert IssueCustomFieldTypes.STATE == "StateIssueCustomField"
        assert IssueCustomFieldTypes.SINGLE_USER == "SingleUserIssueCustomField"
        assert IssueCustomFieldTypes.MULTI_USER == "MultiUserIssueCustomField"
        assert IssueCustomFieldTypes.TEXT == "TextIssueCustomField"

    def test_project_custom_field_types(self):
        """Test project custom field type constants."""
        assert ProjectCustomFieldTypes.ENUM == "EnumProjectCustomField"
        assert ProjectCustomFieldTypes.MULTI_ENUM == "MultiEnumProjectCustomField"
        assert ProjectCustomFieldTypes.STATE == "StateProjectCustomField"
        assert ProjectCustomFieldTypes.SINGLE_USER == "SingleUserProjectCustomField"
        assert ProjectCustomFieldTypes.MULTI_USER == "MultiUserProjectCustomField"

    def test_custom_field_value_types(self):
        """Test custom field value type constants."""
        assert CustomFieldValueTypes.ENUM_BUNDLE_ELEMENT == "EnumBundleElement"
        assert CustomFieldValueTypes.STATE_BUNDLE_ELEMENT == "StateBundleElement"
        assert CustomFieldValueTypes.USER == "User"
        assert CustomFieldValueTypes.TEXT_VALUE == "TextValue"

    def test_get_display_name(self):
        """Test display name formatting."""
        assert get_display_name("SingleEnumIssueCustomField") == "Single Enum"
        assert get_display_name("MultiUserProjectCustomField") == "Multi User"
        assert get_display_name("UnknownType") == "UnknownType"

    def test_field_type_display_map_completeness(self):
        """Test that all field types have display mappings."""
        # Test some key field types
        assert "SingleEnumIssueCustomField" in FIELD_TYPE_DISPLAY_MAP
        assert "MultiUserProjectCustomField" in FIELD_TYPE_DISPLAY_MAP
        assert FIELD_TYPE_DISPLAY_MAP["SingleEnumIssueCustomField"] == "Single Enum"


class TestCustomFieldManager:
    """Test CustomFieldManager functionality."""

    def test_create_single_enum_field(self):
        """Test creating single enum custom field."""
        field = CustomFieldManager.create_single_enum_field("Priority", "High")

        expected = {
            "$type": "SingleEnumIssueCustomField",
            "name": "Priority",
            "value": {"$type": "EnumBundleElement", "name": "High"},
        }

        assert field == expected

    def test_create_multi_enum_field(self):
        """Test creating multi enum custom field."""
        field = CustomFieldManager.create_multi_enum_field("Tags", ["bug", "urgent"])

        expected = {
            "$type": "MultiEnumIssueCustomField",
            "name": "Tags",
            "value": [{"$type": "EnumBundleElement", "name": "bug"}, {"$type": "EnumBundleElement", "name": "urgent"}],
        }

        assert field == expected

    def test_create_state_field(self):
        """Test creating state custom field."""
        field = CustomFieldManager.create_state_field("State", "Open")

        expected = {
            "$type": "StateIssueCustomField",
            "name": "State",
            "value": {"$type": "StateBundleElement", "name": "Open"},
        }

        assert field == expected

    def test_create_single_user_field(self):
        """Test creating single user custom field."""
        field = CustomFieldManager.create_single_user_field("Assignee", "john.doe")

        expected = {
            "$type": "SingleUserIssueCustomField",
            "name": "Assignee",
            "value": {"$type": "User", "login": "john.doe"},
        }

        assert field == expected

    def test_create_multi_user_field(self):
        """Test creating multi user custom field."""
        field = CustomFieldManager.create_multi_user_field("Reviewers", ["john.doe", "jane.smith"])

        expected = {
            "$type": "MultiUserIssueCustomField",
            "name": "Reviewers",
            "value": [{"$type": "User", "login": "john.doe"}, {"$type": "User", "login": "jane.smith"}],
        }

        assert field == expected

    def test_create_text_field(self):
        """Test creating text custom field."""
        field = CustomFieldManager.create_text_field("Description", "Test description")

        expected = {
            "$type": "TextIssueCustomField",
            "name": "Description",
            "value": {"$type": "TextValue", "text": "Test description"},
        }

        assert field == expected

    def test_extract_field_value_simple(self):
        """Test extracting simple field value."""
        custom_fields = [{"name": "Priority", "value": {"name": "High"}}]

        result = CustomFieldManager.extract_field_value(custom_fields, "Priority")
        assert result == "High"

    def test_extract_field_value_user(self):
        """Test extracting user field value."""
        custom_fields = [{"name": "Assignee", "value": {"login": "john.doe", "fullName": "John Doe"}}]

        result = CustomFieldManager.extract_field_value(custom_fields, "Assignee")
        assert result == "John Doe"  # fullName takes precedence according to priority order

    def test_extract_field_value_multi_value(self):
        """Test extracting multi-value field."""
        custom_fields = [{"name": "Tags", "value": [{"name": "bug"}, {"name": "urgent"}]}]

        result = CustomFieldManager.extract_field_value(custom_fields, "Tags")
        assert result == "bug, urgent"

    def test_extract_field_value_not_found(self):
        """Test extracting non-existent field."""
        custom_fields = [{"name": "Priority", "value": {"name": "High"}}]

        result = CustomFieldManager.extract_field_value(custom_fields, "NonExistent")
        assert result is None

    def test_extract_field_value_empty_list(self):
        """Test extracting from empty custom fields list."""
        result = CustomFieldManager.extract_field_value([], "Priority")
        assert result is None

    def test_extract_field_value_none_input(self):
        """Test extracting from None input."""
        result = CustomFieldManager.extract_field_value(None, "Priority")  # type: ignore
        assert result is None

    def test_get_field_id(self):
        """Test getting field ID."""
        custom_fields = [
            {"id": "field-123", "name": "Priority", "value": {"name": "High"}},
            {"id": "field-456", "name": "Assignee", "value": {"login": "john.doe"}},
        ]

        result = CustomFieldManager.get_field_id(custom_fields, "Priority")
        assert result == "field-123"

        result = CustomFieldManager.get_field_id(custom_fields, "Assignee")
        assert result == "field-456"

        result = CustomFieldManager.get_field_id(custom_fields, "NonExistent")
        assert result is None

    def test_format_field_type_for_display(self):
        """Test field type display formatting."""
        result = CustomFieldManager.format_field_type_for_display("SingleEnumIssueCustomField")
        assert result == "Single Enum"

        result = CustomFieldManager.format_field_type_for_display("UnknownType")
        assert result == "UnknownType"

    def test_get_field_with_fallback_primary_field(self):
        """Test getting field with fallback - primary field exists."""
        issue = {"priority": {"name": "High"}, "customFields": [{"name": "Priority", "value": {"name": "Medium"}}]}

        result = CustomFieldManager.get_field_with_fallback(issue, "priority", "Priority")
        assert result == {"name": "High"}

    def test_get_field_with_fallback_custom_field(self):
        """Test getting field with fallback - fallback to custom field."""
        issue = {"customFields": [{"name": "Priority", "value": {"name": "High"}}]}

        result = CustomFieldManager.get_field_with_fallback(issue, "priority", "Priority")
        assert result == "High"

    def test_get_field_with_fallback_none(self):
        """Test getting field with fallback - no field found."""
        issue = {"customFields": []}

        result = CustomFieldManager.get_field_with_fallback(issue, "priority", "Priority")
        assert result is None

    def test_create_project_enum_field_config(self):
        """Test creating project enum field configuration."""
        config = CustomFieldManager.create_project_enum_field_config(
            field_type="EnumProjectCustomField", can_be_empty=False, empty_field_text="Required field", is_public=True
        )

        expected = {
            "$type": "EnumProjectCustomField",
            "canBeEmpty": False,
            "emptyFieldText": "Required field",
            "isPublic": True,
        }

        assert config == expected

    def test_create_project_enum_field_config_defaults(self):
        """Test creating project enum field configuration with defaults."""
        config = CustomFieldManager.create_project_enum_field_config("EnumProjectCustomField")

        expected = {
            "$type": "EnumProjectCustomField",
            "canBeEmpty": True,
            "emptyFieldText": "No value",
            "isPublic": True,
        }

        assert config == expected

    def test_extract_user_field_info(self):
        """Test extracting comprehensive user information."""
        user_value = {
            "login": "john.doe",
            "fullName": "John Doe",
            "name": "John",
            "email": "john@example.com",
            "avatarUrl": "https://example.com/avatar.jpg",
        }

        result = CustomFieldManager.extract_user_field_info(user_value)

        expected = {
            "login": "john.doe",
            "fullName": "John Doe",
            "name": "John",
            "email": "john@example.com",
            "avatarUrl": "https://example.com/avatar.jpg",
        }

        assert result == expected

    def test_extract_user_field_info_empty(self):
        """Test extracting user info from empty dict."""
        result = CustomFieldManager.extract_user_field_info({})

        expected = {"login": "", "fullName": "", "name": "", "email": "", "avatarUrl": ""}

        assert result == expected

    def test_extract_user_field_info_non_dict(self):
        """Test extracting user info from non-dict input."""
        result = CustomFieldManager.extract_user_field_info("not_a_dict")  # type: ignore
        assert result == {}

    def test_is_multi_value_field(self):
        """Test checking if field type is multi-value."""
        assert CustomFieldManager.is_multi_value_field("MultiEnumIssueCustomField") is True
        assert CustomFieldManager.is_multi_value_field("MultiUserIssueCustomField") is True
        assert CustomFieldManager.is_multi_value_field("MultiEnumProjectCustomField") is True
        assert CustomFieldManager.is_multi_value_field("MultiUserProjectCustomField") is True

        assert CustomFieldManager.is_multi_value_field("SingleEnumIssueCustomField") is False
        assert CustomFieldManager.is_multi_value_field("SingleUserIssueCustomField") is False
        assert CustomFieldManager.is_multi_value_field("StateIssueCustomField") is False

    def test_extract_dict_value_priority_order(self):
        """Test that _extract_dict_value follows priority order."""
        # Test presentation has highest priority
        value = {"presentation": "Presentation Value", "fullName": "Full Name", "name": "Name"}
        result = CustomFieldManager._extract_dict_value(value)
        assert result == "Presentation Value"

        # Test fullName has second priority when presentation is not present
        value = {"fullName": "Full Name", "name": "Name"}
        result = CustomFieldManager._extract_dict_value(value)
        assert result == "Full Name"

        # Test name as fallback
        value = {"name": "Name"}
        result = CustomFieldManager._extract_dict_value(value)
        assert result == "Name"

    def test_extract_dict_value_list_input(self):
        """Test _extract_dict_value with list input."""
        value = [{"name": "Item 1"}, {"name": "Item 2"}]
        result = CustomFieldManager._extract_dict_value(value)
        assert result == "Item 1, Item 2"

    def test_extract_dict_value_primitive_input(self):
        """Test _extract_dict_value with primitive input."""
        assert CustomFieldManager._extract_dict_value("string") == "string"
        assert CustomFieldManager._extract_dict_value(42) == 42
        assert CustomFieldManager._extract_dict_value(True) is True

    def test_extract_dict_value_color_field(self):
        """Test _extract_dict_value with color field."""
        value = {"color": {"id": "color-123"}}
        result = CustomFieldManager._extract_dict_value(value)
        assert result == "color-123"

    def test_extract_dict_value_boolean_field(self):
        """Test _extract_dict_value with boolean field."""
        value = {"isResolved": True}
        result = CustomFieldManager._extract_dict_value(value)
        assert result == "True"
