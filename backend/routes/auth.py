import secrets
from datetime import datetime
from flask import Blueprint, session, jsonify
from backend.utils.request import get_json
from backend.services.firestore import get_firestore
from firebase_admin import auth as fb_auth

auth_bp = Blueprint("auth", __name__, url_prefix="/api")


# =========================
# Invite
# =========================
@auth_bp.route("/verify-invite", methods=["POST"])
def verify_invite():
    data, err, code = get_json()
    if err:
        return err, code

    if data.get("code") in ["9191", "ABOUTNINE"]:
        session["invite_verified"] = True
        return jsonify(success=True)

    return jsonify(success=False), 400


# =========================
# Firebase Login
# =========================
@auth_bp.route("/auth/firebase-login", methods=["POST"])
def firebase_login():

    # 🔥 invite 필수
    if not session.get("invite_verified"):
        return jsonify(success=False, message="invite required"), 403

    data, err, code = get_json()
    if err:
        return err, code

    id_token = data.get("idToken")
    if not id_token:
        return jsonify(success=False, message="missing idToken"), 400

    try:
        decoded = fb_auth.verify_id_token(id_token)
    except Exception:
        return jsonify(success=False, message="invalid token"), 401

    firebase_uid = decoded["uid"]
    db = get_firestore()

    # =========================
    # user 조회
    # =========================
    query = (
        db.collection("users")
        .where("firebase_uid", "==", firebase_uid)
        .limit(1)
        .get()
    )

    doc = query[0] if query else None

    if doc:
        user_id = doc.to_dict()["id"]
    else:
        user_id = secrets.token_urlsafe(16)
        db.collection("users").document(user_id).set({
            "id": user_id,
            "firebase_uid": firebase_uid,
            "created_at": datetime.utcnow().isoformat(),
            "playlist": [],
            "location": None,
            "onboarding_completed": False,
        })

    # =========================
    # session
    # =========================
    session["user_id"] = user_id
    session["firebase_uid"] = firebase_uid
    session["phone_verified"] = True
    session.permanent = True

    # invite 1회용
    session.pop("invite_verified", None)

    return jsonify(success=True, user_id=user_id)
