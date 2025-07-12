"""Enhanced tree display components for YouTrack CLI."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from rich.tree import Tree

from .console import get_console


class EnhancedTreeBuilder:
    """Builder class for creating enhanced Rich tree displays."""

    def __init__(self, root_label: str, console=None):
        """Initialize the tree builder.

        Args:
            root_label: Label for the root node
            console: Optional console instance (uses global if not provided)
        """
        self.tree = Tree(root_label)
        self.console = console or get_console()

    def add_node_with_metadata(
        self,
        parent_node: Any,
        label: str,
        metadata: Dict[str, Any],
        style: str = "white",
        dim_metadata: bool = True,
    ) -> Any:
        """Add a node with metadata display.

        Args:
            parent_node: Parent tree node
            label: Primary label for the node
            metadata: Dictionary of metadata to display
            style: Rich style for the main label
            dim_metadata: Whether to dim the metadata display

        Returns:
            The created tree node
        """
        metadata_parts = []
        for key, value in metadata.items():
            if value is not None:
                metadata_parts.append(f"{key}: {value}")

        metadata_text = " | ".join(metadata_parts)

        if metadata_text:
            if dim_metadata:
                node_text = f"[{style}]{label}[/{style}] [dim]({metadata_text})[/dim]"
            else:
                node_text = f"[{style}]{label}[/{style}] ({metadata_text})"
        else:
            node_text = f"[{style}]{label}[/{style}]"

        return parent_node.add(node_text)

    def add_status_node(
        self,
        parent_node: Any,
        label: str,
        status: str,
        status_color: str = "green",
        additional_info: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Add a node with status indicator.

        Args:
            parent_node: Parent tree node
            label: Primary label for the node
            status: Status text
            status_color: Color for status indicator
            additional_info: Optional additional metadata

        Returns:
            The created tree node
        """
        status_text = f"[{status_color}]●[/{status_color}] {status}"

        if additional_info:
            metadata_parts = []
            for key, value in additional_info.items():
                if value is not None:
                    metadata_parts.append(f"{key}: {value}")

            if metadata_parts:
                metadata_text = " | ".join(metadata_parts)
                node_text = f"{label} {status_text} [dim]({metadata_text})[/dim]"
            else:
                node_text = f"{label} {status_text}"
        else:
            node_text = f"{label} {status_text}"

        return parent_node.add(node_text)

    def display(self) -> None:
        """Display the tree."""
        self.console.print(self.tree)

    def get_tree(self) -> Tree:
        """Get the tree object.

        Returns:
            The Rich Tree object
        """
        return self.tree


def create_issue_dependencies_tree(
    issue: Dict[str, Any],
    dependencies: List[Dict[str, Any]],
    show_status: bool = True,
) -> Tree:
    """Create a tree view of issue dependencies.

    Args:
        issue: Main issue data
        dependencies: List of related/dependent issues
        show_status: Whether to show status indicators

    Returns:
        Rich Tree object with dependencies
    """
    issue_id = issue.get("id", "Unknown")
    issue_summary = issue.get("summary", "No summary")

    builder = EnhancedTreeBuilder(f"🎯 Dependencies for {issue_id}")
    root_node = builder.tree

    # Add main issue node
    main_status = issue.get("state", {}).get("name", "Unknown")
    status_color = _get_status_color(main_status)

    main_metadata = {
        "Priority": issue.get("priority", {}).get("name"),
        "Assignee": issue.get("assignee", {}).get("fullName", "Unassigned"),
    }

    if show_status:
        main_node = builder.add_status_node(
            root_node,
            f"{issue_id}: {issue_summary}",
            main_status,
            status_color,
            main_metadata,
        )
    else:
        main_node = builder.add_node_with_metadata(
            root_node,
            f"{issue_id}: {issue_summary}",
            main_metadata,
        )

    # Group dependencies by type
    depends_on = []
    dependents = []
    related = []

    for dep in dependencies:
        link_type = dep.get("linkType", {}).get("name", "").lower()
        if "depend" in link_type:
            if "outward" in dep.get("direction", "").lower():
                depends_on.append(dep)
            else:
                dependents.append(dep)
        else:
            related.append(dep)

    # Add depends on section
    if depends_on:
        depends_node = main_node.add("[red]⬆ Depends On[/red]")
        for dep in depends_on:
            _add_dependency_node(builder, depends_node, dep, show_status)

    # Add dependents section
    if dependents:
        dependents_node = main_node.add("[blue]⬇ Dependents[/blue]")
        for dep in dependents:
            _add_dependency_node(builder, dependents_node, dep, show_status)

    # Add related issues section
    if related:
        related_node = main_node.add("[yellow]🔗 Related[/yellow]")
        for dep in related:
            _add_dependency_node(builder, related_node, dep, show_status)

    return builder.tree


