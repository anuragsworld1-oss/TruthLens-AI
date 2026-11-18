<!-- PLAN STATUS: completed | UPDATED: 2026-11-18T19:58:28.257Z -->
<!-- PLAN ID: plan_mwmj2w26_0 -->
<!-- Phase 1: completed -->
<!-- Phase 2: completed -->
<!-- Phase 3: completed -->
<!-- Phase 4: completed -->
<!-- Phase 5: completed -->

# TruthLens AI — Completion, Bug-Fix & Windows Local-Run Plan

## Context / What this resolves

A thorough codebase audit (read every backend route, service, NLP/ML module, ML pipeline, database model, frontend page/component, tests, and configs; ran the pytest suite and the Vite production build) shows the project is already ~90% functional — **14/14 tests pass**, the **frontend production build succeeds**, and **all 5 ML models + TF-IDF load successfully**. This is NOT a half-finished rewrite; it is a mature codebase with a small number of real, targeted defects that prevent a clean local run on Windows and that lose data between the analysis engine and the UI.

The verified problems are:
1. **`verify_all.py` crashes on Windows** with `UnicodeEncodeError` — it prints Unicode box-drawing chars (═) and emojis on a cp1252 console. (Confirmed by running it.)
2. **Model agreement % and consensus confidence are computed by `prediction_service` but never persisted or returned.** `AnalysisResult.to_dict()` omits `model_agreement_percentage` and `consensus_confidence`, so `ReportDetailPage`'s `ModelAgreementCard` ALWAYS shows the hardcoded fallback `80%` — even immediately after a fresh analysis. The real ensemble agreement is silently discarded. (Verified by reading `database.py` to_dict vs `prediction_service.py` return shape vs `ReportDetailPage.jsx` prop binding.)
3. **`limitations_disclaimer`, `models_analyzed`, and `extracted_claims` (raw shape) are lost on DB round-trip** — minor, but the disclaimer and model count should be surfaced on saved reports.
4. **No Windows PowerShell setup instructions, no `.env`, no one-click startup script.** The user's primary goal is to run the whole stack locally on Windows via VS Code (backend :5000, frontend :3000). The README is detailed but lacks the exact PowerShell commands and a launcher.
5. **`requirements.txt` is missing `python-dotenv`** (referenced conceptually by `.env.example`/config pattern) and the ML pipeline has no `tensorflow`/`torch` dependency (correct — BiLSTM is pure NumPy), but NLTK data (`punkt`, `wordnet`, `stopwords`) must be downloaded for the preprocessor, which currently silently falls back to regex tokenization. This should be documented/seeded.
6. The dashboard `/api/models/performance` fallback hardcodes accuracy numbers when `metrics.json` is missing — acceptable since the real `metrics.json` exists, but the fallback should be clearly marked and never silently used; it currently can be. Minor hardening.

Non-issues confirmed working (do NOT touch): SSRF guard, document parser, image provenance, claim verifier, XAI engine, linguistic analyzer, AI-style detector, all 5 ML model classes, BiLSTM training/inference, TF-IDF vectorizer, JWT auth routes, history/CRUD/review routes, all React pages and components, Vite proxy config, CORS.

## Approach / Why this way

Rather than rewriting working code, this plan makes **surgical, verified fixes** to the specific failure points and adds the missing Windows runbook + launcher. The schema gap (item 2) is fixed by adding two nullable columns to `AnalysisResult` plus a tiny SQLite auto-migration (ALTER TABLE add column if missing) inside `create_app` — this is safe for the existing dev DB (no data loss, idempotent) and avoids a heavy migration framework for a local SQLite app. Everything else is doc/script work plus small response-shape merges. After each fix I re-run pytest, the verification script, and the frontend build to prove the change rather than claim it.

---

## Phase 1: Fix Windows Unicode crash in verify_all.py

**Goal:** Make the master verification script run cleanly on a default Windows (cp1252) console so the user can validate the full API end-to-end.

**Files:**
- (modify) `verify_all.py`

