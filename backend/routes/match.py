from flask import Blueprint, request, jsonify
from backend.services.analysis_service import analyze_talk_pipeline
from backend.services.match_service import recommend_for_user

bp = Blueprint("match", __name__, url_prefix="/api/match")


@bp.route("/analyze-talk", methods=["POST"])
def analyze_talk():
    data = request.get_json()
    talk_id = data.get("talk_id")

    if not talk_id:
        return jsonify(success=False), 400

    analyze_talk_pipeline(talk_id)

    return jsonify(success=True)

@bp.route("/recommend", methods=["GET"])
def recommend():
    uid = request.headers.get("X-User-ID")
    users = recommend_for_user(uid)
    return jsonify(users=[u for u,_ in users])