from firebase_admin import db
from backend.config import FIREBASE_DB_URL

_rtdb = None

def get_rtdb():
    global _rtdb
    if not FIREBASE_DB_URL:
        return None
    if _rtdb:
        return _rtdb
    _rtdb = db.reference("/")
    return _rtdb