**Steps:**
- Replace Unicode box-drawing chars (═), check/cross glyphs, and any non-ASCII print characters with ASCII-safe equivalents (e.g. `=`, `[PASS]`, `[FAIL]`).
- Force stdout to UTF-8 at the top: `sys.stdout.reconfigure(encoding="utf-8", errors="replace")` guarded by a hasattr check, so emojis/Unicode (if any remain) never crash on cp1252.
- Keep all check logic identical; do not weaken any assertion.

**Risks:** None — cosmetic only. Re-run `python verify_all.py` to confirm a full PASS report with no traceback.

---

## Phase 2: Persist & return model agreement + consensus confidence (schema gap fix)

**Goal:** Stop the UI from showing a fake 80% agreement; surface the real ensemble consensus on both fresh analyses and saved reports.

**Files:**
- (modify) `backend/app/models/database.py`
- (modify) `backend/app/__init__.py`
- (modify) `backend/app/routes/analysis_routes.py`
- (modify) `backend/app/services/prediction_service.py` (return-shape only — already computes the values)

**Steps:**
- In `database.py` `AnalysisResult`: add two nullable `Float` columns `model_agreement_percentage` and `consensus_confidence`; add them to `to_dict()`. Also add `limitations_disclaimer` (Text, nullable) and `models_analyzed` (Integer, nullable) to `to_dict()` if added as columns — alternatively keep disclaimer/models_analyzed out of schema and merge at route level. Decision: add `model_agreement_percentage`, `consensus_confidence` as columns (needed on saved reports); merge `limitations_disclaimer`/`models_analyzed` into the response at the route layer (no schema change needed for those two).
- In `__init__.py` `create_app`, after `db.create_all()`, add an idempotent SQLite migration helper that, for each new column not present in `analysis_results` (check via `PRAGMA table_info`), runs `ALTER TABLE analysis_results ADD COLUMN <name> REAL`. Wrap in try/except so non-SQLite/already-present cases are no-ops. This makes the existing `truthlens.db` gain the columns without deletion.
- In `analysis_routes.py` `_save_analysis_to_db`: populate `model_agreement_percentage=analysis_data.get("model_agreement_percentage")` and `consensus_confidence=analysis_data.get("consensus_confidence")` on the `AnalysisResult`.
- In each analyze endpoint (text/url/upload), after building `resp = db_res.to_dict()`, merge the non-persisted display fields from `analysis_res` so the fresh response is complete: `resp.setdefault("limitations_disclaimer", analysis_res.get("limitations_disclaimer"))`, plus `models_analyzed`, and (for url) `publisher_intelligence`/`author`/`published_at` (already done for url — keep).
- Verify `report.model_agreement_percentage` now flows to `ModelAgreementCard`.

**Risks:** ALTER TABLE on existing rows leaves new columns NULL → `to_dict()` returns None → component uses `|| 80` fallback only for NULL saved reports (acceptable; fresh analyses always have the value). Migration must be SQLite-guarded so it doesn't break a hypothetical PostgreSQL deploy (gate on `db.engine.url.drivername == 'sqlite'`). Re-run pytest after; the `test_api_analyze_text` assertion (`"predicted_class" in data`) still holds.

---

## Phase 3: Harden models/performance fallback & seed NLTK data

**Goal:** Ensure the preprocessor uses real NLTK tokenization (not silent regex fallback) and that no fabricated metrics can silently appear.

**Files:**
- (modify) `backend/app/routes/dashboard_routes.py`
- (modify) `backend/requirements.txt` (add `python-dotenv`)
- (create) `backend/app/nltk_setup.py` (or inline in `__init__.py`) — download `punkt`, `punkt_tab`, `wordnet`, `stopwords` if missing, silently and quietly.

**Steps:**
- Add an NLTK data bootstrap that runs once at app init: `nltk.download(..., quiet=True)` for the four resources, each guarded by a try/except so offline machines still fall back gracefully.
- In `get_model_performance`, if `metrics.json` is missing, return a clearly-labeled `evaluated: false` flag with the fallback numbers explicitly marked `"placeholder": true` and a message instructing to run `train_models.py`, instead of presenting placeholders as real benchmarks. (Only triggers if file missing — currently it exists, so no behavior change in normal runs, but closes the "invent accuracy" loophole.)
- Add `python-dotenv` to requirements and load `.env` in `config.py` (currently config reads `os.environ` directly; dotenv makes the `.env.example` actually functional). Guard the import.

