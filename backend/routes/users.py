from datetime import datetime
from flask import Blueprint, jsonify, session, request
from backend.services.firestore import get_firestore
from backend.utils.request import get_json
import math
import random
import os

users_bp = Blueprint("users", __name__, url_prefix="/api/users")

# =========================
# 이미지 파일 스캔
# =========================
def get_image_files(topic, category):
    """
    실제 파일 시스템에서 이미지 파일 목록 가져오기
    """
    # 프로젝트 루트 기준 경로
    base_path = os.path.join("frontend", "images", topic, category)
    
    if not os.path.exists(base_path):
        print(f"⚠️ Path not found: {base_path}")
        return []
    
    # .png, .jpg 파일만 필터링
    files = [f for f in os.listdir(base_path) 
             if f.endswith(('.png', '.jpg', '.jpeg'))]
    
    return files

# =========================
# 질문 풀
# =========================
QUESTIONS = {
    "food": [
        "What are you craving right now?",
        "What do you want to eat when you're stressed?",
        "If you could only eat one food for three years, what would it be?",
        "What's your soul food?",
        "What do you want to eat when you need comfort?",
        "Which food best represents your taste?",
        "What did you have for dinner most recently?",
        "What would you want to cook for your partner?",
        "What tastes even better when you're in a good mood?",
        "What would you eat to cure a hangover?",
        "What would you want as your last meal?",
        "What would you want to eat on a first date?",
        "What tastes better when you eat alone?",
        "Which one appeals to you the least?",
        "What do you want for lunch tomorrow?",
        "What would you eat right after ending a diet?",
        "What would you want to cook together?",
        "What would you serve at a housewarming party?",
        "Which one would you miss most if it disappeared?",
        "Which one suits a special occasion?",
        "Which one would make you like someone more if they chose it?",
        "Which one do you think we'd both choose?"
    ],
    "visual": [
        "Which painting resonates with you the most?",
        "Which painting would you choose as a gift for someone you care about?",
        "If you were opening a café, which painting would you hang?",
        "Which painting would you want to see on your daily commute?",
        "Which one caught your eye within 3 seconds?",
        "Which painting would suit a hotel lobby?",
        "Which painting would you hang in your bedroom?",
        "Which painting would you look at when you need energy?",
        "Which painting would you want to see when you're feeling down?",
        "Which painting would you want to show someone on a first date?",
        "Which painting do you think your parents would like?",
        "Which painting best represents who you are?",
        "Which choice would surprise your friends?",
        "Which painting would make you more attracted to someone if they chose it?",
        "Which painting would worry you a little if someone chose it?",
        "Which painting would you want to see right after a breakup?",
        "Which painting would you look at before a new beginning?",
        "Which painting feels most valuable to you?"
    ]
}

# =========================
# 이미지 카테고리
# =========================
IMAGE_CATEGORIES = {
    "food": ["italian", "pizza", "others", "dessert", "bread"],
    "visual": ["abstract", "landscape", "portrait"]
}

# =========================
# Playlist
# =========================
@users_bp.route("/playlist", methods=["POST"])
def save_playlist():

    user_id = session.get("user_id")
    if not user_id:
        return jsonify(success=False, message="not logged in"), 401

    data, err, code = get_json()
    if err:
        return err, code

    tracks = data.get("tracks", [])

    db = get_firestore()

    db.collection("users").document(user_id).set({
        "playlist": tracks,
        "playlist_updated_at": datetime.utcnow().isoformat()
    }, merge=True)

    return jsonify(success=True)


# =========================
# Location
# =========================
@users_bp.route("/update-location", methods=["POST"])
def update_location():

    user_id = session.get("user_id")
    if not user_id:
        return jsonify(success=False, message="not logged in"), 401

    data, err, code = get_json()
    if err:
        return err, code

    db = get_firestore()

    db.collection("users").document(user_id).set({
        "location": {
            "lat": data.get("lat"),
            "lng": data.get("lng")
        }
    }, merge=True)

    return jsonify(success=True)


# =========================
# 거리 계산
# =========================
def distance_km(lat1, lng1, lat2, lng2):
    R = 6371
    d_lat = math.radians(lat2 - lat1)
    d_lng = math.radians(lng2 - lng1)

    a = (
        math.sin(d_lat/2)**2 +
        math.cos(math.radians(lat1)) *
        math.cos(math.radians(lat2)) *
        math.sin(d_lng/2)**2
    )

    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))


