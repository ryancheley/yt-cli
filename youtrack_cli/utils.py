"""Utility functions for YouTrack CLI.

This module provides common utility functions for HTTP requests, error handling,
user interface operations, and data processing used throughout the YouTrack CLI.

The utilities provide consistent interfaces for API interactions, response
handling, and user feedback with proper error handling and logging.
"""

from collections.abc import AsyncGenerator
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

import httpx

from .client import get_client_manager
from .console import get_console
from .exceptions import (
    CommandValidationError,
    ParameterError,
    UsageError,
    YouTrackError,
)
from .logging import get_logger

__all__ = [
    "make_request",
    "handle_error",
    "display_error",
    "display_success",
    "display_info",
    "display_warning",
    "paginate_results",
    "paginate_issues",
    "paginate_projects",
    "paginate_users",
    "paginate_articles",
    "batch_requests",
    "batch_get_resources",
    "optimize_fields",
    "stream_large_response",
    "format_timestamp",
    "PaginationType",
    "PaginationConfig",
]

logger = get_logger(__name__)
console = get_console()


class PaginationType(Enum):
    """Supported pagination types in YouTrack API."""

    CURSOR = "cursor"
    OFFSET = "offset"


class PaginationConfig:
    """Centralized pagination configuration for different YouTrack API endpoints."""

    # Default page sizes for different operations
    DEFAULT_API_PAGE_SIZE = 100
    DEFAULT_DISPLAY_PAGE_SIZE = 50
    MAX_RESULTS_PER_ENTITY = {
        "issues": 10000,
        "projects": 1000,
        "users": 5000,
        "articles": 2000,
        "reports": 1000,
    }

    # Endpoint-specific pagination support
    PAGINATION_SUPPORT = {
        "/api/issues": PaginationType.CURSOR,
        "/api/admin/projects": PaginationType.OFFSET,
        "/api/users": PaginationType.OFFSET,
        "/api/articles": PaginationType.OFFSET,
    }

    @classmethod
    def get_pagination_type(cls, endpoint: str) -> PaginationType:
        """Determine the pagination type for a given endpoint.

        Args:
            endpoint: API endpoint path

        Returns:
            PaginationType enum indicating cursor or offset pagination
        """
        # Check direct matches first
        for pattern, pagination_type in cls.PAGINATION_SUPPORT.items():
            if pattern in endpoint:
                return pagination_type

        # Default to offset-based pagination for unknown endpoints
        logger.debug(f"Unknown endpoint pagination, defaulting to offset: {endpoint}")
        return PaginationType.OFFSET

    @classmethod
    def get_max_results(cls, entity_type: str) -> int:
        """Get maximum results limit for an entity type.

        Args:
            entity_type: Type of entity (issues, projects, users, etc.)

        Returns:
            Maximum number of results to fetch
        """
        return cls.MAX_RESULTS_PER_ENTITY.get(entity_type, 1000)


async def make_request(
    method: str,
    url: str,
    headers: Optional[Dict[str, str]] = None,
    params: Optional[Dict[str, Any]] = None,
    json_data: Optional[Dict[str, Any]] = None,
    timeout: Optional[float] = None,
    max_retries: int = 3,
) -> httpx.Response:
    """Make an HTTP request with retry logic and proper error handling.

    This is a backward-compatible wrapper around the HTTPClientManager
    that provides simplified request handling with automatic retries.

    Args:
        method: HTTP method (GET, POST, PUT, DELETE, etc.).
        url: Target request URL.
        headers: Optional HTTP headers to include.
        params: Optional query parameters.
        json_data: Optional JSON payload for request body.
        timeout: Request timeout in seconds. Uses client default if None.
        max_retries: Maximum number of retry attempts. Defaults to 3.

    Returns:
        httpx.Response: The HTTP response object.

    Raises:
        YouTrackError: For API-specific errors.
        httpx.HTTPError: For general HTTP errors.
    """
    client_manager = get_client_manager()
    return await client_manager.make_request(
        method=method,
        url=url,
        headers=headers,
        params=params,
        json_data=json_data,
        timeout=timeout,
        max_retries=max_retries,
    )


