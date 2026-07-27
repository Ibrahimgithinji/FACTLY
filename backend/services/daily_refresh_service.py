"""
Shared service for daily content refresh operations.

Extracted from the management command so both the command and Celery tasks
can call the same logic without duplicating the lock-file and sys.exit()
behaviour that belongs only to the CLI entrypoint.
"""

import logging
from datetime import timedelta

from django.utils import timezone

from content.models import FeedSource, Article
from content.management.commands.import_rss import import_feed

logger = logging.getLogger(__name__)

CUTOFF_HOURS = 24
TRENDING_LIMIT = 10


def run_daily_refresh(dry_run=False):
    """Run the full daily refresh pipeline and return a stats dict."""
    active = FeedSource.objects.filter(is_active=True)
    if not active.exists():
        return {'sources_processed': 0, 'imported': 0, 'rotated': 0, 'promoted': 0, 'errors': []}

    cutoff = timezone.now() - timedelta(hours=CUTOFF_HOURS)
    total_imported = 0
    source_log = []
    stale_count = 0
    fresh_count = 0

    for source in active:
        try:
            if dry_run:
                count = 0
            else:
                count = import_feed(source)
            total_imported += count
            source_log.append({'source': source.name, 'imported': count})
        except Exception as exc:
            logger.exception('Import failed for %s', source.name)
            source_log.append({'source': source.name, 'error': str(exc)})

    stale = Article.objects.filter(
        is_imported=True,
        deleted_at__isnull=True,
        published_at__lt=cutoff,
    )
    stale_count = stale.count()

    if not dry_run and total_imported > 0 and stale_count:
        for article in stale.iterator(chunk_size=200):
            article.soft_delete()

    fresh = Article.objects.filter(
        is_imported=True,
        deleted_at__isnull=True,
        published_at__gte=cutoff,
    )
    fresh_count = fresh.count()

    if not dry_run and fresh_count:
        Article.objects.filter(is_imported=True).update(is_trending=False)
        trending = fresh.order_by('-published_at')[:TRENDING_LIMIT]
        for article in trending:
            article.is_trending = True
            article.save(update_fields=['is_trending'])

    errors = [item for item in source_log if 'error' in item]
    return {
        'sources_processed': len(source_log),
        'imported': total_imported,
        'rotated': stale_count,
        'promoted': min(fresh_count, TRENDING_LIMIT) if fresh_count else 0,
        'errors': errors,
    }
