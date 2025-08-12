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
    async def test_create_sub_article_with_parent_id_success(self, article_manager):
        """Test successful sub-article creation with readable parent ID."""
        # Mock responses for project resolution, parent ID resolution, and article creation
        project_response = [{"id": "167-0", "shortName": "FPU"}]

        parent_article_response = {
            "id": "167-6",  # Internal ID
            "idReadable": "FPU-A-1",
            "summary": "Parent Article",
        }

        create_response = {
            "id": "167-7",
            "idReadable": "FPU-A-2",
            "summary": "Sub Article",
            "content": "Sub article content",
            "parentArticle": {"id": "167-6"},
        }

        with patch("youtrack_cli.articles.get_client_manager") as mock_get_client:
            mock_client_manager = Mock()

            # First call is to resolve project ID
            project_resp = Mock()
            project_resp.status_code = 200
            project_resp.json.return_value = project_response
            project_resp.text = '[{"id": "167-0", "shortName": "FPU"}]'
            project_resp.headers = {"content-type": "application/json"}

            # Second call is to resolve parent article ID
            parent_resp = Mock()
            parent_resp.status_code = 200
            parent_resp.json.return_value = parent_article_response
            parent_resp.text = '{"id": "167-6", "idReadable": "FPU-A-1"}'
            parent_resp.headers = {"content-type": "application/json"}

            # Third call is to create the article
            create_resp = Mock()
            create_resp.status_code = 200
            create_resp.json.return_value = create_response
            create_resp.text = '{"id": "167-7", "idReadable": "FPU-A-2"}'
            create_resp.headers = {"content-type": "application/json"}

            # Set up the mock to return different responses for each call
            mock_client_manager.make_request = AsyncMock(side_effect=[project_resp, parent_resp, create_resp])
            mock_get_client.return_value = mock_client_manager

            result = await article_manager.create_article(
                title="Sub Article",
                content="Sub article content",
                project_id="FPU",
                parent_id="FPU-A-1",  # Using readable ID
            )

            assert result["status"] == "success", f"Expected success, got error: {result.get('message', 'No message')}"
            assert "Sub Article" in result["message"]
            assert result["data"]["parentArticle"]["id"] == "167-6"

    @pytest.mark.asyncio
    async def test_create_sub_article_parent_not_found(self, article_manager):
        """Test sub-article creation failure when parent article not found."""
        # Mock project resolution success, but parent article resolution failure
        project_response = [{"id": "167-0", "shortName": "FPU"}]

        with patch("youtrack_cli.articles.get_client_manager") as mock_get_client:
            mock_client_manager = Mock()

            # First call is to resolve project ID (succeeds)
            project_resp = Mock()
            project_resp.status_code = 200
            project_resp.json.return_value = project_response
            project_resp.text = '[{"id": "167-0", "shortName": "FPU"}]'
            project_resp.headers = {"content-type": "application/json"}

            # Mock parent resolution failure for the second call
            mock_client_manager.make_request = AsyncMock(
                side_effect=[project_resp, Exception("Article 'FPU-A-999' not found")]
            )
            mock_get_client.return_value = mock_client_manager

            result = await article_manager.create_article(
                title="Sub Article",
                content="Sub article content",
                project_id="FPU",
                parent_id="FPU-A-999",  # Non-existent parent
            )

            assert result["status"] == "error"
            assert "Failed to resolve parent article" in result["message"]

    @pytest.mark.asyncio
    async def test_resolve_article_id(self, article_manager):
        """Test article ID resolution functionality."""
        # Test resolving readable ID to internal ID
        mock_article_response = {
            "id": "167-6",
            "idReadable": "FPU-A-1",
            "summary": "Test Article",
        }

        with patch("youtrack_cli.articles.get_client_manager") as mock_get_client:
            mock_client_manager = Mock()
            mock_resp = Mock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = mock_article_response
            mock_resp.text = '{"id": "167-6", "idReadable": "FPU-A-1"}'
            mock_resp.headers = {"content-type": "application/json"}
            mock_client_manager.make_request = AsyncMock(return_value=mock_resp)
            mock_get_client.return_value = mock_client_manager

            # Test with readable ID
            internal_id = await article_manager._resolve_article_id("FPU-A-1")
            assert internal_id == "167-6"

            # Test with already internal ID (should return as-is)
            internal_id = await article_manager._resolve_article_id("167-6")
            assert internal_id == "167-6"

    @pytest.mark.asyncio
    async def test_resolve_article_id_nonexistent_internal(self, article_manager):
        """Test that _resolve_article_id fails for non-existent internal IDs."""

        with patch("youtrack_cli.articles.get_client_manager") as mock_get_client:
            mock_client_manager = Mock()
            # Mock response for non-existent article (404 or error)
            mock_resp = Mock()
            mock_resp.status_code = 404
            mock_resp.text = "Article not found"
            mock_resp.headers = {"content-type": "text/plain"}
            mock_client_manager.make_request = AsyncMock(side_effect=Exception("Article not found"))
            mock_get_client.return_value = mock_client_manager

            # Test with non-existent internal ID
            with pytest.raises(ValueError, match="Article '999-999' not found"):
                await article_manager._resolve_article_id("999-999")

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


