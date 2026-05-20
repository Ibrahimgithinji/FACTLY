import json
import logging
from django.core.management.base import BaseCommand
from django.conf import settings
from content.models import PushSubscription

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Send push notification to all subscribers'

    def add_arguments(self, parser):
        parser.add_argument('--title', type=str, default='Factly')
        parser.add_argument('--body', type=str, default='')
        parser.add_argument('--url', type=str, default='/')

    def handle(self, *args, **options):
        title = options['title']
        body = options['body']
        url = options['url']

        vapid_private_key = getattr(settings, 'VAPID_PRIVATE_KEY', '')
        vapid_public_key = getattr(settings, 'VAPID_PUBLIC_KEY', '')
        if not vapid_private_key or not vapid_public_key:
            self.stdout.write(self.style.ERROR('VAPID keys not configured'))
            return

        try:
            from pywebpush import webpush, WebPushException
        except ImportError:
            self.stdout.write(self.style.ERROR('pywebpush not installed'))
            return

        subscriptions = PushSubscription.objects.all()
        if not subscriptions:
            self.stdout.write(self.style.WARNING('No push subscribers'))
            return

        payload = json.dumps({
            'title': title,
            'body': body,
            'url': url,
        })

        sent = 0
        failed = 0
        for sub in subscriptions:
            try:
                webpush(
                    subscription_info={
                        'endpoint': sub.endpoint,
                        'keys': {
                            'p256dh': sub.p256dh_key,
                            'auth': sub.auth_key,
                        }
                    },
                    data=payload,
                    vapid_private_key=vapid_private_key,
                    vapid_public_key=vapid_public_key,
                    vapid_claims={
                        'sub': 'mailto:admin@factly.tech',
                    },
                )
                sent += 1
            except WebPushException as e:
                if e.response and e.response.status_code in (410, 404):
                    sub.delete()
                    logger.info(f'Removed expired push subscription: {sub.endpoint[:50]}')
                else:
                    logger.error(f'Push failed for {sub.endpoint[:50]}: {e}')
                failed += 1
            except Exception as e:
                logger.error(f'Push error for {sub.endpoint[:50]}: {e}')
                failed += 1

        self.stdout.write(self.style.SUCCESS(
            f'Push: {sent} sent, {failed} failed, {len(subscriptions)} total'
        ))
