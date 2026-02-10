from flask import Blueprint, request, jsonify, session
from backend.services.analysis_service import analyze_talk_pipeline
from backend.services.recommend_service import recommend_for_user

match_bp = Blueprint("match", __name__, url_prefix="/api/match")


@match_bp.route("/analyze-talk", methods=["POST"])
def analyze_talk():
    data = request.get_json()
    talk_id = data.get("talk_id")

    if not talk_id:
        return jsonify(success=False), 400

    analyze_talk_pipeline(talk_id)

    return jsonify(success=True)

@match_bp.route("/recommend", methods=["GET"])
def recommend():
    uid = session.get("user_id") or request.headers.get("X-User-ID")
    if not uid:
        return jsonify(success=False, message="not logged in"), 401
    users = recommend_for_user(uid)
    return jsonify(users=[u for u,_ in users])
