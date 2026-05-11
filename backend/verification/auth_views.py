"""
Authentication Views

JWT-based authentication endpoints for user login, signup, token refresh, and password reset.
"""

import logging
import uuid
import os
import re
from threading import Lock
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.db import connection
from django.db.utils import OperationalError
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle


class LoginRateThrottle(AnonRateThrottle):
    rate = '10/minute'
    scope = 'login'


class PasswordResetRateThrottle(AnonRateThrottle):
    rate = '5/minute'
    scope = 'password_reset'
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from .models import PasswordResetToken

logger = logging.getLogger(__name__)
_AUTH_SCHEMA_INIT_LOCK = Lock()
_AUTH_SCHEMA_READY = False


def _ensure_auth_schema_ready():
    """
    Ensure auth tables exist before handling auth requests.
    This avoids login/signup 500s on fresh or in-memory databases.

    Should only be called at module load or app startup, not per-request.
    Uses a lock to prevent race conditions during initialization.
    """
    global _AUTH_SCHEMA_READY
    if _AUTH_SCHEMA_READY:
        return

    with _AUTH_SCHEMA_INIT_LOCK:
        if _AUTH_SCHEMA_READY:
            return

        try:
            from django.apps import apps
            if apps.is_installed('django.contrib.auth'):
                try:
                    apps.get_model('auth', 'User')
                    _AUTH_SCHEMA_READY = True
                    return
                except LookupError:
                    pass

            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='auth_user'"
                )
                table_exists = cursor.fetchone() is not None
        except Exception:
            table_exists = False

        if not table_exists:
            logger.warning("auth_user table missing; running migrations to bootstrap auth schema.")
            call_command('migrate', interactive=False, run_syncdb=True, verbosity=0)

        _AUTH_SCHEMA_READY = True


# Run schema check at module import time instead of per-request
try:
    _ensure_auth_schema_ready()
except Exception as e:
    logger.error(f"Failed to initialize auth schema at startup: {e}", exc_info=True)


def _looks_like_placeholder_secret(value):
    """Detect obvious placeholder values that cannot deliver real email."""
    normalized = (value or '').strip().lower()
    if not normalized:
        return True

    placeholder_markers = (
        'your-',
        'your_',
        'example.com',
        'placeholder',
        'change-this',
        'app-password',
    )
    return any(marker in normalized for marker in placeholder_markers)


def _has_real_smtp_credentials():
    """
    Validate whether SMTP credentials are configured for actual inbox delivery.
    We enforce this only for SMTP/fallback backends that are expected to send real email.
    """
    backend = (getattr(settings, 'EMAIL_BACKEND', '') or '').lower()
    uses_smtp_credentials = (
        'django.core.mail.backends.smtp.emailbackend' in backend
        or 'verification.email_backend.fallbackemailbackend' in backend
    )
    if not uses_smtp_credentials:
        return True

    host_user = getattr(settings, 'EMAIL_HOST_USER', '')
    host_password = getattr(settings, 'EMAIL_HOST_PASSWORD', '')
    return not (
        _looks_like_placeholder_secret(host_user)
        or _looks_like_placeholder_secret(host_password)
    )


