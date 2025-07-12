"""Centralized console management for YouTrack CLI."""

from typing import Dict, Optional

from rich.console import Console
from rich.theme import Theme

from .config import ConfigManager

THEMES: Dict[str, Theme] = {
    "default": Theme(
        {
            "info": "cyan",
            "warning": "yellow",
            "danger": "bold red",
            "success": "bold green",
            "error": "bold red",
            "prompt": "bold cyan",
            "field": "bold magenta",
            "value": "white",
            "highlight": "bold yellow",
            "link": "blue underline",
            "header": "bold cyan",
            "title": "bold white",
            "subtitle": "dim white",
            "muted": "dim white",
            "progress.description": "cyan",
            "progress.percentage": "bold cyan",
            "progress.elapsed": "yellow",
            "table.header": "bold cyan",
            "table.row": "white",
            "table.row.odd": "bright_black",
            "panel.border": "cyan",
            "panel.title": "bold cyan",
            "panel.subtitle": "dim cyan",
        }
    ),
    "dark": Theme(
        {
            "info": "bright_cyan",
            "warning": "bright_yellow",
            "danger": "bold bright_red",
            "success": "bold bright_green",
            "error": "bold bright_red",
            "prompt": "bold bright_blue",
            "field": "bold bright_magenta",
            "value": "bright_white",
            "highlight": "bold bright_yellow",
            "link": "bright_blue underline",
            "header": "bold bright_cyan",
            "title": "bold bright_white",
            "subtitle": "bright_black",
            "muted": "bright_black",
            "progress.description": "bright_cyan",
            "progress.percentage": "bold bright_cyan",
            "progress.elapsed": "bright_yellow",
            "table.header": "bold bright_cyan",
            "table.row": "bright_white",
            "table.row.odd": "white",
            "panel.border": "bright_cyan",
            "panel.title": "bold bright_cyan",
            "panel.subtitle": "bright_black",
        }
    ),
    "light": Theme(
        {
            "info": "blue",
            "warning": "yellow",
            "danger": "bold red",
            "success": "bold green",
            "error": "bold red",
            "prompt": "bold blue",
            "field": "bold magenta",
            "value": "black",
            "highlight": "bold yellow",
            "link": "blue underline",
            "header": "bold blue",
            "title": "bold black",
            "subtitle": "bright_black",
            "muted": "bright_black",
            "progress.description": "blue",
            "progress.percentage": "bold blue",
            "progress.elapsed": "yellow",
            "table.header": "bold blue",
            "table.row": "black",
            "table.row.odd": "bright_black",
            "panel.border": "blue",
            "panel.title": "bold blue",
            "panel.subtitle": "bright_black",
        }
    ),
}


def get_default_theme() -> Theme:
    """Get the default theme for the YouTrack CLI.

    Returns:
        Theme: A Rich Theme object with YouTrack CLI styling
    """
    return THEMES["default"]


def get_theme_by_name(name: str) -> Optional[Theme]:
    """Get a theme by its name.

    Args:
        name: The name of the theme (default, dark, light)

    Returns:
        Optional[Theme]: The theme if found, None otherwise
    """
    return THEMES.get(name)


class ConsoleManager:
    """Manages console instances and theming for YouTrack CLI."""

    _instance: Optional["ConsoleManager"] = None
    _console: Optional[Console] = None
    _theme: Optional[Theme] = None

    def __new__(cls) -> "ConsoleManager":
        """Create a singleton instance of ConsoleManager."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, theme: Optional[Theme] = None) -> None:
        """Initialize the ConsoleManager.

        Args:
            theme: Optional custom theme. If not provided, loads from config or uses default.
        """
        if self._console is None:
            if theme:
                self._theme = theme
            else:
                # Try to load theme from config
                config = ConfigManager()
                theme_name = config.get_config("YOUTRACK_THEME")
                if theme_name and (configured_theme := get_theme_by_name(theme_name)):
                    self._theme = configured_theme
                else:
                    self._theme = get_default_theme()
            self._console = Console(theme=self._theme)

    @property
    def console(self) -> Console:
        """Get the console instance.

        Returns:
            Console: The configured Rich console instance
        """
        if self._console is None:
            self._theme = get_default_theme()
            self._console = Console(theme=self._theme)
        return self._console

    def set_theme(self, theme: Theme) -> None:
        """Set a new theme for the console.

        Args:
            theme: The new Rich Theme to apply
        """
        self._theme = theme
        self._console = Console(theme=self._theme)

    def reset_theme(self) -> None:
        """Reset the console theme to the default."""
        self.set_theme(get_default_theme())

    def get_theme(self) -> Optional[Theme]:
        """Get the current theme.

        Returns:
            Optional[Theme]: The current theme or None if not set
        """
        return self._theme


# Global console manager instance
_console_manager = ConsoleManager()


def get_console() -> Console:
    """Get the global console instance.

    Returns:
        Console: The configured Rich console instance
    """
    return _console_manager.console


def set_console_theme(theme: Theme) -> None:
    """Set a new theme for the global console.

    Args:
        theme: The new Rich Theme to apply
    """
    _console_manager.set_theme(theme)


def reset_console_theme() -> None:
    """Reset the global console theme to the default."""
    _console_manager.reset_theme()


def get_console_theme() -> Optional[Theme]:
    """Get the current console theme.

    Returns:
        Optional[Theme]: The current theme or None if not set
    """
    return _console_manager.get_theme()


def get_available_themes() -> list[str]:
    """Get a list of available theme names.

    Returns:
        list[str]: List of available theme names
    """
    return list(THEMES.keys())


def set_theme_by_name(name: str) -> bool:
    """Set the console theme by name.

    Args:
        name: The name of the theme to set

    Returns:
        bool: True if theme was set successfully, False if theme not found
    """
    theme = get_theme_by_name(name)
    if theme:
        set_console_theme(theme)
        return True
    return False
