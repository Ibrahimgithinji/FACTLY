import logging
import time
from typing import Optional, Dict, Any
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from django.http import JsonResponse
from django_ratelimit.decorators import ratelimit

from .serializers import VerificationRequestSerializer, VerificationResponseSerializer
from services.nlp_service import TextPreprocessor, URLExtractionService
from services.fact_checking_service import FactCheckingService
from services.scoring_service import ScoringService

logger = logging.getLogger(__name__)


class VerificationView(APIView):
    """API view for content verification using Factly Score™."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Initialize services
        self.text_preprocessor = TextPreprocessor()
        self.url_extractor = URLExtractionService()
        self.fact_checker = FactCheckingService()
        self.scorer = ScoringService()

    @ratelimit(key='ip', rate='10/h', method='POST', block=True)
    def post(self, request):
        """
        Verify content and return Factly Score™.

        Accepts either text or URL for verification.
        
        Rate limited to 10 requests per hour per IP address.
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
                            "justification": comp.justification,
                            "evidence": comp.evidence
                        } for comp in factly_score.components
                    ],
                    "justifications": factly_score.justifications,
                    "evidence_summary": factly_score.evidence_summary,
                    "timestamp": factly_score.timestamp.isoformat(),
                    "metadata": factly_score.metadata
                },
                "processing_time": processing_time,
                "api_sources": verification_result.api_sources,
                "timestamp": factly_score.timestamp.isoformat()
            }

            # Validate response serializer
            response_serializer = VerificationResponseSerializer(data=response_data)
            if not response_serializer.is_valid():
                logger.error(f"Response serialization failed: {response_serializer.errors}")
                return Response(
                    {"error": "Response formatting error"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            logger.info(f"Verification completed successfully in {processing_time:.2f}s")
            return Response(response_serializer.validated_data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.exception("Unexpected error in verification")
            return Response(
                {"error": "Internal server error."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(['GET'])
def health_check(request):
    """Health check endpoint."""
    return JsonResponse({
        "status": "healthy",
        "service": "FACTLY Backend API",
        "version": "1.0.0"
    })