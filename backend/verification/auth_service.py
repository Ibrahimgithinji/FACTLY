import logging
import uuid

from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.utils import timezone

from .models import PasswordResetToken

logger = logging.getLogger(__name__)


def _has_real_smtp_credentials():
    backend = (getattr(settings, 'EMAIL_BACKEND', '') or '').lower()
    uses_smtp_credentials = (
        'django.core.mail.backends.smtp.emailbackend' in backend
        or 'verification.email_backend.fallbackemailbackend' in backend
    )
    if not uses_smtp_credentials:
        return True
    if 'developmentemailbackend' in backend or 'fallbackemailbackend' in backend:
        return True
    if 'resend' in backend:
        resend_key = getattr(settings, 'RESEND_API_KEY', '') or ''
        if not resend_key:
            return False
        normalized = resend_key.strip().lower()
        if not normalized:
            return False
        placeholder_markers = ('your-', 'your_', 'example.com', 'placeholder', 'change-this')
        if any(marker in normalized for marker in placeholder_markers):
            logger.warning("RESEND_API_KEY appears to be a placeholder. Email will be saved to file for development.")
            return True
        if len(normalized) < 10:
            return False
        return True
    host_user = getattr(settings, 'EMAIL_HOST_USER', '')
    host_password = getattr(settings, 'EMAIL_HOST_PASSWORD', '')
    return bool(host_user and host_password)


class AuthService:
    def send_password_reset_email(self, email):
        if not _has_real_smtp_credentials():
            logger.error("Password reset email service is not configured with real SMTP credentials.")
            raise RuntimeError(
                'Email service is not configured. '
                'Set valid EMAIL_HOST_USER and EMAIL_HOST_PASSWORD in backend/.env.'
            )

        matching_users = list(
            User.objects.filter(email__iexact=email).order_by('-date_joined')[:2]
        )

        if not matching_users:
            logger.warning(f"Password reset attempt for non-existent email: {email}")
            return

        user = matching_users[0]
        if len(matching_users) > 1:
            logger.warning(
                "Multiple user accounts found for password reset email %s; using most recently created account id=%s.",
                email, user.id
            )

        PasswordResetToken.objects.filter(user=user).delete()

        token = str(uuid.uuid4())
        timeout_hours = getattr(settings, 'PASSWORD_RESET_TIMEOUT_HOURS', 24)
        expires_at = timezone.now() + timezone.timedelta(hours=timeout_hours)

        PasswordResetToken.objects.create(
            user=user, token=token, expires_at=expires_at,
        )

        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000').rstrip('/')
        reset_link = f"{frontend_url}/reset-password/{token}"

        subject = 'Password Reset Request - FACTLY'
        message = f"""
Hello {user.first_name or user.username},

You have requested to reset your password. Click the link below to set a new password:

{reset_link}

This link will expire in {timeout_hours} hours.

If you did not request this, please ignore this email.

Best regards,
FACTLY Team
        """

        sent_count = send_mail(
            subject, message, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False,
        )
        if sent_count != 1:
            logger.error(
                "Password reset email was not delivered for %s. send_mail returned %s.",
                user.email, sent_count,
            )
            raise RuntimeError('Unable to send reset email right now. Please try again later.')

        logger.info(f"Password reset email sent successfully to: {email}")

        if settings.DEBUG:
            logger.info("=" * 60)
            logger.info("RESET LINK (development mode): %s", reset_link)
            logger.info("=" * 60)
