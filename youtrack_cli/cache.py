"""Caching layer for frequently accessed YouTrack resources."""

import asyncio
import time
from dataclasses import dataclass
from functools import wraps
from typing import Any, Optional

from .logging import get_logger

__all__ = [
    "Cache",
    "get_cache",
    "cached",
    "clear_cache",
]

logger = get_logger(__name__)


@dataclass
class CacheEntry:
    """Represents a cached value with metadata."""

    value: Any
    timestamp: float
    ttl: float

    @property
    def is_expired(self) -> bool:
        """Check if the cache entry has expired."""
        return time.time() > (self.timestamp + self.ttl)


class Cache:
    """In-memory cache with TTL support for YouTrack API responses."""

    def __init__(self, default_ttl: float = 300.0):
        """Initialize the cache.

        Args:
            default_ttl: Default time-to-live in seconds (5 minutes)
        """
        self._cache: dict[str, CacheEntry] = {}
        self._default_ttl = default_ttl
        self._lock: Optional[asyncio.Lock] = None

    @property
    def _get_lock(self) -> asyncio.Lock:
        """Get or create the async lock. Lazy initialization to avoid event loop issues."""
        if self._lock is None:
            self._lock = asyncio.Lock()
        return self._lock

    async def get(self, key: str) -> Optional[Any]:
        """Get a value from the cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        async with self._get_lock:
            entry = self._cache.get(key)
            if entry is None:
                logger.debug("Cache miss", key=key)
                return None

            if entry.is_expired:
                logger.debug("Cache expired", key=key, age=time.time() - entry.timestamp)
                del self._cache[key]
                return None

            logger.debug("Cache hit", key=key, age=time.time() - entry.timestamp)
            return entry.value

    async def set(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        """Set a value in the cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (uses default if None)
        """
        ttl = ttl or self._default_ttl
        async with self._get_lock:
            self._cache[key] = CacheEntry(
                value=value,
                timestamp=time.time(),
                ttl=ttl,
            )
            logger.debug("Cache set", key=key, ttl=ttl)

    async def delete(self, key: str) -> bool:
        """Delete a value from the cache.

        Args:
            key: Cache key

        Returns:
            True if the key was deleted, False if not found
        """
        async with self._get_lock:
            if key in self._cache:
                del self._cache[key]
                logger.debug("Cache deleted", key=key)
                return True
            return False

    async def clear(self) -> None:
        """Clear all cached values."""
        async with self._get_lock:
            count = len(self._cache)
            self._cache.clear()
            logger.debug("Cache cleared", removed_entries=count)

    async def cleanup_expired(self) -> int:
        """Remove expired entries from the cache.

        Returns:
            Number of entries removed
        """
        async with self._get_lock:
            expired_keys = [key for key, entry in self._cache.items() if entry.is_expired]

            for key in expired_keys:
                del self._cache[key]

            if expired_keys:
                logger.debug("Cleaned up expired cache entries", count=len(expired_keys))

            return len(expired_keys)

    async def stats(self) -> dict[str, Any]:
        """Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        async with self._get_lock:
            now = time.time()
            expired_count = sum(1 for entry in self._cache.values() if entry.is_expired)

            return {
                "total_entries": len(self._cache),
                "expired_entries": expired_count,
                "active_entries": len(self._cache) - expired_count,
                "oldest_entry_age": (
                    now - min(entry.timestamp for entry in self._cache.values()) if self._cache else 0
                ),
                "newest_entry_age": (
                    now - max(entry.timestamp for entry in self._cache.values()) if self._cache else 0
                ),
            }


# Global cache instance
_cache: Optional[Cache] = None


def get_cache() -> Cache:
    """Get the global cache instance."""
    global _cache
    if _cache is None:
        _cache = Cache()
    # Type checker note: _cache is guaranteed to be non-None here
    return _cache  # type: ignore[return-value]


async def clear_cache() -> None:
    """Clear the global cache."""
    cache = get_cache()
    await cache.clear()


def cached(ttl: Optional[float] = None, key_prefix: str = ""):
    """Decorator to cache function results.

    Args:
        ttl: Time-to-live in seconds (uses cache default if None)
        key_prefix: Prefix for cache keys

    Example:
        @cached(ttl=600, key_prefix="projects")
        async def get_projects():
            # This will be cached for 10 minutes
            return await fetch_projects()
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache = get_cache()

            # Generate cache key from function name and arguments
            # Convert arguments to strings for the key
            arg_strings = [str(arg) for arg in args]
            kwarg_strings = [f"{k}={v}" for k, v in sorted(kwargs.items())]
            all_args = arg_strings + kwarg_strings

            cache_key = (
                f"{key_prefix}:{func.__name__}:{':'.join(all_args)}"
                if key_prefix
                else f"{func.__name__}:{':'.join(all_args)}"
            )

            # Try to get from cache first
            cached_result = await cache.get(cache_key)
            if cached_result is not None:
                return cached_result

            # Cache miss - call the function
            result = await func(*args, **kwargs)

            # Cache the result
            await cache.set(cache_key, result, ttl)

            return result

        return wrapper

    return decorator


# Predefined cache decorators for common use cases
def cache_projects(ttl: float = 900.0):  # 15 minutes
    """Cache project-related data."""
    return cached(ttl=ttl, key_prefix="projects")


def cache_users(ttl: float = 1800.0):  # 30 minutes
    """Cache user-related data."""
    return cached(ttl=ttl, key_prefix="users")


def cache_fields(ttl: float = 3600.0):  # 1 hour
    """Cache custom field definitions."""
    return cached(ttl=ttl, key_prefix="fields")


def cache_boards(ttl: float = 600.0):  # 10 minutes
    """Cache board-related data."""
    return cached(ttl=ttl, key_prefix="boards")
