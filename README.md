## ⚡ Quickstart Guide (Windows PowerShell)

### Prerequisites
- **Python 3.11+** on PATH (`python --version`).
- **Node.js 18+** with npm (`node --version`).
- VS Code recommended.

> If PowerShell blocks scripts, run once:
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
> ```

### One-Click Launcher
```powershell
.\start.ps1
```
This creates the `.venv`, installs all dependencies (first run only), and opens the
**backend** (http://127.0.0.1:5000) and **frontend** (http://localhost:3000) in two
separate windows. Close those windows to stop the servers.

### Manual Step-by-Step

#### 1. Create the Python virtual environment
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

#### 2. Install Python dependencies (includes NLTK bootstrap)
```powershell
pip install -r backend/requirements.txt
# NLTK corpora auto-download on first backend start; or manually:
python -c "import nltk; [nltk.download(x, quiet=True) for x in ['punkt','punkt_tab','stopwords','wordnet']]"
```

#### 3. Install frontend dependencies
```powershell
cd frontend
npm install
cd ..
```

#### 4. Initialize the database
The SQLite database (`backend/instance/truthlens.db`) is created **automatically**
on the first backend run via `db.create_all()`. An idempotent migration also adds
any new columns to existing tables. No manual step required.

#### 5. Load / (re)train ML models
Pre-trained models already ship in `ml_pipeline/saved_models/` and load on startup.
To recompute real benchmarks on the held-out test set:
```powershell
python ml_pipeline/training/train_models.py
```
*Trains all 5 models (Logistic Regression, Naive Bayes, Calibrated Linear SVM,
Random Forest, Bidirectional LSTM), saves weights, and writes true test metrics to
`metrics.json`.*

#### 6. Start the Flask backend
```powershell
$env:PYTHONPATH = "$PWD\backend;$PWD\ml_pipeline"
python backend/run.py
```
→ API live at **http://127.0.0.1:5000/api/health**

#### 7. Start the React frontend (new terminal)
```powershell
cd frontend
npm run dev
```
→ App live at **http://localhost:3000** (Vite proxies `/api` → :5000)

#### 8. Run the automated tests
```powershell
# Backend pytest suite (expect 14/14)
python -m pytest tests/test_truthlens.py -v

# Full API + ML + SSRF integration verification
python verify_all.py

# Frontend production build
cd frontend
npm run build
cd ..
```

### What you can do in the app
- **Landing Page:** Interactive hero with live preview widget.
- **Dashboard:** Real DB telemetry counters, credibility donut chart, trends area chart, recent activity.
- **News Analysis Studio:** Paste text, submit article URLs (SSRF-guarded), upload TXT/PDF/DOCX, or inspect image metadata.
- **Credibility Dossier:** Circular gauge (0–100), **real** multi-model agreement %, linguistic warnings, XAI saliency highlights, verified claim cards, and PDF export.
- **Article History:** Search, filter by category, sort by date, inspect/delete past reports.
- **Model Studio:** Real test-set confusion matrices, macro-F1 comparisons, and BiLSTM epoch curves.
- **Methodology:** Whitepaper and technical specifications.

---

## 🌐 API Reference

Base URL: `http://127.0.0.1:5000/api`

### Health Check
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/health` | — | Service heartbeat, model-load status & version. |

### Authentication
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/auth/register` | — | Register a new user (username, email, password). |
| POST | `/auth/login` | — | Login, returns JWT access token. |
| GET | `/auth/me` | JWT | Current authenticated user profile. |

### Analysis
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/analyze/text` | optional | Analyze pasted article text (`title`, `text`). |
| POST | `/analyze/url` | optional | Fetch & analyze an article URL (SSRF-guarded). |
| POST | `/analyze/upload` | optional | Upload & analyze TXT / PDF / DOCX (multipart). |
| POST | `/analyze/image` | optional | Image metadata / EXIF provenance analysis. |
| GET | `/analysis/history` | — | Paginated analysis history (`page`, `per_page`, `category`). |
| GET | `/analysis/<id>` | — | Full report dossier for a saved analysis. |
| DELETE | `/analysis/<id>` | — | Delete a saved analysis. |
| POST | `/review` | — | Submit a human editorial review for an analysis. |

### Dashboard & Models
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/dashboard/stats` | — | Real DB telemetry: totals by class, credibility distribution, recent analyses. |
| GET | `/models/performance` | — | Real held-out test-set metrics (accuracy, precision, recall, F1, confusion matrix) per model. |

