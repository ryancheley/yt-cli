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
    async def test_list_articles_with_parent_id_filtering(self, article_manager):
        """Test article listing with parent_id filtering using readable ID."""
        # Mock articles data - includes parent and child articles
        mock_articles_response = [
            {
                "id": "167-6",
                "idReadable": "FPU-A-1",
                "summary": "Parent Article",
                "content": "Parent content",
                "parentArticle": None,
            },
            {
                "id": "167-7",
                "idReadable": "FPU-A-2",
                "summary": "Child Article 1",
                "content": "Child content 1",
                "parentArticle": {"id": "167-6", "summary": "Parent Article", "$type": "Article"},
            },
            {
                "id": "167-8",
                "idReadable": "FPU-A-3",
                "summary": "Child Article 2",
                "content": "Child content 2",
                "parentArticle": {"id": "167-6", "summary": "Parent Article", "$type": "Article"},
            },
            {
                "id": "167-9",
                "idReadable": "DEMO-A-1",
                "summary": "Other Article",
                "content": "Other content",
                "parentArticle": None,
            },
        ]

        with patch("youtrack_cli.articles.get_client_manager") as mock_get_client:
            mock_client_manager = Mock()

            # Mock the list_articles API call
            mock_resp = Mock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = mock_articles_response
            mock_resp.text = str(mock_articles_response)
            mock_resp.headers = {"content-type": "application/json"}

            mock_client_manager.make_request = AsyncMock(return_value=mock_resp)
            mock_get_client.return_value = mock_client_manager

            # Test filtering by readable parent ID
            result = await article_manager.list_articles(parent_id="FPU-A-1")

            assert result["status"] == "success"
            assert result["count"] == 2
            # Should only return the two child articles
            assert len(result["data"]) == 2
            assert result["data"][0]["idReadable"] == "FPU-A-2"
            assert result["data"][1]["idReadable"] == "FPU-A-3"

    @pytest.mark.asyncio
    async def test_list_articles_with_parent_id_no_children(self, article_manager):
        """Test article listing with parent_id that has no children."""
        # Mock articles data - no child articles
        mock_articles_response = [
            {
                "id": "167-6",
                "idReadable": "FPU-A-1",
                "summary": "Article with no children",
                "content": "Content",
                "parentArticle": None,
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

            result = await article_manager.list_articles(parent_id="FPU-A-1")

            assert result["status"] == "success"
            assert result["count"] == 0
            assert len(result["data"]) == 0

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
    async def test_not_authenticated_error(self, article_manager):
        """Test operations when not authenticated."""
        article_manager.auth_manager.load_credentials.return_value = None

        result = await article_manager.create_article("Title", "Content", "TEST-PROJECT")
        assert result["status"] == "error"
        assert "Not authenticated" in result["message"]
        assert "yt auth login" in result["message"]

        result = await article_manager.list_articles()
        assert result["status"] == "error"
        assert "Not authenticated" in result["message"]
        assert "yt auth login" in result["message"]

    @pytest.mark.asyncio
    async def test_list_articles_empty_json_response(self, article_manager):
        """Test listing articles with empty JSON response."""
        with patch("youtrack_cli.articles.get_client_manager") as mock_get_client:
            mock_client_manager = Mock()
            mock_resp = Mock()
            mock_resp.status_code = 200
            mock_resp.text = ""  # Empty response
            mock_resp.headers = {"content-type": "application/json"}
            mock_client_manager.make_request = AsyncMock(return_value=mock_resp)
            mock_get_client.return_value = mock_client_manager

            result = await article_manager.list_articles()

            assert result["status"] == "error"
            assert "Response parsing error" in result["message"]
            assert "Empty response body" in result["message"]

    @pytest.mark.asyncio
    async def test_list_articles_invalid_json_response(self, article_manager):
        """Test listing articles with invalid JSON response."""
        with patch("youtrack_cli.articles.get_client_manager") as mock_get_client:
            mock_client_manager = Mock()
            mock_resp = Mock()
            mock_resp.status_code = 200
            mock_resp.text = "invalid json"
            mock_resp.headers = {"content-type": "application/json"}
            # Mock the json() method to raise a JSONDecodeError
            import json

            mock_resp.json.side_effect = json.JSONDecodeError("Expecting value", "invalid json", 0)
            mock_client_manager.make_request = AsyncMock(return_value=mock_resp)
            mock_get_client.return_value = mock_client_manager

            result = await article_manager.list_articles()

            assert result["status"] == "error"
            assert "Response parsing error" in result["message"]
            assert "Expecting value" in result["message"]

    @pytest.mark.asyncio
    async def test_list_articles_html_login_page(self, article_manager):
        """Test listing articles receiving HTML login page."""
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
            assert "HTML login page" in result["message"]

    def test_display_articles_table_empty(self, article_manager):
        """Test displaying empty articles table."""
        with patch("youtrack_cli.articles.get_console") as mock_console:
            article_manager.console = mock_console.return_value
            article_manager.display_articles_table([])

            mock_console.return_value.print.assert_called_with("No articles found.", style="yellow")

    def test_display_articles_table_with_data(self, article_manager):
        """Test displaying articles table with data."""
        articles = [
            {
                "id": "123",
                "summary": "Test Article",
                "content": "Test content",
                "reporter": {"fullName": "Test User"},
                "created": "2023-01-01",
                "visibility": {"type": "public"},
            }
        ]

        with (
            patch("youtrack_cli.articles.get_console") as mock_console,
            patch("youtrack_cli.articles.Table") as mock_table,
        ):
            article_manager.console = mock_console.return_value
            article_manager.display_articles_table(articles)

            mock_table.assert_called_once()
            mock_console.return_value.print.assert_called()

    def test_display_articles_tree_empty(self, article_manager):
        """Test displaying empty articles tree."""
        with patch("youtrack_cli.articles.get_console") as mock_console:
            article_manager.console = mock_console.return_value
            article_manager.display_articles_tree([])

            mock_console.return_value.print.assert_called_with("No articles found.", style="yellow")

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
            patch("youtrack_cli.articles.get_console") as mock_console,
            patch("youtrack_cli.articles.Tree") as mock_tree,
        ):
            article_manager.console = mock_console.return_value
            article_manager.display_articles_tree(articles)

            mock_tree.assert_called_once()
            mock_console.return_value.print.assert_called()

    def test_display_articles_tree_with_null_parent_article(self, article_manager):
        """Test displaying articles tree with null parentArticle field (fixes #299)."""
        articles = [
            {
                "id": "123",
                "summary": "Root Article",
                "parentArticle": None,  # This would cause NoneType error before fix
                "visibility": {"type": "public"},
            },
            {
                "id": "124",
                "summary": "Another Root Article",
                "visibility": {"type": "public"},
            },
        ]

        with (
            patch("youtrack_cli.articles.get_console") as mock_console,
            patch("youtrack_cli.articles.Tree") as mock_tree,
        ):
            article_manager.console = mock_console.return_value
            # This should not raise AttributeError: 'NoneType' object has no attribute 'get'
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

        with patch("youtrack_cli.articles.get_console") as mock_console:
            article_manager.console = mock_console.return_value
            article_manager.display_article_details(article)

            # Check that print was called multiple times for different fields
            assert mock_console.return_value.print.call_count >= 8

    @pytest.mark.asyncio
    async def test_get_available_tags_success(self, article_manager):
        """Test successful fetching of available tags."""
        mock_response = [
            {"id": "1", "name": "bug", "owner": {"login": "user1"}},
            {"id": "2", "name": "feature", "owner": {"login": "user2"}},
        ]

        with patch("youtrack_cli.articles.get_client_manager") as mock_get_client:
            mock_client_manager = Mock()
            mock_response_obj = Mock()
            mock_response_obj.json.return_value = mock_response
            mock_response_obj.text = '{"data": "test"}'
            mock_response_obj.headers = {"content-type": "application/json"}
            mock_client_manager.make_request = AsyncMock(return_value=mock_response_obj)
            mock_get_client.return_value = mock_client_manager

            result = await article_manager.get_available_tags()

            assert result["status"] == "success"
            assert result["data"] == mock_response

    @pytest.mark.asyncio
    async def test_get_available_tags_auth_error(self, article_manager):
        """Test get_available_tags with authentication error."""
        article_manager.auth_manager.load_credentials.return_value = None

        result = await article_manager.get_available_tags()

        assert result["status"] == "error"
        assert "Not authenticated" in result["message"]

    @pytest.mark.asyncio
    async def test_get_article_tags_success(self, article_manager):
        """Test successful fetching of article tags."""
        mock_response = [
            {"id": "1", "name": "bug"},
            {"id": "2", "name": "feature"},
        ]

        with patch("youtrack_cli.articles.get_client_manager") as mock_get_client:
            mock_client_manager = Mock()
            mock_response_obj = Mock()
            mock_response_obj.json.return_value = mock_response
            mock_response_obj.text = '{"data": "test"}'
            mock_response_obj.headers = {"content-type": "application/json"}
            mock_client_manager.make_request = AsyncMock(return_value=mock_response_obj)
            mock_get_client.return_value = mock_client_manager

            result = await article_manager.get_article_tags("123")

            assert result["status"] == "success"
            assert result["data"] == mock_response

    @pytest.mark.asyncio
    async def test_add_tags_to_article_success(self, article_manager):
        """Test successful adding of tags to article."""
        mock_response = {"id": "1", "name": "bug"}

        with patch("youtrack_cli.articles.get_client_manager") as mock_get_client:
            mock_client_manager = Mock()
            mock_response_obj = Mock()
            mock_response_obj.json.return_value = mock_response
            mock_response_obj.text = '{"data": "test"}'
            mock_response_obj.headers = {"content-type": "application/json"}
            mock_client_manager.make_request = AsyncMock(return_value=mock_response_obj)
            mock_get_client.return_value = mock_client_manager

            result = await article_manager.add_tags_to_article("123", ["1", "2"])

            assert result["status"] == "success"
            assert "Successfully added 2 tags" in result["message"]

    @pytest.mark.asyncio
    async def test_add_tags_to_article_partial_success(self, article_manager):
        """Test partial success when adding tags to article."""
        mock_response = {"id": "1", "name": "bug"}

        with patch("youtrack_cli.articles.get_client_manager") as mock_get_client:
            mock_client_manager = Mock()
            mock_response_obj = Mock()
            mock_response_obj.json.return_value = mock_response
            mock_response_obj.text = '{"data": "test"}'
            mock_response_obj.headers = {"content-type": "application/json"}

            # First call succeeds, second fails
            mock_client_manager.make_request = AsyncMock(side_effect=[mock_response_obj, Exception("Tag not found")])
            mock_get_client.return_value = mock_client_manager

            result = await article_manager.add_tags_to_article("123", ["1", "2"])

            assert result["status"] == "partial"
            assert "Added 1 tags, failed to add 1 tags" in result["message"]

    @pytest.mark.asyncio
    async def test_remove_tags_from_article_success(self, article_manager):
        """Test successful removal of tags from article."""
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

    def test_articles_create_command(self):
        """Test articles create command."""
        from youtrack_cli.main import main

        runner = CliRunner()

        with (
            patch("youtrack_cli.main.asyncio.run") as mock_run,
            patch("youtrack_cli.main.AuthManager") as mock_auth,
            patch("youtrack_cli.articles.ArticleManager"),
        ):
            # Mock the AuthManager instance to return a username for audit logging
            mock_auth_instance = mock_auth.return_value
            mock_auth_instance.get_current_user_sync.return_value = "test_user"

            mock_run.return_value = {
                "status": "success",
                "message": "Article created successfully",
                "data": {"id": "123"},
            }

            result = runner.invoke(
                main, ["articles", "create", "Test Title", "--content", "Test content", "--project-id", "TEST-PROJECT"]
            )

            assert result.exit_code == 0
            assert "Creating article" in result.output

    def test_articles_create_command_with_file(self):
        """Test articles create command with file input."""
        from youtrack_cli.main import main

        runner = CliRunner()

        with (
            patch("youtrack_cli.main.asyncio.run") as mock_run,
            patch("youtrack_cli.main.AuthManager") as mock_auth,
            patch("youtrack_cli.articles.ArticleManager"),
            runner.isolated_filesystem(),
        ):
            # Mock the AuthManager instance to return a username for audit logging
            mock_auth_instance = mock_auth.return_value
            mock_auth_instance.get_current_user_sync.return_value = "test_user"

            # Create a test markdown file
            test_file = Path("test_article.md")
            test_file.write_text("# Test Article\n\nThis is test content from a markdown file.")

            mock_run.return_value = {
                "status": "success",
                "message": "Article created successfully",
                "data": {"id": "123"},
            }

            result = runner.invoke(
                main, ["articles", "create", "Test Title", "--file", str(test_file), "--project-id", "TEST-PROJECT"]
            )

            assert result.exit_code == 0
            assert "Reading content from" in result.output
            assert "Creating article" in result.output

    def test_articles_create_command_file_not_found(self):
        """Test articles create command with non-existent file."""
        from youtrack_cli.main import main

        runner = CliRunner()

        result = runner.invoke(
            main, ["articles", "create", "Test Title", "--file", "nonexistent.md", "--project-id", "TEST-PROJECT"]
        )

        assert result.exit_code != 0
        assert "does not exist" in result.output

    def test_articles_create_command_both_content_and_file(self):
        """Test articles create command with both content and file (should fail)."""
        from youtrack_cli.main import main

        runner = CliRunner()

        with runner.isolated_filesystem():
            test_file = Path("test_article.md")
            test_file.write_text("Test content")

            result = runner.invoke(
                main,
                [
                    "articles",
                    "create",
                    "Test Title",
                    "--content",
                    "Test content",
                    "--file",
                    str(test_file),
                    "--project-id",
                    "TEST-PROJECT",
                ],
            )

            assert result.exit_code != 0
            assert "Cannot specify both --content and --file options" in result.output

    def test_articles_create_command_no_content_or_file(self):
        """Test articles create command with neither content nor file (should fail)."""
        from youtrack_cli.main import main

        runner = CliRunner()

        result = runner.invoke(main, ["articles", "create", "Test Title"])

        assert result.exit_code != 0
        # Should fail because project-id is required
        assert "Missing option" in result.output or "required" in result.output

    def test_articles_create_command_missing_project_id(self):
        """Test articles create command without required project-id parameter."""
        from youtrack_cli.main import main

        runner = CliRunner()

        result = runner.invoke(main, ["articles", "create", "Test Title", "--content", "Test content"])

        assert result.exit_code != 0
        assert "Missing option" in result.output or "required" in result.output

    def test_articles_create_command_empty_file(self):
        """Test articles create command with empty file."""
        from youtrack_cli.main import main

        runner = CliRunner()

        with runner.isolated_filesystem():
            test_file = Path("empty.md")
            test_file.write_text("")

            result = runner.invoke(
                main, ["articles", "create", "Test Title", "--file", str(test_file), "--project-id", "TEST-PROJECT"]
            )

            assert result.exit_code != 0
            assert "is empty" in result.output

    def test_articles_list_command(self):
        """Test articles list command."""
        from youtrack_cli.main import main

        runner = CliRunner()

        with (
            patch("youtrack_cli.main.asyncio.run") as mock_run,
            patch("youtrack_cli.main.AuthManager") as mock_auth,
            patch("youtrack_cli.articles.ArticleManager"),
        ):
            # Mock the AuthManager instance to return a username for audit logging
            mock_auth_instance = mock_auth.return_value
            mock_auth_instance.get_current_user_sync.return_value = "test_user"

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
            patch("youtrack_cli.main.AuthManager") as mock_auth,
            patch("youtrack_cli.articles.ArticleManager"),
        ):
            # Mock the AuthManager instance to return a username for audit logging
            mock_auth_instance = mock_auth.return_value
            mock_auth_instance.get_current_user_sync.return_value = "test_user"

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
            patch("youtrack_cli.main.AuthManager") as mock_auth,
            patch("youtrack_cli.articles.ArticleManager"),
        ):
            # Mock the AuthManager instance to return a username for audit logging
            mock_auth_instance = mock_auth.return_value
            mock_auth_instance.get_current_user_sync.return_value = "test_user"

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
            patch("youtrack_cli.main.AuthManager") as mock_auth,
            patch("youtrack_cli.articles.ArticleManager"),
        ):
            # Mock the AuthManager instance to return a username for audit logging
            mock_auth_instance = mock_auth.return_value
            mock_auth_instance.get_current_user_sync.return_value = "test_user"

            mock_run.return_value = {
                "status": "success",
                "message": "Comment added successfully",
                "data": {"id": "comment-1"},
            }

            result = runner.invoke(main, ["articles", "comments", "add", "123", "Test comment"])

            assert result.exit_code == 0
            assert "Adding comment" in result.output

    def test_articles_comments_list_command(self):
        """Test articles comments list command."""
        from youtrack_cli.main import main

        runner = CliRunner()

        with (
            patch("youtrack_cli.main.asyncio.run") as mock_run,
            patch("youtrack_cli.main.AuthManager") as mock_auth,
            patch("youtrack_cli.articles.ArticleManager"),
        ):
            # Mock the AuthManager instance to return a username for audit logging
            mock_auth_instance = mock_auth.return_value
            mock_auth_instance.get_current_user_sync.return_value = "test_user"

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
            patch("youtrack_cli.main.AuthManager") as mock_auth,
            patch("youtrack_cli.articles.ArticleManager"),
        ):
            # Mock the AuthManager instance to return a username for audit logging
            mock_auth_instance = mock_auth.return_value
            mock_auth_instance.get_current_user_sync.return_value = "test_user"

            mock_run.return_value = {
                "status": "success",
                "data": [],
            }

            result = runner.invoke(main, ["articles", "attach", "list", "123"])

            assert result.exit_code == 0
            assert "Fetching attachments" in result.output

    def test_articles_reorder_command_basic(self):
        """Test basic articles reorder command functionality."""
        from youtrack_cli.main import main

        runner = CliRunner()

        with (
            patch("youtrack_cli.main.asyncio.run") as mock_run,
            patch("youtrack_cli.main.AuthManager") as mock_auth,
            patch("youtrack_cli.articles.ArticleManager"),
        ):
            # Mock the AuthManager instance to return a username for audit logging
            mock_auth_instance = mock_auth.return_value
            mock_auth_instance.get_current_user_sync.return_value = "test_user"

            mock_run.return_value = {
                "status": "success",
                "message": "Article ordering preview completed",
            }

            result = runner.invoke(main, ["articles", "reorder", "--sort-by", "title", "--project-id", "TEST"])

            assert result.exit_code == 0
            assert "API Limitation Notice" in result.output
            assert "Analyzing article ordering" in result.output

    def test_articles_reorder_command_with_article_ids(self):
        """Test articles reorder command with specific article IDs."""
        from youtrack_cli.main import main

        runner = CliRunner()

        with (
            patch("youtrack_cli.main.asyncio.run") as mock_run,
            patch("youtrack_cli.main.AuthManager") as mock_auth,
            patch("youtrack_cli.articles.ArticleManager"),
        ):
            # Mock the AuthManager instance to return a username for audit logging
            mock_auth_instance = mock_auth.return_value
            mock_auth_instance.get_current_user_sync.return_value = "test_user"

            mock_run.return_value = {
                "status": "success",
                "message": "Article ordering preview completed",
            }

            result = runner.invoke(main, ["articles", "reorder", "ART-1", "ART-2", "--sort-by", "id"])

            assert result.exit_code == 0
            assert "API Limitation Notice" in result.output

    def test_articles_reorder_command_json_format(self):
        """Test articles reorder command with JSON output format."""
        from youtrack_cli.main import main

        runner = CliRunner()

        with (
            patch("youtrack_cli.main.asyncio.run") as mock_run,
            patch("youtrack_cli.main.AuthManager") as mock_auth,
            patch("youtrack_cli.articles.ArticleManager"),
        ):
            # Mock the AuthManager instance to return a username for audit logging
            mock_auth_instance = mock_auth.return_value
            mock_auth_instance.get_current_user_sync.return_value = "test_user"

            mock_run.return_value = {
                "status": "success",
                "message": "Article ordering preview completed",
            }

            result = runner.invoke(main, ["articles", "reorder", "--sort-by", "title", "--format", "json"])

            assert result.exit_code == 0
            assert "API Limitation Notice" in result.output

    def test_articles_reorder_command_missing_sort_by(self):
        """Test articles reorder command fails without sort-by parameter."""
        from youtrack_cli.main import main

        runner = CliRunner()

        result = runner.invoke(main, ["articles", "reorder", "--project-id", "TEST"])

        assert result.exit_code != 0
        assert "sort-by" in result.output.lower() or "missing option" in result.output.lower()

    def test_articles_reorder_command_error_handling(self):
        """Test articles reorder command error handling."""
        from youtrack_cli.main import main

        runner = CliRunner()

        with (
            patch("youtrack_cli.main.asyncio.run") as mock_run,
            patch("youtrack_cli.main.AuthManager") as mock_auth,
            patch("youtrack_cli.articles.ArticleManager"),
        ):
            # Mock the AuthManager instance to return a username for audit logging
            mock_auth_instance = mock_auth.return_value
            mock_auth_instance.get_current_user_sync.return_value = "test_user"

            mock_run.return_value = {
                "status": "error",
                "message": "No articles found to reorder",
            }

            result = runner.invoke(main, ["articles", "reorder", "--sort-by", "title"])

            assert result.exit_code != 0
            assert "Failed to analyze article ordering" in result.output


