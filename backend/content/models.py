import logging
from django.contrib.auth.models import User
from django.db import models
from django.utils.text import slugify
from django.utils import timezone

logger = logging.getLogger(__name__)


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=10, blank=True, help_text='Emoji or icon character')
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'categories'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class AuthorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='author_profile')
    display_name = models.CharField(max_length=100)
    bio = models.TextField(blank=True)
    avatar = models.URLField(blank=True)
    position = models.CharField(max_length=200, blank=True, help_text='e.g. The Analyst')
    twitter = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    website = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Author Profile'
        verbose_name_plural = 'Author Profiles'

    def __str__(self):
        return self.display_name


class Article(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]

    title = models.CharField(max_length=300)
    slug = models.SlugField(max_length=350, unique=True, blank=True)
    excerpt = models.TextField(blank=True)
    content = models.TextField()
    featured_image = models.URLField(blank=True)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='articles'
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name='articles')
    author = models.ForeignKey(
        AuthorProfile, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='articles'
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    source_url = models.URLField(blank=True, null=True, default=None, help_text='Original URL if imported from RSS')
    source_name = models.CharField(max_length=200, blank=True, help_text='Source attribution name')
    is_imported = models.BooleanField(default=False, help_text='Auto-imported from RSS feed')
    is_featured = models.BooleanField(default=False)
    is_trending = models.BooleanField(default=False)
    read_time = models.IntegerField(default=1, help_text='Estimated read time in minutes')
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-published_at', '-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)


class FeedSource(models.Model):
    name = models.CharField(max_length=200)
    feed_url = models.URLField(unique=True, help_text='RSS or Atom feed URL')
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True,
        help_text='Default category for imported articles'
    )
    is_active = models.BooleanField(default=True)
    import_interval = models.IntegerField(
        default=60, help_text='Minutes between import attempts'
    )
    last_imported_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Feed Source'
        verbose_name_plural = 'Feed Sources'
        ordering = ['name']

    def __str__(self):
        return self.name


class Comment(models.Model):
    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name='comments'
    )
    name = models.CharField(max_length=100)
    email = models.EmailField()
    content = models.TextField()
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Comment by {self.name} on {self.article.title}'
