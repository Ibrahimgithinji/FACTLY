"""
Celery tasks for Daily Story edition management.
"""

import logging

try:
    from celery import shared_task
    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False
    shared_task = lambda *args, **kwargs: lambda func: func

from services.daily_story_service import (
    ensure_tomorrow_draft,
    publish_todays_edition,
    rollover_to_fallback,
)
from content.models import DailyStoryEdition, DailyStoryEditionStatus

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def prepare_tomorrow_daily_story(self):
    """Ensure a draft edition exists for tomorrow."""
    try:
        edition = ensure_tomorrow_draft()
        return {
            'status': 'success',
            'edition_date': edition.edition_date.isoformat(),
            'edition_status': edition.status,
        }
    except Exception as exc:
        logger.error('Failed to prepare tomorrow daily story: %s', exc)
        try:
            self.retry(exc=exc)
        except Exception:
            return {'status': 'failed', 'error': str(exc)}


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def publish_today_daily_story(self):
    """Publish today's scheduled edition if ready."""
    try:
        edition = publish_todays_edition()
        if edition is None:
            return {'status': 'no_action', 'detail': 'No scheduled edition to publish.'}
        return {
            'status': 'success',
            'edition_date': edition.edition_date.isoformat(),
            'edition_status': edition.status,
            'story_title': edition.story.title if edition.story else None,
        }
    except Exception as exc:
        logger.error('Failed to publish today daily story: %s', exc)
        try:
            self.retry(exc=exc)
        except Exception:
            return {'status': 'failed', 'error': str(exc)}


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def ensure_daily_story_fallback(self):
    """Ensure today's edition is marked as fallback if no story is available."""
    try:
        from services.daily_story_service import get_editorial_date
        today, _ = get_editorial_date()
        edition = DailyStoryEdition.objects.filter(edition_date=today).first()
        if not edition:
            from content.models import DailyStoryEditionStatus
            edition = rollover_to_fallback(today)
        if edition.status not in (DailyStoryEditionStatus.PUBLISHED, DailyStoryEditionStatus.FALLBACK):
            edition.status = DailyStoryEditionStatus.FALLBACK
            edition.selection_reason = edition.selection_reason or 'No curated story available for this date.'
            edition.save()
        return {
            'status': 'success',
            'edition_date': today.isoformat(),
            'edition_status': edition.status,
        }
    except Exception as exc:
        logger.error('Failed to ensure daily story fallback: %s', exc)
        try:
            self.retry(exc=exc)
        except Exception:
            return {'status': 'failed', 'error': str(exc)}
