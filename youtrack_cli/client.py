"""HTTP client manager with connection pooling and performance optimizations."""

from __future__ import annotations

import asyncio
import time
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any, Optional, Union, cast

import httpx

from .cache import get_cache
from .exceptions import (
    AuthenticationError,
    ConnectionError,
    NotFoundError,
    PermissionError,
    RateLimitError,
    YouTrackError,
    YouTrackNetworkError,
    YouTrackServerError,
)
from .logging import get_logger, log_api_call
from .models import CachedResponse

__all__ = [
    "HTTPClientManager",
    "get_client_manager",
    "reset_client_manager",
    "reset_client_manager_sync",
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
        self._lock: Optional[asyncio.Lock] = None

    async def _ensure_client(self) -> httpx.AsyncClient:
        """Ensure the HTTP client is initialized."""
        if self._client is None or self._client.is_closed:
            # Create lock if it doesn't exist (for Python 3.9 compatibility)
            if self._lock is None:
                self._lock = asyncio.Lock()

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

            except (httpx.RequestError, OSError) as e:
                # Handle retryable network errors
                if attempt < max_retries:
                    wait_time = 2**attempt
                    logger.warning(
                        "Network error, retrying",
                        url=url,
                        attempt=attempt + 1,
                        wait_time=wait_time,
                        error=str(e),
                        error_type=type(e).__name__,
                    )
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    logger.error(
                        "Network error after max retries",
                        url=url,
                        error=str(e),
                        error_type=type(e).__name__,
                        max_retries=max_retries,
                    )
                    raise YouTrackNetworkError(f"Network error after {max_retries} retries: {str(e)}") from e

            except httpx.HTTPStatusError as e:
                # Handle server errors (5xx status codes) with retry
                if e.response.status_code >= 500:
                    if attempt < max_retries:
                        wait_time = 2**attempt
                        logger.warning(
                            "Server error, retrying",
                            url=url,
                            attempt=attempt + 1,
                            wait_time=wait_time,
                            status_code=e.response.status_code,
                            error=str(e),
                        )
                        await asyncio.sleep(wait_time)
                        continue
                    else:
                        logger.error(
                            "Server error after max retries",
                            url=url,
                            status_code=e.response.status_code,
                            error=str(e),
                            max_retries=max_retries,
                        )
                        raise YouTrackServerError(
                            f"Server error after {max_retries} retries: {str(e)}", status_code=e.response.status_code
                        ) from e
                else:
                    # For client errors (4xx), don't retry
                    raise

            except Exception as e:
                # Handle truly unexpected errors with enhanced logging
                logger.exception(
                    "Unexpected error occurred",
                    url=url,
                    error=str(e),
                    error_type=type(e).__name__,
                    attempt=attempt + 1,
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
    ) -> Union[httpx.Response, CachedResponse]:
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
            return CachedResponse(data=cached_response_data, status_code=200)

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
        import warnings

        from .security import AuditLogger

        verify_ssl_str = os.getenv("YOUTRACK_VERIFY_SSL", "true").lower()
        verify_ssl = verify_ssl_str not in ("false", "0", "no", "off")

        # Issue security warning if SSL verification is disabled
        if not verify_ssl:
            warnings.warn(
                "⚠️  SSL verification is DISABLED. This is insecure and should only be used in development.",
                UserWarning,
                stacklevel=2,
            )

        # Audit log SSL configuration for security compliance
        audit_logger = AuditLogger()
        audit_logger.log_command(
            command="ssl_verification_config",
            arguments=[f"YOUTRACK_VERIFY_SSL={verify_ssl_str}", f"verify_ssl={verify_ssl}"],
            user=None,  # User not available during client initialization
            success=True,
        )

        _client_manager = HTTPClientManager(verify_ssl=verify_ssl)

        # Log the client manager initialization
        logger.info("HTTP client manager initialized", verify_ssl=verify_ssl, env_var=verify_ssl_str)

    # At this point, _client_manager is guaranteed to be non-None
    client_manager = _client_manager
    assert client_manager is not None, "Client manager should never be None after initialization"
    return client_manager


async def cleanup_client_manager() -> None:
    """Cleanup the global client manager."""
    global _client_manager
    manager = _client_manager
    if manager is not None:
        await manager.close()
        _client_manager = None


async def reset_client_manager() -> None:
    """Reset the global client manager and close existing connections.

    This function properly closes any existing HTTP connections before
    resetting the global client manager to prevent resource leaks.
    """
    global _client_manager
    if _client_manager is not None:
        try:
            # Type assertion: _client_manager is guaranteed not None here
            await cast(HTTPClientManager, _client_manager).close()
            logger.debug("Client manager connections closed during reset")
        except Exception as e:
            logger.warning(
                "Failed to close client manager connections during reset",
                error=str(e),
                error_type=type(e).__name__,
            )
        finally:
            _client_manager = None


def reset_client_manager_sync() -> None:
    """Synchronous version of reset_client_manager for backwards compatibility.

    This function provides backwards compatibility for existing code that
    expects a synchronous reset operation. It handles event loop scenarios
    appropriately across all Python versions.
    """
    global _client_manager

    # First, try to do proper async cleanup if possible
    try:
        # Try to run async cleanup - this will work if no event loop is running
        asyncio.run(reset_client_manager())
        return
    except RuntimeError:
        # RuntimeError means either:
        # 1. There's already an event loop running (Python 3.9+)
        # 2. Some other async-related issue
        pass
    except Exception as e:
        logger.warning(
            "Failed to run async reset, falling back to sync reset",
            error=str(e),
            error_type=type(e).__name__,
        )

    # If async cleanup failed, do a simple sync reset
    if _client_manager is not None:
        try:
            # Log what we're doing
            logger.debug("Reset client manager without async cleanup (fallback mode)")
            _client_manager = None
        except Exception as e:
            logger.warning(
                "Failed to reset client manager in fallback mode",
                error=str(e),
                error_type=type(e).__name__,
            )
            # Force reset even if logging fails
            _client_manager = None