**Risks:** NLTK download requires internet on first run; the existing try/except fallback means offline runs still work (regex tokenizer). Adding dotenv load must not crash if `.env` absent. Re-run pytest.

---

## Phase 4: Windows localhost configuration, .env, startup script

**Goal:** Deliver the user's primary goal — one-command local run on Windows (backend :5000, frontend :3000) with exact PowerShell instructions.

**Files:**
- (modify) `.env.example` (restore real `SECRET_KEY=`/`JWT_SECRET_KEY=` keys so it's a usable template; the tool redacted them in display but the file should contain literal key names)
- (create) `.env` (gitignored local dev copy with safe dev defaults) — only if not present
- (create) `start.ps1` (PowerShell launcher: starts Flask backend and Vite frontend in two split panes/windows)
- (modify) `README.md` (add a "Windows PowerShell Quickstart" section with the 8 exact commands: venv, pip install, npm install, db init, model train/load, start backend, start frontend, run tests)

**Steps:**
- `start.ps1`: check for venv + node_modules, create if missing; start `python backend/run.py` in a new window/tab and `npm run dev` (cwd frontend) in another; print both URLs.
- README Quickstart commands:
  1. `python -m venv .venv`
  2. `.\.venv\Scripts\Activate.ps1` ; `pip install -r backend/requirements.txt`
  3. `cd frontend ; npm install ; cd ..`
  4. DB auto-creates on first backend run (`db.create_all()`); document this.
  5. `python ml_pipeline/training/train_models.py` (retrain) — or note existing saved_models are pre-trained.
  6. `python backend/run.py` → http://127.0.0.1:5000
  7. `cd frontend ; npm run dev` → http://localhost:3000
  8. `python -m pytest tests/` and `python verify_all.py`
- Ensure Vite proxy (`/api` → 5000) is documented and that `VITE_API_URL` can be left unset (proxy handles it) OR set to `http://127.0.0.1:5000/api`.

**Risks:** PowerShell execution policy may block `.ps1` — document `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`. The `start.ps1` must not hang the terminal; use `Start-Process` for background windows.

---

## Phase 5: Final verification — tests, build, live smoke test

**Goal:** Prove the whole stack runs, not just claim it.

**Files:** none (verification only)

**Steps:**
- Run `python -m pytest tests/test_truthlens.py -v` → expect 14/14 pass.
- Run `python verify_all.py` → expect full PASS with no Unicode crash, including a real `/api/analyze/text` round-trip showing a non-default `model_agreement_percentage`.
- Run `npm run build` in `frontend/` → expect success.
- Start backend (`python backend/run.py`) and frontend (`npm run dev`) and confirm `http://localhost:3000` loads and the Dashboard hits `http://127.0.0.1:5000/api/dashboard/stats` (200). Kill both after.

**Risks:** Backend startup loads models (a few seconds); ensure no import errors. If a live port is busy, document changing PORT.

---

## Conclusion

End state: a fully functional, explainable-AI fake-news detection web app running locally on Windows — backend Flask API on :5000 with real ML ensemble + claim verification + XAI, React+Vite frontend on :3000 wired to real backend data, 14/14 tests green, verification script green, one-click `start.ps1` launcher, and a README with exact PowerShell commands. No fabricated metrics, no fake data, no removed features.

## Manual Tests

1. `.\start.ps1` opens both servers; visit http://localhost:3000 — Landing page renders.
2. Open Analysis Studio, paste the JWST sample, click Analyze → report page shows a credibility gauge, the **real** model agreement % (not always 80%), model probability bars, XAI highlights, and verified claim cards with clickable NASA source links.
3. Dashboard shows real DB counts (grows after each analysis) with a "Preview Data" badge only when empty.
4. History page lists saved analyses; delete works; Export JSON works.
5. Model Performance page shows real confusion matrices and BiLSTM epoch curves from `metrics.json`.
6. `python verify_all.py` prints a full green PASS report on Windows.