"""Tests for theme management functionality."""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from rich.theme import Theme

from youtrack_cli.themes import ThemeManager


@pytest.fixture
def temp_themes_dir():
    """Create a temporary directory for theme testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def theme_manager(temp_themes_dir):
    """Create a ThemeManager instance with a temporary directory."""
    return ThemeManager(temp_themes_dir)


@pytest.fixture
def sample_theme_data():
    """Sample theme data for testing."""
    return {
        "name": "test-theme",
        "description": "A test theme",
        "colors": {"info": "cyan", "warning": "yellow", "error": "red", "success": "green"},
    }


class TestThemeManager:
    """Test cases for ThemeManager class."""

    def test_init_creates_themes_directory(self, temp_themes_dir):
        """Test that ThemeManager creates the themes directory."""
        themes_dir = Path(temp_themes_dir) / "custom"
        assert not themes_dir.exists()

        ThemeManager(str(themes_dir))
        assert themes_dir.exists()

    def test_list_all_themes_includes_builtin(self, theme_manager):
        """Test that list_all_themes includes built-in themes."""
        themes = theme_manager.list_all_themes()

        assert "default" in themes
        assert "dark" in themes
        assert "light" in themes
        assert themes["default"] == "built-in"
        assert themes["dark"] == "built-in"
        assert themes["light"] == "built-in"

    def test_list_all_themes_includes_custom(self, theme_manager, sample_theme_data):
        """Test that list_all_themes includes custom themes."""
        # Save a custom theme
        theme_manager.save_custom_theme("test-theme", sample_theme_data)

        themes = theme_manager.list_all_themes()
        assert "test-theme" in themes
        assert themes["test-theme"] == "custom"

    def test_save_custom_theme_success(self, theme_manager, sample_theme_data):
        """Test successfully saving a custom theme."""
        result = theme_manager.save_custom_theme("test-theme", sample_theme_data)
        assert result is True

        # Verify file was created
        theme_file = Path(theme_manager.themes_dir) / "test-theme.json"
        assert theme_file.exists()

        # Verify content
        with open(theme_file) as f:
            saved_data = json.load(f)
        assert saved_data == sample_theme_data

    def test_save_custom_theme_cannot_override_builtin(self, theme_manager, sample_theme_data):
        """Test that built-in themes cannot be overridden."""
        result = theme_manager.save_custom_theme("default", sample_theme_data)
        assert result is False

    def test_save_custom_theme_invalid_data(self, theme_manager):
        """Test saving invalid theme data."""
        invalid_data = {"invalid": "data"}
        result = theme_manager.save_custom_theme("invalid-theme", invalid_data)
        assert result is False

    def test_get_custom_theme_success(self, theme_manager, sample_theme_data):
        """Test successfully loading a custom theme."""
        theme_manager.save_custom_theme("test-theme", sample_theme_data)

        theme = theme_manager.get_custom_theme("test-theme")
        assert isinstance(theme, Theme)
        assert "info" in theme.styles
        assert "warning" in theme.styles

    def test_get_custom_theme_not_found(self, theme_manager):
        """Test loading a non-existent theme."""
        theme = theme_manager.get_custom_theme("nonexistent")
        assert theme is None

    def test_get_custom_theme_invalid_json(self, theme_manager):
        """Test loading a theme with invalid JSON."""
        theme_file = Path(theme_manager.themes_dir) / "invalid.json"
        theme_file.write_text("invalid json {")

        theme = theme_manager.get_custom_theme("invalid")
        assert theme is None

    def test_delete_custom_theme_success(self, theme_manager, sample_theme_data):
        """Test successfully deleting a custom theme."""
        theme_manager.save_custom_theme("test-theme", sample_theme_data)

        result = theme_manager.delete_custom_theme("test-theme")
        assert result is True

        # Verify file was deleted
        theme_file = Path(theme_manager.themes_dir) / "test-theme.json"
        assert not theme_file.exists()

    def test_delete_custom_theme_cannot_delete_builtin(self, theme_manager):
        """Test that built-in themes cannot be deleted."""
        result = theme_manager.delete_custom_theme("default")
        assert result is False

    def test_delete_custom_theme_not_found(self, theme_manager):
        """Test deleting a non-existent theme."""
        result = theme_manager.delete_custom_theme("nonexistent")
        assert result is False

    def test_export_theme_builtin(self, theme_manager, temp_themes_dir):
        """Test exporting a built-in theme."""
        output_file = Path(temp_themes_dir) / "exported.json"

        result = theme_manager.export_theme("default", str(output_file))
        assert result is True
        assert output_file.exists()

        # Verify exported content
        with open(output_file) as f:
            exported_data = json.load(f)
        assert exported_data["name"] == "default"
        assert "colors" in exported_data

    def test_export_theme_custom(self, theme_manager, sample_theme_data, temp_themes_dir):
        """Test exporting a custom theme."""
        theme_manager.save_custom_theme("test-theme", sample_theme_data)
        output_file = Path(temp_themes_dir) / "exported.json"

        result = theme_manager.export_theme("test-theme", str(output_file))
        assert result is True
        assert output_file.exists()

        # Verify exported content
        with open(output_file) as f:
            exported_data = json.load(f)
        assert exported_data == sample_theme_data

    def test_export_theme_not_found(self, theme_manager, temp_themes_dir):
        """Test exporting a non-existent theme."""
        output_file = Path(temp_themes_dir) / "exported.json"

        result = theme_manager.export_theme("nonexistent", str(output_file))
        assert result is False
        assert not output_file.exists()

    def test_import_theme_success(self, theme_manager, sample_theme_data, temp_themes_dir):
        """Test successfully importing a theme."""
        # Create theme file to import
        import_file = Path(temp_themes_dir) / "import.json"
        with open(import_file, "w") as f:
            json.dump(sample_theme_data, f)

        result = theme_manager.import_theme(str(import_file))
        assert result == "test-theme"

        # Verify theme was imported
        themes = theme_manager.list_all_themes()
        assert "test-theme" in themes
        assert themes["test-theme"] == "custom"

    def test_import_theme_with_custom_name(self, theme_manager, sample_theme_data, temp_themes_dir):
        """Test importing a theme with a custom name."""
        # Create theme file to import
        import_file = Path(temp_themes_dir) / "import.json"
        with open(import_file, "w") as f:
            json.dump(sample_theme_data, f)

        result = theme_manager.import_theme(str(import_file), "custom-name")
        assert result == "custom-name"

        # Verify theme was imported with custom name
        themes = theme_manager.list_all_themes()
        assert "custom-name" in themes

    def test_import_theme_file_not_found(self, theme_manager):
        """Test importing from a non-existent file."""
        result = theme_manager.import_theme("nonexistent.json")
        assert result is None

    def test_import_theme_invalid_json(self, theme_manager, temp_themes_dir):
        """Test importing a file with invalid JSON."""
        import_file = Path(temp_themes_dir) / "invalid.json"
        import_file.write_text("invalid json {")

        result = theme_manager.import_theme(str(import_file))
        assert result is None

    def test_import_theme_cannot_override_builtin(self, theme_manager, temp_themes_dir):
        """Test that importing cannot override built-in themes."""
        theme_data = {
            "name": "default",  # Try to override built-in theme
            "colors": {"info": "red"},
        }

        import_file = Path(temp_themes_dir) / "override.json"
        with open(import_file, "w") as f:
            json.dump(theme_data, f)

        result = theme_manager.import_theme(str(import_file))
        assert result is None

    @patch("youtrack_cli.themes.get_console")
    @patch("youtrack_cli.themes.Prompt.ask")
    @patch("youtrack_cli.themes.Confirm.ask")
    def test_create_theme_interactively_basic(self, mock_confirm, mock_prompt, mock_console, theme_manager):
        """Test basic interactive theme creation."""
        mock_console.return_value = MagicMock()

        # Mock the prompts - use a function to handle variable number of calls
        def mock_prompt_side_effect(*args, **kwargs):
            # Return appropriate values based on the prompt
            prompt_text = args[0] if args else ""
            if "info" in prompt_text:
                return "blue"
            elif "warning" in prompt_text:
                return "orange"
            elif "error" in prompt_text:
                return "red"
            elif "success" in prompt_text:
                return "green"
            elif "header" in prompt_text:
                return "white"
            elif "link" in prompt_text:
                return "blue"
            elif "highlight" in prompt_text:
                return "yellow"
            elif "description" in prompt_text:
                return "My custom theme"
            else:
                return ""  # Return empty for any other prompts

        mock_prompt.side_effect = mock_prompt_side_effect
        mock_confirm.ask.return_value = False  # Don't customize additional colors

        result = theme_manager.create_theme_interactively("my-theme")
        assert result is True

        # Verify theme was created
        themes = theme_manager.list_all_themes()
        assert "my-theme" in themes

    @patch("youtrack_cli.themes.get_console")
    def test_create_theme_interactively_existing_theme(self, mock_console, theme_manager, sample_theme_data):
        """Test interactive creation when theme already exists."""
        mock_console.return_value = MagicMock()
        theme_manager.save_custom_theme("existing", sample_theme_data)

        with patch("youtrack_cli.themes.Confirm.ask", return_value=False):
            result = theme_manager.create_theme_interactively("existing")
            assert result is False

    @patch("youtrack_cli.themes.get_console")
    def test_create_theme_interactively_cannot_override_builtin(self, mock_console, theme_manager):
        """Test that interactive creation cannot override built-in themes."""
        mock_console_instance = MagicMock()
        mock_console.return_value = mock_console_instance

        result = theme_manager.create_theme_interactively("default")
        assert result is False
        mock_console_instance.print.assert_called_with("❌ Cannot override built-in theme 'default'", style="error")

    def test_validate_theme_data_valid(self, theme_manager, sample_theme_data):
        """Test validation of valid theme data."""
        assert theme_manager._validate_theme_data(sample_theme_data) is True

    def test_validate_theme_data_missing_colors(self, theme_manager):
        """Test validation fails when colors section is missing."""
        invalid_data = {"name": "test"}
        assert theme_manager._validate_theme_data(invalid_data) is False

    def test_validate_theme_data_invalid_structure(self, theme_manager):
        """Test validation fails for invalid data structure."""
        assert theme_manager._validate_theme_data("not a dict") is False
        assert theme_manager._validate_theme_data({"colors": "not a dict"}) is False

    def test_validate_theme_data_invalid_color_values(self, theme_manager):
        """Test validation handles invalid color values."""
        invalid_data = {
            "colors": {
                "info": 123  # Invalid color value
            }
        }
        assert theme_manager._validate_theme_data(invalid_data) is False

    @patch("youtrack_cli.themes.get_console")
    def test_display_themes_table(self, mock_console, theme_manager, sample_theme_data):
        """Test displaying themes table."""
        mock_console_instance = MagicMock()
        mock_console.return_value = mock_console_instance

        theme_manager.save_custom_theme("test-theme", sample_theme_data)
        theme_manager.display_themes_table()

        # Verify console.print was called with a table
        mock_console_instance.print.assert_called()

    @patch("youtrack_cli.themes.get_console")
    def test_display_themes_table_no_themes(self, mock_console, temp_themes_dir):
        """Test displaying themes table when no themes exist."""
        mock_console_instance = MagicMock()
        mock_console.return_value = mock_console_instance

        # Create theme manager with empty built-in themes
        with patch("youtrack_cli.themes.THEMES", {}):
            theme_manager = ThemeManager(temp_themes_dir)
            theme_manager.display_themes_table()

        mock_console_instance.print.assert_called_with("No themes available", style="warning")


class TestThemeIntegration:
    """Integration tests for theme functionality."""

    def test_custom_theme_roundtrip(self, theme_manager, sample_theme_data, temp_themes_dir):
        """Test complete workflow: save -> load -> export -> import."""
        # Save custom theme
        assert theme_manager.save_custom_theme("roundtrip", sample_theme_data) is True

        # Load custom theme
        theme = theme_manager.get_custom_theme("roundtrip")
        assert theme is not None
        assert "info" in theme.styles

        # Export theme
        export_file = Path(temp_themes_dir) / "exported.json"
        assert theme_manager.export_theme("roundtrip", str(export_file)) is True

        # Delete original theme
        assert theme_manager.delete_custom_theme("roundtrip") is True

        # Import theme back
        imported_name = theme_manager.import_theme(str(export_file), "imported")
        assert imported_name == "imported"

        # Verify imported theme works
        imported_theme = theme_manager.get_custom_theme("imported")
        assert imported_theme is not None
        assert "info" in imported_theme.styles
