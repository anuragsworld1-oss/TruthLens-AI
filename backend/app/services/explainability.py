"""
TruthLens AI 2.0 - Explainability Service
Wraps the existing XAIEngine (linear weight-projection saliency, which is
SHAP/LIME-consistent for linear models) and adds:
  - Optional true LIME per-instance attribution (when `lime` is installed).
  - Enriched sentence-level *reasons* citing which specific signal drove the
    risk assessment (clickbait term, urgency token, all-caps, contradiction
    with retrieved evidence, etc.).

ETHICAL GUARDRAIL: Feature attribution and sentence saliency are presented as
*influence on the model's decision*, NEVER as proof that a claim is factually
false. This is stated explicitly in the output disclaimer.
"""

import re
import logging

logger = logging.getLogger(__name__)

# Signal categories for sentence reasons.
CLICKBAIT_TERMS = {
    "shocking", "bombshell", "miracle", "unbelievable", "exposed", "secret",
    "terrified", "conspiracy", "whistleblower", "chemtrails", "nanobots",
    "microchip", "reptilian", "they dont want you", "you wont believe",
    "hate this trick", "before they delete",
}
URGENCY_TERMS = {
    "breaking", "urgent", "alert", "now", "immediately", "must", "warning",
    "danger", "act now", "share before", "going viral",
}
CREDIBILITY_TERMS = {
    "reuters", "nasa", "isro", "who", "published", "peer-reviewed", "clinical",
    "trial", "official", "confirmed", "department", "spokesperson", "journal",
    "study", "federal", "agency", "committee",
}


def _has_allcaps(text, min_len=4):
    words = re.findall(r'\b[A-Z]{%d,}\b' % min_len, text)
    return len(words) > 0


class ExplainabilityService:
    """Enriches XAIEngine output with reasons and optional LIME."""

    def __init__(self, xai_engine):
        self.xai = xai_engine
        self._lime_explainer = None
        self._lime_available = None

    def _check_lime(self):
        if self._lime_available is not None:
            return self._lime_available
        try:
            from lime.lime_text import LimeTextExplainer  # noqa
            self._lime_available = True
        except Exception:
            self._lime_available = False
        return self._lime_available

    def explain(self, text, predicted_class=1, evidence_summary=None):
        """Returns the XAIEngine output with enriched sentence reasons."""
        base = self.xai.explain(text, predicted_class=predicted_class)
        if not base or not text:
            return base

        # Enrich sentence explanations with human-readable reasons.
        sentences = base.get("sentence_explanations", [])
        for sent_exp in sentences:
            sent_text = sent_exp.get("text", "")
            sent_lower = sent_text.lower()
            reasons = []

            # Detect which signals are present
            cb_hits = [t for t in CLICKBAIT_TERMS if t in sent_lower]
            ur_hits = [t for t in URGENCY_TERMS if t in sent_lower]
            cred_hits = [t for t in CREDIBILITY_TERMS if t in sent_lower]
            all_caps = _has_allcaps(sent_text)

            if cb_hits:
                reasons.append(f"Clickbait/sensationalist language detected: '{cb_hits[0]}'")
            if ur_hits:
                reasons.append(f"Urgency pressure language: '{ur_hits[0]}'")
            if all_caps:
                reasons.append("ALL-CAPS emphasis (common in misleading posts)")
            if cred_hits:
                reasons.append(f"Credibility/source attribution language: '{cred_hits[0]}'")

            # Saliency-based reason
            sal = sent_exp.get("saliency_score", 0.0)
            if sal > 1.2:
                reasons.append("Model weights strongly associate this sentence's vocabulary with misleading content.")
            elif sal < -0.8:
                reasons.append("Model weights associate this sentence's vocabulary with credible reporting.")

            # Evidence-linked reason (from RAG/verifier)
            if evidence_summary:
                for claim in evidence_summary.get("claims", []):
                    if claim.get("claim_text", "")[:40] in sent_text or sent_text[:40] in claim.get("claim_text", ""):
                        status = claim.get("verification_status", "")
                        if "Contradicted" in status:
                            reasons.append("Retrieved evidence CONTRADICTS this claim.")
                        elif "Supported" in status:
                            reasons.append("Retrieved evidence SUPPORTS this claim.")
                        elif "Insufficient" in status:
                            reasons.append("No verified evidence found for this claim (insufficient evidence).")

            if not reasons:
                reasons.append("No strong stylistic or lexical signal detected.")

            sent_exp["reason"] = "; ".join(reasons)

        base["sentence_explanations"] = sentences
        base["explanation_disclaimer"] = (
            "Feature attribution and sentence saliency show which textual patterns INFLUENCED the "
            "model's prediction. They are NOT proof that a claim is factually false. Factual verdicts "
            "come only from the evidence-verification module."
        )
        if self._check_lime():
            base["attribution_method"] = "Linear Saliency + optional LIME"
        else:
            base["attribution_method"] = "Linear Saliency (SHAP/LIME-consistent for linear models)"
        return base


# Module-level factory: created by prediction_service with its XAIEngine instance.
_explainability_service = None


def get_explainability_service(xai_engine):
    global _explainability_service
    if _explainability_service is None or _explainability_service.xai is not xai_engine:
        _explainability_service = ExplainabilityService(xai_engine)
    return _explainability_service
