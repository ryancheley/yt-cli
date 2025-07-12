"""Tests for enhanced tree display functionality."""

from unittest.mock import Mock, patch

import pytest
from rich.tree import Tree

from youtrack_cli.trees import (
    EnhancedTreeBuilder,
    _get_status_color,
    create_enhanced_articles_tree,
    create_issue_dependencies_tree,
    create_project_hierarchy_tree,
)


class TestEnhancedTreeBuilder:
    """Test the EnhancedTreeBuilder class."""

    def test_builder_creation(self):
        """Test creating a tree builder."""
        builder = EnhancedTreeBuilder("Test Root")

        assert isinstance(builder.tree, Tree)
        assert builder.tree.label == "Test Root"

    def test_add_node_with_metadata(self):
        """Test adding a node with metadata."""
        builder = EnhancedTreeBuilder("Root")

        metadata = {
            "Author": "John Doe",
            "Date": "2024-01-01",
            "Status": "Active",
        }

        node = builder.add_node_with_metadata(builder.tree, "Test Node", metadata, style="green")

        assert node is not None

    def test_add_node_with_empty_metadata(self):
        """Test adding a node with empty metadata."""
        builder = EnhancedTreeBuilder("Root")

        node = builder.add_node_with_metadata(builder.tree, "Test Node", {}, style="green")

        assert node is not None

    def test_add_node_with_none_values(self):
        """Test adding a node with None values in metadata."""
        builder = EnhancedTreeBuilder("Root")

        metadata = {
            "Author": "John Doe",
            "Date": None,
            "Status": "Active",
        }

        node = builder.add_node_with_metadata(builder.tree, "Test Node", metadata)

        assert node is not None

    def test_add_status_node(self):
        """Test adding a status node."""
        builder = EnhancedTreeBuilder("Root")

        additional_info = {
            "Priority": "High",
            "Assignee": "Jane Doe",
        }

        node = builder.add_status_node(builder.tree, "Test Issue", "Open", "blue", additional_info)

        assert node is not None

    def test_add_status_node_without_additional_info(self):
        """Test adding a status node without additional info."""
        builder = EnhancedTreeBuilder("Root")

        node = builder.add_status_node(builder.tree, "Test Issue", "Closed", "green")

        assert node is not None

    def test_get_tree(self):
        """Test getting the tree object."""
        builder = EnhancedTreeBuilder("Root")

        tree = builder.get_tree()

        assert isinstance(tree, Tree)
        assert tree is builder.tree

    @patch("youtrack_cli.trees.get_console")
    def test_display(self, mock_get_console):
        """Test displaying the tree."""
        mock_console = Mock()
        mock_get_console.return_value = mock_console

        builder = EnhancedTreeBuilder("Root")
        builder.display()

        mock_console.print.assert_called_once_with(builder.tree)


class TestIssueDependenciesTree:
    """Test the issue dependencies tree function."""

    def test_create_issue_dependencies_tree_basic(self):
        """Test creating a basic dependencies tree."""
        issue = {
            "id": "MAIN-123",
            "summary": "Main Issue",
            "state": {"name": "Open"},
            "priority": {"name": "High"},
            "assignee": {"fullName": "John Doe"},
        }

        dependencies = []

        tree = create_issue_dependencies_tree(issue, dependencies)

        assert isinstance(tree, Tree)

    def test_create_issue_dependencies_tree_with_dependencies(self):
        """Test creating a dependencies tree with actual dependencies."""
        issue = {
            "id": "MAIN-123",
            "summary": "Main Issue",
            "state": {"name": "In Progress"},
            "priority": {"name": "High"},
            "assignee": {"fullName": "John Doe"},
        }

        dependencies = [
            {
                "linkType": {"name": "Depends on"},
                "direction": "outward",
                "target": {
                    "id": "DEP-456",
                    "summary": "Dependency Issue",
                    "state": {"name": "Open"},
                    "type": {"name": "Task"},
                    "priority": {"name": "Medium"},
                },
            },
            {
                "linkType": {"name": "Blocks"},
                "direction": "inward",
                "target": {
                    "id": "BLOCK-789",
                    "summary": "Blocked Issue",
                    "state": {"name": "Waiting"},
                    "type": {"name": "Bug"},
                    "priority": {"name": "Low"},
                },
            },
        ]

        tree = create_issue_dependencies_tree(issue, dependencies, show_status=True)

        assert isinstance(tree, Tree)

    def test_create_issue_dependencies_tree_without_status(self):
        """Test creating a dependencies tree without status indicators."""
        issue = {
            "id": "MAIN-123",
            "summary": "Main Issue",
            "state": {"name": "Open"},
        }

        dependencies = [
            {
                "linkType": {"name": "Related to"},
                "direction": "bidirectional",
                "target": {
                    "id": "REL-999",
                    "summary": "Related Issue",
                    "state": {"name": "Closed"},
                },
            },
        ]

        tree = create_issue_dependencies_tree(issue, dependencies, show_status=False)

        assert isinstance(tree, Tree)


