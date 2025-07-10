@echo off
chcp 65001 > nul
echo.
echo 🚀 AIRISS 네온 DB 연결 테스트 시작
echo ================================================
echo.

REM 가상환경 활성화 (있는 경우)
if exist "venv\Scripts\activate.bat" (
    echo 🔧 가상환경 활성화 중...
    call venv\Scripts\activate.bat
) else (
    echo ⚠️ 가상환경이 없습니다. 전역 Python 사용
)

echo.
echo 📦 필요한 패키지 설치 중...
pip install psycopg2-binary python-dotenv sqlalchemy

echo.
echo 🧪 네온 DB 연결 테스트 실행...
python test_neon_db_connection.py

echo.
echo 🏁 테스트 완료
pause