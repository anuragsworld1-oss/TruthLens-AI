"""
TruthLens AI - Core Analysis & Verification REST API Routes
Handles text analysis, URL scraping, document uploads, image inspection,
and persistence to database.
"""

import os
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename

from app.extensions import limiter
from app.models.database import db, User, Article, AnalysisResult, Claim, EvidenceSource, Review
from app.services.prediction_service import prediction_service
from app.services.source_intelligence import extract_article_from_url
from app.services.doc_parser import parse_document
from app.services.image_provenance import inspect_image_provenance

analysis_bp = Blueprint("analysis", __name__, url_prefix="/api")

def _save_analysis_to_db(article_data: dict, analysis_data: dict, user_id=None) -> AnalysisResult:
    """Helper function to record article, analysis results, and claims into database."""
    article = Article(
        user_id=int(user_id) if user_id else None,
        title=article_data.get("title", "Untitled News Article"),
        content=article_data.get("content", ""),
        source_url=article_data.get("source_url"),
        language=analysis_data.get("language", "en"),
        word_count=len(article_data.get("content", "").split())
    )
    db.session.add(article)
    db.session.flush()

    res = AnalysisResult(
        article_id=article.id,
        predicted_class=analysis_data.get("prediction", "Needs Further Verification"),
        credibility_score=analysis_data.get("credibility_score", 50.0),
        model_confidence=analysis_data.get("consensus_confidence", 50.0),
        model_agreement_percentage=analysis_data.get("model_agreement_percentage"),
        consensus_confidence=analysis_data.get("consensus_confidence"),
        limitations_disclaimer=analysis_data.get("limitations_disclaimer"),
        uncertainty_level=analysis_data.get("uncertainty_level"),
        outcome=analysis_data.get("outcome"),
        credibility_reasoning=analysis_data.get("credibility_reasoning"),
        model_predictions=analysis_data.get("model_predictions"),
        linguistic_analysis=analysis_data.get("linguistic_analysis"),
        ai_writing_style=analysis_data.get("ai_writing_style"),
        explanation=analysis_data.get("explainable_ai"),
        recommended_actions=analysis_data.get("recommended_actions")
    )
    db.session.add(res)
    db.session.flush()

    # Save Claims and their Sources
    for c_data in analysis_data.get("extracted_claims", []):
        claim = Claim(
            analysis_id=res.id,
            claim_text=c_data.get("claim_text", ""),
            normalized_claim=c_data.get("normalized_claim"),
            verification_status=c_data.get("verification_status", "Insufficient evidence"),
            evidence_summary=c_data.get("evidence_summary", "")
        )
        db.session.add(claim)
        db.session.flush()

        for s_data in c_data.get("supporting_sources", []) + c_data.get("contradicting_sources", []):
            src = EvidenceSource(
                claim_id=claim.id,
                source_title=s_data.get("title", "Reference Source"),
                source_url=s_data.get("url", "#"),
                publisher=s_data.get("publisher"),
                published_at=s_data.get("published_at"),
                stance=s_data.get("stance", "support")
            )
            db.session.add(src)

    db.session.commit()
    return res

def _enrich_response(db_res: AnalysisResult, analysis_data: dict) -> dict:
    """Builds the JSON response from the persisted record, merging display-only
    fields that are not separate DB columns (models_analyzed, language override).
    Persisted fields (agreement, consensus, disclaimer) come from to_dict()."""
    resp = db_res.to_dict()
    resp["analysis_id"] = db_res.id
    resp.setdefault("models_analyzed", analysis_data.get("models_analyzed"))
    # Display-only fields not stored as separate columns.
    resp.setdefault("confidence_signals", analysis_data.get("confidence_signals"))
    resp.setdefault("evidence_signal", analysis_data.get("evidence_signal"))
    resp.setdefault("credibility_reasoning", analysis_data.get("credibility_reasoning"))
    resp.setdefault("outcome", analysis_data.get("outcome"))
    resp.setdefault("uncertainty_level", analysis_data.get("uncertainty_level"))
    return resp

@analysis_bp.route("/analyze/text", methods=["POST"])
@limiter.limit("40 per minute")
@jwt_required(optional=True)
def analyze_text():
    data = request.get_json() or {}
    text = data.get("text", "").strip()
    title = data.get("title", "").strip()
    language = data.get("language")
    source_url = data.get("source_url", "").strip()

    if not text:
        return jsonify({"error": "Article text is required for analysis."}), 400

    try:
        user_id = get_jwt_identity()
        analysis_res = prediction_service.analyze(text=text, title=title, source_url=source_url, language=language)
        
        # Persist to database
        db_res = _save_analysis_to_db(
            article_data={"title": title or "Analyzed Text Snippet", "content": text, "source_url": source_url},
            analysis_data=analysis_res,
            user_id=user_id
        )

        resp = _enrich_response(db_res, analysis_res)
        return jsonify(resp), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500

