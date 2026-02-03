"""
Claim Extraction Service

Extracts verifiable claims from text content using NLP techniques.
Identifies factual statements that can be checked against external sources.
"""

import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from .text_preprocessing import TextPreprocessor

logger = logging.getLogger(__name__)


class ClaimType(Enum):
    """Types of claims that can be extracted."""
    FACTUAL = "factual"  # Objective facts (dates, statistics, events)
    QUOTATION = "quotation"  # Direct quotes from people
    PREDICTION = "prediction"  # Future predictions
    COMPARISON = "comparison"  # Comparisons between entities
    CAUSAL = "causal"  # Cause-and-effect statements


@dataclass
class ExtractedClaim:
    """Represents an extracted claim with metadata."""
    text: str
    claim_type: ClaimType
    confidence: float  # 0.0 to 1.0
    context: str  # Surrounding text for context
    entities: List[str]  # Named entities mentioned
    keywords: List[str]  # Key terms for searching
    position: Tuple[int, int]  # Start and end positions in original text
    verifiability_score: float  # How easy to verify (0.0 to 1.0)


class ClaimExtractor:
    """Extracts verifiable claims from text content."""

    # Patterns that indicate factual claims
    FACTUAL_INDICATORS = [
        r'\b\d{1,3}(?:,\d{3})+(?:\.\d+)?\b',  # Numbers with commas
        r'\b\d+\s*(?:percent|%|million|billion|thousand)\b',  # Statistics
        r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}(?:,\s+\d{4})?\b',  # Dates
        r'\b\d{4}\b',  # Years
        r'\b(?:according to|reported by|stated that|claimed that|announced)\b',  # Attribution
    ]

    # Patterns that indicate non-factual content
    NON_FACTUAL_PATTERNS = [
        r'\b(?:I think|I believe|in my opinion|personally|I feel)\b',  # Opinions
        r'\b(?:should|must|need to|ought to)\b.*\b(?:do|act|change)\b',  # Prescriptions
        r'\b(?:beautiful|ugly|good|bad|best|worst|amazing|terrible)\b.*\b(?:is|are|was|were)\b',  # Subjective
        r'\?\s*$',  # Questions
    ]

    # Claim keywords that suggest verifiability
    VERIFIABLE_KEYWORDS = [
        'announced', 'reported', 'confirmed', 'denied', 'stated', 'claimed',
        'according to', 'data shows', 'statistics', 'study', 'research',
        'survey', 'poll', 'found', 'discovered', 'revealed', 'documented'
    ]

    def __init__(self):
        """Initialize the claim extractor."""
        self.text_preprocessor = TextPreprocessor()
        self.factual_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.FACTUAL_INDICATORS]
        self.non_factual_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.NON_FACTUAL_PATTERNS]

    def extract_claims(self, text: str, min_confidence: float = 0.5) -> List[ExtractedClaim]:
        """
        Extract verifiable claims from text.

        Args:
            text: Input text to analyze
            min_confidence: Minimum confidence threshold for claims

        Returns:
            List of extracted claims
        """
        if not text or len(text.strip()) < 10:
            return []

        logger.info(f"Extracting claims from text ({len(text)} chars)")

        # Preprocess text
        cleaned_text = self.text_preprocessor.clean_text(text)
        sentences = self.text_preprocessor.tokenize(cleaned_text, method="sentence")

        claims = []
        for i, sentence in enumerate(sentences):
            # Skip very short sentences
            if len(sentence.split()) < 3:
                continue

            claim = self._analyze_sentence(sentence, text, i, sentences)
            if claim and claim.confidence >= min_confidence:
                claims.append(claim)

        # Sort by verifiability score (highest first)
        claims.sort(key=lambda x: x.verifiability_score, reverse=True)

        logger.info(f"Extracted {len(claims)} claims from text")
        return claims

    def _analyze_sentence(self, sentence: str, full_text: str,
                          sentence_index: int, all_sentences: List[str]) -> Optional[ExtractedClaim]:
        """Analyze a single sentence for claim extraction."""
        # Get context (previous and next sentence)
        context = self._get_context(sentence_index, all_sentences)

        # Determine claim type
        claim_type = self._determine_claim_type(sentence)

        # Check for factual indicators
        factual_score = self._calculate_factual_score(sentence)

        # Check for non-factual indicators
        non_factual_score = self._calculate_non_factual_score(sentence)

        # Calculate confidence
        confidence = max(0.0, min(1.0, factual_score - non_factual_score))

        # Extract entities and keywords
        entities = self._extract_entities(sentence)
        keywords = self._extract_keywords(sentence)

        # Calculate verifiability score
        verifiability_score = self._calculate_verifiability(
            sentence, claim_type, entities, keywords
        )

        # Find position in original text
        position = self._find_position(sentence, full_text)

        return ExtractedClaim(
            text=sentence,
            claim_type=claim_type,
            confidence=confidence,
            context=context,
            entities=entities,
            keywords=keywords,
            position=position,
            verifiability_score=verifiability_score
        )

    def _get_context(self, sentence_index: int, sentences: List[str], window: int = 1) -> str:
        """Get surrounding context for a sentence."""
        start = max(0, sentence_index - window)
        end = min(len(sentences), sentence_index + window + 1)
        return ' '.join(sentences[start:end])

    def _determine_claim_type(self, sentence: str) -> ClaimType:
        """Determine the type of claim."""
        sentence_lower = sentence.lower()

        # Check for quotations
        if '"' in sentence or '"' in sentence or '"' in sentence:
            return ClaimType.QUOTATION

        # Check for predictions (future tense indicators)
        prediction_words = ['will', 'going to', 'predicted', 'forecast', 'expected to']
        if any(word in sentence_lower for word in prediction_words):
            return ClaimType.PREDICTION

        # Check for comparisons
        comparison_words = ['than', 'compared to', 'more than', 'less than', 'equal to', 'versus', 'vs']
        if any(word in sentence_lower for word in comparison_words):
            return ClaimType.COMPARISON

        # Check for causal statements
        causal_words = ['because', 'caused by', 'led to', 'resulted in', 'due to', 'as a result']
        if any(word in sentence_lower for word in causal_words):
            return ClaimType.CAUSAL

        return ClaimType.FACTUAL

    def _calculate_factual_score(self, sentence: str) -> float:
        """Calculate factual indicator score."""
        score = 0.0
        for pattern in self.factual_patterns:
            matches = len(pattern.findall(sentence))
            score += matches * 0.2
        return min(1.0, score)

    def _calculate_non_factual_score(self, sentence: str) -> float:
        """Calculate non-factual indicator score."""
        score = 0.0
        for pattern in self.non_factual_patterns:
            if pattern.search(sentence):
                score += 0.3
        return min(1.0, score)

    def _extract_entities(self, sentence: str) -> List[str]:
        """Extract named entities from sentence (simplified)."""
        # Simple entity extraction based on capitalization patterns
        words = sentence.split()
        entities = []
        current_entity = []

        for word in words:
            # Clean the word
            clean_word = re.sub(r'[^\w\s]', '', word)

            if clean_word and clean_word[0].isupper() and len(clean_word) > 1:
                current_entity.append(clean_word)
            else:
                if len(current_entity) >= 1:
                    entity = ' '.join(current_entity)
                    if len(entity) > 2:
                        entities.append(entity)
                current_entity = []

        # Don't forget the last entity
        if len(current_entity) >= 1:
            entity = ' '.join(current_entity)
            if len(entity) > 2:
                entities.append(entity)

        return list(set(entities))  # Remove duplicates

    def _extract_keywords(self, sentence: str) -> List[str]:
        """Extract key terms for searching."""
        # Remove stop words and keep important terms
        tokens = self.text_preprocessor.tokenize(sentence, method="word")
        stop_words = self.text_preprocessor.stop_words

        keywords = []
        for token in tokens:
            # Keep words that are:
            # - Not stop words
            # - Longer than 3 characters
            # - Or contain numbers
            if (token.lower() not in stop_words and len(token) > 3) or \
               (any(c.isdigit() for c in token)):
                keywords.append(token)

        return keywords[:10]  # Limit to top 10 keywords

    def _calculate_verifiability(self, sentence: str, claim_type: ClaimType,
                                  entities: List[str], keywords: List[str]) -> float:
        """Calculate how easy it is to verify this claim."""
        score = 0.5  # Base score

        # Factual claims are more verifiable
        if claim_type == ClaimType.FACTUAL:
            score += 0.2
        elif claim_type == ClaimType.QUOTATION:
            score += 0.15
        elif claim_type == ClaimType.PREDICTION:
            score -= 0.1  # Harder to verify

        # More entities = more specific = more verifiable
        score += min(0.2, len(entities) * 0.05)

        # Check for verifiable keywords
        sentence_lower = sentence.lower()
        for keyword in self.VERIFIABLE_KEYWORDS:
            if keyword in sentence_lower:
                score += 0.1
                break

        # Check for numbers/statistics
        if re.search(r'\d+', sentence):
            score += 0.1

        return max(0.0, min(1.0, score))

    def _find_position(self, sentence: str, full_text: str) -> Tuple[int, int]:
        """Find the position of the sentence in the original text."""
        # Try to find exact match first
        start = full_text.find(sentence)
        if start != -1:
            return (start, start + len(sentence))

        # Try with cleaned text
        cleaned_sentence = sentence.strip()
        start = full_text.find(cleaned_sentence)
        if start != -1:
            return (start, start + len(cleaned_sentence))

        return (0, len(full_text))

    def get_primary_claim(self, text: str) -> Optional[ExtractedClaim]:
        """
        Extract the primary (most verifiable) claim from text.

        Args:
            text: Input text to analyze

        Returns:
            The most verifiable claim, or None if no claims found
        """
        claims = self.extract_claims(text, min_confidence=0.3)

        if not claims:
            return None

        # Return the claim with highest verifiability score
        return max(claims, key=lambda x: x.verifiability_score)

    def generate_search_queries(self, claim: ExtractedClaim, max_queries: int = 3) -> List[str]:
        """
        Generate search queries for fact-checking a claim.

        Args:
            claim: The extracted claim
            max_queries: Maximum number of queries to generate

        Returns:
            List of search query strings
        """
        queries = []

        # Primary query: main claim text
        # Truncate to reasonable length
        primary_query = claim.text[:150] if len(claim.text) > 150 else claim.text
        queries.append(primary_query)

        # Secondary query: entities + keywords
        if claim.entities and claim.keywords:
            entity_terms = ' '.join(claim.entities[:2])
            keyword_terms = ' '.join(claim.keywords[:3])
            secondary_query = f"{entity_terms} {keyword_terms}"
            if len(secondary_query) > 20:
                queries.append(secondary_query)

        # Third query: focus on key facts
        if len(queries) < max_queries:
            # Extract numbers and key terms
            numbers = re.findall(r'\b\d+(?:,\d{3})*(?:\.\d+)?(?:\s*(?:percent|%|million|billion))?\b', claim.text)
            if numbers and claim.entities:
                fact_query = f"{claim.entities[0]} {numbers[0]}"
                queries.append(fact_query)

        return queries[:max_queries]
