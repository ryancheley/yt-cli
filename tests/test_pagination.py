"""Tests for pagination functionality."""

from unittest.mock import AsyncMock, Mock, patch

import pytest
from rich.console import Console
from rich.table import Table

from youtrack_cli.pagination import PaginatedTableDisplay, create_paginated_display
from youtrack_cli.utils import PaginationConfig, PaginationType, paginate_results


@pytest.mark.unit
class TestPaginatedTableDisplay:
    """Test the PaginatedTableDisplay class."""

    def test_init(self):
        """Test initialization of PaginatedTableDisplay."""
        console = Mock(spec=Console)
        paginated_display = PaginatedTableDisplay(console, page_size=25)

        assert paginated_display.console == console
        assert paginated_display.page_size == 25
        assert paginated_display.current_page == 1

    def test_init_default_page_size(self):
        """Test initialization with default page size."""
        console = Mock(spec=Console)
        paginated_display = PaginatedTableDisplay(console)

        assert paginated_display.page_size == 50

    def test_display_paginated_table_empty_data(self):
        """Test display with empty data."""
        console = Mock(spec=Console)
        paginated_display = PaginatedTableDisplay(console)
        table_builder = Mock()

        paginated_display.display_paginated_table([], table_builder, "Test")

        console.print.assert_called_once_with("No test found.", style="yellow")
        table_builder.assert_not_called()

    def test_display_paginated_table_show_all(self):
        """Test display with show_all=True."""
        console = Mock(spec=Console)
        paginated_display = PaginatedTableDisplay(console)
        data = [{"id": 1}, {"id": 2}, {"id": 3}]
        table = Mock(spec=Table)
        table_builder = Mock(return_value=table)

        paginated_display.display_paginated_table(data, table_builder, "Test", show_all=True)

        table_builder.assert_called_once_with(data)
        console.print.assert_called_once_with(table)

    def test_display_paginated_table_small_dataset(self):
        """Test display with data smaller than page size."""
        console = Mock(spec=Console)
        paginated_display = PaginatedTableDisplay(console, page_size=50)
        data = [{"id": 1}, {"id": 2}, {"id": 3}]
        table = Mock(spec=Table)
        table_builder = Mock(return_value=table)

        paginated_display.display_paginated_table(data, table_builder, "Test")

        table_builder.assert_called_once_with(data)
        console.print.assert_called_once_with(table)

    @patch("builtins.input")
    def test_display_paginated_table_single_page(self, mock_input):
        """Test display with single page of data."""
        mock_input.return_value = "q"
        console = Mock(spec=Console)
        paginated_display = PaginatedTableDisplay(console, page_size=5)
        data = [{"id": i} for i in range(5)]
        table = Mock(spec=Table)
        table_builder = Mock(return_value=table)

        paginated_display.display_paginated_table(data, table_builder, "Test")

        table_builder.assert_called_once_with(data)
        console.print.assert_called_with(table)

    @patch("builtins.input")
    def test_display_paginated_table_navigation(self, mock_input):
        """Test navigation through multiple pages."""
        mock_input.side_effect = ["n", "p", "q"]
        console = Mock(spec=Console)
        paginated_display = PaginatedTableDisplay(console, page_size=2)
        data = [{"id": i} for i in range(5)]
        table = Mock(spec=Table)
        table_builder = Mock(return_value=table)

        paginated_display.display_paginated_table(data, table_builder, "Test")

        # Should be called 3 times: initial page, next page, previous page
        assert table_builder.call_count == 3
        # Check the data passed to table_builder for each call
        calls = table_builder.call_args_list
        assert calls[0][0][0] == [{"id": 0}, {"id": 1}]  # First page
        assert calls[1][0][0] == [{"id": 2}, {"id": 3}]  # Second page (after 'n')
        assert calls[2][0][0] == [{"id": 0}, {"id": 1}]  # Back to first page (after 'p')

    @patch("builtins.input")
    def test_display_paginated_table_jump_to_page(self, mock_input):
        """Test jumping to a specific page."""
        mock_input.side_effect = ["j", "3", "q"]
        console = Mock(spec=Console)
        paginated_display = PaginatedTableDisplay(console, page_size=2)
        data = [{"id": i} for i in range(10)]
        table = Mock(spec=Table)
        table_builder = Mock(return_value=table)

        paginated_display.display_paginated_table(data, table_builder, "Test")

        # Should be called 2 times: initial page, jumped page
        assert table_builder.call_count == 2
        calls = table_builder.call_args_list
        assert calls[0][0][0] == [{"id": 0}, {"id": 1}]  # First page
        assert calls[1][0][0] == [{"id": 4}, {"id": 5}]  # Third page (after jump)

    @patch("builtins.input")
    def test_display_paginated_table_show_all_navigation(self, mock_input):
        """Test show all navigation option."""
        mock_input.return_value = "a"
        console = Mock(spec=Console)
        paginated_display = PaginatedTableDisplay(console, page_size=2)
        data = [{"id": i} for i in range(5)]
        table = Mock(spec=Table)
        table_builder = Mock(return_value=table)

        paginated_display.display_paginated_table(data, table_builder, "Test")

        # Should be called 2 times: initial page, then all data
        assert table_builder.call_count == 2
        calls = table_builder.call_args_list
        assert calls[0][0][0] == [{"id": 0}, {"id": 1}]  # First page
        assert calls[1][0][0] == data  # All data

    @patch("builtins.input")
    def test_display_paginated_table_invalid_input(self, mock_input):
        """Test handling of invalid input."""
        mock_input.side_effect = ["invalid", "xyz", "q"]
        console = Mock(spec=Console)
        paginated_display = PaginatedTableDisplay(console, page_size=2)
        data = [{"id": i} for i in range(5)]
        table = Mock(spec=Table)
        table_builder = Mock(return_value=table)

        paginated_display.display_paginated_table(data, table_builder, "Test")

        # Should display error messages for invalid input
        error_calls = [
            call for call in console.print.call_args_list if "Invalid option" in str(call) or "red" in str(call)
        ]
        assert len(error_calls) >= 2  # At least 2 error messages

    @patch("builtins.input")
    def test_display_paginated_table_start_page(self, mock_input):
        """Test starting from a specific page."""
        mock_input.return_value = "q"
        console = Mock(spec=Console)
        paginated_display = PaginatedTableDisplay(console, page_size=2)
        data = [{"id": i} for i in range(10)]
        table = Mock(spec=Table)
        table_builder = Mock(return_value=table)

        paginated_display.display_paginated_table(data, table_builder, "Test", start_page=3)

        # Should start from page 3
        table_builder.assert_called_once()
        calls = table_builder.call_args_list
        assert calls[0][0][0] == [{"id": 4}, {"id": 5}]  # Third page data

    def test_display_pagination_info(self):
        """Test pagination info display."""
        console = Mock(spec=Console)
        paginated_display = PaginatedTableDisplay(console, page_size=10)

        paginated_display._display_pagination_info(2, 5, 42)

        # Should print pagination info
        console.print.assert_called_once()
        call_args = console.print.call_args[0][0]
        assert "Page 2 of 5" in str(call_args)
        assert "showing items 11-20 of 42" in str(call_args)

    @patch("builtins.input")
    def test_get_user_action_navigation_options(self, mock_input):
        """Test user action navigation options."""
        mock_input.return_value = "q"
        console = Mock(spec=Console)
        paginated_display = PaginatedTableDisplay(console)
        paginated_display.current_page = 2

        action = paginated_display._get_user_action(5)

        assert action == "quit"
        # Should show navigation options
        options_call = [call for call in console.print.call_args_list if "Options:" in str(call)]
        assert len(options_call) >= 1

    @patch("builtins.input")
    def test_get_user_action_edge_pages(self, mock_input):
        """Test user action on first and last pages."""
        mock_input.return_value = "q"
        console = Mock(spec=Console)
        paginated_display = PaginatedTableDisplay(console)

        # Test first page (no previous option)
        paginated_display.current_page = 1
        paginated_display._get_user_action(3)

        # Test last page (no next option)
        paginated_display.current_page = 3
        paginated_display._get_user_action(3)

        # Both should complete without error
        assert mock_input.call_count == 2

    @patch("builtins.input")
    def test_keyboard_interrupt_handling(self, mock_input):
        """Test handling of keyboard interrupt."""
        mock_input.side_effect = KeyboardInterrupt()
        console = Mock(spec=Console)
        paginated_display = PaginatedTableDisplay(console)

        action = paginated_display._get_user_action(3)

        assert action == "quit"

    @patch("builtins.input")
    def test_eof_error_handling(self, mock_input):
        """Test handling of EOF error."""
        mock_input.side_effect = EOFError()
        console = Mock(spec=Console)
        paginated_display = PaginatedTableDisplay(console)

        action = paginated_display._get_user_action(3)

        assert action == "quit"


