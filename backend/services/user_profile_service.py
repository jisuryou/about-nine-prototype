from firebase_admin import firestore

db = firestore.client()

FEATURES = ["turn","flow","romantic","lsm","preference","pitch"]


def update_user_profile(uid, feats, chemistry):

    ref = db.collection("user_profiles").document(uid)
    snap = ref.get()

    if not snap.exists:
        data = {
            "count": 1,
            **{f: feats[f] for f in FEATURES}
        }
        ref.set(data)
        return

    p = snap.to_dict()
    n = p["count"]

    new = {
        "count": n + 1
    }

    for f in FEATURES:
        new[f] = (p[f]*n + feats[f])/(n+1)

    ref.update(new)
