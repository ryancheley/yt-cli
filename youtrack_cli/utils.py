"""Utility functions for YouTrack CLI."""

import asyncio
import json
from typing import Any, Optional

import httpx
from rich.console import Console

from .exceptions import (
    AuthenticationError,
    ConnectionError,
    NotFoundError,
    PermissionError,
    RateLimitError,
    YouTrackError,
)
from .logging import get_logger

logger = get_logger(__name__)
console = Console()


async def make_request(
    method: str,
    url: str,
    headers: Optional[dict[str, str]] = None,
    params: Optional[dict[str, Any]] = None,
    json_data: Optional[dict[str, Any]] = None,
    timeout: int = 30,
    max_retries: int = 3,
) -> httpx.Response:
    """Make an HTTP request with retry logic and proper error handling.

    Args:
        method: HTTP method (GET, POST, etc.)
        url: Request URL
        headers: Optional request headers
        params: Optional query parameters
        json_data: Optional JSON data for POST/PUT requests
        timeout: Request timeout in seconds
        max_retries: Maximum number of retry attempts

    Returns:
        HTTP response object

    Raises:
        YouTrackError: Various specific error types based on response
    """
    headers = headers or {}

    for attempt in range(max_retries + 1):
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                logger.debug(
                    f"Making {method} request to {url} (attempt {attempt + 1})"
                )

                response = await client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    json=json_data,
                )

                # Handle specific HTTP status codes
                if response.status_code == 200 or response.status_code == 201:
                    logger.debug(f"Request successful: {response.status_code}")
                    return response
                elif response.status_code == 401:
                    raise AuthenticationError("Invalid credentials or token expired")
                elif response.status_code == 403:
                    raise PermissionError("access this resource")
                elif response.status_code == 404:
                    raise NotFoundError("Resource", url.split("/")[-1])
                elif response.status_code == 429:
                    retry_after = response.headers.get("Retry-After")
                    retry_seconds = int(retry_after) if retry_after else 60
                    raise RateLimitError(retry_seconds)
                else:
                    # Try to get error details from response
                    try:
                        error_data = response.json()
                        error_message = error_data.get("error", {}).get(
                            "description", response.text
                        )
                    except (json.JSONDecodeError, AttributeError):
                        error_message = response.text or f"HTTP {response.status_code}"

                    raise YouTrackError(
                        f"Request failed with status {response.status_code}: "
                        f"{error_message}"
                    )

        except httpx.TimeoutException:
            if attempt < max_retries:
                wait_time = 2**attempt  # Exponential backoff
                logger.warning(f"Request timed out, retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)
                continue
            else:
                raise ConnectionError(
                    "Request timed out after multiple attempts"
                ) from None

        except httpx.ConnectError:
            if attempt < max_retries:
                wait_time = 2**attempt
                logger.warning(f"Connection failed, retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)
                continue
            else:
                raise ConnectionError("Unable to connect to YouTrack server") from None

        except (RateLimitError, AuthenticationError, PermissionError, NotFoundError):
            # Don't retry these errors
            raise

        except Exception as e:
            if attempt < max_retries:
                wait_time = 2**attempt
                logger.warning(f"Unexpected error, retrying in {wait_time}s: {e}")
                await asyncio.sleep(wait_time)
                continue
            else:
                raise YouTrackError(f"Unexpected error: {str(e)}") from e

    # Should never reach here, but just in case
    raise YouTrackError("Maximum retry attempts exceeded")


def handle_error(error: Exception, operation: str = "operation") -> dict[str, Any]:
    """Handle and format errors for CLI output.

    Args:
        error: The exception that occurred
        operation: Description of the operation that failed

    Returns:
        Dictionary with error information for CLI display
    """
    if isinstance(error, YouTrackError):
        result = {
            "status": "error",
            "message": error.message,
        }
        if error.suggestion:
            result["suggestion"] = error.suggestion
        return result
    else:
        logger.error(f"Unexpected error during {operation}: {error}")
        return {
            "status": "error",
            "message": f"An unexpected error occurred during {operation}",
            "suggestion": "Please try again or contact support if the problem persists",
        }


def display_error(error_result: dict[str, Any]) -> None:
    """Display an error message to the user.

    Args:
        error_result: Error information dictionary from handle_error()
    """
    console.print(f"[red]Error:[/red] {error_result['message']}")

    if "suggestion" in error_result:
        console.print(f"[yellow]Suggestion:[/yellow] {error_result['suggestion']}")


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
