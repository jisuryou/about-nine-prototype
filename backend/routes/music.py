from flask import Blueprint, jsonify, request

music_bp = Blueprint("music", __name__, url_prefix="/api/music")


@music_bp.route("/search")
def search_music():
    q = request.args.get("q", "")

    # prototype mock
    tracks = [
        {"id": "1", "name": "Blinding Lights", "artist": "The Weeknd"},
        {"id": "2", "name": "Levitating", "artist": "Dua Lipa"},
        {"id": "3", "name": "As It Was", "artist": "Harry Styles"},
    ]

    filtered = [t for t in tracks if q.lower() in t["name"].lower()]
    return jsonify(success=True, tracks=filtered)
