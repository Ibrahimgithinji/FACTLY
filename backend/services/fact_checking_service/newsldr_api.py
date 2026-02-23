"""
NewsLdr API Client

Integrates with NewsLdr API for news coverage analysis and source reliability.
"""

import os
import requests
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from .unified_schema import RelatedNews, SourceReliability
from .cache_manager import CacheManager
from .rate_limiter import RateLimiter

logger = logging.getLogger(__name__)


class NewsLdrClient:
    """Client for NewsLdr API."""

    BASE_URL = "https://api.newsldr.com/v1"  # Placeholder - replace with actual API endpoint

    def __init__(self, api_key: Optional[str] = None, cache_manager: Optional[CacheManager] = None):
        """
        Initialize NewsLdr client.

        Args:
            api_key: NewsLdr API key (defaults to environment variable)
            cache_manager: Cache manager instance
        """
        self.api_key = api_key or os.getenv('NEWSLDR_API_KEY')
        if not self.api_key:
            raise ValueError("NewsLdr API key not provided")

        self.cache = cache_manager or CacheManager()
        self.rate_limiter = RateLimiter()

    def get_related_news(self, query: str, max_results: int = 10) -> List[RelatedNews]:
        """
        Get related news coverage for a query.

        Args:
            query: Search query for related news
            max_results: Maximum number of results to return

        Returns:
            List of RelatedNews objects
        """
        cache_key = {
            'query': query,
            'max_results': max_results,
            'endpoint': 'related_news'
        }

        # Check cache first
        cached_result = self.cache.get('newsldr', cache_key, data_type='news')
        if cached_result:
            logger.info("Returning cached NewsLdr related news results")
            return cached_result

        # Make API call with rate limiting
        try:
            result = self.rate_limiter.newsldr_api_call(self._get_related_news_api, query, max_results)
            self.cache.set('newsldr', cache_key, result, data_type='news')
            return result
        except Exception as e:
            logger.error(f"Error getting NewsLdr related news: {e}")
            return []

    def _get_related_news_api(self, query: str, max_results: int) -> List[RelatedNews]:
        """Internal method to make the actual API call for related news."""
        # Placeholder implementation - replace with actual API calls
        # This would need to be adapted based on the actual NewsLdr API documentation

        endpoint = f"{self.BASE_URL}/news/search"
        headers = {
            'Authorization': f'Bearer {self.api_key}',  # Use header to avoid logging/history exposure
            'Accept': 'application/json'
        }
        params = {
            'q': query,
            'limit': max_results
        }

        response = requests.get(endpoint, params=params, headers=headers, timeout=30)
        response.raise_for_status()

        data = response.json()
        return self._parse_related_news_response(data)

    def _parse_related_news_response(self, data: Dict[str, Any]) -> List[RelatedNews]:
        """Parse API response into RelatedNews objects."""
        articles = data.get('articles', [])
        related_news = []

        for article in articles:
            try:
                publish_date = datetime.fromisoformat(article.get('publishedAt', '').replace('Z', '+00:00'))
            except:
                publish_date = datetime.now()

            news_item = RelatedNews(
                title=article.get('title', ''),
                url=article.get('url', ''),
                source=article.get('source', {}).get('name', ''),
                publish_date=publish_date,
                relevance_score=article.get('relevance_score', 0.5),  # Placeholder
                sentiment=article.get('sentiment'),
                metadata=article
            )
            related_news.append(news_item)

        return related_news

    def get_source_reliability(self, source_name: str) -> Optional[SourceReliability]:
        """
        Get reliability assessment for a news source.

        Args:
            source_name: Name of the news source

        Returns:
            SourceReliability object or None if not found
        """
        cache_key = {
            'source_name': source_name,
            'endpoint': 'source_reliability'
        }

        # Check cache first
        cached_result = self.cache.get('newsldr', cache_key, data_type='official')
        if cached_result:
            logger.info("Returning cached NewsLdr source reliability result")
            return cached_result

        # Make API call with rate limiting
        try:
            result = self.rate_limiter.newsldr_api_call(self._get_source_reliability_api, source_name)
            self.cache.set('newsldr', cache_key, result, data_type='official')
            return result
        except Exception as e:
            logger.error(f"Error getting NewsLdr source reliability: {e}")
            return None

    def _get_source_reliability_api(self, source_name: str) -> Optional[SourceReliability]:
        """Internal method to make the actual API call for source reliability."""
        # Placeholder implementation - replace with actual API calls

        endpoint = f"{self.BASE_URL}/sources/reliability"
        headers = {
            'Authorization': f'Bearer {self.api_key}',  # Use header to avoid logging/history exposure
            'Accept': 'application/json'
        }
        params = {
            'name': source_name
        }

        response = requests.get(endpoint, params=params, headers=headers, timeout=30)
        response.raise_for_status()

        data = response.json()
        return self._parse_source_reliability_response(data)

    def _parse_source_reliability_response(self, data: Dict[str, Any]) -> Optional[SourceReliability]:
        """Parse API response into SourceReliability object."""
        if not data.get('source'):
            return None

        source_data = data['source']

        reliability = SourceReliability(
            source_name=source_data.get('name', ''),
            reliability_score=source_data.get('reliability_score', 0.5),
            bias_rating=source_data.get('bias_rating'),
            factual_reporting=source_data.get('factual_reporting', 0.5),
            historical_patterns=source_data.get('historical_patterns', {}),
            metadata=source_data
        )

        return reliability