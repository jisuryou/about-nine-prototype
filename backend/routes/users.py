from datetime import datetime
import secrets
from flask import Blueprint, jsonify, session
from backend.services.firestore import get_firestore
from backend.utils.request import get_json

users_bp = Blueprint("users", __name__, url_prefix="/api")

@users_bp.route("/register", methods=["POST"])
def register():
    data, err, code = get_json()
    if err:
        return err, code

    user_id = secrets.token_urlsafe(16)
    payload = {
        **data,
        "id": user_id,
        "created_at": datetime.utcnow().isoformat(),
    }

    session["user_id"] = user_id
    
    try:
        db = get_firestore()
        db.collection("users").document(user_id).set(payload)
    except RuntimeError as error:
        return jsonify(
            success=True,
            user_id=user_id,
            warning=str(error),
        )

    return jsonify(success=True, user_id=user_id)
