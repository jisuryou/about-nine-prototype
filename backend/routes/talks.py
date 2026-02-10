"""
talks.py - 대화 관련 엔드포인트

- calculate-round: 다음 라운드 계산
- save-talk-history: 대화 저장 (클라이언트에서 호출하지 않음, talk-end.html에서 직접 저장)
- get-talk-history: 대화 기록 조회
"""

from flask import Blueprint, jsonify, session, request
from backend.services.firestore import get_firestore
from backend.utils.request import get_json
import random
import os

talks_bp = Blueprint("talks", __name__, url_prefix="/api/talks")

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
# 이미지 파일 스캔
# =========================
def get_image_files(topic, category):
    """실제 파일 시스템에서 이미지 파일 목록 가져오기"""
    base_path = os.path.join("frontend", "images", topic, category)
    
    if not os.path.exists(base_path):
        print(f"⚠️ Path not found: {base_path}")
        return []
    
    files = [f for f in os.listdir(base_path) 
             if f.endswith(('.png', '.jpg', '.jpeg'))]
    
    return files


# =========================
# 🔥 Calculate Round
# =========================
@talks_bp.route("/calculate-round", methods=["POST"])
def calculate_round():
    """
    두 사용자 간의 다음 대화 라운드 계산
    
    Request:
    {
        "partner_id": "user_xxx"
    }
    
    Response:
    {
        "success": true,
        "round": 1,
        "topic": "food",
        "question": "What are you craving?",
        "options": [...]
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

        # 🔥 talk_history (top-level)에서 완료된 대화 수 계산
        completed_count = count_completed_talks(db, user_id, partner_id)

        # 다음 라운드 (최대 3)
        next_round = min(completed_count + 1, 3)

        # Round별 Topic
        topics = {
            1: "food",
            2: "visual",
            3: "life" 
        }
        
        topic = topics[next_round]

        print(f"📊 Round 계산: {user_id} ↔ {partner_id}")
        print(f"   완료된 대화: {completed_count}개")
        print(f"   다음 Round: {next_round} ({topic})")

        response = {
            "success": True,
            "round": next_round,
            "topic": topic,
            "completed_talks": completed_count
        }

        # food/visual만 질문/옵션 제공
        if topic in ["food", "visual"]:
            # 이미 받은 질문들
            used_questions = get_used_questions(db, user_id, partner_id, topic)
            
            # 새 질문 선택
            question = select_new_question(topic, used_questions)
            
            # 랜덤 옵션 선택
            options = select_random_options(topic)
            
            response["question"] = question
            response["options"] = options
            
            print(f"   질문: {question}")
            print(f"   옵션: {len(options)}개")

        return jsonify(response)

    except Exception as e:
        print(f"❌ calculate-round 실패: {e}")
        import traceback
        traceback.print_exc()
        return jsonify(success=False, message=str(e)), 500


# =========================
# 🔥 Helper Functions
# =========================

def count_completed_talks(db, user_id, partner_id):
    """
    두 사용자 간 완료된 대화 수 계산 (top-level talk_history)
    """
    talks_ref = db.collection("talk_history")
    
    # Case 1: user_a = user_id, user_b = partner_id
    query1 = (
        talks_ref
        .where("participants.user_a", "==", user_id)
        .where("participants.user_b", "==", partner_id)
        .where("completed", "==", True)
        .stream()
    )
    
    # Case 2: user_a = partner_id, user_b = user_id
    query2 = (
        talks_ref
        .where("participants.user_a", "==", partner_id)
        .where("participants.user_b", "==", user_id)
        .where("completed", "==", True)
        .stream()
    )
    
    # 두 쿼리 결과 합치기
    count = len(list(query1)) + len(list(query2))
    
    return count


def get_used_questions(db, user_id, partner_id, topic):
    """
    이 파트너와 이미 받은 질문들 (top-level talk_history)
    """
    talks_ref = db.collection("talk_history")
    
    # Case 1
    query1 = (
        talks_ref
        .where("participants.user_a", "==", user_id)
        .where("participants.user_b", "==", partner_id)
        .where("topic", "==", topic)
        .where("completed", "==", True)
        .stream()
    )
    
    # Case 2
    query2 = (
        talks_ref
        .where("participants.user_a", "==", partner_id)
        .where("participants.user_b", "==", user_id)
        .where("topic", "==", topic)
        .where("completed", "==", True)
        .stream()
    )
    
    questions = set()
    for doc in query1:
        q = doc.to_dict().get("question")
        if q:
            questions.add(q)
    for doc in query2:
        q = doc.to_dict().get("question")
        if q:
            questions.add(q)
    
    return questions


def select_new_question(topic, used_questions):
    """
    새로운 질문 선택 (이미 받은 질문 제외)
    """
    all_questions = QUESTIONS.get(topic, [])
    
    # 사용 안 한 질문
    unused = [q for q in all_questions if q not in used_questions]
    
    if unused:
        return random.choice(unused)
    
    # 다 사용했으면 아무거나
    return random.choice(all_questions)


def select_random_options(topic):
    """
    랜덤 옵션 선택 (실제 파일명 사용)
    """
    categories = IMAGE_CATEGORIES.get(topic)
    if not categories:
        return []
    
    # 3개 카테고리 랜덤 선택
    selected_categories = random.sample(categories, 3)
    
    options = []
    for category in selected_categories:
        # 실제 파일 목록
        files = get_image_files(topic, category)
        
        if not files:
            print(f"⚠️ No files: {topic}/{category}")
            continue
        
        # 랜덤 파일 선택
        random_file = random.choice(files)
        
        options.append({
            "category": category,
            "fileName": random_file
        })
    
    return options


# =========================
# 🔥 Get Talk History
# =========================
@talks_bp.route("/history", methods=["GET"])
def get_talk_history():
    """
    사용자의 대화 기록 조회
    
    Query params:
    - partner_id (optional): 특정 파트너와의 대화만
    - limit (optional): 최대 개수
    """
    user_id = session.get("user_id")
    if not user_id:
        return jsonify(success=False, message="not logged in"), 401

    partner_id = request.args.get("partner_id")
    limit = int(request.args.get("limit", 50))

    try:
        db = get_firestore()
        talks_ref = db.collection("talk_history")
        
        # user_a 또는 user_b인 대화 모두 가져오기
        query1 = talks_ref.where("participants.user_a", "==", user_id).stream()
        query2 = talks_ref.where("participants.user_b", "==", user_id).stream()
        
        talks = []
        for doc in query1:
            talk = doc.to_dict()
            talk["id"] = doc.id
            talks.append(talk)
        for doc in query2:
            talk = doc.to_dict()
            talk["id"] = doc.id
            talks.append(talk)
        
        # partner_id 필터링
        if partner_id:
            talks = [
                t for t in talks
                if t["participants"]["user_a"] == partner_id or t["participants"]["user_b"] == partner_id
            ]
        
        # 시간순 정렬 (최신순)
        talks.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
        
        # 제한
        talks = talks[:limit]
        
        print(f"📜 Talk history: {user_id} → {len(talks)}개")
        
        return jsonify(success=True, talks=talks)

    except Exception as e:
        print(f"❌ get-talk-history 실패: {e}")
        return jsonify(success=False, message=str(e)), 500