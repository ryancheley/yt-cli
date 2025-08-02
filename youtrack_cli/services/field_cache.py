"""Simple caching mechanism for project field metadata."""

import time
from typing import Any, Dict, Optional


class FieldCache:
    """Simple in-memory cache for project field metadata.

    Caches field discovery results to avoid repeated API calls.
    Cache entries expire after a configurable TTL (time-to-live).
    """

    def __init__(self, ttl_seconds: int = 300):  # 5 minutes default
        """Initialize the cache.

        Args:
            ttl_seconds: Time-to-live for cache entries in seconds
        """
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._ttl = ttl_seconds

    def _get_cache_key(self, project_id: str, field_type: str = "state") -> str:
        """Generate cache key for project field metadata."""
        return f"{project_id}:{field_type}"

    def _is_expired(self, entry: Dict[str, Any]) -> bool:
        """Check if cache entry has expired."""
        if "timestamp" not in entry:
            return True
        return time.time() - entry["timestamp"] > self._ttl

    def get(self, project_id: str, field_type: str = "state") -> Optional[Dict[str, Any]]:
        """Get cached field metadata for a project.

        Args:
            project_id: Project ID
            field_type: Type of field to get (default: "state")

        Returns:
            Cached field metadata or None if not found/expired
        """
        cache_key = self._get_cache_key(project_id, field_type)

        if cache_key not in self._cache:
            return None

        entry = self._cache[cache_key]
        if self._is_expired(entry):
            del self._cache[cache_key]
            return None

        return entry.get("data")

    def set(self, project_id: str, field_data: Dict[str, Any], field_type: str = "state") -> None:
        """Cache field metadata for a project.

        Args:
            project_id: Project ID
            field_data: Field metadata to cache
            field_type: Type of field being cached (default: "state")
        """
        cache_key = self._get_cache_key(project_id, field_type)
        self._cache[cache_key] = {"data": field_data, "timestamp": time.time()}

    def clear(self, project_id: Optional[str] = None) -> None:
        """Clear cache entries.

        Args:
            project_id: If provided, clear only entries for this project.
                       If None, clear all entries.
        """
        if project_id is None:
            self._cache.clear()
        else:
            # Clear all entries for the specified project
            keys_to_remove = [key for key in self._cache.keys() if key.startswith(f"{project_id}:")]
            for key in keys_to_remove:
                del self._cache[key]

    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics for debugging."""
        total_entries = len(self._cache)
        expired_entries = sum(1 for entry in self._cache.values() if self._is_expired(entry))

        return {
            "total_entries": total_entries,
            "active_entries": total_entries - expired_entries,
            "expired_entries": expired_entries,
        }


# Global cache instance to be shared across services
_field_cache = FieldCache()


def get_field_cache() -> FieldCache:
    """Get the global field cache instance."""
    return _field_cache
