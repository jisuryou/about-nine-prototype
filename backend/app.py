from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from pathlib import Path

from backend.config import SECRET_KEY, CORS_ORIGINS, DEBUG

# =========================
# App init
# =========================

app = Flask(__name__)
app.secret_key = SECRET_KEY
CORS(
    app,
    supports_credentials=True,
    origins=CORS_ORIGINS,
    resources={r"/api/*": {"origins": CORS_ORIGINS}},
)

# =========================
# Routes (API)
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
# Health check
# =========================

@app.route("/api/health")
def health():
    return jsonify(
        status="ok",
        env="development" if DEBUG else "production"
    )

# =========================
# Frontend serving (SPA)
# =========================

FRONTEND_DIR = Path(__file__).resolve().parents[1] / "frontend"

@app.route("/", defaults={"path": "index.html"})
@app.route("/<path:path>")
def serve_frontend(path):
    file_path = FRONTEND_DIR / path

    # 정적 파일 존재하면 그대로 서빙
    if file_path.exists() and file_path.is_file():
        return send_from_directory(FRONTEND_DIR, path)

    # SPA fallback (react / vanilla 모두 대응)
    return send_from_directory(FRONTEND_DIR, "index.html")

# =========================
# Error handlers
# =========================

@app.errorhandler(404)
def not_found(e):
    return jsonify(success=False, message="Not found"), 404


@app.errorhandler(500)
def internal_error(e):
    return jsonify(success=False, message="Internal server error"), 500


# =========================
# Run
# =========================

if __name__ == "__main__":
    print("🚀 About Nine API Server")
    print(f"📍 http://127.0.0.1:5001")
    print(f"🔧 DEBUG = {DEBUG}")
    app.run(
        host="0.0.0.0",
        port=5001,
        debug=DEBUG
    )
