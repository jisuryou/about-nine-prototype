from datetime import datetime
from flask import Blueprint, jsonify, session

from backend.services.firestore import get_firestore
from backend.utils.request import get_json

onboarding_bp = Blueprint("onboarding", __name__, url_prefix="/api/onboarding")


@onboarding_bp.route("/save", methods=["POST"])
def save_onboarding():

    user_id = session.get("user_id")
    if not user_id:
        return jsonify(success=False, message="not logged in"), 401

    data, err, code = get_json()
    if err:
        return err, code

    profile = data.get("profile")

    if profile is None:
        return jsonify(success=False, message="profile is required"), 400

    db = get_firestore()

    db.collection("users").document(user_id).set(
        {
            "onboarding_profile": profile,
            "onboarding_completed": True,
            "onboarding_updated_at": datetime.utcnow().isoformat(),
        },
        merge=True,
    )

    return jsonify(success=True)