@pytest.mark.unit
class TestArticleIDManagement:
    """Test cases for ArticleID comment management in markdown files."""

    def test_extract_article_id_from_content(self):
        """Test extracting ArticleID from markdown content."""
        from youtrack_cli.articles import extract_article_id_from_content

        # Test with valid ArticleID
        content = "<!-- ArticleID: DOCS-A-123 -->\n# My Article\nContent here"
        assert extract_article_id_from_content(content) == "DOCS-A-123"

        # Test with whitespace variations
        content = "<!--   ArticleID:   DOCS-A-456   -->\n# Article"
        assert extract_article_id_from_content(content) == "DOCS-A-456"

        # Test with no ArticleID
        content = "# My Article\nNo ID here"
        assert extract_article_id_from_content(content) is None

        # Test with malformed ArticleID
        content = "<!-- ArticleID: -->\n# Article"
        assert extract_article_id_from_content(content) is None

        # Test with ArticleID in middle of content
        content = "# Title\nSome content\n<!-- ArticleID: MID-123 -->\nMore content"
        assert extract_article_id_from_content(content) == "MID-123"

    def test_insert_or_update_article_id(self):
        """Test inserting or updating ArticleID in markdown content."""
        from youtrack_cli.articles import insert_or_update_article_id

        # Test inserting new ArticleID
        content = "# My Article\nContent here"
        result = insert_or_update_article_id(content, "NEW-123")
        assert "<!-- ArticleID: NEW-123 -->" in result
        assert result.startswith("<!-- ArticleID: NEW-123 -->")
        assert "# My Article" in result

        # Test updating existing ArticleID
        content = "<!-- ArticleID: OLD-123 -->\n# My Article\nContent"
        result = insert_or_update_article_id(content, "NEW-456")
        assert "<!-- ArticleID: NEW-456 -->" in result
        assert "<!-- ArticleID: OLD-123 -->" not in result
        assert "# My Article" in result

        # Test with empty content
        content = ""
        result = insert_or_update_article_id(content, "EMPTY-123")
        assert result == "<!-- ArticleID: EMPTY-123 -->\n"

        # Test with whitespace variations
        content = "<!--  ArticleID:  OLD-789  -->\n# Title"
        result = insert_or_update_article_id(content, "NEW-789")
        assert "<!-- ArticleID: NEW-789 -->" in result
        assert "OLD-789" not in result

    def test_remove_article_id_comment(self):
        """Test removing ArticleID comment from markdown content."""
        from youtrack_cli.articles import remove_article_id_comment

        # Test removing ArticleID at beginning
        content = "<!-- ArticleID: DOCS-123 -->\n\n# My Article\nContent"
        result = remove_article_id_comment(content)
        assert "ArticleID" not in result
        assert result.startswith("# My Article")

        # Test removing ArticleID in middle
        content = "# Title\n<!-- ArticleID: MID-456 -->\nContent"
        result = remove_article_id_comment(content)
        assert "ArticleID" not in result
        assert "# Title\nContent" in result

        # Test with no ArticleID
        content = "# My Article\nNo ID here"
        result = remove_article_id_comment(content)
        assert result == content

        # Test with multiple newlines after ArticleID
        content = "<!-- ArticleID: TEST-789 -->\n\n\n# Title"
        result = remove_article_id_comment(content)
        assert result.startswith("# Title")


