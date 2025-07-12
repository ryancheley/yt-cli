"""Pagination infrastructure for table displays."""

import math
from typing import Any, Callable, List

from rich.console import Console
from rich.table import Table
from rich.text import Text


class PaginatedTableDisplay:
    """Handle paginated display of table data with user navigation controls."""

    def __init__(self, console: Console, page_size: int = 50):
        """Initialize paginated table display.

        Args:
            console: Rich console instance for output
            page_size: Number of items per page (default: 50)
        """
        self.console = console
        self.page_size = page_size
        self.current_page = 1

    def display_paginated_table(
        self,
        data: List[Any],
        table_builder: Callable[[List[Any]], Table],
        title: str = "Results",
        show_all: bool = False,
        start_page: int = 1,
    ) -> None:
        """Display data in a paginated table format.

        Args:
            data: List of data items to display
            table_builder: Function that takes a list of items and returns a Rich Table
            title: Title for the table display
            show_all: If True, display all results without pagination
            start_page: Page number to start displaying from
        """
        if not data:
            self.console.print(f"No {title.lower()} found.", style="yellow")
            return

        # Show all results if requested or if data is small
        if show_all or len(data) <= self.page_size:
            table = table_builder(data)
            self.console.print(table)
            return

        total_pages = math.ceil(len(data) / self.page_size)
        self.current_page = max(1, min(start_page, total_pages))

        while True:
            # Calculate page boundaries
            start_idx = (self.current_page - 1) * self.page_size
            end_idx = min(start_idx + self.page_size, len(data))
            page_data = data[start_idx:end_idx]

            # Display the table for current page
            table = table_builder(page_data)
            self.console.print(table)

            # Display pagination info
            self._display_pagination_info(self.current_page, total_pages, len(data))

            # Show navigation options
            action = self._get_user_action(total_pages)

            if action == "quit":
                break
            elif action == "next" and self.current_page < total_pages:
                self.current_page += 1
            elif action == "previous" and self.current_page > 1:
                self.current_page -= 1
            elif action == "show_all":
                table = table_builder(data)
                self.console.print(table)
                break
            elif action.startswith("jump_"):
                try:
                    page_num = int(action.split("_")[1])
                    if 1 <= page_num <= total_pages:
                        self.current_page = page_num
                    else:
                        self.console.print(
                            f"[red]Invalid page number. Please enter a number between 1 and {total_pages}.[/red]"
                        )
                except (ValueError, IndexError):
                    self.console.print("[red]Invalid page number format.[/red]")

    def _display_pagination_info(self, current_page: int, total_pages: int, total_items: int) -> None:
        """Display pagination information."""
        start_item = (current_page - 1) * self.page_size + 1
        end_item = min(current_page * self.page_size, total_items)

        info_text = Text()
        info_text.append(f"Page {current_page} of {total_pages} ", style="cyan")
        info_text.append(f"(showing items {start_item}-{end_item} of {total_items})", style="dim")

        self.console.print(info_text)

    def _get_user_action(self, total_pages: int) -> str:
        """Get user action for navigation.

        Returns:
            Action string: 'next', 'previous', 'jump_N', 'show_all', or 'quit'
        """
        options = []
        if self.current_page > 1:
            options.append("[bold]p[/bold]revious")
        if self.current_page < total_pages:
            options.append("[bold]n[/bold]ext")
        options.extend(["[bold]j[/bold]ump to page", "[bold]a[/bold]ll (show all results)", "[bold]q[/bold]uit"])

        self.console.print(f"Options: {' | '.join(options)}")

        while True:
            try:
                user_input = input("Enter your choice: ").strip().lower()

                if user_input in ["q", "quit", ""]:
                    return "quit"
                elif user_input in ["n", "next"] and self.current_page < total_pages:
                    return "next"
                elif user_input in ["p", "previous", "prev"] and self.current_page > 1:
                    return "previous"
                elif user_input in ["a", "all"]:
                    return "show_all"
                elif user_input in ["j", "jump"]:
                    page_input = input(f"Enter page number (1-{total_pages}): ").strip()
                    try:
                        page_num = int(page_input)
                        if 1 <= page_num <= total_pages:
                            return f"jump_{page_num}"
                        else:
                            self.console.print(f"[red]Please enter a number between 1 and {total_pages}.[/red]")
                    except ValueError:
                        self.console.print("[red]Please enter a valid number.[/red]")
                else:
                    # Try to parse as direct page number
                    try:
                        page_num = int(user_input)
                        if 1 <= page_num <= total_pages:
                            return f"jump_{page_num}"
                        else:
                            self.console.print(f"[red]Please enter a number between 1 and {total_pages}.[/red]")
                    except ValueError:
                        self.console.print("[red]Invalid option. Please try again.[/red]")

            except (EOFError, KeyboardInterrupt):
                return "quit"


def create_paginated_display(console: Console, page_size: int = 50) -> PaginatedTableDisplay:
    """Factory function to create a paginated display instance.

    Args:
        console: Rich console instance
        page_size: Number of items per page

    Returns:
        PaginatedTableDisplay instance
    """
    return PaginatedTableDisplay(console, page_size)
