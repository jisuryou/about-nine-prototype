import os
import tempfile
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


class StorageLoader:
    def __init__(self, local_root: str | None = None):
        self.local_root = local_root or os.path.join(
            tempfile.gettempdir(), "about_nine_recordings"
        )

    def download_recordings(self, recording_files, talk_id: str):
        """
        recording_files: list of dicts with at least fileName/storage_path.
        returns: [{"uid": ..., "storage_path": ..., "local_path": ...}, ...]
        """
        bucket = get_bucket()
        local_dir = os.path.join(self.local_root, str(talk_id))
        os.makedirs(local_dir, exist_ok=True)

        downloaded = []
        for item in recording_files:
            if not isinstance(item, dict):
                continue
            storage_path = (
                item.get("fileName")
                or item.get("storage_path")
                or item.get("path")
                or item.get("filename")
            )
            if not storage_path:
                continue
            filename = os.path.basename(storage_path)
            local_path = os.path.join(local_dir, filename)

            blob = bucket.blob(storage_path)
            blob.download_to_filename(local_path)

            downloaded.append(
                {
                    "uid": item.get("uid"),
                    "storage_path": storage_path,
                    "local_path": local_path,
                }
            )

        return downloaded
