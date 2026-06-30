"""
Database Models for Trend Discovery and Misinformation Detection

Defines PostgreSQL schema for storing trends, claims, and misinformation risk data.
"""

from django.db import models
from django.utils import timezone


class Platform(models.TextChoices):
    TWITTER = 'twitter', 'Twitter/X'
    REDDIT = 'reddit', 'Reddit'
    TIKTOK = 'tiktok', 'TikTok'
    GOOGLE_TRENDS = 'google_trends', 'Google Trends'
    BING_TRENDS = 'bing_trends', 'Bing Trends'
    NEWS_API = 'news_api', 'News API'
    RSS = 'rss', 'RSS Feed'
    CUSTOM = 'custom', 'Custom Source'


class Region(models.TextChoices):
    GLOBAL = 'global', 'Global'
    AFRICA = 'africa', 'Africa'
    INDIA = 'india', 'India'
    US = 'us', 'United States'
    EUROPE = 'europe', 'Europe'
    ASIA = 'asia', 'Asia'
    LATIN_AMERICA = 'latin_america', 'Latin America'


class RiskLevel(models.TextChoices):
    LOW = 'low', 'Low Risk'
    MEDIUM = 'medium', 'Medium Risk'
    HIGH = 'high', 'High Risk'
    CRITICAL = 'critical', 'Critical Risk'


class VerificationStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    PROCESSING = 'processing', 'Processing'
    VERIFIED = 'verified', 'Verified'
    FALSE = 'false', 'False Claim'
    TRUE = 'true', 'True Claim'
    UNVERIFIABLE = 'unverifiable', 'Unverifiable'


class ClaimCategory(models.TextChoices):
    HEALTH_MISINFORMATION = 'health_misinformation', 'Health Misinformation'
    POLITICAL_MISINFORMATION = 'political_misinformation', 'Political Misinformation'
    SCIENTIFIC_FALSEHOOD = 'scientific_falsehood', 'Scientific Falsehood'
    FINANCIAL_SCAM = 'financial_scam', 'Financial Scam'
    SOCIAL_FALSEHOOD = 'social_falsehood', 'Social Falsehood'
    UNVERIFIED = 'unverified', 'Unverified'
    FACTUAL = 'factual', 'Factual'


class Sentiment(models.TextChoices):
    POSITIVE = 'positive', 'Positive'
    NEGATIVE = 'negative', 'Negative'
    NEUTRAL = 'neutral', 'Neutral'
    MIXED = 'mixed', 'Mixed'


class SentimentTrajectory(models.TextChoices):
    IMPROVING = 'improving', 'Improving'
    DECLINING = 'declining', 'Declining'
    STABLE = 'stable', 'Stable'


class BiasRating(models.TextChoices):
    LEFT = 'left', 'Left'
    CENTER_LEFT = 'center_left', 'Center-Left'
    CENTER = 'center', 'Center'
    CENTER_RIGHT = 'center_right', 'Center-Right'
    RIGHT = 'right', 'Right'
    UNKNOWN = 'unknown', 'Unknown'


class FactualReporting(models.TextChoices):
    VERY_HIGH = 'very_high', 'Very High'
    HIGH = 'high', 'High'
    MIXED = 'mixed', 'Mixed'
    LOW = 'low', 'Low'
    VERY_LOW = 'very_low', 'Very Low'
    UNKNOWN = 'unknown', 'Unknown'


class CollectionStatus(models.TextChoices):
    SUCCESS = 'success', 'Success'
    FAILED = 'failed', 'Failed'
    PARTIAL = 'partial', 'Partial'


class AlertPriority(models.TextChoices):
    LOW = 'low', 'Low'
    MEDIUM = 'medium', 'Medium'
    HIGH = 'high', 'High'
    CRITICAL = 'critical', 'Critical'


class AlertStatus(models.TextChoices):
    ACTIVE = 'active', 'Active'
    ACKNOWLEDGED = 'acknowledged', 'Acknowledged'
    RESOLVED = 'resolved', 'Resolved'
    DISMISSED = 'dismissed', 'Dismissed'


