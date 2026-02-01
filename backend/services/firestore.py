import json
from pathlib import Path
import firebase_admin
from firebase_admin import credentials, firestore, initialize_app
from backend.config import (
    FIREBASE_SERVICE_ACCOUNT_JSON,
    FIREBASE_SERVICE_ACCOUNT_PATH,
)

_app = None
_db = None


def get_firestore():
    global _app, _db

    if _db:
        return _db

    cred = None

    # 1️⃣ JSON env 방식 (권장)
    if FIREBASE_SERVICE_ACCOUNT_JSON:
        cred = credentials.Certificate(
            json.loads(FIREBASE_SERVICE_ACCOUNT_JSON)
        )

    # 2️⃣ 파일 path 방식
    elif FIREBASE_SERVICE_ACCOUNT_PATH:
        path = Path(FIREBASE_SERVICE_ACCOUNT_PATH)
        if not path.exists():
            raise RuntimeError(
                f"Firebase service account file not found: {path}"
            )
        cred = credentials.Certificate(str(path))

    # 3️⃣ 둘 다 없으면 명확한 에러
    else:
        raise RuntimeError(
            "Firebase credentials not configured. "
            "Set FIREBASE_SERVICE_ACCOUNT_JSON or FIREBASE_SERVICE_ACCOUNT_PATH"
        )

    # Firebase app 중복 초기화 방지
    if not firebase_admin._apps:
        _app = initialize_app(cred)

    _db = firestore.client()
    return _db
