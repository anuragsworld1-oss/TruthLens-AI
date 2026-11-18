"""
TruthLens AI - Dashboard & Model Performance Analytics Routes
Provides executive stats, trends, language distribution, and real ML evaluation benchmarks.
"""

import os
import re
import json
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from flask import Blueprint, jsonify
from app.models.database import db, Article, AnalysisResult, ModelMetric

_TOPIC_STOPWORDS = {
    "the", "and", "for", "with", "from", "that", "this", "have", "has", "was",
    "were", "are", "news", "article", "untitled", "analyzed", "text", "snippet",
    "about", "into", "over", "after", "their", "they", "will", "been", "more",
    "than", "your", "you", "not", "but", "its", "his", "her", "who", "what",
}


def _wire_tag(predicted_class):
    if predicted_class == "Likely Genuine":
        return "[VERIFIED]"
    if predicted_class == "Potentially Misleading":
        return "[DECEPTIVE]"
    return "[UNDER REVIEW]"


def _risk_for(predicted_class):
    if predicted_class == "Potentially Misleading":
        return "High"
    if predicted_class == "Needs Further Verification":
        return "Medium"
    return "Low"


def _activity_row(record):
    return {
        "id": record.id,
        "title": record.article.title if record.article else "Untitled",
        "predicted_class": record.predicted_class,
        "credibility_score": record.credibility_score,
        "created_at": record.created_at.isoformat() if record.created_at else None,
    }


def _derive_trending_topics(records, limit=5):
    """Cluster recent archive headlines by distinctive terms. No fabricated counts."""
    clusters = defaultdict(list)
    for record in records:
        title = (record.article.title if record.article else "") or ""
        tokens = re.findall(r"[A-Za-z\u0900-\u097F]{4,}", title.lower())
        keywords = [token for token in dict.fromkeys(tokens) if token not in _TOPIC_STOPWORDS]
        for token in keywords[:6]:
            clusters[token].append(record)

    ranked = sorted(clusters.items(), key=lambda item: len(item[1]), reverse=True)[:limit]
    topics = []
    for token, group in ranked:
        classes = [item.predicted_class for item in group]
        dominant = max(set(classes), key=classes.count)
        label = token if not token.isascii() else token.title()
        topics.append({
            "topic": label,
            "mentions": len(group),
            "dominant_sentiment": dominant,
            "risk": _risk_for(dominant),
        })
    return topics


def _live_wire(activity):
    return [
        {
            "tag": _wire_tag(item["predicted_class"]),
            "headline": item["title"],
            "score": item["credibility_score"],
        }
        for item in activity[:6]
    ]

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/api")

# Project root = 4 dirnames up from backend/app/routes/dashboard_routes.py
# (routes -> app -> backend -> project root).
METRICS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
    "ml_pipeline", "saved_models", "metrics.json"
)

@dashboard_bp.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "operational",
        "service": "TruthLens AI API",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }), 200

@dashboard_bp.route("/dashboard/stats", methods=["GET"])
def get_dashboard_stats():
    total_analyses = AnalysisResult.query.count()

    if total_analyses > 0:
        genuine_count = AnalysisResult.query.filter_by(predicted_class="Likely Genuine").count()
        misleading_count = AnalysisResult.query.filter_by(predicted_class="Potentially Misleading").count()
        verify_count = AnalysisResult.query.filter_by(predicted_class="Needs Further Verification").count()

        # Average credibility score
        avg_score = db.session.query(db.func.avg(AnalysisResult.credibility_score)).scalar() or 0.0

        # Language distribution
        lang_counts = (
            db.session.query(Article.language, db.func.count(Article.id))
            .join(AnalysisResult, Article.id == AnalysisResult.article_id)
            .group_by(Article.language)
            .all()
        )
        language_dist = [{"language": (lang or "en").upper(), "count": count} for lang, count in lang_counts]

        recent_records = (
            AnalysisResult.query.order_by(AnalysisResult.created_at.desc())
            .limit(40)
            .all()
        )
        recent_activity = [_activity_row(record) for record in recent_records[:6]]
        trending_topics = _derive_trending_topics(recent_records)
        live_wire = _live_wire(recent_activity)

        # Trends over recent days — actual daily counts, including zeros.
        trends = []
        today = datetime.now(timezone.utc).date()
        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            day_count = AnalysisResult.query.filter(
                db.func.date(AnalysisResult.created_at) == str(day)
            ).count()
            trends.append({
                "date": day.strftime("%b %d"),
                "analyses": day_count
            })

        is_sample = False
    else:
        # Initial launch baseline preview (clearly identified)
        total_analyses = 284
        genuine_count = 142
        misleading_count = 98
        verify_count = 44
        avg_score = 64.8
        language_dist = [
            {"language": "EN (English)", "count": 218},
            {"language": "HI (Hindi)", "count": 66}
        ]
        recent_activity = [
            {
                "id": 1,
                "title": "NASA James Webb Telescope Discovers Distant Galaxy Nucleus",
                "predicted_class": "Likely Genuine",
                "credibility_score": 92.4,
                "created_at": datetime.utcnow().isoformat()
            },
            {
                "id": 2,
                "title": "Viral 5G Radiation Mind Control Rumor Debunked",
                "predicted_class": "Potentially Misleading",
                "credibility_score": 14.2,
                "created_at": (datetime.utcnow() - timedelta(hours=2)).isoformat()
            },
            {
                "id": 3,
                "title": "Preliminary Energy Storage Research Awaiting Peer Review",
                "predicted_class": "Needs Further Verification",
                "credibility_score": 48.0,
                "created_at": (datetime.utcnow() - timedelta(hours=5)).isoformat()
            }
        ]
        trends = [
            {"date": "Mon", "analyses": 32},
            {"date": "Tue", "analyses": 45},
            {"date": "Wed", "analyses": 38},
            {"date": "Thu", "analyses": 52},
            {"date": "Fri", "analyses": 49},
            {"date": "Sat", "analyses": 36},
            {"date": "Sun", "analyses": 32}
        ]
        trending_topics = [
            {"topic": "5G & Public Health Rumors", "mentions": 48, "dominant_sentiment": "Misleading", "risk": "High"},
            {"topic": "James Webb Astrophysical Releases", "mentions": 34, "dominant_sentiment": "Genuine", "risk": "Low"},
            {"topic": "Central Bank Currency Policies", "mentions": 29, "dominant_sentiment": "Needs Verification", "risk": "Medium"},
            {"topic": "Artificial Intelligence Safety Treaties", "mentions": 25, "dominant_sentiment": "Genuine", "risk": "Low"},
            {"topic": "Herbal Miracle Cures & Supplements", "mentions": 21, "dominant_sentiment": "Misleading", "risk": "High"}
        ]
        live_wire = _live_wire(recent_activity)
        is_sample = True

    credibility_distribution = [
        {"name": "Likely Genuine", "value": genuine_count, "color": "#22C55E"},
        {"name": "Potentially Misleading", "value": misleading_count, "color": "#EF4444"},
        {"name": "Needs Verification", "value": verify_count, "color": "#F59E0B"}
    ]

    return jsonify({
        "is_sample_data": is_sample,
        "total_articles_analyzed": total_analyses,
        "likely_genuine_count": genuine_count,
        "potentially_misleading_count": misleading_count,
        "needs_verification_count": verify_count,
        "average_credibility_score": round(avg_score, 1),
        "credibility_distribution": credibility_distribution,
        "analysis_trends": trends,
        "language_distribution": language_dist,
        "recent_activity": recent_activity,
        "trending_topics": trending_topics,
        "live_wire": live_wire
    }), 200

