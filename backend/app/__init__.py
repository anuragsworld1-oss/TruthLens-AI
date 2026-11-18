"""
TruthLens AI - Flask Application Factory
Configures SQLAlchemy, JWT Extended, CORS, and Blueprints.
"""

import os
import sys

# Ensure backend directory is in sys.path
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from flask import Flask, jsonify, render_template
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from config import Config
from app.models.database import db
from app.extensions import limiter


def _ensure_nltk_data():
    """Downloads the NLTK corpora required by the preprocessor on first run.
    Silent and best-effort: if the machine is offline, the preprocessor's
    existing try/except falls back to regex tokenization."""
    try:
        import nltk
        for resource in [("punkt", "tokenizers/punkt"),
                         ("punkt_tab", "tokenizers/punkt_tab"),
                         ("wordnet", "corpora/wordnet"),
                         ("stopwords", "corpora/stopwords")]:
            try:
                nltk.data.find(resource[1])
            except LookupError:
                try:
                    nltk.download(resource[0], quiet=True)
                except Exception:
                    pass
    except Exception:
        pass

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure required directories exist
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    instance_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "instance")
    os.makedirs(instance_dir, exist_ok=True)

    # Enable CORS for all API routes
    CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

    # Initialize extensions
    db.init_app(app)
    limiter.init_app(app)
    jwt = JWTManager(app)

    # Ensure NLTK tokenizer/lemmatizer corpora are available
    _ensure_nltk_data()

    @jwt.unauthorized_loader
    def unauthorized_callback(callback):
        return jsonify({"error": "Missing or invalid authorization token."}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(callback):
        return jsonify({"error": "Authorization token is signature-invalid or corrupted."}), 401

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({"error": "Authorization token has expired. Please log in again."}), 401

    # Register blueprints
    from app.routes.auth_routes import auth_bp
    from app.routes.analysis_routes import analysis_bp
    from app.routes.dashboard_routes import dashboard_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(analysis_bp)
    app.register_blueprint(dashboard_bp)

    # Web Client Single Page Application Routes
    @app.route("/")
    @app.route("/dashboard")
    @app.route("/studio")
    @app.route("/report/<path:path>")
    @app.route("/history")
    @app.route("/models")
    @app.route("/about")
    def serve_spa(path=None):
        return render_template("index.html")

    # Error Handlers
    @app.errorhandler(404)
    def handle_404(e):
        return jsonify({"error": "Resource or endpoint not found."}), 404

    @app.errorhandler(500)
    def handle_500(e):
        return jsonify({"error": "An internal server error occurred.", "details": str(e)}), 500

    # Auto-create database tables
    with app.app_context():
        db.create_all()
        _auto_migrate_sqlite(app, db)

    return app


def _auto_migrate_sqlite(app, db):
    """
    Lightweight, idempotent SQLite schema migration for local development.
    Adds new nullable columns to existing tables via ALTER TABLE if they are
    missing, so an older truthlens.db gains the columns without being deleted.
    No-op on non-SQLite backends and when columns already exist.
    """
    try:
        if app.config.get("SQLALCHEMY_DATABASE_URI", "").startswith("sqlite"):
            from sqlalchemy import text, inspect
            inspector = inspect(db.engine)
            migrations = {
                "analysis_results": [
                    "model_agreement_percentage REAL",
                    "consensus_confidence REAL",
                    "limitations_disclaimer TEXT",
                    "uncertainty_level VARCHAR(20)",
                    "outcome VARCHAR(40)",
                    "credibility_reasoning JSON",
                ],
            }
            for table, new_cols in migrations.items():
                if table not in inspector.get_table_names():
                    continue
                existing = {c["name"] for c in inspector.get_columns(table)}
                for col_def in new_cols:
                    col_name = col_def.split()[0]
                    if col_name not in existing:
                        with db.engine.begin() as conn:
                            conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {col_def}"))
                        print(f"[Migration] Added column {col_name} to {table}.")
    except Exception as e:
        # Migration is best-effort for local dev; never block app startup.
        print(f"[Migration] Skipped (non-fatal): {e}")
