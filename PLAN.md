<!-- PLAN STATUS: completed | UPDATED: 2026-11-18T21:13:08.044Z -->
<!-- PLAN ID: plan_mwmkygo3_1 -->
<!-- Phase 1: completed -->
<!-- Phase 2: completed -->
<!-- Phase 3: completed -->
<!-- Phase 4: completed -->
<!-- Phase 5: completed -->
<!-- Phase 6: completed -->
<!-- Phase 7: completed -->
<!-- Phase 8: completed -->

# TruthLens AI 2.0 — Intelligent Misinformation Detection Upgrade

## Context / What this resolves

The existing TruthLens AI is a working Flask + React + NumPy-ML fake-news platform (14/14 tests pass, 5 models load, frontend builds). A deep audit of the **prediction and credibility core** reveals the central weakness the user wants fixed:

- **Credibility is naive and miscalibrated.** `prediction_service.analyze()` computes `raw_credibility = prob_genuine * 100` then subtracts a linguistic penalty. Because the models are trained on a small (~90-article) benchmark, they are poorly calibrated — genuinely-sourced science articles (e.g. the JWST/CEERS 1019 release) score ~44 ("Potentially Misleading") purely because their vocabulary is rare in training. This is a **false-positive problem**: model confidence is being treated as a proxy for factual truth, which the user explicitly forbids.
- **No transformer model.** Only classical + BiLSTM, both weak on the tiny dataset.
- **Claim extraction is shallow** — regex keyword matching in `factcheck/verifier.py`, not structured entity-aware extraction.
- **No RAG/evidence retrieval.** Fact-checking matches against a small hardcoded `VERIFIED_EVIDENCE_REPOSITORY` list; no vector search, no document retrieval.
- **Explainability is keyword-saliency only** — no SHAP/LIME, no sentence-risk reasoning tied to evidence.

The user's priority order is explicit: **fix the prediction + credibility scoring FIRST, then add new models.** Special mandate: genuine scientific articles must not auto-receive low scores because their vocabulary differs from training data.

## Approach / Why this way

Three architectural principles govern this upgrade:

1. **Optional heavy dependencies, graceful degradation.** DistilBERT (`transformers`+`torch`), sentence-transformers, and FAISS are large installs (~2GB+). On a minimal Windows install the app must still run. Therefore every new heavy module is **opt-in**: `transformer_service`, `evidence_retrieval`, and embeddings load *if* the package is importable and the artifact exists, and the prediction pipeline falls back to the existing classical+BiLSTM ensemble + the existing evidence repository when they are absent. This satisfies "handle missing dependencies gracefully" and "runs locally on Windows" simultaneously, while enabling full power when deps are present.
2. **Separate model confidence from factual verification.** The redesigned `credibility_engine` keeps two signals distinct: (a) an *ML confidence* vector from the ensemble, and (b) an *evidence verification* outcome from the RAG fact-checker. The final article outcome fuses them with explicit uncertainty handling — when models disagree or evidence is insufficient, the result is "Unverified", never a forced fake verdict.
3. **No fabrication, no hardcoded metrics.** All new metrics come from a real held-out test split. The existing curated dataset is expanded with a proper train/val/test split and stratification. DistilBERT is fine-tuned and evaluated only if torch is installed; otherwise it is skipped with a logged warning, never faked.

Backward compatibility: the existing `/api/analyze/*` response shape is preserved (all current fields kept); new fields are *added* (transformer prediction, structured claims, evidence, uncertainty). Existing models and `metrics.json` are never deleted. The existing 14 tests must remain green throughout.

---

## Phase 1: Fix the credibility engine & calibration (PRIORITY — fixes false positives)

**Goal:** Stop genuine science articles from being mislabeled. Redesign scoring so model confidence and evidence are separate, with uncertainty handling.

**Files:**
- (create) `backend/app/services/credibility_engine.py` — new `CredibilityEngine`
- (modify) `backend/app/services/prediction_service.py` — delegate scoring to the new engine; keep response fields backward-compatible
- (modify) `backend/app/models/database.py` — add nullable `uncertainty_level`, `evidence_summary` columns to `AnalysisResult` + `to_dict()` (migration already exists in `__init__.py`; extend its column list)

