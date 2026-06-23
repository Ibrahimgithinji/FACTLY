from rest_framework import serializers
from .models import Category, Tag, AuthorProfile, Article, Comment


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'icon', 'order']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']


class AuthorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthorProfile
        fields = ['id', 'display_name', 'bio', 'avatar', 'position', 'twitter', 'linkedin', 'website']


class ArticleListSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    author = AuthorProfileSerializer(read_only=True)

    class Meta:
        model = Article
        fields = [
            'id', 'title', 'slug', 'excerpt', 'featured_image',
            'category', 'tags', 'author', 'is_featured', 'is_trending',
            'read_time', 'published_at',
        ]


class ArticleDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    author = AuthorProfileSerializer(read_only=True)

    class Meta:
        model = Article
        fields = [
            'id', 'title', 'slug', 'excerpt', 'content', 'featured_image',
            'category', 'tags', 'author', 'is_featured', 'is_trending',
            'read_time', 'published_at', 'created_at', 'updated_at',
        ]


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'article', 'name', 'email', 'content', 'is_approved', 'created_at']
        read_only_fields = ['is_approved']


class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['article', 'name', 'email', 'content']
        extra_kwargs = {
            'name': {'max_length': 100},
            'content': {'max_length': 5000},
        }


class GuestArticleSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=300)
    content = serializers.CharField()
    excerpt = serializers.CharField(required=False, allow_blank=True)
    category_slug = serializers.CharField(required=False, allow_blank=True)
    author_name = serializers.CharField(max_length=100)
    author_email = serializers.EmailField()

    def validate_title(self, value):
        if Article.objects.filter(title__iexact=value).exists():
            raise serializers.ValidationError('An article with this title already exists.')
        return value