# =========================
# Nearby list
# =========================
@users_bp.route("/list")
def list_users():
    uid = session.get("user_id")
    if not uid:
        return jsonify(success=False), 401

    db = get_firestore()
    me = db.collection("users").document(uid).get().to_dict()

    print(f"\n=== USER LIST DEBUG ===")
    print(f"My ID: {uid}")
    print(f"My profile: {me}")

    my_loc = me.get("location")
    my_gender = me.get("gender")
    my_age = me.get("age")
    my_sexual_orientation = me.get("sexual_orientation")
    my_age_pref = me.get("age_preference", {})

    print(f"My location: {my_loc}")
    print(f"My gender: {my_gender}, age: {my_age}")
    print(f"My preferences: orientation={my_sexual_orientation}, age_range={my_age_pref}")

    users = []
    total_count = 0
    filtered_stats = {
        "same_user": 0,
        "no_onboarding": 0,
        "no_location": 0,
        "too_far": 0,
        "orientation_mismatch": 0,
        "age_mismatch": 0,
        "reverse_orientation": 0,
        "reverse_age": 0,
        "passed": 0
    }

    for doc in db.collection("users").stream():
        u = doc.to_dict()
        total_count += 1

        if u["id"] == uid:
            filtered_stats["same_user"] += 1
            continue

        if not u.get("onboarding_completed"):
            filtered_stats["no_onboarding"] += 1
            continue

        loc = u.get("location")
        if not loc or not my_loc:
            filtered_stats["no_location"] += 1
            continue

        # 거리 체크
        d = distance_km(
            my_loc["lat"], my_loc["lng"],
            loc["lat"], loc["lng"]
        )
        if d > 10:
            filtered_stats["too_far"] += 1
            continue

        other_gender = u.get("gender")
        other_age = u.get("age")
        other_sexual_orientation = u.get("sexual_orientation")
        other_age_pref = u.get("age_preference", {})

        if not other_gender or not other_age:
            filtered_stats["no_location"] += 1
            continue

        # 내가 상대를 선호하는지
        if not matches_orientation(my_sexual_orientation, other_gender):
            filtered_stats["orientation_mismatch"] += 1
            continue

        if my_age_pref:
            if not (my_age_pref.get("min", 0) <= other_age <= my_age_pref.get("max", 100)):
                filtered_stats["age_mismatch"] += 1
                continue

        # 상대가 나를 선호하는지
        if not matches_orientation(other_sexual_orientation, my_gender):
            filtered_stats["reverse_orientation"] += 1
            continue

        if other_age_pref:
            if not (other_age_pref.get("min", 0) <= my_age <= other_age_pref.get("max", 100)):
                filtered_stats["reverse_age"] += 1
                continue

        filtered_stats["passed"] += 1
        users.append(u)

    print(f"\nTotal users in DB: {total_count}")
    print(f"Filter results:")
    for key, value in filtered_stats.items():
        print(f"  {key}: {value}")
    print(f"Final result: {len(users)} users")
    print("======================\n")

    return jsonify(success=True, users=users)


# =========================
# 성적 지향 매칭 헬퍼
# =========================
def matches_orientation(orientation, target_gender):
    """
    orientation: 내 성적 지향 (예: "men", "women", "all types of genders")
    target_gender: 상대방의 성별 (예: "man", "woman", "non-binary")
    """
    if not orientation:
        return True  # 기본값: 모두 허용
    
    orientation = orientation.lower()
    target_gender = target_gender.lower()
    
    # "all types of genders" → 모두 허용
    if "all types" in orientation:
        return True
    
    # "men" → man만
    if orientation == "men":
        return target_gender == "man"
    
    # "women" → woman만
    if orientation == "women":
        return target_gender == "woman"
    
    # "men and women" → man 또는 woman
    if orientation == "men and women":
        return target_gender in ["man", "woman"]
    
    # "men and non-binary people"
    if "men and non-binary" in orientation:
        return target_gender in ["man", "non-binary"]
    
    # "women and non-binary people"
    if "women and non-binary" in orientation:
        return target_gender in ["woman", "non-binary"]
    
    return False

