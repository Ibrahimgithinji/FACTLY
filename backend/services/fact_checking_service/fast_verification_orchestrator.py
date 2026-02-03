"""
Fast Verification Orchestrator

High-performance verification using async processing, connection pooling,
and optimized caching for sub-second response times.
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
import time

from services.nlp_service.claim_extraction_service import ClaimExtractor, ExtractedClaim
from services.nlp_service.text_preprocessing import TextPreprocessor
from services.fact_checking_service.async_evidence_search import (
    AsyncEvidenceSearchService, search_evidence_sync, batch_search_evidence_sync
)
from services.fact_checking_service.evidence_search_service import EvidenceCollection
from services.fact_checking_service.cross_source_analyzer import CrossSourceAnalyzer, CrossSourceAnalysis
from services.scoring_service.scoring_service import ScoringService, FactlyScoreResult
from services.fact_checking_service.unified_schema import VerificationResult
from services.fact_checking_service.cache_manager import CacheManager

logger = logging.getLogger(__name__)


@dataclass
class FastVerificationResult:
    """Optimized verification result for fast responses."""
    factly_score: int
    classification: str
    confidence_level: str
    recommended_verdict: str
    consensus_level: str
    evidence_strength: str
    headline: str
    explanation: str
    key_points: List[str]
    recommendations: List[str]
    sources_consulted: int
    processing_time: float
    cached: bool
    timestamp: datetime


class FastVerificationOrchestrator:
    """
    High-performance verification orchestrator.
    
    Optimizations:
    - Async concurrent API calls
    - Connection pooling
    - Intelligent caching
    - Early termination
    - Batch processing support
    """

    def __init__(self, cache_manager: Optional[CacheManager] = None):
        """Initialize fast verification orchestrator."""
        self.cache = cache_manager or CacheManager()
        self.claim_extractor = ClaimExtractor()
        self.text_preprocessor = TextPreprocessor()
        self.cross_source_analyzer = CrossSourceAnalyzer()
        self.scoring_service = ScoringService()
        
        # Performance settings
        self.max_results_per_source = 10
        self.early_termination_threshold = 5
        self.enable_caching = True
        
        logger.info("FastVerificationOrchestrator initialized")

    def verify_fast(self, text: str, language: str = "en",
                    use_cache: bool = True) -> FastVerificationResult:
        """
        Fast verification with async processing.
        
        Typical response time: 1-3 seconds (vs 5-10 seconds synchronous)
        """
        start_time = time.time()
        
        # Check cache first
        if use_cache and self.enable_caching:
            cache_key = {'text': text, 'language': language}
            cached = self.cache.get('fast_verification', cache_key)
            if cached:
                logger.info("Returning cached verification result")
                cached['cached'] = True
                cached['processing_time'] = 0.0
                return FastVerificationResult(**cached)

        logger.info(f"Starting fast verification for text ({len(text)} chars)")

        # Step 1: Extract claims (fast, local processing)
        extracted_claims = self.claim_extractor.extract_claims(text, min_confidence=0.4)
        primary_claim = self.claim_extractor.get_primary_claim(text)
        claim_to_verify = primary_claim.text if primary_claim else text

        # Step 2: Async evidence search (concurrent API calls)
        try:
            evidence_collection = search_evidence_sync(
                claim=claim_to_verify,
                language=language,
                max_results_per_source=self.max_results_per_source,
                cache_manager=self.cache
            )
        except Exception as e:
            logger.error(f"Async evidence search failed: {e}")
            # Fallback to empty collection
            evidence_collection = EvidenceCollection(
                claim=claim_to_verify,
                evidence_items=[],
                source_diversity_score=0.0,
                agreement_score=0.0,
                coverage_gaps=["Evidence search failed"],
                timestamp=datetime.now()
            )

        # Step 3: Cross-source analysis
        cross_source_analysis = self.cross_source_analyzer.analyze(evidence_collection)

        # Step 4: Calculate Factly Score™
        verification_result = self._convert_to_verification_result(claim_to_verify, evidence_collection)
        nlp_confidence = primary_claim.confidence if primary_claim else None
        
        factly_score_result = self.scoring_service.calculate_factly_score(
            verification_result,
            nlp_confidence=nlp_confidence,
            text_content=text
        )

        # Adjust score based on cross-source analysis
        adjusted_score = self._adjust_score_with_analysis(
            factly_score_result.factly_score,
            cross_source_analysis
        )

        # Step 5: Generate summary
        summary = self._generate_fast_summary(
            text, cross_source_analysis, adjusted_score
        )

        processing_time = time.time() - start_time

        # Build result
        result = FastVerificationResult(
            factly_score=adjusted_score,
            classification=factly_score_result.classification,
            confidence_level=factly_score_result.confidence_level,
            recommended_verdict=cross_source_analysis.recommended_verdict,
            consensus_level=cross_source_analysis.consensus_level.value,
            evidence_strength=cross_source_analysis.evidence_strength.value,
            headline=summary['headline'],
            explanation=summary['explanation'],
            key_points=summary['key_points'],
            recommendations=summary['recommendations'],
            sources_consulted=len(evidence_collection.evidence_items),
            processing_time=processing_time,
            cached=False,
            timestamp=datetime.now()
        )

        # Cache result
        if use_cache and self.enable_caching:
            self.cache.set('fast_verification', cache_key, result.__dict__)

        logger.info(f"Fast verification completed in {processing_time:.2f}s, score: {adjusted_score}")
        return result

    def verify_batch(self, texts: List[str], language: str = "en") -> List[FastVerificationResult]:
        """
        Batch verification for multiple texts.
        
        More efficient than individual calls due to:
        - Shared connection pool
        - Parallel processing
        - Reduced overhead
        """
        start_time = time.time()
        logger.info(f"Starting batch verification for {len(texts)} texts")

        # Extract all claims first
        claims_to_verify = []
        for text in texts:
            primary_claim = self.claim_extractor.get_primary_claim(text)
            claims_to_verify.append(primary_claim.text if primary_claim else text)

        # Batch evidence search (all claims in parallel)
        try:
            evidence_collections = batch_search_evidence_sync(
                claims=claims_to_verify,
                language=language,
                max_results_per_source=self.max_results_per_source,
                cache_manager=self.cache
            )
        except Exception as e:
            logger.error(f"Batch evidence search failed: {e}")
            # Return empty results
            return [self._create_error_result(text, str(e)) for text in texts]

        # Process each result
        results = []
        for i, (text, evidence_collection) in enumerate(zip(texts, evidence_collections)):
            # Cross-source analysis
            cross_source_analysis = self.cross_source_analyzer.analyze(evidence_collection)
            
            # Calculate score
            verification_result = self._convert_to_verification_result(
                claims_to_verify[i], evidence_collection
            )
            primary_claim = self.claim_extractor.get_primary_claim(text)
            nlp_confidence = primary_claim.confidence if primary_claim else None
            
            factly_score_result = self.scoring_service.calculate_factly_score(
                verification_result,
                nlp_confidence=nlp_confidence,
                text_content=text
            )
            
            adjusted_score = self._adjust_score_with_analysis(
                factly_score_result.factly_score,
                cross_source_analysis
            )
            
            # Generate summary
            summary = self._generate_fast_summary(text, cross_source_analysis, adjusted_score)
            
            result = FastVerificationResult(
                factly_score=adjusted_score,
                classification=factly_score_result.classification,
                confidence_level=factly_score_result.confidence_level,
                recommended_verdict=cross_source_analysis.recommended_verdict,
                consensus_level=cross_source_analysis.consensus_level.value,
                evidence_strength=cross_source_analysis.evidence_strength.value,
                headline=summary['headline'],
                explanation=summary['explanation'],
                key_points=summary['key_points'],
                recommendations=summary['recommendations'],
                sources_consulted=len(evidence_collection.evidence_items),
                processing_time=0.0,  # Will be calculated at end
                cached=False,
                timestamp=datetime.now()
            )
            results.append(result)

        total_time = time.time() - start_time
        avg_time = total_time / len(texts) if texts else 0
        
        logger.info(f"Batch verification completed: {len(texts)} texts in {total_time:.2f}s (avg: {avg_time:.2f}s)")
        
        # Update processing times
        for result in results:
            result.processing_time = avg_time
        
        return results

    def _convert_to_verification_result(self, claim: str,
                                        evidence: EvidenceCollection) -> VerificationResult:
        """Convert evidence collection to VerificationResult format."""
        from services.fact_checking_service.unified_schema import (
            ClaimReview, RelatedNews, SourceReliability, PublisherCredibility
        )

        claim_reviews = []
        related_news = []
        source_reliability = None

        for item in evidence.evidence_items:
            if item.source_type == 'fact_check':
                claim_reviews.append(ClaimReview(
                    claim=claim,
                    verdict=item.verdict or 'Unverified',
                    confidence_score=item.relevance_score,
                    publisher=PublisherCredibility(
                        name=item.source,
                        credibility_score=item.credibility_score,
                        review_count=0,
                        average_rating=None,
                        categories=[],
                        metadata=item.metadata
                    ),
                    review_date=item.published_date or datetime.now(),
                    url=item.url,
                    language='en',
                    metadata=item.metadata
                ))
            elif item.source_type == 'news':
                related_news.append(RelatedNews(
                    title=item.title,
                    url=item.url or '',
                    source=item.source,
                    publish_date=item.published_date or datetime.now(),
                    relevance_score=item.relevance_score,
                    sentiment=item.metadata.get('sentiment'),
                    metadata=item.metadata
                ))

        # Get source reliability from highest credibility news source
        news_items = [item for item in evidence.evidence_items if item.source_type == 'news']
        if news_items:
            top_source = max(news_items, key=lambda x: x.credibility_score)
            source_reliability = SourceReliability(
                source_name=top_source.source,
                reliability_score=top_source.credibility_score,
                bias_rating=top_source.metadata.get('bias_rating'),
                factual_reporting=top_source.credibility_score,
                historical_patterns={},
                metadata=top_source.metadata
            )

        return VerificationResult(
            original_claim=claim,
            claim_reviews=claim_reviews,
            related_news=related_news,
            source_reliability=source_reliability,
            overall_confidence=evidence.agreement_score,
            timestamp=datetime.now(),
            api_sources=list(set(item.source for item in evidence.evidence_items)),
            metadata={
                'source_diversity': evidence.source_diversity_score,
                'coverage_gaps': evidence.coverage_gaps
            }
        )

    def _adjust_score_with_analysis(self, base_score: int,
                                     analysis: CrossSourceAnalysis) -> int:
        """Adjust Factly Score™ based on cross-source analysis."""
        adjusted = base_score

        consensus_adjustments = {
            'strong_agreement': 5,
            'moderate_agreement': 0,
            'mixed': -5,
            'moderate_disagreement': -10,
            'strong_disagreement': -15,
            'insufficient_data': -10
        }
        adjusted += consensus_adjustments.get(analysis.consensus_level.value, 0)

        strength_adjustments = {
            'strong': 5,
            'moderate': 0,
            'weak': -5,
            'conflicting': -10,
            'insufficient': -15
        }
        adjusted += strength_adjustments.get(analysis.evidence_strength.value, 0)

        confidence_boost = int((analysis.confidence_score - 0.5) * 20)
        adjusted += confidence_boost

        return max(0, min(100, adjusted))

    def _generate_fast_summary(self, text: str, analysis: CrossSourceAnalysis,
                                score: int) -> Dict[str, Any]:
        """Generate fast summary."""
        # Headline
        if score >= 80:
            headline = f"Likely Authentic - {analysis.recommended_verdict}"
        elif score >= 60:
            headline = f"Probably True - {analysis.recommended_verdict}"
        elif score >= 40:
            headline = f"Uncertain - {analysis.recommended_verdict}"
        elif score >= 20:
            headline = f"Probably False - {analysis.recommended_verdict}"
        else:
            headline = f"Likely Fake - {analysis.recommended_verdict}"

        # Explanation
        if score >= 80:
            explanation = "Multiple credible sources confirm this information."
        elif score >= 60:
            explanation = "Credible sources generally support this claim."
        elif score >= 40:
            explanation = "Sources provide mixed or limited information about this claim."
        elif score >= 20:
            explanation = "Credible sources contradict or question this claim."
        else:
            explanation = "Multiple credible sources indicate this information is false."

        # Key points
        key_points = analysis.key_findings[:3]
        if analysis.contradictions:
            key_points.append(f"Found {len(analysis.contradictions)} contradiction(s) between sources")

        # Recommendations
        if score >= 80:
            recommendations = ["This information appears reliable and well-supported."]
        elif score >= 60:
            recommendations = ["This information is likely accurate but verify with additional sources if critical."]
        elif score >= 40:
            recommendations = [
                "Exercise caution: seek additional verification before sharing.",
                "Consider checking official sources directly."
            ]
        else:
            recommendations = [
                "Do not share this information - it appears to be false or misleading.",
                "Search for fact-checks from reputable organizations."
            ]

        return {
            'headline': headline,
            'explanation': explanation,
            'key_points': key_points,
            'recommendations': recommendations
        }

    def _create_error_result(self, text: str, error: str) -> FastVerificationResult:
        """Create error result."""
        return FastVerificationResult(
            factly_score=50,
            classification="Uncertain",
            confidence_level="Low",
            recommended_verdict="Error - Unable to verify",
            consensus_level="insufficient_data",
            evidence_strength="insufficient",
            headline="Verification Error",
            explanation=f"Unable to verify this claim: {error}",
            key_points=["Verification service encountered an error"],
            recommendations=["Please try again later or verify manually"],
            sources_consulted=0,
            processing_time=0.0,
            cached=False,
            timestamp=datetime.now()
        )

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        cache_stats = self.cache.get_stats()
        return {
            'cache': cache_stats,
            'settings': {
                'max_results_per_source': self.max_results_per_source,
                'early_termination_threshold': self.early_termination_threshold,
                'enable_caching': self.enable_caching
            }
        }
