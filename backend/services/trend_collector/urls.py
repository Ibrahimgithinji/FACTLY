"""
URL Configuration for Trend Discovery and Misinformation Detection

Routes:
- /api/trends - List and manage trends
- /api/claims - List extracted claims
- /api/misinformation-risk - Get risk scores
- /api/predictions - Get trend predictions
- /api/trends/collect - Trigger collection
- /api/alerts - Get active alerts
- /api/analytics - Get analytics
"""

from django.urls import path
from . import views

app_name = 'trend_collector'

urlpatterns = [
    # Trend endpoints
    path('trends/', views.TrendListAPIView.as_view(), name='trend_list'),
    path('trends/<int:trend_id>/', views.TrendDetailAPIView.as_view(), name='trend_detail'),
    path('trends/collect/', views.TriggerCollectionAPIView.as_view(), name='trend_collect'),
    
    # Claims
    path('claims/', views.ClaimListAPIView.as_view(), name='claim_list'),
    
    # Risk assessment
    path('misinformation-risk/', views.MisinformationRiskAPIView.as_view(), name='misinformation_risk'),
    
    # Predictions
    path('predictions/', views.PredictionAPIView.as_view(), name='predictions'),
    
    # Alerts
    path('alerts/', views.AlertsAPIView.as_view(), name='alerts'),
    
    # Analytics
    path('analytics/', views.AnalyticsAPIView.as_view(), name='analytics'),
]
