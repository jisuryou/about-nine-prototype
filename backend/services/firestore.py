import json
import os
from firebase_admin import credentials, firestore, initialize_app
from backend.config import FIREBASE_SERVICE_ACCOUNT_JSON

_app = None
_db = None

def get_firestore():
    global _app, _db
    if _db:
        return _db

    if FIREBASE_SERVICE_ACCOUNT_JSON:
        cred = credentials.Certificate(json.loads(FIREBASE_SERVICE_ACCOUNT_JSON))
    else:
        cred = credentials.Certificate("serviceAccountKey.json")

    _app = initialize_app(cred)
    _db = firestore.client()
    return _db
