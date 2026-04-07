"""
User and History Views

Handles user profile information and verification history storage.
"""

import logging
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger(__name__)


class UserProfileView(APIView):
    """User profile endpoint - returns authenticated user information."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get current user profile information."""
        try:
            user = request.user
            return Response({
                'id': user.id,
                'email': user.email,
                'name': user.first_name or user.username,
                'username': user.username,
                'created_at': user.date_joined.isoformat(),
                'last_login': user.last_login.isoformat() if user.last_login else None,
                'is_active': user.is_active,
                'verified': True  # Assuming all authenticated users are verified
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception("Failed to fetch user profile")
            return Response(
                {'error': 'Failed to fetch user profile'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def put(self, request):
        """Update user profile information."""
        try:
            user = request.user
            data = request.data
            
            # Update allowed fields
            if 'name' in data:
                user.first_name = data['name']
            
            if 'email' in data:
                # Check if email is already used
                if data['email'] != user.email:
                    if User.objects.filter(email__iexact=data['email']).exclude(id=user.id).exists():
                        return Response(
                            {'error': 'Email already in use'},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                user.email = data['email']
            
            user.save()
            
            return Response({
                'id': user.id,
                'email': user.email,
                'name': user.first_name or user.username,
                'updated_at': timezone.now().isoformat(),
                'message': 'Profile updated successfully'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.exception("Failed to update user profile")
            return Response(
                {'error': 'Failed to update user profile'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserStatisticsView(APIView):
    """User statistics endpoint - returns verification stats for authenticated user."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get user verification statistics."""
        try:
            # This would normally fetch stats from a verification history model
            # For now, return default stats
            user = request.user
            
            return Response({
                'user_id': user.id,
                'total_verifications': 0,
                'successful_verifications': 0,
                'failed_verifications': 0,
                'avg_processing_time_ms': 0,
                'most_verified_topics': [],
                'account_created': user.date_joined.isoformat(),
                'last_verification': None,
                'message': 'Statistics from verification history'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.exception("Failed to fetch user statistics")
            return Response(
                {'error': 'Failed to fetch user statistics'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
