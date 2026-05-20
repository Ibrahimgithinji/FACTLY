from django.db.models import Count
from rest_framework import generics, permissions, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from django.utils import timezone
from .models import Category, Tag, Article, Comment
from .serializers import (
    CategorySerializer, TagSerializer, ArticleListSerializer,
    ArticleDetailSerializer, CommentSerializer, CommentCreateSerializer,
    GuestArticleSerializer,
)


class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]


class ArticleListView(generics.ListAPIView):
    serializer_class = ArticleListSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'excerpt', 'content']
    ordering_fields = ['published_at', 'title']
    ordering = ['-published_at']

    def get_queryset(self):
        queryset = Article.objects.filter(
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


class ArticleDetailView(generics.RetrieveAPIView):
    queryset = Article.objects.filter(status='published')
    serializer_class = ArticleDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'


class RelatedArticlesView(generics.ListAPIView):
    serializer_class = ArticleListSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        slug = self.kwargs.get('slug')
        try:
            article = Article.objects.get(slug=slug, status='published')
            return Article.objects.filter(
                status='published', category=article.category
            ).exclude(id=article.id)[:4]
        except Article.DoesNotExist:
            return Article.objects.none()


class CommentListView(generics.ListCreateAPIView):
    permission_classes = [AllowAny]

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
        serializer.save()


@api_view(['GET'])
@permission_classes([AllowAny])
def homepage_data(request):
    featured = Article.objects.filter(
        status='published', is_featured=True,
        published_at__lte=timezone.now()
    )[:5]
    trending = Article.objects.filter(
        status='published', is_trending=True,
        published_at__lte=timezone.now()
    )[:8]
    latest = Article.objects.filter(
        status='published', published_at__lte=timezone.now()
    )[:10]
    categories = Category.objects.annotate(
        article_count=Count('articles')
    ).filter(article_count__gt=0).order_by('order', 'name')

    sections = {}
    for cat in categories:
        cat_articles = Article.objects.filter(
            status='published', category=cat,
            published_at__lte=timezone.now()
        )[:5]
        if cat_articles:
            sections[cat.slug] = {
                'category': CategorySerializer(cat).data,
                'articles': ArticleListSerializer(cat_articles, many=True).data,
            }

    return Response({
        'featured': ArticleListSerializer(featured, many=True).data,
        'trending': ArticleListSerializer(trending, many=True).data,
        'latest': ArticleListSerializer(latest, many=True).data,
        'sections': sections,
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def guest_submit(request):
    serializer = GuestArticleSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)

    article = Article(
        title=serializer.validated_data['title'],
        content=serializer.validated_data['content'],
        excerpt=serializer.validated_data.get('excerpt', '')[:300],
        status='draft',
        is_imported=True,
        source_name=f'Guest: {serializer.validated_data["author_name"]}',
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


@api_view(['GET'])
@permission_classes([AllowAny])
def search_articles(request):
    query = request.query_params.get('q', '').strip()
    if not query:
        return Response({'results': []})

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

    articles = articles.distinct().order_by('-published_at')[:20]

    return Response({
        'query': query,
        'count': articles.count(),
        'results': ArticleListSerializer(articles, many=True).data,
    })
