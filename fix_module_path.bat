@echo off
chcp 65001 > nul
echo 🔧 AIRISS v4.1 모듈 경로 문제 해결
echo ==========================================

cd /d "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

echo 📍 현재 디렉토리: %CD%
echo 🐍 Python 경로 설정 중...

REM Python 경로를 현재 디렉토리로 설정
set PYTHONPATH=%CD%

echo ✅ PYTHONPATH 설정: %PYTHONPATH%
echo.
echo 🚀 AIRISS 서버 시작...
echo 브라우저에서 http://localhost:8002 접속하세요
echo.

python app\main.py

pause
