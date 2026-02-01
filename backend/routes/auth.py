import secrets
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

@auth_bp.route("/send-sms", methods=["POST"])
def send_sms():
    data, err, code = get_json()
    if err:
        return err, code

    phone = data.get("phone")
    if not phone or not isinstance(phone, str):
        return jsonify(success=False, message="phone is required"), 400

    sanitized = "".join(ch for ch in phone if ch.isdigit())
    if len(sanitized) < 10:
        return jsonify(success=False, message="phone must be at least 10 digits"), 400

    sms_code = f"{secrets.randbelow(1000000):06d}"
    session["sms_phone"] = sanitized
    session["sms_code"] = sms_code
    session["sms_verified"] = False

    return jsonify(success=True, debug_code=sms_code)


@auth_bp.route("/verify-sms", methods=["POST"])
def verify_sms():
    data, err, code = get_json()
    if err:
        return err, code

    submitted_code = data.get("code")
    if not submitted_code:
        return jsonify(success=False, message="code is required"), 400

    expected_code = session.get("sms_code")
    if not expected_code:
        return jsonify(success=False, message="no code requested"), 400

    if str(submitted_code) != str(expected_code):
        return jsonify(success=False, message="invalid code"), 400

    session["sms_verified"] = True
    return jsonify(success=True)