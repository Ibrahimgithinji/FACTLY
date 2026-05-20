from django.contrib import admin
from .models import Category, Tag, AuthorProfile, Article, Comment, FeedSource, NewsletterSubscriber, Bookmark


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