# =========================
# Get Profile
# =========================
@users_bp.route("/profile", methods=["GET"])
def get_profile():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify(success=False, message="not logged in"), 401

    db = get_firestore()
    user = db.collection("users").document(user_id).get().to_dict()
    
    if not user:
        return jsonify(success=False, message="user not found"), 404
    
    return jsonify(success=True, user=user)


# =========================
# Update Profile
# =========================
@users_bp.route("/profile", methods=["POST"])
def update_profile():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify(success=False, message="not logged in"), 401

    data, err, code = get_json()
    if err:
        return err, code

    db = get_firestore()
    
    # 업데이트할 필드만 전송
    update_data = {}
    
    if "onboarding_profile" in data:
        update_data["onboarding_profile"] = data["onboarding_profile"]
    
    if "bio" in data:
        update_data["bio"] = data["bio"]
    
    if "sexual_orientation" in data:
        update_data["sexual_orientation"] = data["sexual_orientation"]
    
    if "age_preference" in data:
        update_data["age_preference"] = data["age_preference"]
    
    db.collection("users").document(user_id).set(update_data, merge=True)
    
    return jsonify(success=True)

# =========================
# 🔥 Calculate Round + Select Question/Options
# =========================
@users_bp.route("/calculate-round", methods=["POST"])
def calculate_round():
    """
    두 사용자 간의 다음 대화 라운드 계산 + 질문/옵션 선택
    
    Response:
    {
        "success": true,
        "round": 1,
        "topic": "food",
        "question": "What are you craving right now?",
        "options": [
            {"category": "italian", "imageNum": 3},
            {"category": "dessert", "imageNum": 7},
            {"category": "bread", "imageNum": 2}
        ]
    }
    """
    user_id = session.get("user_id")
    if not user_id:
        return jsonify(success=False, message="not logged in"), 401

    data, err, code = get_json()
    if err:
        return err, code
    
    partner_id = data.get("partner_id")
    if not partner_id:
        return jsonify(success=False, message="partner_id required"), 400

    try:
        db = get_firestore()

        # 1️⃣ 양쪽 talk_history 확인
        user_talks = get_completed_talks(db, user_id, partner_id)
        partner_talks = get_completed_talks(db, partner_id, user_id)

        if len(user_talks) != len(partner_talks):
            print(f"⚠️ Talk history mismatch: {user_id}={len(user_talks)}, {partner_id}={len(partner_talks)}")
        
        completed_count = min(len(user_talks), len(partner_talks))

        # 다음 라운드 (최대 3)
        next_round = min(completed_count + 1, 3)

        topics = {
            1: "food",
            2: "visual",
            3: "life"
        }
        
        topic = topics[next_round]

        # 2️⃣ 질문/옵션 선택 (food/visual만)
        if topic in ["food", "visual"]:
            # 이전에 받은 질문들 확인
            user_questions = get_used_questions(db, user_id, topic)
            partner_questions = get_used_questions(db, partner_id, topic)

            # 새로운 질문 선택
            question = select_new_question(topic, user_questions, partner_questions)

            # 랜덤 옵션 선택
            options = select_random_options(topic)
        else:
            # life는 질문/옵션 없음
            question = None
            options = None

        print(f"📊 Round: {user_id} ↔ {partner_id} = {next_round} ({topic})")
        if question:
            print(f"   Question: {question}")
            print(f"   Options: {options}")

        response = {
            "success": True,
            "round": next_round,
            "topic": topic,
            "completed_talks": completed_count
        }

        if question:
            response["question"] = question
        if options:
            response["options"] = options

        return jsonify(response)

    except Exception as e:
        print(f"❌ Error calculating round: {e}")
        return jsonify(success=False, message=str(e)), 500


def get_completed_talks(db, user_id, partner_id):
    """특정 파트너와의 완료된 대화 목록"""
    talks_ref = (
        db.collection("users")
        .document(user_id)
        .collection("talk_history")
    )
    
    query = talks_ref.where("partner_id", "==", partner_id).where("completed", "==", True).stream()
    
    talks = []
    for doc in query:
        talk_data = doc.to_dict()
        talk_data["id"] = doc.id
        talks.append(talk_data)
    
    return talks


