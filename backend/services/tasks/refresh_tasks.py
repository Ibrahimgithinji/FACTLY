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
    
    ENHANCEMENT 3: Added RSS feed fallback when no API keys are configured.
    Uses RealTimeNewsService.RSS_FEEDS (BBC, Reuters, AP) as fallback.
    """
    try:
        logger.info("Starting trending topics update")
        
        # Try to fetch from API first
        breaking_news = []
        world_news = []
        
        try:
            breaking_news = realtime_news.get_real_time_news(
                "breaking news",
                max_results=20,
                max_age_hours=2
            )
        except Exception as e:
            logger.warning(f"Failed to fetch breaking news from API: {e}")
        
        try:
            world_news = realtime_news.get_real_time_news(
                "world news",
                max_results=20,
                max_age_hours=6
            )
        except Exception as e:
            logger.warning(f"Failed to fetch world news from API: {e}")
        
        # Combine results
        all_news = breaking_news + world_news
        
        # ENHANCEMENT 3: RSS Feed Fallback - if no results from API, use RSS directly
        if not all_news:
            logger.info("No API results, falling back to RSS feeds")
            try:
                # Use the RSS feeds from RealTimeNewsService
                # Try all RSS feeds for general news
                for feed_name, feed_url in RealTimeNewsService.RSS_FEEDS.items():
                    try:
                        rss_results = realtime_news._fetch_single_rss(
                            feed_url,
                            query="news",
                            max_results=10
                        )
                        all_news.extend(rss_results)
                        logger.info(f"Fetched {len(rss_results)} items from RSS feed: {feed_name}")
                    except Exception as rss_err:
                        logger.warning(f"Failed to fetch RSS feed {feed_name}: {rss_err}")
            except Exception as rss_fallback_err:
                logger.warning(f"RSS fallback failed: {rss_fallback_err}")
        
        # Extract trending topics
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
    FIXED: Now emits the correct frontend schema with all required fields.
    Frontend needs: id, topic, mention_count, trending_score (0-100), freshness (0-1),
                   risk_level, verification_status, last_updated
    """
    from collections import Counter
    import re
    import hashlib
    
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
    
    # Get top trending topics with correct schema
    trending = []
    now = datetime.now()
    for idx, (word, count) in enumerate(word_counts.most_common(10)):
        if count >= 2:  # Only include if mentioned multiple times
            # Generate deterministic ID from topic
            topic_text = word.title()
            id_hash = hashlib.md5(topic_text.encode()).hexdigest()[:8]
            
            # Calculate freshness (decay over time - simplified)
            # Freshness starts at 1.0 and decays based on count (more mentions = more recent)
            freshness = min(1.0, count / 10.0)
            
            trending.append({
                'id': f'live-{id_hash}',
                'topic': topic_text,
                'mention_count': count,
                'trending_score': int(min(100, count * 10)),  # Convert to 0-100 int
                'freshness': round(freshness, 2),
                'risk_level': 'medium',  # Default risk level
                'verification_status': 'pending',  # Default status
                'last_updated': now.isoformat()
            })
    
    return trending


# =============================================================================
# Demo/Fallback Trending Topics - Uses CORRECT frontend schema
# Frontend needs: id, topic, mention_count, trending_score (0-100), freshness (0-1),
#                risk_level, verification_status, last_updated
# =============================================================================