**Steps:**
- Create `CredibilityEngine` that takes: per-model probabilities, consensus/agreement, linguistic risk, and (later) evidence outcome + transformer prob. It produces:
  - `credibility_score` (0–100)
  - `outcome` ∈ {Likely Reliable, Potentially Misleading, Unverified} (mapped from the 3 existing labels for backward compat: "Likely Genuine"→"Likely Reliable", "Needs Further Verification"→"Unverified")
  - `uncertainty_level` (Low/Medium/High) driven by model disagreement + evidence insufficiency
  - `confidence_signals` (model confidence, kept SEPARATE from factual verification)
- **Calibration fix:** instead of `prob_genuine*100`, use a *temperature-scaled* confidence and a *prior* that prevents vocabulary-rarity from dominating. Specifically: shrink extreme model probabilities toward a neutral prior when agreement is low or text is long/technical (length & lexical-diversity aware), so a rare-vocabulary science article with no linguistic warning signals and no contradicting evidence does not collapse to ~44. The linguistic penalty only applies when warning signals are actually present.
- **Uncertainty rule:** if `agreement < 60%` OR evidence is "Insufficient" AND no strong misleading signals → outcome "Unverified" with a capped mid-range score, NOT "Potentially Misleading". This directly fixes the JWST false positive.
- Wire `prediction_service.analyze()` to call `CredibilityEngine`; keep returning `predicted_class` (old name) populated from the new outcome for backward compatibility, plus the new `outcome` and `uncertainty_level`.
- Extend the SQLite auto-migration column list in `__init__.py` for the two new columns.

**Risks:** Changing scoring could shift existing test expectations — but tests only assert field *presence* and that disinfo scores <50, not exact science-article scores. Verify the JWST sample now scores ≥60 or "Unverified" rather than "Potentially Misleading". Re-run pytest after.

---

## Phase 2: Improve classical ML pipeline — preprocessing, n-grams, imbalance, hyperparams

**Goal:** Raise real model quality and produce honest, expanded metrics; fix preprocessing train/predict consistency.

**Files:**
- (modify) `ml_pipeline/preprocessing/text_cleaner.py` — consistency audit (ensure `transform_to_string` is used identically in train & predict; preserve negation; add char-ngram-friendly normalization)
- (modify) `ml_pipeline/training/classical_models.py` — add char-ngram option to `SublinearTfidfVectorizer`; expose key hyperparams (C, alpha, n_estimators) on each model
- (modify) `ml_pipeline/training/train_models.py` — proper stratified train/val/test split, class-weight/imbalance handling, hyperparameter grid search over a small grid, per-model independent evaluation, ROC-AUC (one-vs-rest) for binary-capable models, write expanded `metrics.json` with `improved` flags and old-vs-new comparison
- (modify) `ml_pipeline/datasets/dataset_loader.py` — add a `get_train_val_test_splits()` returning stratified splits; keep `get_benchmark_dataset()` intact for backward compat

**Steps:**
- Audit for data leakage: confirm the TF-IDF vectorizer is fit ONLY on train (not val/test) — it already is in train_models; verify the preprocessor is the same instance/config used by `prediction_service` (currently `remove_stopwords=False` in service vs whatever train used — make them identical and store the preprocessor config).
- Add char n-gram (3–5) TF-IDF path as an alternative feature set; grid-search word vs char vs combined per model.
- Add class-weighting to LogisticRegression/SVM and balanced priors to NB to handle the 3-class imbalance.
- Small grid search (e.g. LR C∈{0.5,1,2,4}, NB alpha∈{0.1,0.5,1}, RF n_estimators∈{80,150,250}) selected on val, reported on test.
- Compute one-vs-rest ROC-AUC where probabilities are available (LR, NB, calibrated SVM); RF AUC via vote proportions.
- Write an honest comparison block in `metrics.json`: `{"baseline": {...}, "improved": {...}}` per model. Never overwrite the old metrics without keeping a `baseline` copy.
- Do NOT delete existing `.joblib` models; overwrite only after the improved versions are validated on the test set.

