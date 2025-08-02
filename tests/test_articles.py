"""Tests for article management functionality."""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
from click.testing import CliRunner

from youtrack_cli.articles import ArticleManager
from youtrack_cli.auth import AuthConfig


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
    auth_manager = MagicMock()
    auth_manager.load_credentials.return_value = mock_credentials
    return auth_manager


@pytest.fixture
def article_manager(mock_auth_manager):
    """Article manager instance for testing."""
    return ArticleManager(mock_auth_manager)


@pytest.mark.unit
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

        with patch("youtrack_cli.articles.get_client_manager") as mock_get_client:
            mock_client_manager = Mock()
            mock_resp = Mock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = mock_response
            mock_resp.text = '{"id": "123", "summary": "Test Article"}'
            mock_resp.headers = {"content-type": "application/json"}
            mock_client_manager.make_request = AsyncMock(return_value=mock_resp)
            mock_get_client.return_value = mock_client_manager

            result = await article_manager.create_article(
                title="Test Article",
                content="Test content",
                project_id="TEST-PROJECT",
            )

            assert result["status"] == "success"
            assert "Test Article" in result["message"]
            assert result["data"] == mock_response

    @pytest.mark.asyncio
    async def test_create_article_failure(self, article_manager):
        """Test article creation failure."""
        with patch("youtrack_cli.articles.get_client_manager") as mock_get_client:
            mock_client_manager = Mock()
            mock_client_manager.make_request = AsyncMock(side_effect=Exception("HTTP 400: Bad Request"))
            mock_get_client.return_value = mock_client_manager

            result = await article_manager.create_article(
                title="Test Article",
                content="Test content",
                project_id="TEST-PROJECT",
            )

            assert result["status"] == "error"
            assert "HTTP 400: Bad Request" in result["message"]

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

        with patch("youtrack_cli.articles.get_client_manager") as mock_get_client:
            mock_client_manager = Mock()
            mock_resp = Mock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = mock_response
            mock_resp.text = '[{"id": "123", "summary": "Article 1"}]'
            mock_resp.headers = {"content-type": "application/json"}
            mock_client_manager.make_request = AsyncMock(return_value=mock_resp)
            mock_get_client.return_value = mock_client_manager

            result = await article_manager.list_articles()

            assert result["status"] == "success"
            assert result["data"] == mock_response
            assert result["count"] == 2

    @pytest.mark.asyncio
    async def test_list_articles_with_parent_filtering(self, article_manager):
        """Test article listing with parent_id filtering."""
        # Mock articles data with parent-child relationships
        mock_articles_response = [
            {"id": "167-6", "idReadable": "FPU-A-1", "summary": "Parent Article", "parentArticle": None},
            {
                "id": "167-7",
                "idReadable": "FPU-A-2",
                "summary": "Child Article 1",
                "parentArticle": {"id": "167-6", "summary": "Parent Article", "$type": "Article"},
            },
            {
                "id": "167-8",
                "idReadable": "FPU-A-3",
                "summary": "Child Article 2",
                "parentArticle": {"id": "167-6", "summary": "Parent Article", "$type": "Article"},
            },
        ]

        with patch("youtrack_cli.articles.get_client_manager") as mock_get_client:
            mock_client_manager = Mock()
            mock_resp = Mock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = mock_articles_response
            mock_resp.text = str(mock_articles_response)
            mock_resp.headers = {"content-type": "application/json"}
            mock_client_manager.make_request = AsyncMock(return_value=mock_resp)
            mock_get_client.return_value = mock_client_manager

            # Test filtering by readable parent ID - should return child articles
            result = await article_manager.list_articles(parent_id="FPU-A-1")
            assert result["status"] == "success"
            assert result["count"] == 2
            assert len(result["data"]) == 2

    @pytest.mark.asyncio
    async def test_get_article_success(self, article_manager):
        """Test successful article retrieval."""
        mock_response = {
            "id": "123",
            "summary": "Test Article",
            "content": "Test content",
        }

        with patch("youtrack_cli.articles.get_client_manager") as mock_get_client:
            mock_client_manager = Mock()
            mock_resp = Mock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = mock_response
            mock_resp.text = '{"mock": "response"}'
            mock_resp.headers = {"content-type": "application/json"}
            mock_client_manager.make_request = AsyncMock(return_value=mock_resp)
            mock_get_client.return_value = mock_client_manager

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

        with patch("youtrack_cli.articles.get_client_manager") as mock_get_client:
            mock_client_manager = Mock()
            mock_resp = Mock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = mock_response
            mock_resp.text = '{"mock": "response"}'
            mock_resp.headers = {"content-type": "application/json"}
            mock_client_manager.make_request = AsyncMock(return_value=mock_resp)
            mock_get_client.return_value = mock_client_manager

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
        with patch("youtrack_cli.articles.get_client_manager") as mock_get_client:
            mock_client_manager = Mock()
            mock_resp = Mock()
            mock_resp.status_code = 200
            mock_client_manager.make_request = AsyncMock(return_value=mock_resp)
            mock_get_client.return_value = mock_client_manager

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

        with patch("youtrack_cli.articles.get_client_manager") as mock_get_client:
            mock_client_manager = Mock()
            mock_resp = Mock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = mock_response
            mock_resp.text = '{"mock": "response"}'
            mock_resp.headers = {"content-type": "application/json"}
            mock_client_manager.make_request = AsyncMock(return_value=mock_resp)
            mock_get_client.return_value = mock_client_manager

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

        with patch("youtrack_cli.articles.get_client_manager") as mock_get_client:
            mock_client_manager = Mock()
            mock_resp = Mock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = mock_response
            mock_resp.text = '{"mock": "response"}'
            mock_resp.headers = {"content-type": "application/json"}
            mock_client_manager.make_request = AsyncMock(return_value=mock_resp)
            mock_get_client.return_value = mock_client_manager

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
                "reporter": {"fullName": "Test User"},
            }
        ]

        with patch("youtrack_cli.articles.get_client_manager") as mock_get_client:
            mock_client_manager = Mock()
            mock_resp = Mock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = mock_response
            mock_resp.text = '{"mock": "response"}'
            mock_resp.headers = {"content-type": "application/json"}
            mock_client_manager.make_request = AsyncMock(return_value=mock_resp)
            mock_get_client.return_value = mock_client_manager

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

        with patch("youtrack_cli.articles.get_client_manager") as mock_get_client:
            mock_client_manager = Mock()
            mock_resp = Mock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = mock_response
            mock_resp.text = '{"mock": "response"}'
            mock_resp.headers = {"content-type": "application/json"}
            mock_client_manager.make_request = AsyncMock(return_value=mock_resp)
            mock_get_client.return_value = mock_client_manager

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

        with patch("youtrack_cli.articles.get_client_manager") as mock_get_client:
            mock_client_manager = Mock()
            mock_resp = Mock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = mock_response
            mock_resp.text = '{"mock": "response"}'
            mock_resp.headers = {"content-type": "application/json"}
            mock_client_manager.make_request = AsyncMock(return_value=mock_resp)
            mock_get_client.return_value = mock_client_manager

            result = await article_manager.get_article_attachments("123")

            assert result["status"] == "success"
            assert result["data"] == mock_response

    @pytest.mark.asyncio
    async def test_error_handling(self, article_manager):
        """Test error handling scenarios."""
        # Test authentication error
        article_manager.auth_manager.load_credentials.return_value = None
        result = await article_manager.create_article("Title", "Content", "TEST-PROJECT")
        assert result["status"] == "error"
        assert "Not authenticated" in result["message"]

        result = await article_manager.list_articles()
        assert result["status"] == "error"
        assert "Not authenticated" in result["message"]

        # Reset auth for other tests
        article_manager.auth_manager.load_credentials.return_value = Mock()

        # Test empty JSON response
        with patch("youtrack_cli.articles.get_client_manager") as mock_get_client:
            mock_client_manager = Mock()
            mock_resp = Mock()
            mock_resp.status_code = 200
            mock_resp.text = ""
            mock_resp.headers = {"content-type": "application/json"}
            mock_client_manager.make_request = AsyncMock(return_value=mock_resp)
            mock_get_client.return_value = mock_client_manager

            result = await article_manager.list_articles()
            assert result["status"] == "error"
            assert "Response parsing error" in result["message"]

        # Test HTML login page response
        with patch("youtrack_cli.articles.get_client_manager") as mock_get_client:
            mock_client_manager = Mock()
            mock_resp = Mock()
            mock_resp.status_code = 200
            mock_resp.text = "<!doctype html><html><body>Login page</body></html>"
            mock_resp.headers = {"content-type": "text/html"}
            mock_client_manager.make_request = AsyncMock(return_value=mock_resp)
            mock_get_client.return_value = mock_client_manager

            result = await article_manager.list_articles()
            assert result["status"] == "error"
            assert "Authentication error" in result["message"]

    def test_display_methods(self, article_manager):
        """Test display methods for articles."""
        # Test empty table display
        with patch("youtrack_cli.articles.get_console") as mock_console:
            article_manager.console = mock_console.return_value
            article_manager.display_articles_table([])
            mock_console.return_value.print.assert_called_with("No articles found.", style="yellow")

        # Test table with data
        articles = [{"id": "123", "summary": "Test Article", "visibility": {"type": "public"}}]
        with (
            patch("youtrack_cli.articles.get_console") as mock_console,
            patch("youtrack_cli.articles.Table") as mock_table,
        ):
            article_manager.console = mock_console.return_value
            article_manager.display_articles_table(articles)
            mock_table.assert_called_once()

        # Test tree display with null parent handling
        tree_articles = [
            {"id": "123", "summary": "Root Article", "parentArticle": None, "visibility": {"type": "public"}},
            {"id": "124", "summary": "Child Article", "parentArticle": {"id": "123"}, "visibility": {"type": "public"}},
        ]
        with (
            patch("youtrack_cli.articles.get_console") as mock_console,
            patch("youtrack_cli.articles.Tree") as mock_tree,
        ):
            article_manager.console = mock_console.return_value
            article_manager.display_articles_tree(tree_articles)
            mock_tree.assert_called_once()

        # Test article details display
        article = {"id": "123", "summary": "Test", "content": "Content", "author": {"fullName": "User"}}
        with patch("youtrack_cli.articles.get_console") as mock_console:
            article_manager.console = mock_console.return_value
            article_manager.display_article_details(article)
            assert mock_console.return_value.print.call_count >= 3

    @pytest.mark.asyncio
    async def test_tags_operations(self, article_manager):
        """Test article tags operations."""
        # Test get available tags
        mock_tags = [{"id": "1", "name": "bug"}, {"id": "2", "name": "feature"}]
        with patch("youtrack_cli.articles.get_client_manager") as mock_get_client:
            mock_client_manager = Mock()
            mock_response_obj = Mock()
            mock_response_obj.json.return_value = mock_tags
            mock_response_obj.text = '{"data": "test"}'
            mock_response_obj.headers = {"content-type": "application/json"}
            mock_client_manager.make_request = AsyncMock(return_value=mock_response_obj)
            mock_get_client.return_value = mock_client_manager

            result = await article_manager.get_available_tags()
            assert result["status"] == "success"
            assert result["data"] == mock_tags

            # Test get article tags
            result = await article_manager.get_article_tags("123")
            assert result["status"] == "success"
            assert result["data"] == mock_tags

        # Test add tags success
        with patch("youtrack_cli.articles.get_client_manager") as mock_get_client:
            mock_client_manager = Mock()
            mock_response_obj = Mock()
            mock_response_obj.text = '{"id": "1", "name": "bug"}'
            mock_response_obj.headers = {"content-type": "application/json"}
            mock_response_obj.json.return_value = {"id": "1", "name": "bug"}
            # Mock successful response for both tags
            mock_client_manager.make_request = AsyncMock(return_value=mock_response_obj)
            mock_get_client.return_value = mock_client_manager

            result = await article_manager.add_tags_to_article("123", ["1", "2"])
            assert result["status"] == "success"
            assert "Successfully added 2 tags" in result["message"]

        # Test remove tags
        with patch("youtrack_cli.articles.get_client_manager") as mock_get_client:
            mock_client_manager = Mock()
            mock_response_obj = Mock()
            mock_client_manager.make_request = AsyncMock(return_value=mock_response_obj)
            mock_get_client.return_value = mock_client_manager

            result = await article_manager.remove_tags_from_article("123", ["1", "2"])
            assert result["status"] == "success"
            assert "Successfully removed 2 tags" in result["message"]


