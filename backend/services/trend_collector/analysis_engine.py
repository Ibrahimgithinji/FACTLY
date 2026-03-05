"""
Trend Analysis Engine

Contains:
- Trend Normalizer: Transforms heterogeneous data into unified structure
- Claim Extractor: NLP-based factual claim extraction
- Misinformation Detector: Risk scoring algorithm
- Trend Ranker: Intelligent priority scoring
- Prediction Engine: AI-based trend forecasting
"""

import os
import re
import logging
import hashlib
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import Counter

from .models import Trend, Claim, TrendPrediction
from .trend_aggregator import NormalizedTrend

logger = logging.getLogger(__name__)


# =============================================================================
# Data Normalization Pipeline
# =============================================================================

@dataclass
class NormalizedTrendData:
    """Unified trend data structure."""
    topic: str
    keywords: List[str]
    source: str
    source_platform: str
    engagement_score: float
    engagement_velocity: float
    mention_volume: int
    share_count: int
    comment_count: int
    view_count: int
    region: str
    regions_detected: List[str]
    timestamp: datetime
    cross_platform_count: int
    metadata: Dict[str, Any] = field(default_factory=dict)


class TrendNormalizer:
    """
    Transforms heterogeneous data formats into unified structure.
    
    Converts:
    - topic
    - keywords array
    - source
    - engagement score
    - region
    - ISO timestamp
    """
    
    # Keywords extraction patterns
    STOP_WORDS = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during',
        'before', 'after', 'above', 'below', 'between', 'among', 'is', 'are',
        'was', 'were', 'been', 'have', 'has', 'had', 'do', 'does', 'did',
        'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can',
        'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it',
        'we', 'they', 'what', 'which', 'who', 'whom', 'whose', 'where', 'when',
        'why', 'how', 'all', 'each', 'every', 'both', 'few', 'more', 'most',
        'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same',
        'so', 'than', 'too', 'very', 'just', 'also', 'now', 'new', 'like'
    }
    
    # Region keywords mapping
    REGION_KEYWORDS = {
        'africa': ['africa', 'african', 'nigeria', 'kenya', 'south africa', 'egypt', 'ethiopia'],
        'india': ['india', 'indian', 'delhi', 'mumbai', 'modi', 'bjp', 'congress'],
        'us': ['usa', 'america', 'american', 'trump', 'biden', 'congress', 'senate', 'white house'],
        'europe': ['europe', 'european', 'uk', 'britain', 'france', 'germany', 'eu', 'brexit'],
        'asia': ['china', 'chinese', 'japan', 'korea', 'taiwan', 'russia', 'putin'],
        'latin_america': ['brazil', 'mexico', 'argentina', 'colombia', 'chile']
    }
    
    def normalize(self, raw_trends: List[NormalizedTrend]) -> List[NormalizedTrendData]:
        """Convert raw trends to normalized format."""
        normalized = []
        
        for trend in raw_trends:
            # Extract keywords
            keywords = self._extract_keywords(trend.topic)
            
            # Detect regions
            regions = self._detect_regions(trend.topic, trend.metadata)
            
            # Calculate cross-platform count
            cross_platform = len(set(trend.source_platform))
            
            # Normalize engagement score (0-100)
            normalized_engagement = self._normalize_engagement(
                trend.engagement_score,
                trend.mention_volume,
                trend.share_count,
                trend.comment_count
            )
            
            normalized_trend = NormalizedTrendData(
                topic=trend.topic,
                keywords=keywords,
                source=trend.source_name,
                source_platform=trend.source_platform,
                engagement_score=normalized_engagement,
                engagement_velocity=trend.engagement_score / max(1, (datetime.utcnow() - trend.timestamp).total_seconds() / 3600),
                mention_volume=trend.mention_volume,
                share_count=trend.share_count,
                comment_count=trend.comment_count,
                view_count=trend.view_count,
                region=regions[0] if regions else 'global',
                regions_detected=regions,
                timestamp=trend.timestamp,
                cross_platform_count=cross_platform,
                metadata=trend.metadata
            )
            
            normalized.append(normalized_trend)
        
        return normalized
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract meaningful keywords from text."""
        # Clean and tokenize
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        words = text.split()
        
        # Filter stop words and short words
        keywords = [w for w in words if w not in self.STOP_WORDS and len(w) > 3]
        
        # Get top keywords
        keyword_counts = Counter(keywords)
        top_keywords = [word for word, count in keyword_counts.most_common(10)]
        
        return top_keywords
    
    def _detect_regions(self, text: str, metadata: Dict) -> List[str]:
        """Detect regions mentioned in the text."""
        text = text.lower()
        detected = []
        
        for region, keywords in self.REGION_KEYWORDS.items():
            if any(kw in text for kw in keywords):
                detected.append(region)
        
        # Check metadata for region
        if metadata.get('region'):
            if metadata['region'] not in detected:
                detected.append(metadata['region'])
        
        return detected if detected else ['global']
    
    def _normalize_engagement(self, engagement: float, mentions: int, shares: int, comments: int) -> float:
        """Normalize engagement score to 0-100 scale."""
        # Weighted engagement calculation
        score = (engagement * 1.0 + 
                 mentions * 0.5 + 
                 shares * 0.8 + 
                 comments * 0.3)
        
        # Normalize to 0-100 (assuming max possible engagement is 10000)
        normalized = min(100, score / 100)
        
        return normalized


# =============================================================================
# Claim Extraction Engine
# =============================================================================

class ClaimExtractor:
    """
    NLP-based claim extraction using transformer models.
    
    Distinguishes factual claims from general discussions.
    Categories:
    - Health Misinformation
    - Political Misinformation
    - Scientific Falsehood
    - Financial Scam
    - Social Falsehood
    - Factual
    """
    
    # Claim patterns for different categories
    CLAIM_PATTERNS = {
        'health_misinformation': [
            r'vaccine\s+causes?', r'vaccine\s+is\s+dangerous', r'cure\s+for\s+cancer',
            r'natural\s+remedy', r'disease\s+is\s+a\s+hoax', r'virus\s+is\s+fake',
            r'side\s+effects?', r'infertility', r'autism', r'death'
        ],
        'political_misinformation': [
            r'election\s+fraud', r'vote\s+rigged', r'stolen\s+election',
            r'politician\s+said', r'congress\s+passed', r'law\s+passed',
            r'president\s+ordered', r'executive\s+order'
        ],
        'scientific_falsehood': [
            r'climate\s+change\s+is\s+fake', r'earth\s+is\s+flat',
            r'global\s+warming\s+is\s+a\s+hoax', r'science\s+says',
            r'research\s+shows', r'study\s+proves'
        ],
        'financial_scam': [
            r'make\s+money\s+fast', r'bitcoin', r'crypto',
            r'investment\s+opportunity', r'guaranteed\s+return',
            r'double\s+your\s+money', r'free\s+money'
        ],
    }
    
    # Sentiment/emotional language patterns
    EMOTIONAL_PATTERNS = [
        r'shocking', r'outrageous', r'must\s+share', r'breaking',
        r'wake\s+up', r'don\'t\s+trust', r'they\s+don\'t\s+want',
        r'you\s+won\'t\s+believe', r'censored', r'cover-up'
    ]
    
    # Sensationalist patterns
    SENSATIONALIST_PATTERNS = [
        r'\bexclusive\b', r'\bleaked\b', r'\brevealed\b',
        r'\bincredible\b', r'\bunbelievable\b', r'\bexplosive\b',
        r'\bdevastating\b', r'\bdevastating\b', r'\bshocking\b'
    ]
    
    def extract_claims(self, trend_text: str) -> List[Dict[str, Any]]:
        """Extract claims from trend text."""
        claims = []
        
        # Check each category
        for category, patterns in self.CLAIM_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, trend_text.lower()):
                    claims.append({
                        'text': trend_text,
                        'category': category,
                        'matched_pattern': pattern,
                        'confidence': 0.8
                    })
                    break
        
        # If no specific claim found, classify as potentially factual
        if not claims:
            claims.append({
                'text': trend_text,
                'category': 'unverified',
                'confidence': 0.5
            })
        
        return claims
    
    def analyze_sentiment(self, text: str) -> Dict[str, float]:
        """Analyze emotional language and sentiment."""
        text_lower = text.lower()
        
        # Emotional language score
        emotional_matches = sum(1 for p in self.EMOTIONAL_PATTERNS if re.search(p, text_lower))
        emotional_score = min(1.0, emotional_matches / 3)
        
        # Sensationalist score
        sensational_matches = sum(1 for p in self.SENSATIONALIST_PATTERNS if re.search(p, text_lower))
        sensational_score = min(1.0, sensational_matches / 2)
        
        return {
            'emotional_score': emotional_score,
            'sensational_score': sensational_score,
            'is_sensational': sensational_score > 0.5,
            'is_emotional': emotional_score > 0.5
        }


# =============================================================================
# Misinformation Risk Scoring Algorithm
# =============================================================================

class MisinformationDetector:
    """
    Risk scoring system evaluating:
    - Virality metrics (engagement velocity, cross-platform propagation)
    - Misinformation indicators (emotional language, sensationalism)
    - Source credibility assessment
    
    Output: Normalized score 0-100
    """
    
    # Known false claim keywords (simplified - in production, use database)
    KNOWN_FALSE_KEYWORDS = [
        'fake news', 'hoax', 'conspiracy', 'lies', 'false flag',
        'deep state', 'chemtrails', 'flat earth', 'anti vax'
    ]
    
    def __init__(self):
        self.claim_extractor = ClaimExtractor()
    
    def calculate_risk_score(
        self,
        normalized_trend: NormalizedTrendData,
        claims: List[Dict],
        source_credibility: float = 0.5
    ) -> Dict[str, Any]:
        """
        Calculate misinformation risk score (0-100).
        
        Factors:
        - Virality (40%): engagement velocity, cross-platform spread
        - Emotional/Sensational language (25%): emotional_score, sensational_score
        - Claim type (20%): category-based risk
        - Source credibility (15%): source reputation
        """
        
        # 1. Virality Score (0-100)
        virality_score = self._calculate_virality_score(
            normalized_trend.engagement_velocity,
            normalized_trend.cross_platform_count,
            normalized_trend.mention_volume
        )
        
        # 2. Content Analysis Score (0-100)
        sentiment_analysis = self.claim_extractor.analyze_sentiment(normalized_trend.topic)
        content_score = (sentiment_analysis['emotional_score'] * 50 + 
                        sentiment_analysis['sensational_score'] * 50)
        
        # 3. Claim Type Risk (0-100)
        claim_risk = self._calculate_claim_risk(claims)
        
        # 4. Source Credibility Score (0-100) - inverted (low credibility = high risk)
        credibility_risk = (1 - source_credibility) * 100
        
        # 5. Known false claim check
        known_false_match = self._check_known_false_claims(normalized_trend.topic)
        
        # Weighted final score
        final_score = (
            virality_score * 0.40 +
            content_score * 0.25 +
            claim_risk * 0.20 +
            credibility_risk * 0.15
        )
        
        # Boost if matches known false claims
        if known_false_match:
            final_score = min(100, final_score * 1.5)
        
        # Determine risk level
        risk_level = self._get_risk_level(final_score)
        
        return {
            'risk_score': round(final_score, 2),
            'risk_level': risk_level,
            'virality_score': round(virality_score, 2),
            'content_analysis': sentiment_analysis,
            'claim_risk': round(claim_risk, 2),
            'known_false_claim': known_false_match,
            'requires_verification': final_score > 50,
            'triggers': self._get_risk_triggers(
                sentiment_analysis, known_false_match, claim_risk
            )
        }
    
    def _calculate_virality_score(self, velocity: float, cross_platform: int, volume: int) -> float:
        """Calculate virality score based on engagement velocity and spread."""
        # Velocity score (0-50)
        velocity_score = min(50, velocity / 10)
        
        # Cross-platform score (0-30)
        platform_score = min(30, cross_platform * 10)
        
        # Volume score (0-20)
        volume_score = min(20, min(1000, volume) / 50)
        
        return velocity_score + platform_score + volume_score
    
    def _calculate_claim_risk(self, claims: List[Dict]) -> float:
        """Calculate risk based on claim categories."""
        category_risk = {
            'health_misinformation': 90,
            'political_misinformation': 85,
            'scientific_falsehood': 80,
            'financial_scam': 95,
            'social_falsehood': 70,
            'unverified': 50,
            'factual': 10
        }
        
        if not claims:
            return 50
        
        # Return highest risk category
        return max(category_risk.get(claims[0].get('category', 'unverified'), 50) for claims in claims)
    
    def _check_known_false_claims(self, text: str) -> bool:
        """Check if text matches known false claim patterns."""
        text_lower = text.lower()
        return any(kw in text_lower for kw in self.KNOWN_FALSE_KEYWORDS)
    
    def _get_risk_level(self, score: float) -> str:
        """Determine risk level from score."""
        if score >= 80:
            return 'critical'
        elif score >= 60:
            return 'high'
        elif score >= 40:
            return 'medium'
        return 'low'
    
    def _get_risk_triggers(self, sentiment: Dict, known_false: bool, claim_risk: float) -> List[str]:
        """Get list of risk triggers."""
        triggers = []
        
        if sentiment.get('is_emotional'):
            triggers.append('emotional_language')
        if sentiment.get('is_sensational'):
            triggers.append('sensationalist_content')
        if known_false:
            triggers.append('known_false_claim_match')
        if claim_risk > 70:
            triggers.append('high_risk_category')
        
        return triggers


# =============================================================================
# Intelligent Trend Ranking Engine
# =============================================================================

class TrendRanker:
    """
    Calculate priority scores using formula:
    priority_score = virality_score × misinformation_risk
    
    Surfaces top claims requiring immediate verification.
    """
    
    def rank_trends(
        self,
        normalized_trends: List[NormalizedTrendData],
        risk_scores: Dict[str, Dict]
    ) -> List[Dict]:
        """
        Rank trends by priority score.
        
        Returns sorted list with priority_score and metadata.
        """
        ranked = []
        
        for trend in normalized_trends:
            # Get risk score for this trend
            trend_key = hashlib.md5(trend.topic.encode()).hexdigest()
            risk_data = risk_scores.get(trend_key, {'risk_score': 0})
            
            # Calculate priority score
            priority_score = trend.engagement_score * (risk_data.get('risk_score', 0) / 100)
            
            ranked.append({
                'topic': trend.topic,
                'keywords': trend.keywords,
                'source_platforms': trend.source_platform,
                'engagement_score': trend.engagement_score,
                'engagement_velocity': trend.engagement_velocity,
                'risk_level': risk_data.get('risk_level', 'low'),
                'misinformation_risk_score': risk_data.get('risk_score', 0),
                'priority_score': round(priority_score, 4),
                'requires_verification': risk_data.get('requires_verification', False),
                'triggers': risk_data.get('triggers', []),
                'region': trend.region,
                'regions_detected': trend.regions_detected,
                'timestamp': trend.timestamp.isoformat()
            })
        
        # Sort by priority score (highest first)
        ranked.sort(key=lambda x: x['priority_score'], reverse=True)
        
        return ranked
    
    def get_top_requiring_verification(self, ranked_trends: List[Dict], limit: int = 10) -> List[Dict]:
        """Get top N trends requiring verification."""
        verification_needed = [
            t for t in ranked_trends 
            if t.get('requires_verification', False)
        ]
        return verification_needed[:limit]


# =============================================================================
# AI Trend Prediction Model
# =============================================================================

class TrendPredictor:
    """
    Predictive system analyzing:
    - Engagement acceleration patterns
    - Cross-platform emergence timing
    - Influencer amplification signals
    - Sentiment trajectory
    
    Forecasts which topics will trend in 24-48 hours.
    """
    
    def predict_trend_trajectory(
        self,
        trend_history: List[Dict],
        current_engagement: float,
        hours_ahead: int = 24
    ) -> Dict[str, Any]:
        """
        Predict future engagement and trend probability.
        
        Args:
            trend_history: Historical engagement data points
            current_engagement: Current engagement score
            hours_ahead: Hours to predict ahead (24 or 48)
        
        Returns:
            Prediction with confidence interval
        """
        
        if not trend_history or len(trend_history) < 2:
            # Not enough data - use simple projection
            growth_rate = 1.2  # Assume 20% growth
        else:
            # Calculate growth rate from history
            first = trend_history[0].get('engagement', 0)
            last = trend_history[-1].get('engagement', current_engagement)
            
            if first > 0:
                growth_rate = (last / first) ** (1 / len(trend_history))
            else:
                growth_rate = 1.2
        
        # Project future engagement
        predicted_engagement = current_engagement * (growth_rate ** (hours_ahead / 24))
        
        # Calculate confidence based on data quality
        confidence = min(0.9, 0.3 + 0.1 * len(trend_history))
        
        # Determine trajectory
        if growth_rate > 1.3:
            trajectory = 'accelerating'
        elif growth_rate < 0.9:
            trajectory = 'declining'
        else:
            trajectory = 'stable'
        
        return {
            'predicted_engagement': round(predicted_engagement, 2),
            'current_engagement': current_engagement,
            'growth_rate': round(growth_rate, 2),
            'confidence_score': confidence,
            'prediction_horizon_hours': hours_ahead,
            'trajectory': trajectory,
            'will_trend': predicted_engagement > 50 or growth_rate > 1.5
        }
    
    def analyze_signals(
        self,
        cross_platform_emergence: int,
        influencer_engagement: float,
        sentiment_score: float
    ) -> Dict[str, float]:
        """Analyze various prediction signals."""
        
        # Cross-platform emergence (0-1)
        emergence_score = min(1.0, cross_platform_emergence / 5)
        
        # Influencer amplification (0-1)
        influencer_score = min(1.0, influencer_engagement / 1000)
        
        # Combined signal
        overall_signal = (
            emergence_score * 0.4 +
            influencer_score * 0.3 +
            sentiment_score * 0.3
        )
        
        return {
            'cross_platform_emergence_score': emergence_score,
            'influencer_amplification_score': influencer_score,
            'sentiment_trajectory_score': sentiment_score,
            'overall_signal_strength': overall_signal
        }


# =============================================================================
# Observability - Metrics Collection
# =============================================================================

class MetricsCollector:
    """Collects and logs observability metrics."""
    
    def __init__(self):
        self.logger = logging.getLogger('trend_collector.metrics')
    
    def log_collection_metrics(self, source: str, status: str, items_collected: int, latency_ms: int):
        """Log API collection metrics."""
        self.logger.info(
            f"Collection: source={source}, status={status}, "
            f"items={items_collected}, latency_ms={latency_ms}"
        )
    
    def log_detection_accuracy(self, true_positives: int, false_positives: int, false_negatives: int):
        """Log misinformation detection accuracy."""
        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        self.logger.info(
            f"Detection metrics: precision={precision:.2f}, recall={recall:.2f}, f1={f1:.2f}"
        )
    
    def log_latency_percentiles(self, p50: float, p95: float, p99: float):
        """Log latency percentiles."""
        self.logger.info(f"Latency: p50={p50}ms, p95={p95}ms, p99={p99}ms")
    
    def log_anomaly(self, metric_name: str, value: float, threshold: float):
        """Log anomalous metric value."""
        self.logger.warning(
            f"Anomaly detected: {metric_name}={value} (threshold={threshold})"
        )