@pytest.mark.unit
class TestCreatePaginatedDisplay:
    """Test the factory function."""

    def test_create_paginated_display(self):
        """Test factory function creation."""
        console = Mock(spec=Console)

        paginated_display = create_paginated_display(console, 25)

        assert isinstance(paginated_display, PaginatedTableDisplay)
        assert paginated_display.console == console
        assert paginated_display.page_size == 25

    def test_create_paginated_display_default(self):
        """Test factory function with default page size."""
        console = Mock(spec=Console)

        paginated_display = create_paginated_display(console)

        assert isinstance(paginated_display, PaginatedTableDisplay)
        assert paginated_display.page_size == 50


@pytest.mark.unit
class TestPaginationConfig:
    """Test the PaginationConfig class."""

    def test_default_page_sizes(self):
        """Test default page size constants."""
        assert PaginationConfig.DEFAULT_API_PAGE_SIZE == 100
        assert PaginationConfig.DEFAULT_DISPLAY_PAGE_SIZE == 50

    def test_max_results_per_entity(self):
        """Test max results configuration."""
        assert PaginationConfig.MAX_RESULTS_PER_ENTITY["issues"] == 10000
        assert PaginationConfig.MAX_RESULTS_PER_ENTITY["projects"] == 1000
        assert PaginationConfig.MAX_RESULTS_PER_ENTITY["users"] == 5000
        assert PaginationConfig.MAX_RESULTS_PER_ENTITY["articles"] == 2000

    def test_pagination_support(self):
        """Test pagination type mapping."""
        assert PaginationConfig.PAGINATION_SUPPORT["/api/issues"] == PaginationType.CURSOR
        assert PaginationConfig.PAGINATION_SUPPORT["/api/admin/projects"] == PaginationType.OFFSET
        assert PaginationConfig.PAGINATION_SUPPORT["/api/users"] == PaginationType.OFFSET
        assert PaginationConfig.PAGINATION_SUPPORT["/api/articles"] == PaginationType.OFFSET

    def test_get_pagination_type(self):
        """Test pagination type detection."""
        assert PaginationConfig.get_pagination_type("/api/issues") == PaginationType.CURSOR
        assert PaginationConfig.get_pagination_type("/api/admin/projects") == PaginationType.OFFSET
        assert PaginationConfig.get_pagination_type("/api/unknown") == PaginationType.OFFSET  # default


