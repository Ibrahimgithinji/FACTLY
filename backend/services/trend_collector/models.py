"""
Database Models for Trend Discovery and Misinformation Detection

Defines PostgreSQL schema for storing trends, claims, and misinformation risk data.
"""

from django.db import models
from django.contrib.postgres.indexes import GinIndex, BrinIndex
from django.contrib.postgres.fields import ArrayField, JSONField
from django.utils import timezone


class TrendSource(models.Model):
    """Source platforms for trend collection."""
    
    PLATFORM_CHOICES = [
        ('twitter', 'Twitter/X'),
        ('reddit', 'Reddit'),
        ('tiktok', 'TikTok'),
        ('google_trends', 'Google Trends'),
        ('bing_trends', 'Bing Trends'),
        ('news_api', 'News API'),
        ('rss', 'RSS Feed'),
        ('custom', 'Custom Source'),
    ]
    
    REGION_CHOICES = [
        ('global', 'Global'),
        ('africa', 'Africa'),
        ('india', 'India'),
        ('us', 'United States'),
        ('europe', 'Europe'),
        ('asia', 'Asia'),
        ('latin_america', 'Latin America'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    region = models.CharField(max_length=20, choices=REGION_CHOICES, default='global')
    api_endpoint = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    rate_limit_per_minute = models.IntegerField(default=60)
    last_fetched = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'trend_sources'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.platform})"


class Trend(models.Model):
    """Main trend/claim model storing aggregated trends from multiple sources."""
    
    RISK_LEVEL_CHOICES = [
        ('low', 'Low Risk'),
        ('medium', 'Medium Risk'),
        ('high', 'High Risk'),
        ('critical', 'Critical Risk'),
    ]
    
    VERIFICATION_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('verified', 'Verified'),
        ('false', 'False Claim'),
        ('true', 'True Claim'),
        ('unverifiable', 'Unverifiable'),
    ]
    
    # Core fields
    topic = models.CharField(max_length=500, db_index=True)
    keywords = ArrayField(models.CharField(max_length=100), default=list)
    summary = models.TextField(blank=True)
    
    # Source information
    source_platforms = ArrayField(models.CharField(max_length=20), default=list)
    source_count = models.IntegerField(default=1)
    
    # Engagement metrics
    engagement_score = models.FloatField(default=0.0, db_index=True)
    engagement_velocity = models.FloatField(default=0.0)  # Engagement per hour
    mention_volume = models.IntegerField(default=0)
    share_count = models.IntegerField(default=0)
    comment_count = models.IntegerField(default=0)
    view_count = models.BigIntegerField(default=0)
    
    # Region and time
    primary_region = models.CharField(max_length=20, default='global')
    detected_regions = ArrayField(models.CharField(max_length=20), default=list)
    first_detected = models.DateTimeField(default=timezone.now)
    last_updated = models.DateTimeField(default=timezone.now)
    
    # Risk assessment
    risk_level = models.CharField(max_length=10, choices=RISK_LEVEL_CHOICES, default='low')
    misinformation_risk_score = models.FloatField(default=0.0, db_index=True)  # 0-100
    
    # AI/ML predictions
    predicted_trend_score = models.FloatField(default=0.0)  # Predicted 24-48h score
    prediction_confidence = models.FloatField(default=0.0)
    prediction_horizon_hours = models.IntegerField(default=24)
    
    # Verification
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_STATUS_CHOICES, default='pending')
    factly_score = models.IntegerField(null=True, blank=True)  # 0-100
    verification_summary = models.TextField(blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    metadata = JSONField(default=dict)
    is_active = models.BooleanField(default=True)
    priority_score = models.FloatField(default=0.0, db_index=True)  # virality × risk
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'trends'
        ordering = ['-priority_score', '-engagement_score']
        indexes = [
            GinIndex(fields=['keywords'], name='trend_keywords_gin'),
            BrinIndex(fields=['created_at'], name='trend_created_brin'),
            models.Index(fields=['risk_level', '-priority_score']),
            models.Index(fields=['verification_status', '-misinformation_risk_score']),
        ]
    
    def __str__(self):
        return f"{self.topic[:50]}... (Risk: {self.risk_level})"
    
    def calculate_priority_score(self):
        """Calculate priority score: virality × misinformation risk."""
        self.priority_score = self.engagement_score * (self.misinformation_risk_score / 100)
        return self.priority_score


class Claim(models.Model):
    """Extracted factual claims from trends."""
    
    CATEGORY_CHOICES = [
        ('health_misinformation', 'Health Misinformation'),
        ('political_misinformation', 'Political Misinformation'),
        ('scientific_falsehood', 'Scientific Falsehood'),
        ('financial_scam', 'Financial Scam'),
        ('social_falsehood', 'Social Falsehood'),
        ('unverified', 'Unverified'),
        ('factual', 'Factual'),
    ]
    
    # Claim information
    claim_text = models.TextField()
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='unverified')
    extracted_from = models.ForeignKey(Trend, on_delete=models.CASCADE, related_name='claims')
    
    # Claim analysis
    sentiment = models.CharField(max_length=20, blank=True)
    emotional_language_score = models.FloatField(default=0.0)  # 0-1
    sensationalist_score = models.FloatField(default=0.0)  # 0-1
    
    # Source credibility
    source_credibility_score = models.FloatField(default=0.5)  # 0-1
    verified_source_count = models.IntegerField(default=0)
    
    # Matching against known false claims
    matches_known_false_claim = models.BooleanField(default=False)
    false_claim_database_match = models.CharField(max_length=100, blank=True)
    
    # Timestamps
    claim_date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'claims'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['category', '-created_at']),
            models.Index(fields=['matches_known_false_claim', '-emotional_language_score']),
        ]
    
    def __str__(self):
        return f"{self.claim_text[:50]}... ({self.category})"


