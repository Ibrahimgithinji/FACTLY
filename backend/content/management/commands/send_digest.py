import logging
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.template.loader import render_to_string
from content.models import Article, NewsletterSubscriber

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Send newsletter digest with latest articles to all active subscribers'

    def add_arguments(self, parser):
        parser.add_argument('--days', type=int, default=7,
                            help='Include articles from last N days (default: 7)')
        parser.add_argument('--test', type=str, default='',
                            help='Send to a single email for testing')
        parser.add_argument('--limit', type=int, default=5,
                            help='Max articles in digest (default: 5)')

    def handle(self, *args, **options):
        days = options['days']
        test_email = options['test']
        limit = options['limit']

        since = timezone.now() - timedelta(days=days)

        articles = Article.objects.filter(
            status='published',
            published_at__gte=since,
        ).order_by('-published_at')[:limit]

        if not articles:
            self.stdout.write(self.style.WARNING('No articles found in the last %d days' % days))
            return

        if test_email:
            recipients = [test_email]
        else:
            recipients = list(
                NewsletterSubscriber.objects.filter(is_active=True)
                .values_list('email', flat=True)
            )

        if not recipients:
            self.stdout.write(self.style.WARNING('No subscribers to send to.'))
            return

        # Build HTML content
        articles_html = ''.join(
            '<div style="margin-bottom:24px;padding-bottom:20px;border-bottom:1px solid #eee;">'
            f'<h3 style="margin:0 0 6px;font-size:16px;"><a href="{settings.SITE_URL}/article/{a.slug}" style="color:#1a73e8;text-decoration:none;">{a.title}</a></h3>'
            f'<p style="margin:0;font-size:13px;color:#666;">{a.excerpt[:200]}</p>'
            f'<p style="margin:6px 0 0;font-size:12px;color:#999;">{a.read_time} min read</p>'
            '</div>'
            for a in articles
        )

        subject = 'Factly Digest - Latest Articles'
        html_message = f'''
        <div style="max-width:600px;margin:0 auto;font-family:Arial,sans-serif;">
            <div style="background:#0f172a;padding:24px;text-align:center;border-radius:8px 8px 0 0;">
                <h1 style="color:#fff;margin:0;font-size:24px;">Factly</h1>
                <p style="color:#94a3b8;margin:4px 0 0;font-size:14px;">Tech News & Fact Verification</p>
            </div>
            <div style="padding:24px;background:#fff;border:1px solid #e2e8f0;">
                <h2 style="margin:0 0 20px;font-size:18px;color:#0f172a;">
                    This Week in Tech {'(' + str(days) + ' days)' if days != 7 else ''}
                </h2>
                {articles_html}
                <p style="margin-top:24px;text-align:center;">
                    <a href="{settings.SITE_URL}" style="background:#0f172a;color:#fff;padding:10px 20px;border-radius:6px;text-decoration:none;font-size:14px;">Visit Factly</a>
                </p>
            </div>
            <div style="padding:16px;text-align:center;font-size:12px;color:#94a3b8;">
                <p style="margin:0;">You received this because you subscribed to Factly.</p>
                <p style="margin:4px 0 0;">
                    <a href="{settings.SITE_URL}" style="color:#1a73e8;">Unsubscribe</a>
                </p>
            </div>
        </div>
        '''

        plain_message = f'Factly Digest\n\nLatest articles from the past {days} days:\n\n'
        for a in articles:
            plain_message += f'- {a.title}\n  {a.excerpt[:100]}...\n  {settings.SITE_URL}/article/{a.slug}\n\n'
        plain_message += f'\nVisit {settings.SITE_URL} for more.'

        sent = 0
        failed = 0
        for email in recipients:
            try:
                send_mail(
                    subject=subject,
                    message=plain_message,
                    html_message=html_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=False,
                )
                sent += 1
            except Exception as e:
                logger.error(f'Failed to send digest to {email}: {e}')
                failed += 1

        self.stdout.write(self.style.SUCCESS(
            f'Digest sent: {sent} delivered, {failed} failed, {len(articles)} articles'
        ))
