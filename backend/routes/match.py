from flask import Blueprint, request, jsonify, session
from backend.services.analysis_service import analyze_talk_pipeline
from backend.services.recommend_service import recommend_for_user

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
    return jsonify(users=[u for u,_ in users])
