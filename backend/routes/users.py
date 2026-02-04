from datetime import datetime
from flask import Blueprint, jsonify, session
from backend.services.firestore import get_firestore
from backend.utils.request import get_json
import math

users_bp = Blueprint("users", __name__, url_prefix="/api/users")

# =========================
# Playlist
# =========================
@users_bp.route("/playlist", methods=["POST"])
def save_playlist():

    user_id = session.get("user_id")
    if not user_id:
        return jsonify(success=False, message="not logged in"), 401

    data, err, code = get_json()
    if err:
        return err, code

    tracks = data.get("tracks", [])

    db = get_firestore()

    db.collection("users").document(user_id).set({
        "playlist": tracks,
        "playlist_updated_at": datetime.utcnow().isoformat()
    }, merge=True)

    return jsonify(success=True)


# =========================
# Location
# =========================
@users_bp.route("/update-location", methods=["POST"])
def update_location():

    user_id = session.get("user_id")
    if not user_id:
        return jsonify(success=False, message="not logged in"), 401

    data, err, code = get_json()
    if err:
        return err, code

    db = get_firestore()

    db.collection("users").document(user_id).set({
        "location": {
            "lat": data.get("lat"),
            "lng": data.get("lng")
        }
    }, merge=True)

    return jsonify(success=True)


# =========================
# 거리 계산
# =========================
def distance_km(lat1, lng1, lat2, lng2):
    R = 6371
    d_lat = math.radians(lat2 - lat1)
    d_lng = math.radians(lng2 - lng1)

    a = (
        math.sin(d_lat/2)**2 +
        math.cos(math.radians(lat1)) *
        math.cos(math.radians(lat2)) *
        math.sin(d_lng/2)**2
    )

    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))


# =========================
# Nearby list
# =========================
@users_bp.route("/list")
def list_users():

    uid = session.get("user_id")
    if not uid:
        return jsonify(success=False), 401

    db = get_firestore()

    me = db.collection("users").document(uid).get().to_dict()

    my_loc = me.get("location")
    my_profile = me.get("onboarding_profile", {})

    my_gender_pref = my_profile.get("sexual_orientation")
    age_pref = my_profile.get("age_preference", {})

    users = []

    for doc in db.collection("users").stream():
        u = doc.to_dict()

        if u["id"] == uid:
            continue

        loc = u.get("location")
        if not loc or not my_loc:
            continue

        d = distance_km(
            my_loc["lat"], my_loc["lng"],
            loc["lat"], loc["lng"]
        )

        if d > 10:
            continue

        if my_gender_pref == "men" and u.get("gender") != "man":
            continue
        if my_gender_pref == "women" and u.get("gender") != "woman":
            continue

        if age_pref:
            age = u.get("age", 0)
            if not (age_pref["min"] <= age <= age_pref["max"]):
                continue

        users.append(u)

    return jsonify(success=True, users=users)
