@echo off
chcp 65001 > nul
echo.
echo 🔧 AIRISS 패키지 재설치 (Python 3.13 호환)
echo ================================================
echo.

echo 📦 기존 SQLAlchemy 제거...
pip uninstall sqlalchemy -y

echo.
echo 📦 Python 3.13 호환 패키지 설치...
pip install sqlalchemy>=2.0.23
pip install psycopg2-binary>=2.9.9
pip install python-dotenv

echo.
echo 🧪 네온 DB 연결 테스트 실행...
python simple_neon_test.py

echo.
echo 🏁 재설치 및 테스트 완료
pause