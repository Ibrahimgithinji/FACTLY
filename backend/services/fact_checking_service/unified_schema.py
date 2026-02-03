"""
Unified Schema for Fact-Checking Data

Defines standardized data structures for verification results from different APIs.
"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class PublisherCredibility:
    """Represents publisher credibility assessment."""
    name: str
    credibility_score: float  # 0.0 to 1.0
    review_count: int
    average_rating: Optional[float]
    categories: List[str]
    metadata: Dict[str, Any]


@dataclass
class ClaimReview:
    """Represents a claim review from fact-checking sources."""
    claim: str
    verdict: str  # e.g., "True", "False", "Misleading", etc.
    confidence_score: float  # 0.0 to 1.0
    publisher: PublisherCredibility
    review_date: datetime
    url: Optional[str]
    language: str
    metadata: Dict[str, Any]


@dataclass
class RelatedNews:
    """Represents related news coverage."""
    title: str
    url: str
    source: str
    publish_date: datetime
    relevance_score: float  # 0.0 to 1.0
    sentiment: Optional[str]  # "positive", "negative", "neutral"
    metadata: Dict[str, Any]


@dataclass
class SourceReliability:
    """Represents source reliability assessment."""
    source_name: str
    reliability_score: float  # 0.0 to 1.0
    bias_rating: Optional[str]  # e.g., "left", "right", "center"
    factual_reporting: float  # 0.0 to 1.0
    historical_patterns: Dict[str, Any]
    metadata: Dict[str, Any]


@dataclass
class VerificationResult:
    """Unified verification result from multiple APIs."""
    original_claim: str
    claim_reviews: List[ClaimReview]
    related_news: List[RelatedNews]
    source_reliability: Optional[SourceReliability]
    overall_confidence: float  # 0.0 to 1.0
    timestamp: datetime
    api_sources: List[str]  # e.g., ["google_fact_check", "newsldr"]
    metadata: Dict[str, Any]