### Analysis Response Shape
```json
{
  "analysis_id": 1,
  "predicted_class": "Likely Genuine",
  "credibility_score": 78.5,
  "model_confidence": 46.2,
  "model_agreement_percentage": 80.0,
  "consensus_confidence": 46.2,
  "models_analyzed": 5,
  "model_predictions": [ { "model": "Logistic Regression", "prediction": "Likely Genuine", "probabilities": {...} } ],
  "linguistic_analysis": { "readability": {...}, "warning_signals": [...], "sensationalism_score": 12.0 },
  "ai_writing_style": { "ai_probability": 31.0, "indicators": [...] },
  "explanation": { "top_credibility_features": [...], "top_suspicion_features": [...] },
  "claims": [ { "text": "...", "status": "Supported by available evidence", "sources": [...] } ],
  "limitations_disclaimer": "ML predictions are probabilistic...",
  "recommended_actions": [...]
}
```

---

## 🛡️ Security & Ethical Safeguards

- **SSRF Protection:** URL analysis blocks private/link-local/loopback IPs and resolves hostnames before fetching.
- **Secure Uploads:** Extension + content-type allow-listing; files stored outside the web root.
- **JWT Auth:** Token-based session protection on authenticated endpoints.
- **Rate Limiting:** Flask-Limiter guards abuse on API routes.
- **Secret Hygiene:** Secrets read from environment / `.env`; never committed. `.env.example` ships safe dev defaults.
- **Zero Hallucination:** Evidence retrieval only ever cites certified primary repositories (NASA, WHO, Reuters, PIB, Nature). When no evidence is available, the system explicitly returns **"Insufficient evidence"** — it never fabricates URLs, citations, or verification results.
- **Non-Dogmatic:** ML predictions are probabilistic signals, never definitive truth verdicts.

---

## 🔬 TruthLens AI 2.0 — Upgraded Credibility Architecture

### The Core Problem This Solves
A genuine scientific article (e.g. a NASA JWST discovery release) was being labeled
"Potentially Misleading" purely because its specialist vocabulary was rare relative
to the small training set, causing the models to be under-confident on the "Genuine"
class. Model confidence was being equated with factual truth.

### The 2.0 Solution

**1. Calibrated Credibility Engine** (`backend/app/services/credibility_engine.py`)
- **Separates model confidence from factual verification.** The credibility score
  is NOT just `P(genuine) × 100`.
- **Temperature shrinkage:** Probabilities are shrunk toward a neutral prior
  proportional to model disagreement, so out-of-distribution vocabulary does
  not collapse the genuine probability.
- **Linguistic penalties apply ONLY when real warning signals exist.** A clean,
  formal science article pays ~0 penalty.
- **Evidence fusion:** Corroborating evidence (from the fact-checker) can boost
  the score; contradicting evidence can penalize it — but within bounded limits.
- **Explicit uncertainty levels:** Low / Medium / High, surfaced to the user.
- **3 outcomes:** `Likely Reliable`, `Potentially Misleading`, `Unverified`.
  The legacy 3-class labels are preserved via a backward-compatible mapping.

**Key decision rules (in priority order):**
1. Strong contradicting evidence → Potentially Misleading.
2. High model disagreement + no warning signals + no evidence → Unverified (never fake).
3. Clean article + evidence corroborates claims → Likely Reliable.
4. Clean article + models agree genuine → Likely Reliable (vocabulary rarity
   does NOT flip it to misleading).
5. Warning signals present → score-driven (can be Misleading).
6. No signals + no evidence + uncertain → Unverified (false-positive guard).

**2. Improved Classical ML Pipeline** (`ml_pipeline/training/`)
- Class-imbalance handling (`class_weight="balanced"`) in Logistic Regression.
- ROC-AUC (one-vs-rest macro) computed for every model with probabilities.
- Same preprocessing at train and inference time (verified).

**3. Optional DistilBERT Transformer** (`backend/app/services/transformer_service.py`)
- Adds a 6th ensemble vote when `transformers` + `torch` are installed.
- **Graceful degradation:** Without them, the 5-model ensemble runs unchanged.
- Model loaded ONCE and cached; never re-downloaded per request.
- Train via: `python ml_pipeline/training/train_transformer.py`

