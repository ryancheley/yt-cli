"""Tests for console management module."""

from rich.console import Console
from rich.theme import Theme

from youtrack_cli.console import (
    THEMES,
    ConsoleManager,
    get_available_themes,
    get_console,
    get_console_theme,
    get_default_theme,
    get_theme_by_name,
    reset_console_theme,
    set_console_theme,
    set_theme_by_name,
)


class TestThemes:
    """Test theme-related functionality."""

    def test_default_theme_exists(self):
        """Test that default theme is available."""
        theme = get_default_theme()
        assert isinstance(theme, Theme)
        assert "info" in theme.styles
        assert "error" in theme.styles
        assert "success" in theme.styles

    def test_get_theme_by_name_valid(self):
        """Test getting a theme by valid name."""
        theme = get_theme_by_name("default")
        assert isinstance(theme, Theme)
        assert theme == THEMES["default"]

    def test_get_theme_by_name_invalid(self):
        """Test getting a theme by invalid name."""
        theme = get_theme_by_name("nonexistent")
        assert theme is None

    def test_available_themes(self):
        """Test getting list of available themes."""
        themes = get_available_themes()
        assert isinstance(themes, list)
        assert "default" in themes
        assert "dark" in themes
        assert "light" in themes
        assert len(themes) >= 3

    def test_themes_structure(self):
        """Test that all themes have the required structure."""
        required_styles = [
            "info",
            "warning",
            "danger",
            "success",
            "error",
            "prompt",
            "field",
            "value",
            "highlight",
            "link",
            "header",
            "title",
            "subtitle",
            "muted",
        ]

        for theme_name, theme in THEMES.items():
            assert isinstance(theme, Theme)
            for style in required_styles:
                assert style in theme.styles, f"Style '{style}' missing from theme '{theme_name}'"


class TestConsoleManager:
    """Test ConsoleManager functionality."""

    def setup_method(self):
        """Reset console manager for each test."""
        # Clear singleton instance
        ConsoleManager._instance = None
        ConsoleManager._console = None
        ConsoleManager._theme = None

    def test_singleton_pattern(self):
        """Test that ConsoleManager follows singleton pattern."""
        manager1 = ConsoleManager()
        manager2 = ConsoleManager()
        assert manager1 is manager2

    def test_console_property(self):
        """Test console property returns a Console instance."""
        manager = ConsoleManager()
        console = manager.console
        assert isinstance(console, Console)

    def test_default_theme_initialization(self):
        """Test that manager initializes with default theme."""
        manager = ConsoleManager()
        theme = manager.get_theme()
        assert isinstance(theme, Theme)
        assert theme == get_default_theme()

    def test_custom_theme_initialization(self):
        """Test manager initialization with custom theme."""
        custom_theme = Theme({"info": "red"})
        # Clear singleton to test custom theme initialization
        ConsoleManager._instance = None
        ConsoleManager._console = None
        ConsoleManager._theme = None
        manager = ConsoleManager()
        manager.set_theme(custom_theme)
        assert manager.get_theme() == custom_theme

    def test_set_theme(self):
        """Test setting a new theme."""
        manager = ConsoleManager()
        new_theme = Theme({"info": "green"})
        manager.set_theme(new_theme)
        assert manager.get_theme() == new_theme

    def test_reset_theme(self):
        """Test resetting theme to default."""
        manager = ConsoleManager()
        custom_theme = Theme({"info": "purple"})
        manager.set_theme(custom_theme)
        manager.reset_theme()
        assert manager.get_theme() == get_default_theme()


class TestGlobalFunctions:
    """Test global console functions."""

    def setup_method(self):
        """Reset console manager for each test."""
        # Clear singleton instance
        ConsoleManager._instance = None
        ConsoleManager._console = None
        ConsoleManager._theme = None

    def test_get_console(self):
        """Test getting global console instance."""
        console = get_console()
        assert isinstance(console, Console)

    def test_get_console_consistency(self):
        """Test that get_console returns the same instance."""
        console1 = get_console()
        console2 = get_console()
        assert console1 is console2

    def test_set_console_theme(self):
        """Test setting global console theme."""
        custom_theme = Theme({"info": "blue"})
        set_console_theme(custom_theme)
        assert get_console_theme() == custom_theme

    def test_reset_console_theme(self):
        """Test resetting global console theme."""
        custom_theme = Theme({"info": "yellow"})
        set_console_theme(custom_theme)
        reset_console_theme()
        assert get_console_theme() == get_default_theme()

    def test_set_theme_by_name_valid(self):
        """Test setting theme by valid name."""
        result = set_theme_by_name("dark")
        assert result is True
        assert get_console_theme() == THEMES["dark"]

    def test_set_theme_by_name_invalid(self):
        """Test setting theme by invalid name."""
        result = set_theme_by_name("nonexistent")
        assert result is False
        # Theme should remain unchanged


class TestConfigIntegration:
    """Test integration with configuration system."""

    def setup_method(self):
        """Reset console manager for each test."""
        # Clear singleton instance
        ConsoleManager._instance = None
        ConsoleManager._console = None
        ConsoleManager._theme = None

    def test_theme_from_config(self, monkeypatch):
        """Test loading theme from configuration."""

        class MockConfig:
            def get_config(self, key):
                return "dark" if key == "YOUTRACK_THEME" else None

        monkeypatch.setattr("youtrack_cli.console.ConfigManager", MockConfig)

        manager = ConsoleManager()
        theme = manager.get_theme()

        assert theme == THEMES["dark"]

    def test_config_theme_not_found(self, monkeypatch):
        """Test fallback when configured theme doesn't exist."""

        class MockConfig:
            def get_config(self, key):
                return "nonexistent" if key == "YOUTRACK_THEME" else None

        monkeypatch.setattr("youtrack_cli.console.ConfigManager", MockConfig)

        manager = ConsoleManager()
        theme = manager.get_theme()

        assert theme == get_default_theme()

    def test_no_theme_config(self, monkeypatch):
        """Test fallback when no theme is configured."""

        class MockConfig:
            def get_config(self, key):
                return None

        monkeypatch.setattr("youtrack_cli.console.ConfigManager", MockConfig)

        manager = ConsoleManager()
        theme = manager.get_theme()

        assert theme == get_default_theme()


class TestThemeContent:
    """Test theme content and styling."""

    def test_default_theme_styles(self):
        """Test default theme has correct styles."""
        theme = THEMES["default"]
        assert str(theme.styles["info"]) == "cyan"
        assert str(theme.styles["error"]) == "bold red"
        assert str(theme.styles["success"]) == "bold green"

    def test_dark_theme_styles(self):
        """Test dark theme has correct styles."""
        theme = THEMES["dark"]
        assert "bright_cyan" in str(theme.styles["info"])
        assert "bright_green" in str(theme.styles["success"])

    def test_light_theme_styles(self):
        """Test light theme has correct styles."""
        theme = THEMES["light"]
        assert str(theme.styles["value"]) == "black"
        assert str(theme.styles["title"]) == "bold black"

    def test_all_themes_have_same_keys(self):
        """Test that all themes have the same style keys."""
        default_keys = set(THEMES["default"].styles.keys())

        for theme_name, theme in THEMES.items():
            theme_keys = set(theme.styles.keys())
            assert theme_keys == default_keys, f"Theme '{theme_name}' has different keys than default"
