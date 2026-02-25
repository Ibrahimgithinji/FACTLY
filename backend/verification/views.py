import logging
import time
from datetime import datetime
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import VerificationRequestSerializer, VerificationResponseSerializer
from services.nlp_service import TextPreprocessor, URLExtractionService
from services.fact_checking_service import FactCheckingService
from services.fact_checking_service.unified_schema import datetime_to_iso
from services.scoring_service import ScoringService
from services.fact_checking_service.enhanced_verification_orchestrator import EnhancedVerificationOrchestrator

logger = logging.getLogger(__name__)


class EnhancedVerificationView(APIView):
    """API view for enhanced content verification with direct source verification."""
    
    # Simple in-memory rate limiting
    _rate_limit_storage = {}
    RATE_LIMIT_REQUESTS = 10
    RATE_LIMIT_WINDOW = 3600
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.enhanced_orchestrator = EnhancedVerificationOrchestrator()
    
    def _check_rate_limit(self, request):
        """Simple rate limiting check."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '')
        
        import time as time_module
        current_time = time_module.time()
        
        if ip in self._rate_limit_storage:
            self._rate_limit_storage[ip] = [
                t for t in self._rate_limit_storage[ip]
                if current_time - t < self.RATE_LIMIT_WINDOW
            ]
            
            if len(self._rate_limit_storage[ip]) >= self.RATE_LIMIT_REQUESTS:
                return False
            
            self._rate_limit_storage[ip].append(current_time)
        else:
            self._rate_limit_storage[ip] = [current_time]
        
        return True
    
    def post(self, request):
        """
        Perform enhanced verification with direct source verification.
        
        This endpoint provides comprehensive verification including:
        - Direct verification against authoritative sources
        - Complete verification trace for transparency
        - Verified/unverified data point tracking
        - Primary vs secondary source classification
        """
        start_time = time.time()
        
        # Check rate limit
        if not self._check_rate_limit(request):
            return Response(
                {"error": "Rate limit exceeded. Please try again later.", "retry_after": self.RATE_LIMIT_WINDOW},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        
        try:
            # Validate request data
            serializer = VerificationRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            data = serializer.validated_data
            text = data.get('text', '')
            url = data.get('url', '')
            language = data.get('language', 'en')
            
            logger.info(f"Starting enhanced verification for {'URL' if url else 'text'}: {url or text[:100]}...")
            
            # Extract content if URL provided
            if url:
                url_extractor = URLExtractionService()
                try:
                    extracted_content = url_extractor.extract_content(url)
                    text = extracted_content.content or text
                    logger.info(f"Extracted content from URL: {len(text)} characters")
                except Exception as e:
                    logger.exception("URL extraction failed")
                    return Response(
                        {"error": "Failed to extract content from URL."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            if not text:
                return Response(
                    {"error": "No text content available for verification"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Perform enhanced verification
            result = self.enhanced_orchestrator.verify(text, language=language)
            
            # Build response with verification transparency
            response_data = {
                "query": text,
                "factly_score": result.factly_score,
                "classification": result.factly_score_result.classification if result.factly_score_result else "Unknown",
                "confidence_level": result.verification_trace.confidence_level if result.verification_trace else "Unknown",
                "recommended_verdict": result.verification_trace.recommended_verdict if result.verification_trace else "Unable to determine",
                
                # Enhanced verification summary
                "verification_summary": {
                    "headline": result.verification_summary.headline if result.verification_summary else "Verification Failed",
                    "overall_assessment": result.verification_summary.overall_assessment if result.verification_summary else "Unable to verify",
                    "verification_methodology": result.verification_summary.verification_methodology_explanation if result.verification_summary else "",
                    "key_findings": result.verification_summary.key_findings if result.verification_summary else [],
                    "verified_data_points": result.verification_summary.verified_data_points if result.verification_summary else [],
                    "unverified_data_points": result.verification_summary.unverified_data_points if result.verification_summary else [],
                    "discrepancies_and_caveats": result.verification_summary.discrepancies_and_caveats if result.verification_summary else [],
                    "sources_consulted": result.verification_summary.sources_consulted if result.verification_summary else [],
                    "source_diversity_assessment": result.verification_summary.source_diversity_assessment if result.verification_summary else "Unknown",
                    "confidence_statement": result.verification_summary.confidence_statement if result.verification_summary else "",
                    "recommendations": result.verification_summary.recommendations if result.verification_summary else [],
                    "verification_limitations": result.verification_summary.verification_limitations if result.verification_summary else []
                },
                
                # Verification trace for transparency
                "verification_trace": {
                    "verification_steps": [
                        {
                            "step_number": step.step_number,
                            "step_name": step.step_name,
                            "description": step.description,
                            "status": step.status,
                            "result": step.result,
                            "timestamp": step.timestamp.isoformat() if step.timestamp else None,
                            "duration_ms": step.duration_ms
                        }
                        for step in (result.verification_trace.verification_steps if result.verification_trace else [])
                    ],
                    "sources_consulted": result.verification_trace.sources_consulted if result.verification_trace else [],
                    "primary_sources_used": result.verification_trace.primary_sources_used if result.verification_trace else [],
                    "secondary_sources_used": result.verification_trace.secondary_sources_used if result.verification_trace else [],
                    "data_points_verified": result.verification_trace.data_points_verified if result.verification_trace else [],
                    "data_points_unverified": result.verification_trace.data_points_unverified if result.verification_trace else [],
                    "discrepancies_found": result.verification_trace.discrepancies_found if result.verification_trace else [],
                    "confidence_level": result.verification_trace.confidence_level if result.verification_trace else "Unknown",
                    "recommended_verdict": result.verification_trace.recommended_verdict if result.verification_trace else "Unknown",
                    "processing_time_ms": result.verification_trace.processing_time_ms if result.verification_trace else 0
                },
                
                # Evidence from traditional sources
                "evidence": self._build_evidence_list(result),
                
                # Direct verification details
                "direct_verification": {
                    "sources_consulted": result.direct_verification_report.sources_consulted if result.direct_verification_report else 0,
                    "primary_sources_found": result.direct_verification_report.primary_sources_found if result.direct_verification_report else 0,
                    "secondary_sources_found": result.direct_verification_report.secondary_sources_found if result.direct_verification_report else 0,
                    "overall_verification_score": result.direct_verification_report.overall_verification_score if result.direct_verification_report else 0,
                    "verified_data_points": result.direct_verification_report.verified_data_points if result.direct_verification_report else [],
                    "unverified_data_points": result.direct_verification_report.unverified_data_points if result.direct_verification_report else [],
                    "discrepancies": result.direct_verification_report.discrepancies_found if result.direct_verification_report else [],
                    "verification_steps": result.direct_verification_report.verification_steps if result.direct_verification_report else []
                } if result.direct_verification_report else None,
                
                # Cross-source analysis
                "cross_source_analysis": {
                    "consensus_level": result.cross_source_analysis.consensus_level.value if result.cross_source_analysis else "unknown",
                    "evidence_strength": result.cross_source_analysis.evidence_strength.value if result.cross_source_analysis else "unknown",
                    "agreement_score": result.cross_source_analysis.agreement_score if result.cross_source_analysis else 0,
                    "confidence_score": result.cross_source_analysis.confidence_score if result.cross_source_analysis else 0,
                    "key_findings": result.cross_source_analysis.key_findings if result.cross_source_analysis else [],
                    "contradictions": result.cross_source_analysis.contradictions if result.cross_source_analysis else [],
                    "recommended_verdict": result.cross_source_analysis.recommended_verdict if result.cross_source_analysis else "Unknown",
                    "uncertainty_factors": result.cross_source_analysis.uncertainty_factors if result.cross_source_analysis else []
                } if result.cross_source_analysis else None,
                
                # Data freshness information
                "data_freshness": {
                    "verification_timestamp": result.timestamp.isoformat(),
                    "most_recent_evidence_age_hours": self._calculate_evidence_age(result),
                    "realtime_sources_used": any(source in result.api_sources_used for source in ['Real-Time News', 'NewsAPI', 'Bing News']),
                    "cache_status": "fresh" if self._is_data_fresh(result) else "stale",
                    "data_age_warning": self._get_data_age_warning(result)
                },
                
                "api_sources_used": result.api_sources_used,
                "processing_time_ms": result.processing_time_ms,
                "timestamp": result.timestamp.isoformat()
            }
            
            logger.info(f"Enhanced verification complete. Score: {result.factly_score}, Time: {result.processing_time_ms:.2f}ms")
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.exception("Enhanced verification failed")
            return Response(
                {"error": f"Enhanced verification failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _build_evidence_list(self, result):
        """Build evidence list from enhanced result."""
        evidence_items = []
        
        if result.evidence_collection and result.evidence_collection.evidence_items:
            for item in result.evidence_collection.evidence_items:
                evidence_items.append({
                    "id": f"evidence_{len(evidence_items)}",
                    "type": item.source_type,
                    "title": item.title,
                    "content": item.content,
                    "source": item.source,
                    "source_credibility": item.credibility_score,
                    "relevance_score": item.relevance_score,
                    "verdict": item.verdict,
                    "url": item.url,
                    "date": item.published_date.isoformat() if item.published_date else None,
                    "metadata": item.metadata
                })
        
        return evidence_items


class VerificationView(APIView):
    """API view for content verification using Factly Score™."""
    
    # Simple in-memory rate limiting (requests per IP)
    _rate_limit_storage = {}
    RATE_LIMIT_REQUESTS = 10
    RATE_LIMIT_WINDOW = 3600  # 1 hour in seconds
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Initialize services
        self.text_preprocessor = TextPreprocessor()
        self.url_extractor = URLExtractionService()
        self.fact_checker = FactCheckingService()
        self.scorer = ScoringService()

    def _check_rate_limit(self, request):
        """Simple rate limiting check."""
        # Get client IP
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '')
        
        import time as time_module
        current_time = time_module.time()
        
        # Clean old entries
        if ip in self._rate_limit_storage:
            # Remove entries older than the window
            self._rate_limit_storage[ip] = [
                t for t in self._rate_limit_storage[ip]
                if current_time - t < self.RATE_LIMIT_WINDOW
            ]
            
            # Check if over limit
            if len(self._rate_limit_storage[ip]) >= self.RATE_LIMIT_REQUESTS:
                return False
            
            # Add current request
            self._rate_limit_storage[ip].append(current_time)
        else:
            self._rate_limit_storage[ip] = [current_time]
        
        return True

    def post(self, request):
        """
        Verify content and return Factly Score™.

        Accepts either text or URL for verification.
        
        Rate limited to 10 requests per hour per IP address.
        """
        start_time = time.time()

        # Check rate limit
        if not self._check_rate_limit(request):
            return Response(
                {"error": "Rate limit exceeded. Please try again later.", "retry_after": self.RATE_LIMIT_WINDOW},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )

        try:
            # Validate request data
            serializer = VerificationRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            data = serializer.validated_data
            text = data.get('text', '')
            url = data.get('url', '')
            language = data.get('language', 'en')

            logger.info(f"Starting verification for {'URL' if url else 'text'}: {url or text[:100]}...")

            # Step 1: Extract content if URL provided
            extracted_content = None
            if url:
                try:
                    extracted_content = self.url_extractor.extract_content(url)
                    text = extracted_content.content or text
                    logger.info(f"Extracted content from URL: {len(text)} characters")
                except Exception as e:
                    logger.exception("URL extraction failed")
                    return Response(
                        {"error": "Failed to extract content from URL."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            if not text:
                return Response(
                    {"error": "No text content available for verification"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Step 2: Preprocess text
            nlp_analysis = None
            try:
                nlp_analysis = self.text_preprocessor.preprocess(text, language=language)
                logger.info(f"NLP preprocessing completed: {nlp_analysis['language']}")
            except Exception as e:
                logger.warning(f"NLP preprocessing failed: {e}")
                nlp_analysis = {"error": str(e)}

            # Step 3: Fact-check the claim
            verification_result = None
            try:
                verification_result = self.fact_checker.verify_claim(text, language)
                logger.info(f"Fact-checking completed: {len(verification_result.claim_reviews)} reviews")
            except Exception as e:
                logger.exception("Fact-checking failed")
                return Response(
                    {"error": "Fact-checking service error."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            # Step 4: Calculate Factly Score™
            factly_score = None
            try:
                # Use NLP confidence if available, otherwise None
                nlp_confidence = nlp_analysis.get('confidence') if isinstance(nlp_analysis, dict) else None
                factly_score = self.scorer.calculate_factly_score(
                    verification_result,
                    nlp_confidence=nlp_confidence,
                    text_content=text
                )
                logger.info(f"Factly Score™ calculated: {factly_score.factly_score}")
            except Exception as e:
                logger.exception("Scoring failed")
                return Response(
                    {"error": "Scoring service error."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            # Step 5: Prepare response
            processing_time = time.time() - start_time

            # Build evidence list with exact metadata
            evidence_items = []
            
            # Add claim reviews as evidence
            for review in verification_result.claim_reviews:
                evidence_items.append({
                    "id": f"review_{len(evidence_items)}",
                    "type": "fact_check",
                    "claim": review.claim,
                    "text": review.claim[:500] if len(review.claim) > 500 else review.claim,
                    "full_text": review.claim,
                    "rating": review.verdict,
                    "confidence_score": review.confidence_score,
                    "source": review.publisher.name if review.publisher else "Unknown",
                    "source_credibility": review.publisher.credibility_score if review.publisher else 0.5,
                    "url": review.url,
                    "date": datetime_to_iso(review.review_date),
                    "exact_date": review.review_date.isoformat() if review.review_date else None,
                    "metadata": review.metadata
                })
            
            # Add related news as evidence
            for news in verification_result.related_news:
                evidence_items.append({
                    "id": f"news_{len(evidence_items)}",
                    "type": "news",
                    "title": news.title,
                    "text": news.title[:500] if len(news.title) > 500 else news.title,
                    "full_text": news.title,
                    "rating": news.sentiment or "neutral",
                    "confidence_score": news.relevance_score,
                    "source": news.source,
                    "source_credibility": news.relevance_score,  # Use relevance as proxy
                    "url": news.url,
                    "date": datetime_to_iso(news.publish_date),
                    "exact_date": news.publish_date.isoformat() if news.publish_date else None,
                    "metadata": news.metadata
                })
            
            # Build sources list with exact metadata
            sources_list = []
            for review in verification_result.claim_reviews:
                if review.publisher:
                    sources_list.append({
                        "name": review.publisher.name,
                        "url": review.url,
                        "credibility": review.publisher.credibility_score,
                        "exact_credibility_score": review.publisher.credibility_score,
                        "review_count": review.publisher.review_count,
                        "categories": review.publisher.categories
                    })
            
            for news in verification_result.related_news:
                source_name = news.source
                if not any(s["name"] == source_name for s in sources_list):
                    sources_list.append({
                        "name": source_name,
                        "url": news.url,
                        "credibility": "High" if news.relevance_score >= 0.8 else ("Medium" if news.relevance_score >= 0.5 else "Low"),
                        "exact_credibility_score": news.relevance_score,
                        "relevance_score": news.relevance_score,
                        "sentiment": news.sentiment
                    })

            response_data = {
                "original_text": text,
                "extracted_content": extracted_content.to_dict() if extracted_content else None,
                "nlp_analysis": nlp_analysis,
                "fact_checking_results": {
                    "claim_reviews": [review.to_dict() for review in verification_result.claim_reviews],
                    "related_news": [news.to_dict() for news in verification_result.related_news],
                    "source_reliability": verification_result.source_reliability.to_dict() if verification_result.source_reliability else None,
                    "overall_confidence": verification_result.overall_confidence,
                    "api_sources": verification_result.api_sources,
                    "timestamp": verification_result.timestamp.isoformat()
                },
                "factly_score": {
                    "factly_score": factly_score.factly_score,
                    "classification": factly_score.classification,
                    "confidence_level": factly_score.confidence_level,
                    "components": [
                        {
                            "name": comp.name,
                            "score": comp.score,
                            "weight": comp.weight,
                            "weighted_score": comp.weighted_score,
                            "justification": comp.justification
                        }
                        for comp in factly_score.components
                    ],
                    "processing_time": factly_score.processing_time
                },
                "evidence": evidence_items,
                "sources": sources_list,
                "processing_time": processing_time
            }
            
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.exception("Verification failed")
            return Response(
                {"error": f"Verification failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _calculate_evidence_age(self, result) -> float:
        """Calculate the age of the most recent evidence in hours."""
        if not result.evidence_collection or not result.evidence_collection.evidence_items:
            return float('inf')
        
        # Find the most recent evidence
        most_recent = max(
            (item for item in result.evidence_collection.evidence_items 
             if item.published_date),
            key=lambda x: x.published_date,
            default=None
        )
        
        if most_recent and most_recent.published_date:
            age = datetime.now() - most_recent.published_date.replace(tzinfo=None)
            return age.total_seconds() / 3600
        
        return float('inf')
    
    def _is_data_fresh(self, result) -> bool:
        """Check if the verification data is considered fresh."""
        evidence_age = self._calculate_evidence_age(result)
        return evidence_age <= 24  # Consider fresh if evidence is less than 24 hours old
    
    def _get_data_age_warning(self, result) -> str:
        """Get a warning message about data age."""
        evidence_age = self._calculate_evidence_age(result)
        
        if evidence_age <= 1:
            return "Data is very recent (less than 1 hour old)"
        elif evidence_age <= 6:
            return "Data is recent (less than 6 hours old)"
        elif evidence_age <= 24:
            return "Data is moderately recent (less than 24 hours old)"
        elif evidence_age <= 72:
            return "Data is somewhat stale (1-3 days old) - consider verifying with current sources"
        else:
            return "Data is stale (more than 3 days old) - strongly recommend fresh verification"


def health_check(request):
    """Health check endpoint for monitoring."""
    response = Response({
        "status": "healthy",
        "service": "Factly API",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat(),
        "features": [
            "Enhanced fact-checking with real-time news",
            "Multi-source verification",
            "Data freshness indicators",
            "Configurable caching"
        ]
    }, status=status.HTTP_200_OK)
    # Ensure JSON response header
    response['Content-Type'] = 'application/json'
    return response
