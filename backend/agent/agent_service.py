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
import re
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
            from services.scoring_service import ScoringService
            self._scoring_service = ScoringService()
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

    def _item_to_dict(self, item) -> Dict[str, Any]:
        """Convert a RealTimeNewsItem dataclass (or dict) to a plain dict."""
        if hasattr(item, '__dataclass_fields__'):
            return {
                "title": item.title,
                "content": item.content,
                "url": item.url,
                "published_date": item.published_date,
                "source": item.source,
                "source_name": item.source,
                "freshness_score": item.freshness_score,
                "relevance_score": item.relevance_score,
                "credibility_score": item.credibility_score,
                "metadata": item.metadata,
            }
        return dict(item)

    def _fetch_news_for_query(self, query: str) -> List[Dict[str, Any]]:
        """Search news from all available sources."""
        items = []
        try:
            results = self.realtime_news.get_real_time_news(
                query, max_results=15, max_age_hours=72
            )
            items.extend(self._item_to_dict(r) for r in results)
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
                items.extend(self._item_to_dict(r) for r in results)
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
                    items.extend(
                        self._fetch_rss_no_filter(url, max_results=5)
                    )
                except Exception:
                    continue
            return items
        except Exception:
            return []

    def _fetch_rss_no_filter(self, feed_url: str, max_results: int) -> List[Dict[str, Any]]:
        """Fetch RSS entries without requiring an exact query match."""
        import feedparser
        results = []
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:max_results]:
                published_date = self._parse_rss_date(entry)
                hours_old = (datetime.now() - published_date).total_seconds() / 3600
                freshness_score = max(0, 1 - (hours_old / 24))
                results.append({
                    "title": entry.title,
                    "content": getattr(entry, 'description', ''),
                    "url": entry.link,
                    "published_date": published_date,
                    "source": feed.feed.title if hasattr(feed.feed, 'title') else 'RSS',
                    "source_name": feed.feed.title if hasattr(feed.feed, 'title') else 'RSS',
                    "freshness_score": freshness_score,
                    "relevance_score": 0.7,
                    "credibility_score": 0.8,
                    "metadata": {"source_type": "rss_fallback"},
                })
        except Exception as e:
            logger.error(f"RSS feed error: {e}")
        return results

    def _parse_rss_date(self, entry) -> datetime:
        """Parse RSS date formats."""
        date_str = getattr(entry, 'published_parsed', None)
        if date_str:
            try:
                return datetime(*date_str[:6])
            except Exception:
                pass
        return datetime.now() - timedelta(hours=2)

    # ------------------------------------------------------------------
    # Internal: Scoring / Fact-Checking
    # ------------------------------------------------------------------

    def _score_item(self, item) -> Dict[str, Any]:
        """Run the scoring engine on a news item."""
        # Handle both dict items and RealTimeNewsItem dataclass objects
        if hasattr(item, '__dataclass_fields__'):
            title = item.title or ""
            content = item.content or ""
            source = item.source or ""
            published_date = getattr(item, 'published_date', datetime.now())
            item_url = getattr(item, 'url', '')
            relevance_score = getattr(item, 'relevance_score', 0.5)
        else:
            title = item.get("title", "") or ""
            content = item.get("content", "") or item.get("summary", "") or ""
            source = item.get("source_name") or item.get("source", "") or ""
            published_date = item.get("published_date", datetime.now())
            item_url = item.get("url", '')
            relevance_score = item.get("relevance_score", 0.5)

        text = f"{title}. {content}"

        try:
            from services.fact_checking_service.unified_schema import (
                VerificationResult, RelatedNews
            )

            related_news = [RelatedNews(
                title=title[:500],
                url=item_url,
                source=source[:200],
                publish_date=published_date if isinstance(published_date, datetime) else datetime.now(),
                relevance_score=relevance_score,
                sentiment=None,
            )]

            verification_result = VerificationResult(
                claim=title[:1000],
                claim_reviews=[],
                related_news=related_news,
                source_reliability=None,
                overall_confidence=0.5,
                api_sources=["agent"],
                metadata={}
            )

            result = self.scoring_service.calculate_factly_score(
                verification_result=verification_result,
                text_content=text
            )

            # Extract component scores
            bias_score = 50
            sensationalism_score = 50
            for comp in getattr(result, 'components', []):
                name = getattr(comp, 'name', '')
                if 'bias' in name.lower():
                    bias_score = int((1.0 - getattr(comp, 'score', 0.5)) * 100)
                elif 'sensationalism' in name.lower() or 'content' in name.lower():
                    sensationalism_score = int((1.0 - getattr(comp, 'score', 0.5)) * 100)

            return {
                "credibility_score": getattr(result, 'factly_score', 50),
                "verdict": self._score_to_verdict(getattr(result, 'factly_score', 50)),
                "bias_score": bias_score,
                "sensationalism_score": sensationalism_score,
                "importance_score": getattr(result, 'factly_score', 50),
                "confidence": getattr(result, 'confidence_level', 'low').lower(),
            }
        except Exception as e:
            logger.warning(f"Scoring service failed for '{title[:50]}': {e}")
            return self._fallback_score(text, source)

    def _score_to_verdict(self, score: int) -> str:
        """Map a numeric score to a verdict string."""
        if score >= 70:
            return "true"
        elif score >= 50:
            return "mostly_true"
        elif score >= 35:
            return "unverifiable"
        elif score >= 20:
            return "misleading"
        return "false"

    def _fallback_score(self, text: str, source: str) -> Dict[str, Any]:
        """Simple fallback scoring when the scoring service is unavailable."""
        text_lower = text.lower()

        # Bias indicators
        bias_patterns = [
            r'\b(conspiracy|hoax|fake news|propaganda)\b',
            r'\b(deep state|illuminati|new world order)\b',
            r'\b(crisis actor|false flag|inside job)\b',
        ]
        bias_count = sum(len(re.findall(p, text_lower)) for p in bias_patterns)

        # Sensationalism indicators
        sensational_words = [
            'shocking', 'outrageous', 'unbelievable', 'scandalous',
            'devastating', 'catastrophic', 'terrifying', 'mind-blowing',
            'you won\'t believe', 'this changes everything',
        ]
        sens_count = sum(1 for w in sensational_words if w in text_lower)
        sens_count += text.count('!') // 3

        bias_score = min(100, bias_count * 25)
        sensationalism_score = min(100, sens_count * 20)

        # Base credibility on source and text quality
        credible_sources = ['reuters', 'ap', 'bbc', 'guardian', 'nytimes',
                           'washington post', 'npr', 'bloomberg', 'wsj']
        source_lower = source.lower()
        source_bonus = 20 if any(s in source_lower for s in credible_sources) else 0
        if source_lower in ('twitter/x', 'twitter', 'facebook', 'reddit'):
            source_bonus = -20

        credibility_score = max(0, min(100, 60 + source_bonus - bias_score // 2 - sensationalism_score // 2))

        if credibility_score >= 70:
            verdict = "true"
        elif credibility_score >= 50:
            verdict = "mostly_true"
        elif credibility_score >= 35:
            verdict = "unverifiable"
        elif credibility_score >= 20:
            verdict = "misleading"
        else:
            verdict = "false"

        if credibility_score >= 70 and bias_score < 30:
            confidence = "high"
        elif credibility_score >= 40:
            confidence = "medium"
        else:
            confidence = "low"

        return {
            "credibility_score": credibility_score,
            "verdict": verdict,
            "bias_score": bias_score,
            "sensationalism_score": sensationalism_score,
            "importance_score": credibility_score,
            "confidence": confidence,
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
