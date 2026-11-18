"""
TruthLens AI 2.0 - Optional DistilBERT Transformer Service
Provides a 6th ensemble vote when `transformers` + `torch` are installed and a
fine-tuned model artifact exists. When they are absent, the service is disabled
and the prediction pipeline falls back to the classical + BiLSTM ensemble
without any error. This keeps the app fully runnable on a minimal Windows
install while enabling full transformer power when the optional deps are present.

The model is loaded ONCE and cached as a module-level singleton; it is never
downloaded on every prediction.
"""

import os
import logging

logger = logging.getLogger(__name__)

# Project root (ml_pipeline/saved_models is relative to project root).
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
MODEL_DIR = os.path.join(_ROOT, "ml_pipeline", "saved_models", "distilbert_fake_news")
META_PATH = os.path.join(_ROOT, "ml_pipeline", "saved_models", "distilbert_meta.json")

CLASS_NAMES = ["Likely Genuine", "Potentially Misleading", "Needs Further Verification"]


def _check_dependencies():
    """Returns (transformers_module, torch_module) or (None, None) if unavailable."""
    try:
        import torch  # noqa: F401
        from transformers import AutoTokenizer, AutoModelForSequenceClassification  # noqa: F401
        import transformers
        return transformers, torch
    except Exception:
        return None, None


class TransformerService:
    """Lazy-loading, cached DistilBERT inference wrapper with graceful fallback."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        self._initialized = True
        self._available = None
        self._tokenizer = None
        self._model = None
        self._torch = None
        self._device = None
        self._meta = None
        self._load_attempted = False

    def is_available(self):
        """True only if deps are importable AND a trained artifact exists."""
        if self._available is not None:
            return self._available
        transformers, torch = _check_dependencies()
        if transformers is None or torch is None:
            self._available = False
            return False
        if not os.path.isdir(MODEL_DIR):
            self._available = False
            return False
        # Check for model weights
        has_weights = (
            os.path.exists(os.path.join(MODEL_DIR, "pytorch_model.bin"))
            or os.path.exists(os.path.join(MODEL_DIR, "model.safetensors"))
        )
        self._available = has_weights
        return self._available

    def _load(self):
        """Loads the model + tokenizer once (cached). Safe to call repeatedly."""
        if self._load_attempted:
            return
        self._load_attempted = True
        if not self.is_available():
            return
        try:
            import torch
            from transformers import AutoTokenizer, AutoModelForSequenceClassification
            self._torch = torch
            self._device = "cuda" if torch.cuda.is_available() else "cpu"
            self._tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
            self._model = AutoModelForSequenceClassification.from_pretrained(MODEL_DIR)
            self._model.to(self._device)
            self._model.eval()
            # Load metadata (real metrics) if present.
            if os.path.exists(META_PATH):
                import json
                with open(META_PATH, "r") as f:
                    self._meta = json.load(f)
            logger.info("[TransformerService] DistilBERT loaded on %s.", self._device)
        except Exception as e:
            logger.warning("[TransformerService] Failed to load DistilBERT: %s", e)
            self._available = False
            self._model = None
            self._tokenizer = None

    def predict(self, text, max_length=512):
        """
        Returns dict {prediction, probabilities, confidence} or None if disabled.
        Never raises; returns None on any failure so the ensemble can continue.
        """
        if not self.is_available():
            return None
        self._load()
        if self._model is None or self._tokenizer is None:
            return None
        try:
            torch = self._torch
            inputs = self._tokenizer(
                text, return_tensors="pt", truncation=True,
                max_length=max_length, padding=True
            )
            inputs = {k: v.to(self._device) for k, v in inputs.items()}
            with torch.no_grad():
                logits = self._model(**inputs).logits
                probs = torch.softmax(logits, dim=-1)[0].cpu().numpy()
            pred_id = int(probs.argmax())
            return {
                "prediction": CLASS_NAMES[pred_id],
                "probabilities": [float(p) for p in probs],
                "confidence": round(float(probs[pred_id]) * 100, 1),
            }
        except Exception as e:
            logger.warning("[TransformerService] Inference failed: %s", e)
            return None

    def status(self):
        """Human-readable availability status for logging/UI."""
        transformers, torch = _check_dependencies()
        if transformers is None or torch is None:
            return "disabled (transformers/torch not installed)"
        if not os.path.isdir(MODEL_DIR) or not (
            os.path.exists(os.path.join(MODEL_DIR, "pytorch_model.bin"))
            or os.path.exists(os.path.join(MODEL_DIR, "model.safetensors"))
        ):
            return "disabled (no fine-tuned model; run ml_pipeline/training/train_transformer.py)"
        return f"enabled (device={self._device or 'cpu'})"

    def meta(self):
        """Returns the real training metrics dict, or None."""
        if self._meta is None and os.path.exists(META_PATH):
            try:
                import json
                with open(META_PATH, "r") as f:
                    self._meta = json.load(f)
            except Exception:
                self._meta = None
        return self._meta


# Module-level singleton used by prediction_service.
transformer_service = TransformerService()
