from flask import Blueprint, request, jsonify, session
from backend.services.analysis_service import analyze_talk_pipeline
from backend.services.recommend_service import recommend_for_user
from backend.services.firestore import get_firestore

match_bp = Blueprint("match", __name__, url_prefix="/api/match")


@match_bp.route("/analyze-talk", methods=["POST"])
def analyze_talk():
    data = request.get_json() or {}
    talk_id = data.get("talk_id")

    if not talk_id:
        return jsonify(success=False, message="talk_id required"), 400

    try:
        result = analyze_talk_pipeline(talk_id)
        if not result.get("success", True):
            return jsonify(result), 500
        return jsonify(success=True, talk_id=talk_id)
    except Exception as e:
        return jsonify(success=False, message="analysis failed", error=str(e)), 500

@match_bp.route("/recommend", methods=["GET"])
def recommend():
    uid = session.get("user_id") or request.headers.get("X-User-ID")
    if not uid:
        return jsonify(success=False, message="not logged in"), 401
    users = recommend_for_user(uid)
    db = get_firestore()
    results = []
    for user_id, _score in users:
        doc = db.collection("users").document(user_id).get()
        if not doc.exists:
            continue
        data = doc.to_dict() or {}
        if "id" not in data:
            data["id"] = doc.id
        results.append(data)
    return jsonify(users=results)