**4. Intelligent Claim Extraction** (`backend/app/services/claim_extraction.py`)
- Structured entity recognition: dates, organizations, people, locations, numbers.
- Fact/opinion separation (opinion sentences excluded from fact-checking).
- Extraction scoring (claims with verifiable entities prioritized).

**5. RAG Evidence Retrieval** (`backend/app/services/evidence_retrieval.py`)
- FAISS + sentence-transformer similarity search over the verified repository.
- **Optional:** Without `faiss`/`sentence-transformers`, falls back to keyword matching.
- Below similarity threshold → "Insufficient evidence" (never auto-fake).
- Build index via: `python ml_pipeline/training/build_evidence_index.py`

**6. Enhanced Explainability** (`backend/app/services/explainability.py`)
- SHAP/LIME-consistent linear saliency (always available).
- Optional true LIME per-instance attribution.
- Sentence-level **reasons** citing which signal drove the assessment
  (clickbait term, urgency, ALL-CAPS, evidence support/contradiction).
- Ethical disclaimer: attribution shows *influence on the model*, not proof of falsity.

### Optional Dependencies

The app runs fully on the core dependencies. To unlock advanced features:

```powershell
# DistilBERT ensemble vote
pip install transformers torch
python ml_pipeline/training/train_transformer.py

# RAG evidence retrieval
pip install sentence-transformers faiss-cpu
python ml_pipeline/training/build_evidence_index.py

# LIME per-instance explanations
pip install lime
```

---

## 🧪 Testing

```powershell
# Original unit + integration suite (14 tests)
python -m pytest tests/test_truthlens.py -v

# TruthLens 2.0 extended suite (23 tests: false-positive regression, claim extraction,
# uncertainty handling, graceful degradation, edge cases)
python -m pytest tests/test_truthlens_v2.py -v

# End-to-end verification (models load, API round-trips, SSRF guard, SPA routes)
python verify_all.py

# Frontend production build
cd frontend ; npm run build ; cd ..
```
Coverage spans: model loading & inference, linguistic analyzer, claim verifier, auth flow,
analyze text/url/upload, dashboard stats, model performance, history CRUD, SSRF rejection,
SPA fallback routing, explainable-AI engine, calibrated credibility engine, structured
claim extraction, uncertainty handling, and graceful optional-dependency degradation.

---

## 📁 Project Structure

```
truthlenAI/
├── backend/                 # Flask REST API
│   ├── app/
│   │   ├── __init__.py      # App factory + SQLite auto-migration + NLTK bootstrap
│   │   ├── config.py        # Config (loads .env via python-dotenv)
│   │   ├── extensions.py    # CORS, JWT, Limiter
│   │   ├── models/database.py   # SQLAlchemy models (Article, AnalysisResult, Claim, ...)
│   │   ├── routes/          # auth, analysis, dashboard blueprints
│   │   ├── services/        # prediction_service, source_intelligence, doc_parser, image_provenance
│   │   ├── nlp/             # linguistic_analyzer, ai_style_detector
│   │   ├── ml/xai_engine.py # Explainable AI feature attribution
│   │   └── factcheck/verifier.py  # Claim verification workflow
│   ├── instance/truthlens.db
│   └── run.py
├── frontend/               # React 18 + Vite + Tailwind
│   ├── src/pages/          # Landing, Dashboard, AnalysisStudio, ReportDetail, History, ModelPerformance, About
│   ├── src/components/     # CircularGauge, ModelAgreementCard, ClaimVerificationCards, XAIVisualizer, ...
│   ├── src/services/api.js # Axios client
│   └── vite.config.js      # /api proxy → :5000
├── ml_pipeline/            # Training & inference
│   ├── preprocessing/text_cleaner.py
│   ├── training/           # train_models, classical_models, bilstm_model
│   ├── datasets/dataset_loader.py
│   └── saved_models/       # 5 models + tfidf + metrics.json (pre-trained)
├── tests/test_truthlens.py
├── verify_all.py
├── start.ps1               # Windows one-click launcher
├── .env / .env.example
└── README.md
```

---

## 📜 License

MIT License — see repository headers. Educational and research use encouraged.

---

<div align="center">

**See Beyond Headlines. Discover What's True.**

Built with Flask · React · Tailwind CSS · scikit-learn · NumPy BiLSTM · Explainable AI

</div>
