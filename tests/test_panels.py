"""Tests for panel display functionality."""

from unittest.mock import Mock, patch

import pytest
from rich.console import Console
from rich.panel import Panel

from youtrack_cli.panels import (
    PanelFactory,
    PanelGroup,
    create_custom_fields_panel,
    create_issue_details_panel,
    create_issue_overview_panel,
    create_project_overview_panel,
)


class TestPanelFactory:
    """Test the PanelFactory class."""

    def test_create_info_panel(self):
        """Test creating an info panel."""
        panel = PanelFactory.create_info_panel("Test Title", "Test Content")

        assert isinstance(panel, Panel)
        assert "Test Title" in str(panel.title)
        assert "Test Content" in str(panel.renderable)

    def test_create_info_panel_with_subtitle(self):
        """Test creating an info panel with subtitle."""
        panel = PanelFactory.create_info_panel("Test Title", "Test Content", subtitle="Test Subtitle")

        assert isinstance(panel, Panel)
        assert "Test Subtitle" in str(panel.subtitle)

    def test_create_details_panel(self):
        """Test creating a details panel with data."""
        data = {
            "Field 1": "Value 1",
            "Field 2": "Value 2",
            "Field 3": None,  # Should be skipped
        }

        panel = PanelFactory.create_details_panel("Details", data)

        assert isinstance(panel, Panel)
        assert "Details" in str(panel.title)

    def test_create_details_panel_with_list_value(self):
        """Test creating a details panel with list values."""
        data = {
            "Tags": ["tag1", "tag2", "tag3"],
            "Numbers": [1, 2, 3],
        }

        panel = PanelFactory.create_details_panel("Details", data)

        assert isinstance(panel, Panel)

    def test_create_details_panel_with_boolean_value(self):
        """Test creating a details panel with boolean values."""
        data = {
            "Active": True,
            "Archived": False,
        }

        panel = PanelFactory.create_details_panel("Details", data)

        assert isinstance(panel, Panel)

    def test_create_status_panel(self):
        """Test creating a status panel."""
        panel = PanelFactory.create_status_panel("Status", "Active", "green")

        assert isinstance(panel, Panel)
        assert "Status" in str(panel.title)

    def test_create_status_panel_with_details(self):
        """Test creating a status panel with additional details."""
        details = {
            "Last Updated": "2024-01-01",
            "Owner": "John Doe",
        }

        panel = PanelFactory.create_status_panel("Status", "Active", "green", details=details)

        assert isinstance(panel, Panel)

    def test_create_warning_panel(self):
        """Test creating a warning panel."""
        panel = PanelFactory.create_warning_panel("Warning", "This is a warning")

        assert isinstance(panel, Panel)
        assert "Warning" in str(panel.title)

    def test_create_error_panel(self):
        """Test creating an error panel."""
        panel = PanelFactory.create_error_panel("Error", "This is an error")

        assert isinstance(panel, Panel)
        assert "Error" in str(panel.title)


class TestPanelGroup:
    """Test the PanelGroup class."""

    def test_panel_group_creation(self):
        """Test creating a panel group."""
        group = PanelGroup("Test Group")

        assert group.title == "Test Group"
        assert len(group.panels) == 0

    def test_add_panel(self):
        """Test adding a panel to a group."""
        group = PanelGroup("Test Group")
        panel = PanelFactory.create_info_panel("Test", "Content")

        group.add_panel(panel)

        assert len(group.panels) == 1
        assert group.panels[0] == panel

    def test_add_info_panel(self):
        """Test adding an info panel via helper method."""
        group = PanelGroup("Test Group")

        group.add_info_panel("Test Title", "Test Content")

        assert len(group.panels) == 1

    def test_add_details_panel(self):
        """Test adding a details panel via helper method."""
        group = PanelGroup("Test Group")
        data = {"Field": "Value"}

        group.add_details_panel("Details", data)

        assert len(group.panels) == 1

    def test_render_without_title(self):
        """Test rendering a group without title."""
        group = PanelGroup()
        group.add_info_panel("Test", "Content")

        rendered = group.render()

        # Should have at least one panel
        assert len(rendered.renderables) >= 1

    def test_render_with_title(self):
        """Test rendering a group with title."""
        group = PanelGroup("Test Group")
        group.add_info_panel("Test", "Content")

        rendered = group.render()

        # Should have title, empty line, and panel
        assert len(rendered.renderables) >= 2

    @patch("youtrack_cli.panels.get_console")
    def test_display(self, mock_get_console):
        """Test displaying a panel group."""
        mock_console = Mock()
        mock_get_console.return_value = mock_console

        group = PanelGroup("Test Group")
        group.add_info_panel("Test", "Content")

        group.display()

        mock_console.print.assert_called_once()


