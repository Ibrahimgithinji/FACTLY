import logging
import re
import feedparser
from datetime import datetime, timezone
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.utils import timezone as dj_timezone
from content.models import FeedSource, Article, Tag

logger = logging.getLogger(__name__)

PUBLISHER_TAGS = {
    'techcrunch.com': 'TechCrunch',
    'theverge.com': 'The Verge',
    'wired.com': 'WIRED',
    'arstechnica.com': 'Ars Technica',
    'techpoint.africa': 'Techpoint Africa',
    'techcabal.com': 'TechCabal',
    'cnbc.com': 'CNBC',
    'reuters.com': 'Reuters',
    'bbc.com': 'BBC',
    'bbc.co.uk': 'BBC',
}

MAX_CONTENT_LENGTH = 50000
MAX_EXCERPT_LENGTH = 300


def clean_html(html):
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r'<iframe[^>]*>.*?</iframe>', '', html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r'<svg[^>]*>.*?</svg>', '', html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r' on\w+="[^"]*"', '', html, flags=re.IGNORECASE)
    html = re.sub(r' class="[^"]*"', '', html)
    html = re.sub(r' style="[^"]*"', '', html)
    html = re.sub(r'<a[^>]*>', '<p>', html)
    html = re.sub(r'</a>', '</p>', html)
    return html.strip()


def strip_html(text):
    return re.sub(r'<[^>]+>', '', text).strip()


def get_source_name(url):
    for domain, name in PUBLISHER_TAGS.items():
        if domain in url:
            return name
    return ''


def import_feed(source):
    logger.info(f'Fetching feed: {source.feed_url}')
    feed = feedparser.parse(source.feed_url)

    if feed.bozo and not feed.entries:
        logger.error(f'Failed to parse feed: {source.feed_url} — {feed.bozo_exception}')
        return 0

    new_count = 0
    for entry in feed.entries:
        article_url = entry.get('link', '')
        if not article_url:
            continue

        if Article.objects.filter(source_url=article_url).exists():
            continue

        title = entry.get('title', '').strip()
        if not title:
            continue

        content = ''
        if hasattr(entry, 'content') and entry.content:
            content = entry.content[0].get('value', '')
        elif hasattr(entry, 'description') and entry.description:
            content = entry.description

        if not content:
            continue

        content = clean_html(content)[:MAX_CONTENT_LENGTH]
        text_content = strip_html(content)
        if len(text_content) < 50:
            continue

        excerpt = ''
        summary = entry.get('summary', '')
        if summary:
            excerpt = strip_html(summary)[:MAX_EXCERPT_LENGTH]
        if not excerpt:
            excerpt = text_content[:MAX_EXCERPT_LENGTH]

        published = None
        if entry.get('published_parsed'):
            published = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
        elif entry.get('updated_parsed'):
            published = datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)

        source_name = get_source_name(article_url)

        image_url = ''
        if hasattr(entry, 'media_content') and entry.media_content:
            for media in entry.media_content:
                if media.get('medium') == 'image' or 'image' in media.get('type', ''):
                    image_url = media.get('url', '')
                    break
        if not image_url and hasattr(entry, 'links'):
            for link in entry.links:
                if link.get('rel') == 'enclosure' and 'image' in link.get('type', ''):
                    image_url = link.get('href', '')
                    break

        read_time = max(1, len(text_content) // 2000 + 1)

        article = Article(
            title=title,
            slug=slugify(title)[:350] or 'article',
            excerpt=excerpt,
            content=content,
            featured_image=image_url,
            source_url=article_url,
            source_name=source_name,
            is_imported=True,
            category=source.category,
            status='draft',
            published_at=published or dj_timezone.now(),
            read_time=read_time,
        )
        article.save()

        if source_name:
            tag, _ = Tag.objects.get_or_create(name=source_name)
            article.tags.add(tag)

        new_count += 1
        logger.info(f'  Imported: {title[:60]}')

    source.last_imported_at = dj_timezone.now()
    source.save(update_fields=['last_imported_at'])
    return new_count


class Command(BaseCommand):
    help = 'Import articles from configured RSS feed sources'

    def add_arguments(self, parser):
        parser.add_argument(
            '--source', type=int, help='Import only from a specific FeedSource ID',
        )

    def handle(self, *args, **options):
        sources = FeedSource.objects.filter(is_active=True)
        if options['source']:
            sources = sources.filter(id=options['source'])
        if not sources.exists():
            self.stdout.write(self.style.WARNING('No active feed sources found.'))
            return

        total = 0
        for source in sources:
            self.stdout.write(f'Processing: {source.name} ({source.feed_url})')
            count = import_feed(source)
            total += count
            self.stdout.write(f'  Imported {count} new article(s)')
        self.stdout.write(self.style.SUCCESS(f'Done. Total: {total} new articles imported.'))
