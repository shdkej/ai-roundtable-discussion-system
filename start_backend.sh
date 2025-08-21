#!/bin/bash

echo "🚀 백엔드 서버를 시작합니다..."

# 백엔드 디렉토리로 이동
cd backend

# Python 버전 확인
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "🐍 Python 버전: $PYTHON_VERSION"

# Python 버전별 호환성 체크
if [[ "$PYTHON_VERSION" == "3.13" ]]; then
    echo "⚠️  경고: Python 3.13이 감지되었습니다."
    echo "   CrewAI는 Python 3.9-3.12를 지원합니다."
    echo "   pyenv 등으로 Python 3.11 또는 3.12 사용을 권장합니다."
    echo ""
elif [[ "$PYTHON_VERSION" == "3.9" ]]; then
    echo "ℹ️  Python 3.9 감지 - CrewAI 0.28.8 버전을 사용합니다."
    echo ""
fi

# 가상환경이 없으면 생성
if [ ! -d "venv" ]; then
    echo "📦 가상환경을 생성합니다..."
    python3 -m venv .venv
fi

# 가상환경 활성화
echo "🔧 가상환경을 활성화합니다..."
source .venv/bin/activate

# 의존성 설치
echo "📋 의존성을 설치합니다..."
pip3 install --upgrade pip
pip3 install -r requirements.txt

# .env 파일 확인
if [ ! -f ".env" ]; then
    echo "⚠️  .env 파일이 없습니다. OPENAI_API_KEY를 설정해주세요."
    echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
    echo "📝 .env 파일을 생성했습니다. OPENAI_API_KEY를 설정하고 다시 실행해주세요."
    exit 1
fi

# 서버 시작
echo "🎯 FastAPI 서버를 시작합니다..."
echo "서버 주소: http://localhost:8101"
echo "API 문서: http://localhost:8101/docs"
echo ""
python3 -muvicorn main:app --host 0.0.0.0 --port 8101 --reload