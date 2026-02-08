"""
Factly Score™ Credibility Scoring Service - Enhanced Version

Implements an advanced weighted credibility scoring algorithm that combines multiple
fact-checking and NLP analysis components to produce a unified credibility score.
This enhanced version includes better fact-checking integration and more accurate scoring.
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import time
import re

from ..fact_checking_service.unified_schema import VerificationResult, ClaimReview
from ..nlp_service.text_preprocessing import TextPreprocessor

logger = logging.getLogger(__name__)


@dataclass
class ComponentScore:
    """Represents a score component with justification."""
    name: str
    score: float  # 0.0 to 1.0
    weight: float  # 0.0 to 1.0
    weighted_score: float
    justification: str
    evidence: List[str]


@dataclass
class FactlyScoreResult:
    """Complete Factly Score™ result with classification and evidence."""
    factly_score: int  # 0-100
    classification: str  # "Likely Fake", "Uncertain", "Likely Authentic"
    confidence_level: str  # "Low", "Medium", "High"
    components: List[ComponentScore]
    justifications: List[str]
    evidence_summary: Dict[str, Any]
    timestamp: datetime
    metadata: Dict[str, Any]
    processing_time: float  # Time in seconds to calculate the score


class ScoringService:
    """Enhanced service for computing Factly Score™ credibility assessments."""

    # Updated Scoring weights (sum to 1.0) - giving more weight to fact-check results
    WEIGHTS = {
        'fact_check_consensus': 0.45,    # Google Fact Check results (increased)
        'source_credibility': 0.25,      # Source reliability assessment
        'evidence_quality': 0.20,        # Quality and quantity of evidence
        'content_analysis': 0.10         # Content bias & tone analysis
    }

    # Classification thresholds
    CLASSIFICATION_THRESHOLDS = {
        'Likely Fake': (0, 35),
        'Uncertain': (36, 65),
        'Likely Authentic': (66, 100)
    }

    # Verdict to score mapping with more granularity
    VERDICT_SCORES = {
        'true': 1.0,
        'mostly true': 0.85,
        'half true': 0.60,
        'mixed': 0.50,
        'mostly false': 0.25,
        'false': 0.10,
        'misleading': 0.30,
        'unverified': 0.50,
        'satire': 0.15,
        'correct': 1.0,
        'incorrect': 0.10,
        'verified': 0.95,
        'partially true': 0.55
    }

    def __init__(self):
        """Initialize the scoring service."""
        self.text_preprocessor = TextPreprocessor()

    def calculate_factly_score(
        self,
        verification_result: VerificationResult,
        nlp_confidence: Optional[float] = None,
        text_content: Optional[str] = None
    ) -> FactlyScoreResult:
        """
        Calculate the enhanced Factly Score™ for a given verification result.

        Args:
            verification_result: Result from fact-checking services
            nlp_confidence: Optional NLP model confidence score (0.0-1.0)
            text_content: Optional text content for bias/tone analysis

        Returns:
            Complete Factly Score™ result
        """
        logger.info(f"Calculating enhanced Factly Score™ for claim: {verification_result.original_claim[:100]}...")

        # Track processing time
        start_time = time.time()

        # Calculate component scores
        components = []

        # 1. Fact-Check Consensus (45%) - Most important factor
        fact_check_score = self._calculate_fact_check_consensus(verification_result)
        components.append(fact_check_score)

        # 2. Source Credibility (25%)
        credibility_score = self._calculate_source_credibility(verification_result)
        components.append(credibility_score)

        # 3. Evidence Quality (20%)
        evidence_score = self._calculate_evidence_quality(verification_result)
        components.append(evidence_score)

        # 4. Content Analysis (10%)
        content_score = self._calculate_content_analysis(text_content or verification_result.original_claim)
        components.append(content_score)

        # Calculate final weighted score
        total_weighted_score = sum(comp.weighted_score for comp in components)
        factly_score = int(round(total_weighted_score * 100))  # Convert to 0-100 scale
        
        # Calculate processing time
        processing_time = time.time() - start_time

        # Determine classification
        classification = self._classify_score(factly_score)

        # Determine confidence level
        confidence_level = self._calculate_confidence_level(components, verification_result)

        # Generate justifications
        justifications = self._generate_justifications(components, factly_score, verification_result)

        # Create evidence summary
        evidence_summary = self._create_evidence_summary(verification_result, components)

        return FactlyScoreResult(
            factly_score=factly_score,
            classification=classification,
            confidence_level=confidence_level,
            components=components,
            justifications=justifications,
            evidence_summary=evidence_summary,
            timestamp=datetime.now(),
            metadata={
                'original_claim': verification_result.original_claim,
                'api_sources': verification_result.api_sources,
                'processing_timestamp': datetime.now().isoformat(),
                'total_claim_reviews': len(verification_result.claim_reviews),
                'total_related_news': len(verification_result.related_news)
            },
            processing_time=processing_time
        )

    def _calculate_fact_check_consensus(self, verification_result: VerificationResult) -> ComponentScore:
        """
        Calculate score based on fact-check consensus across multiple sources.
        This is the most heavily weighted component.
        """
        claim_reviews = verification_result.claim_reviews

        if not claim_reviews:
            score = 0.5  # Neutral when no reviews found
            justification = "No fact-check reviews found - insufficient data for verification"
            evidence = ["No claim reviews available from fact-checking APIs"]
        else:
            # Calculate weighted average based on publisher credibility and review confidence
            total_weighted_score = 0.0
            total_weight = 0.0
            review_details = []

            for review in claim_reviews:
                # Map verdict to numerical score
                verdict_score = self._map_verdict_to_score(review.verdict)
                
                # Get publisher credibility (default to 0.7 if not available)
                publisher_weight = getattr(review.publisher, 'credibility_score', 0.7)
                
                # Get review confidence (default to 0.8 if not available)
                confidence = getattr(review, 'confidence_score', 0.8)
                
                # Calculate weighted contribution
                weight = publisher_weight * confidence
                total_weighted_score += verdict_score * weight
                total_weight += weight
                
                review_details.append(
                    f"{review.publisher.name}: {review.verdict} (confidence: {confidence:.2f})"
                )

            if total_weight > 0:
                score = total_weighted_score / total_weight
            else:
                score = 0.5

            # Adjust score based on number of reviews (more reviews = more confidence)
            review_count_factor = min(1.0, len(claim_reviews) / 5.0)  # Max bonus at 5+ reviews
            score = score * (0.7 + 0.3 * review_count_factor)  # Scale between 70-100% of original

            justification = f"Fact-check consensus from {len(claim_reviews)} sources"
            evidence = [
                f"Analyzed {len(claim_reviews)} fact-check reviews",
                f"Average verdict score: {score:.2f}",
                "Sources: " + ", ".join(review_details[:5])  # Show top 5
            ]

        weight = self.WEIGHTS['fact_check_consensus']
        weighted_score = score * weight

        return ComponentScore(
            name="Fact-Check Consensus",
            score=score,
            weight=weight,
            weighted_score=weighted_score,
            justification=justification,
            evidence=evidence
        )

    def _calculate_source_credibility(self, verification_result: VerificationResult) -> ComponentScore:
        """Calculate score based on source credibility assessment."""
        source_reliability = verification_result.source_reliability
        related_news = verification_result.related_news

        if source_reliability is None and not related_news:
            score = 0.5
            justification = "No source credibility data available"
            evidence = ["Source reliability assessment not available"]
        else:
            scores = []
            sources_analyzed = []

            # Primary source reliability
            if source_reliability:
                reliability = getattr(source_reliability, 'reliability_score', 0.5)
                factual = getattr(source_reliability, 'factual_reporting', 0.5)
                scores.append((reliability + factual) / 2.0)
                sources_analyzed.append(getattr(source_reliability, 'source_name', 'Unknown'))

            # Related news sources
            # Note: RelatedNews doesn't have source_credibility, so we use relevance_score as proxy
            # In production, you'd want to look up source credibility from a database
            for news in related_news[:5]:  # Consider top 5 related articles
                # Use relevance_score as a proxy for source credibility when not available
                source_score = getattr(news, 'relevance_score', 0.5)
                relevance = getattr(news, 'relevance_score', 0.5)
                weighted = source_score * relevance
                scores.append(weighted)
                sources_analyzed.append(getattr(news, 'source', 'Unknown'))

            score = sum(scores) / len(scores) if scores else 0.5

            justification = f"Source credibility from {len(sources_analyzed)} sources"
            evidence = [
                f"Analyzed {len(sources_analyzed)} sources",
                f"Average credibility: {score:.2f}",
                f"Sources: {', '.join(sources_analyzed[:5])}"
            ]

        weight = self.WEIGHTS['source_credibility']
        weighted_score = score * weight

        return ComponentScore(
            name="Source Credibility",
            score=score,
            weight=weight,
            weighted_score=weighted_score,
            justification=justification,
            evidence=evidence
        )

    def _calculate_evidence_quality(self, verification_result: VerificationResult) -> ComponentScore:
        """Calculate score based on evidence quality and quantity."""
        claim_reviews = verification_result.claim_reviews
        related_news = verification_result.related_news

        # Base score on evidence quantity
        review_count = len(claim_reviews)
        news_count = len(related_news)
        
        # Calculate evidence score (more evidence = higher score, with diminishing returns)
        review_score = min(1.0, review_count / 3.0)  # Max at 3+ reviews
        news_score = min(1.0, news_count / 5.0)      # Max at 5+ news articles
        
        # Weight reviews more heavily than news
        score = (review_score * 0.7) + (news_score * 0.3)

        if review_count == 0 and news_count == 0:
            score = 0.3  # Low score when no evidence
            justification = "Limited evidence available"
        else:
            justification = f"Evidence quality: {review_count} reviews, {news_count} related articles"

        evidence = [
            f"Fact-check reviews: {review_count}",
            f"Related news articles: {news_count}",
            f"Evidence coverage score: {score:.2f}"
        ]

        weight = self.WEIGHTS['evidence_quality']
        weighted_score = score * weight

        return ComponentScore(
            name="Evidence Quality",
            score=score,
            weight=weight,
            weighted_score=weighted_score,
            justification=justification,
            evidence=evidence
        )

    def _calculate_content_analysis(self, text: str) -> ComponentScore:
        """Enhanced content analysis for bias and credibility indicators."""
        # Analyze multiple factors
        bias_indicators = self._analyze_bias_indicators(text)
        sensationalism = self._analyze_sensationalism(text)
        citation_quality = self._analyze_citations(text)
        
        # Calculate individual scores
        bias_score = 1.0 - min(1.0, bias_indicators / 5.0)
        sensationalism_score = 1.0 - min(1.0, sensationalism / 5.0)
        
        # Combine scores
        score = (bias_score * 0.4) + (sensationalism_score * 0.4) + (citation_quality * 0.2)

        justification = f"Content analysis: bias={bias_indicators}, sensationalism={sensationalism}"
        evidence = [
            f"Bias indicators: {bias_indicators}",
            f"Sensationalism markers: {sensationalism}",
            f"Citation quality: {citation_quality:.2f}",
            f"Overall content score: {score:.2f}"
        ]

        weight = self.WEIGHTS['content_analysis']
        weighted_score = score * weight

        return ComponentScore(
            name="Content Analysis",
            score=score,
            weight=weight,
            weighted_score=weighted_score,
            justification=justification,
            evidence=evidence
        )

    def _map_verdict_to_score(self, verdict: str) -> float:
        """Map fact-check verdict to numerical score with better normalization."""
        if not verdict:
            return 0.5
        
        verdict_lower = verdict.lower().strip()
        
        # Direct match
        if verdict_lower in self.VERDICT_SCORES:
            return self.VERDICT_SCORES[verdict_lower]
        
        # Partial match
        for key, score in self.VERDICT_SCORES.items():
            if key in verdict_lower or verdict_lower in key:
                return score
        
        return 0.5  # Default for unknown verdicts

    def _analyze_bias_indicators(self, text: str) -> int:
        """Enhanced bias indicator detection."""
        bias_patterns = [
            r'\b(conspiracy|hoax|fake news|propaganda)\b',
            r'\b(mainstream media|liberal media|conservative media)\b',
            r'\b(deep state|illuminati|new world order)\b',
            r'\b(they don\'t want you to know|wake up sheeple)\b',
            r'\b(crisis actor|false flag|inside job)\b'
        ]
        
        text_lower = text.lower()
        count = 0
        for pattern in bias_patterns:
            matches = re.findall(pattern, text_lower)
            count += len(matches)
        
        return count

    def _analyze_sensationalism(self, text: str) -> int:
        """Analyze text for sensationalism markers."""
        sensational_words = [
            'shocking', 'outrageous', 'unbelievable', 'scandalous',
            'devastating', 'catastrophic', 'terrifying', 'mind-blowing',
            'you won\'t believe', 'this changes everything', 'what happens next',
            'doctors hate this', 'secret they don\'t want you to know'
        ]
        
        text_lower = text.lower()
        count = sum(1 for word in sensational_words if word in text_lower)
        
        # Also check for excessive punctuation
        exclamation_count = text.count('!')
        if exclamation_count > 2:
            count += 1
        
        # Check for ALL CAPS words
        caps_words = len([w for w in text.split() if w.isupper() and len(w) > 2])
        if caps_words > 2:
            count += 1
        
        return count

    def _analyze_citations(self, text: str) -> float:
        """Analyze quality of citations and references in text."""
        score = 0.5  # Base score
        
        # Check for named sources
        source_patterns = [
            r'according to [A-Z][a-z]+',
            r'said [A-Z][a-z]+',
            r'reported by [A-Z][a-z]+',
            r'\b(?:Reuters|AP|BBC|CNN|NBC|CBS|ABC|Fox|NYT|Washington Post)\b'
        ]
        
        for pattern in source_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                score += 0.1
        
        # Check for dates
        if re.search(r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\b \d{1,2},? \d{4}', text):
            score += 0.1
        
        # Check for statistics/numbers
        if re.search(r'\d+%|\d+ percent', text):
            score += 0.1
        
        return min(1.0, score)

    def _classify_score(self, score: int) -> str:
        """Classify the Factly Score™ into categories."""
        for category, (min_score, max_score) in self.CLASSIFICATION_THRESHOLDS.items():
            if min_score <= score <= max_score:
                return category
        return "Uncertain"

    def _calculate_confidence_level(self, components: List[ComponentScore], verification_result: VerificationResult) -> str:
        """Calculate overall confidence level based on component consistency and evidence quantity."""
        scores = [comp.score for comp in components]
        variance = sum((score - sum(scores)/len(scores))**2 for score in scores) / len(scores)
        
        # Factor in evidence quantity
        evidence_bonus = 0.0
        if len(verification_result.claim_reviews) >= 3:
            evidence_bonus += 0.1
        if verification_result.source_reliability:
            evidence_bonus += 0.05
        
        adjusted_variance = max(0, variance - evidence_bonus)
        
        if adjusted_variance < 0.08:
            return "High"
        elif adjusted_variance < 0.20:
            return "Medium"
        else:
            return "Low"

    def _generate_justifications(self, components: List[ComponentScore], final_score: int, verification_result: VerificationResult) -> List[str]:
        """Generate comprehensive human-readable justifications for the score."""
        justifications = []
        
        # Overall assessment
        classification = self._classify_score(final_score)
        justifications.append(f"Factly Score™ of {final_score}/100 indicates {classification.lower()} credibility.")
        
        # Key findings from fact-checks
        claim_reviews = verification_result.claim_reviews
        if claim_reviews:
            true_count = sum(1 for r in claim_reviews if self._map_verdict_to_score(r.verdict) >= 0.7)
            false_count = sum(1 for r in claim_reviews if self._map_verdict_to_score(r.verdict) <= 0.3)
            
            if true_count > false_count:
                justifications.append(f"Majority of fact-checkers ({true_count}/{len(claim_reviews)}) rate this as credible.")
            elif false_count > true_count:
                justifications.append(f"Majority of fact-checkers ({false_count}/{len(claim_reviews)}) question this claim's accuracy.")
            else:
                justifications.append("Fact-checkers have mixed opinions on this claim.")
        
        # Component breakdown
        for comp in components:
            if comp.weighted_score > 0.15:  # Only mention significant contributors
                justifications.append(f"{comp.name}: {comp.justification}")
        
        # Evidence summary
        if not claim_reviews and not verification_result.related_news:
            justifications.append("Limited evidence available - verification based primarily on content analysis.")
        
        return justifications

    def _create_evidence_summary(
        self,
        verification_result: VerificationResult,
        components: List[ComponentScore]
    ) -> Dict[str, Any]:
        """Create a comprehensive summary of evidence supporting the score."""
        claim_reviews = verification_result.claim_reviews
        
        # Calculate verdict distribution
        verdict_counts = {}
        for review in claim_reviews:
            verdict = review.verdict.lower() if review.verdict else 'unknown'
            verdict_counts[verdict] = verdict_counts.get(verdict, 0) + 1
        
        return {
            'claim_reviews_count': len(claim_reviews),
            'related_news_count': len(verification_result.related_news),
            'verdict_distribution': verdict_counts,
            'source_reliability_available': verification_result.source_reliability is not None,
            'component_breakdown': {
                comp.name: {
                    'score': round(comp.score, 2),
                    'weight': comp.weight,
                    'weighted_score': round(comp.weighted_score, 2)
                } for comp in components
            },
            'api_sources_used': verification_result.api_sources,
            'overall_confidence': verification_result.overall_confidence,
            'top_fact_check_sources': [
                {
                    'publisher': r.publisher.name if hasattr(r, 'publisher') else 'Unknown',
                    'verdict': r.verdict,
                    'url': r.url if hasattr(r, 'url') else None
                }
                for r in claim_reviews[:5]
            ]
        }