async def paginate_results(
    endpoint: str,
    headers: Optional[Dict[str, str]] = None,
    params: Optional[Dict[str, Any]] = None,
    page_size: Optional[int] = None,
    max_results: Optional[int] = None,
    after_cursor: Optional[str] = None,
    before_cursor: Optional[str] = None,
    use_cursor_pagination: Optional[bool] = None,
) -> Dict[str, Any]:
    """Efficiently paginate through large result sets with automatic pagination type detection.

    This function automatically detects whether to use cursor-based or offset-based
    pagination based on the endpoint, providing a unified interface for all YouTrack
    API pagination patterns.

    Args:
        endpoint: API endpoint URL
        headers: Optional request headers
        params: Optional query parameters
        page_size: Number of items per page (defaults to PaginationConfig.DEFAULT_API_PAGE_SIZE)
        max_results: Maximum number of results to fetch (None for all)
        after_cursor: Start pagination after this cursor (for cursor-based pagination)
        before_cursor: Start pagination before this cursor (for cursor-based pagination)
        use_cursor_pagination: Override automatic detection of pagination type (None for auto-detect)

    Returns:
        Dictionary with 'results' list and pagination metadata including:
        - results: List of paginated items
        - total_results: Total number of results fetched
        - has_after: Whether more results are available after current position
        - has_before: Whether results are available before current position
        - after_cursor: Cursor for next page (cursor pagination only)
        - before_cursor: Cursor for previous page (cursor pagination only)
        - pagination_type: Type of pagination used ("cursor" or "offset")

    Raises:
        YouTrackError: If any request fails
        ValueError: If invalid pagination parameters are provided
    """
    # Auto-detect pagination type if not specified
    if use_cursor_pagination is None:
        detected_type = PaginationConfig.get_pagination_type(endpoint)
        use_cursor_pagination = detected_type == PaginationType.CURSOR

    # Set default page size if not provided
    if page_size is None:
        page_size = PaginationConfig.DEFAULT_API_PAGE_SIZE

    # Validate pagination parameters
    if use_cursor_pagination and (after_cursor is not None or before_cursor is not None):
        # Cursor pagination with explicit cursors - validate
        if after_cursor and before_cursor:
            raise ValueError("Cannot specify both after_cursor and before_cursor simultaneously")

    # Initialize pagination state
    all_results = []
    skip = 0
    params = params or {}
    current_after_cursor = after_cursor
    current_before_cursor = before_cursor
    has_after = False
    has_before = False
    final_after_cursor = None
    final_before_cursor = None
    pagination_type = "cursor" if use_cursor_pagination else "offset"

    logger.debug(
        "Starting pagination",
        endpoint=endpoint,
        page_size=page_size,
        max_results=max_results,
        use_cursor_pagination=use_cursor_pagination,
        pagination_type=pagination_type,
        after_cursor=after_cursor,
        before_cursor=before_cursor,
    )

    while True:
        # Set pagination parameters
        page_params = params.copy()
        page_params["$top"] = str(page_size)

        if use_cursor_pagination:
            # Use cursor-based pagination
            if current_after_cursor:
                page_params["$after"] = current_after_cursor
            if current_before_cursor:
                page_params["$before"] = current_before_cursor
        else:
            # Use offset-based pagination (legacy)
            page_params["$skip"] = str(skip)

        # Check if we need to limit the current page size
        if max_results and (len(all_results) + page_size) > max_results:
            page_params["$top"] = str(max_results - len(all_results))

        logger.debug(
            "Fetching page",
            skip=skip if not use_cursor_pagination else None,
            after_cursor=current_after_cursor if use_cursor_pagination else None,
            before_cursor=current_before_cursor if use_cursor_pagination else None,
            top=page_params["$top"],
            total_fetched=len(all_results),
        )

        # Make the request
        response = await make_request(
            method="GET",
            url=endpoint,
            headers=headers,
            params=page_params,
        )

        # Parse response
        try:
            response_data = response.json()
            if use_cursor_pagination and isinstance(response_data, dict):
                # Handle YouTrackSearchResult format
                page_results = response_data.get("results", [])
                has_after = response_data.get("hasAfter", False)
                has_before = response_data.get("hasBefore", False)
                final_after_cursor = response_data.get("afterCursor")
                final_before_cursor = response_data.get("beforeCursor")
            elif isinstance(response_data, list):
                # Handle direct list responses (legacy format)
                page_results = response_data
            else:
                # Handle single object responses
                page_results = [response_data] if response_data else []
        except Exception as e:
            logger.error("Failed to parse JSON response", error=str(e))
            raise YouTrackError(f"Failed to parse response: {str(e)}") from e

        # Add results to our collection
        all_results.extend(page_results)

        logger.debug(
            "Page fetched",
            page_size=len(page_results),
            total_fetched=len(all_results),
            has_after=has_after if use_cursor_pagination else None,
            has_before=has_before if use_cursor_pagination else None,
        )

        # Check if we should continue
        if use_cursor_pagination:
            # For cursor pagination, check if there are more results
            if not has_after or len(page_results) == 0:
                break
            current_after_cursor = final_after_cursor
        else:
            # For offset pagination, check traditional conditions
            if (
                len(page_results) < page_size  # Less than a full page means we're done
                or len(page_results) == 0  # No more results
            ):
                break
            skip += page_size

        # Check if we hit our limit
        if max_results and len(all_results) >= max_results:
            break

    logger.debug(
        "Pagination complete",
        total_results=len(all_results),
        use_cursor_pagination=use_cursor_pagination,
    )

    # Trim to max_results if specified
    if max_results and len(all_results) > max_results:
        all_results = all_results[:max_results]

    # Return structured result with pagination metadata
    return {
        "results": all_results,
        "total_results": len(all_results),
        "has_after": has_after if use_cursor_pagination else len(all_results) >= (max_results or float("inf")),
        "has_before": has_before if use_cursor_pagination else skip > 0,
        "after_cursor": final_after_cursor if use_cursor_pagination else None,
        "before_cursor": final_before_cursor if use_cursor_pagination else None,
        "pagination_type": pagination_type,
    }