class TrendPrediction(models.Model):
    """AI predictions for trend forecasting."""
    
    trend = models.ForeignKey(Trend, on_delete=models.CASCADE, related_name='predictions')
    
    # Prediction metrics
    predicted_engagement_24h = models.FloatField(default=0.0)
    predicted_engagement_48h = models.FloatField(default=0.0)
    confidence_score = models.FloatField(default=0.0)  # 0-1
    
    # Signal analysis
    engagement_acceleration = models.FloatField(default=0.0)
    cross_platform_emergence_score = models.FloatField(default=0.0)
    influencer_amplification_score = models.FloatField(default=0.0)
    sentiment_trajectory = models.CharField(max_length=20, blank=True)  # improving, declining, stable
    
    # Model info
    model_version = models.CharField(max_length=50, default='1.0.0')
    prediction_horizon = models.IntegerField(default=24)  # hours
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'trend_predictions'
        ordering = ['-confidence_score', '-predicted_engagement_48h']
    
    def __str__(self):
        return f"Prediction for {self.trend.topic[:30]}... (24h: {self.predicted_engagement_24h})"


class SourceCredibility(models.Model):
    """Source credibility tracking and scoring."""
    
    source_name = models.CharField(max_length=200, unique=True)
    source_url = models.URLField(blank=True)
    platform = models.CharField(max_length=20)
    
    # Credibility metrics
    credibility_score = models.FloatField(default=0.5)  # 0-1
    fact_check_history_count = models.IntegerField(default=0)
    fact_check_accuracy = models.FloatField(default=0.0)  # 0-1
    bias_rating = models.CharField(max_length=50, blank=True)
    factual_reporting = models.CharField(max_length=50, blank=True)
    
    # Historical patterns
    historical_patterns = JSONField(default=dict)
    
    last_analyzed = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'source_credibility'
        ordering = ['-credibility_score']
    
    def __str__(self):
        return f"{self.source_name} (Credibility: {self.credibility_score:.2f})"


class TrendCollectionLog(models.Model):
    """Observability: Log of trend collection activities."""
    
    source = models.ForeignKey(TrendSource, on_delete=models.CASCADE, related_name='logs')
    
    # Collection metrics
    status = models.CharField(max_length=20)  # success, failed, partial
    items_collected = models.IntegerField(default=0)
    items_new = models.IntegerField(default=0)
    items_deduplicated = models.IntegerField(default=0)
    
    # Performance metrics
    latency_ms = models.IntegerField(default=0)
    api_success_rate = models.FloatField(default=0.0)  # 0-1
    rate_limit_hits = models.IntegerField(default=0)
    
    # Error tracking
    error_message = models.TextField(blank=True)
    error_code = models.CharField(max_length=50, blank=True)
    
    # Timestamps
    started_at = models.DateTimeField()
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'trend_collection_logs'
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['source', '-started_at']),
            models.Index(fields=['status', '-started_at']),
        ]
    
    def __str__(self):
        return f"{self.source.name} - {self.status} ({self.items_collected} items)"
    
    @property
    def duration_seconds(self):
        if self.completed_at and self.started_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None


class MisinformationAlert(models.Model):
    """Alerts for high-risk misinformation detection."""
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('acknowledged', 'Acknowledged'),
        ('resolved', 'Resolved'),
        ('dismissed', 'Dismissed'),
    ]
    
    trend = models.ForeignKey(Trend, on_delete=models.CASCADE, related_name='alerts')
    
    # Alert details
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    alert_message = models.TextField()
    
    # Detection triggers
    triggers = ArrayField(models.CharField(max_length=100), default=list)
    
    # Notification
    notified_users = ArrayField(models.EmailField(), default=list)
    sent_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'misinformation_alerts'
        ordering = ['-priority', '-created_at']
    
    def __str__(self):
        return f"Alert: {self.trend.topic[:30]}... ({self.priority})"
