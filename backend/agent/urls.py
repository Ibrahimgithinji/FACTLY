from django.urls import path
from . import views

app_name = "agent"

urlpatterns = [
    path("agent/chat/", views.ChatView.as_view(), name="chat"),
    path("agent/digest/", views.DigestView.as_view(), name="digest"),
    path("agent/trending/", views.TrendingView.as_view(), name="trending"),
]
