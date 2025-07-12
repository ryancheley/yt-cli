"""Panel utilities and display components for YouTrack CLI."""

from typing import Any, Dict, List, Optional, Union

from rich.console import Group, RenderableType
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .console import get_console


class PanelFactory:
    """Factory class for creating themed panels with consistent styling."""

    @staticmethod
    def create_info_panel(
        title: str,
        content: Union[str, RenderableType],
        subtitle: Optional[str] = None,
        expand: bool = True,
        padding: tuple = (0, 1),
    ) -> Panel:
        """Create an info panel with standard styling.

        Args:
            title: Panel title
            content: Panel content (string or Rich renderable)
            subtitle: Optional subtitle
            expand: Whether panel should expand to fill width
            padding: Panel padding (top/bottom, left/right)

        Returns:
            Panel: Styled panel with info theme
        """
        return Panel(
            content,
            title=f"[header]{title}[/header]",
            subtitle=f"[subtitle]{subtitle}[/subtitle]" if subtitle else None,
            title_align="left",
            border_style="info",
            expand=expand,
            padding=padding,
        )

    @staticmethod
    def create_details_panel(
        title: str,
        data: Dict[str, Any],
        subtitle: Optional[str] = None,
        expand: bool = True,
    ) -> Panel:
        """Create a details panel displaying key-value pairs.

        Args:
            title: Panel title
            data: Dictionary of field names to values
            subtitle: Optional subtitle
            expand: Whether panel should expand to fill width

        Returns:
            Panel: Styled panel with formatted data
        """
        table = Table.grid(padding=(0, 1))
        table.add_column(style="field", no_wrap=True)
        table.add_column(style="value")

        for key, value in data.items():
            if value is not None:
                # Handle different value types
                if isinstance(value, list):
                    formatted_value = ", ".join(str(v) for v in value)
                elif isinstance(value, bool):
                    formatted_value = "✓" if value else "✗"
                else:
                    formatted_value = str(value)

                table.add_row(f"{key}:", formatted_value)

        return PanelFactory.create_info_panel(
            title=title,
            content=table,
            subtitle=subtitle,
            expand=expand,
        )

    @staticmethod
    def create_status_panel(
        title: str,
        status: str,
        status_color: str = "success",
        details: Optional[Dict[str, Any]] = None,
        subtitle: Optional[str] = None,
    ) -> Panel:
        """Create a status panel with colored status indicator.

        Args:
            title: Panel title
            status: Status text
            status_color: Rich color style for status
            details: Optional additional details to display
            subtitle: Optional subtitle

        Returns:
            Panel: Styled status panel
        """
        content_parts = [Text(status, style=status_color)]

        if details:
            table = Table.grid(padding=(0, 1))
            table.add_column(style="field", no_wrap=True)
            table.add_column(style="value")

            for key, value in details.items():
                if value is not None:
                    table.add_row(f"{key}:", str(value))

            content_parts.append(Text())  # Empty line
            content_parts.append(table)

        return PanelFactory.create_info_panel(
            title=title,
            content=Group(*content_parts),
            subtitle=subtitle,
        )

    @staticmethod
    def create_warning_panel(
        title: str,
        content: Union[str, RenderableType],
        subtitle: Optional[str] = None,
    ) -> Panel:
        """Create a warning panel with warning styling.

        Args:
            title: Panel title
            content: Panel content
            subtitle: Optional subtitle

        Returns:
            Panel: Styled warning panel
        """
        return Panel(
            content,
            title=f"[warning]{title}[/warning]",
            subtitle=f"[subtitle]{subtitle}[/subtitle]" if subtitle else None,
            title_align="left",
            border_style="warning",
            expand=True,
            padding=(0, 1),
        )

    @staticmethod
    def create_error_panel(
        title: str,
        content: Union[str, RenderableType],
        subtitle: Optional[str] = None,
    ) -> Panel:
        """Create an error panel with error styling.

        Args:
            title: Panel title
            content: Panel content
            subtitle: Optional subtitle

        Returns:
            Panel: Styled error panel
        """
        return Panel(
            content,
            title=f"[error]{title}[/error]",
            subtitle=f"[subtitle]{subtitle}[/subtitle]" if subtitle else None,
            title_align="left",
            border_style="danger",
            expand=True,
            padding=(0, 1),
        )


