import logging
import json
import time
from datetime import datetime

from django.conf import settings
from rest_framework import status

from services.nlp_service import TextPreprocessor, URLExtractionService
from services.fact_checking_service import FactCheckingService
from services.fact_checking_service.unified_schema import datetime_to_iso
from services.scoring_service import ScoringService
from services.fact_checking_service.enhanced_verification_orchestrator import EnhancedVerificationOrchestrator

logger = logging.getLogger(__name__)

MAX_INPUT_LENGTH = 5000


class ClaimService:
    def __init__(self):
        self.text_preprocessor = TextPreprocessor()
        self.url_extractor = URLExtractionService()
        self.fact_checker = FactCheckingService()
        self.scorer = ScoringService()
        self.enhanced_orchestrator = EnhancedVerificationOrchestrator()

    def verify_claim(self, text, url, language):
        extracted_content = None
        if url:
            extracted_content = self._extract_content(url)
            text = extracted_content.content or text

        if not text:
            raise ValueError("No text content available for verification")

        if len(text) > MAX_INPUT_LENGTH:
            raise ValueError(f"Input too long. Maximum {MAX_INPUT_LENGTH} characters allowed.")

        nlp_analysis = self._preprocess_text(text, language)

        verification_result = self._fact_check(text, language)

        factly_score = self._calculate_score(verification_result, nlp_analysis, text)

        return {
            "text": text,
            "extracted_content": extracted_content,
            "nlp_analysis": nlp_analysis,
            "verification_result": verification_result,
            "factly_score": factly_score,
        }

    def _extract_content(self, url):
        try:
            extracted = self.url_extractor.extract_content(url)
            logger.info(f"Extracted content from URL: {len(extracted.content or '')} characters")
            return extracted
        except Exception as e:
            logger.exception("URL extraction failed")
            raise

    def _preprocess_text(self, text, language):
        try:
            analysis = self.text_preprocessor.preprocess(text, language=language)
            logger.info(f"NLP preprocessing completed: {analysis.get('language')}")
            return analysis
        except Exception as e:
            logger.warning(f"NLP preprocessing failed: {type(e).__name__}")
            return {"error": "NLP analysis unavailable"}

    def _fact_check(self, text, language):
        try:
            result = self.fact_checker.verify_claim(text, language)
            logger.info(f"Fact-checking completed: {len(result.claim_reviews)} reviews")
            return result
        except Exception as e:
            logger.exception("Fact-checking failed")
            raise

    def _calculate_score(self, verification_result, nlp_analysis, text):
        try:
            nlp_confidence = nlp_analysis.get("confidence") if isinstance(nlp_analysis, dict) else None
            score = self.scorer.calculate_factly_score(
                verification_result,
                nlp_confidence=nlp_confidence,
                text_content=text,
            )
            logger.info(f"Factly Score calculated: {score.factly_score}")
            return score
        except Exception as e:
            logger.exception("Scoring failed")
            raise

    def build_evidence_list(self, verification_result):
        evidence_items = []
        for review in verification_result.claim_reviews:
            evidence_items.append({
                "id": f"review_{len(evidence_items)}",
                "type": "fact_check",
                "claim": review.claim,
                "text": review.claim[:500] if len(review.claim) > 500 else review.claim,
                "full_text": review.claim,
                "rating": review.verdict,
                "confidence_score": review.confidence_score,
                "source": review.publisher.name if review.publisher else "Unknown",
                "source_credibility": review.publisher.credibility_score if review.publisher else 0.5,
                "url": review.url,
                "date": datetime_to_iso(review.review_date),
                "exact_date": review.review_date.isoformat() if review.review_date else None,
                "metadata": review.metadata,
            })

        for news in verification_result.related_news:
            evidence_items.append({
                "id": f"news_{len(evidence_items)}",
                "type": "news",
                "title": news.title,
                "text": news.title[:500] if len(news.title) > 500 else news.title,
                "full_text": news.title,
                "rating": news.sentiment or "neutral",
                "confidence_score": news.relevance_score,
                "source": news.source,
                "source_credibility": news.relevance_score,
                "url": news.url,
                "date": datetime_to_iso(news.publish_date),
                "exact_date": news.publish_date.isoformat() if news.publish_date else None,
                "metadata": news.metadata,
            })

        return evidence_items

    def build_sources_list(self, verification_result):
        sources_list = []
        for review in verification_result.claim_reviews:
            if review.publisher:
                sources_list.append({
                    "name": review.publisher.name,
                    "url": review.url,
                    "credibility": review.publisher.credibility_score,
                    "exact_credibility_score": review.publisher.credibility_score,
                    "review_count": review.publisher.review_count,
                    "categories": review.publisher.categories,
                })

        for news in verification_result.related_news:
            source_name = news.source
            if not any(s["name"] == source_name for s in sources_list):
                sources_list.append({
                    "name": source_name,
                    "url": news.url,
                    "credibility": "High" if news.relevance_score >= 0.8 else ("Medium" if news.relevance_score >= 0.5 else "Low"),
                    "exact_credibility_score": news.relevance_score,
                    "relevance_score": news.relevance_score,
                    "sentiment": news.sentiment,
                })

        return sources_list

    def log_verification(self, user, text, verification_result, factly_score):
        try:
            from .models import VerificationLog
            VerificationLog.objects.create(
                user=user if user.is_authenticated else None,
                claim=text[:500],
                overall_confidence=verification_result.overall_confidence,
                factly_score=factly_score.factly_score,
                classification=factly_score.classification,
                api_sources=json.dumps(verification_result.api_sources),
            )
        except Exception as log_err:
            logger.warning(f"Failed to log verification: {log_err}")


