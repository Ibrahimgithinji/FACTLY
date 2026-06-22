"""Comprehensive tests for the Factly Score™ scoring engine."""

import sys
import os
from datetime import datetime
from unittest import TestCase

backend_dir = os.path.join(os.path.dirname(__file__), '..', '..')
sys.path.insert(0, backend_dir)

# Import directly from source modules to bypass circular imports in __init__.py
from services.scoring_service.scoring_service import (
    ScoringService,
    FactlyScoreResult,
    ComponentScore,
)
from services.fact_checking_service.unified_schema import (
    VerificationResult,
    ClaimReview,
    PublisherCredibility,
    RelatedNews,
    SourceReliability,
)


class TestVerdictToScore(TestCase):
    """Verify verdict-to-score mappings cover all known verdict types."""

    def setUp(self):
        self.service = ScoringService()

    def test_exact_verdict_matches(self):
        cases = [
            ('true', 1.0),
            ('mostly true', 0.85),
            ('half true', 0.60),
            ('mixed', 0.50),
            ('mostly false', 0.25),
            ('false', 0.10),
            ('misleading', 0.30),
            ('unverified', 0.50),
            ('satire', 0.15),
            ('correct', 1.0),
            ('incorrect', 0.10),
            ('verified', 0.95),
            ('partially true', 0.55),
        ]
        for verdict, expected in cases:
            with self.subTest(verdict=verdict):
                result = self.service._map_verdict_to_score(verdict)
                self.assertEqual(result, expected,
                                 f"Expected score {expected} for verdict '{verdict}', got {result}")

    def test_verdict_substring_matches_longest_key(self):
        cases = [
            ('mostly true', 0.85),
            ('half true', 0.60),
            ('mostly false', 0.25),
            ('partially true', 0.55),
        ]
        for verdict, expected in cases:
            with self.subTest(verdict=verdict):
                result = self.service._map_verdict_to_score(verdict)
                self.assertEqual(result, expected,
                                 f"Expected score {expected} for verdict '{verdict}', got {result}")

    def test_verdict_partial_match_prefers_most_specific(self):
        result = self.service._map_verdict_to_score('mostly true')
        self.assertEqual(result, 0.85, "'mostly true' should return 0.85 not 1.0")

    def test_empty_verdict_defaults_to_neutral(self):
        result = self.service._map_verdict_to_score('')
        self.assertEqual(result, 0.5)

    def test_none_verdict_defaults_to_neutral(self):
        result = self.service._map_verdict_to_score(None)
        self.assertEqual(result, 0.5)

    def test_unknown_verdict_defaults_to_neutral(self):
        result = self.service._map_verdict_to_score('something completely different')
        self.assertEqual(result, 0.5)

    def test_verdict_case_insensitive(self):
        result = self.service._map_verdict_to_score('TRUE')
        self.assertEqual(result, 1.0)
        result = self.service._map_verdict_to_score('False')
        self.assertEqual(result, 0.10)

    def test_verdict_whitespace_handling(self):
        result = self.service._map_verdict_to_score('  true  ')
        self.assertEqual(result, 1.0)


class TestClassification(TestCase):
    """Verify score-to-classification boundaries."""

    def setUp(self):
        self.service = ScoringService()

    def test_likely_fake_range(self):
        for score in [0, 15, 35]:
            with self.subTest(score=score):
                result = self.service._classify_score(score)
                self.assertEqual(result, 'Likely Fake')

    def test_uncertain_range(self):
        for score in [36, 50, 65]:
            with self.subTest(score=score):
                result = self.service._classify_score(score)
                self.assertEqual(result, 'Uncertain')

    def test_likely_authentic_range(self):
        for score in [66, 85, 100]:
            with self.subTest(score=score):
                result = self.service._classify_score(score)
                self.assertEqual(result, 'Likely Authentic')

    def test_boundary_values(self):
        self.assertEqual(self.service._classify_score(35), 'Likely Fake')
        self.assertEqual(self.service._classify_score(36), 'Uncertain')
        self.assertEqual(self.service._classify_score(65), 'Uncertain')
        self.assertEqual(self.service._classify_score(66), 'Likely Authentic')

    def test_out_of_range_above_clamps_to_max(self):
        result = self.service._classify_score(150)
        self.assertEqual(result, 'Likely Authentic')

    def test_out_of_range_below_returns_likely_fake(self):
        result = self.service._classify_score(-10)
        self.assertEqual(result, 'Likely Fake')


