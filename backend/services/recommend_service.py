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

    profiles = {
        d.id: d.to_dict()
        for d in db.collection("user_profiles").stream()
    }

    me = profiles[uid]

    scores = []

    for other, p in profiles.items():
        if other == uid:
            continue

        s = pair_score(me,p)
        scores.append((other,s))

    scores.sort(key=lambda x:-x[1])
    return scores[:top_k]
