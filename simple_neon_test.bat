@echo off
chcp 65001 > nul
echo.
echo 🚀 AIRISS 네온 DB 간단 테스트 (Python 3.13 호환)
echo ================================================
echo.

echo 📦 psycopg2 패키지 설치 중...
pip install psycopg2-binary

echo.
echo 🧪 네온 DB 연결 테스트 실행...
python simple_neon_test.py

echo.
echo 🏁 테스트 완료