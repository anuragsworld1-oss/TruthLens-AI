"""
TruthLens AI 2.0 - RAG Evidence Retrieval (OPTIONAL)
Retrieval-augmented evidence matching using sentence-transformer embeddings and
FAISS vector similarity search over the VERIFIED_EVIDENCE_REPOSITORY.

When `sentence-transformers` / `faiss` are NOT installed, the retriever is
disabled and the ClaimVerifier falls back to keyword matching against the
repository (current behaviour). This keeps the app fully functional on a
minimal install.

IMPORTANT: Only the curated, cited VERIFIED_EVIDENCE_REPOSITORY is indexed.
No scraped or fabricated documents are ever introduced. When similarity is
below threshold, the claim is classified "Insufficient evidence" -- never
auto-flagged as fake.
"""

import os
import logging

logger = logging.getLogger(__name__)

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
INDEX_DIR = os.path.join(_ROOT, "ml_pipeline", "saved_models", "evidence_index")
INDEX_PATH = os.path.join(INDEX_DIR, "evidence.faiss")
META_PATH = os.path.join(INDEX_DIR, "evidence_meta.json")

# Similarity threshold (cosine). Below this => "Insufficient evidence".
SIMILARITY_THRESHOLD = 0.55


def _check_deps():
    try:
        import faiss  # noqa: F401
        import sentence_transformers  # noqa: F401
        return True
    except Exception:
        return False


class EvidenceRetriever:
    """FAISS + sentence-transformer evidence retriever with graceful fallback."""

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
        self._model = None
        self._index = None
        self._meta = None
        self._load_attempted = False

    def is_available(self):
        if self._available is not None:
            return self._available
        if not _check_deps():
            self._available = False
            return False
        self._available = os.path.exists(INDEX_PATH) and os.path.exists(META_PATH)
        return self._available

    def _load(self):
        if self._load_attempted:
            return
        self._load_attempted = True
        if not self.is_available():
            return
        try:
            import faiss
            import json
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(os.path.join(INDEX_DIR, "st_model"))
            self._index = faiss.read_index(INDEX_PATH)
            with open(META_PATH, "r") as f:
                self._meta = json.load(f)
            logger.info("[EvidenceRetriever] FAISS index loaded (%d entries).", len(self._meta.get("entries", [])))
        except Exception as e:
            logger.warning("[EvidenceRetriever] Failed to load index: %s", e)
            self._available = False

    def retrieve(self, claim_text, top_k=3):
        """Returns a list of evidence dicts with similarity scores, or []."""
        if not self.is_available():
            return []
        self._load()
        if self._index is None or self._model is None:
            return []
        try:
            import faiss
            import numpy as np
            query_vec = self._model.encode([claim_text], normalize_embeddings=True).astype("float32")
            k = min(top_k, self._index.ntotal)
            if k == 0:
                return []
            scores, indices = self._index.search(query_vec, k)
            entries = self._meta.get("entries", [])
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx < 0 or idx >= len(entries):
                    continue
                sim = float(score)  # cosine similarity (normalized vectors)
                if sim < SIMILARITY_THRESHOLD:
                    continue
                entry = entries[idx]
                results.append({
                    "score": round(sim, 4),
                    "stance": entry.get("stance", "neutral"),
                    "evidence_summary": entry.get("evidence_summary", ""),
                    "claim_summary": entry.get("claim_summary", ""),
                    "source": entry.get("source", {}),
                })
            return results
        except Exception as e:
            logger.warning("[EvidenceRetriever] Retrieval failed: %s", e)
            return []

    def status(self):
        if not _check_deps():
            return "disabled (sentence-transformers/faiss not installed)"
        if not (os.path.exists(INDEX_PATH) and os.path.exists(META_PATH)):
            return "disabled (no index; run ml_pipeline/training/build_evidence_index.py)"
        return "enabled"


def get_evidence_retriever():
    """Returns the singleton EvidenceRetriever, or None if unavailable."""
    r = EvidenceRetriever()
    return r if r.is_available() else None
