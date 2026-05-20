import logging
from datetime import timedelta
from django.db.models import Count
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import Article, PageView, NewsletterSubscriber, PushSubscription, Bookmark, Comment

logger = logging.getLogger(__name__)


class LogPageView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        path = request.data.get('path', '')
        article_id = request.data.get('article_id')

        if not path:
            return Response({'error': 'path required'}, status=400)

        PageView.objects.create(
            article_id=article_id if article_id else None,
            path=path[:500],
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
        )
        return Response({'message': 'logged'})


class DashboardStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_staff:
            return Response({'error': 'Staff only'}, status=403)

        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)

        total_articles = Article.objects.count()
        published_articles = Article.objects.filter(status='published').count()
        total_categories = Article.objects.values('category').distinct().count()

        # Page views
        total_views = PageView.objects.count()
        today_views = PageView.objects.filter(viewed_at__gte=today_start).count()
        week_views = PageView.objects.filter(viewed_at__gte=week_ago).count()

        # Subscribers
        total_subscribers = NewsletterSubscriber.objects.filter(is_active=True).count()
        today_subscribers = NewsletterSubscriber.objects.filter(
            created_at__gte=today_start
        ).count()

        # Push subs
        total_push_subs = PushSubscription.objects.count()

        # Bookmarks
        total_bookmarks = Bookmark.objects.count()

        # Comments
        total_comments = Comment.objects.count()

        # Most viewed articles (last 30 days)
        most_viewed = (
            Article.objects.filter(
                page_views__viewed_at__gte=month_ago,
                status='published',
            )
            .annotate(views=Count('page_views'))
            .order_by('-views')[:10]
            .values('id', 'title', 'slug', 'views')
        )

        # Recent articles
        recent_articles = (
            Article.objects.filter(status='published')
            .order_by('-created_at')[:5]
            .values('id', 'title', 'slug', 'created_at')
        )

        return Response({
            'articles': {
                'total': total_articles,
                'published': published_articles,
                'categories': total_categories,
            },
            'page_views': {
                'total': total_views,
                'today': today_views,
                'this_week': week_views,
            },
            'subscribers': {
                'total': total_subscribers,
                'today': today_subscribers,
            },
            'push_subscriptions': total_push_subs,
            'bookmarks': total_bookmarks,
            'comments': total_comments,
            'most_viewed_articles': list(most_viewed),
            'recent_articles': list(recent_articles),
        })