class TestBiasIndicators(TestCase):
    """Verify bias detection catches known patterns."""

    def setUp(self):
        self.service = ScoringService()

    def test_no_bias_returns_zero(self):
        text = "The study found that 75% of participants responded positively."
        count = self.service._analyze_bias_indicators(text)
        self.assertEqual(count, 0)

    def test_conspiracy_keywords_detected(self):
        text = "This is a conspiracy by the mainstream media to spread propaganda."
        count = self.service._analyze_bias_indicators(text)
        self.assertGreaterEqual(count, 2)

    def test_deep_state_keyword_detected(self):
        text = "The deep state is behind this new world order."
        count = self.service._analyze_bias_indicators(text)
        self.assertGreaterEqual(count, 2)

    def test_multiple_bias_indicators_counted(self):
        text = "The mainstream media calls it a hoax, but it's a conspiracy by the deep state. Wake up sheeple!"
        count = self.service._analyze_bias_indicators(text)
        self.assertGreaterEqual(count, 4)

    def test_false_flag_detected(self):
        text = "This was a false flag operation with crisis actors."
        count = self.service._analyze_bias_indicators(text)
        self.assertGreaterEqual(count, 1)


class TestSensationalism(TestCase):
    """Verify sensationalism detection flags clickbait patterns."""

    def setUp(self):
        self.service = ScoringService()

    def test_neutral_text_returns_low_count(self):
        text = "According to the report, inflation rose by 2.3% this quarter."
        count = self.service._analyze_sensationalism(text)
        self.assertEqual(count, 0)

    def test_sensational_words_detected(self):
        text = "SHOCKING! This devastating discovery changes everything."
        count = self.service._analyze_sensationalism(text)
        self.assertGreaterEqual(count, 2)

    def test_excessive_exclamation_marks_flagged(self):
        text = "This is incredible!!! You won't believe what happened next!!!"
        count = self.service._analyze_sensationalism(text)
        self.assertGreaterEqual(count, 2)

    def test_clickbait_phrases_detected(self):
        text = "Doctors hate this one secret trick. You won't believe what happens next!"
        count = self.service._analyze_sensationalism(text)
        self.assertGreaterEqual(count, 3)


class TestCitationAnalysis(TestCase):
    """Verify citation quality scoring."""

    def setUp(self):
        self.service = ScoringService()

    def test_no_citations_returns_base_score(self):
        text = "Some random statement without any attribution."
        score = self.service._analyze_citations(text)
        self.assertEqual(score, 0.5)

    def test_named_source_increases_score(self):
        text = "According to Dr. Smith, the treatment shows promise."
        score = self.service._analyze_citations(text)
        self.assertGreater(score, 0.5)

    def test_news_agency_mention_increases_score(self):
        text = "Reuters reported on the development yesterday."
        score = self.service._analyze_citations(text)
        self.assertGreater(score, 0.5)

    def test_date_and_statistics_increase_score(self):
        text = "According to the report, 45% of respondents agreed. The study was published on January 15, 2024."
        score = self.service._analyze_citations(text)
        self.assertGreater(score, 0.7)

    def test_score_capped_at_one(self):
        text = ("According to Dr. Smith, Reuters reported that 75% of patients improved "
                "by March 2024. The BBC confirmed the findings.")
        score = self.service._analyze_citations(text)
        self.assertLessEqual(score, 1.0)


