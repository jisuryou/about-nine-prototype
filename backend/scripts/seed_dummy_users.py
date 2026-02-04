import random
import uuid
from datetime import datetime
import firebase_admin
from firebase_admin import firestore, db, credentials

from backend.services.firestore import get_firestore
from backend.services.rtdb import get_rtdb


db_fs = get_firestore()
rtdb = get_rtdb()

GENDERS = ["man", "woman", "non-binary"]

FIRST = ["Alex","Sam","Chris","Jamie","Taylor","Jordan","Casey","Riley","Morgan","Lee"]
LAST = ["Kim","Park","Choi","Lee","Han","Jung","Song","Kang","Shin","Yoon"]

PLAYLIST = [
    {"name":"Blinding Lights","artist":"The Weeknd"},
    {"name":"Hype Boy","artist":"NewJeans"},
    {"name":"Shape of You","artist":"Ed Sheeran"},
    {"name":"Seven","artist":"Jung Kook"},
    {"name":"Stay","artist":"Post Malone"},
]


def random_loc():
    # 서울 중심 ± 5km
    base_lat = 37.5665
    base_lng = 126.9780
    return {
        "lat": base_lat + random.uniform(-0.04, 0.04),
        "lng": base_lng + random.uniform(-0.04, 0.04)
    }


def create_user():

    uid = str(uuid.uuid4())[:12]

    gender = random.choice(GENDERS)

    data = {
        "id": uid,
        "firstName": random.choice(FIRST),
        "lastName": random.choice(LAST),
        "age": random.randint(20, 35),
        "gender": gender,
        "location": random_loc(),
        "playlist": random.sample(PLAYLIST, 3),
        "created_at": datetime.utcnow().isoformat(),
        "onboarding_profile": {
            "sexual_orientation": "all types of genders",
            "age_preference": {"min":20,"max":40}
        }
    }

    db_fs.collection("users").document(uid).set(data)

    # ⭐ presence 랜덤
    if rtdb:
        rtdb.child("presence").child(uid).set({
            "online": random.choice([True, False]),
            "updated_at": "seed"
        })

    print("created:", uid)


if __name__ == "__main__":
    for _ in range(10):
        create_user()
