"""
REST API Views for Trend Discovery and Misinformation Detection

Endpoints:
- /api/trends - List and manage trends
- /api/claims - List extracted claims
- /api/misinformation-risk - Get risk scores
- /api/predictions - Get trend predictions
"""

import logging
from datetime import datetime, timedelta
from typing import Optional

from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.db.models import Q, Count, Avg
from django.utils import timezone

from .models import (
    Trend, Claim, TrendPrediction, 
    TrendSource, MisinformationAlert
)
from .trend_aggregator import TrendAggregatorService, collect_trends_task
from .analysis_engine import (
    TrendNormalizer, ClaimExtractor,
    MisinformationDetector, TrendRanker,
    TrendPredictor, MetricsCollector
)
from services.fact_checking_service.cache_manager import CacheManager

logger = logging.getLogger(__name__)


class TrendListAPIView(APIView):
    """
    GET /api/trends
    
    List trends with filtering and pagination.
    
    Query Parameters:
    - region: Filter by region (africa, india, us, europe, global)
    - risk_level: Filter by risk level (low, medium, high, critical)
    - verification_status: Filter by verification status
    - limit: Number of results (default 50)
    - offset: Pagination offset (default 0)
    """
    permission_classes = [AllowAny]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cache = CacheManager()
    
    def get(self, request):
        """Get list of trends with optional filtering."""
        
        # Get query parameters
        region = request.query_params.get('region')
        risk_level = request.query_params.get('risk_level')
        verification_status = request.query_params.get('verification_status')
        limit = int(request.query_params.get('limit', 50))
        offset = int(request.query_params.get('offset', 0))
        
        # Build query
        queryset = Trend.objects.filter(is_active=True)
        
        if region:
            queryset = queryset.filter(primary_region=region)
        
        if risk_level:
            queryset = queryset.filter(risk_level=risk_level)
        
        if verification_status:
            queryset = queryset.filter(verification_status=verification_status)
        
        # Order by priority score
        queryset = queryset.order_by('-priority_score', '-engagement_score')
        
        # Paginate
        total = queryset.count()
        trends = queryset[offset:offset + limit]
        
        # Serialize
        results = []
        for trend in trends:
            results.append({
                'id': trend.id,
                'topic': trend.topic,
                'keywords': trend.keywords,
                'source_platforms': trend.source_platforms,
                'engagement_score': trend.engagement_score,
                'engagement_velocity': trend.engagement_velocity,
                'risk_level': trend.risk_level,
                'misinformation_risk_score': trend.misinformation_risk_score,
                'priority_score': trend.priority_score,
                'verification_status': trend.verification_status,
                'factly_score': trend.factly_score,
                'primary_region': trend.primary_region,
                'predicted_trend_score': trend.predicted_trend_score,
                'first_detected': trend.first_detected.isoformat() if trend.first_detected else None,
                'last_updated': trend.last_updated.isoformat() if trend.last_updated else None,
            })
        
        return Response({
            'count': total,
            'limit': limit,
            'offset': offset,
            'results': results
        })