@pytest.mark.unit
class TestArticleIDCommandIntegration:
    """Test cases for ArticleID management in create and edit commands."""

    def test_create_command_with_file_and_article_id(self):
        """Test create command with file and ArticleID insertion."""
        import tempfile
        from pathlib import Path
        from unittest.mock import AsyncMock, MagicMock, patch

        from click.testing import CliRunner

        from youtrack_cli.commands.articles import create

        runner = CliRunner()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("# Test Article\nThis is test content.")
            temp_file = f.name

        try:
            with patch("youtrack_cli.auth.AuthManager") as mock_auth:
                with patch("youtrack_cli.articles.ArticleManager") as mock_manager_class:
                    # Setup mocks
                    mock_auth_instance = MagicMock()
                    mock_auth.return_value = mock_auth_instance

                    mock_manager = MagicMock()
                    mock_manager_class.return_value = mock_manager

                    # Mock successful creation
                    mock_manager.create_article = AsyncMock(
                        return_value={
                            "status": "success",
                            "message": "Article created",
                            "data": {"id": "123-456", "idReadable": "DOCS-A-789"},
                        }
                    )

                    # Run command
                    runner.invoke(
                        create, ["Test Article", "--file", temp_file, "--project-id", "TEST"], obj={"config": {}}
                    )

                    # Check the file was updated with ArticleID
                    with open(temp_file) as f:
                        updated_content = f.read()

                    assert "<!-- ArticleID: DOCS-A-789 -->" in updated_content
                    assert "# Test Article" in updated_content

        finally:
            Path(temp_file).unlink()

    def test_create_command_with_no_article_id_flag(self):
        """Test create command with --no-article-id flag."""
        import tempfile
        from pathlib import Path
        from unittest.mock import AsyncMock, MagicMock, patch

        from click.testing import CliRunner

        from youtrack_cli.commands.articles import create

        runner = CliRunner()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            original_content = "# Test Article\nThis is test content."
            f.write(original_content)
            temp_file = f.name

        try:
            with patch("youtrack_cli.auth.AuthManager") as mock_auth:
                with patch("youtrack_cli.articles.ArticleManager") as mock_manager_class:
                    # Setup mocks
                    mock_auth_instance = MagicMock()
                    mock_auth.return_value = mock_auth_instance

                    mock_manager = MagicMock()
                    mock_manager_class.return_value = mock_manager

                    # Mock successful creation
                    mock_manager.create_article = AsyncMock(
                        return_value={
                            "status": "success",
                            "message": "Article created",
                            "data": {"id": "123-456", "idReadable": "DOCS-A-789"},
                        }
                    )

                    # Run command with --no-article-id
                    runner.invoke(
                        create,
                        ["Test Article", "--file", temp_file, "--project-id", "TEST", "--no-article-id"],
                        obj={"config": {}},
                    )

                    # Check the file was NOT updated with ArticleID
                    with open(temp_file) as f:
                        content = f.read()

                    assert "<!-- ArticleID:" not in content
                    assert content == original_content

        finally:
            Path(temp_file).unlink()

    def test_edit_command_with_file(self):
        """Test edit command with file option."""
        import tempfile
        from pathlib import Path
        from unittest.mock import AsyncMock, MagicMock, patch

        from click.testing import CliRunner

        from youtrack_cli.commands.articles import edit

        runner = CliRunner()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("# Updated Article\nUpdated content.")
            temp_file = f.name

        try:
            with patch("youtrack_cli.auth.AuthManager") as mock_auth:
                with patch("youtrack_cli.articles.ArticleManager") as mock_manager_class:
                    # Setup mocks
                    mock_auth_instance = MagicMock()
                    mock_auth.return_value = mock_auth_instance

                    mock_manager = MagicMock()
                    mock_manager_class.return_value = mock_manager

                    # Mock successful update
                    mock_manager.update_article = AsyncMock(
                        return_value={"status": "success", "message": "Article updated"}
                    )

                    # Run command
                    runner.invoke(edit, ["DOCS-A-789", "--file", temp_file], obj={"config": {}})

                    # Check the file was updated with ArticleID
                    with open(temp_file) as f:
                        updated_content = f.read()

                    assert "<!-- ArticleID: DOCS-A-789 -->" in updated_content
                    assert "# Updated Article" in updated_content

        finally:
            Path(temp_file).unlink()

    def test_edit_command_with_file_containing_article_id(self):
        """Test edit command with file containing ArticleID and no argument."""
        import tempfile
        from pathlib import Path
        from unittest.mock import AsyncMock, MagicMock, patch

        from click.testing import CliRunner

        from youtrack_cli.commands.articles import edit

        runner = CliRunner()

        # Create a file with ArticleID comment
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("<!-- ArticleID: DOCS-A-123 -->\n# Updated Article\nUpdated content.")
            temp_file = f.name

        try:
            with patch("youtrack_cli.auth.AuthManager") as mock_auth:
                with patch("youtrack_cli.articles.ArticleManager") as mock_manager_class:
                    # Setup mocks
                    mock_auth_instance = MagicMock()
                    mock_auth.return_value = mock_auth_instance

                    mock_manager = MagicMock()
                    mock_manager_class.return_value = mock_manager

                    # Mock successful update
                    mock_manager.update_article = AsyncMock(
                        return_value={"status": "success", "message": "Article updated"}
                    )

                    # Run command without article ID argument
                    result = runner.invoke(edit, ["--file", temp_file], obj={"config": {}})

                    # Command should succeed
                    assert result.exit_code == 0

                    # Check that update_article was called with the extracted ID
                    mock_manager.update_article.assert_called_once()
                    call_args = mock_manager.update_article.call_args
                    assert call_args[1]["article_id"] == "DOCS-A-123"

        finally:
            Path(temp_file).unlink()

    def test_edit_command_with_file_missing_article_id(self):
        """Test edit command with file without ArticleID and no argument."""
        import tempfile
        from pathlib import Path
        from unittest.mock import MagicMock, patch

        from click.testing import CliRunner

        from youtrack_cli.commands.articles import edit

        runner = CliRunner()

        # Create a file without ArticleID comment
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("# Updated Article\nUpdated content without ArticleID.")
            temp_file = f.name

        try:
            with patch("youtrack_cli.auth.AuthManager") as mock_auth:
                with patch("youtrack_cli.articles.ArticleManager") as mock_manager_class:
                    # Setup mocks
                    mock_auth_instance = MagicMock()
                    mock_auth.return_value = mock_auth_instance

                    mock_manager = MagicMock()
                    mock_manager_class.return_value = mock_manager

                    # Run command without article ID argument
                    result = runner.invoke(edit, ["--file", temp_file], obj={"config": {}})

                    # Command should fail
                    assert result.exit_code != 0
                    assert "No article ID provided and none found in file" in result.output

        finally:
            Path(temp_file).unlink()

    def test_edit_command_with_conflicting_article_ids(self):
        """Test edit command with different article IDs in argument and file."""
        import tempfile
        from pathlib import Path
        from unittest.mock import AsyncMock, MagicMock, patch

        from click.testing import CliRunner

        from youtrack_cli.commands.articles import edit

        runner = CliRunner()

        # Create a file with ArticleID comment
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("<!-- ArticleID: DOCS-A-123 -->\n# Updated Article\nUpdated content.")
            temp_file = f.name

        try:
            with patch("youtrack_cli.auth.AuthManager") as mock_auth:
                with patch("youtrack_cli.articles.ArticleManager") as mock_manager_class:
                    # Setup mocks
                    mock_auth_instance = MagicMock()
                    mock_auth.return_value = mock_auth_instance

                    mock_manager = MagicMock()
                    mock_manager_class.return_value = mock_manager

                    # Mock successful update
                    mock_manager.update_article = AsyncMock(
                        return_value={"status": "success", "message": "Article updated"}
                    )

                    # Run command with different article ID argument
                    result = runner.invoke(edit, ["DOCS-A-456", "--file", temp_file], obj={"config": {}})

                    # Command should succeed but show warning
                    assert result.exit_code == 0
                    assert "Warning: File contains ArticleID 'DOCS-A-123'" in result.output
                    assert "DOCS-A-456" in result.output

                    # Check that update_article was called with the argument ID
                    mock_manager.update_article.assert_called_once()
                    call_args = mock_manager.update_article.call_args
                    assert call_args[1]["article_id"] == "DOCS-A-456"

        finally:
            Path(temp_file).unlink()
