from django.urls import path
from . import views

urlpatterns = [
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    path('articles/', views.ArticleListView.as_view(), name='article-list'),
    path('articles/<slug:slug>/', views.ArticleDetailView.as_view(), name='article-detail'),
    path('articles/<slug:slug>/related/', views.RelatedArticlesView.as_view(), name='article-related'),
    path('articles/<int:article_id>/comments/', views.CommentListView.as_view(), name='article-comments'),
    path('homepage/', views.homepage_data, name='homepage-data'),
    path('search/', views.search_articles, name='article-search'),
    path('guest-submit/', views.guest_submit, name='guest-submit'),
    path('newsletter/', views.newsletter_subscribe, name='newsletter-subscribe'),
    path('bookmarks/', views.my_bookmarks, name='my-bookmarks'),
    path('bookmarks/<int:article_id>/', views.toggle_bookmark, name='toggle-bookmark'),
    path('authors/<int:author_id>/', views.author_detail, name='author-detail'),
]
