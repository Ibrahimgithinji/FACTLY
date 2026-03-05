# Real-Time World Information Update Guide

## Overview

FACTLY is fully configured to automatically stay updated with current world information through a distributed real-time architecture. The system continuously monitors multiple news sources, trends, and global events.

## Real-Time Data Architecture

### 1. **Real-Time News Service**
Integrates with multiple news sources:
- **RSS Feeds**: BBC, CNN, Reuters, AP, NYT, Guardian, Al Jazeera
- **NewsAPI**: Real-time news aggregation
- **Google News API**: Global news monitoring  
- **Twitter/X API**: Breaking news detection
- **Regional News Services**: Localized content from each region

### 2. **Automatic Refresh Schedule**

The system runs scheduled Celery tasks to keep data fresh:

| Task | Frequency | Purpose |
|------|-----------|---------|
| **Monitor Global News** | Every 5 minutes | Fetch breaking news from all sources |
| **Process Claim Queue** | Every minute | Process queued claims for verification |
| **Update Trending Topics** | Every 10 minutes | Extract trending topics from news |
| **Cleanup Cache** | Every hour | Remove expired cached data |
| **Generate Daily Reports** | Once daily | Analytics and summary reports |
| **Sync Regional Nodes** | Every 30 minutes | Sync data across regional servers |

### 3. **Cache Strategy**

Smart caching ensures fresh data while optimizing performance:

```
Real-Time Data:        5 minutes  (breaking news, live events)
News Articles:        10 minutes  (general news)
Fact Checks:          30 minutes  (fact check database)
Official Sources:      1 hour     (government, institutional data)
Academic Sources:     24 hours    (research, historical data)
```

### 4. **Frontend Auto-Refresh**

The trending topics component automatically updates:
- **Initial Load**: Fetches current trending topics on page load
- **Auto-Refresh**: Updates every 5 minutes
- **Manual Refresh**: Users can click refresh button for immediate update
- **Backend Trigger**: When user clicks refresh, triggers all backend tasks

## How to Ensure Current Information

### ✅ Built-In Features (Already Active)

1. **Real-Time News Integration**
   - RSS feeds from 7 major news organizations
   - Real-time API integrations
   - Automatic source credibility evaluation

2. **Intelligent Caching**
   - Very short TTLs for real-time data
   - Automatic cache expiration
   - Force-refresh capability

3. **Scheduled Background Jobs**
   - Runs 24/7 with Celery workers
   - Automatic retry on failure
   - Detailed logging for monitoring

4. **Trending Topics & Global Events**
   - Automatic extraction from news sources
   - Regional news digests
   - Freshness scoring on all content

5. **Multi-Source Verification**
   - Checks trending topics against fact-check databases
   - Compares across multiple news sources
   - Identifies contradictions and consensus

### 🚀 Setup Instructions

#### Step 1: Configure Environment Variables

```bash
# .env file in backend/
GOOGLE_FACT_CHECK_API_KEY=your_key_here
NEWSAPI_KEY=your_key_here
TWITTER_BEARER_TOKEN=your_token_here  # Optional
GOOGLE_NEWS_API_KEY=your_key_here
```

#### Step 2: Install Redis (Cache & Message Broker)

```bash
# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis-server

# macOS
brew install redis
brew services start redis

# Or use Docker
docker run -d -p 6379:6379 redis:latest
```

#### Step 3: Run Celery Worker

```bash
cd backend
celery -A factly_backend worker --loglevel=info
```

#### Step 4: Run Celery Beat Scheduler

```bash
cd backend
celery -A factly_backend beat --loglevel=info
```

#### Step 5: Start Django Development Server

```bash
cd backend
python manage.py runserver
```

#### Step 6: Start Frontend

```bash
cd frontend
npm start
```

### 🔍 Monitoring Real-Time Updates

#### Check Current Trending Topics
```bash
# Via API
curl http://localhost:8000/api/verification/trending/

# Response includes:
# - trending_topics: List with mention counts and trending scores
# - global_events: Regional event digests
# - last_updated: Timestamp of last refresh
# - cache_stats: Current cache statistics
```

#### Trigger Manual Refresh
```bash
curl -X POST http://localhost:8000/api/verification/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"task": "all", "force": true}'
```

#### Monitor Celery Tasks
```bash
# In a new terminal
celery -A factly_backend inspect active

# Check scheduled tasks
celery -A factly_backend inspect scheduled

# Check registered tasks
celery -A factly_backend inspect registered
```