@dashboard_bp.route("/models/performance", methods=["GET"])
def get_model_performance():
    """
    Returns real evaluation metrics computed directly on test data.
    Never fabricates arbitrary accuracy numbers.
    """
    metrics_evaluated = os.path.exists(METRICS_PATH)
    if metrics_evaluated:
        with open(METRICS_PATH, "r") as f:
            metrics_data = json.load(f)
    else:
        # PLACEHOLDER fallback ONLY when training has not been run. These are
        # illustrative defaults, never presented as real benchmarks; clearly flagged.
        metrics_data = {
            "Multinomial Naive Bayes": {
                "model_name": "Multinomial Naive Bayes",
                "accuracy": 0.7222,
                "precision": 0.7139,
                "recall": 0.7222,
                "f1_score": 0.7139,
                "training_time_sec": 0.001,
                "inference_time_ms": 0.01,
                "confusion_matrix": [[7, 0, 0], [1, 5, 0], [2, 2, 1]]
            },
            "Logistic Regression": {
                "model_name": "Logistic Regression",
                "accuracy": 0.6667,
                "precision": 0.6056,
                "recall": 0.6667,
                "f1_score": 0.6056,
                "training_time_sec": 0.066,
                "inference_time_ms": 0.01,
                "confusion_matrix": [[7, 0, 0], [2, 5, 0], [2, 2, 0]]
            },
            "Calibrated Linear SVM": {
                "model_name": "Calibrated Linear SVM",
                "accuracy": 0.6111,
                "precision": 0.5890,
                "recall": 0.6111,
                "f1_score": 0.5920,
                "training_time_sec": 0.208,
                "inference_time_ms": 0.01,
                "confusion_matrix": [[6, 1, 0], [1, 4, 1], [1, 2, 2]]
            },
            "Bidirectional LSTM": {
                "model_name": "Bidirectional LSTM",
                "accuracy": 0.6111,
                "precision": 0.5940,
                "recall": 0.6111,
                "f1_score": 0.5890,
                "training_time_sec": 1.402,
                "inference_time_ms": 0.93,
                "confusion_matrix": [[6, 1, 0], [1, 4, 1], [2, 1, 2]]
            },
            "Random Forest": {
                "model_name": "Random Forest",
                "accuracy": 0.5556,
                "precision": 0.5230,
                "recall": 0.5556,
                "f1_score": 0.5180,
                "training_time_sec": 0.602,
                "inference_time_ms": 0.26,
                "confusion_matrix": [[5, 2, 0], [2, 4, 0], [2, 2, 1]]
            }
        }

    response = {
        "evaluation_dataset": "TruthLens Benchmark Test Set (Held-Out Stratified Split)",
        "evaluated": metrics_evaluated,
        "models": metrics_data,
        "classes": ["Likely Genuine", "Potentially Misleading", "Needs Further Verification"],
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    if not metrics_evaluated:
        response["warning"] = ("No trained metrics found. The values below are illustrative "
                                "placeholders. Run `python ml_pipeline/training/train_models.py` "
                                "to compute real benchmarks on the held-out test set.")
    return jsonify(response), 200
