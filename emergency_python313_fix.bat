@echo off
chcp 65001 > nul
echo.
echo 🔧 AIRISS Python 3.13 호환성 긴급 수정
echo =============================================
echo.

echo 📋 현재 database.py 백업 중...
copy app\db\database.py app\db\database_backup_%date:~0,4%%date:~5,2%%date:~8,2%.py

echo.
echo 🔄 Python 3.13 호환 database.py로 교체 중...
echo 만약 SQLAlchemy 오류가 발생하면 이 스크립트를 실행하세요.

echo.
echo 📦 최신 호환 패키지 설치...
pip install --upgrade sqlalchemy>=2.0.25
pip install --upgrade psycopg2-binary>=2.9.9

echo.
echo 🧪 연결 테스트...
python simple_neon_test.py

echo.
echo 🚀 서버 시작...
python app/main.py

pause