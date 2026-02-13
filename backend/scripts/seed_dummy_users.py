import random
import uuid
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import firestore, db, credentials

from backend.services.firestore import get_firestore
from backend.services.rtdb import get_rtdb


db_fs = get_firestore()
rtdb = get_rtdb()

GENDERS = ["man", "woman", "non-binary"]

# Gender detail 매핑
GENDER_DETAILS = {
    "woman": ["cis woman", "trans woman", "intersex woman", "transfeminine", "woman and non-binary"],
    "man": ["cis man", "trans man", "intersex man", "transmasculine", "man and non-binary"],
    "non-binary": ["Agender", "Bigender", "Genderfluid", "Genderqueer", "Gender nonconforming"]
}

# Sexual orientation 옵션들
ORIENTATIONS = [
    "men",
    "women",
    "men and women",
    "men and non-binary people",
    "women and non-binary people",
    "all types of genders"
]

# 취향 옵션들
DRINK_OPTIONS = ["yes", "no"]
SMOKE_OPTIONS = ["yes", "no"]
MARIJUANA_OPTIONS = ["yes", "no"]

FIRST = ["Alex", "Sam", "Chris", "Jamie", "Taylor", "Jordan", "Casey", "Riley", "Morgan", "Lee"]
LAST = ["Kim", "Park", "Choi", "Lee", "Han", "Jung", "Song", "Kang", "Shin", "Yoon"]

PLAYLIST = [
    {"id": "1", "name": "Blinding Lights", "artist": "The Weeknd", "image": "https://i.ytimg.com/vi/4NRXx6U8ABQ/hqdefault.jpg", "preview": "https://www.youtube.com/watch?v=4NRXx6U8ABQ"},
    {"id": "2", "name": "Hype Boy", "artist": "NewJeans", "image": "https://i.ytimg.com/vi/11cta61wi0g/hqdefault.jpg", "preview": "https://www.youtube.com/watch?v=11cta61wi0g"},
    {"id": "3", "name": "Shape of You", "artist": "Ed Sheeran", "image": "https://i.ytimg.com/vi/JGwWNGJdvx8/hqdefault.jpg", "preview": "https://www.youtube.com/watch?v=JGwWNGJdvx8"},
    {"id": "4", "name": "Seven", "artist": "Jung Kook", "image": "https://i.ytimg.com/vi/QU9c0053UAU/hqdefault.jpg", "preview": "https://www.youtube.com/watch?v=QU9c0053UAU"},
    {"id": "5", "name": "Stay", "artist": "Post Malone", "image": "https://i.ytimg.com/vi/kTJczUoc26U/hqdefault.jpg", "preview": "https://www.youtube.com/watch?v=kTJczUoc26U"},
    {"id": "6", "name": "Anti-Hero", "artist": "Taylor Swift", "image": "https://i.ytimg.com/vi/b1kbLwvqugk/hqdefault.jpg", "preview": "https://www.youtube.com/watch?v=b1kbLwvqugk"},
    {"id": "7", "name": "As It Was", "artist": "Harry Styles", "image": "https://i.ytimg.com/vi/H5v3kku4y6Q/hqdefault.jpg", "preview": "https://www.youtube.com/watch?v=H5v3kku4y6Q"},
]

EMBEDDING_DIM = 128


def random_loc():
    """서울 중심 ± 5km"""
    base_lat = 37.5665
    base_lng = 126.9780
    return {
        "lat": base_lat + random.uniform(-0.04, 0.04),
        "lng": base_lng + random.uniform(-0.04, 0.04)
    }


def random_birthdate(age):
    """나이로부터 생년월일 생성"""
    year = datetime.now().year - age
    month = random.randint(1, 12)
    day = random.randint(1, 28)  # 안전하게 28일까지만
    return f"{year}-{str(month).zfill(2)}-{str(day).zfill(2)}"


def random_phone():
    """랜덤 한국 전화번호"""
    return f"+8210{random.randint(10000000, 99999999)}"

def random_embedding(dim: int = EMBEDDING_DIM):
    values = [random.gauss(0, 1) for _ in range(dim)]
    norm = sum(v * v for v in values) ** 0.5
    if norm == 0:
        return values
    return [v / norm for v in values]


def create_user():
    uid = str(uuid.uuid4())[:12]
    
    # 기본 정보
    first_name = random.choice(FIRST)
    last_name = random.choice(LAST)
    age = random.randint(20, 35)
    gender = random.choice(GENDERS)
    gender_detail = random.choice(GENDER_DETAILS[gender])
    
    # 성적 지향 및 나이 선호도
    sexual_orientation = random.choice(ORIENTATIONS)
    age_min = random.randint(20, 30)
    age_max = random.randint(age_min + 5, 60)
    
    # 온보딩 프로필
    onboarding_profile = {
        "gender": gender,
        "gender_detail": gender_detail,
        "drink": random.choice(DRINK_OPTIONS),
        "smoke": random.choice(SMOKE_OPTIONS),
        "marijuana": random.choice(MARIJUANA_OPTIONS),
        "sexual_orientation": sexual_orientation,
        "age_preference": {"min": age_min, "max": age_max}
    }
    
    # ✅ 새로운 데이터 구조
    data = {
        "id": uid,
        "firebase_uid": f"dummy_{uid}",
        "created_at": datetime.utcnow().isoformat(),
        
        # 개인 정보
        "first_name": first_name,
        "last_name": last_name,
        "phone": random_phone(),
        "age": age,
        "birthdate": random_birthdate(age),
        
        # 필터링용 필드 (루트 레벨)
        "gender": gender,
        "gender_detail": gender_detail,
        "sexual_orientation": sexual_orientation,
        "age_preference": {"min": age_min, "max": age_max},
        
        # 위치
        "location": random_loc(),
        
        # 플레이리스트 (3-5곡 랜덤)
        "playlist": random.sample(PLAYLIST, random.randint(3, 5)),
        "playlist_updated_at": datetime.utcnow().isoformat(),
        
        # 온보딩 정보
        "onboarding_profile": onboarding_profile,
        "onboarding_completed": True,
        "onboarding_updated_at": datetime.utcnow().isoformat(),

        # 추천용 임베딩
        "embedding": {
            "vector": random_embedding(),
            "dim": EMBEDDING_DIM,
            "updated_at": int(datetime.utcnow().timestamp() * 1000),
        },

        # 간단 통계
        "stats": {
            "talk_count": 0,
            "go_rate": 0.0,
        },
    }

    db_fs.collection("users").document(uid).set(data)

    # ⭐ presence 랜덤
    if rtdb:
        rtdb.child("presence").child(uid).set({
            "online": random.choice([True, False]),
            "updated_at": datetime.utcnow().isoformat()
        })

    print(f"✅ Created: {uid} | {first_name} {last_name} | {gender} ({gender_detail}) | age {age} | prefers: {sexual_orientation}")


if __name__ == "__main__":
    print("🌱 Seeding dummy users...\n")
    
    num_users = 10
    for i in range(num_users):
        create_user()
    
    print(f"\n✨ Done! Created {num_users} dummy users.")
