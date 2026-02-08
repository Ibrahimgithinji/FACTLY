"""
Unified Schema for Fact-Checking Data

Defines standardized data structures for verification results from different APIs.
"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime


def datetime_to_iso(dt: Optional[datetime]) -> Optional[str]:
    """Convert datetime to ISO format string."""
    return dt.isoformat() if dt else None


@dataclass
class PublisherCredibility:
    """Represents publisher credibility assessment."""
    name: str
    credibility_score: float  # 0.0 to 1.0
    review_count: int
    average_rating: Optional[float]
    categories: List[str]
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with exact values preserved."""
        return {
            "name": self.name,
            "credibility_score": self.credibility_score,
            "review_count": self.review_count,
            "average_rating": self.average_rating,
            "categories": self.categories,
            "metadata": self.metadata
        }


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
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with exact values preserved."""
        return {
            "claim": self.claim,
            "verdict": self.verdict,
            "confidence_score": self.confidence_score,
            "publisher": self.publisher.to_dict() if self.publisher else None,
            "review_date": datetime_to_iso(self.review_date),
            "url": self.url,
            "language": self.language,
            "metadata": self.metadata
        }


@dataclass
class RelatedNews:
    """Represents related news coverage."""
    title: str
    url: str
    source: str
    publish_date: datetime
    relevance_score: float  # 0.0 to 1.0
    sentiment: Optional[str]  # "positive", "negative", "neutral"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with exact values preserved."""
        return {
            "title": self.title,
            "url": self.url,
            "source": self.source,
            "publish_date": datetime_to_iso(self.publish_date),
            "relevance_score": self.relevance_score,
            "sentiment": self.sentiment,
            "metadata": self.metadata
        }


@dataclass
class SourceReliability:
    """Represents source reliability assessment."""
    source_name: str
    reliability_score: float  # 0.0 to 1.0
    bias_rating: Optional[str]  # e.g., "left", "right", "center"
    factual_reporting: float  # 0.0 to 1.0
    historical_patterns: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with exact values preserved."""
        return {
            "source_name": self.source_name,
            "reliability_score": self.reliability_score,
            "bias_rating": self.bias_rating,
            "factual_reporting": self.factual_reporting,
            "historical_patterns": self.historical_patterns,
            "metadata": self.metadata
        }


@dataclass
class DirectVerificationEntry:
    """Entry for direct source verification in results."""
    source_name: str
    source_type: str
    source_url: Optional[str]
    verification_method: str
    is_verified: bool
    verification_score: float
    evidence_found: List[str]
    data_points_confirmed: List[str]
    discrepancies: List[str]
    source_credibility: float
    verified_at: datetime

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with exact values preserved."""
        return {
            "source_name": self.source_name,
            "source_type": self.source_type,
            "source_url": self.source_url,
            "verification_method": self.verification_method,
            "is_verified": self.is_verified,
            "verification_score": self.verification_score,
            "evidence_found": self.evidence_found,
            "data_points_confirmed": self.data_points_confirmed,
            "discrepancies": self.discrepancies,
            "source_credibility": self.source_credibility,
            "verified_at": datetime_to_iso(self.verified_at)
        }


@dataclass
class VerificationTraceEntry:
    """Entry for verification process trace."""
    step_number: int
    step_name: str
    description: str
    status: str
    result: Optional[Dict[str, Any]]
    timestamp: datetime
    duration_ms: float

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with exact values preserved."""
        return {
            "step_number": self.step_number,
            "step_name": self.step_name,
            "description": self.description,
            "status": self.status,
            "result": self.result,
            "timestamp": datetime_to_iso(self.timestamp),
            "duration_ms": self.duration_ms
        }


@dataclass
class EnhancedVerificationSummaryData:
    """Enhanced verification summary data for frontend display."""
    headline: str
    overall_assessment: str
    verification_methodology: str
    key_findings: List[str]
    verified_data_points: List[str]
    unverified_data_points: List[str]
    discrepancies_and_caveats: List[str]
    sources_consulted: List[Dict[str, Any]]
    source_diversity_assessment: str
    confidence_statement: str
    recommendations: List[str]
    verification_limitations: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with exact values preserved."""
        return {
            "headline": self.headline,
            "overall_assessment": self.overall_assessment,
            "verification_methodology": self.verification_methodology,
            "key_findings": self.key_findings,
            "verified_data_points": self.verified_data_points,
            "unverified_data_points": self.unverified_data_points,
            "discrepancies_and_caveats": self.discrepancies_and_caveats,
            "sources_consulted": self.sources_consulted,
            "source_diversity_assessment": self.source_diversity_assessment,
            "confidence_statement": self.confidence_statement,
            "recommendations": self.recommendations,
            "verification_limitations": self.verification_limitations
        }



