#!/bin/bash

echo "🎨 프론트엔드 개발 서버를 시작합니다..."

# 프론트엔드 디렉토리로 이동
cd frontend

# Node.js가 설치되어 있는지 확인
if ! command -v node &> /dev/null; then
    echo "❌ Node.js가 설치되어 있지 않습니다."
    echo "Node.js를 설치해주세요: https://nodejs.org/"
    exit 1
fi

# npm이 설치되어 있는지 확인
if ! command -v npm &> /dev/null; then
    echo "❌ npm이 설치되어 있지 않습니다."
    echo "npm을 설치해주세요."
    exit 1
fi

# node_modules가 없으면 의존성 설치
if [ ! -d "node_modules" ]; then
    echo "📦 의존성을 설치합니다..."
    npm install
fi

# React 개발 서버 시작
echo "🚀 React 개발 서버를 시작합니다..."
echo "프론트엔드 주소: http://localhost:3000"
echo ""
npm start