class EnhancedVerificationService:
    def __init__(self):
        self.orchestrator = EnhancedVerificationOrchestrator()

    def verify(self, text, url, language):
        from services.nlp_service import URLExtractionService

        if url:
            extractor = URLExtractionService()
            try:
                extracted = extractor.extract_content(url)
                text = extracted.content or text
                logger.info(f"Extracted content from URL: {len(text)} characters")
            except Exception as e:
                logger.exception("URL extraction failed")
                raise

        if not text:
            raise ValueError("No text content available for verification")

        result = self.orchestrator.verify(text, language=language)
        return result

    def build_response_data(self, result, query_text):
        return {
            "query": query_text,
            "factly_score": result.factly_score,
            "classification": result.factly_score_result.classification if result.factly_score_result else "Unknown",
            "confidence_level": result.verification_trace.confidence_level if result.verification_trace else "Unknown",
            "recommended_verdict": result.verification_trace.recommended_verdict if result.verification_trace else "Unable to determine",
            "verification_summary": {
                "headline": result.verification_summary.headline if result.verification_summary else "Verification Failed",
                "overall_assessment": result.verification_summary.overall_assessment if result.verification_summary else "Unable to verify",
                "verification_methodology": result.verification_summary.verification_methodology_explanation if result.verification_summary else "",
                "key_findings": result.verification_summary.key_findings if result.verification_summary else [],
                "verified_data_points": result.verification_summary.verified_data_points if result.verification_summary else [],
                "unverified_data_points": result.verification_summary.unverified_data_points if result.verification_summary else [],
                "discrepancies_and_caveats": result.verification_summary.discrepancies_and_caveats if result.verification_summary else [],
                "sources_consulted": result.verification_summary.sources_consulted if result.verification_summary else [],
                "source_diversity_assessment": result.verification_summary.source_diversity_assessment if result.verification_summary else "Unknown",
                "confidence_statement": result.verification_summary.confidence_statement if result.verification_summary else "",
                "recommendations": result.verification_summary.recommendations if result.verification_summary else [],
                "verification_limitations": result.verification_summary.verification_limitations if result.verification_summary else [],
            },
            "verification_trace": self._build_trace(result),
            "evidence": self._build_evidence_list(result),
            "direct_verification": self._build_direct_verification(result),
            "cross_source_analysis": self._build_cross_source_analysis(result),
            "data_freshness": self._build_data_freshness(result),
            "api_sources_used": result.api_sources,
            "processing_time_ms": result.processing_time_ms,
            "timestamp": result.timestamp.isoformat(),
        }

    def _build_trace(self, result):
        if not result.verification_trace:
            return {}
        return {
            "verification_steps": [
                {
                    "step_number": step.step_number,
                    "step_name": step.step_name,
                    "description": step.description,
                    "status": step.status,
                    "result": step.result,
                    "timestamp": step.timestamp.isoformat() if step.timestamp else None,
                    "duration_ms": step.duration_ms,
                }
                for step in (result.verification_trace.verification_steps or [])
            ],
            "sources_consulted": result.verification_trace.sources_consulted or [],
            "primary_sources_used": result.verification_trace.primary_sources_used or [],
            "secondary_sources_used": result.verification_trace.secondary_sources_used or [],
            "data_points_verified": result.verification_trace.data_points_verified or [],
            "data_points_unverified": result.verification_trace.data_points_unverified or [],
            "discrepancies_found": result.verification_trace.discrepancies_found or [],
            "confidence_level": result.verification_trace.confidence_level or "Unknown",
            "recommended_verdict": result.verification_trace.recommended_verdict or "Unknown",
            "processing_time_ms": result.verification_trace.processing_time_ms or 0,
        }

    def _build_evidence_list(self, result):
        evidence_items = []
        if result.evidence_collection and result.evidence_collection.evidence_items:
            for item in result.evidence_collection.evidence_items:
                evidence_items.append({
                    "id": f"evidence_{len(evidence_items)}",
                    "type": item.source_type,
                    "title": item.title,
                    "content": item.content,
                    "source": item.source,
                    "source_credibility": item.credibility_score,
                    "relevance_score": item.relevance_score,
                    "verdict": item.verdict,
                    "url": item.url,
                    "date": item.published_date.isoformat() if item.published_date else None,
                    "metadata": item.metadata,
                })
        return evidence_items

    def _build_direct_verification(self, result):
        if not result.direct_verification_report:
            return None
        d = result.direct_verification_report
        return {
            "sources_consulted": d.sources_consulted or 0,
            "primary_sources_found": d.primary_sources_found or 0,
            "secondary_sources_found": d.secondary_sources_found or 0,
            "overall_verification_score": d.overall_verification_score or 0,
            "verified_data_points": d.verified_data_points or [],
            "unverified_data_points": d.unverified_data_points or [],
            "discrepancies": d.discrepancies_found or [],
            "verification_steps": d.verification_steps or [],
        }

    def _build_cross_source_analysis(self, result):
        if not result.cross_source_analysis:
            return None
        c = result.cross_source_analysis
        return {
            "consensus_level": c.consensus_level.value if c.consensus_level else "unknown",
            "evidence_strength": c.evidence_strength.value if c.evidence_strength else "unknown",
            "agreement_score": c.agreement_score or 0,
            "confidence_score": c.confidence_score or 0,
            "key_findings": c.key_findings or [],
            "contradictions": c.contradictions or [],
            "recommended_verdict": c.recommended_verdict or "Unknown",
            "uncertainty_factors": c.uncertainty_factors or [],
        }

    def _build_data_freshness(self, result):
        return {
            "verification_timestamp": result.timestamp.isoformat(),
            "most_recent_evidence_age_hours": self._calculate_evidence_age(result),
            "realtime_sources_used": any(
                source in result.api_sources_used
                for source in ["Real-Time News", "NewsAPI", "Bing News"]
            ),
            "cache_status": "fresh" if self._is_data_fresh(result) else "stale",
            "data_age_warning": self._get_data_age_warning(result),
        }

    def _calculate_evidence_age(self, result):
        if not result.evidence_collection or not result.evidence_collection.evidence_items:
            return None
        most_recent = max(
            (item for item in result.evidence_collection.evidence_items if item.published_date),
            key=lambda x: x.published_date,
            default=None,
        )
        if most_recent and most_recent.published_date:
            age = datetime.now() - most_recent.published_date.replace(tzinfo=None)
            return age.total_seconds() / 3600
        return None

    def _is_data_fresh(self, result):
        age = self._calculate_evidence_age(result)
        if age is None:
            return False
        return age <= 24

    def _get_data_age_warning(self, result):
        age = self._calculate_evidence_age(result)
        if age is None:
            return "No evidence with timestamps available for freshness assessment"
        elif age <= 1:
            return "Data is very recent (less than 1 hour old)"
        elif age <= 6:
            return "Data is recent (less than 6 hours old)"
        elif age <= 24:
            return "Data is moderately recent (less than 24 hours old)"
        elif age <= 72:
            return "Data is somewhat stale (1-3 days old) - consider verifying with current sources"
        else:
            return "Data is stale (more than 3 days old) - strongly recommend fresh verification"
