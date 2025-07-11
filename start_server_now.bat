@echo off
chcp 65001 > nul
echo 🔧 Git Merge Conflict 해결 완료!
echo 🚀 AIRISS 서버 재시작 중...
echo.

cd /d "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

echo 📋 Python 경로 확인:
python --version
echo.

echo 🔥 AIRISS v4.1 서버 시작 (Excel 개선 버전)
python -m uvicorn app.main:app --host 0.0.0.0 --port 8002

pause
