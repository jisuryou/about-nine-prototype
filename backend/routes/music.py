import base64
import os
import time

import requests
from flask import Blueprint, jsonify, request

music_bp = Blueprint("music", __name__, url_prefix="/api/music")

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_MARKET = os.getenv("SPOTIFY_MARKET", "US")

SPOTIFY_SEARCH_LIMIT = 10
SPOTIFY_SCAN_PAGES = 5

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
        try:
            requested_limit = int(request.args.get("limit", SPOTIFY_SEARCH_LIMIT))
        except (TypeError, ValueError):
            requested_limit = SPOTIFY_SEARCH_LIMIT
        limit = max(1, min(requested_limit, SPOTIFY_SEARCH_LIMIT))
        offset = request.args.get("offset")
        offset_value = None
        if offset is not None:
            try:
                offset_value = max(0, int(offset))
            except (TypeError, ValueError):
                offset_value = None

        params = {
            "q": q,
            "type": "track",
            "limit": limit,
            "market": SPOTIFY_MARKET,
        }
        if offset_value is not None:
            params["offset"] = offset_value

        items = []
        total = None
        current_offset = params.get("offset", 0) or 0
        pages = 0

        while len(items) < limit and pages < SPOTIFY_SCAN_PAGES:
            r = requests.get(
                "https://api.spotify.com/v1/search",
                params={
                    **params,
                    "limit": SPOTIFY_SEARCH_LIMIT,
                    "offset": current_offset,
                },
                headers={"Authorization": f"Bearer {token}"},
                timeout=5,
            )

            r.raise_for_status()
            data = r.json().get("tracks", {})
            page_items = data.get("items", [])
            if total is None:
                total = data.get("total")

            if not page_items:
                break

            items.extend(page_items)
            pages += 1
            current_offset += len(page_items)
            if total is not None and current_offset >= total:
                break

    except Exception as e:
        details = ""
        if hasattr(e, "response") and e.response is not None:
            details = e.response.text
        print("🔥 Spotify API error:", e, details)
        return jsonify(success=True, tracks=[])

    tracks = []
    fallback_tracks = []
    seen_ids = set()

    for it in items:
        preview_url = it.get("preview_url")
        album_images = it.get("album", {}).get("images", [])
        image_url = album_images[0]["url"] if album_images else ""
        artists = ", ".join([a.get("name", "") for a in it.get("artists", [])])
        track_id = it.get("id")

        track = {
            "id": track_id,
            "uri": it.get("uri"),
            "name": it.get("name"),
            "artist": artists,
            "image": image_url,
            "preview_url": preview_url,
            "has_preview": bool(preview_url),
            "duration_ms": it.get("duration_ms"),
        }

        if track_id and track_id in seen_ids:
            continue
        if track_id:
            seen_ids.add(track_id)

        if preview_url:
            tracks.append(track)
        else:
            fallback_tracks.append(track)

        if len(tracks) >= limit:
            break

    if len(tracks) < limit:
        for track in fallback_tracks:
            if len(tracks) >= limit:
                break
            tracks.append(track)

    return jsonify(success=True, tracks=tracks)
