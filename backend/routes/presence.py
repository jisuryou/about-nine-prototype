from flask import Blueprint, jsonify
from backend.services.rtdb import get_rtdb
from datetime import datetime

presence_bp = Blueprint("presence", __name__, url_prefix="/api/presence")
rtdb = get_rtdb()

@presence_bp.route("/<user_id>", methods=["POST"])
def set_presence(user_id):
    if not rtdb:
        return jsonify(success=False), 500
    rtdb.child("presence").child(user_id).set({
        "online": True,
        "updated_at": datetime.utcnow().isoformat()
    })
    return jsonify(success=True)