@analysis_bp.route("/analyze/url", methods=["POST"])
@limiter.limit("20 per minute")
@jwt_required(optional=True)
def analyze_url():
    data = request.get_json() or {}
    url = data.get("url", "").strip()

    if not url:
        return jsonify({"error": "Target article URL is required."}), 400

    try:
        user_id = get_jwt_identity()
        # Safe SSRF-protected extraction
        extracted = extract_article_from_url(url)
        
        if not extracted.get("text") or len(extracted["text"].strip()) < 20:
            return jsonify({"error": "Unable to extract sufficient article text from the submitted URL."}), 400

        analysis_res = prediction_service.analyze(
            text=extracted["text"],
            title=extracted["title"],
            source_url=url
        )
        analysis_res["publisher_intelligence"] = extracted.get("publisher_intelligence")
        analysis_res["author"] = extracted.get("author")
        analysis_res["published_at"] = extracted.get("published_at")

        db_res = _save_analysis_to_db(
            article_data={"title": extracted["title"], "content": extracted["text"], "source_url": url},
            analysis_data=analysis_res,
            user_id=user_id
        )

        resp = _enrich_response(db_res, analysis_res)
        resp["publisher_intelligence"] = extracted.get("publisher_intelligence")
        resp["author"] = extracted.get("author")
        resp["published_at"] = extracted.get("published_at")
        return jsonify(resp), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": f"URL analysis failed: {str(e)}"}), 500

@analysis_bp.route("/analyze/upload", methods=["POST"])
@limiter.limit("20 per minute")
@jwt_required(optional=True)
def analyze_upload():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded."}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected."}), 400

    filename = secure_filename(file.filename)
    upload_dir = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_dir, exist_ok=True)
    save_path = os.path.join(upload_dir, filename)
    file.save(save_path)

    try:
        user_id = get_jwt_identity()
        doc_data = parse_document(save_path, filename)

        if not doc_data.get("text") or len(doc_data["text"]) < 20:
            return jsonify({"error": "Extracted document text is too short for analysis."}), 400

        analysis_res = prediction_service.analyze(
            text=doc_data["text"],
            title=doc_data["title"],
            source_url=f"Document: {filename}"
        )

        db_res = _save_analysis_to_db(
            article_data={"title": doc_data["title"], "content": doc_data["text"], "source_url": f"Uploaded File ({doc_data['file_format']})"},
            analysis_data=analysis_res,
            user_id=user_id
        )

        resp = _enrich_response(db_res, analysis_res)
        resp["file_format"] = doc_data["file_format"]
        return jsonify(resp), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": f"Document analysis failed: {str(e)}"}), 500
    finally:
        # Clean up temporary upload
        if os.path.exists(save_path):
            try:
                os.remove(save_path)
            except Exception:
                pass

@analysis_bp.route("/analyze/image", methods=["POST"])
def analyze_image():
    if "image" not in request.files:
        return jsonify({"error": "No image file uploaded."}), 400

    image_file = request.files["image"]
    if image_file.filename == "":
        return jsonify({"error": "No image selected."}), 400

    filename = secure_filename(image_file.filename)
    upload_dir = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_dir, exist_ok=True)
    save_path = os.path.join(upload_dir, filename)
    image_file.save(save_path)

    try:
        provenance = inspect_image_provenance(save_path, filename)
        return jsonify(provenance), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": f"Image inspection failed: {str(e)}"}), 500
    finally:
        if os.path.exists(save_path):
            try:
                os.remove(save_path)
            except Exception:
                pass

@analysis_bp.route("/analysis/history", methods=["GET"])
def get_history():
    query = AnalysisResult.query.order_by(AnalysisResult.created_at.desc())
    
    # Filter by category
    category = request.args.get("category")
    if category:
        query = query.filter(AnalysisResult.predicted_class == category)

    # Search filter
    search = request.args.get("search", "").strip()
    if search:
        query = query.join(Article).filter(
            (Article.title.ilike(f"%{search}%")) | (Article.content.ilike(f"%{search}%"))
        )

    try:
        page = max(1, int(request.args.get("page", 1)))
        per_page = min(50, max(1, int(request.args.get("limit", 15))))
    except (TypeError, ValueError):
        return jsonify({"error": "page and limit must be integers."}), 400
    total_count = query.count()
    results = query.offset((page - 1) * per_page).limit(per_page).all()

    return jsonify({
        "total": total_count,
        "page": page,
        "per_page": per_page,
        "items": [r.to_dict() for r in results]
    }), 200

@analysis_bp.route("/analysis/<int:analysis_id>", methods=["GET"])
def get_analysis_detail(analysis_id):
    res = AnalysisResult.query.get(analysis_id)
    if not res:
        return jsonify({"error": f"Analysis report #{analysis_id} not found."}), 404
    return jsonify(res.to_dict()), 200

@analysis_bp.route("/analysis/<int:analysis_id>", methods=["DELETE"])
def delete_analysis(analysis_id):
    res = AnalysisResult.query.get(analysis_id)
    if not res:
        return jsonify({"error": f"Analysis #{analysis_id} not found."}), 404

    article = res.article
    if article is not None:
        db.session.delete(article)
    else:
        db.session.delete(res)
    db.session.commit()
    return jsonify({"message": f"Analysis #{analysis_id} successfully deleted."}), 200

@analysis_bp.route("/review", methods=["POST"])
@jwt_required(optional=True)
def submit_review():
    data = request.get_json() or {}
    analysis_id = data.get("analysis_id")
    status = data.get("status", "Verified")
    notes = data.get("notes", "")

    if not analysis_id:
        return jsonify({"error": "analysis_id is required."}), 400

    user_id = get_jwt_identity()
    review = Review(
        analysis_id=int(analysis_id),
        reviewer_id=int(user_id) if user_id else None,
        review_status=status,
        notes=notes
    )
    db.session.add(review)
    db.session.commit()

    return jsonify({"message": "Review submitted successfully.", "review": review.to_dict()}), 201
