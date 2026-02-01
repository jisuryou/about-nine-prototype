# ABOUT NINE App (Prototype)

음성 대화 기반 소셜 매칭 웹 애플리케이션

## 기술 스택
- Backend: Flask (Python)
- Frontend: HTML, CSS, JavaScript
- Database: Firebase Firestore
- Real-time: Firebase Realtime Database
- Voice: Agora RTC

## 설치 방법

### 1. 가상환경 생성
\`\`\`bash
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
\`\`\`

### 2. 패키지 설치
\`\`\`bash
pip install -r backend/requirements.txt
\`\`\`

### 3. 환경 변수 설정
`.env` 파일을 생성하고 필요한 API 키 입력

### 4. 실행
\`\`\`bash
python backend/app.py
\`\`\`

## 페이지 구성
- 초대 코드 입력
- 전화번호 인증
- 생년월일/이름 입력
- 온보딩 (챗봇)
- 음악 선택 (Spotify)
- 라운지 & AI 매칭
- 음성 대화
- 프로필

## 개발자
[Jisu Ryou]
```

### `backend/requirements.txt`
```
Flask==3.0.0
Flask-CORS==4.0.0
firebase-admin==6.3.0
python-dotenv==1.0.0
requests==2.31.0
```

### `.env` (템플릿 - 실제 값은 나중에 입력)
```
SECRET_KEY=yTMkGMgKr1IXi03aJ4ZX3m92BYvszaAK1RHOSKXB0pVk
FIREBASE_DB_URL=https://about-nine-prototype-46a2c-default-rtdb.asia-southeast1.firebasedatabase.app/
<!-- SPOTIFY_CLIENT_ID=your-spotify-client-id
SPOTIFY_CLIENT_SECRET=your-spotify-client-secret -->
AGORA_APP_ID=ebc1a1bf4b4347cd896087d76d9e32db