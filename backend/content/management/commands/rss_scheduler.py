import logging
from datetime import datetime, timezone
from django.core.management.base import BaseCommand
from django.utils import timezone as dj_timezone
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from content.models import FeedSource
from content.management.commands.import_rss import import_feed

logger = logging.getLogger(__name__)


def check_and_import():
    now = dj_timezone.now()
    sources = FeedSource.objects.filter(is_active=True)
    for source in sources:
        if source.last_imported_at:
            elapsed = (now - source.last_imported_at).total_seconds() / 60
        else:
            elapsed = float('inf')

        if elapsed >= source.import_interval:
            logger.info(f'Scheduler triggered import: {source.name}')
            try:
                count = import_feed(source)
                logger.info(f'  Imported {count} new articles from {source.name}')
            except Exception as e:
                logger.error(f'  Failed to import {source.name}: {e}')


class Command(BaseCommand):
    help = 'Background RSS scheduler that imports articles periodically'

    def add_arguments(self, parser):
        parser.add_argument(
            '--interval',
            type=int,
            default=15,
            help='Check interval in minutes (default: 15)',
        )

    def handle(self, *args, **options):
        interval = options['interval']
        self.stdout.write(f'Starting RSS scheduler (check every {interval} minutes)...')

        scheduler = BackgroundScheduler()

        scheduler.add_job(
            check_and_import,
            trigger=IntervalTrigger(minutes=interval),
            id='rss_import',
            name='Check and import RSS feeds',
            replace_existing=True,
        )

        scheduler.start()
        self.stdout.write(self.style.SUCCESS('RSS scheduler is running. Press Ctrl+C to stop.'))

        try:
            import time
            while True:
                time.sleep(60)
        except KeyboardInterrupt:
            self.stdout.write('\nStopping scheduler...')
            scheduler.shutdown()
            self.stdout.write(self.style.SUCCESS('Scheduler stopped.'))