class TrendSource(models.Model):
    """Source platforms for trend collection."""

    name = models.CharField(max_length=100, unique=True)
    platform = models.CharField(max_length=20, choices=Platform.choices)
    region = models.CharField(max_length=20, choices=Region.choices, default=Region.GLOBAL)
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

    topic = models.CharField(max_length=500, db_index=True)
    keywords = models.JSONField(default=list)
    summary = models.TextField(blank=True)

    source_platforms = models.JSONField(default=list)
    source_count = models.IntegerField(default=1)

    engagement_score = models.FloatField(default=0.0, db_index=True)
    engagement_velocity = models.FloatField(default=0.0)
    mention_volume = models.IntegerField(default=0)
    share_count = models.IntegerField(default=0)
    comment_count = models.IntegerField(default=0)
    view_count = models.BigIntegerField(default=0)

    primary_region = models.CharField(max_length=20, default='global')
    detected_regions = models.JSONField(default=list)
    first_detected = models.DateTimeField(default=timezone.now)
    last_updated = models.DateTimeField(default=timezone.now)

    risk_level = models.CharField(
        max_length=10, choices=RiskLevel.choices, default=RiskLevel.LOW,
    )
    misinformation_risk_score = models.FloatField(default=0.0, db_index=True)

    predicted_trend_score = models.FloatField(default=0.0)
    prediction_confidence = models.FloatField(default=0.0)
    prediction_horizon_hours = models.IntegerField(default=24)

    verification_status = models.CharField(
        max_length=20, choices=VerificationStatus.choices, default=VerificationStatus.PENDING,
    )
    factly_score = models.IntegerField(null=True, blank=True)
    verification_summary = models.TextField(blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)

    metadata = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)
    priority_score = models.FloatField(default=0.0, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'trends'
        ordering = ['-priority_score', '-engagement_score']
        indexes = [
            models.Index(fields=['risk_level', '-priority_score']),
            models.Index(fields=['verification_status', '-misinformation_risk_score']),
        ]

    def __str__(self):
        return f"{self.topic[:50]}... (Risk: {self.risk_level})"

    def calculate_priority_score(self):
        self.priority_score = self.engagement_score * (self.misinformation_risk_score / 100)
        return self.priority_score


class Claim(models.Model):
    """Extracted factual claims from trends."""

    claim_text = models.TextField()
    category = models.CharField(
        max_length=30, choices=ClaimCategory.choices, default=ClaimCategory.UNVERIFIED,
    )
    extracted_from = models.ForeignKey(Trend, on_delete=models.CASCADE, related_name='claims')

    sentiment = models.CharField(
        max_length=20, choices=Sentiment.choices, blank=True,
    )
    emotional_language_score = models.FloatField(default=0.0)
    sensationalist_score = models.FloatField(default=0.0)

    source_credibility_score = models.FloatField(default=0.5)
    verified_source_count = models.IntegerField(default=0)

    matches_known_false_claim = models.BooleanField(default=False)
    false_claim_database_match = models.CharField(max_length=100, blank=True)

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

    predicted_engagement_24h = models.FloatField(default=0.0)
    predicted_engagement_48h = models.FloatField(default=0.0)
    confidence_score = models.FloatField(default=0.0)

    engagement_acceleration = models.FloatField(default=0.0)
    cross_platform_emergence_score = models.FloatField(default=0.0)
    influencer_amplification_score = models.FloatField(default=0.0)
    sentiment_trajectory = models.CharField(
        max_length=20, choices=SentimentTrajectory.choices, blank=True,
    )

    model_version = models.CharField(max_length=50, default='1.0.0')
    prediction_horizon = models.IntegerField(default=24)

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

    credibility_score = models.FloatField(default=0.5)
    fact_check_history_count = models.IntegerField(default=0)
    fact_check_accuracy = models.FloatField(default=0.0)
    bias_rating = models.CharField(
        max_length=20, choices=BiasRating.choices, blank=True,
    )
    factual_reporting = models.CharField(
        max_length=20, choices=FactualReporting.choices, blank=True,
    )

    historical_patterns = models.JSONField(default=dict)

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

    status = models.CharField(max_length=20, choices=CollectionStatus.choices)
    items_collected = models.IntegerField(default=0)
    items_new = models.IntegerField(default=0)
    items_deduplicated = models.IntegerField(default=0)

    latency_ms = models.IntegerField(default=0)
    api_success_rate = models.FloatField(default=0.0)
    rate_limit_hits = models.IntegerField(default=0)

    error_message = models.TextField(blank=True)
    error_code = models.CharField(max_length=50, blank=True)

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

    trend = models.ForeignKey(Trend, on_delete=models.CASCADE, related_name='alerts')

    priority = models.CharField(
        max_length=10, choices=AlertPriority.choices, default=AlertPriority.MEDIUM,
    )
    status = models.CharField(
        max_length=20, choices=AlertStatus.choices, default=AlertStatus.ACTIVE,
    )
    alert_message = models.TextField()

    triggers = models.JSONField(default=list)

    notified_users = models.JSONField(default=list)
    sent_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'misinformation_alerts'
        ordering = ['-priority', '-created_at']

    def __str__(self):
        return f"Alert: {self.trend.topic[:30]}... ({self.priority})"