def create_project_hierarchy_tree(projects: List[Dict[str, Any]]) -> Tree:
    """Create a tree view of project hierarchy.

    Args:
        projects: List of project data

    Returns:
        Rich Tree object with project hierarchy
    """
    builder = EnhancedTreeBuilder("🏗️ Project Hierarchy")

    # Group projects by parent
    root_projects = []
    child_projects: Dict[str, List[Dict[str, Any]]] = {}

    for project in projects:
        parent_id = project.get("parent", {}).get("id")
        if parent_id:
            if parent_id not in child_projects:
                child_projects[parent_id] = []
            child_projects[parent_id].append(project)
        else:
            root_projects.append(project)

    def add_project_to_tree(parent_node: Any, project: Dict[str, Any]) -> None:
        project_id = project.get("shortName", project.get("id", "unknown"))
        project_name = project.get("name", "Unnamed Project")

        metadata = {
            "Lead": project.get("leader", {}).get("fullName"),
            "Issues": project.get("issuesCount", 0),
        }

        # Determine project status
        archived = project.get("archived", False)
        if archived:
            style = "dim red"
            metadata["Status"] = "Archived"
        else:
            style = "green"
            metadata["Status"] = "Active"

        child_node = builder.add_node_with_metadata(
            parent_node,
            f"{project_name} ({project_id})",
            metadata,
            style=style,
        )

        # Add children if any
        if project_id in child_projects:
            for child in child_projects[project_id]:
                add_project_to_tree(child_node, child)

    # Add root projects
    for project in root_projects:
        add_project_to_tree(builder.tree, project)

    return builder.tree


def create_enhanced_articles_tree(
    articles: List[Dict[str, Any]],
    show_metadata: bool = True,
    expand_all: bool = False,
) -> Tree:
    """Create an enhanced tree view of articles with metadata.

    Args:
        articles: List of article data
        show_metadata: Whether to show metadata (author, dates, etc.)
        expand_all: Whether to expand all nodes (placeholder for future feature)

    Returns:
        Rich Tree object with enhanced article display
    """
    builder = EnhancedTreeBuilder("📚 Articles")

    # Group articles by parent
    root_articles = []
    child_articles: Dict[str, List[Dict[str, Any]]] = {}

    for article in articles:
        parent_id = article.get("parentArticle", {}).get("id")
        if parent_id:
            if parent_id not in child_articles:
                child_articles[parent_id] = []
            child_articles[parent_id].append(article)
        else:
            root_articles.append(article)

    def add_article_to_tree(parent_node: Any, article: Dict[str, Any]) -> None:
        article_id = str(article.get("idReadable", article.get("id", "unknown")))
        title = str(article.get("summary", "Untitled"))

        metadata = {}

        if show_metadata:
            # Add author information
            author = article.get("reporter", {}).get("fullName")
            if author:
                metadata["Author"] = author

            # Add creation date
            created = article.get("created")
            if created:
                try:
                    # Format date nicely
                    date_obj = datetime.fromisoformat(created.replace("Z", "+00:00"))
                    metadata["Created"] = date_obj.strftime("%Y-%m-%d")
                except (ValueError, AttributeError):
                    metadata["Created"] = created

        # Determine visibility status and style
        visibility_info = article.get("visibility", {})
        visibility_type = visibility_info.get("$type", "")

        if visibility_type == "UnlimitedVisibility":
            style = "green"
            metadata["Visibility"] = "Public"
        elif visibility_type == "LimitedVisibility":
            style = "yellow"
            metadata["Visibility"] = "Limited"
        else:
            style = "dim white"
            metadata["Visibility"] = "Unknown"

        child_node = builder.add_node_with_metadata(
            parent_node,
            f"{title} ({article_id})",
            metadata,
            style=style,
        )

        # Add children if any
        if article_id in child_articles:
            for child in child_articles[article_id]:
                add_article_to_tree(child_node, child)

    # Add root articles
    for article in root_articles:
        add_article_to_tree(builder.tree, article)

    return builder.tree


def _add_dependency_node(
    builder: EnhancedTreeBuilder,
    parent_node: Any,
    dependency: Dict[str, Any],
    show_status: bool,
) -> None:
    """Helper function to add a dependency node to the tree."""
    target_issue = dependency.get("target", {})
    issue_id = target_issue.get("id", "Unknown")
    issue_summary = target_issue.get("summary", "No summary")

    metadata = {
        "Type": target_issue.get("type", {}).get("name"),
        "Priority": target_issue.get("priority", {}).get("name"),
    }

    if show_status:
        status = target_issue.get("state", {}).get("name", "Unknown")
        status_color = _get_status_color(status)
        builder.add_status_node(
            parent_node,
            f"{issue_id}: {issue_summary}",
            status,
            status_color,
            metadata,
        )
    else:
        builder.add_node_with_metadata(
            parent_node,
            f"{issue_id}: {issue_summary}",
            metadata,
        )


def _get_status_color(status: str) -> str:
    """Get color for issue status.

    Args:
        status: Issue status name

    Returns:
        Rich color string
    """
    status_lower = status.lower()

    if any(word in status_lower for word in ["open", "new", "to do", "backlog"]):
        return "blue"
    elif any(word in status_lower for word in ["in progress", "working", "active"]):
        return "yellow"
    elif any(word in status_lower for word in ["done", "resolved", "closed", "fixed"]):
        return "green"
    elif any(word in status_lower for word in ["blocked", "waiting", "on hold"]):
        return "red"
    else:
        return "white"
