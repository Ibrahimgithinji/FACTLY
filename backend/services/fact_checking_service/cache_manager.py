"""
Cache Manager for API Responses

Implements caching to avoid repeated API calls and improve performance.
Uses Redis as the primary backend (shared across processes/workers).
Falls back to in-memory TTLCache when Redis is unavailable.
"""

import hashlib
import json
import logging
import os
from typing import Any, Optional, Dict
from cachetools import TTLCache

logger = logging.getLogger(__name__)


class CacheManager:
    """Manages caching of API responses with configurable TTLs.

    Primary backend is Redis (shared across workers). Falls back to
    in-process TTLCache when Redis is unreachable.
    """

    # Default TTL configurations for different data types
    DEFAULT_TTLS = {
        'fact_check': 1800,  # 30 minutes for fact checks
        'news': 600,         # 10 minutes for news
        'realtime': 300,     # 5 minutes for real-time data
        'academic': 86400,   # 24 hours for academic sources
        'official': 3600,    # 1 hour for official sources
        'default': 3600      # 1 hour default
    }

    _CACHE_KEY_PREFIX = 'factly:cache:'

    def __init__(self, maxsize: int = 1000, default_ttl_seconds: int = 3600):
        self.default_ttl = default_ttl_seconds
        self._redis = None
        self._fallback_caches = {}
        self._redis_available = False

        # Initialize fallback caches
        for data_type, ttl in self.DEFAULT_TTLS.items():
            self._fallback_caches[data_type] = TTLCache(maxsize=maxsize, ttl=ttl)

        # Try connecting to Redis
        self._connect_redis()

    def _connect_redis(self):
        try:
            import redis
            redis_host = os.getenv('REDIS_HOST', 'localhost')
            redis_port = int(os.getenv('REDIS_PORT', '6379'))
            redis_db = int(os.getenv('REDIS_DB', '1'))
            redis_password = os.getenv('REDIS_PASSWORD', None) or None

            self._redis = redis.Redis(
                host=redis_host,
                port=redis_port,
                db=redis_db,
                password=redis_password,
                decode_responses=True,
                socket_connect_timeout=2,
                socket_timeout=2,
            )
            self._redis.ping()
            self._redis_available = True
            logger.info("CacheManager connected to Redis at %s:%s/%s", redis_host, redis_port, redis_db)
        except Exception as e:
            self._redis = None
            self._redis_available = False
            logger.warning("CacheManager Redis unavailable, using in-memory fallback: %s", e)

    def _generate_key(self, api_name: str, params: dict) -> str:
        """Generate a unique cache key from API name and parameters."""
        key_data = {
            'api': api_name,
            'params': params
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(key_string.encode()).hexdigest()

    def _redis_key(self, data_type: str, key: str) -> str:
        return f"{self._CACHE_KEY_PREFIX}{data_type}:{key}"

    def get(self, api_name: str, params: dict, data_type: str = 'default') -> Optional[Any]:
        """Retrieve cached response if available."""
        key = self._generate_key(api_name, params)

        if self._redis_available and self._redis:
            try:
                rkey = self._redis_key(data_type, key)
                data = self._redis.get(rkey)
                if data is not None:
                    return json.loads(data)
            except Exception as e:
                logger.error("CacheManager Redis get failed, falling back: %s", e)
                self._redis_available = False

        cache = self._fallback_caches.get(data_type, self._fallback_caches['default'])
        return cache.get(key)

    def set(self, api_name: str, params: dict, response: Any, data_type: str = 'default') -> None:
        """Cache an API response with appropriate TTL."""
        key = self._generate_key(api_name, params)
        ttl = self.DEFAULT_TTLS.get(data_type, self.default_ttl)

        if self._redis_available and self._redis:
            try:
                rkey = self._redis_key(data_type, key)
                self._redis.setex(rkey, ttl, json.dumps(response, default=str))
                return
            except Exception as e:
                logger.error("CacheManager Redis set failed, falling back: %s", e)
                self._redis_available = False

        cache = self._fallback_caches.get(data_type, self._fallback_caches['default'])
        cache[key] = response

    def clear(self, data_type: str = None) -> None:
        """Clear cached responses for specific data type or all."""
        if self._redis_available and self._redis:
            try:
                if data_type:
                    pattern = f"{self._redis_key(data_type, '')}*"
                    cursor = 0
                    while True:
                        cursor, keys = self._redis.scan(cursor=cursor, match=pattern, count=100)
                        if keys:
                            self._redis.delete(*keys)
                        if cursor == 0:
                            break
                else:
                    cursor = 0
                    while True:
                        cursor, keys = self._redis.scan(
                            cursor=cursor, match=f"{self._CACHE_KEY_PREFIX}*", count=100
                        )
                        if keys:
                            self._redis.delete(*keys)
                        if cursor == 0:
                            break
            except Exception as e:
                logger.error("CacheManager Redis clear failed: %s", e)

        if data_type:
            if data_type in self._fallback_caches:
                self._fallback_caches[data_type].clear()
        else:
            for cache in self._fallback_caches.values():
                cache.clear()

    def force_refresh(self, api_name: str, params: dict, data_type: str = 'default') -> None:
        """Force remove cached item to ensure fresh data on next request."""
        key = self._generate_key(api_name, params)

        if self._redis_available and self._redis:
            try:
                rkey = self._redis_key(data_type, key)
                self._redis.delete(rkey)
            except Exception as e:
                logger.error("CacheManager Redis delete failed: %s", e)

        cache = self._fallback_caches.get(data_type, self._fallback_caches['default'])
        if key in cache:
            del cache[key]

    def get_stats(self) -> Dict[str, Dict]:
        """Get cache statistics for all data types."""
        stats = {}
        for data_type, cache in self._fallback_caches.items():
            stats[data_type] = {
                'size': len(cache),
                'maxsize': cache.maxsize,
                'ttl_seconds': self.DEFAULT_TTLS.get(data_type, self.default_ttl),
                'backend': 'redis' if self._redis_available else 'memory',
            }
        return stats
