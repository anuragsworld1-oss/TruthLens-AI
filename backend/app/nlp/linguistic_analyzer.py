"""
TruthLens AI - Linguistic & Stylistic Analysis Engine
Detects clickbait patterns, sensationalism, emotional urgency, excessive capitalization,
unusual punctuation, and stylistic patterns without conflating style with absolute falsehood.
"""

import re
import math

CLICKBAIT_KEYWORDS = {
    "shocking", "bombshell", "miracle", "unbelievable", "secret", "exposed", "terrified",
    "furious", "banned", "conspiracy", "covert", "cataclysm", "insane", "they don't want you to know",
    "share before deleted", "mind-blowing", "jaw-dropping", "hidden truth", "wake up"
}

HINDI_CLICKBAIT_KEYWORDS = {
    "सनसनीखेज", "चमत्कार", "होश उड़ गए", "गुप्त", "साजिश", "तुरंत शेयर करें", "फॉरवर्ड करें", "बड़ा खुलासा"
}

EMOTIONAL_URGENCY_TOKENS = {
    "immediately", "urgent", "emergency", "danger", "deadly", "crisis", "fatal", "disaster",
    "warning", "alert", "peril", "threat", "apocalypse", "collapse", "catastrophic"
}

POSITIVE_CREDIBILITY_MARKERS = {
    "according to", "reuters", "spokesperson", "clinical trial", "peer-reviewed",
    "published in", "official data", "confirmed by", "study found", "ministry of",
    "department of", "press conference", "formal statement", "university researchers"
}

class LinguisticAnalyzer:
    def __init__(self):
        pass

    def analyze(self, text: str, title: str = "") -> dict:
        """
        Executes full linguistic inspection.
        Returns clickbait score, emotional intensity, punctuation metrics,
        capitalization metrics, and specific warning signals.
        """
        if not text:
            text = ""
        combined = f"{title} {text}".strip()
        words = re.findall(r'\b\w+\b', combined)
        total_words = len(words)

        if total_words == 0:
            return self._empty_result()

        # 1. Capitalization metrics
        caps_words = [w for w in words if w.isupper() and len(w) > 1 and not w.isdigit()]
        caps_ratio = len(caps_words) / total_words

        # 2. Punctuation metrics
        exclamation_count = combined.count("!")
        question_count = combined.count("?")
        mult_exclamations = len(re.findall(r'!{2,}', combined))
        sensational_punct = len(re.findall(r'[!?]{2,}', combined))

        # 3. Clickbait detection
        lower_combined = combined.lower()
        matched_clickbait = []
        for kw in CLICKBAIT_KEYWORDS:
            if kw in lower_combined:
                matched_clickbait.append(kw)
        for hkw in HINDI_CLICKBAIT_KEYWORDS:
            if hkw in combined:
                matched_clickbait.append(hkw)

        # 4. Emotional urgency
        matched_urgency = [w for w in words if w.lower() in EMOTIONAL_URGENCY_TOKENS]
        urgency_score = min(1.0, len(matched_urgency) / max(1, total_words * 0.05))

        # 5. Credibility markers
        matched_credibility = [m for m in POSITIVE_CREDIBILITY_MARKERS if m in lower_combined]

        # 6. Lexical Diversity (Type-Token Ratio)
        unique_words = len(set(w.lower() for w in words))
        ttr = unique_words / total_words

        # 7. Synthesize Warning Signals
        warning_signals = []
        if caps_ratio > 0.08:
            warning_signals.append({
                "type": "excessive_capitalization",
                "severity": "medium",
                "label": "High Capitalization Ratio",
                "description": f"{round(caps_ratio * 100, 1)}% of words in all-caps, common in sensationalist headlines."
            })

        if sensational_punct > 0 or exclamation_count > 3:
            warning_signals.append({
                "type": "sensational_punctuation",
                "severity": "medium",
                "label": "Sensational Punctuation",
                "description": f"Found {exclamation_count} exclamation marks and repeated punctuation patterns (e.g., '!!', '?!')."
            })

        if len(matched_clickbait) > 0:
            warning_signals.append({
                "type": "clickbait_language",
                "severity": "high" if len(matched_clickbait) >= 2 else "medium",
                "label": "Clickbait & Hyperbolic Phrasing",
                "description": f"Detected clickbait terms: {', '.join(matched_clickbait[:5])}."
            })

        if urgency_score > 0.4:
            warning_signals.append({
                "type": "artificial_urgency",
                "severity": "medium",
                "label": "High Emotional Urgency",
                "description": "Article creates acute urgency or fear triggers to encourage rapid sharing."
            })

        # Calculate Overall Linguistic Risk Index (0 to 100)
        risk_points = (
            min(35, len(matched_clickbait) * 15) +
            min(25, caps_ratio * 250) +
            min(20, sensational_punct * 10 + min(10, exclamation_count * 2)) +
            min(20, urgency_score * 25)
        )
        # Offset by formal credibility markers
        risk_points = max(0, min(100, risk_points - (len(matched_credibility) * 10)))

        return {
            "linguistic_risk_score": round(risk_points, 1),
            "word_count": total_words,
            "capitalization_ratio": round(caps_ratio, 3),
            "exclamation_count": exclamation_count,
            "sensational_punctuation_count": sensational_punct,
            "lexical_diversity_ttr": round(ttr, 3),
            "detected_clickbait_terms": matched_clickbait,
            "detected_urgency_terms": list(set(matched_urgency)),
            "detected_credibility_markers": matched_credibility,
            "warning_signals": warning_signals,
            "summary_note": "Linguistic features represent stylistic signals and behavioral heuristics, not conclusive proof of factual accuracy."
        }

    def _empty_result(self) -> dict:
        return {
            "linguistic_risk_score": 0.0,
            "word_count": 0,
            "capitalization_ratio": 0.0,
            "exclamation_count": 0,
            "sensational_punctuation_count": 0,
            "lexical_diversity_ttr": 0.0,
            "detected_clickbait_terms": [],
            "detected_urgency_terms": [],
            "detected_credibility_markers": [],
            "warning_signals": [],
            "summary_note": "No text provided for analysis."
        }
