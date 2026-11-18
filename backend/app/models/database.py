"""
TruthLens AI - Database Schema & SQLAlchemy ORM Models
Defines tables for Users, Articles, AnalysisResults, Claims, EvidenceSources, Reviews, and ModelMetrics.
Compatible with SQLite (local development) and PostgreSQL (production deployment).
"""

from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

def utc_now():
    return datetime.now(timezone.utc)

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(50), default="analyst")  # analyst, reviewer, admin
    created_at = db.Column(db.DateTime, default=utc_now)

    # Relationships
    articles = db.relationship("Article", backref="author", lazy=True, cascade="all, delete-orphan")
    reviews = db.relationship("Review", backref="reviewer", lazy=True)

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "created_at": self.created_at.isoformat()
        }


class Article(db.Model):
    __tablename__ = "articles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    title = db.Column(db.String(350), nullable=False, default="Untitled News Article")
    content = db.Column(db.Text, nullable=False)
    source_url = db.Column(db.String(1000), nullable=True)
    language = db.Column(db.String(10), default="en")
    word_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=utc_now, index=True)

    # Relationships
    analysis = db.relationship("AnalysisResult", backref="article", uselist=False, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "content": self.content[:300] + ("..." if len(self.content) > 300 else ""),
            "source_url": self.source_url,
            "language": self.language,
            "word_count": self.word_count,
            "created_at": self.created_at.isoformat()
        }


class AnalysisResult(db.Model):
    __tablename__ = "analysis_results"

    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey("articles.id"), nullable=False, index=True)
    predicted_class = db.Column(db.String(60), nullable=False)  # Likely Genuine, Potentially Misleading, Needs Further Verification
    credibility_score = db.Column(db.Float, nullable=False)    # 0 to 100
    model_confidence = db.Column(db.Float, nullable=False)
    model_agreement_percentage = db.Column(db.Float, nullable=True)  # ensemble agreement 0-100
    consensus_confidence = db.Column(db.Float, nullable=True)        # mean prob of consensus class 0-100
    limitations_disclaimer = db.Column(db.Text, nullable=True)
    uncertainty_level = db.Column(db.String(20), nullable=True)      # Low / Medium / High (TruthLens 2.0)
    outcome = db.Column(db.String(40), nullable=True)                # Likely Reliable / Potentially Misleading / Unverified
    credibility_reasoning = db.Column(db.JSON, nullable=True)        # human-readable factors driving the score
    model_predictions = db.Column(db.JSON, nullable=True)
    linguistic_analysis = db.Column(db.JSON, nullable=True)
    ai_writing_style = db.Column(db.JSON, nullable=True)
    explanation = db.Column(db.JSON, nullable=True)
    recommended_actions = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=utc_now, index=True)

    # Relationships
    claims = db.relationship("Claim", backref="analysis", lazy=True, cascade="all, delete-orphan")
    reviews = db.relationship("Review", backref="analysis", lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "article_id": self.article_id,
            "article_title": self.article.title if self.article else "",
            "article_content": self.article.content if self.article else "",
            "source_url": self.article.source_url if self.article else "",
            "language": self.article.language if self.article else "en",
            "predicted_class": self.predicted_class,
            "credibility_score": self.credibility_score,
            "model_confidence": self.model_confidence,
            "model_agreement_percentage": self.model_agreement_percentage,
            "consensus_confidence": self.consensus_confidence,
            "uncertainty_level": self.uncertainty_level,
            "outcome": self.outcome,
            "credibility_reasoning": self.credibility_reasoning,
            "limitations_disclaimer": self.limitations_disclaimer,
            "model_predictions": self.model_predictions,
            "linguistic_analysis": self.linguistic_analysis,
            "ai_writing_style": self.ai_writing_style,
            "explanation": self.explanation,
            "recommended_actions": self.recommended_actions,
            "claims": [c.to_dict() for c in self.claims],
            "reviews": [r.to_dict() for r in self.reviews],
            "created_at": self.created_at.isoformat()
        }


class Claim(db.Model):
    __tablename__ = "claims"

    id = db.Column(db.Integer, primary_key=True)
    analysis_id = db.Column(db.Integer, db.ForeignKey("analysis_results.id"), nullable=False, index=True)
    claim_text = db.Column(db.Text, nullable=False)
    normalized_claim = db.Column(db.String(500), nullable=True)
    verification_status = db.Column(db.String(80), nullable=False)  # Supported, Contradicted, Insufficient, Conflicting
    evidence_summary = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=utc_now)

    # Relationships
    sources = db.relationship("EvidenceSource", backref="claim", lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "analysis_id": self.analysis_id,
            "claim_text": self.claim_text,
            "normalized_claim": self.normalized_claim,
            "verification_status": self.verification_status,
            "evidence_summary": self.evidence_summary,
            "sources": [s.to_dict() for s in self.sources]
        }


class EvidenceSource(db.Model):
    __tablename__ = "evidence_sources"

    id = db.Column(db.Integer, primary_key=True)
    claim_id = db.Column(db.Integer, db.ForeignKey("claims.id"), nullable=False, index=True)
    source_title = db.Column(db.String(300), nullable=False)
    source_url = db.Column(db.String(1000), nullable=False)
    publisher = db.Column(db.String(150), nullable=True)
    published_at = db.Column(db.String(50), nullable=True)
    relevance_score = db.Column(db.Float, default=0.95)
    stance = db.Column(db.String(30), default="support")  # support, contradict

    def to_dict(self):
        return {
            "id": self.id,
            "source_title": self.source_title,
            "source_url": self.source_url,
            "publisher": self.publisher,
            "published_at": self.published_at,
            "relevance_score": self.relevance_score,
            "stance": self.stance
        }


class Review(db.Model):
    __tablename__ = "reviews"

    id = db.Column(db.Integer, primary_key=True)
    analysis_id = db.Column(db.Integer, db.ForeignKey("analysis_results.id"), nullable=False, index=True)
    reviewer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    review_status = db.Column(db.String(50), default="Under Review")  # Verified, Rejected, Inconclusive, Under Review
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=utc_now)

    def to_dict(self):
        return {
            "id": self.id,
            "analysis_id": self.analysis_id,
            "reviewer_name": self.reviewer.name if self.reviewer else "Editorial Reviewer",
            "review_status": self.review_status,
            "notes": self.notes,
            "created_at": self.created_at.isoformat()
        }


class ModelMetric(db.Model):
    __tablename__ = "model_metrics"

    id = db.Column(db.Integer, primary_key=True)
    model_name = db.Column(db.String(100), nullable=False, unique=True)
    accuracy = db.Column(db.Float, nullable=False)
    precision = db.Column(db.Float, nullable=False)
    recall = db.Column(db.Float, nullable=False)
    f1_score = db.Column(db.Float, nullable=False)
    weighted_f1 = db.Column(db.Float, nullable=True)
    training_time_sec = db.Column(db.Float, nullable=True)
    inference_time_ms = db.Column(db.Float, nullable=True)
    confusion_matrix = db.Column(db.JSON, nullable=True)
    evaluation_date = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "model_name": self.model_name,
            "accuracy": self.accuracy,
            "precision": self.precision,
            "recall": self.recall,
            "f1_score": self.f1_score,
            "weighted_f1": self.weighted_f1,
            "training_time_sec": self.training_time_sec,
            "inference_time_ms": self.inference_time_ms,
            "confusion_matrix": self.confusion_matrix,
            "evaluation_date": self.evaluation_date.isoformat()
        }
