"""
Seed several days of editor-selected daily stories for development and testing.
"""

import logging
from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.utils import timezone

from content.models import Category, Story, StoryEvent, DailyStoryEdition, DailyStoryEditionStatus, DailyStorySelectionType

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Seed several days of editor-selected daily stories.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=5,
            help='Number of days to seed (default: 5).',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Remove existing seeded editions before creating new ones.',
        )

    def handle(self, *args, **options):
        days = options['days']
        clear = options['clear']

        if clear:
            deleted, _ = DailyStoryEdition.objects.filter(
                selection_type=DailyStorySelectionType.EDITORIAL,
            ).delete()
            self.stdout.write(self.style.WARNING(f'Cleared {deleted} existing editorial editions.'))

        category, _ = Category.objects.get_or_create(
            name='Global News',
            defaults={'slug': 'global-news', 'description': 'Curated global events.'},
        )

        stories_data = [
            {
                'title': 'Global Climate Summit Reaches Historic Agreement',
                'summary': 'World leaders agreed on a new framework for emissions reductions at the latest climate summit.',
                'current_status': 'Agreement signed; implementation discussions ongoing.',
                'events': [
                    {'position': 1, 'title': 'Summit opens in Nairobi', 'summary': 'Delegates from 190 countries gather to negotiate a new emissions framework.', 'source_name': 'Reuters', 'source_url': 'https://reuters.com/climate-summit-opens', 'hours_ago': 48},
                    {'position': 2, 'title': 'Draft text published', 'summary': 'A 12-page draft agreement is released for member-state review.', 'source_name': 'BBC', 'source_url': 'https://bbc.com/draft-text-published', 'hours_ago': 36},
                    {'position': 3, 'title': 'Historic agreement reached', 'summary': 'After 48 hours of negotiations, countries agree on binding emissions targets.', 'source_name': 'Al Jazeera', 'source_url': 'https://aljazeera.com/agreement-reached', 'hours_ago': 24},
                ],
            },
            {
                'title': 'Tech Giants Face New Regulatory Framework in the EU',
                'summary': 'The European Union unveiled a sweeping regulatory package targeting major technology platforms.',
                'current_status': 'Legislation proposed; industry lobbying intensifies.',
                'events': [
                    {'position': 1, 'title': 'EU proposes Digital Markets Act', 'summary': 'The European Commission releases the full text of the proposed regulation.', 'source_name': 'TechCrunch', 'source_url': 'https://techcrunch.com/eu-dma-proposal', 'hours_ago': 72},
                    {'position': 2, 'title': 'Major platforms respond', 'summary': 'Leading tech companies issue statements opposing specific provisions.', 'source_name': 'The Verge', 'source_url': 'https://theverge.com/platforms-respond', 'hours_ago': 60},
                ],
            },
            {
                'title': 'African Union Launches Continental Free Trade Area',
                'summary': 'The African Union officially launched the AfCFTA, creating the world\'s largest free trade zone.',
                'current_status': 'Launch successful; tariff reductions begin next quarter.',
                'events': [
                    {'position': 1, 'title': 'AfCFTA agreement signed', 'summary': '44 African nations sign the agreement to create a single continental market.', 'source_name': 'Bloomberg', 'source_url': 'https://bloomberg.com/afcfta-signed', 'hours_ago': 96},
                    {'position': 2, 'title': 'First cross-border shipment', 'summary': 'The first cargo shipment under AfCFTA rules crosses from Ghana to Ivory Coast.', 'source_name': 'CNBC', 'source_url': 'https://cnbc.com/first-shipment', 'hours_ago': 48},
                ],
            },
            {
                'title': 'Breakthrough in Malaria Vaccine Development',
                'summary': 'Researchers announced a new malaria vaccine candidate with 80% efficacy in late-stage trials.',
                'current_status': 'Awaiting WHO prequalification and regulatory approval.',
                'events': [
                    {'position': 1, 'title': 'Trial results published', 'summary': 'Phase 3 trial data published in The Lancet showing strong efficacy.', 'source_name': 'BBC', 'source_url': 'https://bbc.com/malaria-trial', 'hours_ago': 120},
                    {'position': 2, 'title': 'WHO responds positively', 'summary': 'WHO calls the results a potential turning point in malaria prevention.', 'source_name': 'Reuters', 'source_url': 'https://reuters.com/who-response', 'hours_ago': 96},
                ],
            },
            {
                'title': 'Global Semiconductor Supply Chain Restructures',
                'summary': 'Major chipmakers announce new fabrication plants across Asia and North America.',
                'current_status': 'Construction timelines announced; workforce hiring begins.',
                'events': [
                    {'position': 1, 'title': 'TSMC expands Arizona plant', 'summary': 'TSMC confirms a second fabrication facility in Phoenix.', 'source_name': 'Ars Technica', 'source_url': 'https://arstechnica.com/tsmc-arizona', 'hours_ago': 84},
                    {'position': 2, 'title': 'Samsung invests in new fab', 'summary': 'Samsung announces a $170 billion investment in semiconductor manufacturing.', 'source_name': 'WIRED', 'source_url': 'https://wired.com/samsung-investment', 'hours_ago': 60},
                ],
            },
        ]

        created_count = 0
        for i in range(days):
            story_data = stories_data[i % len(stories_data)]
            edition_date = date.today() - timedelta(days=i)

            story, _ = Story.objects.get_or_create(
                slug=slugify(story_data['title'])[:350],
                defaults={
                    'title': story_data['title'],
                    'summary': story_data['summary'],
                    'current_status': story_data['current_status'],
                    'status': 'published',
                    'started_at': timezone.now() - timedelta(days=i + 2),
                    'category': category,
                },
            )

            for event_data in story_data['events']:
                occurred_at = timezone.now() - timedelta(hours=event_data.pop('hours_ago'))
                StoryEvent.objects.get_or_create(
                    story=story,
                    position=event_data['position'],
                    defaults={
                        'title': event_data['title'],
                        'summary': event_data['summary'],
                        'source_name': event_data['source_name'],
                        'source_url': event_data['source_url'],
                        'occurred_at': occurred_at,
                        'is_verified': True,
                    },
                )

            edition, created = DailyStoryEdition.objects.get_or_create(
                edition_date=edition_date,
                defaults={
                    'story': story,
                    'status': DailyStoryEditionStatus.PUBLISHED,
                    'selection_type': DailyStorySelectionType.EDITORIAL,
                    'selection_reason': 'Editor-selected for the daily global story.',
                },
            )
            if created:
                created_count += 1

        self.stdout.write(self.style.SUCCESS(f'Seeded {created_count} daily story editions across {days} days.'))
