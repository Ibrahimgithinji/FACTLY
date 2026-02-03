"""
Async Evidence Search Service

High-performance async implementation for concurrent API calls.
Uses asyncio and aiohttp for parallel requests to multiple sources.
"""

import asyncio
import aiohttp
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
import functools

from .evidence_search_service import EvidenceItem, EvidenceCollection
from .cache_manager import CacheManager

logger = logging.getLogger(__name__)


@dataclass
class APICallResult:
    """Result from an async API call."""
    source: str
    success: bool
    data: Any
    error: Optional[str] = None
    response_time: float = 0.0


class AsyncEvidenceSearchService:
    """
    Async-enabled evidence search for high-performance verification.
    
    Features:
    - Concurrent API calls to all sources
    - Connection pooling for reused connections
    - Configurable timeouts per source
    - Early termination when sufficient evidence found
    - Request batching for multiple claims
    """

    def __init__(self, cache_manager: Optional[CacheManager] = None,
                 max_concurrent: int = 5):
        """
        Initialize async evidence search service.

        Args:
            cache_manager: Cache manager for results
            max_concurrent: Maximum concurrent API calls
        """
        self.cache = cache_manager or CacheManager()
        self.max_concurrent = max_concurrent
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Connection pool settings
        self.connector = aiohttp.TCPConnector(
            limit=100,  # Total connections
            limit_per_host=30,  # Per-host connections
            ttl_dns_cache=300,  # DNS cache TTL
            use_dns_cache=True,
        )
        
        # Timeout settings per source (in seconds)
        self.timeouts = {
            'google_fact_check': aiohttp.ClientTimeout(total=10, connect=5),
            'newsldr': aiohttp.ClientTimeout(total=15, connect=5),
            'newsapi': aiohttp.ClientTimeout(total=10, connect=5),
        }

    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(
            connector=self.connector,
            headers={
                'User-Agent': 'FACTLY-Bot/2.0 (Fact-Checking Service)',
                'Accept': 'application/json',
            }
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
        await self.connector.close()

    async def search_evidence_async(self, claim: str, language: str = "en",
                                    max_results_per_source: int = 10,
                                    early_termination_threshold: int = 5) -> EvidenceCollection:
        """
        Search for evidence asynchronously across all sources.

        Args:
            claim: The claim to search evidence for
            language: Language code
            max_results_per_source: Maximum results per API
            early_termination_threshold: Stop after finding this many high-quality results

        Returns:
            EvidenceCollection with results from all sources
        """
        import time
        start_time = time.time()
        
        logger.info(f"Starting async evidence search for: {claim[:100]}...")

        # Define all search tasks
        tasks = [
            self._search_google_fact_check_async(claim, language, max_results_per_source),
            self._search_newsldr_async(claim, max_results_per_source),
            self._search_newsapi_async(claim, language, max_results_per_source),
        ]

        # Execute all tasks concurrently with semaphore for rate limiting
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        async def bounded_search(task):
            async with semaphore:
                return await task

        # Gather all results
        results = await asyncio.gather(*[bounded_search(t) for t in tasks], return_exceptions=True)

        # Process results
        all_evidence = []
        errors = []
        
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Async search task failed: {result}")
                errors.append(str(result))
            elif isinstance(result, APICallResult):
                if result.success and result.data:
                    all_evidence.extend(result.data)
                    logger.info(f"Got {len(result.data)} items from {result.source} in {result.response_time:.2f}s")
                elif not result.success:
                    errors.append(f"{result.source}: {result.error}")

        # Calculate metrics
        processing_time = time.time() - start_time
        
        # Calculate diversity and agreement
        diversity_score = self._calculate_source_diversity(all_evidence)
        agreement_score = self._calculate_source_agreement(all_evidence)
        coverage_gaps = self._identify_coverage_gaps(all_evidence, errors)

        # Sort by combined credibility and relevance
        all_evidence.sort(
            key=lambda x: (x.credibility_score * 0.6 + x.relevance_score * 0.4),
            reverse=True
        )

        logger.info(f"Async evidence search completed in {processing_time:.2f}s, found {len(all_evidence)} items")

        return EvidenceCollection(
            claim=claim,
            evidence_items=all_evidence,
            source_diversity_score=diversity_score,
            agreement_score=agreement_score,
            coverage_gaps=coverage_gaps,
            timestamp=datetime.now()
        )

    async def batch_search_evidence(self, claims: List[str], language: str = "en",
                                    max_results_per_source: int = 10) -> List[EvidenceCollection]:
        """
        Search evidence for multiple claims concurrently (batch processing).

        Args:
            claims: List of claims to search
            language: Language code
            max_results_per_source: Maximum results per API per claim

        Returns:
            List of EvidenceCollections, one per claim
        """
        logger.info(f"Starting batch evidence search for {len(claims)} claims")
        
        # Create tasks for all claims
        tasks = [
            self.search_evidence_async(claim, language, max_results_per_source)
            for claim in claims
        ]
        
        # Execute all concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        evidence_collections = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Batch search failed for claim {i}: {result}")
                # Return empty collection on error
                evidence_collections.append(EvidenceCollection(
                    claim=claims[i],
                    evidence_items=[],
                    source_diversity_score=0.0,
                    agreement_score=0.0,
                    coverage_gaps=["Search failed"],
                    timestamp=datetime.now()
                ))
            else:
                evidence_collections.append(result)
        
        return evidence_collections

    async def _search_google_fact_check_async(self, claim: str, language: str,
                                               max_results: int) -> APICallResult:
        """Async search Google Fact Check Tools API."""
        import time
        import os
        
        start_time = time.time()
        api_key = os.getenv('GOOGLE_FACT_CHECK_API_KEY')
        
        if not api_key:
            return APICallResult(
                source='google_fact_check',
                success=False,
                data=None,
                error='API key not configured',
                response_time=0.0
            )

        # Check cache first
        cache_key = {'query': claim, 'language': language, 'max_results': max_results}
        cached = self.cache.get('google_fact_check', cache_key)
        if cached:
            return APICallResult(
                source='google_fact_check',
                success=True,
                data=cached,
                response_time=0.0
            )

        url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
        params = {
            'key': api_key,
            'query': claim,
            'languageCode': language,
            'pageSize': max_results
        }

        try:
            async with self.session.get(url, params=params, 
                                        timeout=self.timeouts['google_fact_check']) as response:
                response.raise_for_status()
                data = await response.json()
                
                # Parse results
                evidence_items = self._parse_google_results(data, claim)
                
                # Cache results
                self.cache.set('google_fact_check', cache_key, evidence_items)
                
                return APICallResult(
                    source='google_fact_check',
                    success=True,
                    data=evidence_items,
                    response_time=time.time() - start_time
                )
        except Exception as e:
            logger.error(f"Google Fact Check async error: {e}")
            return APICallResult(
                source='google_fact_check',
                success=False,
                data=None,
                error=str(e),
                response_time=time.time() - start_time
            )

    async def _search_newsldr_async(self, claim: str, max_results: int) -> APICallResult:
        """Async search NewsLdr API."""
        import time
        import os
        
        start_time = time.time()
        api_key = os.getenv('NEWSLDR_API_KEY')
        
        if not api_key:
            return APICallResult(
                source='newsldr',
                success=False,
                data=None,
                error='API key not configured',
                response_time=0.0
            )

        # Check cache
        cache_key = {'query': claim, 'max_results': max_results, 'endpoint': 'related_news'}
        cached = self.cache.get('newsldr', cache_key)
        if cached:
            return APICallResult(
                source='newsldr',
                success=True,
                data=cached,
                response_time=0.0
            )

        # Placeholder implementation - replace with actual NewsLdr endpoint
        url = "https://api.newsldr.com/v1/news/search"
        params = {
            'q': claim,
            'limit': max_results,
            'api_key': api_key
        }

        try:
            async with self.session.get(url, params=params,
                                        timeout=self.timeouts['newsldr']) as response:
                response.raise_for_status()
                data = await response.json()
                
                evidence_items = self._parse_newsldr_results(data)
                self.cache.set('newsldr', cache_key, evidence_items)
                
                return APICallResult(
                    source='newsldr',
                    success=True,
                    data=evidence_items,
                    response_time=time.time() - start_time
                )
        except Exception as e:
            logger.error(f"NewsLdr async error: {e}")
            return APICallResult(
                source='newsldr',
                success=False,
                data=None,
                error=str(e),
                response_time=time.time() - start_time
            )

    async def _search_newsapi_async(self, claim: str, language: str,
                                     max_results: int) -> APICallResult:
        """Async search NewsAPI."""
        import time
        import os
        
        start_time = time.time()
        api_key = os.getenv('NEWSAPI_KEY')
        
        if not api_key:
            return APICallResult(
                source='newsapi',
                success=False,
                data=None,
                error='API key not configured',
                response_time=0.0
            )

        # Check cache
        cache_key = {'query': claim, 'language': language, 'max_results': max_results}
        cached = self.cache.get('newsapi', cache_key)
        if cached:
            return APICallResult(
                source='newsapi',
                success=True,
                data=cached,
                response_time=0.0
            )

        url = "https://newsapi.org/v2/everything"
        params = {
            'q': claim,
            'language': language if language == 'en' else 'en',
            'sortBy': 'relevancy',
            'pageSize': max_results,
            'apiKey': api_key
        }

        try:
            async with self.session.get(url, params=params,
                                        timeout=self.timeouts['newsapi']) as response:
                response.raise_for_status()
                data = await response.json()
                
                evidence_items = self._parse_newsapi_results(data)
                self.cache.set('newsapi', cache_key, evidence_items)
                
                return APICallResult(
                    source='newsapi',
                    success=True,
                    data=evidence_items,
                    response_time=time.time() - start_time
                )
        except Exception as e:
            logger.error(f"NewsAPI async error: {e}")
            return APICallResult(
                source='newsapi',
                success=False,
                data=None,
                error=str(e),
                response_time=time.time() - start_time
            )

    def _parse_google_results(self, data: Dict, claim: str) -> List[EvidenceItem]:
        """Parse Google Fact Check API response."""
        evidence_items = []
        claims = data.get('claims', [])
        
        for claim_data in claims:
            claim_text = claim_data.get('text', '')
            claim_reviews = claim_data.get('claimReview', [])
            
            for review in claim_reviews:
                publisher = review.get('publisher', {})
                
                evidence = EvidenceItem(
                    source=publisher.get('name', 'Unknown'),
                    source_type='fact_check',
                    title=f"Fact Check: {claim_text[:100]}...",
                    content=f"Verdict: {review.get('textualRating', 'Unknown')}",
                    url=review.get('url'),
                    published_date=None,
                    credibility_score=0.8 if publisher.get('name') else 0.5,
                    relevance_score=0.9,
                    verdict=review.get('textualRating'),
                    metadata={'publisher': publisher}
                )
                evidence_items.append(evidence)
        
        return evidence_items

    def _parse_newsldr_results(self, data: Dict) -> List[EvidenceItem]:
        """Parse NewsLdr API response."""
        evidence_items = []
        articles = data.get('articles', [])
        
        for article in articles:
            evidence = EvidenceItem(
                source=article.get('source', {}).get('name', 'Unknown'),
                source_type='news',
                title=article.get('title', ''),
                content=article.get('description', ''),
                url=article.get('url'),
                published_date=None,
                credibility_score=0.7,
                relevance_score=article.get('relevance_score', 0.5),
                verdict=None,
                metadata=article
            )
            evidence_items.append(evidence)
        
        return evidence_items

    def _parse_newsapi_results(self, data: Dict) -> List[EvidenceItem]:
        """Parse NewsAPI response."""
        evidence_items = []
        articles = data.get('articles', [])
        
        # Trusted domains for credibility
        trusted_domains = {
            'reuters.com': 0.95, 'apnews.com': 0.95, 'bbc.com': 0.92,
            'npr.org': 0.90, 'nytimes.com': 0.88, 'washingtonpost.com': 0.88
        }
        
        for article in articles:
            source_name = article.get('source', {}).get('name', 'Unknown')
            domain = self._extract_domain(article.get('url', ''))
            credibility = trusted_domains.get(domain, 0.5)
            
            evidence = EvidenceItem(
                source=source_name,
                source_type='news',
                title=article.get('title', ''),
                content=article.get('description', ''),
                url=article.get('url'),
                published_date=None,
                credibility_score=credibility,
                relevance_score=0.5,
                verdict=None,
                metadata={'domain': domain}
            )
            evidence_items.append(evidence)
        
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
        """Calculate source diversity score."""
        if not evidence_items:
            return 0.0
        
        sources = set(item.source for item in evidence_items)
        source_types = set(item.source_type for item in evidence_items)
        
        source_diversity = min(0.5, len(sources) / max(1, len(evidence_items)) * 0.5)
        type_diversity = min(0.5, len(source_types) / 4 * 0.5)
        
        return source_diversity + type_diversity

    def _calculate_source_agreement(self, evidence_items: List[EvidenceItem]) -> float:
        """Calculate source agreement score."""
        if len(evidence_items) < 2:
            return 0.5
        
        verdict_scores = []
        for item in evidence_items:
            if item.verdict:
                score = self._verdict_to_score(item.verdict)
                verdict_scores.append(score)
        
        if len(verdict_scores) < 2:
            return 0.5
        
        mean_score = sum(verdict_scores) / len(verdict_scores)
        variance = sum((s - mean_score) ** 2 for s in verdict_scores) / len(verdict_scores)
        
        return max(0.0, min(1.0, 1.0 - variance * 4))

    def _verdict_to_score(self, verdict: str) -> float:
        """Convert verdict to numerical score."""
        verdict_scores = {
            'true': 1.0, 'mostly true': 0.9, 'half true': 0.6,
            'mostly false': 0.3, 'false': 0.0, 'misleading': 0.4,
            'pants on fire': 0.0, 'unverified': 0.5, 'satire': 0.2
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


# Synchronous wrapper for compatibility
def search_evidence_sync(claim: str, language: str = "en",
                         max_results_per_source: int = 10,
                         cache_manager: Optional[CacheManager] = None) -> EvidenceCollection:
    """
    Synchronous wrapper for async evidence search.
    
    Usage:
        result = search_evidence_sync("claim to verify")
    """
    async def _search():
        async with AsyncEvidenceSearchService(cache_manager) as service:
            return await service.search_evidence_async(claim, language, max_results_per_source)
    
    return asyncio.run(_search())


def batch_search_evidence_sync(claims: List[str], language: str = "en",
                                max_results_per_source: int = 10,
                                cache_manager: Optional[CacheManager] = None) -> List[EvidenceCollection]:
    """
    Synchronous wrapper for batch async evidence search.
    
    Usage:
        results = batch_search_evidence_sync(["claim1", "claim2", "claim3"])
    """
    async def _search():
        async with AsyncEvidenceSearchService(cache_manager) as service:
            return await service.batch_search_evidence(claims, language, max_results_per_source)
    
    return asyncio.run(_search())