class TestFactCheckConsensus(TestCase):
    """Verify fact-check consensus calculation."""

    def setUp(self):
        self.service = ScoringService()

    def _make_publisher(self, name='Publisher A', credibility=0.7):
        return PublisherCredibility(
            name=name,
            credibility_score=credibility,
            review_count=10,
            average_rating=0.75,
            categories=['news'],
            metadata={}
        )

    def _make_review(self, claim='Test claim', verdict='true', confidence=0.8,
                     publisher_name='Publisher A', publisher_credibility=0.7):
        return ClaimReview(
            claim=claim,
            verdict=verdict,
            confidence_score=confidence,
            publisher=self._make_publisher(publisher_name, publisher_credibility),
            review_date=datetime.now(),
            url=None,
            language='en',
        )

    def _make_result(self, claim='Test claim', reviews=None, news=None,
                     source_reliability=None, metadata=None):
        return VerificationResult(
            claim=claim,
            claim_reviews=reviews or [],
            related_news=news or [],
            source_reliability=source_reliability,
            api_sources=[],
            metadata=metadata or {},
        )

    def test_no_reviews_returns_neutral(self):
        result = self._make_result()
        component = self.service._calculate_fact_check_consensus(result)
        self.assertEqual(component.score, 0.5)
        self.assertEqual(component.weight, 0.45)
        self.assertIn('No fact-check reviews found', component.justification)

    def test_single_true_review(self):
        result = self._make_result(reviews=[self._make_review(verdict='true')])
        component = self.service._calculate_fact_check_consensus(result)
        self.assertGreater(component.score, 0.7)

    def test_single_false_review(self):
        result = self._make_result(reviews=[self._make_review(verdict='false')])
        component = self.service._calculate_fact_check_consensus(result)
        self.assertLess(component.score, 0.3)

    def test_multiple_agreeing_reviews(self):
        reviews = [
            self._make_review(verdict='true', publisher_name='Publisher A'),
            self._make_review(verdict='true', publisher_name='Publisher B'),
            self._make_review(verdict='true', publisher_name='Publisher C'),
        ]
        result = self._make_result(reviews=reviews)
        component = self.service._calculate_fact_check_consensus(result)
        self.assertGreater(component.score, 0.7)

    def test_mixed_verdicts_produce_middle_score(self):
        reviews = [
            self._make_review(verdict='true', publisher_name='Publisher A'),
            self._make_review(verdict='false', publisher_name='Publisher B'),
            self._make_review(verdict='mixed', publisher_name='Publisher C'),
        ]
        result = self._make_result(reviews=reviews)
        component = self.service._calculate_fact_check_consensus(result)
        self.assertGreater(component.score, 0.3)
        self.assertLess(component.score, 0.7)

    def test_publisher_credibility_affects_weight_with_multiple_reviews(self):
        credible_reviews = [
            self._make_review(verdict='true', publisher_name='High Cred A',
                              publisher_credibility=0.9, confidence=0.9),
            self._make_review(verdict='true', publisher_name='High Cred B',
                              publisher_credibility=0.9, confidence=0.9),
            self._make_review(verdict='false', publisher_name='Low Cred',
                              publisher_credibility=0.2, confidence=0.3),
        ]
        equal_weight_reviews = [
            self._make_review(verdict='true', publisher_name='A', publisher_credibility=0.7),
            self._make_review(verdict='true', publisher_name='B', publisher_credibility=0.7),
            self._make_review(verdict='false', publisher_name='C', publisher_credibility=0.7),
        ]
        credible_result = self._make_result(reviews=credible_reviews)
        equal_result = self._make_result(reviews=equal_weight_reviews)
        credible_comp = self.service._calculate_fact_check_consensus(credible_result)
        equal_comp = self.service._calculate_fact_check_consensus(equal_result)
        self.assertGreater(credible_comp.score, equal_comp.score)


class TestSourceCredibility(TestCase):
    """Verify source credibility calculation."""

    def setUp(self):
        self.service = ScoringService()

    def _make_result(self, source_reliability=None, news=None):
        return VerificationResult(
            claim='Test claim',
            claim_reviews=[],
            related_news=news or [],
            source_reliability=source_reliability,
            api_sources=[],
        )

    def test_no_source_data_returns_neutral(self):
        result = self._make_result()
        component = self.service._calculate_source_credibility(result)
        self.assertEqual(component.score, 0.5)

    def test_credible_source_increases_score(self):
        reliability = SourceReliability(
            source_name='Reuters',
            reliability_score=0.9,
            bias_rating='center',
            factual_reporting=0.85,
        )
        result = self._make_result(source_reliability=reliability)
        component = self.service._calculate_source_credibility(result)
        self.assertGreater(component.score, 0.5)

    def test_unreliable_source_lowers_score(self):
        reliability = SourceReliability(
            source_name='ConspiracySite',
            reliability_score=0.1,
            bias_rating='extreme',
            factual_reporting=0.05,
        )
        result = self._make_result(source_reliability=reliability)
        component = self.service._calculate_source_credibility(result)
        self.assertLess(component.score, 0.5)

    def test_related_news_contributes_to_score(self):
        news = [
            RelatedNews(
                title='Article 1', url='http://example.com', source='Source A',
                publish_date=datetime.now(), relevance_score=0.9, sentiment=None,
            ),
        ]
        result = self._make_result(news=news)
        component = self.service._calculate_source_credibility(result)
        self.assertGreater(component.score, 0.5)


