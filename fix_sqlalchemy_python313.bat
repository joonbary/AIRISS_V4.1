@echo off
chcp 65001 > nul
echo ========================================
echo   AIRISS SQLAlchemy Python 3.13 Fix
echo ========================================
echo.
echo [목표] SQLAlchemy 호환성 문제 해결하여 Neon DB 영구 저장 활성화
echo.

cd /d "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

echo [1단계] 현재 SQLAlchemy 버전 확인...
python -c "import sqlalchemy; print(f'현재 SQLAlchemy: {sqlalchemy.__version__}')" 2>nul
if %errorlevel% neq 0 (
    echo ❌ SQLAlchemy 로드 실패
) else (
    echo ✅ SQLAlchemy 로드 성공
)

echo.
echo [2단계] SQLAlchemy 업그레이드 시도...
echo 최신 SQLAlchemy 2.x 설치 중...
pip install --upgrade sqlalchemy

echo.
echo [3단계] 호환성 확인...
python -c "
try:
    import sqlalchemy
    from sqlalchemy import create_engine
    print(f'✅ SQLAlchemy {sqlalchemy.__version__} 로드 성공')
    
    # 간단한 엔진 생성 테스트
    engine = create_engine('sqlite:///:memory:')
    print('✅ 엔진 생성 테스트 성공')
    
except Exception as e:
    print(f'❌ SQLAlchemy 호환성 문제: {e}')
"

echo.
echo [4단계] AIRISS 서버 재시작...
echo "서버를 재시작하여 변경사항을 적용합니다."
echo "Ctrl+C로 중지 후 start_airiss_python313.bat 실행하세요"

pause
