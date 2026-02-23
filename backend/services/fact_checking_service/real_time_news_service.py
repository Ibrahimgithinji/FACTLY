"""
Real-Time News Service

Provides access to the most current global news and information through
multiple real-time news APIs and RSS feeds. Ensures Factly has access
to breaking news and recent developments for accurate fact-checking.
"""

import os
import requests
import logging
import feedparser
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed

from .unified_schema import RelatedNews, SourceReliability
from .cache_manager import CacheManager
from .rate_limiter import RateLimiter

logger = logging.getLogger(__name__)


@dataclass
class RealTimeNewsItem:
    """Real-time news item with freshness indicators."""
    title: str
    content: str
    url: str
    published_date: datetime
    source: str
    freshness_score: float  # 0.0 to 1.0 (how recent)
    relevance_score: float  # 0.0 to 1.0 (how relevant to query)
    credibility_score: float  # 0.0 to 1.0 (source credibility)
    metadata: Dict[str, Any]


class RealTimeNewsService:
    """
    Service for fetching real-time news from multiple sources.
    
    Integrates with:
    - NewsAPI (real-time news)
    - RSS feeds from major news sources
    - Twitter/X API for breaking news
    - Google News API
    """

    # Major news sources RSS feeds
    RSS_FEEDS = {
        'bbc': 'http://feeds.bbci.co.uk/news/rss.xml',
        'cnn': 'http://rss.cnn.com/rss/edition.rss',
        'reuters': 'https://feeds.reuters.com/Reuters/worldNews',
        'ap': 'https://feeds.apnews.com/rss/apf-topnews',
        'nyt': 'https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml',
        'guardian': 'https://www.theguardian.com/world/rss',
        'aljazeera': 'https://www.aljazeera.com/xml/rss/all.xml'
    }

    def __init__(self, cache_manager: Optional[CacheManager] = None):
        """
        Initialize real-time news service.

        Args:
            cache_manager: Cache manager instance
        """
        self.cache = cache_manager or CacheManager()
        self.rate_limiter = RateLimiter()

        # API keys
        self.newsapi_key = os.getenv('NEWSAPI_KEY')
        self.google_news_key = os.getenv('GOOGLE_NEWS_API_KEY')
        self.twitter_bearer_token = os.getenv('TWITTER_BEARER_TOKEN')

    def get_real_time_news(self, query: str, max_results: int = 20,
                          max_age_hours: int = 24) -> List[RealTimeNewsItem]:
        """
        Get real-time news related to a query.

        Args:
            query: Search query
            max_results: Maximum number of results
            max_age_hours: Maximum age of news in hours

        Returns:
            List of RealTimeNewsItem objects
        """
        logger.info(f"Fetching real-time news for query: {query}")

        # Check cache first (very short TTL for real-time data)
        cache_key = {'query': query, 'max_results': max_results, 'max_age_hours': max_age_hours}
        cached = self.cache.get('realtime_news', cache_key, data_type='realtime')
        if cached:
            logger.info("Returning cached real-time news")
            return cached

        all_news = []

        # Fetch from multiple sources concurrently
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = []

            # NewsAPI
            if self.newsapi_key:
                futures.append(executor.submit(self._fetch_newsapi, query, max_results))

            # RSS feeds
            futures.append(executor.submit(self._fetch_rss_feeds, query, max_results))

            # Google News
            if self.google_news_key:
                futures.append(executor.submit(self._fetch_google_news, query, max_results))

            # Twitter/X
            if self.twitter_bearer_token:
                futures.append(executor.submit(self._fetch_twitter_news, query, max_results))

            # Collect results
            for future in as_completed(futures):
                try:
                    news_items = future.result()
                    if news_items:
                        all_news.extend(news_items)
                except Exception as e:
                    logger.error(f"Error fetching from news source: {e}")

        # Filter by age and relevance
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        filtered_news = [
            item for item in all_news
            if item.published_date >= cutoff_time
        ]

        # Sort by freshness and relevance
        filtered_news.sort(
            key=lambda x: (x.freshness_score + x.relevance_score),
            reverse=True
        )

        # Limit results
        result = filtered_news[:max_results]

        # Cache result
        self.cache.set('realtime_news', cache_key, result, data_type='realtime')

        logger.info(f"Found {len(result)} real-time news items")
        return result

    def _fetch_newsapi(self, query: str, max_results: int) -> List[RealTimeNewsItem]:
        """Fetch from NewsAPI."""
        try:
            url = "https://newsapi.org/v2/everything"
            params = {
                'q': query,
                'sortBy': 'publishedAt',
                'pageSize': max_results,
                'apiKey': self.newsapi_key
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            news_items = []
            for article in data.get('articles', []):
                published_date = datetime.fromisoformat(
                    article['publishedAt'].replace('Z', '+00:00')
                )

                # Calculate freshness score (newer = higher score)
                hours_old = (datetime.now() - published_date).total_seconds() / 3600
                freshness_score = max(0, 1 - (hours_old / 24))  # 1.0 for <1h, 0.0 for >24h

                news_item = RealTimeNewsItem(
                    title=article['title'],
                    content=article.get('description', ''),
                    url=article['url'],
                    published_date=published_date,
                    source=article['source']['name'],
                    freshness_score=freshness_score,
                    relevance_score=0.8,  # NewsAPI results are generally relevant
                    credibility_score=self._get_source_credibility(article['source']['name']),
                    metadata={'api': 'newsapi'}
                )
                news_items.append(news_item)

            return news_items

        except Exception as e:
            logger.error(f"NewsAPI error: {e}")
            return []

    def _fetch_rss_feeds(self, query: str, max_results: int) -> List[RealTimeNewsItem]:
        """Fetch from RSS feeds."""
        all_items = []

        for source_name, feed_url in self.RSS_FEEDS.items():
            try:
                feed = feedparser.parse(feed_url)

                for entry in feed.entries[:max_results // len(self.RSS_FEEDS)]:
                    # Check if entry matches query (simple text search)
                    text_content = f"{entry.title} {getattr(entry, 'description', '')}".lower()
                    if query.lower() not in text_content:
                        continue

                    published_date = self._parse_rss_date(entry)

                    # Calculate freshness score
                    hours_old = (datetime.now() - published_date).total_seconds() / 3600
                    freshness_score = max(0, 1 - (hours_old / 24))

                    news_item = RealTimeNewsItem(
                        title=entry.title,
                        content=getattr(entry, 'description', ''),
                        url=entry.link,
                        published_date=published_date,
                        source=source_name.upper(),
                        freshness_score=freshness_score,
                        relevance_score=0.7,  # RSS feeds are curated
                        credibility_score=self._get_source_credibility(source_name),
                        metadata={'api': 'rss', 'feed': source_name}
                    )
                    all_items.append(news_item)

            except Exception as e:
                logger.error(f"RSS feed error for {source_name}: {e}")

        return all_items

    def _fetch_google_news(self, query: str, max_results: int) -> List[RealTimeNewsItem]:
        """Fetch from Google News API."""
        try:
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                'q': query,
                'cx': '017576662512468239146:omuauf_lfve',  # Google News search engine
                'sort': 'date',
                'num': max_results,
                'key': self.google_news_key
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            news_items = []
            for item in data.get('items', []):
                # Estimate published date (Google doesn't always provide exact dates)
                published_date = datetime.now() - timedelta(hours=1)  # Assume recent

                news_item = RealTimeNewsItem(
                    title=item['title'],
                    content=item.get('snippet', ''),
                    url=item['link'],
                    published_date=published_date,
                    source='Google News',
                    freshness_score=0.9,  # Google News tends to be current
                    relevance_score=0.8,
                    credibility_score=0.7,
                    metadata={'api': 'google_news'}
                )
                news_items.append(news_item)

            return news_items

        except Exception as e:
            logger.error(f"Google News API error: {e}")
            return []

    def _fetch_twitter_news(self, query: str, max_results: int) -> List[RealTimeNewsItem]:
        """Fetch breaking news from Twitter/X."""
        try:
            url = "https://api.twitter.com/2/tweets/search/recent"
            headers = {'Authorization': f'Bearer {self.twitter_bearer_token}'}
            params = {
                'query': f'{query} -is:retweet',
                'max_results': min(max_results, 100),
                'tweet.fields': 'created_at,public_metrics,text'
            }

            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            news_items = []
            for tweet in data.get('data', []):
                published_date = datetime.fromisoformat(
                    tweet['created_at'].replace('Z', '+00:00')
                )

                # Calculate freshness score (Twitter is very real-time)
                minutes_old = (datetime.now() - published_date).total_seconds() / 60
                freshness_score = max(0, 1 - (minutes_old / 60))  # 1.0 for <1min, 0.0 for >1h

                news_item = RealTimeNewsItem(
                    title=f"Tweet: {tweet['text'][:100]}...",
                    content=tweet['text'],
                    url=f"https://twitter.com/i/status/{tweet['id']}",
                    published_date=published_date,
                    source='Twitter/X',
                    freshness_score=freshness_score,
                    relevance_score=0.6,  # Twitter can be noisy
                    credibility_score=0.5,  # Varies by account
                    metadata={'api': 'twitter', 'tweet_id': tweet['id']}
                )
                news_items.append(news_item)

            return news_items

        except Exception as e:
            logger.error(f"Twitter API error: {e}")
            return []

    def _parse_rss_date(self, entry) -> datetime:
        """Parse RSS date formats."""
        date_str = getattr(entry, 'published_parsed', None)
        if date_str:
            try:
                return datetime(*date_str[:6])
            except:
                pass

        # Fallback to current time if parsing fails
        return datetime.now() - timedelta(hours=2)

    def _get_source_credibility(self, source_name: str) -> float:
        """Get credibility score for a news source."""
        credibility_map = {
            'BBC': 0.95,
            'CNN': 0.85,
            'Reuters': 0.95,
            'AP': 0.95,
            'New York Times': 0.90,
            'The Guardian': 0.85,
            'Al Jazeera': 0.80,
            'NewsAPI': 0.75,
            'Google News': 0.70,
            'Twitter': 0.50
        }

        # Case-insensitive matching
        for key, score in credibility_map.items():
            if key.lower() in source_name.lower():
                return score

        return 0.6  # Default credibility