### 📊 Key Real-Time Features by Component

#### Backend - Real-Time News Service
**File**: `backend/services/fact_checking_service/real_time_news_service.py`

- Fetches from multiple news APIs simultaneously
- Calculates freshness scores
- Filters by age, relevance, and credibility
- Supports geographic region filtering

#### Backend - Refresh Tasks
**File**: `backend/services/tasks/refresh_tasks.py`

- `refresh_realtime_data()`: Clears real-time caches, pre-fetches trending
- `update_trending_topics()`: Extracts keywords from breaking/world news
- `update_global_events()`: Creates regional event digests
- `cleanup_cache()`: Removes expired entries

#### Backend - Cache Manager
**File**: `backend/services/fact_checking_service/cache_manager.py`

- Type-specific TTL configurations
- Automatic expiration
- Force-refresh capability
- Cache statistics tracking

#### Frontend - Trending Topics Component
**File**: `frontend/src/components/TrendingTopics.js`

- Auto-refresh every 5 minutes
- Manual refresh button
- Global events digest view
- Freshness indicators
- Last updated timestamp

#### Celery Configuration
**Files**: 
- `backend/factly_backend/celery_app.py`
- `backend/factly_backend/celery.py`

- Beat schedule with 6 periodic tasks
- Queue-based routing for different task types
- Worker concurrency settings
- Error handling and retries

## Data Freshness Indicators

The API provides real-time freshness information:

```json
{
  "data_freshness": {
    "verification_timestamp": "2026-03-05T10:30:45",
    "most_recent_evidence_age_hours": 0.5,
    "realtime_sources_used": true,
    "cache_status": "fresh",
    "data_age_warning": "Data is very recent (less than 1 hour old)"
  }
}
```

## Troubleshooting

### Trending Topics Not Updating

1. **Check Redis Connection**
   ```bash
   redis-cli ping
   # Should return PONG
   ```

2. **Verify Celery Beat is Running**
   ```bash
   ps aux | grep "celery beat"
   ```

3. **Check Celery Worker is Active**
   ```bash
   celery -A factly_backend inspect active
   ```

4. **View Task Logs**
   ```bash
   celery -A factly_backend events  # Real-time task monitoring
   ```

5. **Force Manual Refresh**
   ```bash
   curl -X POST http://localhost:8000/api/verification/refresh/ \
     -H "Content-Type: application/json" \
     -d '{"task": "all", "force": true}'
   ```

### Old Data Appearing

1. **Clear Cache Manually**
   ```python
   from services.fact_checking_service.cache_manager import CacheManager
   cache = CacheManager()
   cache.clear()  # Clear all caches
   ```

2. **Reduce TTL for Testing**
   - Modify `DEFAULT_TTLS` in `cache_manager.py`
   - Set shorter intervals for testing

3. **Check API Keys**
   - Verify all external API keys are valid
   - Check usage limits haven't been exceeded

## Performance Tips

1. **Use Production Deployment**
   - Gunicorn for Django
   - Nginx as reverse proxy
   - Multiple Celery workers with concurrency

2. **Database Optimization**
   - Use PostgreSQL with proper indexing
   - Enable connection pooling (pgBouncer)
   - Archive old verification results

3. **Cache Optimization**
   - Use Redis Cluster for high availability
   - Enable memory optimization in Redis
   - Monitor cache hit rates

4. **Celery Optimization**
   - Adjust worker concurrency based on CPU cores
   - Set appropriate task time limits
   - Use task routing for different priority levels

## API Endpoints for Real-Time Data

### Get Trending Topics
```
GET /api/verification/trending/
```

Returns trending topics, global events, cache stats, and last update time.

### Get Global Events
```
GET /api/verification/global-events/
```

Returns regional event digests.

### Trigger Data Refresh
```
POST /api/verification/refresh/
Body: {
  "task": "all|trending|global_events|realtime",
  "force": true/false
}
```

### Verify Content (with data freshness)
```
POST /api/verification/verify/enhanced/
Body: {
  "text": "content to verify",
  "language": "en"
}
```

Response includes `data_freshness` object with age information.

## Summary

Your FACTLY installation is **production-ready for real-time updates**:

✅ Multiple real-time news sources integrated
✅ Automatic refresh every 5-10 minutes
✅ Smart caching with appropriate TTLs
✅ Scheduled background tasks (24/7)
✅ Manual refresh capability
✅ Data freshness indicators
✅ Regional monitoring
✅ Multi-source verification

The website automatically stays current with world information without any manual intervention!
