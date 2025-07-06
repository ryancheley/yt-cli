"""HTTP client manager with connection pooling and performance optimizations."""

import asyncio
import time
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any, Optional

import httpx

from .cache import get_cache
from .exceptions import (
    AuthenticationError,
    ConnectionError,
    NotFoundError,
    PermissionError,
    RateLimitError,
    YouTrackError,
)
from .logging import get_logger, log_api_call

__all__ = [
    "HTTPClientManager",
    "get_client_manager",
]

logger = get_logger(__name__)


class HTTPClientManager:
    """Manages HTTP connections with pooling and performance optimizations."""

    def __init__(
        self,
        max_keepalive_connections: int = 20,
        max_connections: int = 100,
        keepalive_expiry: float = 30.0,
        default_timeout: float = 30.0,
        verify_ssl: bool = True,
    ):
        """Initialize the HTTP client manager.

        Args:
            max_keepalive_connections: Maximum number of keepalive connections
            max_connections: Maximum number of total connections
            keepalive_expiry: How long to keep idle connections alive (seconds)
            default_timeout: Default timeout for requests (seconds)
            verify_ssl: Whether to verify SSL certificates
        """
        self._limits = httpx.Limits(
            max_keepalive_connections=max_keepalive_connections,
            max_connections=max_connections,
            keepalive_expiry=keepalive_expiry,
        )
        self._timeout = httpx.Timeout(default_timeout)
        self._verify_ssl = verify_ssl
        self._client: Optional[httpx.AsyncClient] = None
        self._lock = asyncio.Lock()

    async def _ensure_client(self) -> httpx.AsyncClient:
        """Ensure the HTTP client is initialized."""
        if self._client is None or self._client.is_closed:
            async with self._lock:
                if self._client is None or self._client.is_closed:
                    self._client = httpx.AsyncClient(
                        limits=self._limits,
                        timeout=self._timeout,
                        follow_redirects=True,
                        verify=self._verify_ssl,
                    )
                    logger.debug(
                        "HTTP client initialized",
                        max_keepalive=self._limits.max_keepalive_connections,
                        max_connections=self._limits.max_connections,
                        verify_ssl=self._verify_ssl,
                    )
        return self._client

    @asynccontextmanager
    async def get_client(self) -> AsyncGenerator[httpx.AsyncClient, None]:
        """Get the HTTP client as a context manager."""
        client = await self._ensure_client()
        try:
            yield client
        except Exception:
            # Let the caller handle the exception
            raise

    async def close(self) -> None:
        """Close the HTTP client and cleanup connections."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            logger.debug("HTTP client closed")

    async def make_request(
        self,
        method: str,
        url: str,
        headers: Optional[dict[str, str]] = None,
        params: Optional[dict[str, Any]] = None,
        json_data: Optional[dict[str, Any]] = None,
        timeout: Optional[float] = None,
        max_retries: int = 3,
    ) -> httpx.Response:
        """Make an HTTP request with retry logic and proper error handling.

        Args:
            method: HTTP method (GET, POST, etc.)
            url: Request URL
            headers: Optional request headers
            params: Optional query parameters
            json_data: Optional JSON data for POST/PUT requests
            timeout: Request timeout in seconds (overrides default)
            max_retries: Maximum number of retry attempts

        Returns:
            HTTP response object

        Raises:
            YouTrackError: Various specific error types based on response
        """
        headers = headers or {}
        request_timeout = timeout or self._timeout.connect

        for attempt in range(max_retries + 1):
            try:
                async with self.get_client() as client:
                    logger.debug(
                        "Making API request",
                        method=method,
                        url=url,
                        attempt=attempt + 1,
                        max_retries=max_retries + 1,
                    )

                    request_start = time.time()
                    response = await client.request(
                        method=method,
                        url=url,
                        headers=headers,
                        params=params,
                        json=json_data,
                        timeout=request_timeout,
                    )
                    request_duration = time.time() - request_start

                    # Log the API call
                    log_api_call(
                        method=method,
                        url=url,
                        status_code=response.status_code,
                        duration=request_duration,
                        attempt=attempt + 1,
                    )

                    # Handle specific HTTP status codes
                    if response.status_code in (200, 201):
                        logger.debug("Request successful", status_code=response.status_code)
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
                            error_message = error_data.get("error", {}).get("description", response.text)
                        except Exception:
                            error_message = response.text or f"HTTP {response.status_code}"

                        raise YouTrackError(f"Request failed with status {response.status_code}: {error_message}")

            except httpx.TimeoutException:
                if attempt < max_retries:
                    wait_time = 2**attempt  # Exponential backoff
                    logger.warning(
                        "Request timed out, retrying",
                        url=url,
                        attempt=attempt + 1,
                        wait_time=wait_time,
                    )
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    logger.error(
                        "Request timed out after multiple attempts",
                        url=url,
                        max_retries=max_retries,
                    )
                    raise ConnectionError("Request timed out after multiple attempts") from None

            except httpx.ConnectError:
                if attempt < max_retries:
                    wait_time = 2**attempt
                    logger.warning(
                        "Connection failed, retrying",
                        url=url,
                        attempt=attempt + 1,
                        wait_time=wait_time,
                    )
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    logger.error(
                        "Unable to connect to YouTrack server",
                        url=url,
                        max_retries=max_retries,
                    )
                    raise ConnectionError("Unable to connect to YouTrack server") from None

            except (
                RateLimitError,
                AuthenticationError,
                PermissionError,
                NotFoundError,
            ):
                # Don't retry these errors
                raise

            except Exception as e:
                if attempt < max_retries:
                    wait_time = 2**attempt
                    logger.warning(
                        "Unexpected error, retrying",
                        url=url,
                        attempt=attempt + 1,
                        wait_time=wait_time,
                        error=str(e),
                    )
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    logger.error(
                        "Unexpected error occurred",
                        url=url,
                        error=str(e),
                        max_retries=max_retries,
                    )
                    raise YouTrackError(f"Unexpected error: {str(e)}") from e

        # Should never reach here, but just in case
        raise YouTrackError("Maximum retry attempts exceeded")

    async def batch_requests(
        self,
        requests: list[dict[str, Any]],
        max_concurrent: int = 10,
    ) -> list[httpx.Response]:
        """Execute multiple requests concurrently.

        Args:
            requests: List of request dictionaries with keys: method, url, headers,
                params, json_data
            max_concurrent: Maximum number of concurrent requests

        Returns:
            List of HTTP responses in the same order as input requests
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def _bounded_request(request_data: dict[str, Any]) -> httpx.Response:
            async with semaphore:
                return await self.make_request(**request_data)

        logger.debug(
            "Executing batch requests",
            total_requests=len(requests),
            max_concurrent=max_concurrent,
        )

        tasks = [_bounded_request(req) for req in requests]
        return await asyncio.gather(*tasks)

    async def make_cached_request(
        self,
        method: str,
        url: str,
        headers: Optional[dict[str, str]] = None,
        params: Optional[dict[str, Any]] = None,
        json_data: Optional[dict[str, Any]] = None,
        timeout: Optional[float] = None,
        max_retries: int = 3,
        cache_ttl: Optional[float] = None,
        cache_key_prefix: str = "",
    ) -> Any:  # Returns httpx.Response or MockResponse
        """Make a cached HTTP request for GET operations.

        Args:
            method: HTTP method (caching only works for GET requests)
            url: Request URL
            headers: Optional request headers
            params: Optional query parameters
            json_data: Optional JSON data for POST/PUT requests
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            cache_ttl: Cache time-to-live in seconds (None to disable caching)
            cache_key_prefix: Prefix for cache keys

        Returns:
            HTTP response object

        Raises:
            YouTrackError: Various specific error types based on response
        """
        # Only cache GET requests without JSON data
        if method.upper() != "GET" or json_data is not None or cache_ttl is None:
            return await self.make_request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json_data=json_data,
                timeout=timeout,
                max_retries=max_retries,
            )

        # Generate cache key
        cache = get_cache()
        param_str = "&".join(f"{k}={v}" for k, v in sorted((params or {}).items()))
        cache_key = f"{cache_key_prefix}:request:{url}:{param_str}"

        # Try to get from cache first
        cached_response_data = await cache.get(cache_key)
        if cached_response_data is not None:
            logger.debug("Using cached response", cache_key=cache_key)

            # Create a mock response object with cached data
            # Note: This is a simplified approach - in production you might want
            # to cache the full response object including headers, status, etc.
            class MockResponse:
                def __init__(self, data, status_code=200):
                    self._data = data
                    self.status_code = status_code

                def json(self):
                    return self._data

                @property
                def text(self):
                    return str(self._data)

            return MockResponse(cached_response_data)

        # Cache miss - make the actual request
        response = await self.make_request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            json_data=json_data,
            timeout=timeout,
            max_retries=max_retries,
        )

        # Cache successful responses
        if response.status_code in (200, 201):
            try:
                response_data = response.json()
                await cache.set(cache_key, response_data, cache_ttl)
                logger.debug("Cached response", cache_key=cache_key, ttl=cache_ttl)
            except Exception as e:
                logger.warning("Failed to cache response", error=str(e), cache_key=cache_key)

        return response


# Global client manager instance
_client_manager: Optional[HTTPClientManager] = None


def get_client_manager() -> HTTPClientManager:
    """Get the global HTTP client manager instance."""
    global _client_manager
    if _client_manager is None:
        # Check for SSL verification setting from environment
        import os

        verify_ssl = os.getenv("YOUTRACK_VERIFY_SSL", "true").lower() != "false"
        _client_manager = HTTPClientManager(verify_ssl=verify_ssl)
    # Type checker note: _client_manager is guaranteed to be non-None here
    return _client_manager  # type: ignore[return-value]


async def cleanup_client_manager() -> None:
    """Cleanup the global client manager."""
    global _client_manager
    manager = _client_manager
    if manager is not None:
        await manager.close()
        _client_manager = None
