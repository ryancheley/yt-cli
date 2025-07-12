"""Progress indicator utilities for YouTrack CLI.

This module provides a unified way to show progress indicators for long-running
operations using Rich progress bars and spinners.
"""

import contextlib
from collections.abc import Generator
from typing import Any, Callable, Optional, TypeVar

from rich.console import Console
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TaskID,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)

from .console import get_console

T = TypeVar("T")


class ProgressManager:
    """Manages progress indicators for the YouTrack CLI."""

    def __init__(self, console: Optional[Console] = None, enabled: bool = True):
        """Initialize the progress manager.

        Args:
            console: Rich console instance to use for output
            enabled: Whether progress indicators are enabled
        """
        self.console = console or get_console()
        self.enabled = enabled

    @contextlib.contextmanager
    def spinner(self, description: str = "Working...") -> Generator[None, None, None]:
        """Show a spinner for indeterminate progress operations.

        Args:
            description: Text to display next to the spinner

        Yields:
            None
        """
        if not self.enabled:
            yield
            return

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
            transient=True,
        ) as progress:
            progress.add_task(description, total=None)
            yield

    @contextlib.contextmanager
    def progress_bar(
        self,
        description: str,
        total: Optional[int] = None,
        show_percentage: bool = True,
        show_time: bool = True,
    ) -> Generator["ProgressTracker", None, None]:
        """Show a progress bar for determinate progress operations.

        Args:
            description: Text to display next to the progress bar
            total: Total number of items to process
            show_percentage: Whether to show percentage completion
            show_time: Whether to show time elapsed and remaining

        Yields:
            ProgressTracker: Object to update progress
        """
        if not self.enabled:
            yield _DummyTracker()
            return

        columns = [
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
        ]

        if total is not None:
            columns.extend(
                [
                    BarColumn(),
                    MofNCompleteColumn(),
                ]
            )

            if show_percentage:
                columns.append(TextColumn("[progress.percentage]{task.percentage:>3.0f}%"))

        if show_time:
            columns.append(TimeElapsedColumn())
            if total is not None:
                columns.append(TimeRemainingColumn())

        with Progress(*columns, console=self.console, transient=True) as progress:
            task_id = progress.add_task(description, total=total)
            yield ProgressTracker(progress, task_id)

    def process_with_progress(
        self,
        items: list[T],
        processor: Callable[[T], Any],
        description: str = "Processing items...",
        show_percentage: bool = True,
        show_time: bool = True,
    ) -> list[Any]:
        """Process a list of items with a progress bar.

        Args:
            items: List of items to process
            processor: Function to process each item
            description: Text to display next to the progress bar
            show_percentage: Whether to show percentage completion
            show_time: Whether to show time elapsed and remaining

        Returns:
            List of processing results
        """
        results = []
        with self.progress_bar(
            description,
            total=len(items),
            show_percentage=show_percentage,
            show_time=show_time,
        ) as tracker:
            for item in items:
                result = processor(item)
                results.append(result)
                tracker.advance()
        return results


class ProgressTracker:
    """Tracks progress for a specific task."""

    def __init__(self, progress: Progress, task_id: TaskID):
        """Initialize the progress tracker.

        Args:
            progress: Rich Progress instance
            task_id: Task ID to update
        """
        self.progress = progress
        self.task_id = task_id

    def advance(self, step: int = 1) -> None:
        """Advance the progress by the specified step.

        Args:
            step: Number of steps to advance
        """
        self.progress.update(self.task_id, advance=step)

    def update(
        self,
        completed: Optional[int] = None,
        total: Optional[int] = None,
        description: Optional[str] = None,
    ) -> None:
        """Update progress information.

        Args:
            completed: Number of completed items
            total: Total number of items
            description: New description text
        """
        kwargs = {}
        if completed is not None:
            kwargs["completed"] = completed
        if total is not None:
            kwargs["total"] = total
        if description is not None:
            kwargs["description"] = description

        if kwargs:
            self.progress.update(self.task_id, **kwargs)


class _DummyTracker:
    """Dummy progress tracker that does nothing when progress is disabled."""

    def advance(self, step: int = 1) -> None:
        """No-op advance method."""
        pass

    def update(
        self,
        completed: Optional[int] = None,
        total: Optional[int] = None,
        description: Optional[str] = None,
    ) -> None:
        """No-op update method."""
        pass


# Global progress manager instance
_progress_manager: Optional[ProgressManager] = None


def get_progress_manager() -> ProgressManager:
    """Get the global progress manager instance."""
    global _progress_manager
    if _progress_manager is None:
        _progress_manager = ProgressManager()
    # Type checker should understand _progress_manager is not None here
    return _progress_manager  # type: ignore[return-value]


def set_progress_enabled(enabled: bool) -> None:
    """Enable or disable progress indicators globally.

    Args:
        enabled: Whether to enable progress indicators
    """
    global _progress_manager
    if _progress_manager is None:
        _progress_manager = ProgressManager(enabled=enabled)
    else:
        _progress_manager.enabled = enabled  # type: ignore[union-attr]


def with_spinner(description: str = "Working..."):
    """Decorator to show a spinner during function execution.

    Args:
        description: Text to display next to the spinner
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            with get_progress_manager().spinner(description):
                return func(*args, **kwargs)

        return wrapper

    return decorator
