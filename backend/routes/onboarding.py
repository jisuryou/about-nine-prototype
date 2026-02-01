from datetime import datetime

from flask import Blueprint, jsonify

from backend.services.firestore import get_firestore
from backend.utils.request import get_json

onboarding_bp = Blueprint("onboarding", __name__, url_prefix="/api/onboarding")
db = get_firestore()

@onboarding_bp.route("/save", methods=["POST"])
def save_onboarding():
    data, err, code = get_json()
    if err:
        return err, code

    user_id = data.get("user_id")
    profile = data.get("profile")

    if not user_id or profile is None:
        return jsonify(success=False, message="user_id and profile are required"), 400

    db.collection("users").document(user_id).set(
        {
            "onboarding_profile": profile,
            "onboarding_completed": True,
            "onboarding_updated_at": datetime.utcnow().isoformat(),
        },
        merge=True,
    )

    return jsonify(success=True)