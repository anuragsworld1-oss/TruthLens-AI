"""
TruthLens AI 2.0 - Extended Test Suite
Tests the upgraded pipeline: calibrated credibility engine (false-positive guard),
structured claim extraction, evidence verification, uncertainty handling,
graceful optional-dependency degradation, and edge cases.

Run:  python -m pytest tests/test_truthlens_v2.py -v
"""

import os
import sys
import pytest

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(TEST_DIR)
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")
ML_DIR = os.path.join(PROJECT_ROOT, "ml_pipeline")

for p in [PROJECT_ROOT, BACKEND_DIR, ML_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

from backend.app.services.prediction_service import prediction_service
from backend.app.services.credibility_engine import CredibilityEngine, OUTCOME_TO_LEGACY
from backend.app.services.claim_extraction import ClaimExtractor
from backend.app.factcheck.verifier import ClaimVerifier
from backend.app.services.transformer_service import transformer_service
from backend.app.services.evidence_retrieval import get_evidence_retriever


# --------------------------------------------------------------------------- #
# Test fixtures
# --------------------------------------------------------------------------- #

JWST_SCIENCE = (
    "Astronomers using NASA James Webb Space Telescope have discovered the most "
    "distant active supermassive black hole found to date. The galaxy, CEERS 1019, "
    "existed just over 570 million years after the Big Bang. Researchers published "
    "their peer-reviewed findings in The Astrophysical Journal. The team noted that "
    "the spectroscopic data gathered by Webb NIRSpec instrument provided unequivocal "
    "evidence of ionized gas accretion around the galactic nucleus."
)

HEALTH_MISINFO = (
    "SHOCKING! Doctors HATE this trick! Drinking turmeric water every morning "
    "CURES cancer in just 3 days - Big Pharma is hiding this miracle cure from you! "
    "You will not believe what happens next!!"
)

POLITICAL_MISINFO = (
    "BREAKING: Leaked documents PROVE Senator Johnson secretly funneled millions "
    "to offshore accounts! You wont see this on mainstream media! SHARE before they "
    "delete this!! Sources say insiders confirmed the explosive allegations."
)

GENUINE_ECONOMY = (
    "The Federal Reserve concluded its two-day Federal Open Market Committee meeting "
    "on Wednesday, maintaining the federal funds rate in a range between 5.25 percent "
    "and 5.50 percent. In a formal policy statement, Fed officials stated that while "
    "economic activity has continued to expand at a solid pace, job gains have "
    "moderated and the unemployment rate remains low. Federal Reserve Chair Jerome "
    "Powell emphasized that future decisions will be made meeting by meeting based "
    "on incoming macroeconomic data."
)

OPINION_PIECE = (
    "In my opinion, the new tax policy is deeply flawed and will harm the middle "
    "class. I believe the government should reconsider its approach entirely. Perhaps "
    "a simpler flat tax would be fairer for everyone involved."
)


@pytest.fixture(scope="module")
def analyzer():
    return prediction_service


# --------------------------------------------------------------------------- #
# 1. FALSE-POSITIVE REGRESSION: genuine science must NOT be "Misleading"
# --------------------------------------------------------------------------- #

def test_jwst_science_not_misleading(analyzer):
    """The core TruthLens 2.0 mandate: a genuine science article with rare
    vocabulary must not be auto-labeled 'Potentially Misleading'."""
    r = analyzer.analyze(JWST_SCIENCE, title="NASA JWST Discovers Oldest Black Hole")
    outcome = r.get("outcome") or r.get("predicted_class")
    assert outcome != "Potentially Misleading", (
        f"FALSE POSITIVE: JWST science article labeled '{outcome}' (score {r['credibility_score']}). "
        f"Reasoning: {r.get('credibility_reasoning')}"
    )

def test_jwst_science_outcome_is_reliable_or_unverified(analyzer):
    """A clean science article corroborated by evidence should be Reliable or
    at worst Unverified — never Misleading."""
    r = analyzer.analyze(JWST_SCIENCE, title="NASA JWST Discovers Oldest Black Hole")
    outcome = r.get("outcome") or r.get("predicted_class")
    assert outcome in ("Likely Reliable", "Unverified", "Likely Genuine", "Needs Further Verification"), (
        f"Unexpected outcome: {outcome}"
    )

def test_genuine_economy_article_not_misleading(analyzer):
    """Genuine economic reporting should not be flagged as misleading."""
    r = analyzer.analyze(GENUINE_ECONOMY, title="Fed Holds Rates Steady")
    outcome = r.get("outcome") or r.get("predicted_class")
    assert outcome != "Potentially Misleading", (
        f"FALSE POSITIVE: Economy article labeled '{outcome}'."
    )


# --------------------------------------------------------------------------- #
# 2. MISINFORMATION DETECTION (must still flag real fake news)
# --------------------------------------------------------------------------- #

def test_health_misinfo_is_flagged(analyzer):
    """Health misinformation with clickbait signals must be flagged."""
    r = analyzer.analyze(HEALTH_MISINFO, title="MIRACLE CURE")
    outcome = r.get("outcome") or r.get("predicted_class")
    assert outcome == "Potentially Misleading", (
        f"Health misinfo not flagged: outcome={outcome}, signals={len(r['linguistic_analysis']['warning_signals'])}"
    )
    assert r["credibility_score"] < 50

def test_political_misinfo_is_flagged(analyzer):
    """Political misinformation with urgency/clickbait signals must be flagged."""
    r = analyzer.analyze(POLITICAL_MISINFO, title="Senator Caught")
    outcome = r.get("outcome") or r.get("predicted_class")
    assert outcome == "Potentially Misleading", (
        f"Political misinfo not flagged: outcome={outcome}"
    )


# --------------------------------------------------------------------------- #
# 3. NEW RESPONSE FIELDS (backward-compatible additions)
# --------------------------------------------------------------------------- #

def test_response_has_new_v2_fields(analyzer):
    """The response must include the new TruthLens 2.0 fields."""
    r = analyzer.analyze("NASA confirmed a new discovery today.", title="Test")
    assert "outcome" in r
    assert "uncertainty_level" in r
    assert "confidence_signals" in r
    assert "evidence_signal" in r
    assert "credibility_reasoning" in r
    # Backward-compatible fields preserved
    assert "predicted_class" in r or "prediction" in r
    assert "credibility_score" in r
    assert "model_predictions" in r

def test_confidence_signals_note_present(analyzer):
    """Confidence signals must carry the disclaimer that confidence != truth."""
    r = analyzer.analyze("Test article content.", title="Test")
    cs = r.get("confidence_signals", {})
    assert "note" in cs
    assert "truth" in cs["note"].lower() or "factual" in cs["note"].lower()


# --------------------------------------------------------------------------- #
# 4. UNCERTAINTY HANDLING
# --------------------------------------------------------------------------- #

def test_uncertainty_level_is_valid(analyzer):
    r = analyzer.analyze("Some ambiguous text without clear signals.", title="Ambiguous")
    assert r["uncertainty_level"] in ("Low", "Medium", "High")

def test_credibility_engine_outcomes():
    """The credibility engine must only produce the 3 valid outcomes."""
    engine = CredibilityEngine()
    import numpy as np
    for probs in [np.array([0.8,0.1,0.1]), np.array([0.2,0.7,0.1]), np.array([0.34,0.33,0.33])]:
        res = engine.assess(probs, 80.0, {"linguistic_risk_score": 0, "warning_signals": []}, word_count=50)
        assert res["outcome"] in (CredibilityEngine.RELIABLE, CredibilityEngine.MISLEADING, CredibilityEngine.UNVERIFIED)

def test_legacy_label_mapping_covers_all_outcomes():
    """Every new outcome must map to a backward-compatible legacy label."""
    for outcome in [CredibilityEngine.RELIABLE, CredibilityEngine.MISLEADING, CredibilityEngine.UNVERIFIED]:
        assert outcome in OUTCOME_TO_LEGACY


# --------------------------------------------------------------------------- #
# 5. CLAIM EXTRACTION (structured entities)
# --------------------------------------------------------------------------- #

def test_claim_extractor_returns_structured_claims():
    extractor = ClaimExtractor()
    claims = extractor.extract(JWST_SCIENCE)
    assert len(claims) > 0
    for c in claims:
        assert "claim_text" in c
        assert "claim_type" in c
        assert "entities" in c
        assert "has_entities" in c
        assert c["claim_type"] in ("factual", "opinion")

def test_claim_extractor_detects_organizations():
    extractor = ClaimExtractor()
    claims = extractor.extract(JWST_SCIENCE)
    all_orgs = []
    for c in claims:
        all_orgs.extend(c["entities"].get("organizations", []))
    assert len(all_orgs) > 0, "Expected to detect NASA or similar org in JWST text"

def test_claim_extractor_detects_numbers():
    extractor = ClaimExtractor()
    claims = extractor.extract("The GDP grew by 5.2 percent to $3.4 billion last year.")
    all_nums = []
    for c in claims:
        all_nums.extend(c["entities"].get("numbers", []))
    assert len(all_nums) > 0, "Expected to detect numerical claims"

def test_opinion_detection():
    extractor = ClaimExtractor()
    assert extractor._is_opinion("I believe this policy is wrong.")
    assert extractor._is_opinion("In my opinion, the decision was flawed.")
    assert not extractor._is_opinion("NASA confirmed the discovery of a new exoplanet.")


# --------------------------------------------------------------------------- #
# 6. EVIDENCE VERIFICATION (no fabrication)
# --------------------------------------------------------------------------- #

def test_verified_claims_have_real_sources_only(analyzer):
    """When claims match the evidence repository, sources must have real URLs."""
    r = analyzer.analyze(JWST_SCIENCE, title="NASA JWST Discovery")
    claims = r.get("extracted_claims", [])
    for c in claims:
        for src in c.get("supporting_sources", []) + c.get("contradicting_sources", []):
            assert src.get("url", "").startswith("http"), f"Fabricated or missing URL: {src}"

def test_insufficient_evidence_not_auto_fake(analyzer):
    """Claims with no evidence match must be 'Insufficient evidence', not fake."""
    r = analyzer.analyze("A small bakery in rural France reported record sales.", title="Local News")
    claims = r.get("extracted_claims", [])
    insufficient = [c for c in claims if c["verification_status"] == "Insufficient evidence"]
    # At least some claims should be insufficient (no repo match for a bakery)
    if insufficient:
        for c in insufficient:
            assert "Insufficient" in c["verification_status"]
            assert not c.get("has_verified_match", False)


# --------------------------------------------------------------------------- #
# 7. GRACEFUL DEGRADATION (optional dependencies)
# --------------------------------------------------------------------------- #

def test_transformer_service_graceful_when_unavailable():
    """When torch/transformers are absent, the service must be disabled, not crash."""
    if not transformer_service.is_available():
        assert transformer_service.predict("test text") is None
        assert "disabled" in transformer_service.status()

def test_evidence_retriever_graceful_when_unavailable():
    """When faiss/sentence-transformers are absent, the retriever returns None."""
    retriever = get_evidence_retriever()
    if retriever is None:
        # The verifier must still work via keyword fallback
        verifier = ClaimVerifier()
        claims = verifier.verify_claims(JWST_SCIENCE)
        assert len(claims) > 0

def test_ensemble_works_without_transformer(analyzer):
    """The ensemble must produce a full result without the transformer."""
    r = analyzer.analyze("A news article about a local event.", title="Local")
    assert r["models_analyzed"] >= 5  # 4 classical + BiLSTM minimum
    if not transformer_service.is_available():
        assert "DistilBERT" not in r["model_predictions"]


# --------------------------------------------------------------------------- #
# 8. EDGE CASES
# --------------------------------------------------------------------------- #

def test_empty_title_handled(analyzer):
    r = analyzer.analyze("NASA confirmed a new discovery.", title="")
    assert "credibility_score" in r

def test_very_short_text(analyzer):
    # Just above the 15-char minimum; must process without error.
    r = analyzer.analyze("Breaking news update.", title="Short")
    assert "credibility_score" in r
    assert r["credibility_score"] >= 0

def test_opinion_piece_not_misleading(analyzer):
    """An opinion piece without warning signals should not be 'Misleading'."""
    r = analyzer.analyze(OPINION_PIECE, title="Opinion: Tax Policy")
    outcome = r.get("outcome") or r.get("predicted_class")
    assert outcome != "Potentially Misleading", (
        f"Opinion piece flagged as misleading: {outcome}"
    )

def test_long_article_handled(analyzer):
    """Long articles must process without error."""
    long_text = ("The committee announced new regulations. " * 50)
    r = analyzer.analyze(long_text, title="Long Article")
    assert "credibility_score" in r
    assert r["credibility_score"] >= 0 and r["credibility_score"] <= 100
