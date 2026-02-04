from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from pathlib import Path

from backend.config import SECRET_KEY, CORS_ORIGINS, DEBUG
from backend.services.firestore import get_firestore

get_firestore()

# =========================
# App init
# =========================

app = Flask(__name__)
app.secret_key = SECRET_KEY

CORS(app, supports_credentials=True, origins=CORS_ORIGINS)

if DEBUG:
    app.config.update(
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=False,
    )
else:
    app.config.update(
        SESSION_COOKIE_SAMESITE="None",
        SESSION_COOKIE_SECURE=True,
    )


# =========================
# API Routes
# =========================

from backend.routes.auth import auth_bp
from backend.routes.users import users_bp
from backend.routes.music import music_bp
from backend.routes.onboarding import onboarding_bp
from backend.routes.presence import presence_bp
from backend.routes.debug import debug_bp

app.register_blueprint(auth_bp)
app.register_blueprint(users_bp)
app.register_blueprint(music_bp)
app.register_blueprint(onboarding_bp)
app.register_blueprint(presence_bp)

if DEBUG:
    app.register_blueprint(debug_bp)


# =========================
# Health
# =========================

@app.route("/api/health")
def health():
    return jsonify(status="ok")


# =========================
# ⭐⭐⭐ 핵심 수정 부분
# =========================

FRONTEND_DIR = Path(__file__).resolve().parents[1] / "frontend"


# 1️⃣ 정적 파일만 서빙
@app.route("/<path:filename>")
def static_files(filename):
    file_path = FRONTEND_DIR / filename

    if file_path.exists():
        return send_from_directory(FRONTEND_DIR, filename)

    return jsonify(success=False, message="Not found"), 404


# 2️⃣ 루트만 index
@app.route("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")


# =========================
# Run
# =========================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=DEBUG)
