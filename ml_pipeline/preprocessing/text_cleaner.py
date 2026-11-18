"""
TruthLens AI - Advanced Text Preprocessing Engine
Handles multilingual text normalization, URL/HTML stripping, negation preservation,
NLTK tokenization, lemmatization, and Hindi language token processing.
"""

import re
import html
import unicodedata
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

# English negation tokens that must be preserved to prevent factual inversion
NEGATION_TOKENS = {"not", "no", "never", "nor", "neither", "none", "hardly", "scarcely", "barely", "cannot", "without"}

# Hindi stopwords set
HINDI_STOPWORDS = {
    "के", "का", "एक", "की", "में", "हो", "था", "पर", "होते", "हैं", "को", "इस",
    "कि", "जो", "कर", "मे", "गया", "करने", "किया", "लिये", "अपने", "ने", "बनी",
    "नहीं", "तो", "ही", "या", "एवं", "दिया", "होता", "थी", "से", "है", "व", "थे"
}

class TextPreprocessor:
    def __init__(self, remove_stopwords=False, lemmatize=True):
        self.remove_stopwords = remove_stopwords
        self.lemmatize = lemmatize
        
        try:
            self.en_stopwords = set(stopwords.words("english")) - NEGATION_TOKENS
        except Exception:
            self.en_stopwords = {"the", "a", "an", "in", "is", "it", "to", "and", "of"}
            
        try:
            self.lemmatizer = WordNetLemmatizer()
        except Exception:
            self.lemmatizer = None

    def detect_language(self, text: str) -> str:
        """
        Lightweight script-based language detector.
        Checks for Devanagari Unicode block (U+0900 - U+097F) for Hindi.
        """
        devanagari_count = sum(1 for c in text if '\u0900' <= c <= '\u097F')
        total_letters = sum(1 for c in text if c.isalpha())
        if total_letters > 0 and (devanagari_count / total_letters) > 0.25:
            return "hi"
        return "en"

    def clean_text(self, text: str, preserve_case: bool = False) -> str:
        """
        Cleans and normalizes text:
        - Decodes HTML entities and strips HTML tags
        - Normalizes URLs and mentions
        - Normalizes unicode (NFKC)
        - Handles punctuation and whitespace
        """
        if not text or not isinstance(text, str):
            return ""

        # Decode HTML entities like &amp;, &quot;, &#39;
        text = html.unescape(text)

        # Remove HTML tags safely
        text = re.sub(r'<[^>]+>', ' ', text)

        # Normalize URLs to a standard token
        text = re.sub(r'https?://\S+|www\.\S+', ' [URL] ', text)

        # Normalize Twitter/X mentions and hashtags
        text = re.sub(r'@\w+', ' [MENTION] ', text)

        # Normalize Unicode characters
        text = unicodedata.normalize('NFKC', text)

        if not preserve_case:
            text = text.lower()

        # Collapse excessive whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def tokenize_and_process(self, text: str, lang: str = "en") -> list[str]:
        """
        Tokenizes cleaned text, applies lemmatization, and optionally removes stopwords
        while preserving negations and semantic markers.
        """
        cleaned = self.clean_text(text)
        if not cleaned:
            return []

        if lang == "hi":
            # Devanagari whitespace and punctuation tokenization
            tokens = re.findall(r'[\u0900-\u097F]+|[a-zA-Z0-9]+', cleaned)
            if self.remove_stopwords:
                tokens = [t for t in tokens if t not in HINDI_STOPWORDS or t == "नहीं"]
            return tokens

        # English tokenization
        try:
            raw_tokens = word_tokenize(cleaned)
        except Exception:
            raw_tokens = re.findall(r'\b\w+\b', cleaned)

        processed = []
        for token in raw_tokens:
            # Skip pure punctuation
            if not any(c.isalnum() for c in token):
                continue

            # Optional stopword filter
            if self.remove_stopwords and token in self.en_stopwords:
                continue

            # Lemmatization
            if self.lemmatize and self.lemmatizer:
                try:
                    lemma = self.lemmatizer.lemmatize(token)
                except Exception:
                    lemma = token
            else:
                lemma = token

            processed.append(lemma)

        return processed

    def transform_to_string(self, text: str, lang: str = "en") -> str:
        """Returns clean tokenized text joined as a single string for TF-IDF vectorization."""
        tokens = self.tokenize_and_process(text, lang=lang)
        return " ".join(tokens)
