"""Tests for field selection optimization functionality."""

from unittest.mock import Mock, patch

from youtrack_cli.field_selection import (
    FIELD_PROFILES,
    FieldProfile,
    FieldSelector,
    get_field_selector,
)


class TestFieldProfile:
    """Test field profile functionality."""

    def test_field_profile_creation(self):
        """Test creating a field profile."""
        fields = ["id", "summary", "state(name)"]
        profile = FieldProfile("issues", "minimal", fields)

        assert profile.entity_type == "issues"
        assert profile.profile_name == "minimal"
        assert profile.fields == fields

    def test_get_fields_string(self):
        """Test getting fields as string."""
        fields = ["id", "summary", "state(name,id)"]
        profile = FieldProfile("issues", "minimal", fields)

        result = profile.get_fields_string()
        assert result == "id,summary,state(name,id)"

    def test_get_fields_list(self):
        """Test getting fields as list."""
        fields = ["id", "summary", "state(name)"]
        profile = FieldProfile("issues", "minimal", fields)

        result = profile.get_fields_list()
        assert result == fields
        assert result is not fields  # Should be a copy

    def test_string_representation(self):
        """Test string representation."""
        profile = FieldProfile("issues", "minimal", ["id", "summary"])
        assert str(profile) == "issues:minimal"


class TestFieldSelector:
    """Test field selector functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.selector = FieldSelector()

    def test_initialization(self):
        """Test field selector initialization."""
        assert self.selector._profiles == FIELD_PROFILES
        assert "issues" in self.selector._default_profiles
        assert self.selector._default_profiles["issues"] == "standard"

    def test_get_profile_valid(self):
        """Test getting a valid profile."""
        profile = self.selector.get_profile("issues", "minimal")

        assert profile is not None
        assert profile.entity_type == "issues"
        assert profile.profile_name == "minimal"
        assert "id" in profile.fields

    def test_get_profile_invalid_entity(self):
        """Test getting profile for invalid entity type."""
        profile = self.selector.get_profile("invalid", "minimal")
        assert profile is None

    def test_get_profile_invalid_profile(self):
        """Test getting invalid profile name."""
        profile = self.selector.get_profile("issues", "invalid")
        assert profile is None

    def test_get_fields_default_profile(self):
        """Test getting fields with default profile."""
        fields = self.selector.get_fields("issues")

        # Should use standard profile by default
        assert "id" in fields
        assert "summary" in fields
        assert "description" in fields

    def test_get_fields_minimal_profile(self):
        """Test getting fields with minimal profile."""
        fields = self.selector.get_fields("issues", "minimal")

        assert "id" in fields
        assert "summary" in fields
        # Minimal profile should not include description
        assert "description" not in fields

    def test_get_fields_full_profile(self):
        """Test getting fields with full profile."""
        fields = self.selector.get_fields("issues", "full")

        assert "id" in fields
        assert "summary" in fields
        assert "description" in fields
        assert "customFields" in fields
        assert "attachments" in fields

    def test_get_fields_custom_fields(self):
        """Test adding custom fields."""
        fields = self.selector.get_fields("issues", "minimal", custom_fields=["priority(name)", "tags(name)"])

        assert "priority(name)" in fields
        assert "tags(name)" in fields
        assert "id" in fields  # Should still include base fields

    def test_get_fields_exclude_fields(self):
        """Test excluding specific fields."""
        fields = self.selector.get_fields("issues", "standard", exclude_fields=["description", "priority(name,id)"])

        assert "description" not in fields
        assert "priority(name,id)" not in fields
        assert "id" in fields  # Should still include essential fields

    def test_get_fields_unknown_entity_fallback(self):
        """Test fallback behavior for unknown entity type."""
        fields = self.selector.get_fields("unknown_entity", "minimal")

        # Should fallback to basic fields
        assert "id" in fields
        assert "summary" in fields

    def test_get_available_profiles(self):
        """Test getting available profiles."""
        profiles = self.selector.get_available_profiles("issues")

        assert "minimal" in profiles
        assert "standard" in profiles
        assert "full" in profiles

    def test_get_supported_entities(self):
        """Test getting supported entities."""
        entities = self.selector.get_supported_entities()

        assert "issues" in entities
        assert "projects" in entities
        assert "users" in entities

    def test_set_default_profile_valid(self):
        """Test setting valid default profile."""
        result = self.selector.set_default_profile("issues", "minimal")

        assert result is True
        assert self.selector._default_profiles["issues"] == "minimal"

    def test_set_default_profile_invalid_entity(self):
        """Test setting default for invalid entity."""
        result = self.selector.set_default_profile("invalid", "minimal")
        assert result is False

    def test_set_default_profile_invalid_profile(self):
        """Test setting invalid default profile."""
        result = self.selector.set_default_profile("issues", "invalid")
        assert result is False

    def test_validate_fields_valid(self):
        """Test field validation with valid fields."""
        fields = "id,summary,state(name,id),assignee(login,fullName)"
        result = self.selector.validate_fields(fields, "issues")
        assert result is True

    def test_validate_fields_unbalanced_parentheses(self):
        """Test field validation with unbalanced parentheses."""
        fields = "id,summary,state(name"
        result = self.selector.validate_fields(fields, "issues")
        assert result is False

    def test_validate_fields_empty(self):
        """Test field validation with empty fields."""
        result = self.selector.validate_fields("", "issues")
        assert result is False

    def test_validate_fields_invalid_characters(self):
        """Test field validation with invalid characters."""
        fields = "id,summary,state(name);DROP TABLE issues"
        result = self.selector.validate_fields(fields, "issues")
        assert result is False


class TestFieldSelectorWithConfig:
    """Test field selector with configuration manager."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_config = Mock()
        self.selector = FieldSelector(self.mock_config)

    def test_load_config_defaults(self):
        """Test loading defaults from configuration."""
        self.mock_config.get_config.side_effect = lambda key: {
            "FIELD_PROFILE_ISSUES": "minimal",
            "FIELD_PROFILE_PROJECTS": "full",
        }.get(key)

        selector = FieldSelector(self.mock_config)

        assert selector._default_profiles["issues"] == "minimal"
        assert selector._default_profiles["projects"] == "full"

    def test_load_config_invalid_profile(self):
        """Test loading invalid profile from config is ignored."""
        self.mock_config.get_config.return_value = "invalid_profile"

        selector = FieldSelector(self.mock_config)

        # Should use default since config value is invalid
        assert selector._default_profiles["issues"] == "standard"

    def test_save_default_to_config_success(self):
        """Test saving default to configuration."""
        result = self.selector.save_default_to_config("issues", "minimal")

        assert result is True
        self.mock_config.set_config.assert_called_with("FIELD_PROFILE_ISSUES", "minimal")

    def test_save_default_to_config_invalid_profile(self):
        """Test saving invalid profile to config fails."""
        result = self.selector.save_default_to_config("issues", "invalid")

        assert result is False
        self.mock_config.set_config.assert_not_called()

    def test_save_default_to_config_error(self):
        """Test handling config save error."""
        self.mock_config.set_config.side_effect = Exception("Config error")

        result = self.selector.save_default_to_config("issues", "minimal")

        assert result is False

    def test_no_config_manager(self):
        """Test behavior without config manager."""
        selector = FieldSelector(None)

        result = selector.save_default_to_config("issues", "minimal")
        assert result is False


