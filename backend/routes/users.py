from flask import Blueprint, jsonify, session
from backend.services.firestore import get_firestore
from backend.utils.request import get_json
from datetime import datetime
import secrets

users_bp = Blueprint("users", __name__, url_prefix="/api")
db = get_firestore()

@users_bp.route("/register", methods=["POST"])
def register():
    data, err, code = get_json()
    if err:
        return err, code

    user_id = secrets.token_urlsafe(16)
    db.collection("users").document(user_id).set({
        **data,
        "id": user_id,
        "created_at": datetime.utcnow().isoformat()
    })

    session["user_id"] = user_id
    return jsonify(success=True, user_id=user_id)
