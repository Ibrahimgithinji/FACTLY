"""
Fact Checking Service Module

This module provides integration with external fact-checking APIs:
- Google Fact Check Tools API
- NewsLdr API

It includes unified schema for verification data, caching, rate limiting,
and error handling.
"""

from .google_fact_check import GoogleFactCheckClient
from .newsldr_api import NewsLdrClient
from .unified_schema import VerificationResult, ClaimReview, PublisherCredibility, RelatedNews, SourceReliability
from .cache_manager import CacheManager
from .rate_limiter import RateLimiter
from .evidence_search_service import EvidenceSearchService, EvidenceItem, EvidenceCollection
from .cross_source_analyzer import CrossSourceAnalyzer, CrossSourceAnalysis, ConsensusLevel, EvidenceStrength
from .verification_orchestrator import VerificationOrchestrator, CompleteVerificationResult, VerificationSummary

# Import from existing modules
from .fact_checking_service import FactCheckingService
from .google_fact_check import GoogleFactCheckClient
from .newsldr_api import NewsLdrClient
from .unified_schema import VerificationResult, ClaimReview, PublisherCredibility, RelatedNews, SourceReliability
from .cache_manager import CacheManager
from .rate_limiter import RateLimiter

# Import new modules (avoid importing orchestrator here to prevent circular imports)
from .evidence_search_service import EvidenceSearchService, EvidenceItem, EvidenceCollection
from .cross_source_analyzer import CrossSourceAnalyzer, CrossSourceAnalysis, ConsensusLevel, EvidenceStrength

__all__ = [
    # Original Services
    'FactCheckingService',
    # API Clients
    'GoogleFactCheckClient',
    'NewsLdrClient',
    # Schema
    'VerificationResult',
    'ClaimReview',
    'PublisherCredibility',
    'RelatedNews',
    'SourceReliability',
    # Infrastructure
    'CacheManager',
    'RateLimiter',
    # New Services
    'EvidenceSearchService',
    'EvidenceItem',
    'EvidenceCollection',
    'CrossSourceAnalyzer',
    'CrossSourceAnalysis',
    'ConsensusLevel',
    'EvidenceStrength',
]