"""
Custom email backend for development and production use.

Provides fallback functionality when email credentials are not properly configured.
"""

import logging
from django.core.mail.backends.smtp import EmailBackend as SMTPBackend
from django.core.mail.backends.console import EmailBackend as ConsoleBackend
from django.core.mail.backends.filebased import EmailBackend as FileBasedEmailBackend
from django.conf import settings

logger = logging.getLogger(__name__)


def _credentials_usable():
    """Check if SMTP credentials are non-empty and long enough to be real."""
    host_user = getattr(settings, 'EMAIL_HOST_USER', '') or ''
    host_password = getattr(settings, 'EMAIL_HOST_PASSWORD', '') or ''
    if not host_user.strip() or not host_password.strip():
        return False
    if len(host_user.strip()) < 5 or len(host_password.strip()) < 5:
        return False
    return True


class FallbackEmailBackend(SMTPBackend):
    """
    Email backend that falls back to file-based delivery if SMTP credentials
    are missing, invalid, or the SMTP connection fails.

    - If EMAIL_HOST_USER and EMAIL_HOST_PASSWORD are set and look valid -> SMTP.
    - If SMTP fails at runtime -> saves to EMAIL_FILE_PATH.
    - If credentials are missing entirely -> saves to EMAIL_FILE_PATH directly.
    """

    def send_messages(self, email_messages):
        if not email_messages:
            return 0

        # If we have usable credentials, try SMTP
        if _credentials_usable():
            try:
                return super().send_messages(email_messages)
            except Exception as e:
                logger.error(f'Error sending emails via SMTP: {e}')
                logger.info('Retrying with file backend')
        else:
            logger.warning(
                f'Email credentials are missing or invalid. '
                f'EMAIL_HOST_USER: {getattr(settings, "EMAIL_HOST_USER", "")}, '
                f'EMAIL_HOST_PASSWORD: [REDACTED]. '
                f'Saving emails to {settings.EMAIL_FILE_PATH}. '
                f'Configure EMAIL_HOST_USER and EMAIL_HOST_PASSWORD in .env for delivery.'
            )

        # Fallback to file-based
        try:
            file_backend = FileBasedEmailBackend(file_path=settings.EMAIL_FILE_PATH)
            return file_backend.send_messages(email_messages)
        except Exception as fb_error:
            logger.error(f'File backend error: {fb_error}', exc_info=True)
            return 0


class DevelopmentEmailBackend(FallbackEmailBackend):
    """
    Email backend optimized for development.
    Logs email content and sends via console backend.
    Bypasses SMTP entirely.
    """

    def send_messages(self, email_messages):
        if not email_messages:
            return 0

        for message in email_messages:
            logger.info(f"\n{'='*60}")
            logger.info(f"EMAIL MESSAGE (Development Mode)")
            logger.info(f"{'='*60}")
            logger.info(f"To: {', '.join(message.to)}")
            logger.info(f"From: {message.from_email}")
            logger.info(f"Subject: {message.subject}")
            logger.info(f"Body:\n{message.body}")
            logger.info(f"{'='*60}\n")

        console_backend = ConsoleBackend()
        return console_backend.send_messages(email_messages)
