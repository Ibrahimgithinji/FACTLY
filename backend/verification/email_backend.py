"""
Custom email backend for development and production use.

Provides fallback functionality when email credentials are not properly configured.
"""

import logging
from django.core.mail.backends.smtp import EmailBackend as SMTPBackend
from django.core.mail.backends.console import EmailBackend as ConsoleBackend
from django.conf import settings

logger = logging.getLogger(__name__)


class FallbackEmailBackend(SMTPBackend):
    """
    Email backend that falls back to console output if SMTP credentials are invalid.
    Useful for development when real email credentials are not available.
    """
    
    def open(self):
        """
        Open connection to SMTP server.
        Falls back to console backend if credentials are placeholders or invalid.
        """
        # Check if using placeholder or clearly non-configured credentials
        host_user = settings.EMAIL_HOST_USER
        host_password = settings.EMAIL_HOST_PASSWORD

        def _looks_like_placeholder(value):
            v = (value or '').lower()
            if v == '':
                return True
            # catch common placeholder patterns
            if 'your' in v or 'example' in v or 'app' in v or 'password' in v:
                return True
            return False

        if _looks_like_placeholder(host_user) or _looks_like_placeholder(host_password):
            logger.warning(
                'Email credentials appear to be placeholders. '
                'Using console backend for development. '
                'Configure EMAIL_HOST_USER and EMAIL_HOST_PASSWORD in .env for production.'
            )
            # Switch to console backend
            self.connection = None
            # We'll use console output instead
            self._use_console = True
            return False
        
        self._use_console = False
        # Try to open SMTP connection
        try:
            return super().open()
        except Exception as e:
            logger.error(f'Failed to open SMTP connection: {e}')
            logger.warning('Falling back to console email backend')
            self._use_console = True
            self.connection = None
            return False
    
    def send_messages(self, email_messages):
        """
        Send messages using SMTP or fallback to console.
        """
        if not email_messages:
            return 0
        
        # If we need to use console backend, do that
        if getattr(self, '_use_console', False):
            console_backend = ConsoleBackend()
            return console_backend.send_messages(email_messages)
        
        # Otherwise try SMTP
        try:
            return super().send_messages(email_messages)
        except Exception as e:
            logger.error(f'Error sending emails via SMTP: {e}')
            logger.info('Retrying with console backend')
            # Fallback to console
            console_backend = ConsoleBackend()
            try:
                return console_backend.send_messages(email_messages)
            except Exception as console_error:
                logger.error(f'Error sending emails via console backend: {console_error}')
                raise

class DevelopmentEmailBackend(FallbackEmailBackend):
    """
    Email backend optimized for development.
    Logs all emails including password reset tokens for easy testing.
    """
    
    def send_messages(self, email_messages):
        """
        Send messages and log them for development/debugging.
        """
        if not email_messages:
            return 0
        
        # Log all emails being sent for development purposes
        for message in email_messages:
            logger.info(f"\n{'='*60}")
            logger.info(f"EMAIL MESSAGE (Development Mode)")
            logger.info(f"{'='*60}")
            logger.info(f"To: {', '.join(message.to)}")
            logger.info(f"From: {message.from_email}")
            logger.info(f"Subject: {message.subject}")
            logger.info(f"\nBody:\n{message.body}")
            logger.info(f"{'='*60}\n")
        
        # Then try to send normally
        return super().send_messages(email_messages)