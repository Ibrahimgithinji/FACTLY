"""
Verification Orchestrator

Main orchestration service that coordinates the entire verification workflow:
1. Claim extraction from input text
2. Multi-source evidence search
3. Cross-source analysis
4. Factly Score™ calculation
5. Summary generation

This is the primary entry point for the FACTLY verification system.
"""

import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime

from services.nlp_service.claim_extraction_service import ClaimExtractor, ExtractedClaim
from services.nlp_service.text_preprocessing import TextPreprocessor
from services.fact_checking_service.evidence_search_service import EvidenceSearchService, EvidenceCollection
from services.fact_checking_service.cross_source_analyzer import CrossSourceAnalyzer, CrossSourceAnalysis
from services.scoring_service.scoring_service import ScoringService, FactlyScoreResult
from services.fact_checking_service.unified_schema import VerificationResult
from services.fact_checking_service.cache_manager import CacheManager

logger = logging.getLogger(__name__)


@dataclass
class VerificationSummary:
    """Human-readable summary of verification results."""
    headline: str
    explanation: str
    key_points: List[str]
    recommendations: List[str]
    confidence_statement: str


@dataclass
class CompleteVerificationResult:
    """Complete verification result with all components."""
    # Input
    original_text: str
    extracted_claims: List[ExtractedClaim]
    primary_claim: Optional[ExtractedClaim]

    # Evidence
    evidence_collection: EvidenceCollection

    # Analysis
    cross_source_analysis: CrossSourceAnalysis

    # Scoring
    factly_score: int  # 0-100
    factly_score_result: FactlyScoreResult

    # Summary
    verification_summary: VerificationSummary

    # Metadata
    processing_time: float
    timestamp: datetime
    api_sources_used: List[str]