class LoginView(APIView):
    """User login endpoint that returns JWT tokens."""
    permission_classes = [AllowAny]
    throttle_classes = [LoginRateThrottle]
    
    def post(self, request):
        email = request.data.get('email') or ''
        password = request.data.get('password')
        
        email = email.strip().lower()

        if not email or not password:
            return Response(
                {'error': 'Email and password required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Perform case-insensitive lookup and normalize email before login
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            logger.warning(f"Login attempt with non-existent email: {email}")
            return Response(
                {'error': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        except User.MultipleObjectsReturned:
            logger.error(f"Multiple user accounts found for email: {email}", exc_info=True)
            return Response(
                {'error': 'Multiple accounts found for this email address. Please contact support.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Database error during user lookup: {e}", exc_info=True)
            return Response(
                {'error': 'Server error. Please try again later.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Make sure username is still used for Django authentication
        try:
            username = user.username or email
            user = authenticate(username=username, password=password)
            if not user:
                logger.warning(f"Failed login attempt for user: {email}")
                return Response(
                    {'error': 'Invalid credentials'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
        except Exception as e:
            logger.error(f"Authentication error: {e}", exc_info=True)
            return Response(
                {'error': 'Server error during authentication. Please try again later.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Generate JWT tokens
        try:
            refresh = RefreshToken.for_user(user)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'name': user.first_name or user.username,
                }
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"JWT token generation error: {e}", exc_info=True)
            return Response(
                {'error': 'Server error generating tokens. Please try again later.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SignupView(APIView):
    """User registration endpoint that returns JWT tokens."""
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]
    
    def post(self, request):
        name = request.data.get('name', '')
        email = request.data.get('email')
        password = request.data.get('password')
        # normalize email to lowercase for consistency and to avoid duplicates
        if email:
            email = email.strip().lower()
        
        # Validate
        if not email or not password or not name:
            return Response(
                {'error': 'Name, email, and password required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if len(password) < 8:
            return Response(
                {'error': 'Password must be at least 8 characters'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Enforce Django password validators (complexity, common passwords, etc.)
        try:
            temp_user = User(username=email, email=email, first_name=name)
            validate_password(password, user=temp_user)
        except ValidationError as e:
            return Response(
                {'error': ' '.join(e.messages)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # check for existing account with same email (case-insensitive)
        if User.objects.filter(email__iexact=email).exists():
            return Response(
                {'error': 'Email already registered'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=name
            )
            
            refresh = RefreshToken.for_user(user)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'name': user.first_name or user.username,
                }
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Signup error: {e}")
            return Response(
                {'error': 'Unable to create account'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RefreshTokenView(APIView):
    """Token refresh endpoint for getting new access tokens."""
    permission_classes = [AllowAny]
    
    def post(self, request):
        refresh_token = request.data.get('refresh')
        
        if not refresh_token:
            return Response(
                {'error': 'Refresh token required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            refresh = RefreshToken(refresh_token)
            return Response({
                'access': str(refresh.access_token),
            })
        except Exception as e:
            logger.warning(f"Invalid refresh token: {e}")
            return Response(
                {'error': 'Invalid refresh token'},
                status=status.HTTP_401_UNAUTHORIZED
            )


class ForgotPasswordView(APIView):
    """Send password reset email to user."""
    permission_classes = [AllowAny]
    throttle_classes = [PasswordResetRateThrottle]
    
    def post(self, request):
        email = (request.data.get('email') or '').strip().lower()
        
        if not email:
            return Response(
                {'error': 'Email is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            validate_email(email)
        except ValidationError:
            return Response(
                {'error': 'Please provide a valid email address'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not _has_real_smtp_credentials():
            logger.error(
                "Password reset email service is not configured with real SMTP credentials."
            )
            return Response(
                {
                    'error': (
                        'Email service is not configured. '
                        'Set valid EMAIL_HOST_USER and EMAIL_HOST_PASSWORD in backend/.env.'
                    )
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        # Fetch at most two rows so we can detect duplicates without an extra count query.
        matching_users = list(
            User.objects.filter(email__iexact=email).order_by('-date_joined')[:2]
        )

        if not matching_users:
            # For security, don't reveal if email exists
            logger.warning(f"Password reset attempt for non-existent email: {email}")
            return Response(
                {'message': 'If an account exists with this email, a password reset link has been sent.'},
                status=status.HTTP_200_OK
            )

        user = matching_users[0]
        if len(matching_users) > 1:
            logger.warning(
                "Multiple user accounts found for password reset email %s; using most recently created account id=%s.",
                email,
                user.id
            )
        
        try:
            # Delete existing reset token if any
            PasswordResetToken.objects.filter(user=user).delete()
            
            # Generate new reset token
            token = str(uuid.uuid4())
            timeout_hours = getattr(settings, 'PASSWORD_RESET_TIMEOUT_HOURS', 24)
            expires_at = timezone.now() + timezone.timedelta(hours=timeout_hours)
            
            reset_token = PasswordResetToken.objects.create(
                user=user,
                token=token,
                expires_at=expires_at,
            )
            
            # Send email with reset link
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
            
            try:
                sent_count = send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
                if sent_count != 1:
                    logger.error(
                        "Password reset email was not delivered for %s. send_mail returned %s.",
                        user.email,
                        sent_count
                    )
                    return Response(
                        {'error': 'Unable to send reset email right now. Please try again later.'},
                        status=status.HTTP_503_SERVICE_UNAVAILABLE
                    )
                logger.info(f"Password reset email sent successfully to: {email}")
            except Exception as email_error:
                logger.error(f"Error sending password reset email: {email_error}", exc_info=True)
                return Response(
                    {'error': 'Unable to send reset email right now. Please try again later.'},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
            
            return Response(
                {'message': 'If an account exists with this email, a password reset link has been sent.'},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error(f"Error processing password reset request: {e}")
            return Response(
                {'error': 'Unable to process password reset request. Please try again later.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class VerifyResetTokenView(APIView):
    """Verify if a password reset token is valid."""
    permission_classes = [AllowAny]
    
    def post(self, request):
        token = request.data.get('token')
        
        if not token:
            return Response(
                {'error': 'Token is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            reset_token = PasswordResetToken.objects.get(token=token)
            
            if not reset_token.is_valid():
                return Response(
                    {'error': 'Reset link has expired or already been used'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            return Response(
                {
                    'valid': True,
                    'email': reset_token.user.email,
                },
                status=status.HTTP_200_OK
            )
        except PasswordResetToken.DoesNotExist:
            return Response(
                {'error': 'Invalid reset token'},
                status=status.HTTP_401_UNAUTHORIZED
            )


class ResetPasswordView(APIView):
    """Reset password using a valid reset token."""
    permission_classes = [AllowAny]
    throttle_classes = [PasswordResetRateThrottle]
    
    def post(self, request):
        token = request.data.get('token')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')
        
        # Validate inputs
        if not token or not new_password or not confirm_password:
            return Response(
                {'error': 'Token, new password, and confirmation required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if new_password != confirm_password:
            return Response(
                {'error': 'Passwords do not match'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if len(new_password) < 8:
            return Response(
                {'error': 'Password must be at least 8 characters'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            reset_token = PasswordResetToken.objects.get(token=token)

            if not reset_token.is_valid():
                return Response(
                    {'error': 'Reset link has expired or already been used'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            # Enforce Django password validators on reset too
            try:
                validate_password(new_password, user=reset_token.user)
            except ValidationError as e:
                return Response(
                    {'error': ' '.join(e.messages)},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Update password
            user = reset_token.user
            user.set_password(new_password)
            user.save()
            
            # Mark token as used
            reset_token.is_used = True
            reset_token.save()
            
            logger.info(f"Password reset successfully for user: {user.email}")
            return Response(
                {'message': 'Password has been reset successfully'},
                status=status.HTTP_200_OK
            )
        except PasswordResetToken.DoesNotExist:
            return Response(
                {'error': 'Invalid reset token'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        except Exception as e:
            logger.error(f"Error resetting password: {e}")
            return Response(
                {'error': 'Unable to reset password'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


