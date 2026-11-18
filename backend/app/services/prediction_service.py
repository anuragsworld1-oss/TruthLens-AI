"""
TruthLens AI - Centralized Prediction & Credibility Synthesizer
Orchestrates:
1. Input validation & language detection (EN / HI)
2. NLP text preprocessing (negation preservation, lemmatization)
3. Model inference & consensus across 5 models:
   - Logistic Regression
   - Multinomial Naive Bayes
   - Calibrated Linear SVM
   - Random Forest
   - Bidirectional LSTM
4. Consensus agreement/disagreement calculation
5. 0-100 Credibility Score mapping with strict categories:
   - Likely Genuine (Score >= 70)
   - Potentially Misleading (Score 40-69)
   - Needs Further Verification (Score < 40 or high model disagreement)
6. Linguistic warning signals
7. Explainable AI (XAI) feature saliency map
8. AI writing style assessment
9. Claim extraction and evidence matching
"""

import os
import sys
import json
import joblib
import numpy as np

# Ensure root paths are in sys.path
SERVICES_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.dirname(SERVICES_DIR)
BACKEND_DIR = os.path.dirname(APP_DIR)
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)
ML_PIPELINE_DIR = os.path.join(PROJECT_ROOT, "ml_pipeline")

for p in [APP_DIR, BACKEND_DIR, PROJECT_ROOT, ML_PIPELINE_DIR]:
    if p not in sys.path:
        sys.path.append(p)

from ml_pipeline.preprocessing.text_cleaner import TextPreprocessor
from app.nlp.linguistic_analyzer import LinguisticAnalyzer
from app.nlp.ai_style_detector import AIWritingStyleDetector
from app.ml.xai_engine import XAIEngine
from app.factcheck.verifier import ClaimVerifier
from app.services.credibility_engine import CredibilityEngine, OUTCOME_TO_LEGACY
from app.services.transformer_service import transformer_service
from app.services.explainability import get_explainability_service

SAVED_MODELS_DIR = os.path.join(ML_PIPELINE_DIR, "saved_models")

CLASS_LABELS = {
    0: "Likely Genuine",
    1: "Potentially Misleading",
    2: "Needs Further Verification"
}

