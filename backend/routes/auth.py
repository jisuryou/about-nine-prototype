from flask import Blueprint, session, jsonify
from backend.utils.request import get_json

auth_bp = Blueprint("auth", __name__, url_prefix="/api")

@auth_bp.route("/verify-invite", methods=["POST"])
def verify_invite():
    data, err, code = get_json()
    if err:
        return err, code

    if data.get("code") in ["9191", "ABOUTNINE"]:
        session["invite_verified"] = True
        return jsonify(success=True)

    return jsonify(success=False), 400
