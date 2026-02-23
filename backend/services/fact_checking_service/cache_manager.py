"""
Cache Manager for API Responses

Implements caching to avoid repeated API calls and improve performance.
Supports different TTLs for different types of data to ensure freshness.
"""

import hashlib
import json
from typing import Any, Optional, Dict
from datetime import datetime, timedelta
from cachetools import TTLCache


class CacheManager:
    """Manages caching of API responses with configurable TTLs."""

    # Default TTL configurations for different data types
    DEFAULT_TTLS = {
        'fact_check': 1800,  # 30 minutes for fact checks
        'news': 600,         # 10 minutes for news
        'realtime': 300,     # 5 minutes for real-time data
        'academic': 86400,   # 24 hours for academic sources
        'official': 3600,    # 1 hour for official sources
        'default': 3600      # 1 hour default
    }

    def __init__(self, maxsize: int = 1000, default_ttl_seconds: int = 3600):
        """
        Initialize cache manager.

        Args:
            maxsize: Maximum number of cached items
            default_ttl_seconds: Default time-to-live in seconds
        """
        self.default_ttl = default_ttl_seconds
        self.caches = {}
        
        # Initialize caches for different data types
        for data_type, ttl in self.DEFAULT_TTLS.items():
            self.caches[data_type] = TTLCache(maxsize=maxsize, ttl=ttl)

    def _generate_key(self, api_name: str, params: dict) -> str:
        """Generate a unique cache key from API name and parameters."""
        key_data = {
            'api': api_name,
            'params': params
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()

    def get(self, api_name: str, params: dict, data_type: str = 'default') -> Optional[Any]:
        """Retrieve cached response if available."""
        cache = self.caches.get(data_type, self.caches['default'])
        key = self._generate_key(api_name, params)
        return cache.get(key)

    def set(self, api_name: str, params: dict, response: Any, data_type: str = 'default') -> None:
        """Cache an API response with appropriate TTL."""
        cache = self.caches.get(data_type, self.caches['default'])
        key = self._generate_key(api_name, params)
        cache[key] = response

    def clear(self, data_type: str = None) -> None:
        """Clear cached responses for specific data type or all."""
        if data_type:
            if data_type in self.caches:
                self.caches[data_type].clear()
        else:
            for cache in self.caches.values():
                cache.clear()

    def force_refresh(self, api_name: str, params: dict, data_type: str = 'default') -> None:
        """Force remove cached item to ensure fresh data on next request."""
        cache = self.caches.get(data_type, self.caches['default'])
        key = self._generate_key(api_name, params)
        if key in cache:
            del cache[key]

    def get_stats(self) -> Dict[str, Dict]:
        """Get cache statistics for all data types."""
        stats = {}
        for data_type, cache in self.caches.items():
            stats[data_type] = {
                'size': len(cache),
                'maxsize': cache.maxsize,
                'ttl_seconds': getattr(cache, 'ttl', None)
            }
        return stats