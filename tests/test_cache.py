"""Tests for caching functionality with TTL and locking logic."""

import asyncio
import time

import pytest

from youtrack_cli.cache import (
    Cache,
    CacheEntry,
    cached,
    clear_cache,
    get_cache,
)


class TestCacheEntry:
    """Test CacheEntry dataclass."""

    def test_cache_entry_creation(self):
        """Test creating a cache entry."""
        now = time.time()
        entry = CacheEntry(value="test_value", timestamp=now, ttl=300.0)

        assert entry.value == "test_value"
        assert entry.timestamp == now
        assert entry.ttl == 300.0

    def test_cache_entry_not_expired(self):
        """Test cache entry that hasn't expired."""
        now = time.time()
        entry = CacheEntry(value="test_value", timestamp=now, ttl=300.0)
        assert not entry.is_expired

    def test_cache_entry_expired(self):
        """Test cache entry that has expired."""
        old_time = time.time() - 400  # 400 seconds ago
        entry = CacheEntry(value="test_value", timestamp=old_time, ttl=300.0)
        assert entry.is_expired


@pytest.mark.unit
class TestCache:
    """Test Cache class functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.cache = Cache(default_ttl=300.0)

    @pytest.mark.asyncio
    async def test_cache_set_and_get(self):
        """Test setting and getting values from cache."""
        await self.cache.set("test_key", "test_value")
        value = await self.cache.get("test_key")
        assert value == "test_value"

    @pytest.mark.asyncio
    async def test_cache_get_nonexistent_key(self):
        """Test getting a non-existent key returns None."""
        value = await self.cache.get("nonexistent_key")
        assert value is None

    @pytest.mark.asyncio
    async def test_cache_get_expired_entry(self):
        """Test getting an expired cache entry returns None."""
        await self.cache.set("test_key", "test_value", ttl=0.01)
        await asyncio.sleep(0.02)
        value = await self.cache.get("test_key")
        assert value is None

    @pytest.mark.asyncio
    async def test_cache_set_with_custom_ttl(self):
        """Test setting cache entry with custom TTL."""
        await self.cache.set("test_key", "test_value", ttl=600.0)
        entry = self.cache._cache["test_key"]
        assert entry.ttl == 600.0

    @pytest.mark.asyncio
    async def test_cache_delete_existing_key(self):
        """Test deleting an existing key."""
        await self.cache.set("test_key", "test_value")
        result = await self.cache.delete("test_key")
        assert result is True
        value = await self.cache.get("test_key")
        assert value is None

    @pytest.mark.asyncio
    async def test_cache_delete_nonexistent_key(self):
        """Test deleting a non-existent key."""
        result = await self.cache.delete("nonexistent_key")
        assert result is False

    @pytest.mark.asyncio
    async def test_cache_clear(self):
        """Test clearing all cache entries."""
        await self.cache.set("key1", "value1")
        await self.cache.set("key2", "value2")
        await self.cache.clear()
        assert await self.cache.get("key1") is None
        assert await self.cache.get("key2") is None

    @pytest.mark.asyncio
    async def test_cache_cleanup_expired(self):
        """Test cleanup of expired entries."""
        await self.cache.set("fresh_key", "fresh_value", ttl=300.0)
        await self.cache.set("expired_key", "expired_value", ttl=0.01)
        await asyncio.sleep(0.02)

        removed_count = await self.cache.cleanup_expired()

        assert removed_count == 1
        assert await self.cache.get("fresh_key") == "fresh_value"
        assert await self.cache.get("expired_key") is None

    @pytest.mark.asyncio
    async def test_cache_stats_empty_cache(self):
        """Test cache statistics for empty cache."""
        stats = await self.cache.stats()
        assert stats["total_entries"] == 0
        assert stats["hits"] == 0
        assert stats["misses"] == 0

    @pytest.mark.asyncio
    async def test_cache_stats_with_entries(self):
        """Test cache statistics with entries."""
        await self.cache.set("key1", "value1")
        await self.cache.get("key1")  # Hit
        await self.cache.get("nonexistent")  # Miss

        stats = await self.cache.stats()
        assert stats["total_entries"] == 1
        assert stats["hits"] == 1
        assert stats["misses"] == 1

    @pytest.mark.asyncio
    async def test_cache_lru_eviction(self):
        """Test LRU eviction when cache reaches size limit."""
        cache = Cache(default_ttl=300.0, max_size=2)

        await cache.set("key1", "value1")
        await cache.set("key2", "value2")
        await cache.set("key3", "value3")  # Should evict key1

        assert await cache.get("key1") is None
        assert await cache.get("key2") == "value2"
        assert await cache.get("key3") == "value3"

    @pytest.mark.asyncio
    async def test_invalidate_pattern(self):
        """Test pattern-based cache invalidation."""
        await self.cache.set("projects:123", "project1")
        await self.cache.set("projects:456", "project2")
        await self.cache.set("users:789", "user1")

        invalidated = await self.cache.invalidate_pattern("projects:*")

        assert invalidated == 2
        assert await self.cache.get("projects:123") is None
        assert await self.cache.get("users:789") == "user1"

    @pytest.mark.asyncio
    async def test_invalidate_by_tag(self):
        """Test tag-based cache invalidation."""
        await self.cache.set("key1", "value1", tags={"projects", "api"})
        await self.cache.set("key2", "value2", tags={"users", "api"})
        await self.cache.set("key3", "value3", tags={"boards"})

        invalidated = await self.cache.invalidate_by_tag("api")

        assert invalidated == 2
        assert await self.cache.get("key1") is None
        assert await self.cache.get("key2") is None
        assert await self.cache.get("key3") == "value3"

    @pytest.mark.asyncio
    async def test_set_many(self):
        """Test bulk setting of cache entries."""
        items = {"key1": "value1", "key2": "value2"}
        await self.cache.set_many(items, ttl=600.0)

        for key, expected_value in items.items():
            value = await self.cache.get(key)
            assert value == expected_value

    @pytest.mark.asyncio
    async def test_delete_many(self):
        """Test bulk deletion of cache entries."""
        await self.cache.set("key1", "value1")
        await self.cache.set("key2", "value2")

        deleted = await self.cache.delete_many(["key1", "nonexistent"])

        assert deleted == 1
        assert await self.cache.get("key1") is None
        assert await self.cache.get("key2") == "value2"


@pytest.mark.unit
class TestGlobalCacheFunctions:
    """Test global cache functions."""

    def setup_method(self):
        """Set up test fixtures."""
        import youtrack_cli.cache

        youtrack_cli.cache._cache = None

    @pytest.mark.asyncio
    async def test_get_cache_singleton(self):
        """Test that get_cache returns singleton instance."""
        cache1 = get_cache()
        cache2 = get_cache()
        assert cache1 is cache2

    @pytest.mark.asyncio
    async def test_clear_cache_function(self):
        """Test global clear_cache function."""
        cache = get_cache()
        await cache.set("test_key", "test_value")
        await clear_cache()
        value = await cache.get("test_key")
        assert value is None


@pytest.mark.unit
class TestCachedDecorator:
    """Test cached decorator functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        import youtrack_cli.cache

        youtrack_cli.cache._cache = None

    @pytest.mark.asyncio
    async def test_cached_decorator_basic(self):
        """Test basic cached decorator functionality."""
        call_count = [0]

        @cached(ttl=300.0)
        async def test_function(arg: str):
            call_count[0] += 1
            return f"result_{arg}"

        # First call should execute function
        result1 = await test_function("test")
        assert result1 == "result_test"
        assert call_count[0] == 1

        # Second call should return cached result
        result2 = await test_function("test")
        assert result2 == "result_test"
        assert call_count[0] == 1

    @pytest.mark.asyncio
    async def test_cached_decorator_different_args(self):
        """Test cached decorator with different arguments."""
        call_count = [0]

        @cached(ttl=300.0)
        async def test_function(arg: str):
            call_count[0] += 1
            return f"result_{arg}"

        result1 = await test_function("arg1")
        result2 = await test_function("arg2")

        assert result1 == "result_arg1"
        assert result2 == "result_arg2"
        assert call_count[0] == 2

    @pytest.mark.asyncio
    async def test_cached_decorator_ttl_expiration(self):
        """Test cached decorator with TTL expiration."""
        call_count = [0]

        @cached(ttl=0.01)
        async def test_function(arg: str):
            call_count[0] += 1
            return f"result_{arg}"

        await test_function("test")
        assert call_count[0] == 1

        await asyncio.sleep(0.02)

        result2 = await test_function("test")
        assert result2 == "result_test"
        assert call_count[0] == 2
