import logging
import json
import bleach
from django.conf import settings
from django.core.management import call_command
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from verification.rbac import IsAdminOnly
from .models import PushSubscription, Article

logger = logging.getLogger(__name__)


class PushSubscribeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        endpoint = request.data.get('endpoint')
        p256dh_key = request.data.get('keys', {}).get('p256dh')
        auth_key = request.data.get('keys', {}).get('auth')

        if not endpoint or not p256dh_key or not auth_key:
            return Response(
                {'error': 'endpoint, keys.p256dh, and keys.auth are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = request.user if request.user.is_authenticated else None

        sub, created = PushSubscription.objects.get_or_create(
            endpoint=endpoint,
            defaults={
                'user': user,
                'p256dh_key': p256dh_key,
                'auth_key': auth_key,
                'user_agent': bleach.clean(request.META.get('HTTP_USER_AGENT', ''), tags=[], strip=True)[:200],
            }
        )

        if not created:
            sub.p256dh_key = p256dh_key
            sub.auth_key = auth_key
            if user:
                sub.user = user
            sub.save()

        return Response({'message': 'Subscribed to push notifications'})


class PushUnsubscribeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        endpoint = request.data.get('endpoint')
        if not endpoint:
            return Response({'error': 'endpoint required'}, status=400)
        PushSubscription.objects.filter(endpoint=endpoint).delete()
        return Response({'message': 'Unsubscribed'})


class PushNotifyAllView(APIView):
    permission_classes = [IsAdminOnly]

    def post(self, request):

        title = request.data.get('title', 'Factly')
        body = request.data.get('body', '')
        url = request.data.get('url', '/')

        call_command('send_push', title=title, body=body, url=url)
        return Response({'message': 'Push notifications sent'})