**Risks:** Grid search on a ~90-article dataset is fast but results will be modest — report them honestly, do not inflate. Ensure `prediction_service` loads the new vectorizer/model format unchanged (same joblib interface). Re-run pytest.

---

## Phase 3: DistilBERT transformer model (optional, graceful)

**Goal:** Add a fine-tuned DistilBERT as a 6th model vote when torch+transformers are installed; degrade cleanly otherwise.

**Files:**
- (create) `ml_pipeline/training/train_transformer.py` — fine-tune DistilBERT on the labeled dataset, save to `ml_pipeline/saved_models/distilbert_fake_news/`
- (create) `backend/app/services/transformer_service.py` — lazy loader + inference; cached model; availability check
- (modify) `backend/app/services/prediction_service.py` — optionally add transformer vote to the ensemble (only if loaded); never invent a vote when absent
- (modify) `backend/requirements.txt` — add `transformers`, `torch` under an **optional** comment block (not forced)
- (create) `ml_pipeline/saved_models/distilbert_meta.json` — stores training metrics (real) + `available: bool`

**Steps:**
- `train_transformer.py`: load dataset, stratified split, fine-tune `distilbert-base-uncased` for 3-class classification (num_labels=3), GPU if available else CPU, save model+tokenizer locally, evaluate on held-out test, write real metrics to `distilbert_meta.json`. Skip with a clear message if torch missing.
- `transformer_service.TransformerService`: `is_available()` checks import + artifact; `predict(text)` returns `{probabilities, prediction, confidence}`; caches the loaded model as a module-level singleton; robust try/except returning `None` on failure.
- In `prediction_service`: after BiLSTM, attempt `transformer_service.predict()`; if it returns a result, add `"DistilBERT"` to `model_predictions` and include its probs in the ensemble mean; if unavailable, log once and continue (ensemble uses 5 models as before).
- Never download on every prediction — load once, reuse.

**Risks:** Torch install is large and may be slow on Windows; this is why it's optional. If the user hasn't installed torch, the app runs with 5 models and logs `[TransformerService] Disabled (transformers/torch not installed)`. Fine-tuning on ~90 articles will overfit — report real metrics honestly and note the limitation. Must not block app startup if torch absent.

---

## Phase 4: Intelligent claim extraction

**Goal:** Replace shallow regex claim matching with structured, entity-aware claim extraction.

**Files:**
- (create) `backend/app/services/claim_extraction.py` — `ClaimExtractor`
- (modify) `backend/app/factcheck/verifier.py` — consume structured claims instead of internal regex; keep the evidence repository
- (modify) `backend/app/services/prediction_service.py` — call `ClaimExtractor` then pass claims to the fact-checker

**Steps:**
- `ClaimExtractor` identifies factual statements vs opinions using cue-phrase heuristics ("I believe", "in my opinion"→opinion; declarative sentences with entities→factual claim).
- Extract entities with lightweight regex + gazetteer patterns (no spaCy to avoid heavy dep): DATES, ORGANIZATIONS (capitalized multi-word + known org list), PEOPLE (titles + caps), LOCATIONS (known place list), NUMERICAL claims (percentages, money, counts).
- Return structured: `{claim_text, claim_type: factual|opinion, entities: {dates,orgs,people,locations,numbers}, normalized_claim}`.
- Limit to top N most claim-like sentences (presence of entities + declarative).
- `ClaimVerifier` consumes these structured claims and matches against evidence (Phase 5).

**Risks:** Regex NER is imperfect — clearly label it as heuristic in the UI. Must not present entity extraction as proof of falsity. Re-run pytest (existing claim test must still pass).

---

## Phase 5: RAG-based evidence retrieval & fact-checking (FAISS + sentence-transformers, optional)

**Goal:** Retrieval-augmented evidence matching against a verified corpus, with honest "Insufficient Evidence" when nothing is found.