class TestEvidenceQuality(TestCase):
    """Verify evidence quality scoring."""

    def setUp(self):
        self.service = ScoringService()

    def _make_publisher(self, name='Pub'):
        return PublisherCredibility(name=name, credibility_score=0.7,
                                    review_count=5, average_rating=0.7,
                                    categories=['news'], metadata={})

    def _make_review(self, verdict='true'):
        return ClaimReview(claim='Test', verdict=verdict, confidence_score=0.8,
                           publisher=self._make_publisher(),
                           review_date=datetime.now(), url=None, language='en')

    def _make_news(self, relevance=0.5):
        return RelatedNews(title='News', url='http://x.com', source='Src',
                           publish_date=datetime.now(), relevance_score=relevance,
                           sentiment=None)

    def test_no_evidence_returns_low_score(self):
        result = VerificationResult(claim='Test', claim_reviews=[], related_news=[])
        component = self.service._calculate_evidence_quality(result)
        self.assertEqual(component.score, 0.3)

    def test_single_review_increases_score(self):
        result = VerificationResult(claim='Test', claim_reviews=[self._make_review()],
                                    related_news=[])
        component = self.service._calculate_evidence_quality(result)
        self.assertGreater(component.score, 0.2)
        self.assertLess(component.score, 0.5)

    def test_multiple_reviews_max_out_evidence_score(self):
        reviews = [self._make_review() for _ in range(5)]
        result = VerificationResult(claim='Test', claim_reviews=reviews, related_news=[])
        component = self.service._calculate_evidence_quality(result)
        self.assertGreater(component.score, 0.6)

    def test_news_articles_contribute_to_score(self):
        news = [self._make_news() for _ in range(5)]
        result = VerificationResult(claim='Test', claim_reviews=[], related_news=news)
        component = self.service._calculate_evidence_quality(result)
        self.assertGreaterEqual(component.score, 0.3)

    def test_both_reviews_and_news_combined(self):
        reviews = [self._make_review() for _ in range(3)]
        news = [self._make_news() for _ in range(5)]
        result = VerificationResult(claim='Test', claim_reviews=reviews, related_news=news)
        component = self.service._calculate_evidence_quality(result)
        self.assertGreater(component.score, 0.5)


class TestConfidenceLevel(TestCase):
    """Verify confidence level calculation."""

    def setUp(self):
        self.service = ScoringService()

    def test_consistent_components_yield_high_confidence(self):
        components = [
            ComponentScore(name='A', score=0.8, weight=0.45, weighted_score=0.36,
                           justification='', evidence=[]),
            ComponentScore(name='B', score=0.8, weight=0.25, weighted_score=0.20,
                           justification='', evidence=[]),
        ]
        result = VerificationResult(claim='Test', claim_reviews=[], related_news=[])
        level = self.service._calculate_confidence_level(components, result)
        self.assertEqual(level, 'High')

    def test_widely_varying_scores_yield_medium_or_low_confidence(self):
        components = [
            ComponentScore(name='A', score=0.1, weight=0.45, weighted_score=0.045,
                           justification='', evidence=[]),
            ComponentScore(name='B', score=0.9, weight=0.25, weighted_score=0.225,
                           justification='', evidence=[]),
        ]
        result = VerificationResult(claim='Test', claim_reviews=[], related_news=[])
        level = self.service._calculate_confidence_level(components, result)
        self.assertIn(level, ['Medium', 'Low'])

    def test_multiple_claim_reviews_boost_confidence(self):
        components = [
            ComponentScore(name='A', score=0.8, weight=0.45, weighted_score=0.36,
                           justification='', evidence=[]),
            ComponentScore(name='B', score=0.5, weight=0.25, weighted_score=0.125,
                           justification='', evidence=[]),
        ]
        publisher = PublisherCredibility(name='Pub', credibility_score=0.7,
                                         review_count=10, average_rating=0.7,
                                         categories=['news'], metadata={})
        reviews = [
            ClaimReview(claim='Test', verdict='true', confidence_score=0.9,
                        publisher=publisher, review_date=datetime.now(), url=None, language='en'),
            ClaimReview(claim='Test', verdict='true', confidence_score=0.85,
                        publisher=publisher, review_date=datetime.now(), url=None, language='en'),
            ClaimReview(claim='Test', verdict='true', confidence_score=0.8,
                        publisher=publisher, review_date=datetime.now(), url=None, language='en'),
        ]
        result = VerificationResult(claim='Test', claim_reviews=reviews, related_news=[])
        level = self.service._calculate_confidence_level(components, result)
        self.assertEqual(level, 'High')