@pytest.mark.unit
class TestArticlesCLI:
    """Test cases for articles CLI commands."""

    def test_articles_create_commands(self):
        """Test articles create command variations."""
        from youtrack_cli.main import main

        runner = CliRunner()

        # Test successful create with content
        with (
            patch("youtrack_cli.main.asyncio.run") as mock_run,
            patch("youtrack_cli.main.AuthManager") as mock_auth,
            patch("youtrack_cli.articles.ArticleManager"),
        ):
            mock_auth_instance = mock_auth.return_value
            mock_auth_instance.get_current_user_sync.return_value = "test_user"
            mock_run.return_value = {"status": "success", "message": "Article created", "data": {"id": "123"}}

            result = runner.invoke(
                main, ["articles", "create", "Test Title", "--content", "Test content", "--project-id", "TEST-PROJECT"]
            )
            assert result.exit_code == 0
            assert "Creating article" in result.output

        # Test create with file
        with (
            patch("youtrack_cli.main.asyncio.run") as mock_run,
            patch("youtrack_cli.main.AuthManager") as mock_auth,
            patch("youtrack_cli.articles.ArticleManager"),
            runner.isolated_filesystem(),
        ):
            mock_auth_instance = mock_auth.return_value
            mock_auth_instance.get_current_user_sync.return_value = "test_user"
            test_file = Path("test.md")
            test_file.write_text("# Test Article\n\nContent.")
            mock_run.return_value = {"status": "success", "message": "Article created", "data": {"id": "123"}}

            result = runner.invoke(
                main, ["articles", "create", "Test Title", "--file", str(test_file), "--project-id", "TEST-PROJECT"]
            )
            assert result.exit_code == 0

        # Test validation errors
        result = runner.invoke(main, ["articles", "create", "Test Title"])
        assert result.exit_code != 0
        assert "Missing option" in result.output or "required" in result.output

    def test_articles_basic_commands(self):
        """Test basic articles CLI commands."""
        from youtrack_cli.main import main

        runner = CliRunner()

        with (
            patch("youtrack_cli.main.asyncio.run") as mock_run,
            patch("youtrack_cli.main.AuthManager") as mock_auth,
            patch("youtrack_cli.articles.ArticleManager"),
        ):
            mock_auth_instance = mock_auth.return_value
            mock_auth_instance.get_current_user_sync.return_value = "test_user"

            # Test list command
            mock_run.return_value = {"status": "success", "data": [], "count": 0}
            result = runner.invoke(main, ["articles", "list"])
            assert result.exit_code == 0
            assert "Fetching articles" in result.output

            # Test search command
            result = runner.invoke(main, ["articles", "search", "test query"])
            assert result.exit_code == 0
            assert "Searching articles" in result.output

            # Test tree command
            result = runner.invoke(main, ["articles", "tree"])
            assert result.exit_code == 0
            assert "Fetching articles tree" in result.output

    def test_articles_comments_and_attachments(self):
        """Test articles comments and attachments commands."""
        from youtrack_cli.main import main

        runner = CliRunner()

        with (
            patch("youtrack_cli.main.asyncio.run") as mock_run,
            patch("youtrack_cli.main.AuthManager") as mock_auth,
            patch("youtrack_cli.articles.ArticleManager"),
        ):
            mock_auth_instance = mock_auth.return_value
            mock_auth_instance.get_current_user_sync.return_value = "test_user"

            # Test add comment
            mock_run.return_value = {"status": "success", "message": "Comment added", "data": {"id": "comment-1"}}
            result = runner.invoke(main, ["articles", "comments", "add", "123", "Test comment"])
            assert result.exit_code == 0
            assert "Adding comment" in result.output

            # Test list comments
            mock_run.return_value = {"status": "success", "data": []}
            result = runner.invoke(main, ["articles", "comments", "list", "123"])
            assert result.exit_code == 0
            assert "Fetching comments" in result.output

            # Test list attachments
            result = runner.invoke(main, ["articles", "attach", "list", "123"])
            assert result.exit_code == 0
            assert "Fetching attachments" in result.output

    def test_articles_draft_command(self):
        """Test articles draft command filtering."""
        from youtrack_cli.main import main

        runner = CliRunner()

        with (
            patch("youtrack_cli.main.asyncio.run") as mock_run,
            patch("youtrack_cli.main.AuthManager") as mock_auth,
            patch("youtrack_cli.articles.ArticleManager"),
        ):
            mock_auth_instance = mock_auth.return_value
            mock_auth_instance.get_current_user_sync.return_value = "test_user"

            # Test draft command with mixed articles (some published, some draft)
            mock_articles_data = [
                {
                    "id": "123",
                    "idReadable": "DOC-A-1",
                    "summary": "Published Article",
                    "visibility": {"$type": "UnlimitedVisibility"},
                },
                {
                    "id": "124",
                    "idReadable": "DOC-A-2",
                    "summary": "Draft Article",
                    "visibility": {"$type": "LimitedVisibility"},
                },
                {
                    "id": "125",
                    "idReadable": "DOC-A-3",
                    "summary": "Another Draft",
                    "visibility": {"$type": "PrivateVisibility"},
                },
            ]
            mock_run.return_value = {"status": "success", "data": mock_articles_data, "count": 3}

            result = runner.invoke(main, ["articles", "draft", "--project-id", "TEST"])
            assert result.exit_code == 0
            assert "Fetching draft articles" in result.output
            # Should show 2 draft articles (filtering out UnlimitedVisibility)
            assert "Total drafts: 2 articles" in result.output

            # Test draft command with all published articles (should show 0 drafts)
            mock_published_only = [
                {
                    "id": "123",
                    "summary": "Published Article 1",
                    "visibility": {"$type": "UnlimitedVisibility"},
                },
                {
                    "id": "124",
                    "summary": "Published Article 2",
                    "visibility": {"$type": "UnlimitedVisibility"},
                },
            ]
            mock_run.return_value = {"status": "success", "data": mock_published_only, "count": 2}

            result = runner.invoke(main, ["articles", "draft"])
            assert result.exit_code == 0
            assert "Total drafts: 0 articles" in result.output


