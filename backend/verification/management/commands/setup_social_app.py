import logging
from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Register social login apps (Google, GitHub) with Django allauth'

    def add_arguments(self, parser):
        parser.add_argument('--provider', type=str, required=True,
                            choices=['google', 'github'],
                            help='OAuth provider')
        parser.add_argument('--client-id', type=str, required=True,
                            help='OAuth client ID')
        parser.add_argument('--secret', type=str, required=True,
                            help='OAuth client secret')
        parser.add_argument('--site-domain', type=str, default='localhost:3000',
                            help='Site domain (default: localhost:3000)')
        parser.add_argument('--site-name', type=str, default='Factly',
                            help='Site name (default: Factly)')
        parser.add_argument('--key', type=str, default='',
                            help='Optional provider-specific key (Google uses this for API key)')

    def handle(self, *args, **options):
        from allauth.socialaccount.models import SocialApp

        provider = options['provider']
        client_id = options['client_id']
        secret = options['secret']
        site_domain = options['site_domain']
        site_name = options['site_name']
        key = options['key']

        # Ensure the Site record exists
        site, created = Site.objects.get_or_create(
            domain=site_domain,
            defaults={'name': site_name},
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created site: {site_domain}'))
        else:
            site.name = site_name
            site.save(update_fields=['name'])

        # Create or update the SocialApp
        app, created = SocialApp.objects.update_or_create(
            provider=provider,
            defaults={
                'name': f'Factly - {provider.title()}',
                'client_id': client_id,
                'secret': secret,
                'key': key,
            }
        )
        # Add site to the app's sites
        app.sites.add(site)

        status = 'Created' if created else 'Updated'
        self.stdout.write(self.style.SUCCESS(
            f'{status} {provider} SocialApp (client_id={client_id[:12]}...)'
        ))
