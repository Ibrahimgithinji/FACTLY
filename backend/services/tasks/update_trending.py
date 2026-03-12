"""
Live Trending Stories Update Task

Fetches trending stories from NewsAPI.org and NewsData.io
and caches them in Redis for 10 minutes.

Runs every 10 minutes via Celery beat.
"""

import os
import logging
from datetime import datetime

import requests
import json
import redis
from celery import shared_task

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Redis client configuration
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_DB = int(os.getenv('REDIS_DB', 0))

try:
    redis_client = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=REDIS_DB,
        decode_responses=True
    )
    redis_available = True
except Exception as e:
    logger.warning(f"Redis not available: {e}")
    redis_client = None
    redis_available = False


def update_trending_stories():
    """
    Fetch trending stories from NewsAPI and NewsData.io.
    Returns cached data if Redis is available, otherwise returns fresh data.
    """
    newsapi_key = os.getenv("NEWSAPI_KEY")
    newsdata_key = os.getenv("NEWSDATA_IO_KEY")
    
    # If no API keys configured, return empty or cached data
    if not newsapi_key and not newsdata_key:
        logger.warning("Missing API keys — falling back to cache only")
        
        # Try to return cached data if available
        if redis_client:
            try:
                cached = redis_client.get("trending_stories_cache")
                if cached:
                    logger.info("Returning cached trending stories")
                    return json.loads(cached)
            except Exception as e:
                logger.error(f"Cache read error: {e}")
        
        return {"trending_stories": []}
    
    trending_list = []
    
    # Configure session with timeout
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Factly/1.0 (Truth Verification Platform)'
    })
    
    try:
        # Fetch from NewsAPI.org
        if newsapi_key:
            url1 = f"https://newsapi.org/v2/top-headlines"
            params1 = {
                'country': 'us',
                'sortBy': 'popularity',
                'pageSize': 10,
                'apiKey': newsapi_key
            }
            resp1 = session.get(url1, params=params1, timeout=10)
            
            if resp1.status_code == 200:
                data1 = resp1.json()
                articles = data1.get("articles", [])
                
                for a in articles:
                    title = a.get("title", "")
                    if title and title != "[Removed]":
                        trending_list.append({
                            "title": title,
                            "summary": ((a.get("description") or "")[:120] + "...") if a.get("description") else "",
                            "source": a.get("source", {}).get("name", "Unknown"),
                            "timestamp": a.get("publishedAt", datetime.utcnow().isoformat()),
                            "url": a.get("url", ""),
                            "verification_note": "Live via NewsAPI.org"
                        })
                        
            elif resp1.status_code == 401:
                logger.error("NewsAPI: Invalid API key")
            elif resp1.status_code == 429:
                logger.warning("NewsAPI: Rate limit exceeded")
            else:
                logger.error(f"NewsAPI: HTTP {resp1.status_code}")
                
    except requests.exceptions.Timeout:
        logger.error("NewsAPI request timed out")
    except requests.exceptions.RequestException as e:
        logger.error(f"NewsAPI request error: {e}")
    except Exception as e:
        logger.error(f"NewsAPI error: {e}")
    
    # Fetch from NewsData.io if we don't have enough stories
    if len(trending_list) < 5 and newsdata_key:
        try:
            url2 = f"https://newsdata.io/api/1/latest"
            params2 = {
                'apikey': newsdata_key,
                'language': 'en',
                'size': 10
            }
            resp2 = session.get(url2, params=params2, timeout=10)
            
            if resp2.status_code == 200:
                data2 = resp2.json()
                results = data2.get("results", [])
                
                for r in results:
                    title = r.get("title", "")
                    if title:
                        trending_list.append({
                            "title": title,
                            "summary": ((r.get("description") or "")[:120] + "...") if r.get("description") else "",
                            "source": r.get("source_name", "Unknown"),
                            "timestamp": r.get("pubDate", datetime.utcnow().isoformat()),
                            "url": r.get("link", ""),
                            "verification_note": "Live via NewsData.io"
                        })
                        
            elif resp2.status_code == 401:
                logger.error("NewsData.io: Invalid API key")
            elif resp2.status_code == 429:
                logger.warning("NewsData.io: Rate limit exceeded")
            else:
                logger.error(f"NewsData.io: HTTP {resp2.status_code}")
                
        except requests.exceptions.Timeout:
            logger.error("NewsData.io request timed out")
        except requests.exceptions.RequestException as e:
            logger.error(f"NewsData.io request error: {e}")
        except Exception as e:
            logger.error(f"NewsData.io error: {e}")
    
    # Remove duplicates based on title
    seen_titles = set()
    unique_trending = []
    for story in trending_list:
        title_lower = story["title"].lower()
        if title_lower not in seen_titles:
            seen_titles.add(title_lower)
            unique_trending.append(story)
    
    # Limit to 8 stories
    unique_trending = unique_trending[:8]
    
    # Prepare cache data
    cache_data = {
        "trending_stories": unique_trending,
        "last_updated": datetime.utcnow().isoformat()
    }
    
    # Cache in Redis for 10 minutes (600 seconds)
    if redis_client and redis_available:
        try:
            redis_client.setex(
                "trending_stories_cache",
                600,
                json.dumps(cache_data)
            )
            logger.info(f"Trending cached with {len(unique_trending)} stories")
        except Exception as e:
            logger.error(f"Redis cache write error: {e}")
    
    logger.info(f"Trending updated with {len(unique_trending)} stories")
    return cache_data


def get_trending_stories():
    """
    Get trending stories - returns cached data if available,
    otherwise fetches fresh data.
    """
    # Try to get from cache first
    if redis_client and redis_available:
        try:
            cached = redis_client.get("trending_stories_cache")
            if cached:
                return json.loads(cached)
        except Exception as e:
            logger.error(f"Cache read error: {e}")
    
    # If no cache, fetch fresh data
    return update_trending_stories()


# Celery task wrapper (if using Celery)
@shared_task(bind=True, name='services.tasks.update_trending.update_trending_stories')
def run_update_trending():
    """Entry point for Celery task."""
    return update_trending_stories()
