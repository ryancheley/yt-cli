"""Tests for pagination functionality."""

from unittest.mock import Mock, patch

from rich.console import Console
from rich.table import Table

from youtrack_cli.pagination import PaginatedTableDisplay, create_paginated_display


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
