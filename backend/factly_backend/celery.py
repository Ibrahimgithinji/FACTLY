"""
Celery Configuration for FACTLY

Configures Celery for distributed task processing and scheduled tasks
to keep FACTLY updated with global events.
"""

import os
from celery import Celery
from celery.signals import setup_logging

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'factly_backend.settings')

# Create Celery app
app = Celery('factly')

# Load configuration from Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from all installed apps
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    """Debug task to verify Celery is working."""
    print(f'Request: {self.request!r}')


# =============================================================================
# Scheduled Tasks (Celery Beat)
# =============================================================================

app.conf.beat_schedule = {
    # Refresh real-time news cache every 5 minutes
    'refresh-realtime-news': {
        'task': 'factly_backend.services.tasks.refresh_realtime_data',
        'schedule': 300.0,  # 5 minutes
        'options': {'queue': 'high_priority'}
    },
    # Refresh trending topics every 15 minutes
    'update-trending-topics': {
        'task': 'factly_backend.services.tasks.update_trending_topics',
        'schedule': 900.0,  # 15 minutes
        'options': {'queue': 'ingestion'}
    },
    # Update trending stories every 10 minutes (NewsAPI + NewsData.io)
    'update-trending-stories': {
        'task': 'factly_backend.services.tasks.update_trending.update_trending_stories',
        'schedule': 600.0,  # 10 minutes
        'options': {'queue': 'ingestion'}
    },
    # Clear old cache entries every hour
    'cleanup-old-cache': {
        'task': 'factly_backend.services.tasks.cleanup_cache',
        'schedule': 3600.0,  # 1 hour
        'options': {'queue': 'low_priority'}
    },
    # Update global events digest every 30 minutes
    'update-global-events': {
        'task': 'factly_backend.services.tasks.update_global_events',
        'schedule': 1800.0,  # 30 minutes
        'options': {'queue': 'ingestion'}
    },
    # Refresh fact-check database daily
    'daily-fact-check-refresh': {
        'task': 'factly_backend.services.tasks.refresh_fact_check_cache',
        'schedule': 86400.0,  # 24 hours
        'options': {'queue': 'low_priority'}
    },
}

# Enable UTC time for scheduling
app.conf.timezone = 'UTC'
app.conf.enable_utc = True