class TestFullScoreCalculation(TestCase):
    """End-to-end tests for the complete Factly Score calculation."""

    def setUp(self):
        self.service = ScoringService()

    def _make_publisher(self, name='Pub', credibility=0.7):
        return PublisherCredibility(name=name, credibility_score=credibility,
                                    review_count=5, average_rating=0.7,
                                    categories=['news'], metadata={})

    def _make_review(self, verdict='true', confidence=0.8, publisher_name='Pub'):
        return ClaimReview(claim='Test', verdict=verdict, confidence_score=confidence,
                           publisher=self._make_publisher(publisher_name),
                           review_date=datetime.now(), url=None, language='en')

    def test_true_claim_with_evidence_returns_high_score(self):
        reviews = [
            self._make_review(verdict='true', publisher_name='Reuters'),
            self._make_review(verdict='verified', publisher_name='AP'),
            self._make_review(verdict='mostly true', publisher_name='BBC'),
        ]
        news_items = [RelatedNews(title=f'News {i}', url=f'http://x.com/{i}', source='Src',
                                   publish_date=datetime.now(), relevance_score=0.8, sentiment=None)
                       for i in range(3)]
        reliability = SourceReliability(source_name='Reuters', reliability_score=0.9,
                                        bias_rating='center', factual_reporting=0.85)

        result = VerificationResult(
            claim='Climate change is primarily caused by human activity.',
            claim_reviews=reviews,
            related_news=news_items,
            source_reliability=reliability,
            api_sources=['Google Fact Check'],
        )

        score_result = self.service.calculate_factly_score(
            verification_result=result,
            text_content='According to NASA and NOAA data, 97% of climate scientists agree.'
        )

        self.assertGreaterEqual(score_result.factly_score, 60)
        self.assertIn(score_result.classification, ['Likely Authentic', 'Uncertain'])
        self.assertEqual(len(score_result.components), 4)
        self.assertGreater(len(score_result.justifications), 0)
        self.assertGreater(score_result.processing_time, 0)

    def test_false_claim_with_evidence_returns_low_score(self):
        reviews = [
            self._make_review(verdict='false', publisher_name='Reuters'),
            self._make_review(verdict='incorrect', publisher_name='AP'),
            self._make_review(verdict='misleading', publisher_name='BBC'),
        ]
        result = VerificationResult(
            claim='The Earth is flat according to scientific studies.',
            claim_reviews=reviews,
            related_news=[],
            api_sources=['Google Fact Check'],
        )

        score_result = self.service.calculate_factly_score(
            verification_result=result,
            text_content='SHOCKING! What NASA doesnt want you to know! WAKE UP SHEEPLE!'
        )

        self.assertLessEqual(score_result.factly_score, 40)
        self.assertIn(score_result.classification, ['Likely Fake', 'Uncertain'])

    def test_no_evidence_returns_mid_low_score(self):
        result = VerificationResult(
            claim='Something completely unknown to science.',
            claim_reviews=[],
            related_news=[],
            api_sources=[],
        )

        score_result = self.service.calculate_factly_score(
            verification_result=result,
            text_content='Something completely unknown to science.'
        )

        self.assertLess(score_result.factly_score, 60)
        self.assertIsNotNone(score_result.timestamp)
        self.assertIsNotNone(score_result.metadata)
        self.assertIn('No fact-check reviews found', score_result.justifications[1])
        self.assertIn('Limited evidence', score_result.justifications[-1])

    def test_heuristic_match_bypasses_normal_scoring(self):
        result = VerificationResult(
            claim='COVID-19 vaccines contain microchips.',
            claim_reviews=[],
            related_news=[],
            api_sources=[],
            metadata={
                'heuristic_match': {
                    'matched': True,
                    'score': 5,
                    'classification': 'Likely Fake',
                    'confidence': 'High',
                    'verdict': 'This is a known misinformation pattern.',
                    'evidence': ['Microchip conspiracy theory'],
                    'claim_type': 'health_misinformation',
                    'source_note': 'Known misinformation pattern'
                }
            }
        )

        score_result = self.service.calculate_factly_score(
            verification_result=result,
            text_content='COVID-19 vaccines contain microchips for tracking.'
        )

        self.assertEqual(score_result.factly_score, 5)
        self.assertEqual(score_result.classification, 'Likely Fake')
        self.assertEqual(score_result.confidence_level, 'High')
        self.assertEqual(score_result.metadata.get('heuristic_used'), True)

    def test_content_analysis_penalizes_biased_language(self):
        publisher = self._make_publisher()
        review = self._make_review(verdict='half true', confidence=0.5)

        result = VerificationResult(
            claim='Test claim',
            claim_reviews=[review],
            related_news=[],
            api_sources=[],
        )

        neutral_score = self.service.calculate_factly_score(
            verification_result=result,
            text_content='According to the report, the results were mixed.'
        )

        biased_score = self.service.calculate_factly_score(
            verification_result=result,
            text_content='This is a conspiracy by the mainstream media! '
                         'WAKE UP SHEEPLE! They are hiding the TRUTH! '
                         'SHOCKING! UNBELIEVABLE!'
        )

        self.assertGreater(neutral_score.factly_score, biased_score.factly_score,
                           "Biased content should produce a lower score")

    def test_score_result_includes_all_expected_fields(self):
        result = VerificationResult(
            claim='Test claim',
            claim_reviews=[self._make_review(verdict='true')],
            related_news=[],
            api_sources=['Google Fact Check'],
        )

        score_result = self.service.calculate_factly_score(
            verification_result=result,
            text_content='Test claim content.'
        )

        self.assertIsInstance(score_result.factly_score, int)
        self.assertGreaterEqual(score_result.factly_score, 0)
        self.assertLessEqual(score_result.factly_score, 100)
        self.assertIn(score_result.classification,
                      ['Likely Fake', 'Uncertain', 'Likely Authentic'])
        self.assertIn(score_result.confidence_level, ['Low', 'Medium', 'High'])
        self.assertIsInstance(score_result.components, list)
        self.assertEqual(len(score_result.components), 4)
        self.assertIsInstance(score_result.justifications, list)
        self.assertIsInstance(score_result.evidence_summary, dict)
        self.assertIsInstance(score_result.timestamp, datetime)
        self.assertIsInstance(score_result.metadata, dict)
        self.assertIsInstance(score_result.processing_time, float)

    def test_score_never_exceeds_100_or_below_0(self):
        test_scores = [-10, -1, 150, 200]
        for raw in test_scores:
            with self.subTest(raw_score=raw):
                result = VerificationResult(claim=f'Score {raw}', claim_reviews=[],
                                            related_news=[])
                score_result = self.service.calculate_factly_score(result, text_content='x')
                self.assertGreaterEqual(score_result.factly_score, 0)
                self.assertLessEqual(score_result.factly_score, 100)


