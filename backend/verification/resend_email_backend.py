"""
Resend API-based email backend for FACTLY.

Uses the Resend API to send emails reliably without SMTP configuration.
Sign up at https://resend.com to get an API key.
Falls back to file-based email when API key is invalid (for development).
"""

import logging
import os
from typing import Optional
from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend
from django.core.mail.backends.filebased import EmailBackend as FileBasedEmailBackend
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
    
    Falls back to file-based email when API key is invalid (for development).
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_key = getattr(settings, 'RESEND_API_KEY', None)
        self.from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None)
        self._api_url = 'https://api.resend.com/emails'
        self._is_valid_key = self._validate_api_key()
        self._use_file_backend = not self._is_valid_key

    def _validate_api_key(self) -> bool:
        """Check if the API key looks valid (not placeholder)."""
        if not self.api_key:
            return False
        normalized = self.api_key.strip().lower()
        if not normalized:
            return False
        placeholder_markers = ('your-', 'your_', 'example.com', 'placeholder', 'change-this', 're_')
        if any(marker in normalized for marker in placeholder_markers):
            return False
        if len(normalized) < 10:
            return False
        return True

    def open(self):
        """Test the connection to Resend API."""
        if not self.api_key:
            logger.error("RESEND_API_KEY is not configured")
            return False
        return True

    def send_messages(self, email_messages: list[EmailMessage]) -> int:
        """
        Send emails via Resend API.
        Falls back to file-based email when API key is invalid (for development).
        Returns the number of successfully sent emails.
        """
        if not email_messages:
            return 0

        if not self.api_key:
            logger.error("Cannot send email: RESEND_API_KEY not configured")
            return self._fallback_to_file(email_messages)

        if self._use_file_backend:
            logger.warning("RESEND_API_KEY appears to be a placeholder. Using file-based email backend for development.")
            return self._fallback_to_file(email_messages)

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
                    logger.info("Falling back to file-based email")

            except requests.RequestException as e:
                logger.error(f"Failed to send email via Resend: {e}", exc_info=True)
                logger.info("Falling back to file-based email")

        if sent_count < len(email_messages):
            fallback_count = self._fallback_to_file(email_messages[sent_count:])
            sent_count += fallback_count

        return sent_count

    def _fallback_to_file(self, email_messages: list[EmailMessage]) -> int:
        """Save emails to files when API is not available."""
        try:
            file_path = getattr(settings, 'EMAIL_FILE_PATH', 'tmp/emails')
            os.makedirs(file_path, exist_ok=True)
            file_backend = FileBasedEmailBackend(file_path=file_path)
            file_backend.open()
            result = file_backend.send_messages(email_messages)
            file_backend.close()
            logger.info(f"Saved {result} email(s) to {file_path} for development")
            return result
        except Exception as e:
            logger.error(f"Failed to save email to file: {e}", exc_info=True)
            return 0

    def close(self):
        """Close any open connections."""
        pass