"""
TruthLens AI - Comprehensive Automated Test Suite
Tests text preprocessing, TF-IDF vectorization, ML models, BiLSTM, XAI saliency,
claim verification, SSRF guards, document ingestion, and Flask REST API endpoints.
"""

import os
import sys
import pytest
import numpy as np

# Ensure root paths are in sys.path
TEST_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(TEST_DIR)
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")
ML_DIR = os.path.join(PROJECT_ROOT, "ml_pipeline")

for p in [PROJECT_ROOT, BACKEND_DIR, ML_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

from ml_pipeline.preprocessing.text_cleaner import TextPreprocessor
from ml_pipeline.training.classical_models import (
    SublinearTfidfVectorizer,
    LogisticRegressionClassifier,
    MultinomialNBClassifier,
    CalibratedLinearSVMClassifier,
    compute_evaluation_metrics
)
from ml_pipeline.training.bilstm_model import BiLSTMTextClassifier
from backend.app.nlp.linguistic_analyzer import LinguisticAnalyzer
from backend.app.nlp.ai_style_detector import AIWritingStyleDetector
from backend.app.ml.xai_engine import XAIEngine
from backend.app.factcheck.verifier import ClaimVerifier
from backend.app.services.source_intelligence import is_safe_url
from backend.app.services.prediction_service import prediction_service
from backend.app import create_app

@pytest.fixture
def test_client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

# 1. Preprocessing Tests
def test_preprocessing_negation_preservation():
    preprocessor = TextPreprocessor(remove_stopwords=True)
    text = "The medication did NOT cause adverse reactions and is NOT dangerous."
    tokens = preprocessor.tokenize_and_process(text)
    assert "not" in tokens, "Negation 'not' must be preserved during preprocessing!"

def test_preprocessing_hindi_detection():
    preprocessor = TextPreprocessor()
    hindi_text = "इसरो ने चंद्रयान-3 मिशन के डेटा की पुष्टि की।"
    lang = preprocessor.detect_language(hindi_text)
    assert lang == "hi", f"Expected language 'hi' but got '{lang}'"

# 2. Vectorization & Classical ML Tests
def test_sublinear_tfidf_vectorizer():
    corpus = [
        "James Webb telescope observed distant galaxies in the early universe.",
        "Secret mind control microwave towers alter human brain frequencies.",
        "Researchers published peer-reviewed findings in clinical journals."
    ]
    vectorizer = SublinearTfidfVectorizer(ngram_range=(1, 2), max_features=50)
    X = vectorizer.fit_transform(corpus)
    assert X.shape[0] == 3
    assert X.shape[1] > 0
    # L2 norm check
    row_norm = np.linalg.norm(X[0])
    assert abs(row_norm - 1.0) < 1e-4, "Transformed rows must be L2 normalized!"

def test_calibrated_svm_probabilities():
    X = np.array([
        [1.0, 0.0, 0.2],
        [0.0, 1.0, 0.1],
        [0.5, 0.5, 0.8]
    ])
    y = np.array([0, 1, 2])
    svm = CalibratedLinearSVMClassifier(C=1.0, max_iter=20)
    svm.fit(X, y)
    probs = svm.predict_proba(X)
    assert probs.shape == (3, 3)
    row_sums = np.sum(probs, axis=1)
    assert np.allclose(row_sums, 1.0, atol=1e-3), "Calibrated probabilities must sum to 1.0!"

# 3. BiLSTM Sequence Model Test
def test_bilstm_inference():
    bilstm = BiLSTMTextClassifier(vocab_size=100, embed_dim=16, hidden_dim=8, num_classes=3, max_len=20)
    texts = ["scientific discovery in astrophysics", "secret conspiracy viral bombshell"]
    bilstm.fit(texts, np.array([0, 1]), epochs=2, batch_size=2)
    probs = bilstm.predict_proba(texts)
    assert probs.shape == (2, 3)
    assert np.allclose(np.sum(probs, axis=1), 1.0, atol=1e-3)

# 4. Linguistic Analyzer Tests
def test_linguistic_clickbait_detection():
    analyzer = LinguisticAnalyzer()
    clickbait_text = "BOMBSHELL REVELATION!! Whistleblower exposes SHOCKING MIRACLE secret doctors don't want you to know!!!"
    res = analyzer.analyze(clickbait_text, title="SHOCKING SECRET")
    assert res["linguistic_risk_score"] > 35, "Clickbait text should trigger high linguistic risk score."
    assert res["exclamation_count"] >= 3
    assert len(res["warning_signals"]) > 0

# 5. XAI Engine Tests
def test_xai_feature_attribution():
    xai = XAIEngine()
    text = "BOMBSHELL secret leaked by whistleblower regarding miracle cure."
    res = xai.explain(text, predicted_class=1)
    assert "top_misleading_features" in res
    assert "token_highlights" in res
    assert len(res["token_highlights"]) > 0

# 6. Claim Extraction & Verification Tests
def test_claim_verification_matching():
    verifier = ClaimVerifier()
    text = "The James Webb Space Telescope discovered the oldest confirmed black hole in galaxy CEERS 1019."
    claims = verifier.verify_claims(text)
    assert len(claims) > 0
    assert claims[0]["verification_status"] == "Supported by available evidence"
    assert len(claims[0]["supporting_sources"]) > 0

# 7. SSRF Security Guard Tests
def test_ssrf_blocks_private_ips():
    bad_urls = [
        "http://127.0.0.1/admin",
        "http://localhost:8080/secret",
        "http://169.254.169.254/latest/meta-data/",
        "http://192.168.1.1/router"
    ]
    for url in bad_urls:
        safe, msg = is_safe_url(url)
        assert not safe, f"SSRF Guard failed to block malicious URL: {url}"

def test_ssrf_allows_public_https():
    safe, msg = is_safe_url("https://www.reuters.com")
    assert safe, f"SSRF Guard incorrectly blocked valid public site: {msg}"

# 8. Flask REST API Integration Tests
def test_api_health(test_client):
    res = test_client.get("/api/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "operational"

def test_api_dashboard_stats(test_client):
    res = test_client.get("/api/dashboard/stats")
    assert res.status_code == 200
    data = res.get_json()
    assert "total_articles_analyzed" in data
    assert "credibility_distribution" in data

def test_api_models_performance(test_client):
    res = test_client.get("/api/models/performance")
    assert res.status_code == 200
    data = res.get_json()
    assert "models" in data
    assert len(data["models"]) >= 4

def test_api_analyze_text(test_client):
    payload = {
        "title": "NASA Astronomy Release",
        "text": "Astronomers published peer-reviewed findings in The Astrophysical Journal confirming black hole accretion."
    }
    res = test_client.post("/api/analyze/text", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert "predicted_class" in data
    assert "credibility_score" in data
    assert "model_predictions" in data
    assert "explanation" in data
