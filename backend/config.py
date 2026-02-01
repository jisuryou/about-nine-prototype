import os
from dotenv import load_dotenv

load_dotenv()

ENV = os.getenv("FLASK_ENV", "development")
DEBUG = ENV != "production"

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY and not DEBUG:
    raise RuntimeError("SECRET_KEY must be set in production")

raw_cors_origins = os.getenv("CORS_ORIGINS")
if raw_cors_origins:
    CORS_ORIGINS = [origin.strip() for origin in raw_cors_origins.split(",") if origin.strip()]
else:
    CORS_ORIGINS = [
        "http://localhost:5001",
        "http://127.0.0.1:5001",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

# Firebase
FIREBASE_DB_URL = os.getenv("FIREBASE_DB_URL")
FIREBASE_SERVICE_ACCOUNT_JSON = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
FIREBASE_SERVICE_ACCOUNT_PATH = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH")
