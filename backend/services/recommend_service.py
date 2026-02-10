import numpy as np
from firebase_admin import firestore

db = firestore.client()

FEATURES = ["turn","flow","romantic","lsm","preference","pitch"]


def sim(a,b):
    return max(0, 1-abs(a-b)/100)


def delta(a,b):
    return (a-b)/100


def pair_score(pa,pb):

    feats = []
    for f in FEATURES:
        feats.append(sim(pa[f],pb[f]))
        feats.append(delta(pa[f],pb[f]))

    return float(np.mean(feats))   # 간단 버전

def recommend_for_user(uid, top_k=5):
    if not uid:
        return []

    profiles = {
        d.id: d.to_dict()
        for d in db.collection("user_profiles").stream()
    }

    users = {
        d.id: d.to_dict()
        for d in db.collection("users").stream()
    }

    me = profiles.get(uid)
    me_user = users.get(uid, {})
    if not me:
        return []

    my_blocked = set(me_user.get("blocked_users") or [])

    scores = []

    for other, p in profiles.items():
        if other == uid:
            continue

        other_user = users.get(other) or {}
        other_blocked = set(other_user.get("blocked_users") or [])
        if other in my_blocked or uid in other_blocked:
            continue

        s = pair_score(me,p)
        scores.append((other,s))

    scores.sort(key=lambda x:-x[1])
    return scores[:top_k]
