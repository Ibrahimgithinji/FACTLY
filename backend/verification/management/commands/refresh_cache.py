"""
Management command to refresh cached data and ensure Factly stays up-to-date.
"""

import logging
from django.core.management.base import BaseCommand
from services.fact_checking_service.cache_manager import CacheManager
from services.fact_checking_service.real_time_news_service import RealTimeNewsService

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Refresh cached data to ensure Factly stays up-to-date with current information'

    def add_arguments(self, parser):
        parser.add_argument(
            '--data-type',
            type=str,
            choices=['news', 'realtime', 'fact_check', 'all'],
            default='all',
            help='Type of data to refresh (default: all)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force refresh all cached data regardless of age'
        )

    def handle(self, *args, **options):
        self.stdout.write('Starting cache refresh for Factly...')

        cache_manager = CacheManager()
        realtime_news = RealTimeNewsService(cache_manager=cache_manager)

        data_type = options['data_type']
        force_refresh = options['force']

        try:
            if data_type in ['news', 'all']:
                self.stdout.write('Refreshing news data cache...')
                # Clear news-related caches
                cache_manager.clear(data_type='news')
                self.stdout.write(self.style.SUCCESS('News cache cleared'))

            if data_type in ['realtime', 'all']:
                self.stdout.write('Refreshing real-time data cache...')
                # Clear real-time caches
                cache_manager.clear(data_type='realtime')
                # Test real-time news service
                test_news = realtime_news.get_real_time_news("test query", max_results=1)
                self.stdout.write(self.style.SUCCESS(f'Real-time service tested: {len(test_news)} items'))

            if data_type in ['fact_check', 'all']:
                self.stdout.write('Refreshing fact-check data cache...')
                # Clear fact-check caches
                cache_manager.clear(data_type='fact_check')
                self.stdout.write(self.style.SUCCESS('Fact-check cache cleared'))

            if data_type == 'all':
                self.stdout.write('Refreshing all caches...')
                cache_manager.clear()  # Clear all caches
                self.stdout.write(self.style.SUCCESS('All caches cleared'))

            # Get cache stats
            stats = cache_manager.get_stats()
            self.stdout.write('Cache refresh complete. Current stats:')
            for data_type_name, stat in stats.items():
                self.stdout.write(f'  {data_type_name}: {stat["size"]} items cached')

            self.stdout.write(self.style.SUCCESS('Cache refresh completed successfully!'))

        except Exception as e:
            logger.error(f"Cache refresh failed: {e}")
            self.stdout.write(self.style.ERROR(f'Cache refresh failed: {str(e)}'))
            return 1

        return 0