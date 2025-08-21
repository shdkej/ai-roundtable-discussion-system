# 🏢 채팅형 원탁토론 (React + FastAPI)

실시간 채팅으로 AI 전문가들과 토론하는 웹 애플리케이션입니다.

## ✨ 주요 기능

### 🚀 실시간 토론 시스템
- **자동 토론**: 전문가들이 8초마다 자동으로 발언
- **사용자 개입**: 언제든지 토론에 참여 가능
- **실시간 타이핑**: 전문가가 답변 준비 중일 때 타이핑 애니메이션

### 💬 채팅 인터페이스
- **스크롤 가능한 채팅창**: 고정 높이에서 무제한 메시지 표시
- **메시지 타입 구분**: 일반/결론/응답 메시지 시각적 구분
- **실시간 업데이트**: WebSocket으로 즉시 메시지 동기화

### 🎯 전문가 시스템
- **5개 분야 전문가**: 디자인, 영업, 생산, 마케팅, IT
- **개별 질문 기능**: 특정 전문가에게 직접 질문
- **전문 분야별 답변**: 각 전문가의 특화된 관점 제공

### 🎮 토론 제어
- **자동 토론 시작/정지**: 원클릭으로 자동 토론 제어
- **사용자 개입 요청**: 토론 중 언제든 개입 요청 가능
- **결론 생성**: 현재까지의 토론 내용 종합 정리

## 🏗️ 기술 스택

### Frontend
- **React 18**: 현대적인 React 기능 활용
- **Styled Components**: CSS-in-JS로 동적 스타일링
- **Framer Motion**: 부드러운 애니메이션
- **Axios**: HTTP 클라이언트
- **React Hot Toast**: 사용자 알림

### Backend
- **FastAPI**: 고성능 Python 웹 프레임워크
- **WebSocket**: 실시간 양방향 통신
- **CrewAI**: AI 에이전트 오케스트레이션
- **OpenAI GPT-4**: 대화형 AI 모델

## 🚀 설치 및 실행

### 1. 사전 요구사항

```bash
# Python 3.8+ 설치 확인
python3 --version

# Node.js 16+ 설치 확인  
node --version
npm --version
```

### 2. 프로젝트 클론

```bash
git clone <repository-url>
cd roundtable-discussion
```

### 3. 환경 변수 설정

```bash
# backend/.env 파일 생성
echo "OPENAI_API_KEY=your_openai_api_key_here" > backend/.env
```

### 4. 백엔드 서버 실행

```bash
# 터미널 1
./start_backend.sh
```

서버가 실행되면:
- API 서버: http://localhost:8000
- API 문서: http://localhost:8000/docs

### 5. 프론트엔드 개발 서버 실행

```bash
# 터미널 2  
./start_frontend.sh
```

프론트엔드가 실행되면:
- 웹 애플리케이션: http://localhost:3000

## 📱 사용 방법

### 1. 토론 설정
1. **토론 주제 선택**: 미리 정의된 주제 또는 직접 입력
2. **참석자 선택**: 최소 2명 이상의 전문가 선택
3. **회사 정보 입력**: 회사 규모, 사업 분야, 연 매출, 주요 과제

### 2. 토론 진행
1. **🚀 채팅 토론 시작** 버튼 클릭
2. 각 전문가의 초기 의견 확인
3. **▶️ 자동 토론 시작** 으로 자동 진행 시작

### 3. 실시간 참여
- **일반 대화**: 자유로운 의견 개진
- **전문가 질문**: 특정 전문가에게 직접 질문
- **개입 요청**: 자동 토론 중 사용자 발언 기회 요청

### 4. 토론 제어
- **⏸️ 일시정지**: 자동 토론 중단
- **🔄 재개**: 일시정지된 토론 재시작
- **📊 결론**: 현재까지의 토론 내용 종합
- **💾 저장**: 토론 로그 자동 저장

## 🎨 UI/UX 특징

### 💬 채팅 메시지
- **사용자 메시지**: 오른쪽 정렬, 그라디언트 배경
- **전문가 메시지**: 왼쪽 정렬, 발언자별 색상 구분
- **시스템 메시지**: 중앙 정렬, 파란색 강조
- **결론/응답**: 특별한 배경색으로 중요 메시지 구분

### 🔄 실시간 효과
- **타이핑 애니메이션**: 점 3개가 튀는 효과
- **메시지 등장**: 부드러운 fade-in 애니메이션
- **자동 스크롤**: 새 메시지에 자동 포커스

### 📊 사이드바
- **토론 제어판**: 모든 기능을 한 곳에서 제어
- **실시간 상태**: 현재 토론 상태 실시간 표시
- **통계 정보**: 메시지 수, 라운드, 진행 시간

## 🛠️ 개발 정보

### 프로젝트 구조
```
roundtable-discussion/
├── backend/                 # FastAPI 백엔드
│   ├── main.py             # 메인 서버 파일
│   ├── chat_roundtable.py  # AI 토론 시스템
│   └── requirements.txt    # Python 의존성
├── frontend/               # React 프론트엔드
│   ├── src/
│   │   ├── components/     # React 컴포넌트
│   │   ├── hooks/          # 커스텀 훅
│   │   └── App.js          # 메인 App 컴포넌트
│   └── package.json        # Node.js 의존성
└── start_*.sh              # 실행 스크립트
```

### API 엔드포인트
- `POST /api/start_discussion`: 토론 시작
- `POST /api/start_auto_discussion`: 자동 토론 시작
- `POST /api/pause_auto_discussion`: 자동 토론 일시정지
- `POST /api/send_message`: 메시지 전송
- `POST /api/ask_expert`: 전문가 질문
- `GET /api/status`: 토론 상태 조회
- `WebSocket /ws`: 실시간 통신

## 🔧 문제 해결

### 백엔드 실행 오류
```bash
# 의존성 재설치
cd backend
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 프론트엔드 실행 오류
```bash
# 의존성 재설치
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### WebSocket 연결 오류
- 백엔드 서버가 실행 중인지 확인
- 포트 8000번이 사용 가능한지 확인
- 방화벽 설정 확인

## 📝 라이선스

이 프로젝트는 개발 및 학습 목적으로 제작되었습니다.

## 🙋‍♂️ 지원

문제가 발생하면 다음을 확인해주세요:
1. Python 3.8+ 및 Node.js 16+ 설치 여부
2. OpenAI API 키 설정 여부
3. 필요한 포트(3000, 8000)의 사용 가능 여부
4. 인터넷 연결 상태