def get_used_questions(db, user_id, topic):
    """사용자가 이미 받은 질문들 (모든 파트너 포함)"""
    talks_ref = (
        db.collection("users")
        .document(user_id)
        .collection("talk_history")
    )
    
    query = talks_ref.where("topic", "==", topic).where("completed", "==", True).stream()
    
    questions = set()
    for doc in query:
        talk_data = doc.to_dict()
        q = talk_data.get("question")
        if q:
            questions.add(q)
    
    return questions


def select_new_question(topic, user_questions, partner_questions):
    """
    새로운 질문 선택 (우선순위: 둘 다 안 받음 > 한 명만 받음 > 아무거나)
    """
    all_questions = QUESTIONS.get(topic, [])
    
    # 둘 다 안 받은 질문
    unused_by_both = [q for q in all_questions if q not in user_questions and q not in partner_questions]
    if unused_by_both:
        return random.choice(unused_by_both)
    
    # 한 명만 받은 질문
    unused_by_one = [q for q in all_questions if q not in user_questions or q not in partner_questions]
    if unused_by_one:
        return random.choice(unused_by_one)
    
    # 다 받았으면 아무거나
    return random.choice(all_questions)


def select_random_options(topic):
    """
    랜덤 옵션 선택 (실제 파일명 사용)
    """
    categories = IMAGE_CATEGORIES.get(topic)
    if not categories:
        return None
    
    selected_categories = random.sample(categories, 3)
    
    options = []
    for category in selected_categories:
        # 🔥 실제 파일 목록 가져오기
        files = get_image_files(topic, category)
        
        if not files:
            print(f"⚠️ No files found for {topic}/{category}")
            continue
        
        # 🔥 랜덤 파일 선택
        random_file = random.choice(files)
        
        options.append({
            "category": category,
            "fileName": random_file  # 🔥 실제 파일명
        })
    
    return options


# =========================
# 🔥 Save My Talk (각자 저장)
# =========================
@users_bp.route("/save-my-talk", methods=["POST"])
def save_my_talk():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify(success=False, message="not logged in"), 401

    data, err, code = get_json()
    if err:
        return err, code

    partner_id = data.get("partner_id")
    round_num = data.get("round")
    topic = data.get("topic")
    question = data.get("question")  # 🔥 질문 저장

    if not all([partner_id, round_num, topic]):
        return jsonify(success=False, message="missing required fields"), 400

    try:
        db = get_firestore()
        from google.cloud.firestore import SERVER_TIMESTAMP

        # 자신의 talk_history에만 저장
        my_talk_ref = (
            db.collection("users")
            .document(user_id)
            .collection("talk_history")
            .document()
        )
        
        talk_data = {
            "partner_id": partner_id,
            "round": round_num,
            "topic": topic,
            "completed": True,
            "timestamp": SERVER_TIMESTAMP,
            "result": {
                "compatibility_score": data.get("compatibility_score", 0),
                "my_selections": data.get("my_selections", []),
                "partner_selections": data.get("partner_selections", [])
            }
        }
        
        # 🔥 질문 저장 (food/visual만)
        if question:
            talk_data["question"] = question
        
        my_talk_ref.set(talk_data)

        print(f"✅ Talk saved: {user_id} with {partner_id}, Round {round_num}")

        return jsonify(success=True, message="talk history saved")

    except Exception as e:
        print(f"❌ Error saving talk: {e}")
        return jsonify(success=False, message=str(e)), 500


# =========================
# 🔥 Talk History
# =========================
@users_bp.route("/talk-history", methods=["GET"])
def get_talk_history():
    """
    특정 파트너와의 대화 기록 조회
    """
    user_id = session.get("user_id")
    if not user_id:
        return jsonify(success=False, message="not logged in"), 401

    partner_id = request.args.get("partner_id")
    
    if not partner_id:
        return jsonify(success=False, message="partner_id required"), 400

    try:
        db = get_firestore()
        talks = get_completed_talks(db, user_id, partner_id)

        # 시간순 정렬
        talks.sort(key=lambda x: x.get("timestamp", 0) if x.get("timestamp") else 0)

        return jsonify(success=True, talks=talks)

    except Exception as e:
        print(f"❌ Error fetching talk history: {e}")
        return jsonify(success=False, message=str(e)), 500