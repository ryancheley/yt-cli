"""Article management for YouTrack CLI."""

from typing import Any, Optional

import httpx
from rich.console import Console
from rich.table import Table
from rich.tree import Tree

from .auth import AuthManager
from .client import get_client_manager

__all__ = ["ArticleManager"]


class ArticleManager:
    """Manages YouTrack articles operations."""

    def __init__(self, auth_manager: AuthManager):
        self.auth_manager = auth_manager
        self.console = Console()

    def _parse_json_response(self, response: httpx.Response) -> Any:
        """Safely parse JSON response, handling empty or non-JSON responses."""
        try:
            content_type = response.headers.get("content-type", "")
            if not response.text:
                raise ValueError("Empty response body")

            if "application/json" not in content_type:
                raise ValueError(f"Response is not JSON. Content-Type: {content_type}")

            return response.json()
        except Exception as e:
            # Try to provide more context about the error
            status_code = response.status_code
            preview = response.text[:200] if response.text else "empty"
            raise ValueError(
                f"Failed to parse JSON response (status {status_code}): {str(e)}. Response preview: {preview}"
            ) from e

    async def create_article(
        self,
        title: str,
        content: str,
        project_id: Optional[str] = None,
        parent_id: Optional[str] = None,
        summary: Optional[str] = None,
        visibility: str = "public",
    ) -> dict[str, Any]:
        """Create a new article."""
        credentials = self.auth_manager.load_credentials()
        if not credentials:
            return {"status": "error", "message": "Not authenticated"}

        article_data = {
            "summary": title,
            "content": content,
            "visibility": {"type": visibility},
        }

        if project_id:
            article_data["project"] = {"id": project_id}
        if parent_id:
            article_data["parentArticle"] = {"id": parent_id}
        if summary:
            article_data["summary"] = summary

        url = f"{credentials.base_url}/api/articles"
        headers = {
            "Authorization": f"Bearer {credentials.token}",
            "Content-Type": "application/json",
        }

        try:
            client_manager = get_client_manager()
            response = await client_manager.make_request("POST", url, headers=headers, json_data=article_data)
            if response.status_code == 200:
                data = self._parse_json_response(response)
                return {
                    "status": "success",
                    "message": f"Article '{title}' created successfully",
                    "data": data,
                }
            else:
                error_text = response.text
                return {
                    "status": "error",
                    "message": f"Failed to create article: {error_text}",
                }
        except Exception as e:
            return {"status": "error", "message": f"Error creating article: {str(e)}"}

    async def list_articles(
        self,
        project_id: Optional[str] = None,
        parent_id: Optional[str] = None,
        fields: Optional[str] = None,
        top: Optional[int] = None,
        query: Optional[str] = None,
    ) -> dict[str, Any]:
        """List articles with optional filtering."""
        credentials = self.auth_manager.load_credentials()
        if not credentials:
            return {"status": "error", "message": "Not authenticated"}

        params = {}
        if fields:
            params["fields"] = fields
        if top:
            params["$top"] = str(top)
        if project_id:
            params["project"] = project_id
        if parent_id:
            params["parentArticle"] = parent_id
        if query:
            params["query"] = query

        url = f"{credentials.base_url}/api/articles"
        headers = {"Authorization": f"Bearer {credentials.token}"}

        try:
            client_manager = get_client_manager()
            response = await client_manager.make_request("GET", url, headers=headers, params=params)
            if response.status_code == 200:
                data = self._parse_json_response(response)
                return {
                    "status": "success",
                    "data": data,
                    "count": len(data) if isinstance(data, list) else 1,
                }
            else:
                error_text = response.text
                return {
                    "status": "error",
                    "message": f"Failed to list articles: {error_text}",
                }
        except Exception as e:
            return {"status": "error", "message": f"Error listing articles: {str(e)}"}

    async def get_article(self, article_id: str, fields: Optional[str] = None) -> dict[str, Any]:  # noqa: E501
        """Get a specific article."""
        credentials = self.auth_manager.load_credentials()
        if not credentials:
            return {"status": "error", "message": "Not authenticated"}

        params = {}
        if fields:
            params["fields"] = fields

        url = f"{credentials.base_url}/api/articles/{article_id}"
        headers = {"Authorization": f"Bearer {credentials.token}"}

        try:
            client_manager = get_client_manager()
            response = await client_manager.make_request("GET", url, headers=headers, params=params)
            if response.status_code == 200:
                data = self._parse_json_response(response)
                return {"status": "success", "data": data}
            else:
                error_text = response.text
                return {
                    "status": "error",
                    "message": f"Failed to get article: {error_text}",
                }
        except Exception as e:
            return {"status": "error", "message": f"Error getting article: {str(e)}"}

    async def update_article(
        self,
        article_id: str,
        title: Optional[str] = None,
        content: Optional[str] = None,
        summary: Optional[str] = None,
        visibility: Optional[str] = None,
    ) -> dict[str, Any]:
        """Update an existing article."""
        credentials = self.auth_manager.load_credentials()
        if not credentials:
            return {"status": "error", "message": "Not authenticated"}

        article_data: dict[str, Any] = {}
        if title:
            article_data["summary"] = title
        elif summary:
            article_data["summary"] = summary
        if content:
            article_data["content"] = content
        if visibility:
            article_data["visibility"] = {"type": visibility}

        if not article_data:
            return {"status": "error", "message": "No update data provided"}

        url = f"{credentials.base_url}/api/articles/{article_id}"
        headers = {
            "Authorization": f"Bearer {credentials.token}",
            "Content-Type": "application/json",
        }

        try:
            client_manager = get_client_manager()
            response = await client_manager.make_request("POST", url, headers=headers, json_data=article_data)
            if response.status_code == 200:
                data = self._parse_json_response(response)
                return {
                    "status": "success",
                    "message": "Article updated successfully",
                    "data": data,
                }
            else:
                error_text = response.text
                return {
                    "status": "error",
                    "message": f"Failed to update article: {error_text}",
                }
        except Exception as e:
            return {"status": "error", "message": f"Error updating article: {str(e)}"}

    async def delete_article(self, article_id: str) -> dict[str, Any]:
        """Delete an article."""
        credentials = self.auth_manager.load_credentials()
        if not credentials:
            return {"status": "error", "message": "Not authenticated"}

        url = f"{credentials.base_url}/api/articles/{article_id}"
        headers = {"Authorization": f"Bearer {credentials.token}"}

        try:
            client_manager = get_client_manager()
            response = await client_manager.make_request("DELETE", url, headers=headers)
            if response.status_code == 200:
                return {
                    "status": "success",
                    "message": "Article deleted successfully",
                }
            else:
                error_text = response.text
                return {
                    "status": "error",
                    "message": f"Failed to delete article: {error_text}",
                }
        except Exception as e:
            return {"status": "error", "message": f"Error deleting article: {str(e)}"}

    async def publish_article(self, article_id: str) -> dict[str, Any]:
        """Publish a draft article."""
        credentials = self.auth_manager.load_credentials()
        if not credentials:
            return {"status": "error", "message": "Not authenticated"}

        article_data = {"visibility": {"type": "public"}}

        url = f"{credentials.base_url}/api/articles/{article_id}"
        headers = {
            "Authorization": f"Bearer {credentials.token}",
            "Content-Type": "application/json",
        }

        try:
            client_manager = get_client_manager()
            response = await client_manager.make_request("POST", url, headers=headers, json_data=article_data)
            if response.status_code == 200:
                data = self._parse_json_response(response)
                return {
                    "status": "success",
                    "message": "Article published successfully",
                    "data": data,
                }
            else:
                error_text = response.text
                return {
                    "status": "error",
                    "message": f"Failed to publish article: {error_text}",
                }
        except Exception as e:
            return {"status": "error", "message": f"Error publishing article: {str(e)}"}

    async def search_articles(
        self,
        query: str,
        project_id: Optional[str] = None,
        top: Optional[int] = None,
    ) -> dict[str, Any]:
        """Search articles."""
        credentials = self.auth_manager.load_credentials()
        if not credentials:
            return {"status": "error", "message": "Not authenticated"}

        params = {"query": query}
        if project_id:
            params["project"] = project_id
        if top:
            params["$top"] = str(top)

        url = f"{credentials.base_url}/api/articles"
        headers = {"Authorization": f"Bearer {credentials.token}"}

        try:
            client_manager = get_client_manager()
            response = await client_manager.make_request("GET", url, headers=headers, params=params)
            if response.status_code == 200:
                data = self._parse_json_response(response)
                return {
                    "status": "success",
                    "data": data,
                    "count": len(data) if isinstance(data, list) else 1,
                }
            else:
                error_text = response.text
                return {
                    "status": "error",
                    "message": f"Failed to search articles: {error_text}",
                }
        except Exception as e:
            return {"status": "error", "message": f"Error searching articles: {str(e)}"}

    async def get_article_comments(self, article_id: str) -> dict[str, Any]:
        """Get comments for an article."""
        credentials = self.auth_manager.load_credentials()
        if not credentials:
            return {"status": "error", "message": "Not authenticated"}

        url = f"{credentials.base_url}/api/articles/{article_id}/comments"
        headers = {"Authorization": f"Bearer {credentials.token}"}

        try:
            client_manager = get_client_manager()
            response = await client_manager.make_request("GET", url, headers=headers)
            if response.status_code == 200:
                data = self._parse_json_response(response)
                return {"status": "success", "data": data}
            else:
                error_text = response.text
                return {
                    "status": "error",
                    "message": f"Failed to get comments: {error_text}",
                }
        except Exception as e:
            return {"status": "error", "message": f"Error getting comments: {str(e)}"}

    async def add_comment(self, article_id: str, text: str) -> dict[str, Any]:
        """Add a comment to an article."""
        credentials = self.auth_manager.load_credentials()
        if not credentials:
            return {"status": "error", "message": "Not authenticated"}

        comment_data = {"text": text}

        url = f"{credentials.base_url}/api/articles/{article_id}/comments"
        headers = {
            "Authorization": f"Bearer {credentials.token}",
            "Content-Type": "application/json",
        }

        try:
            client_manager = get_client_manager()
            response = await client_manager.make_request("POST", url, headers=headers, json_data=comment_data)
            if response.status_code == 200:
                data = self._parse_json_response(response)
                return {
                    "status": "success",
                    "message": "Comment added successfully",
                    "data": data,
                }
            else:
                error_text = response.text
                return {
                    "status": "error",
                    "message": f"Failed to add comment: {error_text}",
                }
        except Exception as e:
            return {"status": "error", "message": f"Error adding comment: {str(e)}"}

    async def get_article_attachments(self, article_id: str) -> dict[str, Any]:
        """Get attachments for an article."""
        credentials = self.auth_manager.load_credentials()
        if not credentials:
            return {"status": "error", "message": "Not authenticated"}

        url = f"{credentials.base_url}/api/articles/{article_id}/attachments"
        headers = {"Authorization": f"Bearer {credentials.token}"}

        try:
            client_manager = get_client_manager()
            response = await client_manager.make_request("GET", url, headers=headers)
            if response.status_code == 200:
                data = self._parse_json_response(response)
                return {"status": "success", "data": data}
            else:
                error_text = response.text
                return {
                    "status": "error",
                    "message": f"Failed to get attachments: {error_text}",
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error getting attachments: {str(e)}",
            }  # noqa: E501

    def display_articles_table(self, articles: list[dict[str, Any]]) -> None:
        """Display articles in a table format."""
        if not articles:
            self.console.print("No articles found.", style="yellow")
            return

        table = Table(title="Articles")
        table.add_column("ID", style="cyan")
        table.add_column("Title", style="green")
        table.add_column("Summary", style="blue")
        table.add_column("Author", style="magenta")
        table.add_column("Created", style="yellow")
        table.add_column("Visibility", style="red")

        for article in articles:
            content = article.get("content", "N/A")
            summary_text = content[:50] + "..." if len(content) > 50 else content

            table.add_row(
                article.get("id", "N/A"),
                article.get("summary", "N/A"),
                summary_text,
                article.get("author", {}).get("fullName", "N/A"),
                article.get("created", "N/A"),
                article.get("visibility", {}).get("type", "N/A"),
            )

        self.console.print(table)

    def display_articles_tree(self, articles: list[dict[str, Any]]) -> None:
        """Display articles in a tree format."""
        if not articles:
            self.console.print("No articles found.", style="yellow")
            return

        tree = Tree("📚 Articles")

        # Group articles by parent
        root_articles = []
        child_articles: dict[str, list[dict[str, Any]]] = {}

        for article in articles:
            parent_id = article.get("parentArticle", {}).get("id")
            if parent_id:
                if parent_id not in child_articles:
                    child_articles[parent_id] = []
                child_articles[parent_id].append(article)
            else:
                root_articles.append(article)

        def add_article_to_tree(parent_node: Any, article: dict[str, Any]) -> None:
            article_id = article.get("id")
            title = article.get("summary", "Untitled")
            visibility = article.get("visibility", {}).get("type", "unknown")

            node_text = f"[green]{title}[/green] [dim]({article_id})[/dim] [yellow]({visibility})[/yellow]"  # noqa: E501
            child_node = parent_node.add(node_text)

            # Add children if any
            if article_id and article_id in child_articles:
                for child in child_articles[article_id]:
                    add_article_to_tree(child_node, child)

        # Add root articles
        for article in root_articles:
            add_article_to_tree(tree, article)

        self.console.print(tree)

    def display_article_details(self, article: dict[str, Any]) -> None:
        """Display detailed information about an article."""
        self.console.print("\n[bold blue]Article Details[/bold blue]")
        self.console.print(f"ID: {article.get('id', 'N/A')}")
        self.console.print(f"Title: {article.get('summary', 'N/A')}")
        self.console.print(f"Author: {article.get('author', {}).get('fullName', 'N/A')}")  # noqa: E501
        self.console.print(f"Created: {article.get('created', 'N/A')}")
        self.console.print(f"Updated: {article.get('updated', 'N/A')}")
        self.console.print(f"Visibility: {article.get('visibility', {}).get('type', 'N/A')}")  # noqa: E501

        if article.get("project"):
            self.console.print(f"Project: {article.get('project', {}).get('name', 'N/A')}")  # noqa: E501

        if article.get("parentArticle"):
            self.console.print(f"Parent: {article.get('parentArticle', {}).get('summary', 'N/A')}")  # noqa: E501

        self.console.print("\n[bold]Content:[/bold]")
        self.console.print(article.get("content", "No content available"))
