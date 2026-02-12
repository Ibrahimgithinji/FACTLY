"""
Authentication Views

JWT-based authentication endpoints for user login, signup, token refresh, and password reset.
"""

import logging
import uuid
import os
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from .models import PasswordResetToken

logger = logging.getLogger(__name__)


class LoginView(APIView):
    """User login endpoint that returns JWT tokens."""
    permission_classes = [AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            return Response(
                {'error': 'Email and password required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            logger.warning(f"Login attempt with non-existent email: {email}")
            return Response(
                {'error': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        user = authenticate(username=user.username, password=password)
        if not user:
            logger.warning(f"Failed login attempt for user: {email}")
            return Response(
                {'error': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Generate JWT tokens
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


class SignupView(APIView):
    """User registration endpoint that returns JWT tokens."""
    permission_classes = [AllowAny]
    
    def post(self, request):
        name = request.data.get('name', '')
        email = request.data.get('email')
        password = request.data.get('password')
        
        # Validate
        if not email or not password or not name:
            return Response(
                {'error': 'Name, email, and password required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if len(password) < 6:
            return Response(
                {'error': 'Password must be at least 6 characters'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if User.objects.filter(email=email).exists():
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
    
    def post(self, request):
        email = request.data.get('email')
        
        if not email:
            return Response(
                {'error': 'Email is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # For security, don't reveal if email exists
            logger.warning(f"Password reset attempt for non-existent email: {email}")
            return Response(
                {'message': 'If an account exists with this email, a password reset link has been sent.'},
                status=status.HTTP_200_OK
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
            reset_link = f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/reset-password/{token}"
            
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
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
                logger.info(f"Password reset email sent successfully to: {email}")
            except Exception as email_error:
                logger.error(f"Error sending password reset email: {email_error}")
                # Check if email credentials are not configured
                if settings.EMAIL_HOST_USER in ['', 'your-email@gmail.com'] or \
                   settings.EMAIL_HOST_PASSWORD in ['', 'your-app-specific-password']:
                    logger.warning(
                        "Email credentials appear to be not properly configured. "
                        "Using fallback backend (console output). "
                        "Reset token has been created and logged."
                    )
                    # Log the reset link for development purposes
                    logger.warning(f"=== PASSWORD RESET LINK (DEVELOPMENT MODE) ===")
                    logger.warning(f"User: {user.email}")
                    logger.warning(f"Reset Link: {reset_link}")
                    logger.warning(f"Token: {token}")
                    logger.warning(f"Expires at: {expires_at}")
                    logger.warning("==========================================")
                else:
                    # Re-raise if credentials seem configured
                    raise
            
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
        
        if len(new_password) < 6:
            return Response(
                {'error': 'Password must be at least 6 characters'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            reset_token = PasswordResetToken.objects.get(token=token)
            
            if not reset_token.is_valid():
                return Response(
                    {'error': 'Reset link has expired or already been used'},
                    status=status.HTTP_401_UNAUTHORIZED
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

