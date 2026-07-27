import logging
from datetime import date, timedelta

from django.utils import timezone
from django.conf import settings
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from content.models import Story, StoryEvent, DailyStoryEdition, DailyStoryEditionStatus, DailyStorySelectionType, StoryStatus

logger = logging.getLogger(__name__)


def get_editorial_date():
    """Return the current date in the configured editorial timezone."""
    timezone_name = getattr(settings, 'DAILY_STORY_TIME_ZONE', 'Africa/Nairobi')
    try:
        editorial_timezone = ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError:
        logger.warning('Invalid DAILY_STORY_TIME_ZONE %s; falling back to UTC', timezone_name)
        editorial_timezone = ZoneInfo('UTC')
    return timezone.now().astimezone(editorial_timezone).date(), timezone_name


def get_or_create_draft_for_date(target_date, story=None):
    """Get or create a draft edition for the given editorial date."""
    edition, created = DailyStoryEdition.objects.get_or_create(
        edition_date=target_date,
        defaults={
            'story': story,
            'status': DailyStoryEditionStatus.DRAFT,
            'selection_type': DailyStorySelectionType.EDITORIAL,
        },
    )
    return edition, created


def publish_edition(edition):
    """Publish a scheduled or draft edition."""
    if edition.status == DailyStoryEditionStatus.PUBLISHED:
        return edition
    if edition.status == DailyStoryEditionStatus.FALLBACK:
        raise ValueError('Cannot publish a fallback edition.')
    edition.status = DailyStoryEditionStatus.PUBLISHED
    edition.save()
    return edition


def rollover_to_fallback(edition_date):
    """Mark an edition as fallback when no story is assigned."""
    edition, _ = DailyStoryEdition.objects.get_or_create(
        edition_date=edition_date,
        defaults={
            'status': DailyStoryEditionStatus.FALLBACK,
            'selection_type': DailyStorySelectionType.EDITORIAL,
            'selection_reason': 'No curated story available for this date.',
        },
    )
    if edition.status != DailyStoryEditionStatus.FALLBACK:
        edition.status = DailyStoryEditionStatus.FALLBACK
        edition.selection_reason = edition.selection_reason or 'No curated story available for this date.'
        edition.save()
    return edition


def ensure_tomorrow_draft():
    """Prepare a draft edition for tomorrow if one does not already exist."""
    tomorrow, _ = get_editorial_date()
    tomorrow += timedelta(days=1)
    edition, created = get_or_create_draft_for_date(tomorrow)
    if created:
        logger.info('Created draft DailyStoryEdition for %s', tomorrow)
    else:
        logger.debug('Draft already exists for %s (status=%s)', tomorrow, edition.status)
    return edition


def publish_todays_edition():
    """Publish today's scheduled edition if one exists and is ready."""
    today, timezone_name = get_editorial_date()
    try:
        edition = DailyStoryEdition.objects.get(
            edition_date=today,
            status=DailyStoryEditionStatus.SCHEDULED,
        )
    except DailyStoryEdition.DoesNotExist:
        logger.info('No scheduled edition to publish for %s (%s)', today, timezone_name)
        return None

    if not edition.story or edition.story.status != StoryStatus.PUBLISHED:
        logger.warning('Scheduled edition for %s has no published story; cannot publish.', today)
        return edition

    publish_edition(edition)
    logger.info('Published DailyStoryEdition for %s: %s', today, edition.story.title)
    return edition
