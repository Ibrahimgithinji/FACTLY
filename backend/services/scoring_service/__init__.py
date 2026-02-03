"""
Scoring Service Module

Provides Factly Score™ calculation and credibility assessment.
"""

from .scoring_service import ScoringService, ComponentScore, FactlyScoreResult

__all__ = [
    'ScoringService',
    'ComponentScore',
    'FactlyScoreResult'
]
