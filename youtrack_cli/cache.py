"""Caching layer for frequently accessed YouTrack resources."""

import asyncio
import fnmatch
import time
from collections import OrderedDict
from dataclasses import dataclass, field
from functools import wraps
from typing import Any, Optional, Set

from .logging import get_logger

__all__ = [
    "Cache",
    "get_cache",
    "cached",
    "clear_cache",
    "cache_projects",
    "cache_users",
    "cache_fields",
    "cache_boards",
]

logger = get_logger(__name__)


@dataclass
class CacheEntry:
    """Represents a cached value with metadata."""

    value: Any
    timestamp: float
    ttl: float
    tags: Set[str] = field(default_factory=set)
    access_count: int = field(default=0)
    last_accessed: float = field(default_factory=time.time)

    @property
    def is_expired(self) -> bool:
        """Check if the cache entry has expired."""
        return time.time() > (self.timestamp + self.ttl)

    def touch(self) -> None:
        """Update access tracking for LRU/LFU algorithms."""
        self.access_count += 1
        self.last_accessed = time.time()


class Cache:
    """In-memory cache with TTL support and advanced invalidation strategies for YouTrack API responses."""

    def __init__(self, default_ttl: float = 300.0, max_size: Optional[int] = None):
        """Initialize the cache.

        Args:
            default_ttl: Default time-to-live in seconds (5 minutes)
            max_size: Maximum number of entries (None for unlimited)
        """
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._default_ttl = default_ttl
        self._max_size = max_size
        self._lock: Optional[asyncio.Lock] = None
        self._hits = 0
        self._misses = 0
        self._evictions = 0

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
                self._misses += 1
                return None

            if entry.is_expired:
                logger.debug("Cache expired", key=key, age=time.time() - entry.timestamp)
                del self._cache[key]
                self._misses += 1
                return None

            # Update access tracking and move to end for LRU
            entry.touch()
            self._cache.move_to_end(key)
            self._hits += 1
            logger.debug("Cache hit", key=key, age=time.time() - entry.timestamp)
            return entry.value

    async def set(self, key: str, value: Any, ttl: Optional[float] = None, tags: Optional[Set[str]] = None) -> None:
        """Set a value in the cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (uses default if None)
            tags: Optional tags for grouping related entries
        """
        ttl = ttl or self._default_ttl
        tags = tags or set()

        async with self._get_lock:
            # Check if we need to evict entries for size limit
            if self._max_size and len(self._cache) >= self._max_size and key not in self._cache:
                await self._evict_lru()

            self._cache[key] = CacheEntry(
                value=value,
                timestamp=time.time(),
                ttl=ttl,
                tags=tags,
            )
            # Move to end for LRU tracking
            self._cache.move_to_end(key)
            logger.debug("Cache set", key=key, ttl=ttl, tags=list(tags))

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

    async def _evict_lru(self) -> None:
        """Evict the least recently used entry."""
        if not self._cache:
            return

        # Find LRU entry (first in OrderedDict)
        lru_key = next(iter(self._cache))
        del self._cache[lru_key]
        self._evictions += 1
        logger.debug("Evicted LRU entry", key=lru_key)

    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate all cache entries matching a glob pattern.

        Args:
            pattern: Glob pattern (e.g., 'projects:*', 'users:admin:*')

        Returns:
            Number of entries invalidated
        """
        async with self._get_lock:
            matching_keys = [key for key in self._cache.keys() if fnmatch.fnmatch(key, pattern)]

            for key in matching_keys:
                del self._cache[key]

            if matching_keys:
                logger.debug("Pattern invalidation", pattern=pattern, count=len(matching_keys))

            return len(matching_keys)

    async def invalidate_by_tag(self, *tags: str) -> int:
        """Invalidate all cache entries that have any of the specified tags.

        Args:
            tags: Tags to invalidate

        Returns:
            Number of entries invalidated
        """
        async with self._get_lock:
            tag_set = set(tags)
            matching_keys = [key for key, entry in self._cache.items() if entry.tags.intersection(tag_set)]

            for key in matching_keys:
                del self._cache[key]

            if matching_keys:
                logger.debug("Tag invalidation", tags=list(tags), count=len(matching_keys))

            return len(matching_keys)

    async def set_many(
        self, items: dict[str, Any], ttl: Optional[float] = None, tags: Optional[Set[str]] = None
    ) -> None:
        """Set multiple values in the cache efficiently.

        Args:
            items: Dictionary of key-value pairs to cache
            ttl: Time-to-live in seconds (uses default if None)
            tags: Optional tags for all entries
        """
        ttl = ttl or self._default_ttl
        tags = tags or set()

        async with self._get_lock:
            now = time.time()
            for key, value in items.items():
                # Check if we need to evict entries for size limit
                if self._max_size and len(self._cache) >= self._max_size and key not in self._cache:
                    await self._evict_lru()

                self._cache[key] = CacheEntry(
                    value=value,
                    timestamp=now,
                    ttl=ttl,
                    tags=tags.copy(),
                )
                self._cache.move_to_end(key)

            logger.debug("Bulk cache set", count=len(items), ttl=ttl, tags=list(tags))

    async def delete_many(self, keys: list[str]) -> int:
        """Delete multiple keys from the cache efficiently.

        Args:
            keys: List of cache keys to delete

        Returns:
            Number of keys actually deleted
        """
        async with self._get_lock:
            deleted_count = 0
            for key in keys:
                if key in self._cache:
                    del self._cache[key]
                    deleted_count += 1

            if deleted_count > 0:
                logger.debug("Bulk cache delete", count=deleted_count)

            return deleted_count

    async def stats(self) -> dict[str, Any]:
        """Get comprehensive cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        async with self._get_lock:
            now = time.time()
            expired_count = sum(1 for entry in self._cache.values() if entry.is_expired)
            total_requests = self._hits + self._misses
            hit_ratio = (self._hits / total_requests) if total_requests > 0 else 0.0

            # Calculate memory usage estimate (rough)
            estimated_memory = sum(
                len(str(key)) + len(str(entry.value)) + 100  # 100 bytes overhead per entry
                for key, entry in self._cache.items()
            )

            return {
                "total_entries": len(self._cache),
                "expired_entries": expired_count,
                "active_entries": len(self._cache) - expired_count,
                "hits": self._hits,
                "misses": self._misses,
                "hit_ratio": hit_ratio,
                "evictions": self._evictions,
                "max_size": self._max_size,
                "estimated_memory_bytes": estimated_memory,
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


def cached(ttl: Optional[float] = None, key_prefix: str = "", tags: Optional[Set[str]] = None):
    """Decorator to cache function results.

    Args:
        ttl: Time-to-live in seconds (uses cache default if None)
        key_prefix: Prefix for cache keys
        tags: Optional tags for cache entries

    Example:
        @cached(ttl=600, key_prefix="projects", tags={"api", "projects"})
        async def get_projects():
            # This will be cached for 10 minutes with tags
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
            await cache.set(cache_key, result, ttl, tags)

            return result

        return wrapper

    return decorator


# Predefined cache decorators for common use cases
def cache_projects(ttl: float = 900.0):  # 15 minutes
    """Cache project-related data."""
    return cached(ttl=ttl, key_prefix="projects", tags={"projects", "api"})


def cache_users(ttl: float = 1800.0):  # 30 minutes
    """Cache user-related data."""
    return cached(ttl=ttl, key_prefix="users", tags={"users", "api"})


def cache_fields(ttl: float = 3600.0):  # 1 hour
    """Cache custom field definitions."""
    return cached(ttl=ttl, key_prefix="fields", tags={"fields", "api", "metadata"})


def cache_boards(ttl: float = 600.0):  # 10 minutes
    """Cache board-related data."""
    return cached(ttl=ttl, key_prefix="boards", tags={"boards", "api"})
