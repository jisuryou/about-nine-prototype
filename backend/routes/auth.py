import secrets
from flask import Blueprint, session, jsonify
from backend.utils.request import get_json

from firebase_admin import auth as fb_auth

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

@auth_bp.route("/auth/firebase-login", methods=["POST"])
def firebase_login():
    data, err, code = get_json()
    if err:
        return err, code

    id_token = data.get("idToken")

    if not id_token:
        return jsonify(success=False, message="missing idToken"), 400

    try:
        decoded = fb_auth.verify_id_token(id_token)
    except Exception as e:
        print("🔥 token verify failed:", e)
        return jsonify(success=False, message="invalid token"), 401

    session["firebase_uid"] = decoded["uid"]
    session["phone_verified"] = True

    return jsonify(success=True)

