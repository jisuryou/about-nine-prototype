from flask import Blueprint, jsonify, request
from backend.services.rtdb import get_rtdb

presence_bp = Blueprint("presence", __name__, url_prefix="/api/presence")
rtdb = get_rtdb()


@presence_bp.route("/<user_id>", methods=["POST"])
def set_presence(user_id):
    if not rtdb:
        return jsonify(success=False, message="RTDB not configured"), 501

    data = request.get_json() or {}
    online = bool(data.get("online", True))

    rtdb.child("presence").child(user_id).set({
        "online": online,
        "updated_at": "now"
    })
    return jsonify(success=True, online=online)