async def paginate_issues(
    endpoint: str,
    headers: Optional[Dict[str, str]] = None,
    params: Optional[Dict[str, Any]] = None,
    page_size: Optional[int] = None,
    max_results: Optional[int] = None,
    after_cursor: Optional[str] = None,
    before_cursor: Optional[str] = None,
) -> Dict[str, Any]:
    """Paginate through issues using cursor-based pagination.

    This is a convenience wrapper around paginate_results specifically for issues,
    which always use cursor-based pagination.

    Args:
        endpoint: Issues API endpoint URL
        headers: Optional request headers
        params: Optional query parameters
        page_size: Number of items per page
        max_results: Maximum number of results to fetch
        after_cursor: Start pagination after this cursor
        before_cursor: Start pagination before this cursor

    Returns:
        Dictionary with 'results' list and cursor pagination metadata
    """
    effective_max_results = max_results or PaginationConfig.get_max_results("issues")

    return await paginate_results(
        endpoint=endpoint,
        headers=headers,
        params=params,
        page_size=page_size,
        max_results=effective_max_results,
        after_cursor=after_cursor,
        before_cursor=before_cursor,
        use_cursor_pagination=True,
    )


async def paginate_projects(
    endpoint: str,
    headers: Optional[Dict[str, str]] = None,
    params: Optional[Dict[str, Any]] = None,
    page_size: Optional[int] = None,
    max_results: Optional[int] = None,
) -> Dict[str, Any]:
    """Paginate through projects using offset-based pagination.

    This is a convenience wrapper around paginate_results specifically for projects,
    which use offset-based pagination.

    Args:
        endpoint: Projects API endpoint URL
        headers: Optional request headers
        params: Optional query parameters
        page_size: Number of items per page
        max_results: Maximum number of results to fetch

    Returns:
        Dictionary with 'results' list and offset pagination metadata
    """
    effective_max_results = max_results or PaginationConfig.get_max_results("projects")

    return await paginate_results(
        endpoint=endpoint,
        headers=headers,
        params=params,
        page_size=page_size,
        max_results=effective_max_results,
        use_cursor_pagination=False,
    )