@pytest.mark.unit
class TestArticleReorderFunctions:
    """Test cases for article reordering helper functions."""

    def test_sort_articles_by_title(self):
        """Test sorting articles by title."""
        from youtrack_cli.commands.articles import _sort_articles

        articles = [
            {"summary": "Zebra Article", "id": "1"},
            {"summary": "Alpha Article", "id": "2"},
            {"summary": "Beta Article", "id": "3"},
        ]

        sorted_articles = _sort_articles(articles, "title", False, False)

        assert len(sorted_articles) == 3
        assert sorted_articles[0]["summary"] == "Alpha Article"
        assert sorted_articles[1]["summary"] == "Beta Article"
        assert sorted_articles[2]["summary"] == "Zebra Article"

    def test_sort_articles_by_title_reverse(self):
        """Test sorting articles by title in reverse order."""
        from youtrack_cli.commands.articles import _sort_articles

        articles = [
            {"summary": "Alpha Article", "id": "1"},
            {"summary": "Beta Article", "id": "2"},
            {"summary": "Zebra Article", "id": "3"},
        ]

        sorted_articles = _sort_articles(articles, "title", True, False)

        assert len(sorted_articles) == 3
        assert sorted_articles[0]["summary"] == "Zebra Article"
        assert sorted_articles[1]["summary"] == "Beta Article"
        assert sorted_articles[2]["summary"] == "Alpha Article"

    def test_sort_articles_by_title_case_sensitive(self):
        """Test case-sensitive title sorting."""
        from youtrack_cli.commands.articles import _sort_articles

        articles = [
            {"summary": "apple Article", "id": "1"},
            {"summary": "Banana Article", "id": "2"},
            {"summary": "cherry Article", "id": "3"},
        ]

        # Case-sensitive: uppercase comes before lowercase
        sorted_articles = _sort_articles(articles, "title", False, True)

        assert len(sorted_articles) == 3
        assert sorted_articles[0]["summary"] == "Banana Article"

    def test_sort_articles_by_id_numeric(self):
        """Test sorting articles by ID with numeric extraction."""
        from youtrack_cli.commands.articles import _sort_articles

        articles = [
            {"id": "ART-100", "summary": "Article 100"},
            {"id": "ART-2", "summary": "Article 2"},
            {"id": "ART-50", "summary": "Article 50"},
        ]

        sorted_articles = _sort_articles(articles, "id", False, False)

        assert len(sorted_articles) == 3
        assert sorted_articles[0]["id"] == "ART-2"
        assert sorted_articles[1]["id"] == "ART-50"
        assert sorted_articles[2]["id"] == "ART-100"

    def test_sort_articles_by_friendly_id(self):
        """Test sorting articles by friendly ID."""
        from youtrack_cli.commands.articles import _sort_articles

        articles = [
            {"idReadable": "DOC-003", "id": "123", "summary": "Doc 3"},
            {"idReadable": "DOC-001", "id": "124", "summary": "Doc 1"},
            {"idReadable": "DOC-002", "id": "125", "summary": "Doc 2"},
        ]

        sorted_articles = _sort_articles(articles, "friendly-id", False, False)

        assert len(sorted_articles) == 3
        assert sorted_articles[0]["idReadable"] == "DOC-001"
        assert sorted_articles[1]["idReadable"] == "DOC-002"
        assert sorted_articles[2]["idReadable"] == "DOC-003"

    def test_sort_articles_empty_list(self):
        """Test sorting empty article list."""
        from youtrack_cli.commands.articles import _sort_articles

        articles = []
        sorted_articles = _sort_articles(articles, "title", False, False)

        assert len(sorted_articles) == 0

    def test_sort_articles_missing_fields(self):
        """Test sorting articles with missing fields."""
        from youtrack_cli.commands.articles import _sort_articles

        articles = [
            {"id": "1"},  # Missing summary
            {"summary": "Test Article", "id": "2"},
            {"id": "3"},  # Missing summary
        ]

        sorted_articles = _sort_articles(articles, "title", False, False)

        assert len(sorted_articles) == 3
        # Articles with empty summaries should come first when sorted
        assert sorted_articles[0]["id"] in ["1", "3"]

    def test_display_reorder_results_table_format(self):
        """Test displaying reorder results in table format."""
        from unittest.mock import MagicMock

        from youtrack_cli.commands.articles import _display_reorder_results

        console = MagicMock()

        original_articles = [
            {"id": "1", "idReadable": "ART-1", "summary": "Beta Article", "ordinal": 1},
            {"id": "2", "idReadable": "ART-2", "summary": "Alpha Article", "ordinal": 2},
        ]

        sorted_articles = [
            {"id": "2", "idReadable": "ART-2", "summary": "Alpha Article", "ordinal": 2},
            {"id": "1", "idReadable": "ART-1", "summary": "Beta Article", "ordinal": 1},
        ]

        with patch("rich.table.Table") as mock_table:
            _display_reorder_results(
                console=console,
                original_articles=original_articles,
                sorted_articles=sorted_articles,
                sort_by="title",
                reverse=False,
                format="table",
            )

            console.print.assert_called()
            mock_table.assert_called_once()

    def test_display_reorder_results_json_format(self):
        """Test displaying reorder results in JSON format."""
        from unittest.mock import MagicMock

        from youtrack_cli.commands.articles import _display_reorder_results

        console = MagicMock()

        original_articles = [
            {"id": "1", "idReadable": "ART-1", "summary": "Beta Article"},
        ]

        sorted_articles = [
            {"id": "1", "idReadable": "ART-1", "summary": "Beta Article"},
        ]

        _display_reorder_results(
            console=console,
            original_articles=original_articles,
            sorted_articles=sorted_articles,
            sort_by="title",
            reverse=False,
            format="json",
        )

        # Should have printed summary and JSON output
        assert console.print.call_count >= 2

    def test_show_reorder_instructions_with_project(self):
        """Test showing reorder instructions with project ID."""
        from unittest.mock import MagicMock

        from youtrack_cli.commands.articles import _show_reorder_instructions

        console = MagicMock()

        _show_reorder_instructions(console, "TEST-PROJECT", None)

        # Should have printed multiple instruction lines
        assert console.print.call_count >= 6
        # Should mention the project
        calls = [call.args[0] for call in console.print.call_args_list]
        project_mentioned = any("TEST-PROJECT" in call for call in calls)
        assert project_mentioned

    def test_show_reorder_instructions_with_parent(self):
        """Test showing reorder instructions with parent ID."""
        from unittest.mock import MagicMock

        from youtrack_cli.commands.articles import _show_reorder_instructions

        console = MagicMock()

        _show_reorder_instructions(console, None, "PARENT-ART")

        # Should have printed multiple instruction lines
        assert console.print.call_count >= 6
        # Should mention the parent
        calls = [call.args[0] for call in console.print.call_args_list]
        parent_mentioned = any("PARENT-ART" in call for call in calls)
        assert parent_mentioned
