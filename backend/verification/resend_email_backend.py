"""
Resend API-based email backend for FACTLY.

Uses the Resend API to send emails reliably without SMTP configuration.
Sign up at https://resend.com to get an API key.
"""

import logging
from typing import Optional
from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend
from django.core.mail.message import EmailMessage

logger = logging.getLogger(__name__)


class EmailBackend(BaseEmailBackend):
    """
    Email backend that sends emails via Resend's API.

    Advantages over SMTP:
    - No SMTP server configuration needed
    - More reliable delivery
    - Free tier: 100 emails/day
    - Simple API key authentication
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_key = getattr(settings, 'RESEND_API_KEY', None)
        self.from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None)
        self._api_url = 'https://api.resend.com/emails'

    def open(self):
        """Test the connection to Resend API."""
        if not self.api_key:
            logger.error("RESEND_API_KEY is not configured")
            return False
        return True

    def send_messages(self, email_messages: list[EmailMessage]) -> int:
        """
        Send emails via Resend API.

        Returns the number of successfully sent emails.
        """
        if not email_messages:
            return 0

        if not self.api_key:
            logger.error("Cannot send email: RESEND_API_KEY not configured")
            return 0

        import requests

        sent_count = 0
        for message in email_messages:
            try:
                payload = {
                    'from': message.from_email or self.from_email,
                    'to': [addr for addr in message.to],
                    'subject': message.subject,
                    'html': message.body if message.content_subtype == 'html' else None,
                    'text': message.body if message.content_subtype != 'html' else None,
                }

                if not payload.get('from'):
                    payload['from'] = self.from_email

                response = requests.post(
                    self._api_url,
                    json=payload,
                    headers={
                        'Authorization': f'Bearer {self.api_key}',
                        'Content-Type': 'application/json',
                    },
                    timeout=30,
                )

                if response.status_code in (200, 201, 202):
                    sent_count += 1
                    logger.info(f"Email sent successfully via Resend to {message.to}")
                else:
                    logger.error(
                        f"Resend API error: {response.status_code} - {response.text}"
                    )

            except requests.RequestException as e:
                logger.error(f"Failed to send email via Resend: {e}", exc_info=True)

        return sent_count

    def close(self):
        """Close any open connections."""
        pass