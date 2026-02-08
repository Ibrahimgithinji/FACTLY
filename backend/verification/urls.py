from django.urls import path
from . import views
from . import fast_views

app_name = 'verification'

urlpatterns = [
    # Standard verification endpoints
    path('verify/', views.VerificationView.as_view(), name='verify'),
    path('verify/enhanced/', views.EnhancedVerificationView.as_view(), name='verify_enhanced'),
    path('health/', views.health_check, name='health_check'),
    
    # Fast verification endpoints (async, optimized)
    path('verify/fast/', fast_views.FastVerificationView.as_view(), name='verify_fast'),
    path('verify/batch/', fast_views.BatchFastVerificationView.as_view(), name='verify_batch'),
    path('verify/stats/', fast_views.fast_verification_stats, name='verify_stats'),
    path('verify/cache/clear/', fast_views.clear_cache, name='clear_cache'),
]