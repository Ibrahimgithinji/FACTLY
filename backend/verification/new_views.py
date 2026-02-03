"""
Enhanced Verification Views

Updated API views that use the new verification orchestrator
for comprehensive claim verification.
"""

import logging
import time
from typing import Optional, Dict, Any
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from django.http import JsonResponse

from .serializers import VerificationRequestSerializer, VerificationResponseSerializer
from services.nlp_service import TextPreprocessor, URLExtractionService
from services.fact_checking_service import VerificationOrchestrator

logger = logging.getLogger(__name__)


class EnhancedVerificationView(APIView):
    """
    Enhanced API view for content verification using the new orchestrator.
    
    Provides comprehensive verification with:
    - Claim extraction
    - Multi-source evidence search
    - Cross-source analysis
    - Factly Score™ calculation
    - Human-readable summaries
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Initialize services
        self.text_preprocessor = TextPreprocessor()
        self.url_extractor = URLExtractionService()
        self.orchestrator = VerificationOrchestrator()

    def post(self, request):
        """
        Verify content and return comprehensive Factly Score™ results.

        Accepts either text or URL for verification.
        """
        start_time = time.time()

        try:
            # Validate request data
            serializer = VerificationRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            data = serializer.validated_data
            text = data.get('text', '')
            url = data.get('url', '')
            language = data.get('language', 'en')

            logger.info(f"Starting enhanced verification for {'URL' if url else 'text'}")

            # Step 1: Extract content if URL provided
            extracted_content = None
            if url:
                try:
                    extracted_content = self.url_extractor.extract_content(url)
                    text = extracted_content.content or text
                    logger.info(f"Extracted {len(text)} characters from URL")
                except Exception as e:
                    logger.error(f"URL extraction failed: {e}")
                    return Response(
                        {"error": f"Failed to extract content from URL: {str(e)}"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            if not text:
                return Response(
                    {"error": "No text content available for verification"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Step 2: Perform comprehensive verification using orchestrator
            try:
                verification_result = self.orchestrator.verify(text, language)
                logger.info(f"Verification complete. Score: {verification_result.factly_score}")
            except Exception as e:
                logger.error(f"Verification failed: {e}", exc_info=True)
                return Response(
                    {"error": f"Verification service error: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            # Step 3: Prepare comprehensive response
            processing_time = time.time() - start_time

            response_data = {
                # Original input
                "original_text": text,
                "extracted_content": extracted_content.to_dict() if extracted_content else None,

                # Claim extraction
                "extracted_claims": [
                    {
                        "text": claim.text,
                        "type": claim.claim_type.value,
                        "confidence": round(claim.confidence, 2),
                        "entities": claim.entities,
                        "keywords": claim.keywords,
                        "verifiability": round(claim.verifiability_score, 2)
                    }
                    for claim in verification_result.extracted_claims
                ],
                "primary_claim": {
                    "text": verification_result.primary_claim.text,
                    "confidence": round(verification_result.primary_claim.confidence, 2),
                    "keywords": verification_result.primary_claim.keywords
                } if verification_result.primary_claim else None,

                # Evidence
                "evidence": {
                    "total_sources": len(verification_result.evidence_collection.evidence_items),
                    "source_diversity": round(verification_result.evidence_collection.source_diversity_score, 2),
                    "agreement_score": round(verification_result.evidence_collection.agreement_score, 2),
                    "coverage_gaps": verification_result.evidence_collection.coverage_gaps,
                    "sources": [
                        {
                            "name": item.source,
                            "type": item.source_type,
                            "title": item.title,
                            "credibility": round(item.credibility_score, 2),
                            "relevance": round(item.relevance_score, 2),
                            "verdict": item.verdict,
                            "url": item.url,
                            "published": item.published_date.isoformat() if item.published_date else None
                        }
                        for item in verification_result.evidence_collection.evidence_items[:10]  # Limit to top 10
                    ]
                },

                # Cross-source analysis
                "analysis": {
                    "consensus_level": verification_result.cross_source_analysis.consensus_level.value,
                    "evidence_strength": verification_result.cross_source_analysis.evidence_strength.value,
                    "agreement_score": round(verification_result.cross_source_analysis.agreement_score, 2),
                    "confidence_score": round(verification_result.cross_source_analysis.confidence_score, 2),
                    "recommended_verdict": verification_result.cross_source_analysis.recommended_verdict,
                    "key_findings": verification_result.cross_source_analysis.key_findings,
                    "contradictions": verification_result.cross_source_analysis.contradictions,
                    "uncertainty_factors": verification_result.cross_source_analysis.uncertainty_factors
                },

                # Factly Score™
                "factly_score": {
                    "score": verification_result.factly_score,
                    "classification": verification_result.factly_score_result.classification,
                    "confidence_level": verification_result.factly_score_result.confidence_level,
                    "components": [
                        {
                            "name": comp.name,
                            "score": round(comp.score, 2),
                            "weight": round(comp.weight, 2),
                            "weighted_score": round(comp.weighted_score, 2),
                            "justification": comp.justification
                        }
                        for comp in verification_result.factly_score_result.components
                    ]
                },

                # Human-readable summary
                "summary": {
                    "headline": verification_result.verification_summary.headline,
                    "explanation": verification_result.verification_summary.explanation,
                    "key_points": verification_result.verification_summary.key_points,
                    "recommendations": verification_result.verification_summary.recommendations,
                    "confidence_statement": verification_result.verification_summary.confidence_statement
                },

                # Metadata
                "processing_time": round(processing_time, 2),
                "api_sources": verification_result.api_sources_used,
                "timestamp": verification_result.timestamp.isoformat()
            }

            logger.info(f"Enhanced verification completed in {processing_time:.2f}s")
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Unexpected error in verification: {e}", exc_info=True)
            return Response(
                {"error": f"Internal server error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class QuickVerificationView(APIView):
    """
    Quick verification endpoint for fast results.
    
    Returns essential verification data without full evidence details.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.orchestrator = VerificationOrchestrator()

    def post(self, request):
        """Quick verification endpoint."""
        try:
            text = request.data.get('text', '')
            if not text:
                return Response(
                    {"error": "Text is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            result = self.orchestrator.verify_quick(text)
            return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Quick verification error: {e}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(['POST'])
def batch_verify(request):
    """
    Batch verification endpoint for multiple claims.
    
    Accepts a list of texts to verify.
    """
    texts = request.data.get('texts', [])
    if not texts or not isinstance(texts, list):
        return Response(
            {"error": "Please provide a list of texts to verify"},
            status=status.HTTP_400_BAD_REQUEST
        )

    if len(texts) > 10:
        return Response(
            {"error": "Maximum 10 texts allowed per batch"},
            status=status.HTTP_400_BAD_REQUEST
        )

    orchestrator = VerificationOrchestrator()
    results = []

    for text in texts:
        try:
            result = orchestrator.verify_quick(text)
            results.append({
                "text": text[:100] + "..." if len(text) > 100 else text,
                "result": result,
                "success": True
            })
        except Exception as e:
            results.append({
                "text": text[:100] + "..." if len(text) > 100 else text,
                "error": str(e),
                "success": False
            })

    return Response({
        "results": results,
        "total": len(texts),
        "successful": sum(1 for r in results if r["success"])
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
def verification_health_check(request):
    """Health check endpoint for verification services."""
    return JsonResponse({
        "status": "healthy",
        "service": "FACTLY Verification API",
        "version": "2.0.0",
        "features": [
            "claim_extraction",
            "multi_source_search",
            "cross_source_analysis",
            "factly_score",
            "explainable_summaries"
        ]
    })