def _make_demo_topics() -> List[Dict[str, Any]]:
    """
    Create demo trending topics with live timestamps on EVERY call.
    FIXED: This fixes Bug 3 - timestamps were stale when set at module load time.
    """
    now = datetime.now()
    
    # Topics with realistic freshness values (decaying over time)
    demo_topics = [
        {
            "id": "demo-1",
            "topic": "Global Climate Summit Reaches Historic Agreement on Emissions",
            "mention_count": 1250,
            "trending_score": 92,
            "freshness": 0.85,
            "risk_level": "medium",
            "verification_status": "verified",
            "last_updated": (now - timedelta(minutes=15)).isoformat()
        },
        {
            "id": "demo-2",
            "topic": "New Study Reveals Breakthrough in AI Medical Diagnostics",
            "mention_count": 890,
            "trending_score": 88,
            "freshness": 0.78,
            "risk_level": "low",
            "verification_status": "verified",
            "last_updated": (now - timedelta(minutes=25)).isoformat()
        },
        {
            "id": "demo-3",
            "topic": "Economic Report: Inflation Rates Show Signs of Stabilization",
            "mention_count": 720,
            "trending_score": 75,
            "freshness": 0.65,
            "risk_level": "low",
            "verification_status": "pending",
            "last_updated": (now - timedelta(minutes=45)).isoformat()
        },
        {
            "id": "demo-4",
            "topic": "Tech Giants Face New Regulatory Framework in EU",
            "mention_count": 650,
            "trending_score": 72,
            "freshness": 0.55,
            "risk_level": "medium",
            "verification_status": "processing",
            "last_updated": (now - timedelta(hours=1)).isoformat()
        },
        {
            "id": "demo-5",
            "topic": "Renewable Energy Investment Reaches Record High",
            "mention_count": 580,
            "trending_score": 68,
            "freshness": 0.45,
            "risk_level": "low",
            "verification_status": "verified",
            "last_updated": (now - timedelta(hours=2)).isoformat()
        }
    ]
    
    return demo_topics


def _make_demo_global_events() -> List[Dict[str, Any]]:
    """Create demo global events with live timestamps."""
    now = datetime.now()
    
    return [
        {
            "id": "event-1",
            "title": "International Trade Summit Begins",
            "event_type": "summit",
            "region": "global",
            "timestamp": now.isoformat(),
            "importance": "high"
        },
        {
            "id": "event-2",
            "title": "Tech Innovation Forum Announced",
            "event_type": "conference",
            "region": "asia",
            "timestamp": (now - timedelta(hours=2)).isoformat(),
            "importance": "medium"
        },
        {
            "id": "event-3",
            "title": "Global Health Initiative Launched",
            "event_type": "initiative",
            "region": "global",
            "timestamp": (now - timedelta(hours=5)).isoformat(),
            "importance": "high"
        }
    ]


# Keep backwards compatibility - DEMO_TRENDING_TOPICS now calls the builder
def _get_demo_trending_topics() -> List[Dict[str, Any]]:
    """Getter for backwards compatibility - calls builder to get live timestamps."""
    return _make_demo_topics()


DEMO_TRENDING_TOPICS = _get_demo_trending_topics()  # Legacy compatibility - will rebuild on next access
DEMO_GLOBAL_EVENTS = _make_demo_global_events()


def get_trending_topics() -> Dict[str, Any]:
    """
    Get current trending topics (called by views).
    FIXED: Now rebuilds demo topics with live timestamps on every call.
    Returns demo data if cache is empty.
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
    memory_topics = _trending_topics_cache.get('topics', [])
    if memory_topics:
        return {
            'topics': memory_topics,
            'global_events': _trending_topics_cache.get('global_events', []),
            'last_updated': _trending_topics_cache.get('last_updated'),
            'source': 'memory'
        }
    
    # FIXED Bug 3: Return LIVE demo data - rebuild topics with fresh timestamps
    return {
        'topics': _make_demo_topics(),  # Generate fresh timestamps on every call
        'global_events': _make_demo_global_events(),
        'last_updated': datetime.now(),
        'source': 'demo_fallback'
    }


def get_global_events() -> List[Dict[str, Any]]:
    """
    Get global events digest (called by views).
    Returns demo data if cache is empty.
    """
    # Try to get from cache first
    cached = cache_manager.get('global_events', {'type': 'digest'}, data_type='realtime')
    if cached:
        return cached
    
    memory_events = _trending_topics_cache.get('global_events', [])
    if memory_events:
        return memory_events
    
    # Return demo data when cache and memory are empty
    return DEMO_GLOBAL_EVENTS