**Files:**
- (create) `backend/app/services/evidence_retrieval.py` — `EvidenceRetriever` (sentence-transformer embeddings + FAISS index over the verified evidence repository + optional cached web docs)
- (modify) `backend/app/factcheck/verifier.py` — use `EvidenceRetriever` to fetch top-k evidence per claim, then classify Supported/Contradicted/Insufficient/Conflicting
- (create) `ml_pipeline/saved_models/evidence_index/` — FAISS index + evidence docs (built by a build script)
- (create) `ml_pipeline/training/build_evidence_index.py` — builds the FAISS index from `VERIFIED_EVIDENCE_REPOSITORY` + any local trusted docs
- (modify) `backend/requirements.txt` — add `sentence-transformers`, `faiss-cpu` as optional

**Steps:**
- `EvidenceRetriever.is_available()` checks imports + index file. When unavailable, fall back to the existing keyword-match repository (current behavior) — graceful.
- `build_evidence_index.py`: embed every evidence item's `claim_summary` + `evidence_summary` with a sentence-transformer (`all-MiniLM-L6-v2`), store in a FAISS index, persist index + metadata. Only the verified, cited repository is indexed — no scraped/fabricated docs.
- For each extracted claim: embed query, retrieve top-k (k=3) evidence chunks, compute cosine similarity; above threshold → candidate evidence; then stance-classify (supported/contradicted) via the repository's labeled status + keyword entailment heuristics.
- Classification: Supported / Contradicted / Insufficient Evidence / Conflicting. **Never** invent sources — only return items that exist in the indexed repository with their real URLs/citations. Below threshold → "Insufficient Evidence".
- Output per claim: `{status, evidence_summary, supporting_sources:[{title,url,publisher,...}], contradicting_sources, has_verified_match, retrieval_scores}`.

**Risks:** sentence-transformers downloads a model (~80MB) on first use — must be optional. If offline, fall back to keyword match. FAISS on Windows: `faiss-cpu` has wheels for cp313; if install fails, graceful fallback. Never auto-classify unsupported as fake. Re-run pytest.

---

## Phase 6: Explainable AI — SHAP/LIME for classical models + sentence risk

**Goal:** Add real feature attribution for the linear models and evidence-aware sentence highlighting.

**Files:**
- (create) `backend/app/services/explainability.py` — `ExplainabilityService` wrapping the existing `XAIEngine` + optional LIME
- (modify) `backend/app/ml/xai_engine.py` — keep existing saliency; add a sentence-risk reasoner that ties sentence risk to detected signals + evidence
- (modify) `backend/app/services/prediction_service.py` — use `ExplainabilityService`

**Steps:**
- For Logistic Regression / Linear SVM: use the existing weight-projection saliency (already SHAP/LIME-consistent per the docstring) and, if `lime` is installed, add a true LIME explainer for per-instance attribution on the chosen prediction. LIME is optional.
- Add a `sentence_explanations` upgrade: each sentence gets a `reason` string citing *which* signals drove its risk (clickbait term, urgency token, all-caps, contradiction with retrieved evidence) — never "this proves it's false".
- Keep the ethical guardrail: attention/keyword importance is presented as *influence on the model's decision*, never as proof of factual falsity.
- Output unchanged field name `explanation` (backward compat) with richer sub-fields.

**Risks:** LIME can be slow on long text — cap token/sentence counts and cache. Optional dep. Re-run pytest (existing XAI test must pass).

---

## Phase 7: Frontend upgrades (preserve existing design)

**Goal:** Surface the new signals in the existing React/Tailwind UI without removing current components.

**Files:**
- (modify) `frontend/src/pages/ReportDetailPage.jsx` — add uncertainty badge, outcome label, transformer model row, evidence/RAG section
- (modify) `frontend/src/components/ModelAgreementCard.jsx` — show DistilBERT row when present; show uncertainty
- (create) `frontend/src/components/ClaimEvidencePanel.jsx` — claim-by-claim verification with retrieved sources + retrieval scores
- (create) `frontend/src/components/UncertaintyBadge.jsx`
- (modify) `frontend/src/components/XAIVisualizer.jsx` — sentence reasons
- (modify) `frontend/src/pages/ModelPerformancePage.jsx` — show transformer metrics + baseline-vs-improved comparison when present
- (modify) `frontend/src/services/api.js` — no endpoint changes (same `/api/analyze/*`), just consume new fields

