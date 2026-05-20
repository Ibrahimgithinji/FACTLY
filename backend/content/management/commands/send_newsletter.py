import logging
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from content.models import NewsletterSubscriber

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Send newsletter email to all active subscribers'

    def add_arguments(self, parser):
        parser.add_argument('subject', type=str, help='Email subject')
        parser.add_argument('message', type=str, help='Email body (plain text)')
        parser.add_argument('--html', type=str, default='', help='Path to HTML template')
        parser.add_argument('--test', type=str, default='', help='Send to a single email for testing')

    def handle(self, *args, **options):
        subject = options['subject']
        message = options['message']
        html_template = options['html']
        test_email = options['test']

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

        html_message = None
        if html_template:
            try:
                with open(html_template, 'r') as f:
                    html_message = f.read()
            except FileNotFoundError:
                self.stdout.write(self.style.ERROR(f'HTML template not found: {html_template}'))
                return

        sent = 0
        failed = 0
        for email in recipients:
            try:
                send_mail(
                    subject=subject,
                    message=message,
                    html_message=html_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=False,
                )
                sent += 1
            except Exception as e:
                logger.error(f'Failed to send to {email}: {e}')
                failed += 1

        self.stdout.write(self.style.SUCCESS(
            f'Done. Sent: {sent}, Failed: {failed}'
        ))
