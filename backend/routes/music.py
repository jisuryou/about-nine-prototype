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

    if not YOUTUBE_KEY:
        return jsonify(success=False, message="YOUTUBE_API_KEY missing"), 500

    try:
        r = requests.get(
            "https://www.googleapis.com/youtube/v3/search",
            params={
                "part": "snippet",
                "q": f"{q} official audio",
                "type": "video",
                "maxResults": 25,
                "key": YOUTUBE_KEY,
            },
            timeout=5,
        )

        r.raise_for_status()
        items = r.json().get("items", [])

    except Exception as e:
        print("🔥 YouTube API error:", e)
        return jsonify(success=True, tracks=[])

    tracks = []

    for it in items:
        title = it["snippet"]["title"].lower()

        # 앨범/공식 위주 필터
        if any(x in title for x in ["live", "cover", "reaction", "shorts"]):
            continue

        tracks.append({
            "id": it["id"]["videoId"],
            "name": it["snippet"]["title"],
            "artist": it["snippet"]["channelTitle"],
            "image": it["snippet"]["thumbnails"]["high"]["url"],
            "preview": f"https://www.youtube.com/watch?v={it['id']['videoId']}"
        })

    return jsonify(success=True, tracks=tracks)
