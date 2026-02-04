import requests
from flask import Blueprint, jsonify, request
import os

music_bp = Blueprint("music", __name__, url_prefix="/api/music")

YOUTUBE_KEY = os.getenv("YOUTUBE_API_KEY")

@music_bp.route("/search")
def search():
    q = request.args.get("q")
    if not q:
        return jsonify(success=True, tracks=[])

    r = requests.get(
        "https://www.googleapis.com/youtube/v3/search",
        params={
            "part": "snippet",
            "q": q + " official audio",  # ⭐ 정확도 ↑
            "type": "video",
            "maxResults": 25,
            "key": YOUTUBE_KEY,
        },
    )

    items = r.json().get("items", [])

    tracks = [{
        "id": it["id"]["videoId"],
        "name": it["snippet"]["title"],
        "artist": it["snippet"]["channelTitle"],
        "image": it["snippet"]["thumbnails"]["high"]["url"],
        "preview": f"https://www.youtube.com/watch?v={it['id']['videoId']}"
    } for it in items]

    return jsonify(success=True, tracks=tracks)