async def paginate_users(
    endpoint: str,
    headers: Optional[Dict[str, str]] = None,
    params: Optional[Dict[str, Any]] = None,
    page_size: Optional[int] = None,
    max_results: Optional[int] = None,
) -> Dict[str, Any]:
    """Paginate through users using offset-based pagination.

    This is a convenience wrapper around paginate_results specifically for users,
    which use offset-based pagination.

    Args:
        endpoint: Users API endpoint URL
        headers: Optional request headers
        params: Optional query parameters
        page_size: Number of items per page
        max_results: Maximum number of results to fetch

    Returns:
        Dictionary with 'results' list and offset pagination metadata
    """
    effective_max_results = max_results or PaginationConfig.get_max_results("users")

    return await paginate_results(
        endpoint=endpoint,
        headers=headers,
        params=params,
        page_size=page_size,
        max_results=effective_max_results,
        use_cursor_pagination=False,
    )


async def paginate_articles(
    endpoint: str,
    headers: Optional[Dict[str, str]] = None,
    params: Optional[Dict[str, Any]] = None,
    page_size: Optional[int] = None,
    max_results: Optional[int] = None,
) -> Dict[str, Any]:
    """Paginate through articles using offset-based pagination.

    This is a convenience wrapper around paginate_results specifically for articles,
    which use offset-based pagination.

    Args:
        endpoint: Articles API endpoint URL
        headers: Optional request headers
        params: Optional query parameters
        page_size: Number of items per page
        max_results: Maximum number of results to fetch

    Returns:
        Dictionary with 'results' list and offset pagination metadata
    """
    effective_max_results = max_results or PaginationConfig.get_max_results("articles")

    return await paginate_results(
        endpoint=endpoint,
        headers=headers,
        params=params,
        page_size=page_size,
        max_results=effective_max_results,
        use_cursor_pagination=False,
    )


async def batch_requests(
    requests: List[Dict[str, Any]],
    max_concurrent: int = 10,
) -> list[httpx.Response]:
    """Execute multiple HTTP requests concurrently.

    Args:
        requests: List of request dictionaries with keys: method, url, headers,
            params, json_data
        max_concurrent: Maximum number of concurrent requests

    Returns:
        List of HTTP responses in the same order as input requests
    """
    client_manager = get_client_manager()
    return await client_manager.batch_requests(requests, max_concurrent)


async def batch_get_resources(
    base_url: str,
    resource_ids: list[str],
    headers: Optional[Dict[str, str]] = None,
    max_concurrent: int = 10,
) -> List[Dict[str, Any]]:
    """Batch fetch multiple resources by ID.

    Args:
        base_url: Base URL pattern with {id} placeholder (e.g., "https://api.com/issues/{id}")
        resource_ids: List of resource IDs to fetch
        headers: Optional request headers
        max_concurrent: Maximum number of concurrent requests

    Returns:
        List of resource data in the same order as input IDs

    Example:
        resources = await batch_get_resources(
            "https://youtrack.example.com/api/issues/{id}",
            ["PROJ-1", "PROJ-2", "PROJ-3"],
            headers=auth_headers
        )
    """
    if "{id}" not in base_url:
        raise ValueError("base_url must contain {id} placeholder")

    # Build requests for each resource
    requests = []
    for resource_id in resource_ids:
        url = base_url.format(id=resource_id)
        requests.append(
            {
                "method": "GET",
                "url": url,
                "headers": headers,
            }
        )

    logger.debug(
        "Batch fetching resources",
        count=len(resource_ids),
        max_concurrent=max_concurrent,
    )

    # Execute batch requests
    responses = await batch_requests(requests, max_concurrent)

    # Parse JSON responses
    results = []
    for i, response in enumerate(responses):
        try:
            if response.status_code in (200, 201):
                results.append(response.json())
            else:
                logger.warning(
                    "Failed to fetch resource in batch",
                    resource_id=resource_ids[i],
                    status_code=response.status_code,
                )
                results.append(None)
        except Exception as e:
            logger.error(
                "Failed to parse response in batch",
                resource_id=resource_ids[i],
                error=str(e),
            )
            results.append(None)

    logger.debug(
        "Batch fetch complete",
        total=len(resource_ids),
        successful=sum(1 for r in results if r is not None),
        failed=sum(1 for r in results if r is None),
    )

    return results


