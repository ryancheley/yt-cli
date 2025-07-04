"""Tests for article management functionality."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from click.testing import CliRunner

from youtrack_cli.articles import ArticleManager
from youtrack_cli.auth import AuthConfig, AuthManager


@pytest.fixture
def mock_credentials():
    """Mock credentials for testing."""
    return AuthConfig(
        base_url="https://test.youtrack.cloud",
        token="test-token",
        username="test-user",
    )


@pytest.fixture
def mock_auth_manager(mock_credentials):
    """Mock auth manager for testing."""
    auth_manager = MagicMock(spec=AuthManager)
    auth_manager.load_credentials.return_value = mock_credentials
    return auth_manager


@pytest.fixture
def article_manager(mock_auth_manager):
    """Article manager instance for testing."""
    return ArticleManager(mock_auth_manager)


class TestArticleManager:
    """Test cases for ArticleManager class."""

    @pytest.mark.asyncio
    async def test_create_article_success(self, article_manager):
        """Test successful article creation."""
        mock_response = {
            "id": "123",
            "summary": "Test Article",
            "content": "Test content",
        }

        with patch("httpx.AsyncClient") as mock_client:
            mock_resp = AsyncMock()
            mock_resp.status_code = 200
            mock_resp.json = lambda: mock_response
            mock_resp.raise_for_status.return_value = None
            mock_client.return_value.__aenter__.return_value.post.return_value = (
                mock_resp  # noqa: E501
            )

            result = await article_manager.create_article(
                title="Test Article",
                content="Test content",
            )

            assert result["status"] == "success"
            assert "Test Article" in result["message"]
            assert result["data"] == mock_response

    @pytest.mark.asyncio
    async def test_create_article_failure(self, article_manager):
        """Test article creation failure."""
        with patch("httpx.AsyncClient") as mock_client:
            mock_resp = AsyncMock()
            mock_resp.status_code = 400
            mock_resp.text.return_value = "Bad Request"
            mock_client.return_value.__aenter__.return_value.post.return_value = (
                mock_resp  # noqa: E501
            )

            result = await article_manager.create_article(
                title="Test Article",
                content="Test content",
            )

            assert result["status"] == "error"
            assert "Failed to create article" in result["message"]

    @pytest.mark.asyncio
    async def test_list_articles_success(self, article_manager):
        """Test successful article listing."""
        mock_response = [
            {
                "id": "123",
                "summary": "Article 1",
                "content": "Content 1",
            },
            {
                "id": "124",
                "summary": "Article 2",
                "content": "Content 2",
            },
        ]

        with patch("httpx.AsyncClient") as mock_client:
            mock_resp = AsyncMock()
            mock_resp.status_code = 200
            mock_resp.json = lambda: mock_response
            mock_resp.raise_for_status.return_value = None
            mock_client.return_value.__aenter__.return_value.get.return_value = (
                mock_resp  # noqa: E501
            )

            result = await article_manager.list_articles()

            assert result["status"] == "success"
            assert result["data"] == mock_response
            assert result["count"] == 2

    @pytest.mark.asyncio
    async def test_get_article_success(self, article_manager):
        """Test successful article retrieval."""
        mock_response = {
            "id": "123",
            "summary": "Test Article",
            "content": "Test content",
        }

        with patch("httpx.AsyncClient") as mock_client:
            mock_resp = AsyncMock()
            mock_resp.status_code = 200
            mock_resp.json = lambda: mock_response
            mock_resp.raise_for_status.return_value = None
            mock_client.return_value.__aenter__.return_value.get.return_value = (
                mock_resp  # noqa: E501
            )

            result = await article_manager.get_article("123")

            assert result["status"] == "success"
            assert result["data"] == mock_response

    @pytest.mark.asyncio
    async def test_update_article_success(self, article_manager):
        """Test successful article update."""
        mock_response = {
            "id": "123",
            "summary": "Updated Article",
            "content": "Updated content",
        }

        with patch("httpx.AsyncClient") as mock_client:
            mock_resp = AsyncMock()
            mock_resp.status_code = 200
            mock_resp.json = lambda: mock_response
            mock_resp.raise_for_status.return_value = None
            mock_client.return_value.__aenter__.return_value.post.return_value = (
                mock_resp  # noqa: E501
            )

            result = await article_manager.update_article(
                article_id="123",
                title="Updated Article",
                content="Updated content",
            )

            assert result["status"] == "success"
            assert "updated successfully" in result["message"]
            assert result["data"] == mock_response

    @pytest.mark.asyncio
    async def test_update_article_no_data(self, article_manager):
        """Test article update with no data provided."""
        result = await article_manager.update_article(article_id="123")

        assert result["status"] == "error"
        assert "No update data provided" in result["message"]

    @pytest.mark.asyncio
    async def test_delete_article_success(self, article_manager):
        """Test successful article deletion."""
        with patch("httpx.AsyncClient") as mock_client:
            mock_resp = AsyncMock()
            mock_resp.status_code = 200
            mock_resp.raise_for_status.return_value = None
            mock_client.return_value.__aenter__.return_value.delete.return_value = (
                mock_resp  # noqa: E501
            )

            result = await article_manager.delete_article("123")

            assert result["status"] == "success"
            assert "deleted successfully" in result["message"]

    @pytest.mark.asyncio
    async def test_publish_article_success(self, article_manager):
        """Test successful article publishing."""
        mock_response = {
            "id": "123",
            "summary": "Published Article",
            "visibility": {"type": "public"},
        }

        with patch("httpx.AsyncClient") as mock_client:
            mock_resp = AsyncMock()
            mock_resp.status_code = 200
            mock_resp.json = lambda: mock_response
            mock_resp.raise_for_status.return_value = None
            mock_client.return_value.__aenter__.return_value.post.return_value = (
                mock_resp  # noqa: E501
            )

            result = await article_manager.publish_article("123")

            assert result["status"] == "success"
            assert "published successfully" in result["message"]
            assert result["data"] == mock_response

    @pytest.mark.asyncio
    async def test_search_articles_success(self, article_manager):
        """Test successful article search."""
        mock_response = [
            {
                "id": "123",
                "summary": "Found Article",
                "content": "Search content",
            }
        ]

        with patch("httpx.AsyncClient") as mock_client:
            mock_resp = AsyncMock()
            mock_resp.status_code = 200
            mock_resp.json = lambda: mock_response
            mock_resp.raise_for_status.return_value = None
            mock_client.return_value.__aenter__.return_value.get.return_value = (
                mock_resp  # noqa: E501
            )

            result = await article_manager.search_articles("search query")

            assert result["status"] == "success"
            assert result["data"] == mock_response
            assert result["count"] == 1

    @pytest.mark.asyncio
    async def test_get_article_comments_success(self, article_manager):
        """Test successful article comments retrieval."""
        mock_response = [
            {
                "id": "comment-1",
                "text": "Test comment",
                "author": {"fullName": "Test User"},
            }
        ]

        with patch("httpx.AsyncClient") as mock_client:
            mock_resp = AsyncMock()
            mock_resp.status_code = 200
            mock_resp.json = lambda: mock_response
            mock_resp.raise_for_status.return_value = None
            mock_client.return_value.__aenter__.return_value.get.return_value = (
                mock_resp  # noqa: E501
            )

            result = await article_manager.get_article_comments("123")

            assert result["status"] == "success"
            assert result["data"] == mock_response

    @pytest.mark.asyncio
    async def test_add_comment_success(self, article_manager):
        """Test successful comment addition."""
        mock_response = {
            "id": "comment-1",
            "text": "Test comment",
            "author": {"fullName": "Test User"},
        }

        with patch("httpx.AsyncClient") as mock_client:
            mock_resp = AsyncMock()
            mock_resp.status_code = 200
            mock_resp.json = lambda: mock_response
            mock_resp.raise_for_status.return_value = None
            mock_client.return_value.__aenter__.return_value.post.return_value = (
                mock_resp  # noqa: E501
            )

            result = await article_manager.add_comment("123", "Test comment")

            assert result["status"] == "success"
            assert "added successfully" in result["message"]
            assert result["data"] == mock_response

    @pytest.mark.asyncio
    async def test_get_article_attachments_success(self, article_manager):
        """Test successful article attachments retrieval."""
        mock_response = [
            {
                "id": "attachment-1",
                "name": "test.pdf",
                "size": 1024,
                "mimeType": "application/pdf",
            }
        ]

        with patch("httpx.AsyncClient") as mock_client:
            mock_resp = AsyncMock()
            mock_resp.status_code = 200
            mock_resp.json = lambda: mock_response
            mock_resp.raise_for_status.return_value = None
            mock_client.return_value.__aenter__.return_value.get.return_value = (
                mock_resp  # noqa: E501
            )

            result = await article_manager.get_article_attachments("123")

            assert result["status"] == "success"
            assert result["data"] == mock_response

    @pytest.mark.asyncio
    async def test_not_authenticated_error(self, article_manager):
        """Test operations when not authenticated."""
        article_manager.auth_manager.load_credentials.return_value = None

        result = await article_manager.create_article("Title", "Content")
        assert result["status"] == "error"
        assert "Not authenticated" in result["message"]

        result = await article_manager.list_articles()
        assert result["status"] == "error"
        assert "Not authenticated" in result["message"]

    def test_display_articles_table_empty(self, article_manager):
        """Test displaying empty articles table."""
        with patch("youtrack_cli.articles.Console") as mock_console:
            article_manager.console = mock_console.return_value
            article_manager.display_articles_table([])

            mock_console.return_value.print.assert_called_with(
                "No articles found.", style="yellow"
            )

    def test_display_articles_table_with_data(self, article_manager):
        """Test displaying articles table with data."""
        articles = [
            {
                "id": "123",
                "summary": "Test Article",
                "content": "Test content",
                "author": {"fullName": "Test User"},
                "created": "2023-01-01",
                "visibility": {"type": "public"},
            }
        ]

        with (
            patch("youtrack_cli.articles.Console") as mock_console,
            patch("youtrack_cli.articles.Table") as mock_table,
        ):
            article_manager.console = mock_console.return_value
            article_manager.display_articles_table(articles)

            mock_table.assert_called_once()
            mock_console.return_value.print.assert_called()

    def test_display_articles_tree_empty(self, article_manager):
        """Test displaying empty articles tree."""
        with patch("youtrack_cli.articles.Console") as mock_console:
            article_manager.console = mock_console.return_value
            article_manager.display_articles_tree([])

            mock_console.return_value.print.assert_called_with(
                "No articles found.", style="yellow"
            )

    def test_display_articles_tree_with_data(self, article_manager):
        """Test displaying articles tree with data."""
        articles = [
            {
                "id": "123",
                "summary": "Root Article",
                "visibility": {"type": "public"},
            },
            {
                "id": "124",
                "summary": "Child Article",
                "parentArticle": {"id": "123"},
                "visibility": {"type": "public"},
            },
        ]

        with (
            patch("youtrack_cli.articles.Console") as mock_console,
            patch("youtrack_cli.articles.Tree") as mock_tree,
        ):
            article_manager.console = mock_console.return_value
            article_manager.display_articles_tree(articles)

            mock_tree.assert_called_once()
            mock_console.return_value.print.assert_called()

    def test_display_article_details(self, article_manager):
        """Test displaying article details."""
        article = {
            "id": "123",
            "summary": "Test Article",
            "content": "Test content",
            "author": {"fullName": "Test User"},
            "created": "2023-01-01",
            "updated": "2023-01-02",
            "visibility": {"type": "public"},
            "project": {"name": "Test Project"},
            "parentArticle": {"summary": "Parent Article"},
        }

        with patch("youtrack_cli.articles.Console") as mock_console:
            article_manager.console = mock_console.return_value
            article_manager.display_article_details(article)

            # Check that print was called multiple times for different fields
            assert mock_console.return_value.print.call_count >= 8


class TestArticlesCLI:
    """Test cases for articles CLI commands."""

    def test_articles_create_command(self):
        """Test articles create command."""
        from youtrack_cli.main import main

        runner = CliRunner()

        with (
            patch("youtrack_cli.main.asyncio.run") as mock_run,
            patch("youtrack_cli.main.AuthManager"),
            patch("youtrack_cli.articles.ArticleManager"),
        ):
            mock_run.return_value = {
                "status": "success",
                "message": "Article created successfully",
                "data": {"id": "123"},
            }

            result = runner.invoke(
                main, ["articles", "create", "Test Title", "--content", "Test content"]
            )

            assert result.exit_code == 0
            assert "Creating article" in result.output

    def test_articles_list_command(self):
        """Test articles list command."""
        from youtrack_cli.main import main

        runner = CliRunner()

        with (
            patch("youtrack_cli.main.asyncio.run") as mock_run,
            patch("youtrack_cli.main.AuthManager"),
            patch("youtrack_cli.articles.ArticleManager"),
        ):
            mock_run.return_value = {
                "status": "success",
                "data": [],
                "count": 0,
            }

            result = runner.invoke(main, ["articles", "list"])

            assert result.exit_code == 0
            assert "Fetching articles" in result.output

    def test_articles_search_command(self):
        """Test articles search command."""
        from youtrack_cli.main import main

        runner = CliRunner()

        with (
            patch("youtrack_cli.main.asyncio.run") as mock_run,
            patch("youtrack_cli.main.AuthManager"),
            patch("youtrack_cli.articles.ArticleManager"),
        ):
            mock_run.return_value = {
                "status": "success",
                "data": [],
                "count": 0,
            }

            result = runner.invoke(main, ["articles", "search", "test query"])

            assert result.exit_code == 0
            assert "Searching articles" in result.output

    def test_articles_tree_command(self):
        """Test articles tree command."""
        from youtrack_cli.main import main

        runner = CliRunner()

        with (
            patch("youtrack_cli.main.asyncio.run") as mock_run,
            patch("youtrack_cli.main.AuthManager"),
            patch("youtrack_cli.articles.ArticleManager"),
        ):
            mock_run.return_value = {
                "status": "success",
                "data": [],
                "count": 0,
            }

            result = runner.invoke(main, ["articles", "tree"])

            assert result.exit_code == 0
            assert "Fetching articles tree" in result.output

    def test_articles_comments_add_command(self):
        """Test articles comments add command."""
        from youtrack_cli.main import main

        runner = CliRunner()

        with (
            patch("youtrack_cli.main.asyncio.run") as mock_run,
            patch("youtrack_cli.main.AuthManager"),
            patch("youtrack_cli.articles.ArticleManager"),
        ):
            mock_run.return_value = {
                "status": "success",
                "message": "Comment added successfully",
                "data": {"id": "comment-1"},
            }

            result = runner.invoke(
                main, ["articles", "comments", "add", "123", "Test comment"]
            )

            assert result.exit_code == 0
            assert "Adding comment" in result.output

    def test_articles_comments_list_command(self):
        """Test articles comments list command."""
        from youtrack_cli.main import main

        runner = CliRunner()

        with (
            patch("youtrack_cli.main.asyncio.run") as mock_run,
            patch("youtrack_cli.main.AuthManager"),
            patch("youtrack_cli.articles.ArticleManager"),
        ):
            mock_run.return_value = {
                "status": "success",
                "data": [],
            }

            result = runner.invoke(main, ["articles", "comments", "list", "123"])

            assert result.exit_code == 0
            assert "Fetching comments" in result.output

    def test_articles_attach_list_command(self):
        """Test articles attach list command."""
        from youtrack_cli.main import main

        runner = CliRunner()

        with (
            patch("youtrack_cli.main.asyncio.run") as mock_run,
            patch("youtrack_cli.main.AuthManager"),
            patch("youtrack_cli.articles.ArticleManager"),
        ):
            mock_run.return_value = {
                "status": "success",
                "data": [],
            }

            result = runner.invoke(main, ["articles", "attach", "list", "123"])

            assert result.exit_code == 0
            assert "Fetching attachments" in result.output
