#!/bin/bash

# 스크립트가 있는 디렉토리로 이동하여 올바른 상대 경로를 보장합니다.
cd "$(dirname "$0")"

# 가상 환경 디렉토리 정의
VENV_DIR=".venv"

# 가상 환경이 존재하는지 확인하고, 없으면 생성합니다.
if [ ! -d "$VENV_DIR" ]; then
    echo "가상 환경이 존재하지 않습니다. 새로 생성합니다."
    python3 -m venv "$VENV_DIR"
    if [ $? -ne 0 ]; then
        echo "가상 환경 생성에 실패했습니다. Python3가 설치되어 있는지 확인하세요."
        exit 1
    fi
fi

# 가상 환경을 활성화합니다.
source "$VENV_DIR/bin/activate"

# 의존성 라이브러리를 설치/업데이트합니다.
echo "의존성 라이브러리를 설치/업데이트합니다."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "의존성 설치에 실패했습니다. requirements.txt 파일을 확인하세요."
    exit 1
fi

# Streamlit 애플리케이션을 실행합니다.
echo "Streamlit 애플리케이션을 실행합니다..."
streamlit run app.py