import base64
import os
import random
import time
import uuid
from datetime import datetime, timedelta

import requests
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

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_MARKET = os.getenv("SPOTIFY_MARKET", "US")

SPOTIFY_SEED_QUERIES = [
    {"name": "Blinding Lights", "artist": "The Weeknd", "query": "Blinding Lights The Weeknd"},
    {"name": "Hype Boy", "artist": "NewJeans", "query": "Hype Boy NewJeans"},
    {"name": "Shape of You", "artist": "Ed Sheeran", "query": "Shape of You Ed Sheeran"},
    {"name": "Seven", "artist": "Jung Kook", "query": "Seven Jung Kook"},
    {"name": "Stay", "artist": "Post Malone", "query": "Stay Post Malone"},
    {"name": "Anti-Hero", "artist": "Taylor Swift", "query": "Anti-Hero Taylor Swift"},
    {"name": "As It Was", "artist": "Harry Styles", "query": "As It Was Harry Styles"},
]

_spotify_token = None
_spotify_token_expires_at = 0


def get_spotify_token():
    global _spotify_token, _spotify_token_expires_at

    if _spotify_token and time.time() < _spotify_token_expires_at - 30:
        return _spotify_token

    if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
        return None

    auth = f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}"
    encoded = base64.b64encode(auth.encode("utf-8")).decode("utf-8")

    try:
        r = requests.post(
            "https://accounts.spotify.com/api/token",
            data={"grant_type": "client_credentials"},
            headers={"Authorization": f"Basic {encoded}"},
            timeout=5,
        )
        r.raise_for_status()
        data = r.json()
        _spotify_token = data.get("access_token")
        expires_in = data.get("expires_in", 3600)
        _spotify_token_expires_at = time.time() + int(expires_in)
        return _spotify_token
    except Exception as e:
        print("🔥 Spotify token error:", e)
        return None


def fetch_spotify_track(query):
    token = get_spotify_token()
    if not token:
        return None

    try:
        r = requests.get(
            "https://api.spotify.com/v1/search",
            params={
                "q": query,
                "type": "track",
                "limit": 5,
                "market": SPOTIFY_MARKET,
            },
            headers={"Authorization": f"Bearer {token}"},
            timeout=5,
        )
        r.raise_for_status()
        items = r.json().get("tracks", {}).get("items", [])
    except Exception as e:
        print("🔥 Spotify search error:", e)
        return None

    for it in items:
        preview_url = it.get("preview_url")
        if not preview_url:
            continue

        album_images = it.get("album", {}).get("images", [])
        image_url = album_images[0]["url"] if album_images else ""
        artists = ", ".join([a.get("name", "") for a in it.get("artists", [])])

        return {
            "id": it.get("id"),
            "uri": it.get("uri"),
            "name": it.get("name"),
            "artist": artists,
            "image": image_url,
            "preview_url": preview_url,
        }

    return None


def build_seed_playlist():
    tracks = []
    for seed in SPOTIFY_SEED_QUERIES:
        track = fetch_spotify_track(seed["query"])
        if track:
            tracks.append(track)

    if tracks:
        return tracks

    print("⚠️ Spotify preview unavailable; seeding without previews.")
    return [
        {
            "id": str(i + 1),
            "uri": "",
            "name": seed["name"],
            "artist": seed["artist"],
            "image": "",
            "preview_url": "",
        }
        for i, seed in enumerate(SPOTIFY_SEED_QUERIES)
    ]


PLAYLIST = build_seed_playlist()

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
