import logging
from django.conf import settings
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


class ArticleStatus(models.TextChoices):
    DRAFT = 'draft', 'Draft'
    PUBLISHED = 'published', 'Published'


class StoryStatus(models.TextChoices):
    DRAFT = 'draft', 'Draft'
    PUBLISHED = 'published', 'Published'


class DailyStoryEditionStatus(models.TextChoices):
    DRAFT = 'draft', 'Draft'
    SCHEDULED = 'scheduled', 'Scheduled'
    PUBLISHED = 'published', 'Published'
    FALLBACK = 'fallback', 'Fallback'


class DailyStorySelectionType(models.TextChoices):
    EDITORIAL = 'editorial', 'Editorial'
    AUTOMATIC = 'automatic', 'Automatic'


class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)

    def all_with_deleted(self):
        return super().get_queryset()

    def deleted_only(self):
        return super().get_queryset().filter(deleted_at__isnull=False)


class Article(models.Model):
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
    status = models.CharField(
        max_length=10,
        choices=ArticleStatus.choices,
        default=ArticleStatus.DRAFT,
    )
    source_url = models.URLField(blank=True, null=True, default=None, help_text='Original URL if imported from RSS')
    source_name = models.CharField(max_length=200, blank=True, help_text='Source attribution name')
    is_imported = models.BooleanField(default=False, help_text='Auto-imported from RSS feed')
    is_featured = models.BooleanField(default=False)
    is_trending = models.BooleanField(default=False)
    read_time = models.IntegerField(default=1, help_text='Estimated read time in minutes')
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = SoftDeleteManager()

    class Meta:
        ordering = ['-published_at', '-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if self.status == ArticleStatus.PUBLISHED and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    def soft_delete(self):
        self.deleted_at = timezone.now()
        self.save(update_fields=['deleted_at'])

    def restore(self):
        self.deleted_at = None
        self.save(update_fields=['deleted_at'])


class Story(models.Model):
    """A durable, source-backed account of an event that develops over time."""

    title = models.CharField(max_length=300)
    slug = models.SlugField(max_length=350, unique=True, blank=True)
    summary = models.TextField()
    current_status = models.TextField(blank=True)
    featured_image = models.URLField(blank=True)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='stories'
    )
    status = models.CharField(
        max_length=10,
        choices=StoryStatus.choices,
        default=StoryStatus.DRAFT,
    )
    started_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at', '-created_at']
        verbose_name_plural = 'stories'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class StoryEvent(models.Model):
    """A chronological event within a story, with durable source attribution."""

    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='events')
    position = models.PositiveIntegerField(help_text='Order in the reader timeline, starting at 1')
    occurred_at = models.DateTimeField()
    title = models.CharField(max_length=300)
    summary = models.TextField()
    source_url = models.URLField()
    source_name = models.CharField(max_length=200)
    source_published_at = models.DateTimeField(null=True, blank=True)
    source_article = models.ForeignKey(
        Article, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='story_events'
    )
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['position', 'occurred_at', 'id']
        constraints = [
            models.UniqueConstraint(
                fields=['story', 'position'],
                name='content_unique_story_event_position',
            ),
        ]

    def __str__(self):
        return f'{self.story.title}: {self.position}. {self.title}'

    def clean(self):
        if not self.source_url:
            raise ValueError('StoryEvent requires an attributable source_url.')
        if not self.source_name:
            raise ValueError('StoryEvent requires an attributable source_name.')


class DailyStoryEdition(models.Model):
    """An editor-approved story assigned to a single local editorial date."""

    edition_date = models.DateField()
    story = models.ForeignKey(Story, on_delete=models.PROTECT, related_name='daily_editions')
    status = models.CharField(
        max_length=10,
        choices=DailyStoryEditionStatus.choices,
        default=DailyStoryEditionStatus.DRAFT,
    )
    selection_type = models.CharField(
        max_length=10,
        choices=DailyStorySelectionType.choices,
        default=DailyStorySelectionType.EDITORIAL,
    )
    selection_reason = models.TextField(blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    corrected_at = models.DateTimeField(null=True, blank=True)
    correction_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-edition_date']
        constraints = [
            models.UniqueConstraint(
                fields=['edition_date'],
                name='content_unique_daily_story_edition_date',
            ),
        ]

    def __str__(self):
        return f'{self.edition_date}: {self.story.title}'

    def save(self, *args, **kwargs):
        if self.pk and self.status == DailyStoryEditionStatus.PUBLISHED:
            existing = DailyStoryEdition.objects.get(pk=self.pk)
            if existing.status == DailyStoryEditionStatus.PUBLISHED:
                raise ValueError('Published daily editions are immutable.')
        if self.status == DailyStoryEditionStatus.PUBLISHED and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    def record_correction(self, reason):
        self.correction_reason = reason
        self.corrected_at = timezone.now()
        self.save(update_fields=['correction_reason', 'corrected_at'])


class PageView(models.Model):
    article = models.ForeignKey(
        Article, on_delete=models.CASCADE,
        null=True, blank=True, default=None,
        related_name='page_views'
    )
    path = models.CharField(max_length=500, db_index=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, default='')
    viewed_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        ordering = ['-viewed_at']

    def __str__(self):
        return f'{self.path} @ {self.viewed_at}'


class PushSubscription(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        null=True, blank=True, default=None
    )
    endpoint = models.URLField(max_length=500, unique=True)
    p256dh_key = models.TextField()
    auth_key = models.TextField()
    user_agent = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Push sub for {self.user or "anonymous"} - {self.endpoint[:50]}'


class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Newsletter Subscriber'
        verbose_name_plural = 'Newsletter Subscribers'
        ordering = ['-created_at']

    def __str__(self):
        return self.email


class Bookmark(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='bookmarks'
    )
    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name='bookmarks'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'article']
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} → {self.article.title[:50]}'


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
