from firebase_admin import firestore
from .analyzers import (
    turn_taking,
    flow,
    romantic,
    lsm,
    preference,
    pitch
)
from .chemistry_model import ChemistryModel
from .user_profile_service import update_user_profile

db = firestore.client()
model = ChemistryModel()
model.load("chemistry_model.pkl")


def analyze_talk_pipeline(talk_id: str):

    talk_ref = db.collection("talk_history").document(talk_id)
    talk = talk_ref.get().to_dict()

    conversation = talk["conversation"]
    audio_paths = talk["audio_paths"]

    # 1. analyzers
    feats = {
        "turn": turn_taking.score(conversation),
        "flow": flow.score(conversation),
        "romantic": romantic.score(conversation),
        "lsm": lsm.score(conversation),
        "preference": preference.score(conversation),
        "pitch": pitch.score(audio_paths)
    }

    # 2. chemistry score
    chemistry = model.predict(feats)

    analysis = {
        "features": feats,
        "chemistry": chemistry
    }

    # 3. 저장
    talk_ref.update({"analysis": analysis})

    # 4. 🔥 user profile 업데이트
    for uid in talk["participants"]:
        update_user_profile(uid, feats, chemistry)

    return analysis
