"""
Refresh Tasks for FACTLY

Scheduled Celery tasks to keep FACTLY updated with global events.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any
from celery import shared_task
from celery.exceptions import MaxRetriesExceededError

from services.fact_checking_service.cache_manager import CacheManager
from services.fact_checking_service.real_time_news_service import RealTimeNewsService
from services.fact_checking_service.real_time_verification_engine import RealTimeVerificationEngine
from services.fact_checking_service.google_fact_check import GoogleFactCheckClient

logger = logging.getLogger(__name__)

# Initialize services
cache_manager = CacheManager()
realtime_news = RealTimeNewsService(cache_manager=cache_manager)
verification_engine = RealTimeVerificationEngine(cache_manager=cache_manager)

# Global trending topics storage (in production, use Redis/database)
_trending_topics_cache = {
    'topics': [],
    'last_updated': None,
    'global_events': [],
}


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def refresh_realtime_data(self):
    """
    Refresh real-time news data cache.
    Runs every 5 minutes to ensure fresh data.
    """
    try:
        logger.info("Starting real-time data refresh task")
        
        # Clear real-time caches to force fresh data
        cache_manager.clear(data_type='realtime')
        cache_manager.clear(data_type='news')
        
        # Pre-fetch trending topics to warm cache
        trending_queries = [
            "breaking news",
            "world news today",
            "latest developments",
        ]
        
        for query in trending_queries:
            try:
                results = realtime_news.get_real_time_news(query, max_results=5)
                logger.info(f"Pre-fetched {len(results)} items for query: {query}")
            except Exception as e:
                logger.warning(f"Failed to pre-fetch for query '{query}': {e}")
        
        logger.info("Real-time data refresh completed successfully")
        return {
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'cache_types_cleared': ['realtime', 'news']
        }
        
    except Exception as exc:
        logger.error(f"Real-time data refresh failed: {exc}")
        try:
            self.retry(exc=exc)
        except MaxRetriesExceededError:
            logger.error("Max retries exceeded for real-time data refresh")
            return {'status': 'failed', 'error': str(exc)}


@shared_task(bind=True, max_retries=3, default_retry_delay=120)
def update_trending_topics(self):
    """
    Update trending topics based on real-time news.
    Runs every 15 minutes.
    """
    try:
        logger.info("Starting trending topics update")
        
        # Fetch breaking news
        breaking_news = realtime_news.get_real_time_news(
            "breaking news",
            max_results=20,
            max_age_hours=2
        )
        
        # Fetch world news
        world_news = realtime_news.get_real_time_news(
            "world news",
            max_results=20,
            max_age_hours=6
        )
        
        # Combine and analyze for trending topics
        all_news = breaking_news + world_news
        
        # Extract trending topics (simplified extraction)
        trending = extract_trending_topics(all_news)
        
        # Update cache
        _trending_topics_cache['topics'] = trending
        _trending_topics_cache['last_updated'] = datetime.now()
        
        # Cache in the main cache manager
        cache_manager.set(
            'trending_service',
            {'type': 'trending_topics'},
            trending,
            data_type='realtime'
        )
        
        logger.info(f"Updated {len(trending)} trending topics")
        return {
            'status': 'success',
            'topics_count': len(trending),
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as exc:
        logger.error(f"Trending topics update failed: {exc}")
        try:
            self.retry(exc=exc)
        except MaxRetriesExceededError:
            return {'status': 'failed', 'error': str(exc)}


@shared_task(bind=True, max_retries=2, default_retry_delay=300)
def update_global_events(self):
    """
    Update global events digest from multiple regions.
    Runs every 30 minutes.
    """
    try:
        logger.info("Starting global events update")
        
        regions = [
            ('north_america', 'US Canada news'),
            ('europe', 'Europe UK news'),
            ('asia_pacific', 'Asia Pacific China Japan news'),
            ('africa', 'Africa news'),
            ('middle_east', 'Middle East news'),
        ]
        
        global_events = []
        
        for region_id, query in regions:
            try:
                # Fetch regional news
                news_items = realtime_news.get_regional_news(
                    query=query,
                    region=region_id,
                    sources=['reuters', 'bbc', 'ap'],
                    max_results=5,
                    max_age_hours=12
                )
                
                global_events.append({
                    'region': region_id,
                    'region_name': region_id.replace('_', ' ').title(),
                    'headlines': [
                        {
                            'title': item.get('title', ''),
                            'source': item.get('source', ''),
                            'url': item.get('url', ''),
                            'published': item.get('published_date', ''),
                            'freshness_score': item.get('freshness_score', 0)
                        }
                        for item in news_items[:3]  # Top 3 per region
                    ],
                    'updated_at': datetime.now().isoformat()
                })
                
            except Exception as e:
                logger.warning(f"Failed to fetch news for region {region_id}: {e}")
        
        # Update cache
        _trending_topics_cache['global_events'] = global_events
        cache_manager.set(
            'global_events',
            {'type': 'digest'},
            global_events,
            data_type='realtime'
        )
        
        logger.info(f"Updated global events for {len(global_events)} regions")
        return {
            'status': 'success',
            'regions_count': len(global_events),
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as exc:
        logger.error(f"Global events update failed: {exc}")
        try:
            self.retry(exc=exc)
        except MaxRetriesExceededError:
            return {'status': 'failed', 'error': str(exc)}


@shared_task(bind=True)
def cleanup_cache(self):
    """
    Cleanup old cache entries.
    Runs every hour.
    """
    try:
        logger.info("Starting cache cleanup")
        
        stats_before = cache_manager.get_stats()
        
        # The TTLCache automatically removes expired items
        # This task is mainly for logging and monitoring
        
        stats_after = cache_manager.get_stats()
        
        logger.info("Cache cleanup completed")
        return {
            'status': 'success',
            'stats_before': stats_before,
            'stats_after': stats_after,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as exc:
        logger.error(f"Cache cleanup failed: {exc}")
        return {'status': 'failed', 'error': str(exc)}


@shared_task(bind=True, max_retries=2, default_retry_delay=600)
def refresh_fact_check_cache(self):
    """
    Refresh fact-check database cache.
    Runs daily.
    """
    try:
        logger.info("Starting fact-check cache refresh")
        
        cache_manager.clear(data_type='fact_check')
        
        # Pre-fetch popular fact-checks if Google API key is available
        try:
            google_client = GoogleFactCheckClient(cache_manager=cache_manager)
            
            # Search for common claim topics
            common_topics = [
                "election",
                "health",
                "climate",
                "economy",
            ]
            
            for topic in common_topics:
                try:
                    results = google_client.search_claims(topic, max_results=5)
                    logger.info(f"Pre-fetched {len(results)} fact-checks for topic: {topic}")
                except Exception as e:
                    logger.warning(f"Failed to pre-fetch fact-checks for '{topic}': {e}")
                    
        except ValueError as e:
            logger.warning(f"Google Fact Check API not configured: {e}")
        
        logger.info("Fact-check cache refresh completed")
        return {
            'status': 'success',
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as exc:
        logger.error(f"Fact-check cache refresh failed: {exc}")
        try:
            self.retry(exc=exc)
        except MaxRetriesExceededError:
            return {'status': 'failed', 'error': str(exc)}


def extract_trending_topics(news_items: List[Any]) -> List[Dict[str, Any]]:
    """
    Extract trending topics from news items.
    Simplified keyword extraction - in production, use NLP.
    """
    from collections import Counter
    import re
    
    # Common words to exclude
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                  'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during',
                  'before', 'after', 'above', 'below', 'between', 'among', 'is', 'are',
                  'was', 'were', 'been', 'have', 'has', 'had', 'do', 'does', 'did',
                  'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can',
                  'said', 'says', 'say', 'new', 'more', 'all', 'some', 'many', 'most',
                  'other', 'time', 'year', 'years', 'day', 'days', 'way', 'ways'}
    
    # Extract keywords from titles
    all_words = []
    for item in news_items:
        title = item.title if hasattr(item, 'title') else item.get('title', '')
        # Simple word extraction
        words = re.findall(r'\b[A-Za-z]{4,}\b', title.lower())
        all_words.extend([w for w in words if w not in stop_words])
    
    # Count word frequency
    word_counts = Counter(all_words)
    
    # Get top trending topics
    trending = []
    for word, count in word_counts.most_common(10):
        if count >= 2:  # Only include if mentioned multiple times
            trending.append({
                'topic': word.title(),
                'mentions': count,
                'trending_score': min(1.0, count / 5.0),  # Normalize to 0-1
            })
    
    return trending


def get_trending_topics() -> Dict[str, Any]:
    """
    Get current trending topics (called by views).
    """
    # Try to get from cache first
    cached = cache_manager.get('trending_service', {'type': 'trending_topics'}, data_type='realtime')
    if cached:
        return {
            'topics': cached,
            'last_updated': _trending_topics_cache.get('last_updated'),
            'source': 'cache'
        }
    
    # Return from memory if available
    return {
        'topics': _trending_topics_cache.get('topics', []),
        'global_events': _trending_topics_cache.get('global_events', []),
        'last_updated': _trending_topics_cache.get('last_updated'),
        'source': 'memory'
    }


def get_global_events() -> List[Dict[str, Any]]:
    """
    Get global events digest (called by views).
    """
    # Try to get from cache first
    cached = cache_manager.get('global_events', {'type': 'digest'}, data_type='realtime')
    if cached:
        return cached
    
    return _trending_topics_cache.get('global_events', [])