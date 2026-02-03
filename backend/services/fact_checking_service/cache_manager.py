"""
Cache Manager for API Responses

Implements caching to avoid repeated API calls and improve performance.
"""

import hashlib
import json
from typing import Any, Optional
from datetime import datetime, timedelta
from cachetools import TTLCache


class CacheManager:
    """Manages caching of API responses with TTL."""

    def __init__(self, maxsize: int = 1000, ttl_seconds: int = 3600):
        """
        Initialize cache manager.

        Args:
            maxsize: Maximum number of cached items
            ttl_seconds: Time-to-live in seconds for cached items
        """
        self.cache = TTLCache(maxsize=maxsize, ttl=ttl_seconds)

    def _generate_key(self, api_name: str, params: dict) -> str:
        """Generate a unique cache key from API name and parameters."""
        key_data = {
            'api': api_name,
            'params': params
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()

    def get(self, api_name: str, params: dict) -> Optional[Any]:
        """Retrieve cached response if available."""
        key = self._generate_key(api_name, params)
        return self.cache.get(key)

    def set(self, api_name: str, params: dict, response: Any) -> None:
        """Cache an API response."""
        key = self._generate_key(api_name, params)
        self.cache[key] = response

    def clear(self) -> None:
        """Clear all cached responses."""
        self.cache.clear()

    def get_stats(self) -> dict:
        """Get cache statistics."""
        return {
            'size': len(self.cache),
            'maxsize': self.cache.maxsize,
            'ttl': getattr(self.cache, 'ttl', None)
        }