class VerificationOrchestrator:
    """
    Orchestrates the complete FACTLY verification workflow.

    Workflow:
    1. Extract claims from input text
    2. Search for evidence across multiple sources
    3. Analyze evidence for consensus/conflicts
    4. Calculate Factly Score™
    5. Generate human-readable summary
    """

    def __init__(self, cache_manager: Optional[CacheManager] = None):
        """
        Initialize the verification orchestrator.

        Args:
            cache_manager: Optional cache manager for caching results
        """
        self.cache = cache_manager or CacheManager()

        # Initialize component services
        self.claim_extractor = ClaimExtractor()
        self.text_preprocessor = TextPreprocessor()
        self.evidence_search = EvidenceSearchService(cache_manager=self.cache)
        self.cross_source_analyzer = CrossSourceAnalyzer()
        self.scoring_service = ScoringService()

        logger.info("VerificationOrchestrator initialized")

    def verify(self, text: str, language: str = "en",
               include_raw_evidence: bool = False) -> CompleteVerificationResult:
        """
        Perform complete verification of input text.

        Args:
            text: Text to verify (headline, article, or claim)
            language: Language code
            include_raw_evidence: Whether to include raw evidence in output

        Returns:
            CompleteVerificationResult with all verification data
        """
        import time
        start_time = time.time()

        logger.info(f"Starting verification for text ({len(text)} chars)")

        # Step 1: Extract claims
        extracted_claims = self.claim_extractor.extract_claims(text, min_confidence=0.4)
        primary_claim = self.claim_extractor.get_primary_claim(text)

        logger.info(f"Extracted {len(extracted_claims)} claims")

        # Use primary claim or full text for verification
        claim_to_verify = primary_claim.text if primary_claim else text

        # Step 2: Search for evidence
        evidence_collection = self.evidence_search.search_evidence(
            claim_to_verify, language=language
        )

        logger.info(f"Found {len(evidence_collection.evidence_items)} evidence items")

        # Step 3: Cross-source analysis
        cross_source_analysis = self.cross_source_analyzer.analyze(evidence_collection)

        logger.info(f"Cross-source analysis complete: {cross_source_analysis.consensus_level.value}")

        # Step 4: Calculate Factly Score™
        # Convert evidence to VerificationResult format for scoring service
        verification_result = self._convert_to_verification_result(
            claim_to_verify, evidence_collection
        )

        factly_score_result = self.scoring_service.calculate_factly_score(
            verification_result=verification_result,
            nlp_confidence=primary_claim.confidence if primary_claim else None,
            text_content=text
        )

        # Override score based on cross-source analysis
        adjusted_score = self._adjust_score_with_analysis(
            factly_score_result.factly_score,
            cross_source_analysis
        )

        logger.info(f"Factly Score™: {adjusted_score}/100")

        # Step 5: Generate summary
        verification_summary = self._generate_summary(
            text, primary_claim, cross_source_analysis, adjusted_score
        )

        processing_time = time.time() - start_time

        # Collect API sources used
        api_sources = list(set(
            item.source for item in evidence_collection.evidence_items
        ))

        return CompleteVerificationResult(
            original_text=text,
            extracted_claims=extracted_claims,
            primary_claim=primary_claim,
            evidence_collection=evidence_collection,
            cross_source_analysis=cross_source_analysis,
            factly_score=adjusted_score,
            factly_score_result=factly_score_result,
            verification_summary=verification_summary,
            processing_time=processing_time,
            timestamp=datetime.now(),
            api_sources_used=api_sources
        )

    def verify_quick(self, text: str, language: str = "en") -> Dict[str, Any]:
        """
        Quick verification that returns essential results only.

        Args:
            text: Text to verify
            language: Language code

        Returns:
            Dictionary with essential verification results
        """
        result = self.verify(text, language, include_raw_evidence=False)

        return {
            'factly_score': result.factly_score,
            'classification': result.factly_score_result.classification,
            'confidence_level': result.factly_score_result.confidence_level,
            'recommended_verdict': result.cross_source_analysis.recommended_verdict,
            'consensus_level': result.cross_source_analysis.consensus_level.value,
            'evidence_strength': result.cross_source_analysis.evidence_strength.value,
            'summary': {
                'headline': result.verification_summary.headline,
                'explanation': result.verification_summary.explanation,
                'key_points': result.verification_summary.key_points
            },
            'sources_consulted': len(result.evidence_collection.evidence_items),
            'processing_time': result.processing_time
        }

    def _convert_to_verification_result(self, claim: str,
                                        evidence: EvidenceCollection) -> VerificationResult:
        """Convert evidence collection to VerificationResult format."""
        from .unified_schema import ClaimReview, RelatedNews, SourceReliability, PublisherCredibility

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
        """
        Adjust Factly Score™ based on cross-source analysis.

        This ensures the score reflects the nuanced analysis of source agreement
        and evidence quality.
        """
        # Start with base score
        adjusted = base_score

        # Adjust based on consensus level
        consensus_adjustments = {
            'strong_agreement': 5,
            'moderate_agreement': 0,
            'mixed': -5,
            'moderate_disagreement': -10,
            'strong_disagreement': -15,
            'insufficient_data': -10
        }
        adjusted += consensus_adjustments.get(analysis.consensus_level.value, 0)

        # Adjust based on evidence strength
        strength_adjustments = {
            'strong': 5,
            'moderate': 0,
            'weak': -5,
            'conflicting': -10,
            'insufficient': -15
        }
        adjusted += strength_adjustments.get(analysis.evidence_strength.value, 0)

        # Adjust based on confidence
        confidence_boost = int((analysis.confidence_score - 0.5) * 20)
        adjusted += confidence_boost

        # Ensure score stays within 0-100
        return max(0, min(100, adjusted))

    def _generate_summary(self, original_text: str,
                          primary_claim: Optional[ExtractedClaim],
                          analysis: CrossSourceAnalysis,
                          score: int) -> VerificationSummary:
        """Generate human-readable verification summary."""

        # Generate headline based on score and verdict
        headline = self._generate_headline(score, analysis.recommended_verdict)

        # Generate explanation
        explanation = self._generate_explanation(analysis, score)

        # Generate key points
        key_points = self._generate_key_points(analysis)

        # Generate recommendations
        recommendations = self._generate_recommendations(analysis, score)

        # Generate confidence statement
        confidence_statement = self._generate_confidence_statement(analysis)

        return VerificationSummary(
            headline=headline,
            explanation=explanation,
            key_points=key_points,
            recommendations=recommendations,
            confidence_statement=confidence_statement
        )

    def _generate_headline(self, score: int, verdict: str) -> str:
        """Generate summary headline."""
        if score >= 80:
            return f"Likely Authentic - {verdict}"
        elif score >= 60:
            return f"Probably True - {verdict}"
        elif score >= 40:
            return f"Uncertain - {verdict}"
        elif score >= 20:
            return f"Probably False - {verdict}"
        else:
            return f"Likely Fake - {verdict}"

    def _generate_explanation(self, analysis: CrossSourceAnalysis, score: int) -> str:
        """Generate detailed explanation."""
        parts = []

        # Overall assessment
        if score >= 80:
            parts.append("Multiple credible sources confirm this information.")
        elif score >= 60:
            parts.append("Credible sources generally support this claim.")
        elif score >= 40:
            parts.append("Sources provide mixed or limited information about this claim.")
        elif score >= 20:
            parts.append("Credible sources contradict or question this claim.")
        else:
            parts.append("Multiple credible sources indicate this information is false.")

        # Source information
        num_sources = len(analysis.source_analyses)
        if num_sources > 0:
            parts.append(f"Analysis based on {num_sources} source(s).")

        # Consensus information
        if analysis.consensus_level.value == 'strong_agreement':
            parts.append("Sources strongly agree on this topic.")
        elif analysis.consensus_level.value == 'strong_disagreement':
            parts.append("Sources strongly disagree on this topic.")
        elif analysis.consensus_level.value == 'mixed':
            parts.append("Sources present conflicting viewpoints.")

        return " ".join(parts)

    def _generate_key_points(self, analysis: CrossSourceAnalysis) -> List[str]:
        """Generate key finding points."""
        points = []

        # Add key findings from analysis
        points.extend(analysis.key_findings[:3])

        # Add contradiction info if present
        if analysis.contradictions:
            points.append(f"Found {len(analysis.contradictions)} contradiction(s) between sources")

        # Add uncertainty factors
        if analysis.uncertainty_factors:
            points.append(f"Note: {analysis.uncertainty_factors[0]}")

        return points

    def _generate_recommendations(self, analysis: CrossSourceAnalysis, score: int) -> List[str]:
        """Generate recommendations for the user."""
        recommendations = []

        if score >= 80:
            recommendations.append("This information appears reliable and well-supported.")
        elif score >= 60:
            recommendations.append("This information is likely accurate but verify with additional sources if critical.")
        elif score >= 40:
            recommendations.append("Exercise caution: seek additional verification before sharing.")
            recommendations.append("Consider checking official sources directly.")
        else:
            recommendations.append("Do not share this information - it appears to be false or misleading.")
            recommendations.append("Search for fact-checks from reputable organizations.")

        if analysis.uncertainty_factors:
            recommendations.append("Be aware of limitations in the available evidence.")

        return recommendations

    def _generate_confidence_statement(self, analysis: CrossSourceAnalysis) -> str:
        """Generate confidence level statement."""
        confidence_pct = int(analysis.confidence_score * 100)

        if confidence_pct >= 80:
            return f"High confidence ({confidence_pct}%) - Strong evidence from multiple credible sources"
        elif confidence_pct >= 60:
            return f"Medium confidence ({confidence_pct}%) - Good evidence but some limitations"
        elif confidence_pct >= 40:
            return f"Low confidence ({confidence_pct}%) - Limited or conflicting evidence"
        else:
            return f"Very low confidence ({confidence_pct}%) - Insufficient evidence to make determination"
