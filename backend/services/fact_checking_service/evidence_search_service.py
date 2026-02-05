"""
Evidence Search Service

Multi-source evidence gathering that searches across different APIs and sources
to find relevant information for claim verification.
"""

import os
import requests
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from .unified_schema import ClaimReview, RelatedNews, SourceReliability, PublisherCredibility
from .cache_manager import CacheManager
from .rate_limiter import RateLimiter

logger = logging.getLogger(__name__)


@dataclass
class EvidenceItem:
    """Represents a piece of evidence from any source."""
    source: str  # API or source name
    source_type: str  # 'fact_check', 'news', 'academic', 'official'
    title: str
    content: str
    url: Optional[str]
    published_date: Optional[datetime]
    credibility_score: float  # 0.0 to 1.0
    relevance_score: float  # 0.0 to 1.0
    verdict: Optional[str]  # For fact-checks
    metadata: Dict[str, Any]


@dataclass
class EvidenceCollection:
    """Collection of evidence from multiple sources."""
    claim: str
    evidence_items: List[EvidenceItem]
    source_diversity_score: float  # How diverse are the sources
    agreement_score: float  # How much do sources agree
    coverage_gaps: List[str]  # Missing evidence types
    timestamp: datetime


class EvidenceSearchService:
    """
    Multi-source evidence search service.
    
    Searches across multiple APIs and sources to gather evidence:
    - Google Fact Check Tools API
    - News APIs (NewsLdr, NewsAPI, etc.)
    - Academic sources (optional)
    - Official sources (optional)
    """

    # Trusted news domains for credibility assessment
    TRUSTED_NEWS_DOMAINS = {
        'reuters.com': 0.95,
        'apnews.com': 0.95,
        'bbc.com': 0.92,
        'bbc.co.uk': 0.92,
        'npr.org': 0.90,
        'nytimes.com': 0.88,
        'washingtonpost.com': 0.88,
        'theguardian.com': 0.87,
        'cnn.com': 0.85,
        'politifact.com': 0.95,
        'snopes.com': 0.93,
        'factcheck.org': 0.94,
        'ap.org': 0.95,
    }

    def __init__(self, cache_manager: Optional[CacheManager] = None):
        """
        Initialize the evidence search service.

        Args:
            cache_manager: Optional cache manager instance
        """
        self.cache = cache_manager or CacheManager()
        self.rate_limiter = RateLimiter()

        # API keys
        self.google_api_key = os.getenv('GOOGLE_FACT_CHECK_API_KEY')
        self.newsldr_api_key = os.getenv('NEWSLDR_API_KEY')
        self.newsapi_key = os.getenv('NEWSAPI_KEY')

        # Initialize API clients
        from .google_fact_check import GoogleFactCheckClient
        from .newsldr_api import NewsLdrClient

        self.google_client = GoogleFactCheckClient(
            api_key=self.google_api_key,
            cache_manager=self.cache
        ) if self.google_api_key else None

        self.newsldr_client = NewsLdrClient(
            api_key=self.newsldr_api_key,
            cache_manager=self.cache
        ) if self.newsldr_api_key else None
        
        # Log which clients are available
        google_status = "READY" if self.google_client else "NOT AVAILABLE"
        newsldr_status = "READY" if self.newsldr_client else "NOT AVAILABLE"
        newsapi_status = "READY" if self.newsapi_key else "NOT AVAILABLE"
        logger.info(f"EvidenceSearchService initialized - Google: {google_status}, NewsLdr: {newsldr_status}, NewsAPI: {newsapi_status}")

    def search_evidence(self, claim: str, language: str = "en",
                        max_results_per_source: int = 10) -> EvidenceCollection:
        """
        Search for evidence across multiple sources.

        Args:
            claim: The claim to search evidence for
            language: Language code
            max_results_per_source: Maximum results per API

        Returns:
            EvidenceCollection with results from all sources
        """
        logger.info(f"Searching evidence for claim: {claim[:100]}...")

        all_evidence = []
        search_errors = []

        # Search Google Fact Check
        if self.google_client:
            try:
                google_evidence = self._search_google_fact_check(
                    claim, language, max_results_per_source
                )
                all_evidence.extend(google_evidence)
                logger.info(f"Found {len(google_evidence)} items from Google Fact Check")
            except Exception as e:
                logger.error(f"Google Fact Check search failed: {e}")
                search_errors.append(f"Google Fact Check: {str(e)}")

        # Search NewsLdr
        if self.newsldr_client:
            try:
                newsldr_evidence = self._search_newsldr(
                    claim, max_results_per_source
                )
                all_evidence.extend(newsldr_evidence)
                logger.info(f"Found {len(newsldr_evidence)} items from NewsLdr")
            except Exception as e:
                logger.error(f"NewsLdr search failed: {e}")
                search_errors.append(f"NewsLdr: {str(e)}")

        # Search NewsAPI as fallback
        if self.newsapi_key:
            try:
                newsapi_evidence = self._search_newsapi(
                    claim, language, max_results_per_source
                )
                all_evidence.extend(newsapi_evidence)
                logger.info(f"Found {len(newsapi_evidence)} items from NewsAPI")
            except Exception as e:
                logger.error(f"NewsAPI search failed: {e}")
                search_errors.append(f"NewsAPI: {str(e)}")

        # Calculate diversity and agreement
        diversity_score = self._calculate_source_diversity(all_evidence)
        agreement_score = self._calculate_source_agreement(all_evidence)
        coverage_gaps = self._identify_coverage_gaps(all_evidence, search_errors)

        # Sort by combined credibility and relevance
        all_evidence.sort(
            key=lambda x: (x.credibility_score * 0.6 + x.relevance_score * 0.4),
            reverse=True
        )

        return EvidenceCollection(
            claim=claim,
            evidence_items=all_evidence,
            source_diversity_score=diversity_score,
            agreement_score=agreement_score,
            coverage_gaps=coverage_gaps,
            timestamp=datetime.now()
        )

    def _search_google_fact_check(self, claim: str, language: str,
                                   max_results: int) -> List[EvidenceItem]:
        """Search Google Fact Check Tools API."""
        claim_reviews = self.google_client.search_claims(claim, language, max_results)

        evidence_items = []
        for review in claim_reviews:
            evidence = EvidenceItem(
                source="Google Fact Check",
                source_type="fact_check",
                title=f"Fact Check: {review.claim[:100]}...",
                content=f"Verdict: {review.verdict}",
                url=review.url,
                published_date=review.review_date,
                credibility_score=review.publisher.credibility_score,
                relevance_score=review.confidence_score,
                verdict=review.verdict,
                metadata={
                    'publisher': review.publisher.name,
                    'language': review.language
                }
            )
            evidence_items.append(evidence)

        return evidence_items

    def _search_newsldr(self, claim: str, max_results: int) -> List[EvidenceItem]:
        """Search NewsLdr API."""
        related_news = self.newsldr_client.get_related_news(claim, max_results)

        evidence_items = []
        for news in related_news:
            # Get source reliability if available
            reliability = None
            try:
                reliability = self.newsldr_client.get_source_reliability(news.source)
            except:
                pass

            credibility = reliability.reliability_score if reliability else 0.5

            evidence = EvidenceItem(
                source=news.source,
                source_type="news",
                title=news.title,
                content=f"Related news article from {news.source}",
                url=news.url,
                published_date=news.publish_date,
                credibility_score=credibility,
                relevance_score=news.relevance_score,
                verdict=None,
                metadata={
                    'sentiment': news.sentiment,
                    'source_reliability': reliability.to_dict() if reliability else None
                }
            )
            evidence_items.append(evidence)

        return evidence_items

    def _search_newsapi(self, claim: str, language: str, max_results: int) -> List[EvidenceItem]:
        """Search NewsAPI as a fallback news source."""
        cache_key = {
            'query': claim,
            'language': language,
            'max_results': max_results,
            'source': 'newsapi'
        }

        cached = self.cache.get('newsapi', cache_key)
        if cached:
            return cached

        url = "https://newsapi.org/v2/everything"
        params = {
            'q': claim,
            'language': language if language == 'en' else 'en',
            'sortBy': 'relevancy',
            'pageSize': max_results,
            'apiKey': self.newsapi_key
        }

        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        evidence_items = []
        for article in data.get('articles', []):
            source_name = article.get('source', {}).get('name', 'Unknown')
            domain = self._extract_domain(article.get('url', ''))
            credibility = self.TRUSTED_NEWS_DOMAINS.get(domain, 0.5)

            # Parse date
            published_date = None
            date_str = article.get('publishedAt', '')
            if date_str:
                try:
                    published_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                except:
                    pass

            evidence = EvidenceItem(
                source=source_name,
                source_type="news",
                title=article.get('title', ''),
                content=article.get('description', ''),
                url=article.get('url'),
                published_date=published_date,
                credibility_score=credibility,
                relevance_score=0.5,  # Default relevance
                verdict=None,
                metadata={
                    'author': article.get('author'),
                    'domain': domain
                }
            )
            evidence_items.append(evidence)

        self.cache.set('newsapi', cache_key, evidence_items)
        return evidence_items

    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        if not url:
            return ''
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc.replace('www.', '')
        except:
            return ''

    def _calculate_source_diversity(self, evidence_items: List[EvidenceItem]) -> float:
        """
        Calculate how diverse the evidence sources are.
        
        Higher diversity = more independent verification = more reliable
        """
        if not evidence_items:
            return 0.0

        # Count unique sources
        sources = set(item.source for item in evidence_items)
        source_types = set(item.source_type for item in evidence_items)

        # Calculate diversity score
        total_items = len(evidence_items)
        unique_sources = len(sources)
        unique_types = len(source_types)

        # Diversity factors:
        # - More unique sources is better (max 0.5)
        # - More source types is better (max 0.5)
        source_diversity = min(0.5, unique_sources / max(1, total_items) * 0.5)
        type_diversity = min(0.5, unique_types / 4 * 0.5)  # 4 types max

        return source_diversity + type_diversity

    def _calculate_source_agreement(self, evidence_items: List[EvidenceItem]) -> float:
        """
        Calculate how much sources agree with each other.
        
        Returns a score between 0 and 1, where:
        - 1.0 = perfect agreement
        - 0.5 = mixed/neutral
        - 0.0 = complete disagreement
        """
        if not evidence_items:
            return 0.0

        # Get verdicts from fact-checks
        verdicts = []
        for item in evidence_items:
            if item.verdict:
                verdict_score = self._verdict_to_score(item.verdict)
                verdicts.append(verdict_score)

        if len(verdicts) < 2:
            # Not enough verdicts to measure agreement
            return 0.5

        # Calculate variance in verdicts
        mean_verdict = sum(verdicts) / len(verdicts)
        variance = sum((v - mean_verdict) ** 2 for v in verdicts) / len(verdicts)

        # Convert variance to agreement score (lower variance = higher agreement)
        agreement = 1.0 - min(1.0, variance * 4)  # Scale factor of 4

        return max(0.0, min(1.0, agreement))

    def _verdict_to_score(self, verdict: str) -> float:
        """Convert verdict string to numerical score."""
        verdict_scores = {
            'true': 1.0,
            'mostly true': 0.9,
            'half true': 0.6,
            'mostly false': 0.3,
            'false': 0.0,
            'misleading': 0.4,
            'pants on fire': 0.0,
            'unverified': 0.5,
            'satire': 0.2
        }
        return verdict_scores.get(verdict.lower(), 0.5)

    def _identify_coverage_gaps(self, evidence_items: List[EvidenceItem],
                                 errors: List[str]) -> List[str]:
        """Identify gaps in evidence coverage."""
        gaps = []

        source_types = set(item.source_type for item in evidence_items)

        if 'fact_check' not in source_types:
            gaps.append("No professional fact-checks found")

        if 'news' not in source_types:
            gaps.append("No news coverage found")

        if len(evidence_items) < 3:
            gaps.append("Limited number of sources")

        if errors:
            gaps.append("Some sources could not be queried")

        return gaps

    def assess_source_credibility(self, source_name: str, domain: Optional[str] = None) -> float:
        """
        Assess the credibility of a news source.

        Args:
            source_name: Name of the source
            domain: Domain of the source

        Returns:
            Credibility score between 0.0 and 1.0
        """
        # Check trusted domains first
        if domain and domain in self.TRUSTED_NEWS_DOMAINS:
            return self.TRUSTED_NEWS_DOMAINS[domain]

        # Try NewsLdr for source reliability
        if self.newsldr_client:
            try:
                reliability = self.newsldr_client.get_source_reliability(source_name)
                if reliability:
                    return reliability.reliability_score
            except:
                pass

        # Default moderate credibility
        return 0.5
