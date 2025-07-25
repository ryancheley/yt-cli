"""Tests for caching functionality with TTL and locking logic."""

import asyncio
import time

import pytest

from youtrack_cli.cache import (
    Cache,
    CacheEntry,
    cache_boards,
    cache_fields,
    cache_projects,
    cache_users,
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
        assert entry.tags == set()
        assert entry.access_count == 0
        assert entry.last_accessed <= time.time()

    def test_cache_entry_with_tags(self):
        """Test creating a cache entry with tags."""
        now = time.time()
        tags = {"projects", "api"}
        entry = CacheEntry(value="test_value", timestamp=now, ttl=300.0, tags=tags)

        assert entry.tags == tags

    def test_cache_entry_touch(self):
        """Test cache entry access tracking."""
        entry = CacheEntry(value="test_value", timestamp=time.time(), ttl=300.0)
        initial_count = entry.access_count
        initial_access = entry.last_accessed

        time.sleep(0.001)  # Small delay to ensure time difference
        entry.touch()

        assert entry.access_count == initial_count + 1
        assert entry.last_accessed > initial_access

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

    def test_cache_entry_just_expired(self):
        """Test cache entry that just expired."""
        just_expired = time.time() - 301  # Just over TTL
        entry = CacheEntry(value="test_value", timestamp=just_expired, ttl=300.0)

        assert entry.is_expired


@pytest.mark.unit
class TestCache:
    """Test Cache class functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.cache = Cache(default_ttl=300.0)

    @pytest.mark.asyncio
    async def test_cache_initialization(self):
        """Test cache initialization."""
        cache = Cache(default_ttl=600.0)
        assert cache._default_ttl == 600.0
        assert len(cache._cache) == 0
        assert cache._get_lock is not None
        assert cache._hits == 0
        assert cache._misses == 0
        assert cache._evictions == 0
        assert cache._max_size is None

    @pytest.mark.asyncio
    async def test_cache_initialization_with_max_size(self):
        """Test cache initialization with size limit."""
        cache = Cache(default_ttl=600.0, max_size=100)
        assert cache._max_size == 100

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
        # Set with very short TTL
        await self.cache.set("test_key", "test_value", ttl=0.01)

        # Wait for expiration
        await asyncio.sleep(0.02)

        value = await self.cache.get("test_key")
        assert value is None

    @pytest.mark.asyncio
    async def test_cache_set_with_custom_ttl(self):
        """Test setting cache entry with custom TTL."""
        await self.cache.set("test_key", "test_value", ttl=600.0)

        # Access internal cache entry to verify TTL
        entry = self.cache._cache["test_key"]
        assert entry.ttl == 600.0
        assert entry.value == "test_value"

    @pytest.mark.asyncio
    async def test_cache_set_with_default_ttl(self):
        """Test setting cache entry with default TTL."""
        await self.cache.set("test_key", "test_value")

        entry = self.cache._cache["test_key"]
        assert entry.ttl == 300.0  # Default TTL

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
        assert len(self.cache._cache) == 0

    @pytest.mark.asyncio
    async def test_cache_cleanup_expired(self):
        """Test cleanup of expired entries."""
        # Set entries with different TTLs
        await self.cache.set("fresh_key", "fresh_value", ttl=300.0)
        await self.cache.set("expired_key", "expired_value", ttl=0.01)

        # Wait for one to expire
        await asyncio.sleep(0.02)

        removed_count = await self.cache.cleanup_expired()

        assert removed_count == 1
        assert await self.cache.get("fresh_key") == "fresh_value"
        assert await self.cache.get("expired_key") is None

    @pytest.mark.asyncio
    async def test_cache_cleanup_no_expired_entries(self):
        """Test cleanup when no entries are expired."""
        await self.cache.set("key1", "value1")
        await self.cache.set("key2", "value2")

        removed_count = await self.cache.cleanup_expired()

        assert removed_count == 0
        assert await self.cache.get("key1") == "value1"
        assert await self.cache.get("key2") == "value2"

    @pytest.mark.asyncio
    async def test_cache_stats_empty_cache(self):
        """Test cache statistics for empty cache."""
        stats = await self.cache.stats()

        expected_stats = {
            "total_entries": 0,
            "expired_entries": 0,
            "active_entries": 0,
            "hits": 0,
            "misses": 0,
            "hit_ratio": 0.0,
            "evictions": 0,
            "max_size": None,
            "estimated_memory_bytes": 0,
            "oldest_entry_age": 0,
            "newest_entry_age": 0,
        }
        assert stats == expected_stats

    @pytest.mark.asyncio
    async def test_cache_stats_with_entries(self):
        """Test cache statistics with entries."""
        await self.cache.set("key1", "value1")
        await asyncio.sleep(0.01)  # Small delay to create age difference
        await self.cache.set("key2", "value2")

        stats = await self.cache.stats()

        assert stats["total_entries"] == 2
        assert stats["expired_entries"] == 0
        assert stats["active_entries"] == 2
        assert stats["oldest_entry_age"] > stats["newest_entry_age"]
        assert stats["oldest_entry_age"] > 0
        assert stats["newest_entry_age"] >= 0

    @pytest.mark.asyncio
    async def test_cache_stats_with_expired_entries(self):
        """Test cache statistics with expired entries."""
        await self.cache.set("active_key", "active_value", ttl=300.0)
        await self.cache.set("expired_key", "expired_value", ttl=0.01)

        # Wait for one to expire
        await asyncio.sleep(0.02)

        stats = await self.cache.stats()

        assert stats["total_entries"] == 2
        assert stats["expired_entries"] == 1
        assert stats["active_entries"] == 1

    @pytest.mark.asyncio
    async def test_cache_concurrent_access(self):
        """Test concurrent access to cache with locking."""

        async def set_value(key: str, value: str):
            await self.cache.set(key, value)

        async def get_value(key: str):
            return await self.cache.get(key)

        # Run concurrent operations
        tasks = []
        for i in range(10):
            tasks.append(set_value(f"key_{i}", f"value_{i}"))
            tasks.append(get_value(f"key_{i}"))

        await asyncio.gather(*tasks)

        # Verify all values were set correctly
        for i in range(10):
            value = await self.cache.get(f"key_{i}")
            assert value == f"value_{i}"

    @pytest.mark.asyncio
    async def test_cache_set_with_tags(self):
        """Test setting cache entry with tags."""
        tags = {"projects", "api"}
        await self.cache.set("test_key", "test_value", tags=tags)

        entry = self.cache._cache["test_key"]
        assert entry.tags == tags
        assert entry.value == "test_value"

    @pytest.mark.asyncio
    async def test_cache_lru_eviction(self):
        """Test LRU eviction when cache reaches size limit."""
        cache = Cache(default_ttl=300.0, max_size=2)

        await cache.set("key1", "value1")
        await cache.set("key2", "value2")

        # This should evict key1 (LRU)
        await cache.set("key3", "value3")

        assert await cache.get("key1") is None  # Evicted
        assert await cache.get("key2") == "value2"
        assert await cache.get("key3") == "value3"
        assert cache._evictions == 1

    @pytest.mark.asyncio
    async def test_cache_lru_access_updates(self):
        """Test that accessing entries updates LRU order."""
        cache = Cache(default_ttl=300.0, max_size=2)

        await cache.set("key1", "value1")
        await cache.set("key2", "value2")

        # Access key1 to make it more recently used
        await cache.get("key1")

        # This should evict key2 (now LRU)
        await cache.set("key3", "value3")

        assert await cache.get("key1") == "value1"
        assert await cache.get("key2") is None  # Evicted
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
        assert await self.cache.get("projects:456") is None
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
    async def test_invalidate_by_multiple_tags(self):
        """Test invalidation by multiple tags."""
        await self.cache.set("key1", "value1", tags={"projects"})
        await self.cache.set("key2", "value2", tags={"users"})
        await self.cache.set("key3", "value3", tags={"boards"})

        invalidated = await self.cache.invalidate_by_tag("projects", "users")

        assert invalidated == 2
        assert await self.cache.get("key1") is None
        assert await self.cache.get("key2") is None
        assert await self.cache.get("key3") == "value3"

    @pytest.mark.asyncio
    async def test_set_many(self):
        """Test bulk setting of cache entries."""
        items = {"key1": "value1", "key2": "value2", "key3": "value3"}
        tags = {"bulk", "test"}

        await self.cache.set_many(items, ttl=600.0, tags=tags)

        for key, expected_value in items.items():
            value = await self.cache.get(key)
            assert value == expected_value

            entry = self.cache._cache[key]
            assert entry.tags == tags
            assert entry.ttl == 600.0

    @pytest.mark.asyncio
    async def test_delete_many(self):
        """Test bulk deletion of cache entries."""
        await self.cache.set("key1", "value1")
        await self.cache.set("key2", "value2")
        await self.cache.set("key3", "value3")

        deleted = await self.cache.delete_many(["key1", "key3", "nonexistent"])

        assert deleted == 2
        assert await self.cache.get("key1") is None
        assert await self.cache.get("key2") == "value2"
        assert await self.cache.get("key3") is None

    @pytest.mark.asyncio
    async def test_cache_stats_comprehensive(self):
        """Test comprehensive cache statistics."""
        cache = Cache(default_ttl=300.0, max_size=100)
        await cache.set("key1", "value1")
        await cache.get("key1")  # Hit
        await cache.get("nonexistent")  # Miss

        stats = await cache.stats()

        assert stats["total_entries"] == 1
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["hit_ratio"] == 0.5
        assert stats["evictions"] == 0
        assert stats["max_size"] == 100
        assert stats["estimated_memory_bytes"] > 0


@pytest.mark.unit
class TestGlobalCacheFunctions:
    """Test global cache functions."""

    def setup_method(self):
        """Set up test fixtures."""
        # Reset global cache state
        import youtrack_cli.cache

        youtrack_cli.cache._cache = None

    @pytest.mark.asyncio
    async def test_get_cache_singleton(self):
        """Test that get_cache returns singleton instance."""
        cache1 = get_cache()
        cache2 = get_cache()

        assert cache1 is cache2
        assert isinstance(cache1, Cache)

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
        # Reset global cache state
        import youtrack_cli.cache

        youtrack_cli.cache._cache = None

    @pytest.mark.asyncio
    async def test_cached_decorator_basic(self):
        """Test basic cached decorator functionality."""
        call_count = [0]  # Use list to avoid nonlocal issues

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
        assert call_count[0] == 1  # Function not called again

    @pytest.mark.asyncio
    async def test_cached_decorator_different_args(self):
        """Test cached decorator with different arguments."""
        call_count = [0]  # Use list to avoid nonlocal issues

        @cached(ttl=300.0)
        async def test_function(arg: str):
            call_count[0] += 1
            return f"result_{arg}"

        result1 = await test_function("arg1")
        result2 = await test_function("arg2")

        assert result1 == "result_arg1"
        assert result2 == "result_arg2"
        assert call_count[0] == 2  # Function called twice for different args

    @pytest.mark.asyncio
    async def test_cached_decorator_with_kwargs(self):
        """Test cached decorator with keyword arguments."""
        call_count = [0]  # Use list to avoid nonlocal issues

        @cached(ttl=300.0)
        async def test_function(arg1: str, arg2: str = "default"):
            call_count[0] += 1
            return f"result_{arg1}_{arg2}"

        result1 = await test_function("test", arg2="custom")
        result2 = await test_function("test", arg2="custom")

        assert result1 == "result_test_custom"
        assert result2 == "result_test_custom"
        assert call_count[0] == 1  # Function called once

    @pytest.mark.asyncio
    async def test_cached_decorator_with_key_prefix(self):
        """Test cached decorator with key prefix."""
        call_count = [0]  # Use list to avoid nonlocal issues

        @cached(ttl=300.0, key_prefix="test_prefix")
        async def test_function(arg: str):
            call_count[0] += 1
            return f"result_{arg}"

        result = await test_function("test")
        assert result == "result_test"
        assert call_count[0] == 1

        # Verify cache key has prefix
        cache = get_cache()
        cache_stats = await cache.stats()
        assert cache_stats["total_entries"] == 1

    @pytest.mark.asyncio
    async def test_cached_decorator_ttl_expiration(self):
        """Test cached decorator with TTL expiration."""
        call_count = [0]  # Use list to avoid nonlocal issues

        @cached(ttl=0.01)  # Very short TTL
        async def test_function(arg: str):
            call_count[0] += 1
            return f"result_{arg}"

        # First call
        await test_function("test")
        assert call_count[0] == 1

        # Wait for cache to expire
        await asyncio.sleep(0.02)

        # Second call should execute function again
        result2 = await test_function("test")
        assert result2 == "result_test"
        assert call_count[0] == 2  # Function called again


@pytest.mark.unit
class TestPredefinedCacheDecorators:
    """Test predefined cache decorators."""

    @pytest.mark.asyncio
    async def test_cache_projects_decorator(self):
        """Test cache_projects decorator."""
        call_count = [0]  # Use list to avoid nonlocal issues

        @cache_projects(ttl=600.0)
        async def get_projects():
            call_count[0] += 1
            return ["project1", "project2"]

        result1 = await get_projects()
        result2 = await get_projects()

        assert result1 == ["project1", "project2"]
        assert result2 == ["project1", "project2"]
        assert call_count[0] == 1

    @pytest.mark.asyncio
    async def test_cache_users_decorator(self):
        """Test cache_users decorator."""
        call_count = [0]  # Use list to avoid nonlocal issues

        @cache_users(ttl=1800.0)
        async def get_users():
            call_count[0] += 1
            return ["user1", "user2"]

        result1 = await get_users()
        result2 = await get_users()

        assert result1 == ["user1", "user2"]
        assert result2 == ["user1", "user2"]
        assert call_count[0] == 1

    @pytest.mark.asyncio
    async def test_cache_fields_decorator(self):
        """Test cache_fields decorator."""
        call_count = [0]  # Use list to avoid nonlocal issues

        @cache_fields(ttl=3600.0)
        async def get_fields():
            call_count[0] += 1
            return ["field1", "field2"]

        result1 = await get_fields()
        result2 = await get_fields()

        assert result1 == ["field1", "field2"]
        assert result2 == ["field1", "field2"]
        assert call_count[0] == 1

    @pytest.mark.asyncio
    async def test_cache_boards_decorator(self):
        """Test cache_boards decorator."""
        call_count = [0]  # Use list to avoid nonlocal issues

        @cache_boards(ttl=600.0)
        async def get_boards():
            call_count[0] += 1
            return ["board1", "board2"]

        result1 = await get_boards()
        result2 = await get_boards()

        assert result1 == ["board1", "board2"]
        assert result2 == ["board1", "board2"]
        assert call_count[0] == 1
