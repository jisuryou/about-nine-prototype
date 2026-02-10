import os
from firebase_admin import storage
from backend.config import FIREBASE_STORAGE_BUCKET
from backend.services.firestore import get_firestore

_bucket = None


def get_bucket():
    global _bucket
    if _bucket:
        return _bucket
    if not FIREBASE_STORAGE_BUCKET:
        raise RuntimeError(
            "FIREBASE_STORAGE_BUCKET is not set. "
            "Set it to your Firebase Storage bucket name "
            "(e.g. 'your-project-id.appspot.com')."
        )
    # Ensure Firebase app is initialized before accessing storage
    get_firestore()
    _bucket = storage.bucket()
    return _bucket


def download_prefix(prefix: str, local_dir: str):
    os.makedirs(local_dir, exist_ok=True)

    bucket = get_bucket()
    blobs = bucket.list_blobs(prefix=prefix)

    local_files = []
    for blob in blobs:
        filename = os.path.basename(blob.name)
        local_path = os.path.join(local_dir, filename)
        blob.download_to_filename(local_path)
        local_files.append(local_path)

    return local_files
