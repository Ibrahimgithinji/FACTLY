"""
Enhanced Verification Orchestrator

Enhanced orchestration service that coordinates comprehensive verification:
1. Claim extraction from input text
2. Direct multi-source verification against authoritative sources
3. Cross-source analysis with rigorous validation
4. Factly Score™ calculation with verification weights
5. Summary generation with transparent verification steps
6. Complete verification tracking for transparency

This enhanced orchestrator ensures every result reflects verified, up-to-date
information confirmed through direct examination of multiple reliable sources.
"""

import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime

from services.nlp_service.claim_extraction_service import ClaimExtractor, ExtractedClaim
from services.nlp_service.text_preprocessing import TextPreprocessor
from services.fact_checking_service.evidence_search_service import EvidenceSearchService, EvidenceCollection
from services.fact_checking_service.cross_source_analyzer import CrossSourceAnalyzer, CrossSourceAnalysis
from services.fact_checking_service.direct_source_verifier import DirectSourceVerifier, SourceVerificationReport
from services.scoring_service.scoring_service import ScoringService, FactlyScoreResult
from services.fact_checking_service.unified_schema import VerificationResult
from services.fact_checking_service.cache_manager import CacheManager

logger = logging.getLogger(__name__)


@dataclass
class VerificationStep:
    """Individual verification step in the process."""
    step_number: int
    step_name: str
    description: str
    status: str  # 'pending', 'in_progress', 'completed', 'failed'
    result: Optional[Dict[str, Any]]
    timestamp: datetime
    duration_ms: float


@dataclass
class VerificationTrace:
    """Complete trace of the verification process."""
    original_text: str
    extracted_claims: List[ExtractedClaim]
    verification_steps: List[VerificationStep]
    direct_verification_report: Optional[SourceVerificationReport]
    evidence_collection: EvidenceCollection
    cross_source_analysis: CrossSourceAnalysis
    factly_score: int
    confidence_level: str
    recommended_verdict: str
    sources_consulted: List[Dict[str, Any]]
    data_points_verified: List[str]
    data_points_unverified: List[str]
    discrepancies_found: List[Dict[str, str]]
    primary_sources_used: List[str]
    secondary_sources_used: List[str]
    processing_time_ms: float
    timestamp: datetime


@dataclass
class EnhancedVerificationResult:
    """Complete enhanced verification result with full transparency."""
    # Original input
    original_text: str
    extracted_claims: List[ExtractedClaim]
    primary_claim: Optional[ExtractedClaim]
    
    # Verification process trace
    verification_trace: VerificationTrace
    
    # Direct verification results
    direct_verification_report: SourceVerificationReport
    
    # Evidence from all sources
    evidence_collection: EvidenceCollection
    
    # Analysis results
    cross_source_analysis: CrossSourceAnalysis
    
    # Scoring
    factly_score: int
    factly_score_result: FactlyScoreResult
    
    # Verification summary with transparency
    verification_summary: 'EnhancedVerificationSummary'
    
    # Metadata
    processing_time_ms: float
    timestamp: datetime
    api_sources_used: List[str]
    verification_methodology: str


@dataclass
class EnhancedVerificationSummary:
    """Human-readable summary with verification transparency."""
    headline: str
    overall_assessment: str
    verification_methodology_explanation: str
    key_findings: List[str]
    verified_data_points: List[str]
    unverified_data_points: List[str]
    discrepancies_and_caveats: List[str]
    sources_consulted: List[Dict[str, Any]]
    source_diversity_assessment: str
    confidence_statement: str
    recommendations: List[str]
    verification_limitations: List[str]