@pytest.mark.unit
class TestArticleSortFunctions:
    """Test cases for article sorting helper functions."""

    def test_sort_articles_functionality(self):
        """Test core article sorting functionality."""
        from youtrack_cli.commands.articles import _sort_articles

        # Test basic title sorting
        articles = [
            {"summary": "Zebra Article", "id": "1"},
            {"summary": "Alpha Article", "id": "2"},
            {"summary": "Beta Article", "id": "3"},
        ]
        sorted_articles = _sort_articles(articles, "title", False, False)
        assert len(sorted_articles) == 3
        assert sorted_articles[0]["summary"] == "Alpha Article"
        assert sorted_articles[2]["summary"] == "Zebra Article"

        # Test reverse sorting
        sorted_articles = _sort_articles(articles, "title", True, False)
        assert sorted_articles[0]["summary"] == "Zebra Article"

        # Test ID sorting with numeric extraction
        id_articles = [
            {"id": "ART-100", "summary": "Article 100"},
            {"id": "ART-2", "summary": "Article 2"},
            {"id": "ART-50", "summary": "Article 50"},
        ]
        sorted_articles = _sort_articles(id_articles, "id", False, False)
        assert sorted_articles[0]["id"] == "ART-2"
        assert sorted_articles[2]["id"] == "ART-100"

        # Test friendly ID sorting
        friendly_articles = [
            {"idReadable": "DOC-003", "id": "123", "summary": "Doc 3"},
            {"idReadable": "DOC-001", "id": "124", "summary": "Doc 1"},
        ]
        sorted_articles = _sort_articles(friendly_articles, "friendly-id", False, False)
        assert sorted_articles[0]["idReadable"] == "DOC-001"

        # Test edge cases
        assert _sort_articles([], "title", False, False) == []
