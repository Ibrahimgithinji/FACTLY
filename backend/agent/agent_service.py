"""
Factly AI Agent Service

Core agentic logic for:
- Chat queries: answer questions with verified sources
- Daily digest: curated, fact-checked news summary
- Trending: what's being discussed with verification status

This is the "agentic feature" — an intelligent assistant that
proactively fetches, verifies, and presents information.
"""

import logging
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

from django.conf import settings

logger = logging.getLogger(__name__)


class FactlyAgent:
    """
    The Factly AI Agent — a simple but powerful engine that
    aggregates news, runs fact-checking, and returns structured,
    verified information in a conversational format.
    """

    def __init__(self):
        self._load_services()

    def _load_services(self):
        """Lazy-load external services so missing API keys don't crash init."""
        self._cache_manager = None
        self._realtime_news = None
        self._scoring_service = None

    @property
    def cache_manager(self):
        if self._cache_manager is None:
            from services.fact_checking_service.cache_manager import CacheManager
            self._cache_manager = CacheManager()
        return self._cache_manager

    @property
    def realtime_news(self):
        if self._realtime_news is None:
            from services.fact_checking_service.real_time_news_service import RealTimeNewsService
            self._realtime_news = RealTimeNewsService(cache_manager=self.cache_manager)
        return self._realtime_news

    @property
    def scoring_service(self):
        if self._scoring_service is None:
            from verification.scoring_service import FactCheckScoringService
            self._scoring_service = FactCheckScoringService()
        return self._scoring_service

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def chat(self, query: str, user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Answer a user query with verified information.

        Returns:
            answer: plain-text summary answer
            sources: list of source articles with verification scores
            fact_checks: list of fact-check results
            trending_context: related trending topics
        """
        if not query or not query.strip():
            return self._empty_response("Please ask a question about news or a claim to verify.")

        query = query.strip()

        # 1. Fetch relevant news
        news_items = self._fetch_news_for_query(query)

        # 2. Run fact-checking / scoring on each item
        scored_items = []
        for item in news_items[:10]:
            score = self._score_item(item)
            scored_items.append({**item, **score})

        # 3. Build an answer summary
        answer = self._build_answer(query, scored_items)

        # 4. Get trending context
        trending = self._get_trending_context()

        return {
            "query": query,
            "answer": answer,
            "sources": scored_items[:8],
            "fact_checks": self._extract_fact_checks(scored_items),
            "trending_context": trending[:5],
            "generated_at": datetime.now().isoformat(),
        }

    def digest(self, hours: int = 24) -> Dict[str, Any]:
        """
        Generate a daily/weekly digest of verified news.

        Returns:
            headline: today's top story
            top_stories: list of important stories with scores
            categories: stories grouped by category (tech, health, etc.)
            verification_summary: overall trust snapshot
        """
        news_items = self._fetch_latest_news(max_age_hours=hours)

        scored_items = []
        for item in news_items[:20]:
            score = self._score_item(item)
            scored_items.append({**item, **score})

        scored_items.sort(key=lambda x: x.get("importance_score", 0), reverse=True)

        categories = self._categorize_stories(scored_items)
        headline = scored_items[0] if scored_items else None
        verified_count = sum(1 for s in scored_items if s.get("verdict") == "true")
        suspicious_count = sum(1 for s in scored_items if s.get("verdict") in ("false", "misleading"))

        return {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "headline": headline,
            "top_stories": scored_items[:10],
            "categories": categories,
            "verification_summary": {
                "total_stories": len(scored_items),
                "verified_true": verified_count,
                "suspicious": suspicious_count,
                "trust_score": round((verified_count / max(len(scored_items), 1)) * 100, 1),
            },
            "sources_checked": list(set(s.get("source_name", "Unknown") for s in scored_items)),
            "generated_at": datetime.now().isoformat(),
        }

    def trending(self) -> Dict[str, Any]:
        """Get trending topics with real-time verification."""
        from services.tasks.refresh_tasks import get_trending_topics
        data = get_trending_topics()
        topics = data.get("topics", [])
        events = data.get("global_events", [])
        return {
            "topics": topics[:10],
            "global_events": events[:5],
            "last_updated": (data.get("last_updated") or datetime.now()).isoformat()
            if hasattr(data.get("last_updated"), "isoformat")
            else str(data.get("last_updated", "")),
        }

    # ------------------------------------------------------------------
    # Internal: News Fetching
    # ------------------------------------------------------------------

    def _fetch_news_for_query(self, query: str) -> List[Dict[str, Any]]:
        """Search news from all available sources."""
        items = []
        try:
            results = self.realtime_news.get_real_time_news(
                query, max_results=15, max_age_hours=72
            )
            items.extend(results)
        except Exception as e:
            logger.warning(f"Agent news fetch failed: {e}")

        if not items:
            items = self._rss_fallback(query)

        return items

    def _fetch_latest_news(self, max_age_hours: int = 24) -> List[Dict[str, Any]]:
        """Fetch the latest general news."""
        items = []
        for q in ["breaking news", "top stories", "world news"]:
            try:
                results = self.realtime_news.get_real_time_news(
                    q, max_results=10, max_age_hours=max_age_hours
                )
                items.extend(results)
            except Exception:
                pass

        if not items:
            items = self._rss_fallback("news")

        seen = set()
        unique = []
        for item in items:
            key = item.get("title", "")[:80]
            if key and key not in seen:
                seen.add(key)
                unique.append(item)
        return unique[:20]

    def _rss_fallback(self, query: str) -> List[Dict[str, Any]]:
        """Fallback to RSS feeds when APIs are unavailable."""
        try:
            rss_feeds = getattr(self.realtime_news, "RSS_FEEDS", {})
            items = []
            for name, url in rss_feeds.items():
                try:
                    results = self.realtime_news._fetch_single_rss(
                        url, query=query, max_results=5
                    )
                    items.extend(results)
                except Exception:
                    continue
            return items
        except Exception:
            return []

    # ------------------------------------------------------------------
    # Internal: Scoring / Fact-Checking
    # ------------------------------------------------------------------

    def _score_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Run the scoring engine on a news item."""
        title = item.get("title", "") or ""
        content = item.get("content", "") or item.get("summary", "") or ""
        text = f"{title}. {content}"

        try:
            result = self.scoring_service.calculate_score(
                claim_text=text,
                publisher=item.get("source_name") or item.get("source", ""),
                author=item.get("author", ""),
            )
            return {
                "credibility_score": result.get("credibility_score", 50),
                "verdict": result.get("verdict", "unverifiable"),
                "bias_score": result.get("bias_score", 50),
                "sensationalism_score": result.get("sensationalism_score", 50),
                "importance_score": result.get("overall_score", 50),
                "confidence": result.get("confidence", "low"),
            }
        except Exception as e:
            logger.warning(f"Scoring failed for item '{title[:50]}': {e}")
            return {
                "credibility_score": 50,
                "verdict": "unverifiable",
                "bias_score": 50,
                "sensationalism_score": 50,
                "importance_score": 50,
                "confidence": "low",
            }

    def _extract_fact_checks(
        self, scored_items: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Extract specific fact-check claims from scored items."""
        checks = []
        for item in scored_items[:5]:
            verdict = item.get("verdict", "unverifiable")
            if verdict in ("true", "mostly_true"):
                label = "Verified True"
            elif verdict in ("false", "mostly_false"):
                label = "Misleading/False"
            elif verdict == "misleading":
                label = "Misleading"
            else:
                label = "Unverifiable"

            checks.append({
                "claim": item.get("title", "")[:120],
                "verdict": verdict,
                "label": label,
                "confidence": item.get("confidence", "low"),
                "score": item.get("credibility_score", 50),
                "source": item.get("source_name") or item.get("source", "Unknown"),
            })
        return checks

    # ------------------------------------------------------------------
    # Internal: Answer Building
    # ------------------------------------------------------------------

    def _build_answer(
        self, query: str, scored_items: List[Dict[str, Any]]
    ) -> str:
        """Build a natural-language answer from scored items."""
        if not scored_items:
            return (
                f"I couldn't find any news articles about '{query}' right now. "
                "Try a different search term or check back later."
            )

        top = scored_items[0]
        verdict = top.get("verdict", "unverifiable")
        score = top.get("credibility_score", 50)

        if verdict in ("true", "mostly_true"):
            quality = "well-supported"
        elif verdict in ("false", "mostly_false"):
            quality = "low credibility"
        elif verdict == "misleading":
            quality = "misleading"
        else:
            quality = "unverifiable"

        parts = [
            f"I found {len(scored_items)} relevant articles about '{query}'.",
            "",
            f"**Top Story:** {top.get('title', 'N/A')}",
            f"**Source:** {top.get('source_name') or top.get('source', 'Unknown')}",
            f"**Credibility Score:** {score}/100 ({quality})",
            f"**Confidence:** {top.get('confidence', 'low').title()}",
        ]

        high_score = [s for s in scored_items if s.get("credibility_score", 0) >= 70]
        if high_score:
            parts.append(
                f"\n{len(high_score)} of {len(scored_items)} articles have "
                "high credibility scores (70+)."
            )

        low_score = [s for s in scored_items if s.get("credibility_score", 0) < 40]
        if low_score:
            parts.append(
                f"\n⚠️ {len(low_score)} article(s) have low credibility scores "
                "— review carefully before sharing."
            )

        parts.append(
            "\n\n💡 Always cross-check information with multiple trusted sources."
        )

        return "\n".join(parts)

    def _categorize_stories(
        self, scored_items: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Group stories into categories."""
        categories = {
            "technology": [],
            "health": [],
            "science": [],
            "politics": [],
            "business": [],
            "world": [],
            "other": [],
        }

        keywords = {
            "technology": ["tech", "ai", "digital", "software", "cyber", "computer",
                          "apple", "google", "microsoft", "data", "robot", "startup"],
            "health": ["health", "medical", "drug", "vaccine", "hospital", "disease",
                      "covid", "patient", "doctor", "mental"],
            "science": ["science", "research", "study", "space", "climate", "nasa",
                       "discovery", "scientist", "genetic", "quantum"],
            "politics": ["election", "president", "congress", "senate", "vote",
                        "political", "government", "minister", "policy", "law"],
            "business": ["market", "stock", "economy", "bank", "trade", "finance",
                        "investment", "economic", "inflation", "revenue"],
            "world": ["world", "international", "global", "foreign", "europe",
                     "china", "russia", "ukraine", "africa", "asia"],
        }

        for item in scored_items:
            title = (item.get("title", "") or "").lower()
            assigned = False
            for cat, words in keywords.items():
                if any(w in title for w in words):
                    categories[cat].append(item)
                    assigned = True
                    break
            if not assigned:
                categories["other"].append(item)

        return {k: v[:5] for k, v in categories.items() if v}

    def _get_trending_context(self) -> List[Dict[str, Any]]:
        """Get current trending topics as context."""
        try:
            from services.tasks.refresh_tasks import get_trending_topics
            data = get_trending_topics()
            return data.get("topics", [])[:5]
        except Exception:
            return []

    def _empty_response(self, message: str) -> Dict[str, Any]:
        return {
            "query": "",
            "answer": message,
            "sources": [],
            "fact_checks": [],
            "trending_context": [],
            "generated_at": datetime.now().isoformat(),
        }
