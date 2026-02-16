from django.urls import path
from . import views, auth_views
# from . import fast_views  # Disabled temporarily - requires additional dependencies

app_name = 'verification'

urlpatterns = [
    # Authentication endpoints
    path('auth/login/', auth_views.LoginView.as_view(), name='login'),
    path('auth/signup/', auth_views.SignupView.as_view(), name='signup'),
    path('auth/refresh/', auth_views.RefreshTokenView.as_view(), name='refresh'),
    path('auth/forgot-password/', auth_views.ForgotPasswordView.as_view(), name='forgot_password'),
    path('auth/verify-reset-token/', auth_views.VerifyResetTokenView.as_view(), name='verify_reset_token'),
    path('auth/reset-password/', auth_views.ResetPasswordView.as_view(), name='reset_password'),
    path('auth/get-reset-link/', auth_views.GetResetLinkView.as_view(), name='get_reset_link'),  # Development only
    
    # Standard verification endpoints
    path('verify/', views.VerificationView.as_view(), name='verify'),
    path('verify/enhanced/', views.EnhancedVerificationView.as_view(), name='verify_enhanced'),
    path('health/', views.health_check, name='health_check'),
    
    # Fast verification endpoints (async, optimized)
    # path('verify/fast/', fast_views.FastVerificationView.as_view(), name='verify_fast'),
    # path('verify/batch/', fast_views.BatchFastVerificationView.as_view(), name='verify_batch'),
    # path('verify/stats/', fast_views.fast_verification_stats, name='verify_stats'),
    # path('verify/cache/clear/', fast_views.clear_cache, name='clear_cache'),
]