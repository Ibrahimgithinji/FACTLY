"""
Cross-Source Analysis Service

Analyzes evidence from multiple sources to determine:
- Source agreement/consensus
- Conflicting information detection
- Evidence strength assessment
- Bias detection across sources
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from collections import Counter

from .evidence_search_service import EvidenceItem, EvidenceCollection

logger = logging.getLogger(__name__)


class ConsensusLevel(Enum):
    """Level of consensus among sources."""
    STRONG_AGREEMENT = "strong_agreement"
    MODERATE_AGREEMENT = "moderate_agreement"
    MIXED = "mixed"
    MODERATE_DISAGREEMENT = "moderate_disagreement"
    STRONG_DISAGREEMENT = "strong_disagreement"
    INSUFFICIENT_DATA = "insufficient_data"


class EvidenceStrength(Enum):
    """Strength of evidence for a claim."""
    STRONG = "strong"  # Multiple high-credibility sources agree
    MODERATE = "moderate"  # Some agreement among credible sources
    WEAK = "weak"  # Limited or low-credibility sources
    CONFLICTING = "conflicting"  # Sources disagree
    INSUFFICIENT = "insufficient"  # Not enough evidence


@dataclass
class SourceAnalysis:
    """Analysis of a single source's position."""
    source_name: str
    source_type: str
    credibility_score: float
    verdict: Optional[str]
    verdict_score: float  # 0.0 to 1.0
    relevance_score: float
    supporting_evidence: List[str]
    contradictions: List[str]


@dataclass
class CrossSourceAnalysis:
    """Complete cross-source analysis result."""
    claim: str
    consensus_level: ConsensusLevel
    evidence_strength: EvidenceStrength
    source_analyses: List[SourceAnalysis]
    agreement_score: float  # 0.0 to 1.0
    confidence_score: float  # 0.0 to 1.0
    key_findings: List[str]
    contradictions: List[Dict[str, Any]]
    recommended_verdict: str
    uncertainty_factors: List[str]


