from flask import Blueprint, jsonify
from backend.services.firestore import get_firestore

debug_bp = Blueprint("debug", __name__, url_prefix="/api/debug")

@debug_bp.route("/users")
def list_users():
    db = get_firestore()
    users = [d.to_dict() for d in db.collection("users").stream()]
    return jsonify(users=users)
