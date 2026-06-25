"""
Agent API Views

Endpoints for the Factly AI Agent — chat, digest, and trending.
"""

import logging
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

from .agent_service import FactlyAgent

logger = logging.getLogger(__name__)
agent = FactlyAgent()


class AgentRateThrottle(AnonRateThrottle):
    rate = "20/minute"
    scope = "agent"


class ChatView(APIView):
    """
    POST /api/agent/chat/

    Ask the agent a question. Returns a verified answer with sources.
    Body: {"query": "your question here"}
    """

    permission_classes = [AllowAny]
    throttle_classes = [AgentRateThrottle]

    def post(self, request):
        query = request.data.get("query", "").strip()
        if not query:
            return Response(
                {"error": "Please provide a query."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            result = agent.chat(query)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Agent chat error: {e}", exc_info=True)
            return Response(
                {
                    "error": "Failed to process your query. Please try again.",
                    "answer": "I encountered an error while searching. Please try again shortly.",
                    "sources": [],
                    "fact_checks": [],
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class DigestView(APIView):
    """
    GET /api/agent/digest/?hours=24

    Get a daily/weekly digest of verified news.
    Optional: ?hours=24 (default) or ?hours=168 for weekly
    """

    permission_classes = [AllowAny]
    throttle_classes = [AgentRateThrottle]

    def get(self, request):
        hours = request.query_params.get("hours", 24)
        try:
            hours = int(hours)
        except (ValueError, TypeError):
            hours = 24
        hours = max(1, min(hours, 168))

        try:
            result = agent.digest(hours=hours)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Agent digest error: {e}", exc_info=True)
            return Response(
                {"error": "Failed to generate digest."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class TrendingView(APIView):
    """
    GET /api/agent/trending/

    Get trending topics with real-time verification status.
    """

    permission_classes = [AllowAny]
    throttle_classes = [AgentRateThrottle]

    def get(self, request):
        try:
            result = agent.trending()
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Agent trending error: {e}", exc_info=True)
            return Response(
                {"error": "Failed to fetch trending topics."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