class CrossSourceAnalyzer:
    """
    Analyzes evidence across multiple sources to determine credibility.
    
    Key principles:
    1. Multiple independent sources > single source
    2. High-credibility sources weighted more heavily
    3. Agreement among diverse sources increases confidence
    4. Conflicting evidence reduces certainty
    5. Missing evidence types create uncertainty
    """

    # Verdict mappings for normalization
    VERDICT_MAPPINGS = {
        # True variants
        'true': 'true',
        'mostly true': 'mostly_true',
        'correct': 'true',
        'accurate': 'true',
        'verified': 'true',
        # False variants
        'false': 'false',
        'mostly false': 'mostly_false',
        'incorrect': 'false',
        'inaccurate': 'false',
        'pants on fire': 'false',
        # Mixed variants
        'misleading': 'misleading',
        'half true': 'half_true',
        'partly true': 'half_true',
        'partly false': 'half_true',
        'mixed': 'mixed',
        'unverified': 'unverified',
        'satire': 'satire',
    }

    # Numerical scores for verdicts
    VERDICT_SCORES = {
        'true': 1.0,
        'mostly_true': 0.85,
        'half_true': 0.6,
        'mixed': 0.5,
        'mostly_false': 0.3,
        'false': 0.0,
        'misleading': 0.4,
        'unverified': 0.5,
        'satire': 0.2
    }

    def __init__(self):
        """Initialize the cross-source analyzer."""
        self.min_sources_for_consensus = 2
        self.high_credibility_threshold = 0.8
        self.agreement_threshold = 0.7

    def analyze(self, evidence_collection: EvidenceCollection) -> CrossSourceAnalysis:
        """
        Perform cross-source analysis on evidence collection.

        Args:
            evidence_collection: Collection of evidence from multiple sources

        Returns:
            CrossSourceAnalysis with comprehensive analysis
        """
        logger.info(f"Analyzing {len(evidence_collection.evidence_items)} evidence items")

        evidence_items = evidence_collection.evidence_items

        if not evidence_items:
            return self._create_insufficient_analysis(evidence_collection.claim)

        # Analyze individual sources
        source_analyses = self._analyze_sources(evidence_items)

        # Calculate agreement
        agreement_score = self._calculate_agreement(source_analyses)

        # Determine consensus level
        consensus_level = self._determine_consensus(agreement_score, len(source_analyses))

        # Determine evidence strength
        evidence_strength = self._determine_evidence_strength(
            source_analyses, consensus_level, evidence_collection
        )

        # Calculate overall confidence
        confidence_score = self._calculate_confidence(
            source_analyses, agreement_score, evidence_collection
        )

        # Identify key findings
        key_findings = self._identify_key_findings(source_analyses, consensus_level)

        # Identify contradictions
        contradictions = self._identify_contradictions(source_analyses)

        # Determine recommended verdict
        recommended_verdict = self._determine_recommended_verdict(source_analyses, consensus_level)

        # Identify uncertainty factors
        uncertainty_factors = self._identify_uncertainty_factors(
            source_analyses, evidence_collection
        )

        return CrossSourceAnalysis(
            claim=evidence_collection.claim,
            consensus_level=consensus_level,
            evidence_strength=evidence_strength,
            source_analyses=source_analyses,
            agreement_score=agreement_score,
            confidence_score=confidence_score,
            key_findings=key_findings,
            contradictions=contradictions,
            recommended_verdict=recommended_verdict,
            uncertainty_factors=uncertainty_factors
        )

    def _analyze_sources(self, evidence_items: List[EvidenceItem]) -> List[SourceAnalysis]:
        """Analyze each source's position and credibility."""
        analyses = []

        for item in evidence_items:
            # Normalize verdict
            normalized_verdict = self._normalize_verdict(item.verdict)
            verdict_score = self.VERDICT_SCORES.get(normalized_verdict, 0.5)

            analysis = SourceAnalysis(
                source_name=item.source,
                source_type=item.source_type,
                credibility_score=item.credibility_score,
                verdict=item.verdict,
                verdict_score=verdict_score,
                relevance_score=item.relevance_score,
                supporting_evidence=[],
                contradictions=[]
            )
            analyses.append(analysis)

        # Now identify supporting evidence and contradictions
        for i, analysis in enumerate(analyses):
            for j, other in enumerate(analyses):
                if i != j:
                    if self._verdicts_agree(analysis.verdict_score, other.verdict_score):
                        analysis.supporting_evidence.append(other.source_name)
                    else:
                        analysis.contradictions.append(other.source_name)

        return analyses

    def _normalize_verdict(self, verdict: Optional[str]) -> str:
        """Normalize verdict to standard form."""
        if not verdict:
            return 'unverified'
        return self.VERDICT_MAPPINGS.get(verdict.lower(), 'unverified')

    def _verdicts_agree(self, score1: float, score2: float, threshold: float = 0.3) -> bool:
        """Check if two verdict scores agree within threshold."""
        return abs(score1 - score2) <= threshold

    def _calculate_agreement(self, source_analyses: List[SourceAnalysis]) -> float:
        """Calculate overall agreement score among sources."""
        if len(source_analyses) < 2:
            return 0.5  # Neutral when only one source

        # Get weighted verdict scores
        weighted_scores = []
        for analysis in source_analyses:
            weight = analysis.credibility_score * analysis.relevance_score
            weighted_scores.append((analysis.verdict_score, weight))

        if not weighted_scores:
            return 0.5

        # Calculate weighted mean
        total_weight = sum(w for _, w in weighted_scores)
        if total_weight == 0:
            return 0.5

        weighted_mean = sum(s * w for s, w in weighted_scores) / total_weight

        # Calculate weighted variance
        weighted_variance = sum(
            w * (s - weighted_mean) ** 2 for s, w in weighted_scores
        ) / total_weight

        # Convert variance to agreement (lower variance = higher agreement)
        agreement = 1.0 - min(1.0, weighted_variance * 4)

        return max(0.0, min(1.0, agreement))

    def _determine_consensus(self, agreement_score: float,
                             num_sources: int) -> ConsensusLevel:
        """Determine the level of consensus among sources."""
        if num_sources < self.min_sources_for_consensus:
            return ConsensusLevel.INSUFFICIENT_DATA

        if agreement_score >= 0.8:
            return ConsensusLevel.STRONG_AGREEMENT
        elif agreement_score >= 0.6:
            return ConsensusLevel.MODERATE_AGREEMENT
        elif agreement_score >= 0.4:
            return ConsensusLevel.MIXED
        elif agreement_score >= 0.2:
            return ConsensusLevel.MODERATE_DISAGREEMENT
        else:
            return ConsensusLevel.STRONG_DISAGREEMENT

    def _determine_evidence_strength(self, source_analyses: List[SourceAnalysis],
                                      consensus: ConsensusLevel,
                                      collection: EvidenceCollection) -> EvidenceStrength:
        """Determine the overall strength of evidence."""
        if len(source_analyses) < 2:
            return EvidenceStrength.INSUFFICIENT

        # Count high-credibility sources
        high_cred_sources = sum(
            1 for sa in source_analyses
            if sa.credibility_score >= self.high_credibility_threshold
        )

        # Check for conflicts
        has_conflicts = consensus in [
            ConsensusLevel.MODERATE_DISAGREEMENT,
            ConsensusLevel.STRONG_DISAGREEMENT
        ]

        if has_conflicts:
            return EvidenceStrength.CONFLICTING

        if high_cred_sources >= 2 and consensus == ConsensusLevel.STRONG_AGREEMENT:
            return EvidenceStrength.STRONG
        elif high_cred_sources >= 1 and consensus in [
            ConsensusLevel.STRONG_AGREEMENT,
            ConsensusLevel.MODERATE_AGREEMENT
        ]:
            return EvidenceStrength.MODERATE
        elif consensus == ConsensusLevel.MIXED:
            return EvidenceStrength.WEAK
        else:
            return EvidenceStrength.INSUFFICIENT

    def _calculate_confidence(self, source_analyses: List[SourceAnalysis],
                               agreement_score: float,
                               collection: EvidenceCollection) -> float:
        """Calculate overall confidence in the analysis."""
        if not source_analyses:
            return 0.0

        # Factors affecting confidence:
        # 1. Number of sources (more = better, up to a point)
        num_sources = len(source_analyses)
        source_factor = min(1.0, num_sources / 5)  # Max at 5 sources

        # 2. Average credibility of sources
        avg_credibility = sum(sa.credibility_score for sa in source_analyses) / num_sources

        # 3. Agreement among sources
        agreement_factor = agreement_score

        # 4. Source diversity
        diversity_factor = collection.source_diversity_score

        # Weighted combination
        confidence = (
            source_factor * 0.2 +
            avg_credibility * 0.35 +
            agreement_factor * 0.30 +
            diversity_factor * 0.15
        )

        return max(0.0, min(1.0, confidence))

    def _identify_key_findings(self, source_analyses: List[SourceAnalysis],
                                consensus: ConsensusLevel) -> List[str]:
        """Identify key findings from the analysis."""
        findings = []

        # Count verdicts
        verdicts = Counter(sa.verdict for sa in source_analyses if sa.verdict)

        if verdicts:
            most_common = verdicts.most_common(1)[0]
            findings.append(
                f"Most common verdict: '{most_common[0]}' "
                f"({most_common[1]} of {len(source_analyses)} sources)"
            )

        # High credibility sources
        high_cred = [sa for sa in source_analyses
                     if sa.credibility_score >= self.high_credibility_threshold]
        if high_cred:
            findings.append(
                f"{len(high_cred)} high-credibility source(s) consulted"
            )

        # Consensus description
        if consensus == ConsensusLevel.STRONG_AGREEMENT:
            findings.append("Strong consensus among sources")
        elif consensus == ConsensusLevel.MIXED:
            findings.append("Mixed results from sources")
        elif consensus in [ConsensusLevel.MODERATE_DISAGREEMENT,
                          ConsensusLevel.STRONG_DISAGREEMENT]:
            findings.append("Sources disagree on this claim")

        return findings

    def _identify_contradictions(self, source_analyses: List[SourceAnalysis]) -> List[Dict[str, Any]]:
        """Identify contradictions between sources."""
        contradictions = []

        for i, sa1 in enumerate(source_analyses):
            for sa2 in source_analyses[i+1:]:
                if not self._verdicts_agree(sa1.verdict_score, sa2.verdict_score, 0.4):
                    contradictions.append({
                        'source_1': sa1.source_name,
                        'verdict_1': sa1.verdict,
                        'source_2': sa2.source_name,
                        'verdict_2': sa2.verdict,
                        'difference': abs(sa1.verdict_score - sa2.verdict_score)
                    })

        return contradictions

    def _determine_recommended_verdict(self, source_analyses: List[SourceAnalysis],
                                        consensus: ConsensusLevel) -> str:
        """Determine the recommended verdict based on analysis."""
        if not source_analyses:
            return "Unverified"

        if consensus == ConsensusLevel.INSUFFICIENT_DATA:
            return "Unverified - Insufficient Data"

        # Calculate weighted average verdict
        weighted_sum = sum(
            sa.verdict_score * sa.credibility_score * sa.relevance_score
            for sa in source_analyses
        )
        total_weight = sum(
            sa.credibility_score * sa.relevance_score
            for sa in source_analyses
        )

        if total_weight == 0:
            return "Unverified"

        average_score = weighted_sum / total_weight

        # Map to verdict
        if average_score >= 0.9:
            return "True"
        elif average_score >= 0.7:
            return "Mostly True"
        elif average_score >= 0.5:
            return "Mixed / Unverified"
        elif average_score >= 0.3:
            return "Mostly False"
        else:
            return "False"

    def _identify_uncertainty_factors(self, source_analyses: List[SourceAnalysis],
                                       collection: EvidenceCollection) -> List[str]:
        """Identify factors contributing to uncertainty."""
        factors = []

        # Low number of sources
        if len(source_analyses) < 3:
            factors.append(f"Limited number of sources ({len(source_analyses)})")

        # Low credibility sources
        low_cred = [sa for sa in source_analyses if sa.credibility_score < 0.6]
        if low_cred:
            factors.append(f"{len(low_cred)} source(s) with lower credibility ratings")

        # Coverage gaps
        if collection.coverage_gaps:
            factors.extend(collection.coverage_gaps[:2])  # Top 2 gaps

        # Conflicting evidence
        if collection.agreement_score < 0.5:
            factors.append("Conflicting information from sources")

        return factors if factors else ["No significant uncertainty factors identified"]

    def _create_insufficient_analysis(self, claim: str) -> CrossSourceAnalysis:
        """Create analysis result for insufficient evidence."""
        return CrossSourceAnalysis(
            claim=claim,
            consensus_level=ConsensusLevel.INSUFFICIENT_DATA,
            evidence_strength=EvidenceStrength.INSUFFICIENT,
            source_analyses=[],
            agreement_score=0.0,
            confidence_score=0.0,
            key_findings=["No evidence found for this claim"],
            contradictions=[],
            recommended_verdict="Unverified - No Evidence",
            uncertainty_factors=["No sources available to verify this claim"]
        )
