"""
TruthLens AI - Backend Configuration
Handles SQLite local development, JWT credentials, rate limiting, and uploads.
"""

import os
from datetime import timedelta

# Load a local .env file if python-dotenv is installed (best-effort).
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))
except Exception:
    pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "truthlens-dev-secure-key-2026-xyz789")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "truthlens-jwt-access-secret-2026")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)

    _default_db = f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'truthlens.db')}"
    _env_db = os.environ.get("DATABASE_URL", _default_db)
    # If a relative sqlite path is supplied via env/.env, resolve it against
    # BASE_DIR (backend/) so the database location is independent of the CWD.
    if _env_db.startswith("sqlite:///") and not os.path.isabs(_env_db.replace("sqlite:///", "", 1)):
        _rel = _env_db.replace("sqlite:///", "", 1)
        # Avoid doubling an existing 'instance' segment when BASE_DIR already points at backend/
        _candidate = os.path.join(BASE_DIR, _rel)
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{_candidate}"
    else:
        SQLALCHEMY_DATABASE_URI = _env_db
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max request payload

    RATELIMIT_DEFAULT = "120 per minute"
    RATELIMIT_STORAGE_URI = "memory://"
