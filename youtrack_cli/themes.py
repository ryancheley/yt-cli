"""Theme management utilities for YouTrack CLI."""

import json
from pathlib import Path
from typing import Dict, Optional

from rich.prompt import Confirm, Prompt
from rich.table import Table
from rich.theme import Theme

from .console import THEMES, get_console


class ThemeManager:
    """Manages custom themes for YouTrack CLI."""

    def __init__(self, themes_dir: Optional[str] = None):
        """Initialize the theme manager.

        Args:
            themes_dir: Custom themes directory. If None, uses default location.
        """
        self.themes_dir = Path(themes_dir or self._get_default_themes_dir())
        self.themes_dir.mkdir(parents=True, exist_ok=True)

    def _get_default_themes_dir(self) -> str:
        """Get the default themes directory path."""
        return str(Path.home() / ".config" / "youtrack-cli" / "themes")

    def _get_theme_file_path(self, name: str) -> Path:
        """Get the file path for a theme.

        Args:
            name: Theme name

        Returns:
            Path to the theme file
        """
        return self.themes_dir / f"{name}.json"

    def list_all_themes(self) -> Dict[str, str]:
        """List all available themes (built-in + custom).

        Returns:
            Dictionary mapping theme names to their types ('built-in' or 'custom')
        """
        themes = {}

        # Add built-in themes
        for theme_name in THEMES.keys():
            themes[theme_name] = "built-in"

        # Add custom themes
        for theme_file in self.themes_dir.glob("*.json"):
            theme_name = theme_file.stem
            if theme_name not in themes:  # Don't override built-in themes
                themes[theme_name] = "custom"

        return themes

    def get_custom_theme(self, name: str) -> Optional[Theme]:
        """Load a custom theme from file.

        Args:
            name: Theme name

        Returns:
            Theme object if found and valid, None otherwise
        """
        theme_file = self._get_theme_file_path(name)
        if not theme_file.exists():
            return None

        try:
            with open(theme_file) as f:
                theme_data = json.load(f)

            if not self._validate_theme_data(theme_data):
                return None

            return Theme(theme_data.get("colors", {}))
        except (json.JSONDecodeError, Exception):
            return None

    def save_custom_theme(self, name: str, theme_data: Dict) -> bool:
        """Save a custom theme to file.

        Args:
            name: Theme name
            theme_data: Theme data dictionary

        Returns:
            True if saved successfully, False otherwise
        """
        if name in THEMES:
            return False  # Cannot override built-in themes

        if not self._validate_theme_data(theme_data):
            return False

        try:
            theme_file = self._get_theme_file_path(name)
            with open(theme_file, "w") as f:
                json.dump(theme_data, f, indent=2)
            return True
        except Exception:
            return False

    def delete_custom_theme(self, name: str) -> bool:
        """Delete a custom theme.

        Args:
            name: Theme name

        Returns:
            True if deleted successfully, False otherwise
        """
        if name in THEMES:
            return False  # Cannot delete built-in themes

        theme_file = self._get_theme_file_path(name)
        if not theme_file.exists():
            return False

        try:
            theme_file.unlink()
            return True
        except Exception:
            return False

    def export_theme(self, name: str, output_file: Optional[str] = None) -> bool:
        """Export a theme to a JSON file.

        Args:
            name: Theme name
            output_file: Output file path. If None, uses theme name with .json extension

        Returns:
            True if exported successfully, False otherwise
        """
        theme_data = None

        # Check if it's a built-in theme
        if name in THEMES:
            theme = THEMES[name]
            # Rich Theme objects store styles as Rich Style objects, we need to convert to strings
            colors = {}
            if hasattr(theme, "styles") and theme.styles:
                # Only export custom styles (our theme-specific ones)
                custom_style_keys = [
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
                    "progress.description",
                    "progress.percentage",
                    "progress.elapsed",
                    "table.header",
                    "table.row",
                    "table.row.odd",
                    "panel.border",
                    "panel.title",
                    "panel.subtitle",
                ]
                for key in custom_style_keys:
                    if key in theme.styles:
                        style = theme.styles[key]
                        # Convert Rich Style to simple string representation
                        color_str = self._style_to_string(style)
                        if color_str:
                            colors[key] = color_str
            theme_data = {"name": name, "description": f"Built-in {name} theme", "colors": colors}
        else:
            # Check if it's a custom theme
            theme_file = self._get_theme_file_path(name)
            if theme_file.exists():
                try:
                    with open(theme_file) as f:
                        theme_data = json.load(f)
                except Exception:
                    return False

        if not theme_data:
            return False

        try:
            output_path = Path(output_file) if output_file else Path(f"{name}.json")
            with open(output_path, "w") as f:
                json.dump(theme_data, f, indent=2)
            return True
        except Exception:
            return False

    def import_theme(self, file_path: str, name: Optional[str] = None) -> Optional[str]:
        """Import a theme from a JSON file.

        Args:
            file_path: Path to the theme file
            name: Theme name. If None, uses name from file or filename

        Returns:
            Theme name if imported successfully, None otherwise
        """
        try:
            with open(file_path) as f:
                theme_data = json.load(f)
        except Exception:
            return None

        if not self._validate_theme_data(theme_data):
            return None

        # Determine theme name
        theme_name = name or theme_data.get("name") or Path(file_path).stem

        # Don't allow overriding built-in themes
        if theme_name in THEMES:
            return None

        if self.save_custom_theme(theme_name, theme_data):
            return theme_name
        return None

    def create_theme_interactively(self, name: str, base_theme: Optional[str] = None) -> bool:
        """Create a custom theme interactively.

        Args:
            name: New theme name
            base_theme: Base theme to copy from (optional)

        Returns:
            True if created successfully, False otherwise
        """
        console = get_console()

        if name in THEMES:
            console.print(f"❌ Cannot override built-in theme '{name}'", style="error")
            return False

        if self._get_theme_file_path(name).exists():
            if not Confirm.ask(f"Theme '{name}' already exists. Overwrite?"):
                return False

        # Start with base theme if provided
        colors = {}
        if base_theme:
            if base_theme in THEMES:
                colors = dict(THEMES[base_theme].styles)
            else:
                custom_theme = self.get_custom_theme(base_theme)
                if custom_theme:
                    colors = dict(custom_theme.styles)

        # Interactive customization
        console.print(f"\n🎨 Creating theme '{name}'", style="info")
        console.print("Press Enter to keep current value, or enter a new color:", style="muted")

        # Core colors that users are most likely to want to customize
        core_colors = [
            ("info", "Information messages"),
            ("warning", "Warning messages"),
            ("error", "Error messages"),
            ("success", "Success messages"),
            ("header", "Headers and titles"),
            ("link", "Links and references"),
            ("highlight", "Highlighted text"),
        ]

        for color_key, description in core_colors:
            current = colors.get(color_key, "")
            new_value = Prompt.ask(f"  {description} [{color_key}]", default=current, show_default=bool(current))
            if new_value:
                colors[color_key] = new_value

        # Ask if user wants to customize more colors
        if Confirm.ask("\nCustomize additional colors?", default=False):
            remaining_colors = [
                "field",
                "value",
                "muted",
                "prompt",
                "title",
                "subtitle",
                "progress.description",
                "progress.percentage",
                "progress.elapsed",
                "table.header",
                "table.row",
                "table.row.odd",
                "panel.border",
                "panel.title",
                "panel.subtitle",
            ]

            for color_key in remaining_colors:
                if color_key not in colors:
                    current = colors.get(color_key, "")
                    new_value = Prompt.ask(f"  {color_key}", default=current, show_default=bool(current))
                    if new_value:
                        colors[color_key] = new_value

        # Get description
        description = Prompt.ask("Theme description", default=f"Custom theme: {name}")

        # Create theme data
        theme_data = {"name": name, "description": description, "colors": colors}

        # Save the theme
        if self.save_custom_theme(name, theme_data):
            console.print(f"✅ Theme '{name}' created successfully!", style="success")
            return True
        else:
            console.print(f"❌ Failed to save theme '{name}'", style="error")
            return False

    def _validate_theme_data(self, theme_data: Dict) -> bool:
        """Validate theme data structure.

        Args:
            theme_data: Theme data dictionary

        Returns:
            True if valid, False otherwise
        """
        if not isinstance(theme_data, dict):
            return False

        # Must have colors section
        if "colors" not in theme_data:
            return False

        colors = theme_data["colors"]
        if not isinstance(colors, dict):
            return False

        # Validate color values (basic validation)
        valid_colors = {
            # Standard colors
            "black",
            "red",
            "green",
            "yellow",
            "blue",
            "magenta",
            "cyan",
            "white",
            # Bright colors
            "bright_black",
            "bright_red",
            "bright_green",
            "bright_yellow",
            "bright_blue",
            "bright_magenta",
            "bright_cyan",
            "bright_white",
            # RGB colors (simplified validation)
        }

        for color_value in colors.values():
            if not isinstance(color_value, str):
                return False

            # Allow rich style combinations like "bold red", "underline blue"
            parts = color_value.lower().split()
            color_part = parts[-1]  # Last part should be the color

            # Basic validation - accept standard colors or RGB patterns
            if not (
                color_part in valid_colors
                or color_part.startswith("#")
                or color_part.startswith("rgb(")
                or color_part.startswith("color(")
            ):
                # Allow some flexibility for Rich's color system
                continue

        return True

    def _style_to_string(self, style) -> str:
        """Convert a Rich Style object to a simple color string.

        Args:
            style: Rich Style object

        Returns:
            String representation of the style
        """
        parts = []

        # Add style modifiers
        if hasattr(style, "bold") and style.bold:
            parts.append("bold")
        if hasattr(style, "italic") and style.italic:
            parts.append("italic")
        if hasattr(style, "underline") and style.underline:
            parts.append("underline")
        if hasattr(style, "dim") and style.dim:
            parts.append("dim")
        if hasattr(style, "reverse") and style.reverse:
            parts.append("reverse")
        if hasattr(style, "strike") and style.strike:
            parts.append("strike")

        # Add color
        if hasattr(style, "color") and style.color:
            color = style.color
            if hasattr(color, "name"):
                parts.append(color.name)
            elif hasattr(color, "_name"):
                parts.append(color._name)
            else:
                parts.append(str(color))

        return " ".join(parts) if parts else ""

    def display_themes_table(self) -> None:
        """Display a table of all available themes."""
        console = get_console()
        themes = self.list_all_themes()

        if not themes:
            console.print("No themes available", style="warning")
            return

        table = Table(title="Available Themes")
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Type", style="green")
        table.add_column("Description", style="blue")

        for name, theme_type in sorted(themes.items()):
            description = ""
            if theme_type == "built-in":
                description = f"Built-in {name} theme"
            else:
                # Try to get description from custom theme file
                theme_file = self._get_theme_file_path(name)
                if theme_file.exists():
                    try:
                        with open(theme_file) as f:
                            theme_data = json.load(f)
                        description = theme_data.get("description", "Custom theme")
                    except Exception:
                        description = "Custom theme"

            table.add_row(name, theme_type, description)

        console.print(table)
