"""
Fast Verification API Views

High-performance API endpoints using async processing and optimized caching.
"""

import logging
import time
from typing import Optional, Dict, Any
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from django.http import JsonResponse

from services.fact_checking_service.fast_verification_orchestrator import (
    FastVerificationOrchestrator, FastVerificationResult
)

logger = logging.getLogger(__name__)


class FastVerificationView(APIView):
    """
    High-performance verification endpoint.
    
    Uses async processing for sub-second response times.
    Typical response time: 1-3 seconds (vs 5-10 seconds standard)
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.orchestrator = FastVerificationOrchestrator()

    def post(self, request):
        """
        Fast verification endpoint.
        
        Request Body:
        {
            "text": "Claim to verify",
            "language": "en" (optional),
            "use_cache": true (optional, default: true)
        }
        
        Response:
        {
            "factly_score": 85,
            "classification": "Likely Authentic",
            "confidence_level": "High",
            "recommended_verdict": "True",
            "consensus_level": "strong_agreement",
            "evidence_strength": "strong",
            "summary": {
                "headline": "Likely Authentic - True",
                "explanation": "Multiple credible sources confirm this information.",
                "key_points": [...],
                "recommendations": [...]
            },
            "sources_consulted": 8,
            "processing_time": 1.23,
            "cached": false,
            "timestamp": "2026-01-30T22:51:00"
        }
        """
        start_time = time.time()

        try:
            # Get request data
            text = request.data.get('text', '')
            language = request.data.get('language', 'en')
            use_cache = request.data.get('use_cache', True)

            if not text:
                return Response(
                    {"error": "Text is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            logger.info(f"Fast verification request: {text[:100]}...")

            # Perform fast verification
            result = self.orchestrator.verify_fast(text, language, use_cache)

            # Format response
            response_data = {
                "factly_score": result.factly_score,
                "classification": result.classification,
                "confidence_level": result.confidence_level,
                "recommended_verdict": result.recommended_verdict,
                "consensus_level": result.consensus_level,
                "evidence_strength": result.evidence_strength,
                "summary": {
                    "headline": result.headline,
                    "explanation": result.explanation,
                    "key_points": result.key_points,
                    "recommendations": result.recommendations
                },
                "sources_consulted": result.sources_consulted,
                "processing_time": result.processing_time,
                "cached": result.cached,
                "timestamp": result.timestamp.isoformat()
            }

            total_time = time.time() - start_time
            logger.info(f"Fast verification completed in {total_time:.2f}s (API: {result.processing_time:.2f}s)")

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Fast verification error: {e}", exc_info=True)
            return Response(
                {"error": f"Verification failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class BatchFastVerificationView(APIView):
    """
    Batch verification endpoint for multiple claims.
    
    More efficient than individual calls due to:
    - Shared connection pool
    - Parallel processing
    - Reduced overhead
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.orchestrator = FastVerificationOrchestrator()

    def post(self, request):
        """
        Batch verification endpoint.
        
        Request Body:
        {
            "texts": ["Claim 1", "Claim 2", "Claim 3"],
            "language": "en" (optional)
        }
        
        Response:
        {
            "results": [...],
            "total": 3,
            "successful": 3,
            "total_processing_time": 2.5
        }
        """
        start_time = time.time()

        try:
            texts = request.data.get('texts', [])
            language = request.data.get('language', 'en')

            if not texts or not isinstance(texts, list):
                return Response(
                    {"error": "Please provide a list of texts to verify"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if len(texts) > 20:
                return Response(
                    {"error": "Maximum 20 texts allowed per batch"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            logger.info(f"Batch verification request: {len(texts)} texts")

            # Perform batch verification
            results = self.orchestrator.verify_batch(texts, language)

            # Format response
            response_results = []
            for result in results:
                response_results.append({
                    "factly_score": result.factly_score,
                    "classification": result.classification,
                    "confidence_level": result.confidence_level,
                    "recommended_verdict": result.recommended_verdict,
                    "summary": {
                        "headline": result.headline,
                        "explanation": result.explanation
                    },
                    "sources_consulted": result.sources_consulted,
                    "processing_time": result.processing_time
                })

            total_time = time.time() - start_time

            return Response({
                "results": response_results,
                "total": len(texts),
                "successful": len([r for r in results if r.factly_score > 0]),
                "total_processing_time": round(total_time, 2)
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Batch verification error: {e}", exc_info=True)
            return Response(
                {"error": f"Batch verification failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(['GET'])
def fast_verification_stats(request):
    """Get performance statistics for fast verification."""
    orchestrator = FastVerificationOrchestrator()
    stats = orchestrator.get_performance_stats()
    
    return Response({
        "performance": stats,
        "status": "operational"
    })


@api_view(['POST'])
def clear_cache(request):
    """Clear verification cache."""
    orchestrator = FastVerificationOrchestrator()
    orchestrator.cache.clear()
    
    return Response({
        "message": "Cache cleared successfully",
        "timestamp": time.time()
    })