def optimize_fields(
    base_params: Optional[Dict[str, Any]] = None,
    fields: Optional[list[str]] = None,
    exclude_fields: Optional[list[str]] = None,
) -> Dict[str, Any]:
    """Optimize API request parameters by selecting only needed fields.

    Args:
        base_params: Base query parameters
        fields: List of fields to include (YouTrack $select)
        exclude_fields: List of fields to exclude

    Returns:
        Optimized parameters dictionary

    Example:
        params = optimize_fields(
            base_params={"project": "PROJ"},
            fields=["id", "summary", "state"],
            exclude_fields=["description"]
        )
    """
    params = (base_params or {}).copy()

    if fields:
        # Build YouTrack field selection syntax
        field_str = ",".join(fields)
        params["fields"] = field_str
        logger.debug("Field selection applied", fields=fields)

    # Note: YouTrack doesn't have a direct exclude syntax like some APIs,
    # but we can log the intention for potential client-side filtering
    if exclude_fields:
        logger.debug("Fields to exclude noted", exclude_fields=exclude_fields)
        # Store for potential client-side filtering
        params["_exclude_fields"] = exclude_fields

    return params


async def stream_large_response(
    url: str,
    headers: Optional[Dict[str, str]] = None,
    params: Optional[Dict[str, Any]] = None,
    chunk_size: int = 8192,
) -> AsyncGenerator[bytes, None]:
    """Stream a large response to avoid memory issues.

    Args:
        url: Request URL
        headers: Optional request headers
        params: Optional query parameters
        chunk_size: Size of chunks to yield

    Yields:
        Bytes chunks from the response

    Example:
        async for chunk in stream_large_response(download_url):
            file.write(chunk)
    """
    client_manager = get_client_manager()

    async with client_manager.get_client() as client:
        logger.debug("Starting streaming download", url=url, chunk_size=chunk_size)

        async with client.stream(
            "GET",
            url,
            headers=headers,
            params=params,
        ) as response:
            # Check if response is successful
            if response.status_code not in (200, 201):
                error_text = await response.aread()
                raise YouTrackError(
                    f"Stream request failed with status {response.status_code}: "
                    f"{error_text.decode('utf-8', errors='ignore')}"
                )

            total_bytes = 0
            async for chunk in response.aiter_bytes(chunk_size):
                total_bytes += len(chunk)
                yield chunk

            logger.debug("Streaming download complete", total_bytes=total_bytes)


def handle_error(error: Exception, operation: str = "operation") -> Dict[str, Any]:
    """Handle and format errors for CLI output.

    Args:
        error: The exception that occurred
        operation: Description of the operation that failed

    Returns:
        Dictionary with error information for CLI display
    """
    if isinstance(error, YouTrackError):
        logger.error(
            "YouTrack operation failed",
            operation=operation,
            error_type=type(error).__name__,
            message=error.message,
        )
        result = {
            "status": "error",
            "message": error.message,
        }
        if error.suggestion:
            result["suggestion"] = error.suggestion

        # Add special handling for enhanced error types
        if isinstance(error, UsageError):
            result["usage_syntax"] = error.usage_syntax
            result["examples"] = error.examples
            result["common_mistakes"] = error.common_mistakes
        elif isinstance(error, CommandValidationError):
            result["similar_commands"] = error.similar_commands
            result["usage_example"] = error.usage_example
        elif isinstance(error, ParameterError):
            result["parameter_name"] = error.parameter_name
            result["valid_choices"] = error.valid_choices
            result["usage_example"] = error.usage_example

        return result
    logger.error(
        "Unexpected error during operation",
        operation=operation,
        error_type=type(error).__name__,
        error=str(error),
    )
    return {
        "status": "error",
        "message": f"An unexpected error occurred during {operation}",
        "suggestion": "Please try again or contact support if the problem persists",
    }