class TestGlobalFieldSelector:
    """Test global field selector functions."""

    def test_get_field_selector_singleton(self):
        """Test global field selector is singleton."""
        with patch("youtrack_cli.field_selection._field_selector", None):
            selector1 = get_field_selector()
            selector2 = get_field_selector()

            assert selector1 is selector2

    def test_get_field_selector_with_config(self):
        """Test getting field selector with config manager."""
        mock_config = Mock()

        with patch("youtrack_cli.field_selection._field_selector", None):
            selector = get_field_selector(mock_config)

            assert selector._config_manager is mock_config


class TestFieldProfiles:
    """Test predefined field profiles."""

    def test_all_entities_have_profiles(self):
        """Test all entities have required profiles."""
        required_profiles = ["minimal", "standard", "full"]

        for entity_type, profiles in FIELD_PROFILES.items():
            for profile_name in required_profiles:
                assert profile_name in profiles, f"Missing {profile_name} profile for {entity_type}"

    def test_minimal_profiles_have_id(self):
        """Test minimal profiles always include ID field."""
        for entity_type, profiles in FIELD_PROFILES.items():
            minimal_fields = profiles["minimal"]
            assert "id" in minimal_fields, f"Minimal profile for {entity_type} missing ID field"

    def test_standard_profiles_include_minimal(self):
        """Test standard profiles include minimal fields."""
        for entity_type, profiles in FIELD_PROFILES.items():
            minimal_set = set(profiles["minimal"])
            standard_set = set(profiles["standard"])

            assert minimal_set.issubset(standard_set), (
                f"Standard profile for {entity_type} doesn't include all minimal fields"
            )

    def test_full_profiles_include_standard(self):
        """Test full profiles include standard fields."""
        for entity_type, profiles in FIELD_PROFILES.items():
            standard_set = set(profiles["standard"])
            full_set = set(profiles["full"])

            assert standard_set.issubset(full_set), (
                f"Full profile for {entity_type} doesn't include all standard fields"
            )


class TestFieldSelection:
    """Integration tests for field selection functionality."""

    def test_issues_minimal_profile(self):
        """Test issues minimal profile has essential fields."""
        selector = FieldSelector()
        fields = selector.get_fields("issues", "minimal")

        # Should have basic issue identification
        assert "id" in fields
        assert "numberInProject" in fields
        assert "summary" in fields
        assert "state(name,id)" in fields

    def test_issues_standard_profile(self):
        """Test issues standard profile has common fields."""
        selector = FieldSelector()
        fields = selector.get_fields("issues", "standard")

        # Should include assignee and project info
        assert "assignee(login,fullName,id)" in fields
        assert "project(id,name,shortName)" in fields
        assert "description" in fields

    def test_projects_minimal_vs_full(self):
        """Test projects field profiles have appropriate scope."""
        selector = FieldSelector()

        minimal = selector.get_fields("projects", "minimal")
        full = selector.get_fields("projects", "full")

        # Minimal should be much shorter
        minimal_count = len(minimal.split(","))
        full_count = len(full.split(","))

        assert minimal_count < full_count / 2, "Minimal profile should be significantly smaller"

    def test_custom_fields_addition(self):
        """Test adding custom fields to profile."""
        selector = FieldSelector()

        base_fields = selector.get_fields("issues", "minimal")
        custom_fields = selector.get_fields("issues", "minimal", custom_fields="priority(name),tags(name)")

        # Custom fields should add to the base
        assert "priority(name)" in custom_fields
        assert "tags(name)" in custom_fields
        assert len(custom_fields) > len(base_fields)

    def test_field_exclusion(self):
        """Test excluding fields from profile."""
        selector = FieldSelector()

        full_fields = selector.get_fields("issues", "full")
        excluded_fields = selector.get_fields(
            "issues", "full", exclude_fields=["description", "attachments(name,size,url)"]
        )

        # Excluded fields should not be present
        assert "description" not in excluded_fields
        assert "attachments(name,size,url)" not in excluded_fields
        assert len(excluded_fields) < len(full_fields)
