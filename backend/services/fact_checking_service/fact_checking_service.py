"""
Main Fact Checking Service

Orchestrates fact-checking using multiple external APIs and returns unified results.
"""

import logging
from typing import List, Optional
from datetime import datetime
import os
from .google_fact_check import GoogleFactCheckClient
from .newsldr_api import NewsLdrClient
from .unified_schema import VerificationResult, ClaimReview, RelatedNews, SourceReliability
from .cache_manager import CacheManager

logger = logging.getLogger(__name__)


class FactCheckingService:
    """Main service for fact-checking claims using multiple APIs."""

    def __init__(self, cache_manager: Optional[CacheManager] = None):
        """
        Initialize the fact-checking service.

        Args:
            cache_manager: Optional cache manager instance
        """
        self.cache = cache_manager or CacheManager()
        
        # Get API keys from environment
        self.google_api_key = os.getenv('GOOGLE_FACT_CHECK_API_KEY')
        self.newsldr_api_key = os.getenv('NEWSLDR_API_KEY')
        
        # Initialize Google Fact Check client (will raise ValueError if no API key)
        self.google_client = None
        if self.google_api_key:
            try:
                self.google_client = GoogleFactCheckClient(api_key=self.google_api_key, cache_manager=self.cache)
            except ValueError as e:
                logger.warning(f"Google Fact Check client not initialized: {e}")
        else:
            logger.warning("GOOGLE_FACT_CHECK_API_KEY not set - Google Fact Check disabled")
        
        # Initialize NewsLdr client (will raise ValueError if no API key)
        self.newsldr_client = None
        if self.newsldr_api_key:
            try:
                self.newsldr_client = NewsLdrClient(api_key=self.newsldr_api_key, cache_manager=self.cache)
            except ValueError as e:
                logger.warning(f"NewsLdr client not initialized: {e}")
        else:
            logger.warning("NEWSLDR_API_KEY not set - NewsLdr disabled")
        
        # Also check if clients were initialized successfully
        self._check_clients_ready()

    def _check_clients_ready(self):
        """Log which API clients are ready for use."""
        google_ready = "Google Fact Check" if self.google_client else "NOT AVAILABLE"
        newsldr_ready = "NewsLdr" if self.newsldr_client else "NOT AVAILABLE"
        logger.info(f"API Clients Ready - Google Fact Check: {google_ready}, NewsLdr: {newsldr_ready}")

    def verify_claim(self, claim: str, language: str = "en") -> VerificationResult:
        """
        Verify a claim using multiple fact-checking APIs.

        Args:
            claim: The claim text to verify
            language: Language code for the claim

        Returns:
            Unified VerificationResult with data from all APIs
        """
        logger.info(f"Verifying claim: {claim[:100]}...")

        # Get claim reviews from Google Fact Check
        claim_reviews = []
        if self.google_client:
            try:
                claim_reviews = self.google_client.search_claims(claim, language)
                logger.info(f"Found {len(claim_reviews)} claim reviews from Google")
            except Exception as e:
                logger.error(f"Error getting Google claim reviews: {e}")
        else:
            logger.warning("Google Fact Check client not available")

        # Get related news from NewsLdr
        related_news = []
        if self.newsldr_client:
            try:
                related_news = self.newsldr_client.get_related_news(claim)
                logger.info(f"Found {len(related_news)} related news articles from NewsLdr")
            except Exception as e:
                logger.error(f"Error getting NewsLdr related news: {e}")
        else:
            logger.warning("NewsLdr client not available")

        # Get source reliability (if we have sources from news)
        source_reliability = None
        if related_news and self.newsldr_client:
            # Use the most relevant source for reliability check
            top_source = max(related_news, key=lambda x: x.relevance_score).source
            try:
                source_reliability = self.newsldr_client.get_source_reliability(top_source)
                if source_reliability:
                    logger.info(f"Got reliability data for source: {top_source}")
            except Exception as e:
                logger.error(f"Error getting source reliability: {e}")

        # Calculate overall confidence
        overall_confidence = self._calculate_overall_confidence(claim_reviews, related_news, source_reliability)

        # Determine API sources used
        api_sources = []
        if claim_reviews:
            api_sources.append("google_fact_check")
        if related_news:
            api_sources.append("newsldr")

        result = VerificationResult(
            original_claim=claim,
            claim_reviews=claim_reviews,
            related_news=related_news,
            source_reliability=source_reliability,
            overall_confidence=overall_confidence,
            timestamp=datetime.now(),
            api_sources=api_sources,
            metadata={
                "language": language,
                "total_reviews": len(claim_reviews),
                "total_news": len(related_news)
            }
        )

        logger.info(f"Verification complete. Overall confidence: {overall_confidence:.2f}")
        return result

    def _calculate_overall_confidence(self, claim_reviews: List[ClaimReview],
                                    related_news: List[RelatedNews],
                                    source_reliability: Optional[SourceReliability]) -> float:
        """
        Calculate overall confidence score from all available data.

        Args:
            claim_reviews: List of claim reviews
            related_news: List of related news
            source_reliability: Source reliability data

        Returns:
            Overall confidence score (0.0 to 1.0)
        """
        if not claim_reviews and not related_news:
            return 0.0

        confidence_scores = []

        # Weight claim review confidence
        if claim_reviews:
            avg_review_confidence = sum(r.confidence_score for r in claim_reviews) / len(claim_reviews)
            confidence_scores.append(avg_review_confidence * 0.7)  # 70% weight

        # Weight source reliability
        if source_reliability:
            confidence_scores.append(source_reliability.reliability_score * 0.3)  # 30% weight

        # If no reviews but we have news, give moderate confidence
        if not claim_reviews and related_news:
            confidence_scores.append(0.5)

        return sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0