from datetime import timedelta
from zoneinfo import ZoneInfo

from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from content.models import Article, DailyStoryEdition, DailyStoryEditionStatus, DailyStorySelectionType, Story, StoryEvent, StoryStatus


@override_settings(DAILY_STORY_TIME_ZONE='Africa/Nairobi')
class DailyStoryApiTests(TestCase):
    def setUp(self):
        self.today = timezone.now().astimezone(ZoneInfo('Africa/Nairobi')).date()
        self.story = Story.objects.create(
            title='The development of a verified event',
            summary='A source-backed timeline for readers who want the full context.',
            current_status='The event remains under active monitoring.',
            status='published',
            started_at=timezone.now() - timedelta(days=2),
        )
        StoryEvent.objects.create(
            story=self.story,
            position=2,
            occurred_at=timezone.now() - timedelta(days=1),
            title='Second development',
            summary='The next documented development in the event.',
            source_name='Example News',
            source_url='https://example.com/second',
            is_verified=True,
        )
        StoryEvent.objects.create(
            story=self.story,
            position=1,
            occurred_at=timezone.now() - timedelta(days=2),
            title='The story begins',
            summary='The earliest documented development in the event.',
            source_name='Example News',
            source_url='https://example.com/first',
            is_verified=True,
        )
        DailyStoryEdition.objects.create(
            edition_date=self.today,
            story=self.story,
            status='scheduled',
            selection_reason='Editor-selected for the daily global story.',
        )

    def test_daily_story_returns_scheduled_published_story_in_timeline_order(self):
        response = self.client.get(reverse('daily-story'))

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload['story']['slug'], self.story.slug)
        self.assertEqual(
            [event['position'] for event in payload['story']['events']],
            [1, 2],
        )
        self.assertEqual(payload['edition_timezone'], 'Africa/Nairobi')

    def test_daily_story_does_not_expose_future_edition(self):
        DailyStoryEdition.objects.filter(edition_date=self.today).delete()
        DailyStoryEdition.objects.create(
            edition_date=self.today + timedelta(days=1),
            story=self.story,
            status='scheduled',
        )

        response = self.client.get(reverse('daily-story'))

        self.assertEqual(response.status_code, 404)
        self.assertIn('fallback', response.json())

    def test_daily_story_returns_published_edition(self):
        DailyStoryEdition.objects.filter(edition_date=self.today).update(
            status=DailyStoryEditionStatus.PUBLISHED,
        )

        response = self.client.get(reverse('daily-story'))

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload['status'], 'published')

    def test_daily_story_returns_404_when_no_edition_exists(self):
        DailyStoryEdition.objects.filter(edition_date=self.today).delete()

        response = self.client.get(reverse('daily-story'))

        self.assertEqual(response.status_code, 404)
        payload = response.json()
        self.assertIn('detail', payload)
        self.assertIn('fallback', payload)
        self.assertTrue(payload.get('fallback'))

    def test_story_keeps_source_snapshot_when_linked_article_is_soft_deleted(self):
        article = Article.objects.create(
            title='Imported source item',
            content='A sufficiently detailed imported item used only as a reference.',
            status='published',
            is_imported=True,
            source_name='Example News',
            source_url='https://example.com/imported',
        )
        StoryEvent.objects.create(
            story=self.story,
            position=3,
            occurred_at=timezone.now(),
            title='Source remains attributable',
            summary='The timeline must retain its own source details after article rotation.',
            source_name=article.source_name,
            source_url=article.source_url,
            source_article=article,
        )
        article.soft_delete()

        response = self.client.get(reverse('story-detail', kwargs={'slug': self.story.slug}))

        self.assertEqual(response.status_code, 200)
        event = response.json()['events'][2]
        self.assertEqual(event['source_name'], 'Example News')
        self.assertEqual(event['source_url'], 'https://example.com/imported')

    def test_unique_daily_edition_constraint_prevents_duplicate_dates(self):
        DailyStoryEdition.objects.create(
            edition_date=self.today + timedelta(days=2),
            story=self.story,
            status='scheduled',
        )
        duplicate = DailyStoryEdition(
            edition_date=self.today + timedelta(days=2),
            story=self.story,
            status='scheduled',
        )
        with self.assertRaises(Exception):
            duplicate.save()

    def test_published_edition_is_immutable(self):
        edition = DailyStoryEdition.objects.get(edition_date=self.today)
        edition.status = DailyStoryEditionStatus.PUBLISHED
        edition.save()

        with self.assertRaises(ValueError):
            edition.selection_reason = 'Changed after publish'
            edition.save()

    def test_story_detail_returns_published_story_only(self):
        draft_story = Story.objects.create(
            title='Draft story',
            summary='Not yet published.',
            status='draft',
        )
        response = self.client.get(reverse('story-detail', kwargs={'slug': draft_story.slug}))
        self.assertEqual(response.status_code, 404)

        response = self.client.get(reverse('story-detail', kwargs={'slug': self.story.slug}))
        self.assertEqual(response.status_code, 200)

    def test_daily_story_excludes_draft_editions(self):
        DailyStoryEdition.objects.filter(edition_date=self.today).update(status='draft')

        response = self.client.get(reverse('daily-story'))
        self.assertEqual(response.status_code, 404)
