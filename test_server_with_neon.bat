@echo off
chcp 65001 > nul
echo.
echo 🚀 AIRISS 서버 + 네온 DB 연동 테스트
echo ===============================================
echo.

echo 📦 필수 패키지 설치 확인...
pip install sqlalchemy>=2.0.23 psycopg2-binary python-dotenv fastapi uvicorn

echo.
echo 🔧 네온 DB 연결 테스트 재확인...
python simple_neon_test.py

echo.
echo 🌐 AIRISS 서버 시작 중...
echo 브라우저에서 http://localhost:8002/health 확인하세요
echo Ctrl+C로 서버 중지 가능
echo.

python app/main.py