"""Tests for article management functionality."""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, Mock, patch

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

        result = await article_manager.create_article("Title", "Content")
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

            result = runner.invoke(main, ["articles", "create", "Test Title", "--content", "Test content"])

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

            result = runner.invoke(main, ["articles", "create", "Test Title", "--file", str(test_file)])

            assert result.exit_code == 0
            assert "Reading content from" in result.output
            assert "Creating article" in result.output

    def test_articles_create_command_file_not_found(self):
        """Test articles create command with non-existent file."""
        from youtrack_cli.main import main

        runner = CliRunner()

        result = runner.invoke(main, ["articles", "create", "Test Title", "--file", "nonexistent.md"])

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
                main, ["articles", "create", "Test Title", "--content", "Test content", "--file", str(test_file)]
            )

            assert result.exit_code != 0
            assert "Cannot specify both --content and --file options" in result.output

    def test_articles_create_command_no_content_or_file(self):
        """Test articles create command with neither content nor file (should fail)."""
        from youtrack_cli.main import main

        runner = CliRunner()

        result = runner.invoke(main, ["articles", "create", "Test Title"])

        assert result.exit_code != 0
        assert "Either --content or --file must be specified" in result.output

    def test_articles_create_command_empty_file(self):
        """Test articles create command with empty file."""
        from youtrack_cli.main import main

        runner = CliRunner()

        with runner.isolated_filesystem():
            test_file = Path("empty.md")
            test_file.write_text("")

            result = runner.invoke(main, ["articles", "create", "Test Title", "--file", str(test_file)])

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
