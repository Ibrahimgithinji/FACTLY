from django.contrib import admin
from .models import (
    Article, AuthorProfile, Bookmark, Category, Comment, DailyStoryEdition, DailyStoryEditionStatus, FeedSource,
    NewsletterSubscriber, Story, StoryEvent, StoryStatus, Tag,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'order', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(AuthorProfile)
class AuthorProfileAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'user', 'position')
    search_fields = ('display_name', 'user__username')


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'author', 'status', 'is_featured', 'published_at')
    list_filter = ('status', 'category', 'is_featured', 'is_trending')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'content')
    date_hierarchy = 'published_at'
    filter_horizontal = ('tags',)


class StoryEventInline(admin.TabularInline):
    model = StoryEvent
    extra = 1
    fields = (
        'position', 'occurred_at', 'title', 'summary', 'source_name', 'source_url',
        'source_published_at', 'source_article', 'is_verified',
    )
    ordering = ('position',)
    autocomplete_fields = ('source_article',)


@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'category', 'started_at', 'updated_at')
    list_filter = ('status', 'category')
    search_fields = ('title', 'summary', 'current_status')
    prepopulated_fields = {'slug': ('title',)}
    list_select_related = ('category',)
    inlines = (StoryEventInline,)


@admin.register(DailyStoryEdition)
class DailyStoryEditionAdmin(admin.ModelAdmin):
    list_display = ('edition_date', 'story', 'status', 'selection_type', 'published_at', 'corrected_at')
    list_filter = ('status', 'selection_type')
    search_fields = ('story__title', 'selection_reason', 'correction_reason')
    date_hierarchy = 'edition_date'
    list_select_related = ('story',)
    autocomplete_fields = ('story',)
    readonly_fields = ('published_at', 'corrected_at')
    actions = ['publish_selected']

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.status == DailyStoryEditionStatus.PUBLISHED:
            return self.readonly_fields + ('edition_date', 'story', 'selection_type', 'selection_reason')
        return self.readonly_fields

    @admin.action(description='Publish selected scheduled editions')
    def publish_selected(self, request, queryset):
        for edition in queryset.filter(status=DailyStoryEditionStatus.SCHEDULED):
            if edition.story and edition.story.status == StoryStatus.PUBLISHED:
                edition.status = DailyStoryEditionStatus.PUBLISHED
                edition.save()
                self.message_user(request, f'Published edition for {edition.edition_date}.')
            else:
                self.message_user(request, f'Cannot publish edition for {edition.edition_date}: story is not published.', level='warning')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'article', 'is_approved', 'created_at')
    list_filter = ('is_approved',)
    search_fields = ('name', 'email', 'content')


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('email', 'name')


@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ('user', 'article', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'article__title')


@admin.register(FeedSource)
class FeedSourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'feed_url', 'category', 'is_active', 'last_imported_at')
    list_filter = ('is_active', 'category')
    search_fields = ('name', 'feed_url')
    actions = ['import_selected']

    @admin.action(description='Import articles from selected feeds')
    def import_selected(self, request, queryset):
        from .management.commands.import_rss import import_feed
        count = 0
        for source in queryset.filter(is_active=True):
            count += import_feed(source)
        self.message_user(request, f'Imported {count} new articles.')
