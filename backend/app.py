from flask import Flask
from flask_cors import CORS
from backend.config import SECRET_KEY, CORS_ORIGINS, DEBUG

app = Flask(__name__)
app.secret_key = SECRET_KEY
CORS(app, supports_credentials=True, origins=CORS_ORIGINS)

# route 등록
from backend.routes.auth import auth_bp
from backend.routes.users import users_bp
from backend.routes.music import music_bp
from backend.routes.presence import presence_bp
from backend.routes.debug import debug_bp

app.register_blueprint(auth_bp)
app.register_blueprint(users_bp)
app.register_blueprint(music_bp)
app.register_blueprint(presence_bp)

if DEBUG:
    app.register_blueprint(debug_bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=DEBUG)
