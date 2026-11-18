"""
TruthLens AI 2.0 - Calibrated Credibility Engine
Separates MODEL CONFIDENCE from FACTUAL VERIFICATION and applies uncertainty
handling so that genuine articles with rare vocabulary (e.g. technical science
releases) are not mislabeled as "Potentially Misleading" purely because the
small training set makes the models under-confident.

Key principles (mandated by the project requirements):
  * Model confidence is NOT the probability that an article is factually true.
  * Model disagreement and insufficient evidence => "Unverified", never a
    forced "fake" verdict.
  * Linguistic penalties apply ONLY when actual warning signals are present.
  * Uncertainty is surfaced explicitly (Low / Medium / High).

Outcomes (3-class, backward-compatible mapping preserved by the caller):
  - Likely Reliable        (was "Likely Genuine")
  - Potentially Misleading (unchanged)
  - Unverified             (was "Needs Further Verification")
"""

import numpy as np


class CredibilityEngine:
    """Fuses ensemble probabilities, agreement, linguistic risk, and (optionally)
    evidence-verification results into a calibrated credibility assessment."""

    # 3-class label names used across the app.
    RELIABLE = "Likely Reliable"
    MISLEADING = "Potentially Misleading"
    UNVERIFIED = "Unverified"

    def __init__(self):
        pass

    def assess(
        self,
        mean_probs,                      # np.ndarray shape (3,) [genuine, misleading, verify]
        agreement_ratio,                 # float 0-100
        linguistic_res,                  # dict from LinguisticAnalyzer
        word_count=0,                    # int
        evidence_summary=None,           # dict | None  (from the fact-checker / RAG)
        transformer_probs=None,          # np.ndarray (3,) | None
        consensus_class_id=0,            # int 0=genuine,1=misleading,2=verify
    ) -> dict:
        """
        Returns:
            credibility_score (float 0-100)
            outcome (str)                 one of the 3 outcomes
            uncertainty_level (str)       Low / Medium / High
            confidence_signals (dict)     model-confidence-only view (separate from truth)
            evidence_signal (dict)        verification-only view (separate from confidence)
            reasoning (list[str])         human-readable factors that drove the decision
        """
        prob_genuine = float(mean_probs[0])
        prob_misleading = float(mean_probs[1])
        prob_verify = float(mean_probs[2])

        # ------------------------------------------------------------------
        # 1. CONFIDENCE SIGNAL (model confidence only -- NOT factual truth)
        # ------------------------------------------------------------------
        # Temperature-shrink the raw probabilities toward a neutral prior so a
        # rare-vocabulary article does not collapse to a near-zero genuine prob
        # merely because the small training set never saw those tokens. The
        # shrink strength grows with model disagreement and with how "technical"
        # the text looks (long + lexically diverse => likely specialist prose).
        linguistic_risk = float(linguistic_res.get("linguistic_risk_score", 0.0) or 0.0)
        warning_signals = linguistic_res.get("warning_signals", []) or []
        ttr = float(linguistic_res.get("lexical_diversity_ttr", 0.0) or 0.0)
        has_warning_signals = len(warning_signals) > 0

        # Disagreement drives uncertainty (0=full agreement, 100=total split).
        disagreement = max(0.0, 100.0 - agreement_ratio)

        # Technical-text indicator: long articles with high lexical diversity
        # and NO warning signals look like specialist/reporting prose, not
        # clickbait -- so we trust the "no warnings" signal and shrink less
        # aggressively toward misleading.
        looks_technical = (word_count >= 120) and (ttr >= 0.45) and (not has_warning_signals)

        # Neutral prior (uniform). Shrink factor in [0.25, 0.75].
        prior = np.array([1 / 3, 1 / 3, 1 / 3])
        # More disagreement => more shrink toward prior (less trust in any class).
        shrink = 0.25 + 0.50 * min(1.0, disagreement / 100.0)
        calibrated = (1.0 - shrink) * mean_probs + shrink * prior

        cal_genuine = float(calibrated[0])
        cal_misleading = float(calibrated[1])
        cal_verify = float(calibrated[2])

        # Base credibility from CALIBRATED genuine probability.
        base_score = cal_genuine * 100.0

        # ------------------------------------------------------------------
        # 2. LINGUISTIC PENALTY (only when real warning signals exist)
        # ------------------------------------------------------------------
        # Previously the penalty was applied unconditionally via the raw risk
        # number. Now it only bites when there are actual warning signals, and
        # its magnitude is bounded. A clean, formal science article pays ~0.
        if has_warning_signals:
            linguistic_penalty = min(25.0, linguistic_risk * 0.30)
        else:
            linguistic_penalty = 0.0
        adjusted_score = base_score - linguistic_penalty

        # ------------------------------------------------------------------
        # 3. EVIDENCE SIGNAL (factual verification -- separate from confidence)
        # ------------------------------------------------------------------
        evidence_signal = {
            "available": False,
            "any_supported": False,
            "any_contradicted": False,
            "any_insufficient": False,
            "verified_claims_ratio": 0.0,
        }
        evidence_boost = 0.0
        evidence_penalty = 0.0
        if evidence_summary and isinstance(evidence_summary, dict):
            claims = evidence_summary.get("claims", []) or []
            if claims:
                evidence_signal["available"] = True
                supported = sum(1 for c in claims if c.get("verification_status", "").startswith("Supported"))
                contradicted = sum(1 for c in claims if c.get("verification_status", "").startswith("Contradicted"))
                insufficient = sum(1 for c in claims if c.get("verification_status", "") == "Insufficient evidence")
                total = max(1, len(claims))
                evidence_signal["any_supported"] = supported > 0
                evidence_signal["any_contradicted"] = contradicted > 0
                evidence_signal["any_insufficient"] = insufficient > 0
                evidence_signal["verified_claims_ratio"] = round(supported / total, 2)
                # External verified evidence can support (+) or contradict (-),
                # but NEVER auto-flips an unsupported claim to "fake".
                evidence_boost = min(12.0, supported / total * 12.0)
                evidence_penalty = min(20.0, contradicted / total * 20.0)

        adjusted_score += evidence_boost - evidence_penalty

        # ------------------------------------------------------------------
        # 4. UNCERTAINTY LEVEL
        # ------------------------------------------------------------------
        high_disagreement = disagreement >= 40.0      # agreement <= 60
        insufficient_evidence = evidence_signal["any_insufficient"] and not evidence_signal["any_supported"]
        low_model_confidence = max(cal_genuine, cal_misleading) < 0.45

        if high_disagreement or (low_model_confidence and insufficient_evidence):
            uncertainty_level = "High"
        elif disagreement >= 20.0 or low_model_confidence or insufficient_evidence:
            uncertainty_level = "Medium"
        else:
            uncertainty_level = "Low"

        # ------------------------------------------------------------------
        # 5. OUTCOME DECISION (with uncertainty handling)
        # ------------------------------------------------------------------
        # Clamp final score.
        final_score = max(5.0, min(98.0, adjusted_score))

        reasoning = []
        strong_evidence_support = (
            evidence_signal["available"]
            and evidence_signal["any_supported"]
            and not evidence_signal["any_contradicted"]
            and evidence_signal["verified_claims_ratio"] >= 0.5
        )
        consensus_genuine = (consensus_class_id == 0)
        consensus_misleading = (consensus_class_id == 1)

        # --- OUTCOME DECISION (evidence- & consensus-aware, uncertainty-safe) ---
        # Rule 1: Strong contradicting evidence => Potentially Misleading.
        #         This is the one place external evidence (not just style) pushes
        #         toward misleading, and only when the contradiction is material.
        if evidence_signal["any_contradicted"] and evidence_penalty >= 10.0:
            outcome = self.MISLEADING
            final_score = min(final_score, 45.0)
            reasoning.append("Retrieved evidence directly contradicts one or more factual claims.")
        # Rule 2: High model disagreement with no warning signals and no strong
        #         evidence support => Unverified. Never force a fake verdict on
        #         disagreement alone. When warning signals ARE present they take
        #         precedence (handled by Rule 5 below).
        elif high_disagreement and not strong_evidence_support and not has_warning_signals:
            outcome = self.UNVERIFIED
            final_score = min(final_score, 55.0)
            reasoning.append("Models strongly disagree and no corroborating evidence is available; treat as unverified.")
        # Rule 3: Clean article (no warning signals) corroborated by evidence =>
        #         Likely Reliable. External evidence is the strongest signal and
        #         outweighs weak out-of-distribution model uncertainty.
        elif not has_warning_signals and strong_evidence_support:
            outcome = self.RELIABLE
            final_score = max(final_score, min(82.0, final_score + 8.0))
            reasoning.append("No warning signals and factual claims are corroborated by retrieved evidence.")
        # Rule 4: Clean article, models agree it is genuine, no contradiction =>
        #         Likely Reliable. A genuine consensus with no red flags should
        #         not be flipped to misleading by vocabulary rarity alone.
        elif not has_warning_signals and consensus_genuine and agreement_ratio >= 60.0 and not evidence_signal["any_contradicted"]:
            outcome = self.RELIABLE
            final_score = max(final_score, 60.0)
            reasoning.append("Models agree the article is likely genuine and no warning signals or contradicting evidence were found.")
        # Rule 5: Warning signals present. A low credibility score here means
        #         the models are confident the article is misleading AND there
        #         are stylistic red flags => Misleading (not Unverified). Only
        #         a high score with minor signals stays Reliable. (High
        #         disagreement is already handled by Rule 2 above.)
        elif has_warning_signals:
            if final_score >= 65.0:
                outcome = self.RELIABLE
            else:
                outcome = self.MISLEADING
                reasoning.append("Linguistic warning signals combined with a low-to-moderate credibility score indicate potential misleading.")
        # Rule 6: No warning signals, no corroborating evidence, models uncertain
        #         => Unverified, NOT Misleading. (False-positive guard.)
        else:
            if final_score >= 62.0 and consensus_genuine:
                outcome = self.RELIABLE
            else:
                outcome = self.UNVERIFIED
                final_score = min(max(final_score, 45.0), 58.0)
                reasoning.append("Insufficient evidence and no warning signals; cannot justify a misleading verdict, treating as unverified.")

        # Build reasoning notes.
        if has_warning_signals:
            reasoning.append(f"Linguistic warning signals present (risk index {linguistic_risk:.0f}).")
        else:
            reasoning.append("No linguistic warning signals detected.")
        reasoning.append(f"Model agreement: {agreement_ratio:.0f}% (disagreement {disagreement:.0f}%).")
        if evidence_signal["available"]:
            reasoning.append(
                f"Evidence: {int(evidence_signal['verified_claims_ratio']*100)}% of claims supported by retrieved sources."
            )
        else:
            reasoning.append("No verified external evidence indexed for these claims.")
        if looks_technical:
            reasoning.append("Text appears to be specialist/technical prose; vocabulary rarity is not treated as a deception signal.")

        confidence_signals = {
            "calibrated_genuine_prob": round(cal_genuine * 100, 1),
            "calibrated_misleading_prob": round(cal_misleading * 100, 1),
            "calibrated_verify_prob": round(cal_verify * 100, 1),
            "raw_genuine_prob": round(prob_genuine * 100, 1),
            "raw_misleading_prob": round(prob_misleading * 100, 1),
            "max_class_confidence": round(max(cal_genuine, cal_misleading, cal_verify) * 100, 1),
            "note": "Model confidence is a probabilistic signal and is NOT a measure of factual truth.",
        }

        return {
            "credibility_score": round(final_score, 1),
            "outcome": outcome,
            "uncertainty_level": uncertainty_level,
            "confidence_signals": confidence_signals,
            "evidence_signal": evidence_signal,
            "reasoning": reasoning,
        }


# Outcome -> backward-compatible legacy label mapping (used by prediction_service
# so existing API consumers keep receiving `predicted_class` in the old namespace).
OUTCOME_TO_LEGACY = {
    CredibilityEngine.RELIABLE: "Likely Genuine",
    CredibilityEngine.MISLEADING: "Potentially Misleading",
    CredibilityEngine.UNVERIFIED: "Needs Further Verification",
}