class TestProjectHierarchyTree:
    """Test the project hierarchy tree function."""

    def test_create_project_hierarchy_tree_flat(self):
        """Test creating a project hierarchy with no nesting."""
        projects = [
            {
                "id": "PROJ1",
                "shortName": "P1",
                "name": "Project One",
                "leader": {"fullName": "Leader One"},
                "issuesCount": 10,
                "archived": False,
            },
            {
                "id": "PROJ2",
                "shortName": "P2",
                "name": "Project Two",
                "leader": {"fullName": "Leader Two"},
                "issuesCount": 5,
                "archived": True,
            },
        ]

        tree = create_project_hierarchy_tree(projects)

        assert isinstance(tree, Tree)

    def test_create_project_hierarchy_tree_nested(self):
        """Test creating a project hierarchy with nesting."""
        projects = [
            {
                "id": "PARENT",
                "shortName": "PAR",
                "name": "Parent Project",
                "leader": {"fullName": "Parent Leader"},
                "issuesCount": 20,
                "archived": False,
            },
            {
                "id": "CHILD1",
                "shortName": "CH1",
                "name": "Child Project One",
                "parent": {"id": "PARENT"},
                "leader": {"fullName": "Child Leader 1"},
                "issuesCount": 8,
                "archived": False,
            },
            {
                "id": "CHILD2",
                "shortName": "CH2",
                "name": "Child Project Two",
                "parent": {"id": "PARENT"},
                "issuesCount": 3,
                "archived": True,
            },
        ]

        tree = create_project_hierarchy_tree(projects)

        assert isinstance(tree, Tree)

    def test_create_project_hierarchy_tree_empty(self):
        """Test creating a project hierarchy with no projects."""
        projects = []

        tree = create_project_hierarchy_tree(projects)

        assert isinstance(tree, Tree)


class TestEnhancedArticlesTree:
    """Test the enhanced articles tree function."""

    def test_create_enhanced_articles_tree_basic(self):
        """Test creating a basic enhanced articles tree."""
        articles = [
            {
                "id": "ART-1",
                "idReadable": "ART-1",
                "summary": "Article One",
                "reporter": {"fullName": "Author One"},
                "created": "2024-01-01T00:00:00Z",
                "visibility": {"$type": "UnlimitedVisibility"},
            },
            {
                "id": "ART-2",
                "idReadable": "ART-2",
                "summary": "Article Two",
                "reporter": {"fullName": "Author Two"},
                "created": "2024-01-02T00:00:00Z",
                "visibility": {"$type": "LimitedVisibility"},
            },
        ]

        tree = create_enhanced_articles_tree(articles, show_metadata=True)

        assert isinstance(tree, Tree)

    def test_create_enhanced_articles_tree_without_metadata(self):
        """Test creating an enhanced articles tree without metadata."""
        articles = [
            {
                "id": "ART-1",
                "summary": "Article One",
                "visibility": {"$type": "UnlimitedVisibility"},
            },
        ]

        tree = create_enhanced_articles_tree(articles, show_metadata=False)

        assert isinstance(tree, Tree)

    def test_create_enhanced_articles_tree_nested(self):
        """Test creating an enhanced articles tree with nesting."""
        articles = [
            {
                "id": "PARENT-ART",
                "idReadable": "PARENT-ART",
                "summary": "Parent Article",
                "reporter": {"fullName": "Parent Author"},
                "created": "2024-01-01T00:00:00Z",
                "visibility": {"$type": "UnlimitedVisibility"},
            },
            {
                "id": "CHILD-ART",
                "idReadable": "CHILD-ART",
                "summary": "Child Article",
                "parentArticle": {"id": "PARENT-ART"},
                "reporter": {"fullName": "Child Author"},
                "created": "2024-01-02T00:00:00Z",
                "visibility": {"$type": "LimitedVisibility"},
            },
        ]

        tree = create_enhanced_articles_tree(articles, show_metadata=True)

        assert isinstance(tree, Tree)

    def test_create_enhanced_articles_tree_invalid_date(self):
        """Test creating an enhanced articles tree with invalid date."""
        articles = [
            {
                "id": "ART-1",
                "summary": "Article One",
                "created": "invalid-date",
                "visibility": {"$type": "UnlimitedVisibility"},
            },
        ]

        tree = create_enhanced_articles_tree(articles, show_metadata=True)

        assert isinstance(tree, Tree)

    def test_create_enhanced_articles_tree_unknown_visibility(self):
        """Test creating an enhanced articles tree with unknown visibility."""
        articles = [
            {
                "id": "ART-1",
                "summary": "Article One",
                "visibility": {"$type": "UnknownVisibility"},
            },
        ]

        tree = create_enhanced_articles_tree(articles, show_metadata=True)

        assert isinstance(tree, Tree)