class TestEdgeCases(TestCase):
    """Edge cases and error handling."""

    def setUp(self):
        self.service = ScoringService()

    def test_empty_claim_does_not_crash(self):
        result = VerificationResult(claim='', claim_reviews=[], related_news=[])
        score_result = self.service.calculate_factly_score(result, text_content='')
        self.assertIsInstance(score_result.factly_score, int)

    def test_very_long_claim_does_not_crash(self):
        long_claim = 'x' * 10000
        result = VerificationResult(claim=long_claim, claim_reviews=[], related_news=[])
        score_result = self.service.calculate_factly_score(result, text_content=long_claim)
        self.assertIsInstance(score_result.factly_score, int)

    def test_result_with_null_metadata_does_not_crash(self):
        result = VerificationResult(
            claim='Test',
            claim_reviews=[],
            related_news=[],
            metadata={'heuristic_match': None},
        )
        score_result = self.service.calculate_factly_score(result, text_content='test')
        self.assertIsInstance(score_result.factly_score, int)

    def test_review_without_publisher_does_not_crash(self):
        review = ClaimReview(
            claim='Test', verdict='true', confidence_score=0.8,
            publisher=None, review_date=datetime.now(), url=None, language='en',
        )
        result = VerificationResult(claim='Test', claim_reviews=[review], related_news=[])
        score_result = self.service.calculate_factly_score(result, text_content='test')
        self.assertIsInstance(score_result.factly_score, int)

    def test_service_reusable_across_calls(self):
        result = VerificationResult(claim='Call 1', claim_reviews=[], related_news=[])
        s1 = self.service.calculate_factly_score(result, text_content='test')
        s2 = self.service.calculate_factly_score(result, text_content='test')
        s3 = self.service.calculate_factly_score(result, text_content='test')
        self.assertEqual(s1.factly_score, s2.factly_score)
        self.assertEqual(s2.factly_score, s3.factly_score)
