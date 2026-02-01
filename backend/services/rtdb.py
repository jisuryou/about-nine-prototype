import firebase_admin
from firebase_admin import db
from backend.config import FIREBASE_DB_URL

_rtdb = None


def get_rtdb():
    global _rtdb

    # RTDB 안 쓰는 환경 (dev / test)
    if not FIREBASE_DB_URL:
        return None

    if _rtdb:
        return _rtdb

    # Firebase app이 이미 초기화돼 있어야 함
    if not firebase_admin._apps:
        raise RuntimeError(
            "Firebase app not initialized. "
            "Initialize Firestore first."
        )

    _rtdb = db.reference("/", url=FIREBASE_DB_URL)
    return _rtdb
