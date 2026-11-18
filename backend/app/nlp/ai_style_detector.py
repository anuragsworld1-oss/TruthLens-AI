"""
TruthLens AI - AI-Generated Writing Style Assessment (Experimental)
Evaluates stylistic characteristics often observed in large language model generated text:
- Sentence length uniformity (low standard deviation)
- Formulaic transitional phrasing ('delve into', 'testament to', 'furthermore', 'it is important to note')
- Lexical predictability & repetitive sentence starts
- Strictly includes ethical disclaimers: AI writing does NOT indicate falsity.
"""

import re
import math
import numpy as np

AI_TRANSITIONAL_PATTERNS = [
    r"\bit is important to (note|remember|consider)\b",
    r"\bit is worth (noting|mentioning)\b",
    r"\bdelve into\b",
    r"\bserves as a testament\b",
    r"\bin conclusion\b",
    r"\bfurthermore\b",
    r"\bmoreover\b",
    r"\bin today's rapidly (evolving|changing) world\b",
    r"\ba wide array of\b",
    r"\bplays a crucial role in\b",
    r"\bcomprehensive overview\b",
    r"\bnavigating the complexities\b",
    r"\blandscape of\b"
]

class AIWritingStyleDetector:
    def __init__(self):
        pass

    def assess_style(self, text: str) -> dict:
        """
        Calculates an experimental AI writing style likelihood score (0 to 100).
        """
        if not text or len(text.strip()) < 50:
            return self._empty_result()

        words = re.findall(r'\b\w+\b', text.lower())
        total_words = len(words)
        if total_words < 10:
            return self._empty_result()

        # 1. Sentence length variance (Burstiness)
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if len(s.strip()) > 0]
        sentence_lengths = [len(s.split()) for s in sentences if len(s.split()) > 2]
        
        if len(sentence_lengths) >= 3:
            mean_len = float(np.mean(sentence_lengths))
            std_len = float(np.std(sentence_lengths))
            # Low standard deviation relative to mean indicates uniform machine rhythm
            cv = std_len / mean_len if mean_len > 0 else 1.0
        else:
            mean_len = 15.0
            std_len = 5.0
            cv = 0.5

        # 2. Cliché AI Transitional Phrases
        matched_patterns = []
        for pat in AI_TRANSITIONAL_PATTERNS:
            matches = re.findall(pat, text.lower())
            if matches:
                matched_patterns.append(pat.replace(r"\b", "").replace("(", "").replace(")", "").replace("|", "/"))

        # 3. Vocabulary Repetition / Type-Token Ratio (TTR)
        unique_tokens = len(set(words))
        ttr = unique_tokens / total_words

        # 4. Repetitive sentence beginnings
        sentence_starts = [s.split()[0].lower() for s in sentences if len(s.split()) > 0]
        start_counts = {}
        for s in sentence_starts:
            start_counts[s] = start_counts.get(s, 0) + 1
        max_start_repeat = max(start_counts.values()) if start_counts else 1
        start_repeat_ratio = max_start_repeat / max(1, len(sentence_starts))

        # 5. Composite AI Writing Style Score (0-100)
        # Note: Humans write with high burstiness (varying short and long sentences)
        uniformity_score = max(0, min(35, (0.6 - min(0.6, cv)) * 60))
        phrase_score = min(35, len(matched_patterns) * 12)
        start_score = min(15, start_repeat_ratio * 30)
        vocab_score = 15 if (0.45 <= ttr <= 0.65) else 5

        ai_style_score = round(uniformity_score + phrase_score + start_score + vocab_score, 1)
        ai_style_score = max(5.0, min(95.0, ai_style_score))

        style_classification = "Standard Human Writing Patterns"
        if ai_style_score >= 65:
            style_classification = "High Concentration of Formulaic AI Writing Patterns"
        elif ai_style_score >= 40:
            style_classification = "Moderate AI-Assisted or Highly Formal Prose Characteristics"

        return {
            "ai_style_score": ai_style_score,
            "style_classification": style_classification,
            "sentence_length_uniformity_cv": round(cv, 2),
            "average_sentence_length": round(mean_len, 1),
            "lexical_diversity_ttr": round(ttr, 3),
            "formulaic_phrases_detected": matched_patterns,
            "repetitive_starters_detected": [k for k, v in start_counts.items() if v > 2],
            "experimental_disclaimer": "This assessment is experimental and evaluates statistical prose symmetry. AI-assisted drafting is common across reputable newsrooms and is NOT proof of misinformation."
        }

    def _empty_result(self) -> dict:
        return {
            "ai_style_score": 0.0,
            "style_classification": "Insufficient text for assessment",
            "sentence_length_uniformity_cv": 0.0,
            "average_sentence_length": 0.0,
            "lexical_diversity_ttr": 0.0,
            "formulaic_phrases_detected": [],
            "repetitive_starters_detected": [],
            "experimental_disclaimer": "Text length too short for statistical stylometry."
        }