def display_error(error_result: Dict[str, Any]) -> None:
    """Display an error message to the user.

    Args:
        error_result: Error information dictionary from handle_error()
    """
    console.print(f"[red]❌ Error:[/red] {error_result['message']}")

    # Handle enhanced error types with rich formatting
    if "usage_syntax" in error_result:
        # UsageError with comprehensive formatting
        console.print(f"\n[blue]Usage:[/blue] {error_result['usage_syntax']}")

        if error_result.get("examples"):
            console.print("\n[green]Examples:[/green]")
            for i, example in enumerate(error_result["examples"], 1):
                console.print(f"  {i}. [cyan]{example}[/cyan]")

        if error_result.get("common_mistakes"):
            console.print("\n[yellow]Common mistakes to avoid:[/yellow]")
            for mistake in error_result["common_mistakes"]:
                console.print(f"  • [dim]{mistake}[/dim]")

    elif "similar_commands" in error_result and error_result["similar_commands"]:
        # CommandValidationError with suggestions
        console.print(f"[yellow]💡 Did you mean:[/yellow] {', '.join(error_result['similar_commands'])}")
        if error_result.get("usage_example"):
            console.print(f"[blue]Usage:[/blue] {error_result['usage_example']}")

    elif "parameter_name" in error_result:
        # ParameterError with specific guidance
        if error_result.get("valid_choices"):
            choices_str = ", ".join(error_result["valid_choices"])
            console.print(f"[yellow]Valid choices:[/yellow] {choices_str}")
        if error_result.get("usage_example"):
            console.print(f"[blue]Example:[/blue] {error_result['usage_example']}")

    elif "suggestion" in error_result:
        # Standard suggestion display
        console.print(f"[yellow]💡 Suggestion:[/yellow] {error_result['suggestion']}")


def display_success(message: str) -> None:
    """Display a success message to the user.

    Args:
        message: Success message to display
    """
    console.print(f"[green]Success:[/green] {message}")


def display_info(message: str) -> None:
    """Display an info message to the user.

    Args:
        message: Info message to display
    """
    console.print(f"[blue]Info:[/blue] {message}")


def display_warning(message: str) -> None:
    """Display a warning message to the user.

    Args:
        message: Warning message to display
    """
    console.print(f"[yellow]Warning:[/yellow] {message}")


def format_timestamp(timestamp: Union[int, str, None]) -> str:
    """Format a timestamp value for display.

    Args:
        timestamp: Unix timestamp (int), ISO string, or None

    Returns:
        Formatted timestamp string or "N/A" if None/empty
    """
    if timestamp is None:
        return "N/A"

    try:
        if isinstance(timestamp, int):
            # Unix timestamp in milliseconds (YouTrack format)
            dt = datetime.fromtimestamp(timestamp / 1000)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        if isinstance(timestamp, str) and timestamp.strip():
            # Try to parse ISO format or other string formats
            if timestamp.isdigit():
                # String representation of timestamp
                dt = datetime.fromtimestamp(int(timestamp) / 1000)
                return dt.strftime("%Y-%m-%d %H:%M:%S")
            # Assume it's already formatted or ISO format
            try:
                dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                return dt.strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                # Return as-is if we can't parse it
                return str(timestamp)
        else:
            return "N/A"
    except (ValueError, TypeError, OverflowError):
        logger.warning("Failed to format timestamp", timestamp=timestamp)
        return str(timestamp) if timestamp else "N/A"