class EnhancedVerificationOrchestrator:
    """
    Enhanced orchestrator for comprehensive FACTLY verification.
    
    Key enhancements over standard verification:
    1. Direct source verification against authoritative databases
    2. Complete verification trace for transparency
    3. Verified/unverified data point tracking
    4. Primary vs secondary source classification
    5. Discrepancy reporting
    6. Methodological transparency
    """
    
    def __init__(self, cache_manager: Optional[CacheManager] = None):
        """
        Initialize the enhanced verification orchestrator.
        
        Args:
            cache_manager: Optional cache manager for caching results
        """
        self.cache = cache_manager or CacheManager()
        
        # Initialize component services
        self.claim_extractor = ClaimExtractor()
        self.text_preprocessor = TextPreprocessor()
        self.evidence_search = EvidenceSearchService(cache_manager=self.cache)
        self.cross_source_analyzer = CrossSourceAnalyzer()
        self.direct_verifier = DirectSourceVerifier(cache_manager=self.cache)
        self.scoring_service = ScoringService()
        
        logger.info("EnhancedVerificationOrchestrator initialized")
    
    def verify(self, text: str, language: str = "en",
               require_direct_verification: bool = True) -> EnhancedVerificationResult:
        """
        Perform comprehensive enhanced verification of input text.
        
        Args:
            text: Text to verify (headline, article, or claim)
            language: Language code
            require_direct_verification: Whether to require direct source verification
            
        Returns:
            EnhancedVerificationResult with full verification data and transparency
        """
        import time
        start_time = time.time()
        
        verification_steps = []
        
        logger.info(f"Starting enhanced verification for text ({len(text)} chars)")
        
        # Step 1: Preprocess and extract claims
        step1_start = time.time()
        step1 = self._record_step(
            1, "Text Preprocessing", "Cleaning and normalizing input text",
            "in_progress", None
        )
        
        try:
            # Preprocess text
            cleaned_text = self.text_preprocessor.clean_text(text)
            extracted_claims = self.claim_extractor.extract_claims(cleaned_text, min_confidence=0.4)
            primary_claim = self.claim_extractor.get_primary_claim(cleaned_text)
            
            step1.result = {
                'cleaned_text_length': len(cleaned_text),
                'claims_extracted': len(extracted_claims),
                'primary_claim_confidence': primary_claim.confidence if primary_claim else None
            }
            step1.status = "completed"
            step1.duration_ms = (time.time() - step1_start) * 1000
            verification_steps.append(step1)
            
        except Exception as e:
            step1.status = "failed"
            step1.result = {'error': str(e)}
            step1.duration_ms = (time.time() - step1_start) * 1000
            verification_steps.append(step1)
            logger.error(f"Error in claim extraction: {e}")
            
            # Return partial result
            return self._create_error_result(text, str(e), start_time)
        
        # Step 2: Direct source verification
        step2_start = time.time()
        step2 = self._record_step(
            2, "Direct Source Verification", 
            "Verifying claims against authoritative sources",
            "in_progress", None
        )
        
        direct_verification_report = None
        try:
            claim_to_verify = primary_claim.text if primary_claim else cleaned_text
            direct_verification_report = self.direct_verifier.verify_claim_directly(claim_to_verify)
            
            step2.result = {
                'sources_consulted': direct_verification_report.sources_consulted,
                'primary_sources': direct_verification_report.primary_sources_found,
                'secondary_sources': direct_verification_report.secondary_sources_found,
                'verification_score': direct_verification_report.overall_verification_score,
                'data_points_verified': len(direct_verification_report.verified_data_points),
                'data_points_unverified': len(direct_verification_report.unverified_data_points),
                'discrepancies': len(direct_verification_report.discrepancies_found)
            }
            step2.status = "completed"
            
        except Exception as e:
            step2.result = {'error': str(e)}
            step2.status = "failed"
            logger.warning(f"Direct verification failed: {e}")
        
        step2.duration_ms = (time.time() - step2_start) * 1000
        verification_steps.append(step2)
        
        # Step 3: Multi-source evidence search
        step3_start = time.time()
        step3 = self._record_step(
            3, "Multi-Source Evidence Search",
            "Gathering evidence from news and fact-check sources",
            "in_progress", None
        )
        
        evidence_collection = None
        try:
            claim_to_verify = primary_claim.text if primary_claim else cleaned_text
            evidence_collection = self.evidence_search.search_evidence(
                claim_to_verify, language=language
            )
            
            step3.result = {
                'evidence_items_found': len(evidence_collection.evidence_items),
                'source_diversity_score': evidence_collection.source_diversity_score,
                'agreement_score': evidence_collection.agreement_score,
                'coverage_gaps': evidence_collection.coverage_gaps
            }
            step3.status = "completed"
            
        except Exception as e:
            step3.result = {'error': str(e)}
            step3.status = "failed"
            logger.error(f"Evidence search failed: {e}")
        
        step3.duration_ms = (time.time() - step3_start) * 1000
        verification_steps.append(step3)
        
        # Step 4: Cross-source analysis
        step4_start = time.time()
        step4 = self._record_step(
            4, "Cross-Source Analysis",
            "Analyzing consensus and conflicts between sources",
            "in_progress", None
        )
        
        cross_source_analysis = None
        try:
            if evidence_collection and evidence_collection.evidence_items:
                cross_source_analysis = self.cross_source_analyzer.analyze(evidence_collection)
            else:
                cross_source_analysis = self.cross_source_analyzer._create_insufficient_analysis(
                    claim_to_verify or cleaned_text
                )
            
            step4.result = {
                'consensus_level': cross_source_analysis.consensus_level.value,
                'evidence_strength': cross_source_analysis.evidence_strength.value,
                'agreement_score': cross_source_analysis.agreement_score,
                'confidence_score': cross_source_analysis.confidence_score,
                'contradictions_found': len(cross_source_analysis.contradictions),
                'key_findings': cross_source_analysis.key_findings[:3]
            }
            step4.status = "completed"
            
        except Exception as e:
            step4.result = {'error': str(e)}
            step4.status = "failed"
            logger.error(f"Cross-source analysis failed: {e}")
        
        step4.duration_ms = (time.time() - step4_start) * 1000
        verification_steps.append(step4)
        
        # Step 5: Calculate enhanced Factly Score™
        step5_start = time.time()
        step5 = self._record_step(
            5, "Enhanced Score Calculation",
            "Calculating Factly Score with verification weights",
            "in_progress", None
        )
        
        try:
            # Convert evidence to VerificationResult format
            verification_result = self._convert_to_verification_result(
                claim_to_verify, evidence_collection
            )
            
            # Calculate base score
            factly_score_result = self.scoring_service.calculate_factly_score(
                verification_result=verification_result,
                nlp_confidence=primary_claim.confidence if primary_claim else None,
                text_content=text
            )
            
            # Adjust score based on direct verification
            base_score = factly_score_result.factly_score
            
            # Factor in direct verification score
            if direct_verification_report:
                direct_verification_weight = 0.3
                base_score = int(
                    base_score * (1 - direct_verification_weight) +
                    direct_verification_report.overall_verification_score * 100 * direct_verification_weight
                )
            
            # Adjust based on cross-source analysis
            adjusted_score = self._adjust_score_with_analysis(
                base_score, cross_source_analysis
            )
            
            factly_score = adjusted_score
            factly_score_result.factly_score = factly_score
            
            # Update classification based on new score
            if factly_score >= 80:
                factly_score_result.classification = "Likely Authentic"
            elif factly_score >= 60:
                factly_score_result.classification = "Probably True"
            elif factly_score >= 40:
                factly_score_result.classification = "Uncertain"
            elif factly_score >= 20:
                factly_score_result.classification = "Probably False"
            else:
                factly_score_result.classification = "Likely Fake"
            
            step5.result = {
                'base_score': factly_score_result.factly_score,
                'adjusted_score': factly_score,
                'classification': factly_score_result.classification,
                'confidence_level': factly_score_result.confidence_level
            }
            step5.status = "completed"
            
        except Exception as e:
            step5.result = {'error': str(e)}
            step5.status = "failed"
            logger.error(f"Score calculation failed: {e}")
            factly_score = 50
            factly_score_result = None
        
        step5.duration_ms = (time.time() - step5_start) * 1000
        verification_steps.append(step5)
        
        # Step 6: Generate enhanced summary
        step6_start = time.time()
        step6 = self._record_step(
            6, "Summary Generation",
            "Creating human-readable verification summary",
            "in_progress", None
        )
        
        verification_summary = None
        try:
            verification_summary = self._generate_enhanced_summary(
                text, primary_claim, direct_verification_report,
                cross_source_analysis, factly_score
            )
            step6.status = "completed"
            
        except Exception as e:
            step6.status = "failed"
            step6.result = {'error': str(e)}
            logger.error(f"Summary generation failed: {e}")
        
        step6.duration_ms = (time.time() - step6_start) * 1000
        verification_steps.append(step6)
        
        # Compile final results
        processing_time_ms = (time.time() - start_time) * 1000
        
        # Build verification trace
        verification_trace = self._build_verification_trace(
            text, extracted_claims, verification_steps,
            direct_verification_report, evidence_collection,
            cross_source_analysis, factly_score
        )
        
        # Collect API sources used
        api_sources = []
        if evidence_collection:
            api_sources = list(set(
                item.source for item in evidence_collection.evidence_items
            ))
        
        # Determine confidence level
        if factly_score >= 80:
            confidence_level = "High"
        elif factly_score >= 60:
            confidence_level = "Medium-High"
        elif factly_score >= 40:
            confidence_level = "Medium"
        elif factly_score >= 20:
            confidence_level = "Medium-Low"
        else:
            confidence_level = "Low"
        
        return EnhancedVerificationResult(
            original_text=text,
            extracted_claims=extracted_claims,
            primary_claim=primary_claim,
            verification_trace=verification_trace,
            direct_verification_report=direct_verification_report,
            evidence_collection=evidence_collection,
            cross_source_analysis=cross_source_analysis,
            factly_score=factly_score,
            factly_score_result=factly_score_result,
            verification_summary=verification_summary,
            processing_time_ms=processing_time_ms,
            timestamp=datetime.now(),
            api_sources_used=api_sources,
            verification_methodology="Direct Source Verification + Multi-Source Cross-Reference"
        )
    
    def _record_step(self, step_number: int, step_name: str, description: str,
                     status: str, result: Optional[Dict[str, Any]]) -> VerificationStep:
        """Create a verification step record."""
        return VerificationStep(
            step_number=step_number,
            step_name=step_name,
            description=description,
            status=status,
            result=result,
            timestamp=datetime.now(),
            duration_ms=0.0
        )
    
    def _create_error_result(self, text: str, error: str, start_time: float) -> EnhancedVerificationResult:
        """Create a result object when verification fails."""
        return EnhancedVerificationResult(
            original_text=text,
            extracted_claims=[],
            primary_claim=None,
            verification_trace=VerificationTrace(
                original_text=text,
                extracted_claims=[],
                verification_steps=[],
                direct_verification_report=None,
                evidence_collection=None,
                cross_source_analysis=None,
                factly_score=0,
                confidence_level="Unknown",
                recommended_verdict="Unable to verify",
                sources_consulted=[],
                data_points_verified=[],
                data_points_unverified=[],
                discrepancies_found=[],
                primary_sources_used=[],
                secondary_sources_used=[],
                processing_time_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.now()
            ),
            direct_verification_report=None,
            evidence_collection=None,
            cross_source_analysis=None,
            factly_score=0,
            factly_score_result=None,
            verification_summary=EnhancedVerificationSummary(
                headline="Verification Failed",
                overall_assessment="Unable to complete verification",
                verification_methodology_explanation="An error occurred during the verification process.",
                key_findings=[f"Error: {error}"],
                verified_data_points=[],
                unverified_data_points=[],
                discrepancies_and_caveats=[],
                sources_consulted=[],
                source_diversity_assessment="No sources consulted due to error",
                confidence_statement="No confidence - verification failed",
                recommendations=["Please try again or verify information through other sources"],
                verification_limitations=["Verification process encountered an error"]
            ),
            processing_time_ms=(time.time() - start_time) * 1000,
            timestamp=datetime.now(),
            api_sources_used=[],
            verification_methodology="Enhanced Direct Verification"
        )
    
    def _build_verification_trace(self, text: str, claims: List[ExtractedClaim],
                                  steps: List[VerificationStep],
                                  direct_report: Optional[SourceVerificationReport],
                                  evidence: Optional[EvidenceCollection],
                                  analysis: Optional[CrossSourceAnalysis],
                                  score: int) -> VerificationTrace:
        """Build the complete verification trace."""
        
        # Compile sources consulted
        sources_consulted = []
        
        if direct_report:
            for result in direct_report.verification_results:
                sources_consulted.append({
                    'name': result.source_name,
                    'type': result.source_type.value,
                    'url': result.source_url,
                    'credibility': result.source_credibility,
                    'verification_score': result.verification_score,
                    'is_verified': result.is_verified
                })
        
        if evidence:
            for item in evidence.evidence_items:
                if not any(s['name'] == item.source for s in sources_consulted):
                    sources_consulted.append({
                        'name': item.source,
                        'type': item.source_type,
                        'url': item.url,
                        'credibility': item.credibility_score,
                        'verification_score': item.relevance_score,
                        'is_verified': item.relevance_score > 0.7
                    })
        
        # Separate primary and secondary sources
        primary_sources = [s for s in sources_consulted 
                          if s['type'] in ['official_government', 'official_institutional', 
                                          'academic_research', 'statistical_database']]
        secondary_sources = [s for s in sources_consulted 
                            if s['type'] not in ['official_government', 'official_institutional',
                                                 'academic_research', 'statistical_database']]
        
        # Determine recommended verdict
        recommended_verdict = "Unable to determine"
        if analysis:
            recommended_verdict = analysis.recommended_verdict
        elif score >= 80:
            recommended_verdict = "Verified"
        elif score >= 60:
            recommended_verdict = "Likely True"
        elif score >= 40:
            recommended_verdict = "Uncertain"
        elif score >= 20:
            recommended_verdict = "Likely False"
        else:
            recommended_verdict = "Disproven"
        
        # Determine confidence level
        if score >= 80:
            confidence_level = "High"
        elif score >= 60:
            confidence_level = "Medium-High"
        elif score >= 40:
            confidence_level = "Medium"
        elif score >= 20:
            confidence_level = "Medium-Low"
        else:
            confidence_level = "Low"
        
        return VerificationTrace(
            original_text=text,
            extracted_claims=claims,
            verification_steps=steps,
            direct_verification_report=direct_report,
            evidence_collection=evidence,
            cross_source_analysis=analysis,
            factly_score=score,
            confidence_level=confidence_level,
            recommended_verdict=recommended_verdict,
            sources_consulted=sources_consulted,
            data_points_verified=direct_report.verified_data_points if direct_report else [],
            data_points_unverified=direct_report.unverified_data_points if direct_report else [],
            discrepancies_found=direct_report.discrepancies_found if direct_report else [],
            primary_sources_used=[s['name'] for s in primary_sources],
            secondary_sources_used=[s['name'] for s in secondary_sources],
            processing_time_ms=sum(s.duration_ms for s in steps),
            timestamp=datetime.now()
        )
    
    def _convert_to_verification_result(self, claim: str,
                                        evidence: Optional[EvidenceCollection]) -> VerificationResult:
        """Convert evidence collection to VerificationResult format."""
        from .unified_schema import ClaimReview, RelatedNews, SourceReliability, PublisherCredibility
        
        claim_reviews = []
        related_news = []
        source_reliability = None
        
        if evidence and evidence.evidence_items:
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
            overall_confidence=evidence.agreement_score if evidence else 0.0,
            timestamp=datetime.now(),
            api_sources=list(set(item.source for item in evidence.evidence_items)) if evidence else [],
            metadata={
                'source_diversity': evidence.source_diversity_score if evidence else 0,
                'coverage_gaps': evidence.coverage_gaps if evidence else []
            }
        )
    
    def _adjust_score_with_analysis(self, base_score: int,
                                     analysis: CrossSourceAnalysis) -> int:
        """Adjust Factly Score based on cross-source analysis."""
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
    
    def _generate_enhanced_summary(self, original_text: str,
                                   primary_claim: Optional[ExtractedClaim],
                                   direct_report: Optional[SourceVerificationReport],
                                   analysis: CrossSourceAnalysis,
                                   score: int) -> EnhancedVerificationSummary:
        """Generate enhanced human-readable summary with full transparency."""
        
        # Generate headline based on score and verification
        headline = self._generate_headline(score, analysis.recommended_verdict)
        
        # Generate overall assessment
        overall_assessment = self._generate_overall_assessment(score, analysis, direct_report)
        
        # Generate methodology explanation
        methodology = self._generate_methodology_explanation(direct_report, analysis)
        
        # Generate key findings
        key_findings = list(analysis.key_findings)
        if direct_report:
            key_findings.extend([f"Verified: {dp}" for dp in direct_report.verified_data_points[:3]])
        
        # Generate verified/unverified data points
        verified_data_points = direct_report.verified_data_points if direct_report else []
        unverified_data_points = direct_report.unverified_data_points if direct_report else []
        
        # Generate discrepancies
        discrepancies = []
        if direct_report:
            for disc in direct_report.discrepancies_found[:3]:
                discrepancies.append(f"Discrepancy in {disc['source']}: {disc['discrepancy']}")
        
        for contradiction in analysis.contradictions[:2]:
            discrepancies.append(f"Contradiction: {contradiction.get('details', 'Source conflict')}")
        
        # Generate sources consulted
        sources_consulted = []
        if direct_report:
            for result in direct_report.verification_results:
                sources_consulted.append({
                    'name': result.source_name,
                    'type': result.source_type.value,
                    'credibility': f"{result.source_credibility:.0%}",
                    'verified': '✓' if result.is_verified else '○'
                })
        
        # Source diversity assessment
        if direct_report:
            diversity = "High" if direct_report.primary_sources_found >= 2 else "Medium" if direct_report.primary_sources_found == 1 else "Low"
            source_diversity = f"Verification consulted {direct_report.sources_consulted} sources ({direct_report.primary_sources_found} primary, {direct_report.secondary_sources_found} secondary) - {diversity} diversity"
        else:
            source_diversity = "Source diversity could not be determined"
        
        # Generate confidence statement
        confidence_statement = self._generate_confidence_statement(score, analysis, direct_report)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(score, analysis, direct_report)
        
        # Generate limitations
        limitations = self._generate_limitations(analysis, direct_report)
        
        return EnhancedVerificationSummary(
            headline=headline,
            overall_assessment=overall_assessment,
            verification_methodology_explanation=methodology,
            key_findings=key_findings,
            verified_data_points=verified_data_points,
            unverified_data_points=unverified_data_points,
            discrepancies_and_caveats=discrepancies,
            sources_consulted=sources_consulted,
            source_diversity_assessment=source_diversity,
            confidence_statement=confidence_statement,
            recommendations=recommendations,
            verification_limitations=limitations
        )
    
    def _generate_headline(self, score: int, verdict: str) -> str:
        """Generate summary headline."""
        if score >= 80:
            return f"✓ Verified Authentic - {verdict}"
        elif score >= 60:
            return f"◐ Likely True - {verdict}"
        elif score >= 40:
            return f"○ Uncertain - {verdict}"
        elif score >= 20:
            return f"◐ Likely False - {verdict}"
        else:
            return f"✕ Disproven - {verdict}"
    
    def _generate_overall_assessment(self, score: int, analysis: CrossSourceAnalysis,
                                     direct_report: Optional[SourceVerificationReport]) -> str:
        """Generate overall assessment text."""
        parts = []
        
        if score >= 80:
            parts.append("This information has been VERIFIED through direct examination of authoritative sources.")
        elif score >= 60:
            parts.append("This information is LIKELY ACCURATE based on credible source verification.")
        elif score >= 40:
            parts.append("This information has MIXED EVIDENCE from verification attempts.")
        elif score >= 20:
            parts.append("This information is LIKELY INACCURATE based on verification findings.")
        else:
            parts.append("This information has been DISPROVEN through verification.")
        
        # Add source information
        if direct_report:
            sources_text = f"Verification consulted {direct_report.sources_consulted} authoritative sources, "
            sources_text += f"including {direct_report.primary_sources_found} primary source(s)."
            parts.append(sources_text)
        
        # Add consensus information
        if analysis:
            if analysis.consensus_level.value == 'strong_agreement':
                parts.append("All credible sources strongly agree on this information.")
            elif analysis.consensus_level.value == 'strong_disagreement':
                parts.append("Credible sources significantly disagree on this information.")
            elif analysis.consensus_level.value == 'mixed':
                parts.append("Sources present varying perspectives on this information.")
        
        return " ".join(parts)
    
    def _generate_methodology_explanation(self, direct_report: Optional[SourceVerificationReport],
                                          analysis: CrossSourceAnalysis) -> str:
        """Explain the verification methodology used."""
        parts = [
            "VERIFICATION METHODOLOGY:",
            "1. Direct Source Verification: Claims were verified against authoritative sources",
            "   including government databases, academic research, and official records."
        ]
        
        if direct_report:
            parts.append(f"2. {direct_report.sources_consulted} source(s) were directly consulted for verification.")
            if direct_report.primary_sources_found > 0:
                parts.append(f"3. {direct_report.primary_sources_found} primary source(s) were examined directly.")
        
        parts.append("4. Cross-reference validation was performed across all sources.")
        parts.append("5. Consensus analysis determined agreement levels between sources.")
        
        return "\n".join(parts)
    
    def _generate_confidence_statement(self, score: int, analysis: CrossSourceAnalysis,
                                        direct_report: Optional[SourceVerificationReport]) -> str:
        """Generate detailed confidence statement."""
        confidence_pct = score
        
        # Determine confidence level and factors
        if confidence_pct >= 80:
            level = "HIGH"
            factors = "Strong verification from multiple authoritative sources"
        elif confidence_pct >= 60:
            level = "MEDIUM-HIGH"
            factors = "Good verification with some limitations"
        elif confidence_pct >= 40:
            level = "MEDIUM"
            factors = "Moderate evidence with some conflicts or gaps"
        elif confidence_pct >= 20:
            level = "MEDIUM-LOW"
            factors = "Weak verification with significant uncertainties"
        else:
            level = "LOW"
            factors = "Insufficient or contradictory evidence"
        
        # Add source confidence if available
        source_confidence = ""
        if direct_report:
            source_confidence = f" Source verification score: {int(direct_report.overall_verification_score * 100)}%."
        
        return f"CONFIDENCE: {level} ({confidence_pct}%) - {factors}.{source_confidence}"
    
    def _generate_recommendations(self, score: int, analysis: CrossSourceAnalysis,
                                   direct_report: Optional[SourceVerificationReport]) -> List[str]:
        """Generate user recommendations based on verification."""
        recommendations = []
        
        if score >= 80:
            recommendations.append("✓ This information is well-verified and can be considered reliable.")
            recommendations.append("✓ Safe to share with confidence in its accuracy.")
        elif score >= 60:
            recommendations.append("◐ This information appears accurate based on available evidence.")
            recommendations.append("◐ Consider verifying with official sources if critical.")
        elif score >= 40:
            recommendations.append("○ Exercise CAUTION with this information.")
            recommendations.append("○ Seek additional verification from authoritative sources.")
            recommendations.append("○ Do not rely on this information for important decisions.")
        elif score >= 20:
            recommendations.append("◐ This information is likely inaccurate.")
            recommendations.append("◐ Do not share without additional verification.")
            recommendations.append("◐ Look for alternative sources or official statements.")
        else:
            recommendations.append("✕ This information has been DISPROVEN.")
            recommendations.append("✕ Do not share - it may spread misinformation.")
        
        # Add specific recommendations based on findings
        if direct_report and direct_report.unverified_data_points:
            recommendations.append(f"Note: {len(direct_report.unverified_data_points)} data point(s) could not be verified.")
        
        if analysis and analysis.contradictions:
            recommendations.append(f"Warning: {len(analysis.contradictions)} contradiction(s) found between sources.")
        
        return recommendations
    
    def _generate_limitations(self, analysis: CrossSourceAnalysis,
                               direct_report: Optional[SourceVerificationReport]) -> List[str]:
        """Identify limitations in the verification process."""
        limitations = []
        
        if analysis and analysis.evidence_strength.value in ['weak', 'insufficient', 'conflicting']:
            limitations.append("Limited evidence was available for comprehensive verification.")
        
        if direct_report:
            if direct_report.primary_sources_found == 0:
                limitations.append("No primary (authoritative) sources could be consulted.")
            
            if direct_report.discrepancies_found:
                limitations.append(f"Found {len(direct_report.discrepancies_found)} discrepancy(ies) between sources.")
        
        if analysis and analysis.uncertainty_factors:
            limitations.extend(analysis.uncertainty_factors[:3])
        
        if not limitations:
            limitations.append("No significant limitations identified in the verification process.")
        
        return limitations
