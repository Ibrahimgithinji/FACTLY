import logging
import bleach
from django.http import Http404
from django.db import DatabaseError
from django.db.models import Count
from django.utils.html import strip_tags
from rest_framework import generics, permissions, filters
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from django.utils import timezone
from .models import Category, Tag, Article, Comment
from .serializers import (
    CategorySerializer, TagSerializer, ArticleListSerializer,
    ArticleDetailSerializer, CommentSerializer, CommentCreateSerializer,
    GuestArticleSerializer, AuthorProfileSerializer,
)
from .fallback_content import DEMO_CATEGORIES, demo_articles, demo_article_detail, demo_homepage

logger = logging.getLogger(__name__)


class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]

    def list(self, request, *args, **kwargs):
        try:
            response = super().list(request, *args, **kwargs)
            if response.data:
                return response
        except DatabaseError as exc:
            logger.warning("Category API falling back to editorial demo data: %s", exc)
        return Response(DEMO_CATEGORIES)


class ArticlePagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 50


class ArticleListView(generics.ListAPIView):
    serializer_class = ArticleListSerializer
    permission_classes = [AllowAny]
    pagination_class = ArticlePagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'excerpt', 'content']
    ordering_fields = ['published_at', 'title']
    ordering = ['-published_at']

    def get_queryset(self):
        queryset = Article.objects.select_related(
            'category', 'author'
        ).prefetch_related('tags').filter(
            status='published', published_at__lte=timezone.now()
        )
        category = self.request.query_params.get('category', None)
        tag = self.request.query_params.get('tag', None)
        author = self.request.query_params.get('author', None)
        featured = self.request.query_params.get('featured', None)
        trending = self.request.query_params.get('trending', None)

        if category:
            queryset = queryset.filter(category__slug=category)
        if tag:
            queryset = queryset.filter(tags__slug=tag)
        if author:
            queryset = queryset.filter(author__id=author)
        if featured:
            queryset = queryset.filter(is_featured=True)
        if trending:
            queryset = queryset.filter(is_trending=True)

        return queryset.distinct()

    def list(self, request, *args, **kwargs):
        try:
            response = super().list(request, *args, **kwargs)
            results = response.data.get('results') if isinstance(response.data, dict) else response.data
            if results:
                return response
        except DatabaseError as exc:
            logger.warning("Article list API falling back to editorial demo data: %s", exc)

        articles = demo_articles()
        category = request.query_params.get('category')
        featured = request.query_params.get('featured')
        trending = request.query_params.get('trending')
        query = (request.query_params.get('search') or '').strip().lower()

        if category:
            articles = [article for article in articles if article['category']['slug'] == category]
        if featured:
            articles = [article for article in articles if article['is_featured']]
        if trending:
            articles = [article for article in articles if article['is_trending']]
        if query:
            articles = [
                article for article in articles
                if query in article['title'].lower()
                or query in article['excerpt'].lower()
                or query in article['content'].lower()
            ]

        return Response({
            'count': len(articles),
            'next': None,
            'previous': None,
            'results': articles,
            'data_source': 'editorial_fallback',
        })


class ArticleDetailView(generics.RetrieveAPIView):
    queryset = Article.objects.select_related(
        'category', 'author'
    ).prefetch_related('tags').filter(status='published')
    serializer_class = ArticleDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'

    def retrieve(self, request, *args, **kwargs):
        try:
            return super().retrieve(request, *args, **kwargs)
        except DatabaseError as exc:
            logger.warning("Article detail API falling back to editorial demo data: %s", exc)
        except (Article.DoesNotExist, Http404):
            pass

        article = demo_article_detail(kwargs.get('slug'))
        if article:
            return Response(article)
        return Response({'error': 'Article not found'}, status=404)


class RelatedArticlesView(generics.ListAPIView):
    serializer_class = ArticleListSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        slug = self.kwargs.get('slug')
        try:
            article = Article.objects.select_related('category').get(
                slug=slug, status='published'
            )
            return Article.objects.select_related(
                'category', 'author'
            ).prefetch_related('tags').filter(
                status='published', category=article.category
            ).exclude(id=article.id)[:4]
        except Article.DoesNotExist:
            return Article.objects.none()

    def list(self, request, *args, **kwargs):
        try:
            response = super().list(request, *args, **kwargs)
            if response.data:
                return response
        except DatabaseError as exc:
            logger.warning("Related articles API falling back to editorial demo data: %s", exc)

        current = demo_article_detail(self.kwargs.get('slug'))
        if not current:
            return Response([])
        related = [
            article for article in demo_articles()
            if article['slug'] != current['slug']
            and article['category']['slug'] == current['category']['slug']
        ][:4]
        return Response(related)


class CommentPagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = 'page_size'
    max_page_size = 100


class CommentListView(generics.ListCreateAPIView):
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]
    pagination_class = CommentPagination

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CommentCreateSerializer
        return CommentSerializer

    def get_queryset(self):
        article_id = self.kwargs.get('article_id')
        return Comment.objects.filter(
            article_id=article_id, is_approved=True
        )

    def perform_create(self, serializer):
        sanitized = {
            'name': strip_tags(serializer.validated_data.get('name', ''))[:100],
            'email': serializer.validated_data.get('email', ''),
            'content': strip_tags(serializer.validated_data.get('content', ''))[:5000],
        }
        if self.request.user.is_authenticated:
            sanitized['name'] = self.request.user.get_full_name() or self.request.user.username
            sanitized['email'] = self.request.user.email
        serializer.save(**sanitized)


@api_view(['GET'])
@permission_classes([AllowAny])
def homepage_data(request):
    from django.db.models import Prefetch

    base_qs = Article.objects.select_related(
        'category', 'author'
    ).prefetch_related('tags').filter(
        status='published', published_at__lte=timezone.now()
    )

    try:
        featured = list(base_qs.filter(is_featured=True)[:5])
        trending = list(base_qs.filter(is_trending=True)[:8])
        latest = list(base_qs[:10])
        categories = list(Category.objects.annotate(
            article_count=Count('articles')
        ).filter(article_count__gt=0).order_by('order', 'name'))

        sections = {}
        for cat in categories:
            cat_articles = [
                a for a in latest + featured + trending
                if a.category_id == cat.id
            ][:5]
            if not cat_articles:
                cat_articles = list(
                    base_qs.filter(category=cat)[:5]
                )
            if cat_articles:
                sections[cat.slug] = {
                    'category': CategorySerializer(cat).data,
                    'articles': ArticleListSerializer(cat_articles, many=True).data,
                }

        payload = {
            'featured': ArticleListSerializer(featured, many=True).data,
            'trending': ArticleListSerializer(trending, many=True).data,
            'latest': ArticleListSerializer(latest, many=True).data,
            'sections': sections,
            'data_source': 'database',
        }
        if payload['featured'] or payload['trending'] or payload['latest'] or payload['sections']:
            return Response(payload)
    except DatabaseError as exc:
        logger.warning("Homepage API falling back to editorial demo data: %s", exc)

    return Response(demo_homepage())


@api_view(['POST'])
@permission_classes([AllowAny])
def newsletter_subscribe(request):
    from .models import NewsletterSubscriber
    from django.core.mail import send_mail
    from django.conf import settings
    import logging
    logger = logging.getLogger(__name__)

    email = request.data.get('email', '').strip()
    name = bleach.clean(request.data.get('name', '').strip(), tags=[], strip=True)
    if not email:
        return Response({'error': 'Email is required'}, status=400)
    sub, created = NewsletterSubscriber.objects.get_or_create(
        email=email, defaults={'name': name, 'is_active': True}
    )
    if not created and not sub.is_active:
        sub.is_active = True
        sub.save(update_fields=['is_active'])

    # Send welcome email
    if created:
        try:
            send_mail(
                subject='Welcome to Factly!',
                message=(
                    f'Hi{ " " + name if name else "" },\n\n'
                    f'Thanks for subscribing to Factly!\n\n'
                    f'You\'ll get the latest tech news, fact-checks, and startup stories delivered to your inbox.\n\n'
                    f'Stay curious,\nThe Factly Team\n'
                    f'{settings.SITE_URL}'
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=True,
            )
        except Exception as e:
            logger.warning(f'Welcome email failed for {email}: {e}')

    return Response({'message': 'Subscribed successfully!'})


@api_view(['POST'])
@permission_classes([AllowAny])
def guest_submit(request):
    serializer = GuestArticleSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)

    ALLOWED_TAGS = ['p', 'br', 'b', 'i', 'strong', 'em', 'ul', 'ol', 'li', 'a', 'blockquote', 'pre', 'code']

    article = Article(
        title=bleach.clean(serializer.validated_data['title'], tags=[], strip=True),
        content=bleach.clean(
            serializer.validated_data['content'],
            tags=ALLOWED_TAGS,
            attributes={'a': ['href', 'title', 'rel']},
            strip=True,
        ),
        excerpt=bleach.clean(
            serializer.validated_data.get('excerpt', '')[:300],
            tags=[], strip=True,
        ),
        status='draft',
        is_imported=True,
        source_name=f'Guest: {bleach.clean(serializer.validated_data["author_name"], tags=[], strip=True)}',
    )
    cat_slug = serializer.validated_data.get('category_slug', '')
    if cat_slug:
        cat = Category.objects.filter(slug=cat_slug).first()
        article.category = cat
    article.save()

    return Response({
        'message': 'Article submitted for review. Thank you!',
        'id': article.id,
    }, status=201)