@pytest.mark.asyncio
class TestPaginateResults:
    """Test the paginate_results function."""

    async def test_cursor_pagination_single_page(self):
        """Test cursor pagination with single page of results."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [{"id": 1}, {"id": 2}],
            "hasAfter": False,
            "hasBefore": False,
            "afterCursor": None,
            "beforeCursor": None,
        }

        with patch("youtrack_cli.utils.make_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response

            result = await paginate_results(
                endpoint="/api/issues",
                headers={"Authorization": "Bearer token"},
                params={"fields": "id,summary"},
                page_size=100,
                use_cursor_pagination=True,
            )

            assert result["results"] == [{"id": 1}, {"id": 2}]
            assert result["total_results"] == 2
            assert result["has_after"] is False
            assert result["pagination_type"] == "cursor"
            mock_request.assert_called_once()

    async def test_cursor_pagination_multiple_pages(self):
        """Test cursor pagination with multiple pages."""
        # First page response
        first_response = Mock()
        first_response.json.return_value = {
            "results": [{"id": 1}, {"id": 2}],
            "hasAfter": True,
            "hasBefore": False,
            "afterCursor": "cursor123",
            "beforeCursor": None,
        }

        # Second page response
        second_response = Mock()
        second_response.json.return_value = {
            "results": [{"id": 3}, {"id": 4}],
            "hasAfter": False,
            "hasBefore": True,
            "afterCursor": None,
            "beforeCursor": "cursor456",
        }

        with patch("youtrack_cli.utils.make_request", new_callable=AsyncMock) as mock_request:
            mock_request.side_effect = [first_response, second_response]

            result = await paginate_results(
                endpoint="/api/issues",
                headers={"Authorization": "Bearer token"},
                params={"fields": "id,summary"},
                page_size=2,
                use_cursor_pagination=True,
            )

            assert result["results"] == [{"id": 1}, {"id": 2}, {"id": 3}, {"id": 4}]
            assert result["total_results"] == 4
            assert result["has_after"] is False
            assert result["pagination_type"] == "cursor"
            assert mock_request.call_count == 2

    async def test_offset_pagination_single_page(self):
        """Test offset pagination with single page."""
        mock_response = Mock()
        mock_response.json.return_value = [{"id": 1}, {"id": 2}]

        with patch("youtrack_cli.utils.make_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response

            result = await paginate_results(
                endpoint="/api/users",
                headers={"Authorization": "Bearer token"},
                params={"fields": "id,login"},
                page_size=100,
                use_cursor_pagination=False,
            )

            assert result["results"] == [{"id": 1}, {"id": 2}]
            assert result["total_results"] == 2
            assert result["pagination_type"] == "offset"
            mock_request.assert_called_once()

    async def test_offset_pagination_multiple_pages(self):
        """Test offset pagination with multiple pages."""
        # First page response (full page)
        first_response = Mock()
        first_response.json.return_value = [{"id": 1}, {"id": 2}]

        # Second page response (partial page, indicating end)
        second_response = Mock()
        second_response.json.return_value = [{"id": 3}]

        with patch("youtrack_cli.utils.make_request", new_callable=AsyncMock) as mock_request:
            mock_request.side_effect = [first_response, second_response]

            result = await paginate_results(
                endpoint="/api/users",
                headers={"Authorization": "Bearer token"},
                params={"fields": "id,login"},
                page_size=2,
                use_cursor_pagination=False,
            )

            assert result["results"] == [{"id": 1}, {"id": 2}, {"id": 3}]
            assert result["total_results"] == 3
            assert result["pagination_type"] == "offset"
            assert mock_request.call_count == 2

    async def test_max_results_limit(self):
        """Test that max_results is respected."""
        mock_response = Mock()
        mock_response.json.return_value = [{"id": i} for i in range(10)]

        with patch("youtrack_cli.utils.make_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response

            result = await paginate_results(
                endpoint="/api/users",
                headers={"Authorization": "Bearer token"},
                params={"fields": "id,login"},
                page_size=10,
                max_results=5,
                use_cursor_pagination=False,
            )

            assert len(result["results"]) == 5
            assert result["total_results"] == 5
            # Should have called with $top=5 to limit the request
            mock_request.assert_called_once()
            call_params = mock_request.call_args[1]["params"]
            assert call_params["$top"] == "5"

    async def test_auto_detect_pagination_type(self):
        """Test automatic pagination type detection."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [{"id": 1}],
            "hasAfter": False,
            "hasBefore": False,
        }

        with patch("youtrack_cli.utils.make_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response

            # Should auto-detect cursor pagination for /api/issues
            result = await paginate_results(
                endpoint="/api/issues",
                headers={"Authorization": "Bearer token"},
                params={"fields": "id,summary"},
                use_cursor_pagination=None,  # Auto-detect
            )

            assert result["pagination_type"] == "cursor"

    async def test_error_handling(self):
        """Test error handling in pagination."""
        with patch("youtrack_cli.utils.make_request", new_callable=AsyncMock) as mock_request:
            mock_request.side_effect = Exception("Network error")

            with pytest.raises(Exception, match="Network error"):
                await paginate_results(
                    endpoint="/api/users",
                    headers={"Authorization": "Bearer token"},
                    params={"fields": "id,login"},
                )

    async def test_invalid_cursor_params(self):
        """Test validation of cursor parameters."""
        with pytest.raises(ValueError, match="Cannot specify both after_cursor and before_cursor"):
            await paginate_results(
                endpoint="/api/issues",
                headers={"Authorization": "Bearer token"},
                after_cursor="cursor1",
                before_cursor="cursor2",
                use_cursor_pagination=True,
            )
