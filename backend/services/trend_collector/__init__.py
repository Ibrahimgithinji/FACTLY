"""
Trend Collector Service

AI-Powered Trend Discovery and Misinformation Detection Engine

Components:
- Trend Aggregator: Multi-source trend collection
- Trend Normalizer: Data normalization pipeline
- Claim Extractor: NLP-based claim extraction
- Misinformation Detector: Risk scoring algorithm
- Trend Ranker: Intelligent priority scoring
- Trend Predictor: AI-based trend forecasting
"""

from .models import (
    TrendSource,
    Trend,
    Claim,
    TrendPrediction,
    SourceCredibility,
    TrendCollectionLog,
    MisinformationAlert,
)

from .trend_aggregator import (
    TrendAggregatorService,
    NormalizedTrend,
)

from .analysis_engine import (
    TrendNormalizer,
    ClaimExtractor,
    MisinformationDetector,
    TrendRanker,
    TrendPredictor,
    MetricsCollector,
)

__all__ = [
    # Models
    'TrendSource',
    'Trend',
    'Claim',
    'TrendPrediction',
    'SourceCredibility',
    'TrendCollectionLog',
    'MisinformationAlert',
    # Services
    'TrendAggregatorService',
    'NormalizedTrend',
    'TrendNormalizer',
    'ClaimExtractor',
    'MisinformationDetector',
    'TrendRanker',
    'TrendPredictor',
    'MetricsCollector',
]
