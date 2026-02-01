import os
from dotenv import load_dotenv

load_dotenv()

ENV = os.getenv("FLASK_ENV", "development")
DEBUG = ENV != "production"

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY and not DEBUG:
    raise RuntimeError("SECRET_KEY must be set in production")

CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")

# Firebase
FIREBASE_DB_URL = os.getenv("FIREBASE_DB_URL")
FIREBASE_SERVICE_ACCOUNT_JSON = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
