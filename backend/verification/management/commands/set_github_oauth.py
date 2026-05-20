import os
import logging
from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)

ENV_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), '.env')


class Command(BaseCommand):
    help = 'Set GitHub OAuth client credentials in the .env file'

    def add_arguments(self, parser):
        parser.add_argument('--client-id', type=str, required=True,
                            help='GitHub OAuth Client ID')
        parser.add_argument('--secret', type=str, required=True,
                            help='GitHub OAuth Client Secret')

    def handle(self, *args, **options):
        client_id = options['client_id']
        secret = options['secret']

        if not os.path.exists(ENV_PATH):
            self.stderr.write(self.style.ERROR(f'.env file not found at {ENV_PATH}'))
            return

        with open(ENV_PATH, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        updated = []
        client_id_set = False
        secret_set = False

        for line in lines:
            if line.startswith('GITHUB_CLIENT_ID='):
                updated.append(f'GITHUB_CLIENT_ID={client_id}\n')
                client_id_set = True
            elif line.startswith('GITHUB_CLIENT_SECRET='):
                updated.append(f'GITHUB_CLIENT_SECRET={secret}\n')
                secret_set = True
            else:
                updated.append(line)

        if not client_id_set:
            updated.append(f'GITHUB_CLIENT_ID={client_id}\n')
        if not secret_set:
            updated.append(f'GITHUB_CLIENT_SECRET={secret}\n')

        with open(ENV_PATH, 'w', encoding='utf-8') as f:
            f.writelines(updated)

        self.stdout.write(self.style.SUCCESS(
            f'GitHub OAuth credentials set (client_id={client_id[:12]}...)'
        ))