class PredictionService:
    def __init__(self):
        self.preprocessor = TextPreprocessor(remove_stopwords=False, lemmatize=True)
        self.linguistic_analyzer = LinguisticAnalyzer()
        self.ai_style_detector = AIWritingStyleDetector()
        self.claim_verifier = ClaimVerifier()
        self.credibility_engine = CredibilityEngine()
        
        self.tfidf = None
        self.models = {}
        self.bilstm = None
        self.xai_engine = None
        self.load_models()

    def load_models(self):
        """Loads all persisted model weights and initialises XAI engine."""
        try:
            tfidf_path = os.path.join(SAVED_MODELS_DIR, "tfidf_vectorizer.joblib")
            if os.path.exists(tfidf_path):
                self.tfidf = joblib.load(tfidf_path)

            classical_names = [
                ("Logistic Regression", "logistic_regression.joblib"),
                ("Multinomial Naive Bayes", "multinomial_naive_bayes.joblib"),
                ("Calibrated Linear SVM", "calibrated_linear_svm.joblib"),
                ("Random Forest", "random_forest.joblib")
            ]

            for display_name, file_name in classical_names:
                fpath = os.path.join(SAVED_MODELS_DIR, file_name)
                if os.path.exists(fpath):
                    self.models[display_name] = joblib.load(fpath)

            # Load BiLSTM
            bilstm_path = os.path.join(SAVED_MODELS_DIR, "bidirectional_lstm.joblib")
            if os.path.exists(bilstm_path):
                from training.bilstm_model import BiLSTMTextClassifier
                self.bilstm = BiLSTMTextClassifier.load(bilstm_path)

            # Initialize XAI engine with Logistic Regression feature weights
            lr_model = self.models.get("Logistic Regression")
            self.xai_engine = XAIEngine(tfidf_vectorizer=self.tfidf, logistic_model=lr_model)
            print(f"[PredictionService] Successfully loaded {len(self.models)} classical models, BiLSTM, and TF-IDF.")
        except Exception as e:
            print(f"[PredictionService] Warning during model loading: {e}")

    def analyze(self, text: str, title: str = "", source_url: str = "", language: str = None) -> dict:
        """
        Executes end-to-end credibility analysis on the provided article text.
        """
        if not text or len(text.strip()) < 15:
            raise ValueError("Article text is too short for credible analysis. Please provide at least 15 characters.")

        # 1. Language Detection & Preprocessing
        detected_lang = language or self.preprocessor.detect_language(title + " " + text)
        clean_text = self.preprocessor.transform_to_string(title + " " + text, lang=detected_lang)

        # 2. Linguistic and Stylistic Analysis
        linguistic_res = self.linguistic_analyzer.analyze(text, title=title)
        ai_style_res = self.ai_style_detector.assess_style(text)

        # 3. Model Predictions & Probability Calibration
        model_predictions = {}
        predicted_classes = []
        all_class_probs = []

        if self.tfidf and self.models:
            X_vec = self.tfidf.transform([clean_text])

            for name, model in self.models.items():
                probs = model.predict_proba(X_vec)[0]  # shape: (3,)
                pred_class = int(np.argmax(probs))
                confidence = float(probs[pred_class])
                predicted_classes.append(pred_class)
                all_class_probs.append(probs)

                model_predictions[name] = {
                    "prediction": CLASS_LABELS[pred_class],
                    "predicted_class_id": pred_class,
                    "confidence": round(confidence * 100, 1),
                    "probabilities": {
                        "Likely Genuine": round(float(probs[0]) * 100, 1),
                        "Potentially Misleading": round(float(probs[1]) * 100, 1),
                        "Needs Further Verification": round(float(probs[2]) * 100, 1)
                    }
                }

        # BiLSTM Inference
        if self.bilstm:
            bilstm_probs = self.bilstm.predict_proba([clean_text])[0]
            bilstm_pred_class = int(np.argmax(bilstm_probs))
            predicted_classes.append(bilstm_pred_class)
            all_class_probs.append(bilstm_probs)

            model_predictions["Bidirectional LSTM"] = {
                "prediction": CLASS_LABELS[bilstm_pred_class],
                "predicted_class_id": bilstm_pred_class,
                "confidence": round(float(bilstm_probs[bilstm_pred_class]) * 100, 1),
                "probabilities": {
                    "Likely Genuine": round(float(bilstm_probs[0]) * 100, 1),
                    "Potentially Misleading": round(float(bilstm_probs[1]) * 100, 1),
                    "Needs Further Verification": round(float(bilstm_probs[2]) * 100, 1)
                }
            }

        # Optional DistilBERT vote (only when transformers+torch installed and a
        # fine-tuned artifact exists). If unavailable, the ensemble continues
        # with the 5 classical/BiLSTM models — no vote is ever invented.
        tf_pred = transformer_service.predict(clean_text)
        if tf_pred is not None:
            tf_probs = np.array(tf_pred["probabilities"])
            tf_pred_class = int(np.argmax(tf_probs))
            predicted_classes.append(tf_pred_class)
            all_class_probs.append(tf_probs)
            model_predictions["DistilBERT"] = {
                "prediction": tf_pred["prediction"],
                "predicted_class_id": tf_pred_class,
                "confidence": tf_pred["confidence"],
                "probabilities": {
                    "Likely Genuine": round(float(tf_probs[0]) * 100, 1),
                    "Potentially Misleading": round(float(tf_probs[1]) * 100, 1),
                    "Needs Further Verification": round(float(tf_probs[2]) * 100, 1)
                }
            }

        # 4. Consensus & Agreement Engine
        if all_class_probs:
            mean_probs = np.mean(all_class_probs, axis=0)
            consensus_class_id = int(np.argmax(mean_probs))
        else:
            consensus_class_id = 0
            mean_probs = np.array([0.7, 0.2, 0.1])

        # Model Agreement calculation
        unique_votes = [m["predicted_class_id"] for m in model_predictions.values() if "predicted_class_id" in m]
        majority_votes = unique_votes.count(consensus_class_id)
        agreement_ratio = round((majority_votes / max(1, len(unique_votes))) * 100, 1)

        # 5. Calibrated Credibility Assessment (TruthLens 2.0)
        # The CredibilityEngine separates model confidence from factual
        # verification, applies temperature shrinkage (so rare-vocabulary
        # specialist text is not punished for being out-of-distribution), and
        # surfaces explicit uncertainty. Model confidence is NOT treated as
        # the probability that the article is factually true.
        word_count = linguistic_res.get("word_count", 0)
        credibility = self.credibility_engine.assess(
            mean_probs=mean_probs,
            agreement_ratio=agreement_ratio,
            linguistic_res=linguistic_res,
            word_count=word_count,
            evidence_summary=None,  # evidence fused below after claim verification
            consensus_class_id=consensus_class_id,
        )
        final_credibility_score = credibility["credibility_score"]
        outcome = credibility["outcome"]
        uncertainty_level = credibility["uncertainty_level"]
        # Backward-compatible legacy class label for existing API consumers.
        final_class = OUTCOME_TO_LEGACY.get(outcome, "Needs Further Verification")

        # 7. Claim Extraction & Evidence-Based Verification
        verified_claims = self.claim_verifier.verify_claims(title + "\n" + text)

        # 7b. Re-assess credibility now that evidence is available, fusing the
        # verification results. This keeps factual verification separate from
        # model confidence while letting corroborating/contradicting evidence
        # move the final score within bounded limits.
        evidence_summary = {"claims": verified_claims} if verified_claims else None
        credibility = self.credibility_engine.assess(
            mean_probs=mean_probs,
            agreement_ratio=agreement_ratio,
            linguistic_res=linguistic_res,
            word_count=word_count,
            evidence_summary=evidence_summary,
            consensus_class_id=consensus_class_id,
        )
        final_credibility_score = credibility["credibility_score"]
        outcome = credibility["outcome"]
        uncertainty_level = credibility["uncertainty_level"]
        final_class = OUTCOME_TO_LEGACY.get(outcome, "Needs Further Verification")

        # 6. Explainable AI Feature Attribution (with enriched sentence reasons
        #    tied to evidence outcomes). Runs after claim verification so that
        #    sentence reasons can cite supporting/contradicting evidence.
        if self.xai_engine:
            _xai_svc = get_explainability_service(self.xai_engine)
            xai_res = _xai_svc.explain(text, predicted_class=consensus_class_id,
                                       evidence_summary=evidence_summary)
        else:
            xai_res = {}

        # 8. Recommended Next Steps & Limitations
        recommended_actions = []
        if final_class == "Likely Genuine":
            recommended_actions = [
                "Verify publication date and primary documents for latest updates.",
                "Cross-reference specific statistics with original institutional releases.",
                "Check for potential regional contextual nuances."
            ]
        elif final_class == "Potentially Misleading":
            recommended_actions = [
                "Exercise caution before sharing on social media platforms.",
                "Seek independent confirmation from accredited wire services (e.g. Reuters, AP).",
                "Inspect the listed warning signals and unsubstantiated claims."
            ]
        else:
            recommended_actions = [
                "Hold judgment pending verification from primary official authorities.",
                "Look for follow-up statements from verified fact-checkers.",
                "Review contradicting evidence sources listed below."
            ]

        return {
            "prediction": final_class,
            "predicted_class": final_class,
            "outcome": outcome,
            "uncertainty_level": uncertainty_level,
            "credibility_score": round(final_credibility_score, 1),
            "consensus_confidence": round(float(mean_probs[consensus_class_id]) * 100, 1),
            "model_agreement_percentage": agreement_ratio,
            "confidence_signals": credibility["confidence_signals"],
            "evidence_signal": credibility["evidence_signal"],
            "credibility_reasoning": credibility["reasoning"],
            "language": detected_lang,
            "models_analyzed": len(model_predictions),
            "model_predictions": model_predictions,
            "linguistic_analysis": linguistic_res,
            "ai_writing_style": ai_style_res,
            "explainable_ai": xai_res,
            "extracted_claims": verified_claims,
            "recommended_actions": recommended_actions,
            "limitations_disclaimer": "TruthLens AI produces probabilistic assessments using machine learning and documented evidence indexes. Model confidence is not a measure of factual truth. It does not replace independent human judgment or establish absolute truth.",
            "source_url": source_url
        }

# Global Singleton Instance
prediction_service = PredictionService()
