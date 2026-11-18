"""
TruthLens AI 2.0 - Build FAISS Evidence Index (OPTIONAL)
Embeds every evidence item in the VERIFIED_EVIDENCE_REPOSITORY with a
sentence-transformer (all-MiniLM-L6-v2) and stores a FAISS index + metadata.

Requires:  pip install sentence-transformers faiss-cpu

If deps are not installed, prints a clear message and exits without error;
the ClaimVerifier will fall back to keyword matching.
"""

import os
import sys
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

SAVED_MODELS_DIR = os.path.join(BASE_DIR, "saved_models")
INDEX_DIR = os.path.join(SAVED_MODELS_DIR, "evidence_index")
INDEX_PATH = os.path.join(INDEX_DIR, "evidence.faiss")
META_PATH = os.path.join(INDEX_DIR, "evidence_meta.json")
ST_MODEL_DIR = os.path.join(INDEX_DIR, "st_model")

MODEL_NAME = "all-MiniLM-L6-v2"


def _check_deps():
    try:
        import faiss  # noqa
        import sentence_transformers  # noqa
        return True
    except Exception as e:
        print("\n[Evidence Index] SKIPPED - optional dependencies not installed.")
        print(f"  Reason: {e}")
        print("  To enable RAG evidence retrieval, install:")
        print("    pip install sentence-transformers faiss-cpu")
        print("  The ClaimVerifier will use keyword matching as fallback.")
        return False


def build_evidence_index():
    if not _check_deps():
        return None

    import faiss
    import numpy as np
    from sentence_transformers import SentenceTransformer

    # Import the verified repository from the backend fact-check module.
    sys.path.insert(0, os.path.join(BASE_DIR, "..", "backend"))
    from app.factcheck.verifier import VERIFIED_EVIDENCE_REPOSITORY

    print("\n" + "=" * 64)
    print("TruthLens AI 2.0 - Building FAISS Evidence Index")
    print("=" * 64)
    print(f"[*] Evidence repository entries: {len(VERIFIED_EVIDENCE_REPOSITORY)}")

    os.makedirs(INDEX_DIR, exist_ok=True)

    # Load + save the sentence-transformer model locally (so it is not
    # re-downloaded at inference time).
    print(f"[*] Loading sentence-transformer: {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME)
    model.save(ST_MODEL_DIR)

    # Build embedding corpus: each evidence entry contributes one document
    # combining its claim_summary + evidence_summary. We also record the
    # primary source for citation.
    texts = []
    entries = []
    for ev in VERIFIED_EVIDENCE_REPOSITORY:
        doc = (ev.get("claim_summary", "") + " " + ev.get("evidence_summary", "")).strip()
        texts.append(doc)
        # Use the first source's stance as the entry stance, or derive from status.
        sources = ev.get("sources", [])
        stance = sources[0].get("stance", "neutral") if sources else (
            "support" if "Supported" in ev.get("status", "") else
            "contradict" if "Contradicted" in ev.get("status", "") else "neutral"
        )
        source = sources[0] if sources else {}
        entries.append({
            "claim_summary": ev.get("claim_summary", ""),
            "evidence_summary": ev.get("evidence_summary", ""),
            "stance": stance,
            "source": source,
        })

    print(f"[*] Embedding {len(texts)} evidence documents...")
    embeddings = model.encode(texts, normalize_embeddings=True).astype("float32")

    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)  # inner product = cosine for normalized vectors
    index.add(embeddings)

    faiss.write_index(index, INDEX_PATH)
    with open(META_PATH, "w") as f:
        json.dump({"entries": entries, "dimension": dim, "model": MODEL_NAME}, f, indent=2)

    print(f"[+] FAISS index saved: {INDEX_PATH} ({index.ntotal} vectors, dim={dim})")
    print(f"[+] Metadata saved: {META_PATH}")
    print(f"[+] ST model saved: {ST_MODEL_DIR}")
    return index.ntotal


if __name__ == "__main__":
    build_evidence_index()