**Steps:**
- Add an "Article Assessment" header showing outcome (Likely Reliable / Potentially Misleading / Unverified) + uncertainty badge + the explicit note "model confidence ≠ factual truth".
- Model comparison card: include DistilBERT row only when `model_predictions` contains it.
- New `ClaimEvidencePanel`: per claim → status pill, evidence summary, source links (real), retrieval confidence, "Insufficient Evidence" empty state.
- Suspicious-sentence highlighting with reason tooltips.
- All new sections render gracefully when optional fields are absent (transformer/evidence not loaded).

**Risks:** Must not break existing report rendering — all new fields accessed with fallbacks. Run `npm run build` to verify.

---

## Phase 8: Tests, requirements, docs, final verification

**Goal:** Honest tests for the new pipeline; updated deps; docs; full local run on Windows.

**Files:**
- (modify) `tests/test_truthlens.py` — keep all 14 existing tests; add new tests
- (create) `tests/test_truthlens_v2.py` — genuine/fake/political/science/health/short/long/opinion/insufficient-evidence/empty-input scenarios; specifically assert the JWST science article is NOT "Potentially Misleading"
- (modify) `backend/requirements.txt` — add optional deps block
- (modify) `README.md` — document new modules, optional deps, training commands, known limitations
- (modify) `verify_all.py` — add checks for new fields (uncertainty, claims structure) where present

**Steps:**
- Add the false-positive regression test: JWST/CEERS article → outcome must be "Likely Reliable" or "Unverified", NOT "Potentially Misleading". This locks in the Phase 1 fix.
- Tests for claim extraction (entities present), evidence retrieval (Insufficient when no match, no fabricated URLs), uncertainty handling.
- Tests run with ONLY core deps (no torch/faiss) to prove graceful degradation — assert transformer/evidence fields are absent or null, not crashed.
- Update requirements with an "Optional (transformer/RAG)" section: `transformers`, `torch`, `sentence-transformers`, `faiss-cpu`, `lime`.
- README: new module table, `python ml_pipeline/training/train_transformer.py`, `python ml_pipeline/training/build_evidence_index.py`, known limitations (small dataset, optional deps, heuristic NER).
- Final: `pytest` all green, `verify_all.py` green, `npm run build` green, live smoke test of `/api/analyze/text` showing new fields.

**Risks:** Tests must not be weakened to pass — fix the real behavior. Optional-dep tests must pass on a minimal install (the default CI/local state). Re-run everything at the end.

---

## Conclusion

End state: TruthLens AI 2.0 — a calibrated, uncertainty-aware credibility engine that stops mislabeling genuine science articles; an improved classical ensemble with honest metrics; an optional DistilBERT vote; structured entity-aware claim extraction; RAG/FAISS evidence retrieval that never fabricates; SHAP/LIME-consistent explainability; a professional frontend surfacing outcomes, uncertainty, per-claim evidence, and model agreement. All existing features and API contracts preserved; 14 existing tests + new v2 tests green; runs on Windows with core deps, full power with optional deps.

## Manual Tests
1. Minimal install (no torch/faiss): `python -m pytest tests/` green; `python backend/run.py` starts; analyze JWST article → NOT "Potentially Misleading".
2. With optional deps: `python ml_pipeline/training/train_transformer.py` fine-tunes; `build_evidence_index.py` builds index; analyze shows DistilBERT row + retrieved evidence links.
3. Frontend: report page shows outcome + uncertainty badge + claim evidence panel + sentence reasons; Model Performance shows transformer + improved metrics.
4. `python verify_all.py` and `npm run build` both green.

## Warnings
- Optional dependencies (torch, transformers, sentence-transformers, faiss-cpu, lime) are NOT installed by default to keep Windows setup light. Install them separately to unlock DistilBERT + RAG.
- Fine-tuning DistilBERT on the small curated dataset will overfit; metrics are reported honestly and flagged as a limitation.
- Regex-based entity extraction is heuristic, not spaCy-grade; labeled as such in the UI.

## Open Questions
- None blocking: the optional-deps + graceful-degradation design resolves the "heavy deps vs. must run on Windows" tension without needing a decision. If the user wants torch installed automatically, that's a follow-up.