class PanelGroup:
    """Container for managing multiple related panels."""

    def __init__(self, title: Optional[str] = None):
        """Initialize panel group.

        Args:
            title: Optional group title
        """
        self.title = title
        self.panels: List[Panel] = []

    def add_panel(self, panel: Panel) -> None:
        """Add a panel to the group.

        Args:
            panel: Panel to add
        """
        self.panels.append(panel)

    def add_info_panel(
        self,
        title: str,
        content: Union[str, RenderableType],
        subtitle: Optional[str] = None,
    ) -> None:
        """Add an info panel to the group.

        Args:
            title: Panel title
            content: Panel content
            subtitle: Optional subtitle
        """
        panel = PanelFactory.create_info_panel(title, content, subtitle)
        self.add_panel(panel)

    def add_details_panel(
        self,
        title: str,
        data: Dict[str, Any],
        subtitle: Optional[str] = None,
    ) -> None:
        """Add a details panel to the group.

        Args:
            title: Panel title
            data: Dictionary of field names to values
            subtitle: Optional subtitle
        """
        panel = PanelFactory.create_details_panel(title, data, subtitle)
        self.add_panel(panel)

    def render(self) -> Group:
        """Render all panels in the group.

        Returns:
            Group: Rich Group containing all panels
        """
        if self.title:
            title_text = Text(self.title, style="title")
            return Group(title_text, "", *self.panels)
        return Group(*self.panels)

    def display(self) -> None:
        """Display all panels in the group using the console."""
        console = get_console()
        console.print(self.render())


def create_issue_overview_panel(issue_data: Dict[str, Any]) -> Panel:
    """Create an issue overview panel with key information.

    Args:
        issue_data: Dictionary containing issue information

    Returns:
        Panel: Formatted issue overview panel
    """
    overview_data = {
        "ID": issue_data.get("id"),
        "Summary": issue_data.get("summary"),
        "Status": issue_data.get("state", {}).get("name"),
        "Priority": issue_data.get("priority", {}).get("name"),
        "Type": issue_data.get("type", {}).get("name"),
    }

    return PanelFactory.create_details_panel(
        title="Issue Overview",
        data=overview_data,
        subtitle=f"Created: {issue_data.get('created', 'Unknown')}",
    )


def create_issue_details_panel(issue_data: Dict[str, Any]) -> Panel:
    """Create an issue details panel with comprehensive information.

    Args:
        issue_data: Dictionary containing issue information

    Returns:
        Panel: Formatted issue details panel
    """
    details_data = {
        "Description": issue_data.get("description", "No description"),
        "Reporter": issue_data.get("reporter", {}).get("name"),
        "Assignee": issue_data.get("assignee", {}).get("name") or "Unassigned",
        "Created": issue_data.get("created"),
        "Updated": issue_data.get("updated"),
        "Resolved": issue_data.get("resolved"),
    }

    return PanelFactory.create_details_panel(
        title="Issue Details",
        data=details_data,
    )


def create_custom_fields_panel(custom_fields: List[Dict[str, Any]]) -> Panel:
    """Create a custom fields panel.

    Args:
        custom_fields: List of custom field dictionaries

    Returns:
        Panel: Formatted custom fields panel
    """
    if not custom_fields:
        return PanelFactory.create_info_panel(
            title="Custom Fields",
            content="[muted]No custom fields configured[/muted]",
        )

    fields_data = {}
    for field in custom_fields:
        field_name = field.get("name", "Unknown Field")
        field_value = field.get("value")

        if field_value is not None:
            if isinstance(field_value, dict):
                # Handle complex field values (e.g., user fields, enum fields)
                display_value = field_value.get("name") or field_value.get("login") or str(field_value)
            elif isinstance(field_value, list):
                # Handle multi-value fields
                display_value = ", ".join(str(v.get("name", v)) if isinstance(v, dict) else str(v) for v in field_value)
            else:
                display_value = str(field_value)

            fields_data[field_name] = display_value

    return PanelFactory.create_details_panel(
        title="Custom Fields",
        data=fields_data,
    )


def create_project_overview_panel(project_data: Dict[str, Any]) -> Panel:
    """Create a project overview panel.

    Args:
        project_data: Dictionary containing project information

    Returns:
        Panel: Formatted project overview panel
    """
    overview_data = {
        "Name": project_data.get("name"),
        "ID": project_data.get("shortName"),
        "Description": project_data.get("description") or "No description",
        "Team": project_data.get("team", {}).get("name") if project_data.get("team") else "No team assigned",
    }

    return PanelFactory.create_details_panel(
        title="Project Overview",
        data=overview_data,
    )