class TrendDetailAPIView(APIView):
    """
    GET /api/trends/{id}
    
    Get detailed information about a specific trend.
    """
    permission_classes = [AllowAny]
    
    def get(self, request, trend_id):
        """Get trend details."""
        try:
            trend = Trend.objects.get(id=trend_id, is_active=True)
            
            # Get associated claims
            claims = trend.claims.all()
            
            # Get predictions
            predictions = trend.predictions.all()
            
            return Response({
                'id': trend.id,
                'topic': trend.topic,
                'keywords': trend.keywords,
                'summary': trend.summary,
                'source_platforms': trend.source_platforms,
                'source_count': trend.source_count,
                'engagement_score': trend.engagement_score,
                'engagement_velocity': trend.engagement_velocity,
                'mention_volume': trend.mention_volume,
                'share_count': trend.share_count,
                'comment_count': trend.comment_count,
                'view_count': trend.view_count,
                'primary_region': trend.primary_region,
                'detected_regions': trend.detected_regions,
                'risk_level': trend.risk_level,
                'misinformation_risk_score': trend.misinformation_risk_score,
                'priority_score': trend.priority_score,
                'verification_status': trend.verification_status,
                'factly_score': trend.factly_score,
                'verification_summary': trend.verification_summary,
                'predicted_trend_score': trend.predicted_trend_score,
                'prediction_confidence': trend.prediction_confidence,
                'first_detected': trend.first_detected.isoformat() if trend.first_detected else None,
                'last_updated': trend.last_updated.isoformat() if trend.last_updated else None,
                'claims': [
                    {
                        'id': c.id,
                        'text': c.claim_text,
                        'category': c.category,
                        'emotional_language_score': c.emotional_language_score,
                        'sensationalist_score': c.sensationalist_score,
                    }
                    for c in claims
                ],
                'predictions': [
                    {
                        'id': p.id,
                        'predicted_engagement_24h': p.predicted_engagement_24h,
                        'predicted_engagement_48h': p.predicted_engagement_48h,
                        'confidence_score': p.confidence_score,
                        'trajectory': p.sentiment_trajectory,
                    }
                    for p in predictions
                ]
            })
            
        except Trend.DoesNotExist:
            return Response(
                {'error': 'Trend not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class ClaimListAPIView(APIView):
    """
    GET /api/claims
    
    List extracted claims with filtering.
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Get list of claims."""
        
        category = request.query_params.get('category')
        limit = int(request.query_params.get('limit', 50))
        offset = int(request.query_params.get('offset', 0))
        
        queryset = Claim.objects.all()
        
        if category:
            queryset = queryset.filter(category=category)
        
        total = queryset.count()
        claims = queryset[offset:offset + limit]
        
        return Response({
            'count': total,
            'limit': limit,
            'offset': offset,
            'results': [
                {
                    'id': c.id,
                    'claim_text': c.claim_text,
                    'category': c.category,
                    'sentiment': c.sentiment,
                    'emotional_language_score': c.emotional_language_score,
                    'sensationalist_score': c.sensationalist_score,
                    'source_credibility_score': c.source_credibility_score,
                    'matches_known_false_claim': c.matches_known_false_claim,
                    'created_at': c.created_at.isoformat() if c.created_at else None,
                }
                for c in claims
            ]
        })


class MisinformationRiskAPIView(APIView):
    """
    GET /api/misinformation-risk
    
    Get misinformation risk assessment for trends.
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Get risk scores for all or specific trends."""
        
        trend_id = request.query_params.get('trend_id')
        limit = int(request.query_params.get('limit', 10))
        
        if trend_id:
            try:
                trend = Trend.objects.get(id=trend_id, is_active=True)
                return Response({
                    'trend_id': trend.id,
                    'topic': trend.topic,
                    'risk_level': trend.risk_level,
                    'misinformation_risk_score': trend.misinformation_risk_score,
                    'virality_score': trend.engagement_score,
                    'priority_score': trend.priority_score,
                    'requires_verification': trend.misinformation_risk_score > 50,
                })
            except Trend.DoesNotExist:
                return Response(
                    {'error': 'Trend not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        # Get highest risk trends
        high_risk = Trend.objects.filter(
            is_active=True,
            misinformation_risk_score__gte=50
        ).order_by('-misinformation_risk_score')[:limit]
        
        return Response({
            'count': high_risk.count(),
            'results': [
                {
                    'trend_id': t.id,
                    'topic': t.topic,
                    'risk_level': t.risk_level,
                    'misinformation_risk_score': t.misinformation_risk_score,
                    'priority_score': t.priority_score,
                }
                for t in high_risk
            ]
        })


class PredictionAPIView(APIView):
    """
    GET /api/predictions
    
    Get AI predictions for trending topics.
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Get trend predictions."""
        
        trend_id = request.query_params.get('trend_id')
        
        if trend_id:
            try:
                predictions = TrendPrediction.objects.filter(trend_id=trend_id)
                return Response({
                    'trend_id': trend_id,
                    'predictions': [
                        {
                            'predicted_engagement_24h': p.predicted_engagement_24h,
                            'predicted_engagement_48h': p.predicted_engagement_48h,
                            'confidence_score': p.confidence_score,
                            'engagement_acceleration': p.engagement_acceleration,
                            'cross_platform_emergence_score': p.cross_platform_emergence_score,
                            'influencer_amplification_score': p.influencer_amplification_score,
                            'sentiment_trajectory': p.sentiment_trajectory,
                            'created_at': p.created_at.isoformat() if p.created_at else None,
                        }
                        for p in predictions
                    ]
                })
            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        # Get top predictions
        top_predictions = TrendPrediction.objects.order_by(
            '-confidence_score', '-predicted_engagement_48h'
        )[:20]
        
        return Response({
            'count': top_predictions.count(),
            'results': [
                {
                    'trend_id': p.trend_id,
                    'topic': p.trend.topic[:100],
                    'predicted_engagement_24h': p.predicted_engagement_24h,
                    'predicted_engagement_48h': p.predicted_engagement_48h,
                    'confidence_score': p.confidence_score,
                    'will_trend': p.predicted_engagement_24h > 50 or p.predicted_engagement_48h > 80,
                }
                for p in top_predictions
            ]
        })


class TriggerCollectionAPIView(APIView):
    """
    POST /api/trends/collect
    
    Manually trigger trend collection from all sources.
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Trigger trend collection."""
        regions = request.data.get('regions', ['global', 'africa', 'us', 'europe'])
        
        try:
            # Run collection task
            result = collect_trends_task(regions)
            
            return Response({
                'status': 'success',
                'collected': result.get('total_collected', 0),
                'sources_status': result.get('sources_status', {}),
                'success_rate': result.get('success_rate', 0),
                'timestamp': result.get('collection_time'),
            })
            
        except Exception as e:
            logger.error(f"Trend collection failed: {e}")
            return Response(
                {'error': f'Collection failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AlertsAPIView(APIView):
    """
    GET /api/alerts
    
    Get active misinformation alerts.
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Get active alerts."""
        
        priority = request.query_params.get('priority')
        
        queryset = MisinformationAlert.objects.filter(status='active')
        
        if priority:
            queryset = queryset.filter(priority=priority)
        
        alerts = queryset[:50]
        
        return Response({
            'count': alerts.count(),
            'results': [
                {
                    'id': a.id,
                    'trend_id': a.trend_id,
                    'topic': a.trend.topic[:100],
                    'priority': a.priority,
                    'alert_message': a.alert_message,
                    'triggers': a.triggers,
                    'created_at': a.created_at.isoformat() if a.created_at else None,
                }
                for a in alerts
            ]
        })


class AnalyticsAPIView(APIView):
    """
    GET /api/analytics
    
    Get analytics and statistics.
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Get trend analytics."""
        
        # Get counts
        total_trends = Trend.objects.filter(is_active=True).count()
        high_risk = Trend.objects.filter(
            is_active=True, 
            risk_level__in=['high', 'critical']
        ).count()
        
        pending_verification = Trend.objects.filter(
            is_active=True,
            verification_status='pending',
            misinformation_risk_score__gte=50
        ).count()
        
        verified = Trend.objects.filter(
            is_active=True,
            verification_status__in=['verified', 'false', 'true']
        ).count()
        
        # Get average scores
        avg_risk = Trend.objects.filter(is_active=True).aggregate(
            avg=Avg('misinformation_risk_score')
        )['avg'] or 0
        
        avg_engagement = Trend.objects.filter(is_active=True).aggregate(
            avg=Avg('engagement_score')
        )['avg'] or 0
        
        # Get recent alerts
        recent_alerts = MisinformationAlert.objects.filter(
            status='active'
        ).count()
        
        return Response({
            'total_trends': total_trends,
            'high_risk_trends': high_risk,
            'pending_verification': pending_verification,
            'verified_claims': verified,
            'average_risk_score': round(avg_risk, 2),
            'average_engagement': round(avg_engagement, 2),
            'active_alerts': recent_alerts,
            'timestamp': timezone.now().isoformat()
        })
