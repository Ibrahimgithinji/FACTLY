"""
Text Preprocessing Service

Provides comprehensive text preprocessing capabilities including cleaning,
tokenization, stop-word removal, and language detection.
"""

import re
import logging
from typing import List, Optional, Dict, Any
from langdetect import detect, LangDetectException
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize

logger = logging.getLogger(__name__)

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')


class TextPreprocessor:
    """Service for preprocessing text data."""

    def __init__(self):
        """Initialize the text preprocessor."""
        self.stop_words = set()
        self._load_stop_words()

    def _load_stop_words(self):
        """Load stop words for multiple languages."""
        try:
            # Load English stop words by default
            self.stop_words.update(stopwords.words('english'))
        except LookupError:
            logger.warning("Could not load NLTK stopwords")

    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text.

        Args:
            text: Raw text to clean

        Returns:
            Cleaned text
            
        Raises:
            ValueError: If text exceeds maximum allowed length
        """
        if not text:
            return ""

        # Enforce maximum text length (50KB = 50,000 chars) to prevent memory exhaustion
        MAX_TEXT_LENGTH = 50000
        if len(text) > MAX_TEXT_LENGTH:
            logger.warning(f"Input text exceeds {MAX_TEXT_LENGTH} chars; truncating")
            text = text[:MAX_TEXT_LENGTH]

        # Convert to lowercase
        text = text.lower()

        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)

        # Remove email addresses
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '', text)

        # Remove special characters and digits (keep spaces and basic punctuation)
        text = re.sub(r'[^\w\s.,!?-]', ' ', text)

        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()

        return text

    def tokenize(self, text: str, method: str = "word") -> List[str]:
        """
        Tokenize text into words or sentences.

        Args:
            text: Text to tokenize
            method: Tokenization method ("word" or "sentence")

        Returns:
            List of tokens
        """
        if not text:
            return []

        try:
            if method == "sentence":
                return sent_tokenize(text)
            else:
                return word_tokenize(text)
        except Exception as e:
            logger.error(f"Tokenization failed: {e}")
            return text.split() if method == "word" else [text]

    def remove_stop_words(self, tokens: List[str], language: str = "english") -> List[str]:
        """
        Remove stop words from tokenized text.

        Args:
            tokens: List of tokens
            language: Language for stop words

        Returns:
            Tokens with stop words removed
        """
        if not tokens:
            return []

        # Load language-specific stop words if available
        try:
            lang_stop_words = set(stopwords.words(language))
        except LookupError:
            lang_stop_words = self.stop_words

        return [token for token in tokens if token.lower() not in lang_stop_words]

    def detect_language(self, text: str) -> Optional[str]:
        """
        Detect the language of the text.

        Args:
            text: Text to analyze

        Returns:
            Language code or None if detection fails
        """
        if not text or len(text.strip()) < 10:
            return None

        try:
            return detect(text)
        except LangDetectException:
            logger.warning("Language detection failed")
            return None

    def preprocess(self, text: str, remove_stopwords: bool = True,
                  language: Optional[str] = None) -> Dict[str, Any]:
        """
        Complete preprocessing pipeline.

        Args:
            text: Raw text to preprocess
            remove_stopwords: Whether to remove stop words
            language: Language code (auto-detected if None)

        Returns:
            Dictionary with preprocessing results
        """
        # Clean text
        cleaned_text = self.clean_text(text)

        # Detect language
        detected_lang = language or self.detect_language(cleaned_text) or "english"

        # Tokenize
        tokens = self.tokenize(cleaned_text, method="word")

        # Remove stop words if requested
        if remove_stopwords:
            filtered_tokens = self.remove_stop_words(tokens, detected_lang)
        else:
            filtered_tokens = tokens

        return {
            "original_text": text,
            "cleaned_text": cleaned_text,
            "language": detected_lang,
            "tokens": tokens,
            "filtered_tokens": filtered_tokens,
            "token_count": len(tokens),
            "filtered_token_count": len(filtered_tokens)
        }