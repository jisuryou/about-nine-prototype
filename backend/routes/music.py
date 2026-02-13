import base64
import os
import time

import requests
from flask import Blueprint, jsonify, request

music_bp = Blueprint("music", __name__, url_prefix="/api/music")

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

_spotify_token = None
_spotify_token_expires_at = 0


def get_spotify_token():
    global _spotify_token, _spotify_token_expires_at

    if _spotify_token and time.time() < _spotify_token_expires_at - 30:
        return _spotify_token

    if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
        return None

    auth = f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}"
    encoded = base64.b64encode(auth.encode("utf-8")).decode("utf-8")

    try:
        r = requests.post(
            "https://accounts.spotify.com/api/token",
            data={"grant_type": "client_credentials"},
            headers={"Authorization": f"Basic {encoded}"},
            timeout=5,
        )
        r.raise_for_status()
        data = r.json()
        _spotify_token = data.get("access_token")
        expires_in = data.get("expires_in", 3600)
        _spotify_token_expires_at = time.time() + int(expires_in)
        return _spotify_token
    except Exception as e:
        print("🔥 Spotify token error:", e)
        return None

@music_bp.route("/search")
def search():
    q = request.args.get("q")

    if not q:
        return jsonify(success=True, tracks=[])

    token = get_spotify_token()
    if not token:
        return (
            jsonify(success=False, message="SPOTIFY_CLIENT_ID/SECRET missing"),
            500,
        )

    try:
        r = requests.get(
            "https://api.spotify.com/v1/search",
            params={
                "q": q,
                "type": "track",
                "limit": 25,
                "market": "US",
            },
            headers={"Authorization": f"Bearer {token}"},
            timeout=5,
        )

        r.raise_for_status()
        items = r.json().get("tracks", {}).get("items", [])

    except Exception as e:
        print("🔥 Spotify API error:", e)
        return jsonify(success=True, tracks=[])

    tracks = []

    for it in items:
        album_images = it.get("album", {}).get("images", [])
        image_url = album_images[0]["url"] if album_images else ""
        artists = ", ".join([a.get("name", "") for a in it.get("artists", [])])

        tracks.append(
            {
                "id": it.get("id"),
                "name": it.get("name"),
                "artist": artists,
                "image": image_url,
                "preview_url": it.get("preview_url"),
            }
        )

    return jsonify(success=True, tracks=tracks)
