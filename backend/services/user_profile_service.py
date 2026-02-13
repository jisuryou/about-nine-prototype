import time
from typing import Iterable, List, Optional

import numpy as np
from firebase_admin import firestore

from backend.services.embedding_service import normalize_vector
from backend.services.firestore import get_firestore

def _get_db():
    return get_firestore()


def _now_ms() -> int:
    return int(time.time() * 1000)


def _as_vector(values: Iterable) -> Optional[List[float]]:
    if not values:
        return None
    try:
        arr = np.array(list(values), dtype=float)
    except Exception:
        return None
    if arr.ndim != 1 or arr.size == 0:
        return None
    return arr.tolist()


def update_user_embedding(uid: str, pair_embedding, go: Optional[bool], alpha: float = 0.2) -> bool:
    if not uid:
        return False

    pair_vec = _as_vector(pair_embedding)
    if not pair_vec:
        return False

    db = _get_db()
    ref = db.collection("users").document(uid)
    snap = ref.get()
    data = snap.to_dict() or {}

    old_vec = (data.get("embedding") or {}).get("vector")
    old_vec = _as_vector(old_vec)

    pair_arr = np.array(pair_vec, dtype=float)

    if old_vec is None or len(old_vec) != len(pair_vec):
        old_arr = np.zeros_like(pair_arr)
    else:
        old_arr = np.array(old_vec, dtype=float)

    if go is None:
        # EMA fallback when explicit go/no isn't available
        new_arr = (1 - alpha) * old_arr + alpha * pair_arr
    else:
        direction = 1.0 if go else -1.0
        new_arr = old_arr + direction * alpha * pair_arr

    new_vec = normalize_vector(new_arr.tolist())

    ref.set(
        {
            "embedding": {
                "vector": new_vec,
                "dim": len(new_vec),
                "updated_at": _now_ms(),
            }
        },
        merge=True,
    )
    return True


def update_user_stats(uid: str, is_go: bool) -> bool:
    if not uid:
        return False

    db = _get_db()
    ref = db.collection("users").document(uid)
    txn = db.transaction()

    @firestore.transactional
    def _update(transaction):
        snap = ref.get(transaction=transaction)
        data = snap.to_dict() or {}
        stats = data.get("stats") or {}
        talk_count = int(stats.get("talk_count") or 0)
        go_count = int(stats.get("go_count") or 0)

        talk_count += 1
        if is_go:
            go_count += 1

        go_rate = (go_count / talk_count) if talk_count else 0.0

        transaction.set(
            ref,
            {
                "stats": {
                    "talk_count": talk_count,
                    "go_count": go_count,
                    "go_rate": go_rate,
                }
            },
            merge=True,
        )

    _update(txn)
    return True
