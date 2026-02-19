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
        
        Enhanced placeholder detection to catch common development mistakes:
        - Values containing 'your-email' (e.g., your-email@gmail.com)
        - Values containing 'your-smtp-password' or 'your-app-password'
        - Values containing 'example.com' domains
        """
        # Check if using placeholder or clearly non-configured credentials
        host_user = settings.EMAIL_HOST_USER
        host_password = settings.EMAIL_HOST_PASSWORD

        def _looks_like_placeholder(value):
            """
            Check if a value looks like a placeholder rather than real credentials.
            Returns True for:
            - Empty strings
            - Common placeholder patterns like 'your-email', 'your-app-password', etc.
            """
            v = (value or '').lower()
            if v == '':
                return True
            # catch common placeholder patterns
            placeholder_patterns = [
                'your-email',      # matches your-email@gmail.com, your-email@example.com
                'your-smtp-password',
                'your-app-password',
                'example.com',     # matches any@example.com placeholders
            ]
            for pattern in placeholder_patterns:
                if pattern in v:
                    return True
            return False

        if _looks_like_placeholder(host_user) or _looks_like_placeholder(host_password):
            logger.warning(
                f'Email credentials appear to be placeholders or not configured. '
                f'EMAIL_HOST_USER: {host_user}, EMAIL_HOST_PASSWORD: [REDACTED]. '
                f'Using console backend for development. '
                f'Configure EMAIL_HOST_USER and EMAIL_HOST_PASSWORD in .env for production.'
            )
            # Switch to console backend
            self.connection = None
            # We'll use console output instead
            self._use_console = True
            self._console_messages = []  # Store messages for logging
            return False
        
        self._use_console = False
        self._console_messages = []
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
    Automatically uses console backend for development.
    """
    
    def open(self):
        """
        Always use console backend in development mode.
        This bypasses SMTP entirely for reliable email logging.
        """
        self._use_console = True
        return False
    
    def send_messages(self, email_messages):
        """
        Send messages and log them for development/debugging.
        """
        if not email_messages:
            return 0
        
        # Use console backend for development
        from django.core.mail.backends.console import EmailBackend as ConsoleBackend
        console_backend = ConsoleBackend()
        
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
        
        # Send via console backend
        return console_backend.send_messages(email_messages)