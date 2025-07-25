"""Article management for YouTrack CLI."""

from datetime import datetime
from typing import Any, Optional

import httpx
from rich.table import Table
from rich.tree import Tree

from .auth import AuthManager
from .client import get_client_manager
from .console import get_console
from .pagination import create_paginated_display

__all__ = ["ArticleManager"]


class ArticleManager:
    """Manages YouTrack articles operations."""

    def __init__(self, auth_manager: AuthManager):
        self.auth_manager = auth_manager
        self.console = get_console()

    async def _resolve_project_id(self, project_identifier: str) -> str:
        """Resolve project short name to project ID."""
        credentials = self.auth_manager.load_credentials()
        if not credentials:
            raise ValueError("Not authenticated")

        # If it looks like an ID (contains hyphen), return as-is
        if "-" in project_identifier:
            return project_identifier

        # Otherwise, treat it as a short name and resolve to ID
        url = f"{credentials.base_url.rstrip('/')}/api/admin/projects"
        headers = {"Authorization": f"Bearer {credentials.token}"}
        params = {"fields": "id,shortName", "$top": "1000"}

        try:
            client_manager = get_client_manager()
            response = await client_manager.make_request("GET", url, headers=headers, params=params)
            projects_data = self._safe_json_parse(response)

            for project in projects_data:
                if project.get("shortName") == project_identifier:
                    return project.get("id")

            # If not found, raise an error
            raise ValueError(f"Project '{project_identifier}' not found")
        except Exception as e:
            raise ValueError(f"Failed to resolve project ID: {str(e)}") from e

    def _safe_json_parse(self, response: httpx.Response) -> Any:
        """Safely parse JSON response, handling empty or invalid JSON responses."""
        try:
            # Check if response has content
            if not response.text.strip():
                raise ValueError("Empty response body")

            # Check content type
            content_type = response.headers.get("content-type", "")
            if "application/json" not in content_type:
                # Check if response looks like HTML (login page)
                if "text/html" in content_type and "<!doctype html>" in response.text.lower():
                    raise ValueError(
                        "Received HTML login page instead of JSON. This usually indicates that the API endpoint "
                        "is not available or requires different authentication. The articles/knowledge base feature "
                        "might not be enabled in your YouTrack instance. Please check if the knowledge base feature "
                        "is enabled in your YouTrack administration settings."
                    )
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
        project_id: str,
        parent_id: Optional[str] = None,
        summary: Optional[str] = None,
        visibility: str = "public",
    ) -> dict[str, Any]:
        """Create a new article."""
        credentials = self.auth_manager.load_credentials()
        if not credentials:
            return {
                "status": "error",
                "message": "Not authenticated. Run 'yt auth login' first.",
            }

        try:
            # Resolve project short name to project ID
            resolved_project_id = await self._resolve_project_id(project_id)
        except ValueError as e:
            return {
                "status": "error",
                "message": str(e),
            }

        article_data = {
            "summary": title,
            "content": content,
            "project": {"id": resolved_project_id},
        }
        if parent_id:
            article_data["parentArticle"] = {"id": parent_id}
        if summary:
            article_data["summary"] = summary

        url = f"{credentials.base_url.rstrip('/')}/api/articles"
        headers = {
            "Authorization": f"Bearer {credentials.token}",
            "Content-Type": "application/json",
        }

        try:
            client_manager = get_client_manager()
            response = await client_manager.make_request("POST", url, headers=headers, json_data=article_data)
            data = self._safe_json_parse(response)
            return {
                "status": "success",
                "message": f"Article '{title}' created successfully",
                "data": data,
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def list_articles(
        self,
        project_id: Optional[str] = None,
        parent_id: Optional[str] = None,
        fields: Optional[str] = None,
        top: Optional[int] = None,
        query: Optional[str] = None,
        page_size: int = 100,
        after_cursor: Optional[str] = None,
        before_cursor: Optional[str] = None,
        use_pagination: bool = False,
        max_results: Optional[int] = None,
    ) -> dict[str, Any]:
        """List articles with optional filtering and pagination support.

        Args:
            project_id: Filter articles by project ID or short name
            parent_id: Filter articles by parent article ID
            fields: Comma-separated list of fields to return
            top: Maximum number of articles to return (legacy, use page_size instead)
            query: Search query to filter articles
            page_size: Number of articles per page
            after_cursor: Start pagination after this cursor
            before_cursor: Start pagination before this cursor
            use_pagination: Enable pagination for large result sets
            max_results: Maximum total number of results to fetch

        Returns:
            Dictionary with operation result including pagination metadata
        """
        from .utils import paginate_results  # Import here to avoid circular imports

        credentials = self.auth_manager.load_credentials()
        if not credentials:
            return {
                "status": "error",
                "message": "Not authenticated. Run 'yt auth login' first.",
            }

        # Handle legacy top parameter
        if top is not None:
            page_size = top
            use_pagination = False

        # Default fields to return if not specified
        if not fields:
            fields = (
                "id,idReadable,summary,content,created,updated,"
                "reporter(fullName),visibility(type),project(name,shortName),"
                "parentArticle(id,summary)"
            )

        params = {"fields": fields}
        # Remove the query-based parent filtering for now - we'll filter post-processing
        if query:
            params["query"] = query

        # Use project-specific endpoint when project_id is provided
        if project_id:
            endpoint = f"{credentials.base_url.rstrip('/')}/api/admin/projects/{project_id}/articles"
        else:
            endpoint = f"{credentials.base_url.rstrip('/')}/api/articles"
        headers = {
            "Authorization": f"Bearer {credentials.token}",
            "Accept": "application/json",
        }

        def filter_parent_articles(articles_data, target_parent_id):
            """Helper function to filter articles by parent ID."""
            if not target_parent_id or not isinstance(articles_data, list):
                return articles_data

            # First, try to get the parent article to determine its internal ID
            parent_internal_id = None

            # Check if parent_id is already an internal ID or if we can find it in the data
            for article in articles_data:
                if article.get("id") == target_parent_id or article.get("idReadable") == target_parent_id:
                    parent_internal_id = article.get("id")
                    break

            # Filter for articles that have the specified parent
            filtered_data = []
            for article in articles_data:
                parent_article = article.get("parentArticle")
                # Check if the article has the specified parent
                if parent_article and isinstance(parent_article, dict):
                    article_parent_id = parent_article.get("id")
                    # Match against both the provided parent_id and the resolved internal ID
                    if article_parent_id == target_parent_id or article_parent_id == parent_internal_id:
                        filtered_data.append(article)

            return filtered_data

        try:
            if use_pagination:
                # Use enhanced pagination with offset support
                result = await paginate_results(
                    endpoint=endpoint,
                    headers=headers,
                    params=params,
                    page_size=page_size,
                    max_results=max_results,
                    after_cursor=after_cursor,
                    before_cursor=before_cursor,
                    use_cursor_pagination=False,  # Articles use offset pagination
                )
                data = result["results"]

                # Handle case where API returns None or null
                if data is None:
                    data = []

                # Apply parent filtering if specified
                data = filter_parent_articles(data, parent_id)

                return {
                    "status": "success",
                    "data": data,
                    "count": len(data),
                    "pagination": {
                        "total_results": result["total_results"],
                        "has_after": result["has_after"],
                        "has_before": result["has_before"],
                        "after_cursor": result["after_cursor"],
                        "before_cursor": result["before_cursor"],
                        "pagination_type": result["pagination_type"],
                    },
                }
            else:
                # Legacy single request approach
                if top:
                    params["$top"] = str(top)

                client_manager = get_client_manager()
                response = await client_manager.make_request(
                    "GET",
                    endpoint,
                    headers=headers,
                    params=params,
                )

                data = self._safe_json_parse(response)
                # Handle case where API returns None or null
                if data is None:
                    data = []

                # Apply parent filtering if specified
                data = filter_parent_articles(data, parent_id)

                return {
                    "status": "success",
                    "data": data,
                    "count": len(data) if data is not None and isinstance(data, list) else 0,
                }
        except ValueError as e:
            # Handle JSON parsing errors specifically
            if "HTML login page" in str(e):
                return {"status": "error", "message": f"Authentication error: {str(e)}"}
            return {"status": "error", "message": f"Response parsing error: {str(e)}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def get_article(self, article_id: str, fields: Optional[str] = None) -> dict[str, Any]:  # noqa: E501
        """Get a specific article."""
        credentials = self.auth_manager.load_credentials()
        if not credentials:
            return {
                "status": "error",
                "message": "Not authenticated. Run 'yt auth login' first.",
            }

        # Default fields to return if not specified
        if not fields:
            fields = (
                "id,idReadable,summary,content,created,updated,"
                "reporter(fullName),visibility(type),project(name,shortName),"
                "parentArticle(id,summary)"
            )

        params = {"fields": fields}

        url = f"{credentials.base_url.rstrip('/')}/api/articles/{article_id}"
        headers = {
            "Authorization": f"Bearer {credentials.token}",
            "Accept": "application/json",
        }

        try:
            client_manager = get_client_manager()
            response = await client_manager.make_request("GET", url, headers=headers, params=params, timeout=10.0)
            data = self._safe_json_parse(response)
            return {"status": "success", "data": data}
        except Exception as e:
            return {"status": "error", "message": str(e)}

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
            return {
                "status": "error",
                "message": "Not authenticated. Run 'yt auth login' first.",
            }

        article_data: dict[str, Any] = {}
        if title:
            article_data["summary"] = title
        elif summary:
            article_data["summary"] = summary
        if content:
            article_data["content"] = content
        if visibility:
            if visibility.lower() in ["public", "unlimited"]:
                article_data["visibility"] = {"$type": "UnlimitedVisibility"}
            elif visibility.lower() in ["private", "limited"]:
                article_data["visibility"] = {"$type": "LimitedVisibility"}
            else:
                # Default to unlimited visibility if unknown value
                article_data["visibility"] = {"$type": "UnlimitedVisibility"}

        if not article_data:
            return {"status": "error", "message": "No update data provided"}

        url = f"{credentials.base_url.rstrip('/')}/api/articles/{article_id}"
        headers = {
            "Authorization": f"Bearer {credentials.token}",
            "Content-Type": "application/json",
        }

        try:
            client_manager = get_client_manager()
            response = await client_manager.make_request("POST", url, headers=headers, json_data=article_data)
            data = self._safe_json_parse(response)
            return {
                "status": "success",
                "message": "Article updated successfully",
                "data": data,
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def delete_article(self, article_id: str) -> dict[str, Any]:
        """Delete an article."""
        credentials = self.auth_manager.load_credentials()
        if not credentials:
            return {
                "status": "error",
                "message": "Not authenticated. Run 'yt auth login' first.",
            }

        url = f"{credentials.base_url.rstrip('/')}/api/articles/{article_id}"
        headers = {"Authorization": f"Bearer {credentials.token}"}

        try:
            client_manager = get_client_manager()
            await client_manager.make_request("DELETE", url, headers=headers)
            return {
                "status": "success",
                "message": "Article deleted successfully",
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def publish_article(self, article_id: str) -> dict[str, Any]:
        """Publish a draft article."""
        credentials = self.auth_manager.load_credentials()
        if not credentials:
            return {
                "status": "error",
                "message": "Not authenticated. Run 'yt auth login' first.",
            }

        # Use correct YouTrack visibility format
        article_data = {"visibility": {"$type": "UnlimitedVisibility"}}

        url = f"{credentials.base_url.rstrip('/')}/api/articles/{article_id}"
        headers = {
            "Authorization": f"Bearer {credentials.token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        try:
            client_manager = get_client_manager()
            response = await client_manager.make_request("POST", url, headers=headers, json_data=article_data)
            data = self._safe_json_parse(response)
            return {
                "status": "success",
                "message": "Article published successfully",
                "data": data,
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def search_articles(
        self,
        query: str,
        project_id: Optional[str] = None,
        top: Optional[int] = None,
    ) -> dict[str, Any]:
        """Search articles."""
        credentials = self.auth_manager.load_credentials()
        if not credentials:
            return {
                "status": "error",
                "message": "Not authenticated. Run 'yt auth login' first.",
            }

        params = {
            "query": query,
            "fields": (
                "id,idReadable,summary,content,created,updated,"
                "reporter(fullName),visibility(type),project(name,shortName)"
            ),
        }

        # Use project-specific endpoint when project_id is provided
        if project_id:
            endpoint = f"{credentials.base_url.rstrip('/')}/api/admin/projects/{project_id}/articles"
        else:
            endpoint = f"{credentials.base_url.rstrip('/')}/api/articles"
        headers = {
            "Authorization": f"Bearer {credentials.token}",
            "Accept": "application/json",
        }

        try:
            # Add $top parameter for API call
            if top:
                params["$top"] = str(top)

            client_manager = get_client_manager()
            response = await client_manager.make_request(
                "GET",
                endpoint,
                headers=headers,
                params=params,
            )

            data = self._safe_json_parse(response)
            # Handle case where API returns None or null
            if data is None:
                data = []
            return {
                "status": "success",
                "data": data,
                "count": len(data) if data is not None and isinstance(data, list) else 0,
            }
        except ValueError as e:
            # Handle JSON parsing errors specifically
            if "HTML login page" in str(e):
                return {"status": "error", "message": f"Authentication error: {str(e)}"}
            return {"status": "error", "message": f"Response parsing error: {str(e)}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def get_article_comments(self, article_id: str) -> dict[str, Any]:
        """Get comments for an article."""
        credentials = self.auth_manager.load_credentials()
        if not credentials:
            return {
                "status": "error",
                "message": "Not authenticated. Run 'yt auth login' first.",
            }

        url = f"{credentials.base_url.rstrip('/')}/api/articles/{article_id}/comments"
        headers = {"Authorization": f"Bearer {credentials.token}"}
        params = {"fields": "id,text,created,author(id,fullName)"}

        try:
            client_manager = get_client_manager()
            response = await client_manager.make_request("GET", url, headers=headers, params=params)
            data = self._safe_json_parse(response)
            return {"status": "success", "data": data}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def add_comment(self, article_id: str, text: str) -> dict[str, Any]:
        """Add a comment to an article."""
        credentials = self.auth_manager.load_credentials()
        if not credentials:
            return {
                "status": "error",
                "message": "Not authenticated. Run 'yt auth login' first.",
            }

        comment_data = {"text": text}

        url = f"{credentials.base_url.rstrip('/')}/api/articles/{article_id}/comments"
        headers = {
            "Authorization": f"Bearer {credentials.token}",
            "Content-Type": "application/json",
        }

        try:
            client_manager = get_client_manager()
            response = await client_manager.make_request("POST", url, headers=headers, json_data=comment_data)
            data = self._safe_json_parse(response)
            return {
                "status": "success",
                "message": "Comment added successfully",
                "data": data,
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def get_article_attachments(self, article_id: str) -> dict[str, Any]:
        """Get attachments for an article."""
        credentials = self.auth_manager.load_credentials()
        if not credentials:
            return {
                "status": "error",
                "message": "Not authenticated. Run 'yt auth login' first.",
            }

        url = f"{credentials.base_url.rstrip('/')}/api/articles/{article_id}/attachments"
        headers = {"Authorization": f"Bearer {credentials.token}"}
        params = {"fields": "id,name,size,mimeType,author(id,fullName)"}

        try:
            client_manager = get_client_manager()
            response = await client_manager.make_request("GET", url, headers=headers, params=params)
            data = self._safe_json_parse(response)
            return {"status": "success", "data": data}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def upload_attachment(self, article_id: str, file_path: str) -> dict[str, Any]:
        """Upload an attachment to an article."""
        credentials = self.auth_manager.load_credentials()
        if not credentials:
            return {
                "status": "error",
                "message": "Not authenticated. Run 'yt auth login' first.",
            }

        url = f"{credentials.base_url.rstrip('/')}/api/articles/{article_id}/attachments"
        headers = {"Authorization": f"Bearer {credentials.token}"}

        try:
            with open(file_path, "rb") as file:
                files = {"file": file}
                client_manager = get_client_manager()
                async with client_manager.get_client() as client:
                    response = await client.post(url, files=files, headers=headers)
                    if response.status_code == 200:
                        return {
                            "status": "success",
                            "message": f"File '{file_path}' uploaded to article '{article_id}' successfully",
                        }
                    error_text = response.text
                    return {
                        "status": "error",
                        "message": f"Failed to upload attachment: {error_text}",
                    }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error uploading attachment: {str(e)}",
            }

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
            # Get the content field and create a truncated version for summary display
            content = article.get("content", "")
            if content:
                summary_text = content[:50] + "..." if len(content) > 50 else content
            else:
                # If no content, show "No Summary Available"
                summary_text = "No Summary Available"

            # Get author info (using reporter field for articles)
            author_info = article.get("reporter", {})
            if author_info and isinstance(author_info, dict):
                author_name = author_info.get("fullName", "Unknown Author")
            else:
                author_name = "Unknown Author"

            # Map visibility type to user-friendly name
            visibility_info = article.get("visibility", {})
            if visibility_info and isinstance(visibility_info, dict):
                visibility_type = visibility_info.get("$type", "")
            else:
                visibility_type = ""
            if visibility_type == "UnlimitedVisibility":
                visibility_display = "Visible"
            elif visibility_type == "LimitedVisibility":
                visibility_display = "Hidden"
            else:
                visibility_display = "Unknown"

            # Format the created timestamp
            created_timestamp = article.get("created")
            if created_timestamp:
                try:
                    # Handle both numeric timestamps (from API) and string timestamps (from tests)
                    if isinstance(created_timestamp, (int, float)):
                        created_date = datetime.fromtimestamp(created_timestamp / 1000).strftime("%Y-%m-%d %H:%M")
                    else:
                        # For string timestamps, just use as-is (test data)
                        created_date = str(created_timestamp)
                except (ValueError, TypeError):
                    created_date = str(created_timestamp)
            else:
                created_date = "N/A"

            table.add_row(
                str(article.get("idReadable", article.get("id", "N/A"))),  # Use friendly ID first
                str(article.get("summary", "N/A")),
                str(summary_text),
                str(author_name),
                str(created_date),
                str(visibility_display),
            )

        self.console.print(table)

    def display_articles_table_paginated(
        self, articles: list[dict[str, Any]], page_size: int = 50, show_all: bool = False, start_page: int = 1
    ) -> None:
        """Display articles in a paginated table format.

        Args:
            articles: List of article dictionaries
            page_size: Number of articles per page (default: 50)
            show_all: If True, display all articles without pagination
            start_page: Page number to start displaying from
        """
        if not articles:
            self.console.print("No articles found.", style="yellow")
            return

        def build_articles_table(article_subset: list[dict[str, Any]]) -> Table:
            """Build a Rich table for the given subset of articles."""
            table = Table(title="Articles")
            table.add_column("ID", style="cyan")
            table.add_column("Title", style="green")
            table.add_column("Summary", style="blue")
            table.add_column("Author", style="magenta")
            table.add_column("Created", style="yellow")
            table.add_column("Visibility", style="red")

            for article in article_subset:
                # Get the content field and create a truncated version for summary display
                content = article.get("content", "")
                if content:
                    summary_text = content[:50] + "..." if len(content) > 50 else content
                else:
                    # If no content, show "No Summary Available"
                    summary_text = "No Summary Available"

                # Get author info (using reporter field for articles)
                author_info = article.get("reporter", {})
                if author_info and isinstance(author_info, dict):
                    author_name = author_info.get("fullName", "Unknown Author")
                else:
                    author_name = "Unknown Author"

                # Map visibility type to user-friendly name
                visibility_info = article.get("visibility", {})
                visibility_type = visibility_info.get("$type", "")
                if visibility_type == "UnlimitedVisibility":
                    visibility_display = "Visible"
                elif visibility_type == "LimitedVisibility":
                    visibility_display = "Hidden"
                else:
                    visibility_display = "Unknown"

                # Format the created timestamp
                created_timestamp = article.get("created")
                if created_timestamp:
                    try:
                        # Handle both numeric timestamps (from API) and string timestamps (from tests)
                        if isinstance(created_timestamp, (int, float)):
                            created_date = datetime.fromtimestamp(created_timestamp / 1000).strftime("%Y-%m-%d %H:%M")
                        else:
                            # For string timestamps, just use as-is (test data)
                            created_date = str(created_timestamp)
                    except (ValueError, TypeError):
                        created_date = str(created_timestamp)
                else:
                    created_date = "N/A"

                table.add_row(
                    str(article.get("idReadable", article.get("id", "N/A"))),  # Use friendly ID first
                    str(article.get("summary", "N/A")),
                    str(summary_text),
                    str(author_name),
                    str(created_date),
                    str(visibility_display),
                )

            return table

        # Use pagination display
        paginated_display = create_paginated_display(self.console, page_size)
        paginated_display.display_paginated_table(
            articles, build_articles_table, "Articles", show_all=show_all, start_page=start_page
        )

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
            parent_article = article.get("parentArticle")
            parent_id = parent_article.get("id") if parent_article else None
            if parent_id:
                if parent_id not in child_articles:
                    child_articles[parent_id] = []
                child_articles[parent_id].append(article)
            else:
                root_articles.append(article)

        def add_article_to_tree(parent_node: Any, article: dict[str, Any]) -> None:
            # Use internal ID for parent-child matching (consistent with child_articles dict keys)
            internal_id = str(article.get("id", "unknown"))
            # Use readable ID for display purposes
            display_id = str(article.get("idReadable", internal_id))
            title = str(article.get("summary", "Untitled"))

            # Map visibility type to user-friendly name
            visibility_info = article.get("visibility", {})
            if visibility_info and isinstance(visibility_info, dict):
                visibility_type = visibility_info.get("$type", "")
            else:
                visibility_type = ""
            if visibility_type == "UnlimitedVisibility":
                visibility_display = "Visible"
            elif visibility_type == "LimitedVisibility":
                visibility_display = "Hidden"
            else:
                visibility_display = "Unknown"

            node_text = f"[green]{title}[/green] [dim]({display_id})[/dim] [yellow]({visibility_display})[/yellow]"  # noqa: E501
            child_node = parent_node.add(node_text)

            # Add children if any (use internal ID for matching)
            if internal_id and internal_id in child_articles:
                for child in child_articles[internal_id]:
                    add_article_to_tree(child_node, child)

        # Add root articles
        for article in root_articles:
            add_article_to_tree(tree, article)

        self.console.print(tree)

    def display_article_details(self, article: dict[str, Any]) -> None:
        """Display detailed information about an article."""
        self.console.print("\n[bold blue]Article Details[/bold blue]")
        self.console.print(f"ID: {article.get('idReadable', article.get('id', 'N/A'))}")
        self.console.print(f"Title: {article.get('summary', 'N/A')}")
        self.console.print(f"Author: {article.get('reporter', {}).get('fullName', 'N/A')}")  # noqa: E501

        # Format timestamps
        created_timestamp = article.get("created")
        if created_timestamp:
            try:
                # Handle both numeric timestamps (from API) and string timestamps (from tests)
                if isinstance(created_timestamp, (int, float)):
                    created_date = datetime.fromtimestamp(created_timestamp / 1000).strftime("%Y-%m-%d %H:%M:%S")
                else:
                    # For string timestamps, just use as-is (test data)
                    created_date = str(created_timestamp)
            except (ValueError, TypeError):
                created_date = str(created_timestamp)
        else:
            created_date = "N/A"

        updated_timestamp = article.get("updated")
        if updated_timestamp:
            try:
                # Handle both numeric timestamps (from API) and string timestamps (from tests)
                if isinstance(updated_timestamp, (int, float)):
                    updated_date = datetime.fromtimestamp(updated_timestamp / 1000).strftime("%Y-%m-%d %H:%M:%S")
                else:
                    # For string timestamps, just use as-is (test data)
                    updated_date = str(updated_timestamp)
            except (ValueError, TypeError):
                updated_date = str(updated_timestamp)
        else:
            updated_date = "N/A"

        self.console.print(f"Created: {created_date}")
        self.console.print(f"Updated: {updated_date}")
        # Map visibility type to user-friendly name
        visibility_info = article.get("visibility", {})
        visibility_type = visibility_info.get("$type", "")
        if visibility_type == "UnlimitedVisibility":
            visibility_display = "Visible"
        elif visibility_type == "LimitedVisibility":
            visibility_display = "Hidden"
        else:
            visibility_display = "Unknown"
        self.console.print(f"Visibility: {visibility_display}")

        if article.get("project"):
            self.console.print(f"Project: {article.get('project', {}).get('name', 'N/A')}")  # noqa: E501

        if article.get("parentArticle"):
            self.console.print(f"Parent: {article.get('parentArticle', {}).get('summary', 'N/A')}")  # noqa: E501

        self.console.print("\n[bold]Content:[/bold]")
        self.console.print(article.get("content", "No content available"))

    async def get_available_tags(self) -> dict[str, Any]:
        """Get all available tags that can be used to tag articles."""
        credentials = self.auth_manager.load_credentials()
        if not credentials:
            return {
                "status": "error",
                "message": "Not authenticated. Run 'yt auth login' first.",
            }

        # Specify fields to retrieve for tags
        fields = "id,name,owner(login,fullName),visibleFor(name,id),color"
        params = {"fields": fields}

        url = f"{credentials.base_url.rstrip('/')}/api/tags"
        headers = {"Authorization": f"Bearer {credentials.token}"}

        try:
            client_manager = get_client_manager()
            response = await client_manager.make_request("GET", url, headers=headers, params=params)
            data = self._safe_json_parse(response)
            return {"status": "success", "data": data}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def get_article_tags(self, article_id: str) -> dict[str, Any]:
        """Get current tags for a specific article."""
        credentials = self.auth_manager.load_credentials()
        if not credentials:
            return {
                "status": "error",
                "message": "Not authenticated. Run 'yt auth login' first.",
            }

        # Specify fields to retrieve for tags
        fields = "id,name,owner(login,fullName),visibleFor(name,id),color"
        params = {"fields": fields}

        url = f"{credentials.base_url.rstrip('/')}/api/articles/{article_id}/tags"
        headers = {"Authorization": f"Bearer {credentials.token}"}

        try:
            client_manager = get_client_manager()
            response = await client_manager.make_request("GET", url, headers=headers, params=params)
            data = self._safe_json_parse(response)
            return {"status": "success", "data": data}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def add_tags_to_article(self, article_id: str, tag_ids: list[str]) -> dict[str, Any]:
        """Add one or more tags to an article."""
        credentials = self.auth_manager.load_credentials()
        if not credentials:
            return {
                "status": "error",
                "message": "Not authenticated. Run 'yt auth login' first.",
            }

        url = f"{credentials.base_url.rstrip('/')}/api/articles/{article_id}/tags"
        headers = {
            "Authorization": f"Bearer {credentials.token}",
            "Content-Type": "application/json",
        }

        # Add tags one by one as the API expects individual tag additions
        results = []
        for tag_id in tag_ids:
            tag_data = {"id": tag_id}
            try:
                client_manager = get_client_manager()
                response = await client_manager.make_request("POST", url, headers=headers, json_data=tag_data)
                data = self._safe_json_parse(response)
                results.append({"tag_id": tag_id, "status": "success", "data": data})
            except Exception as e:
                results.append({"tag_id": tag_id, "status": "error", "message": str(e)})

        # Check if all tags were added successfully
        success_count = sum(1 for r in results if r["status"] == "success")
        if success_count == len(tag_ids):
            return {
                "status": "success",
                "message": f"Successfully added {success_count} tags to article {article_id}",
                "data": results,
            }
        error_count = len(tag_ids) - success_count
        return {
            "status": "partial",
            "message": f"Added {success_count} tags, failed to add {error_count} tags to article {article_id}",
            "data": results,
        }

    async def remove_tags_from_article(self, article_id: str, tag_ids: list[str]) -> dict[str, Any]:
        """Remove one or more tags from an article."""
        credentials = self.auth_manager.load_credentials()
        if not credentials:
            return {
                "status": "error",
                "message": "Not authenticated. Run 'yt auth login' first.",
            }

        # Remove tags one by one
        results = []
        for tag_id in tag_ids:
            url = f"{credentials.base_url.rstrip('/')}/api/articles/{article_id}/tags/{tag_id}"
            headers = {"Authorization": f"Bearer {credentials.token}"}

            try:
                client_manager = get_client_manager()
                await client_manager.make_request("DELETE", url, headers=headers)
                results.append({"tag_id": tag_id, "status": "success"})
            except Exception as e:
                results.append({"tag_id": tag_id, "status": "error", "message": str(e)})

        # Check if all tags were removed successfully
        success_count = sum(1 for r in results if r["status"] == "success")
        if success_count == len(tag_ids):
            return {
                "status": "success",
                "message": f"Successfully removed {success_count} tags from article {article_id}",
                "data": results,
            }
        error_count = len(tag_ids) - success_count
        return {
            "status": "partial",
            "message": f"Removed {success_count} tags, failed to remove {error_count} tags from article {article_id}",  # noqa: E501
            "data": results,
        }