class TestIssuePanelFunctions:
    """Test issue-specific panel functions."""

    def test_create_issue_overview_panel(self):
        """Test creating an issue overview panel."""
        issue_data = {
            "id": "TEST-123",
            "summary": "Test Issue",
            "state": {"name": "Open"},
            "priority": {"name": "High"},
            "type": {"name": "Bug"},
            "created": "2024-01-01T00:00:00Z",
        }

        panel = create_issue_overview_panel(issue_data)

        assert isinstance(panel, Panel)
        assert "Issue Overview" in str(panel.title)

    def test_create_issue_overview_panel_minimal_data(self):
        """Test creating an issue overview panel with minimal data."""
        issue_data = {"id": "TEST-123"}

        panel = create_issue_overview_panel(issue_data)

        assert isinstance(panel, Panel)

    def test_create_issue_details_panel(self):
        """Test creating an issue details panel."""
        issue_data = {
            "id": "TEST-123",
            "description": "Test description",
            "reporter": {"name": "Reporter"},
            "assignee": {"name": "Assignee"},
            "created": "2024-01-01T00:00:00Z",
            "updated": "2024-01-02T00:00:00Z",
            "resolved": "2024-01-03T00:00:00Z",
        }

        panel = create_issue_details_panel(issue_data)

        assert isinstance(panel, Panel)
        assert "Issue Details" in str(panel.title)

    def test_create_issue_details_panel_no_assignee(self):
        """Test creating an issue details panel with no assignee."""
        issue_data = {
            "id": "TEST-123",
            "description": "Test description",
        }

        panel = create_issue_details_panel(issue_data)

        assert isinstance(panel, Panel)

    def test_create_custom_fields_panel_empty(self):
        """Test creating a custom fields panel with no fields."""
        custom_fields = []

        panel = create_custom_fields_panel(custom_fields)

        assert isinstance(panel, Panel)
        assert "Custom Fields" in str(panel.title)

    def test_create_custom_fields_panel_with_fields(self):
        """Test creating a custom fields panel with fields."""
        custom_fields = [
            {"name": "Priority", "value": {"name": "High"}},
            {"name": "Component", "value": "Backend"},
            {"name": "Tags", "value": [{"name": "bug"}, {"name": "urgent"}]},
        ]

        panel = create_custom_fields_panel(custom_fields)

        assert isinstance(panel, Panel)
        assert "Custom Fields" in str(panel.title)

    def test_create_custom_fields_panel_complex_values(self):
        """Test creating a custom fields panel with complex field values."""
        custom_fields = [
            {"name": "User Field", "value": {"login": "user123", "name": "User Name"}},
            {"name": "Dict Field", "value": {"some": "value"}},
            {"name": "None Field", "value": None},
        ]

        panel = create_custom_fields_panel(custom_fields)

        assert isinstance(panel, Panel)

    def test_create_project_overview_panel(self):
        """Test creating a project overview panel."""
        project_data = {
            "name": "Test Project",
            "shortName": "TP",
            "description": "A test project",
            "team": {"name": "Development Team"},
        }

        panel = create_project_overview_panel(project_data)

        assert isinstance(panel, Panel)
        assert "Project Overview" in str(panel.title)

    def test_create_project_overview_panel_minimal(self):
        """Test creating a project overview panel with minimal data."""
        project_data = {
            "name": "Test Project",
        }

        panel = create_project_overview_panel(project_data)

        assert isinstance(panel, Panel)


@pytest.fixture
def mock_console():
    """Provide a mock console for testing."""
    return Mock(spec=Console)


@pytest.fixture
def sample_issue_data():
    """Provide sample issue data for testing."""
    return {
        "id": "TEST-123",
        "summary": "Test Issue Summary",
        "description": "This is a test issue description",
        "state": {"name": "Open"},
        "priority": {"name": "High"},
        "type": {"name": "Bug"},
        "reporter": {"name": "Reporter Name"},
        "assignee": {"name": "Assignee Name"},
        "created": "2024-01-01T00:00:00Z",
        "updated": "2024-01-02T00:00:00Z",
        "customFields": [
            {"name": "Component", "value": "Backend"},
            {"name": "Fix Version", "value": {"name": "v1.0.0"}},
        ],
        "tags": [
            {"name": "bug"},
            {"name": "urgent"},
        ],
    }


@pytest.fixture
def sample_project_data():
    """Provide sample project data for testing."""
    return {
        "name": "Sample Project",
        "shortName": "SP",
        "description": "A sample project for testing",
        "team": {"name": "Sample Team"},
        "leader": {"fullName": "Project Leader"},
        "issuesCount": 42,
        "archived": False,
    }