class TestStatusColorFunction:
    """Test the status color utility function."""

    def test_get_status_color_open_states(self):
        """Test status colors for open states."""
        assert _get_status_color("Open") == "blue"
        assert _get_status_color("New") == "blue"
        assert _get_status_color("To Do") == "blue"
        assert _get_status_color("Backlog") == "blue"

    def test_get_status_color_in_progress_states(self):
        """Test status colors for in progress states."""
        assert _get_status_color("In Progress") == "yellow"
        assert _get_status_color("Working") == "yellow"
        assert _get_status_color("Active") == "yellow"

    def test_get_status_color_done_states(self):
        """Test status colors for done states."""
        assert _get_status_color("Done") == "green"
        assert _get_status_color("Resolved") == "green"
        assert _get_status_color("Closed") == "green"
        assert _get_status_color("Fixed") == "green"

    def test_get_status_color_blocked_states(self):
        """Test status colors for blocked states."""
        assert _get_status_color("Blocked") == "red"
        assert _get_status_color("Waiting") == "red"
        assert _get_status_color("On Hold") == "red"

    def test_get_status_color_unknown_state(self):
        """Test status color for unknown state."""
        assert _get_status_color("Unknown State") == "white"
        assert _get_status_color("") == "white"

    def test_get_status_color_case_insensitive(self):
        """Test that status color matching is case insensitive."""
        assert _get_status_color("OPEN") == "blue"
        assert _get_status_color("in progress") == "yellow"
        assert _get_status_color("DONE") == "green"
        assert _get_status_color("BLOCKED") == "red"


@pytest.fixture
def sample_issue_data():
    """Provide sample issue data for testing."""
    return {
        "id": "TEST-123",
        "summary": "Test Issue",
        "state": {"name": "Open"},
        "priority": {"name": "High"},
        "assignee": {"fullName": "John Doe"},
        "type": {"name": "Bug"},
    }


@pytest.fixture
def sample_dependency_data():
    """Provide sample dependency data for testing."""
    return [
        {
            "linkType": {"name": "Depends on"},
            "direction": "outward",
            "target": {
                "id": "DEP-456",
                "summary": "Dependency Issue",
                "state": {"name": "Open"},
                "type": {"name": "Task"},
                "priority": {"name": "Medium"},
            },
        },
        {
            "linkType": {"name": "Related to"},
            "direction": "bidirectional",
            "target": {
                "id": "REL-789",
                "summary": "Related Issue",
                "state": {"name": "Closed"},
                "type": {"name": "Story"},
                "priority": {"name": "Low"},
            },
        },
    ]


@pytest.fixture
def sample_project_data():
    """Provide sample project data for testing."""
    return [
        {
            "id": "PROJ1",
            "shortName": "P1",
            "name": "Project One",
            "leader": {"fullName": "Leader One"},
            "issuesCount": 10,
            "archived": False,
        },
        {
            "id": "PROJ2",
            "shortName": "P2",
            "name": "Project Two",
            "parent": {"id": "PROJ1"},
            "leader": {"fullName": "Leader Two"},
            "issuesCount": 5,
            "archived": True,
        },
    ]


@pytest.fixture
def sample_articles_data():
    """Provide sample articles data for testing."""
    return [
        {
            "id": "ART-1",
            "idReadable": "ART-1",
            "summary": "Root Article",
            "reporter": {"fullName": "Author One"},
            "created": "2024-01-01T00:00:00Z",
            "visibility": {"$type": "UnlimitedVisibility"},
        },
        {
            "id": "ART-2",
            "idReadable": "ART-2",
            "summary": "Child Article",
            "parentArticle": {"id": "ART-1"},
            "reporter": {"fullName": "Author Two"},
            "created": "2024-01-02T00:00:00Z",
            "visibility": {"$type": "LimitedVisibility"},
        },
    ]