@api_view(['POST', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def toggle_bookmark(request, article_id):
    from .models import Bookmark
    try:
        article = Article.objects.get(id=article_id, status='published')
    except Article.DoesNotExist:
        return Response({'error': 'Article not found'}, status=404)

    if request.method == 'POST':
        _, created = Bookmark.objects.get_or_create(
            user=request.user, article=article
        )
        return Response({'bookmarked': True, 'created': created})

    Bookmark.objects.filter(user=request.user, article=article).delete()
    return Response({'bookmarked': False})


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def my_bookmarks(request):
    from .models import Bookmark
    bookmarks = Bookmark.objects.filter(user=request.user).select_related('article')
    articles = [b.article for b in bookmarks if b.article.status == 'published']
    return Response({
        'count': len(articles),
        'results': ArticleListSerializer(articles, many=True).data,
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def author_detail(request, author_id):
    from .models import AuthorProfile
    try:
        author = AuthorProfile.objects.get(id=author_id)
    except AuthorProfile.DoesNotExist:
        return Response({'error': 'Author not found'}, status=404)

    articles = Article.objects.select_related(
        'category', 'author'
    ).prefetch_related('tags').filter(
        author=author, status='published',
        published_at__lte=timezone.now()
    ).order_by('-published_at')

    article_count = articles.count()

    return Response({
        'author': AuthorProfileSerializer(author).data,
        'articles': ArticleListSerializer(articles, many=True).data,
        'article_count': article_count,
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def search_articles(request):
    query = request.query_params.get('q', '').strip()
    category = request.query_params.get('category', '').strip()
    date_from = request.query_params.get('date_from', '').strip()
    date_to = request.query_params.get('date_to', '').strip()

    if not query:
        return Response({'results': []})

    try:
        articles = Article.objects.filter(
            status='published', published_at__lte=timezone.now()
        ).filter(
            title__icontains=query
        ) | Article.objects.filter(
            status='published', published_at__lte=timezone.now()
        ).filter(
            content__icontains=query
        ) | Article.objects.filter(
            status='published', published_at__lte=timezone.now()
        ).filter(
            excerpt__icontains=query
        )

        articles = articles.select_related(
            'category', 'author'
        ).prefetch_related('tags').distinct()

        if category:
            articles = articles.filter(category__slug=category)
        if date_from:
            articles = articles.filter(published_at__gte=date_from)
        if date_to:
            articles = articles.filter(published_at__lte=date_to)

        articles = articles.order_by('-published_at')

        limit = min(int(request.query_params.get('limit', 20)), 100)
        offset = max(int(request.query_params.get('offset', 0)), 0)
        total = articles.count()
        page = articles[offset:offset + limit]
        results = ArticleListSerializer(page, many=True).data
        if results:
            return Response({
                'query': query,
                'count': total,
                'limit': limit,
                'offset': offset,
                'results': results,
                'data_source': 'database',
            })
    except DatabaseError as exc:
        logger.warning("Search API falling back to editorial demo data: %s", exc)

    fallback_results = [
        article for article in demo_articles()
        if query.lower() in article['title'].lower()
        or query.lower() in article['excerpt'].lower()
        or query.lower() in article['content'].lower()
    ]
    if category:
        fallback_results = [
            article for article in fallback_results
            if article['category']['slug'] == category
        ]
    return Response({
        'query': query,
        'count': len(fallback_results),
        'results': fallback_results,
        'data_source': 'editorial_fallback',
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def search_suggestions(request):
    query = request.query_params.get('q', '').strip()
    if not query or len(query) < 2:
        return Response({'suggestions': []})

    try:
        articles = Article.objects.select_related('category').filter(
            status='published', published_at__lte=timezone.now(),
            title__icontains=query,
        ).order_by('-published_at')[:6]
        suggestions = [
            {'id': a.id, 'title': a.title, 'slug': a.slug, 'category': a.category.slug if a.category else ''}
            for a in articles
        ]
        if suggestions:
            return Response({'suggestions': suggestions})
    except DatabaseError as exc:
        logger.warning("Search suggestions falling back to editorial demo data: %s", exc)

    suggestions = [
        {
            'id': article['id'],
            'title': article['title'],
            'slug': article['slug'],
            'category': article['category']['slug'],
        }
        for article in demo_articles()
        if query.lower() in article['title'].lower()
    ][:6]
    return Response({'suggestions': suggestions, 'data_source': 'editorial_fallback'})
