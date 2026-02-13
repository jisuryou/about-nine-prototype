from typing import Dict, List, Tuple

import numpy as np

from backend.services.firestore import get_firestore


def _get_db():
    return get_firestore()


def _cosine(a: List[float], b: List[float]) -> float:
    if not a or not b:
        return 0.0
    va = np.array(a, dtype=float)
    vb = np.array(b, dtype=float)
    if va.size == 0 or vb.size == 0 or va.size != vb.size:
        return 0.0
    denom = (np.linalg.norm(va) * np.linalg.norm(vb))
    if denom == 0:
        return 0.0
    return float(np.dot(va, vb) / denom)


def recommend_for_user(uid: str, top_k: int = 10) -> List[Tuple[str, float]]:
    if not uid:
        return []

    db = _get_db()
    users: Dict[str, Dict] = {
        d.id: (d.to_dict() or {}) for d in db.collection("users").stream()
    }

    me = users.get(uid) or {}
    my_vec = (me.get("embedding") or {}).get("vector")
    if not my_vec:
        return []

    my_blocked = set(me.get("blocked_users") or [])

    scores: List[Tuple[str, float]] = []

    for other_id, user in users.items():
        if other_id == uid:
            continue

        other_blocked = set(user.get("blocked_users") or [])
        if other_id in my_blocked or uid in other_blocked:
            continue

        other_vec = (user.get("embedding") or {}).get("vector")
        if not other_vec:
            continue

        s = _cosine(my_vec, other_vec)
        scores.append((other_id, s))

    scores.sort(key=lambda x: -x[1])
    return scores[:top_k]
