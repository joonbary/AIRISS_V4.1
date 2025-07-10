@echo off
chcp 65001 > nul
echo ===============================================
echo AIRISS v5.0 - FINAL SOLUTION
echo ===============================================
echo.

REM 환경 변수 설정
set PYTHONPATH=%CD%
set PYTHONIOENCODING=utf-8

echo 🔍 환경 점검 중...
echo 현재 디렉토리: %CD%
echo Python 경로: %PYTHONPATH%
echo.

REM Python 버전 확인
python --version
if errorlevel 1 (
    echo ❌ Python이 설치되지 않았거나 PATH에 없습니다.
    pause
    exit /b 1
)

REM 환경 점검 스크립트 실행
echo 🧪 환경 점검 실행 중...
python debug_environment.py
echo.

REM 의존성 확인
echo 📦 의존성 설치 확인...
pip install -r requirements.txt --quiet
echo.

REM 실행 방법 선택
echo 🚀 AIRISS v5.0 시작 방법을 선택하세요:
echo 1. uvicorn 명령어 실행 (권장)
echo 2. Python 모듈 실행
echo 3. 직접 Python 실행
echo.

choice /c 123 /n /m "선택하세요 (1, 2, 3): "

if errorlevel 3 goto method3
if errorlevel 2 goto method2
if errorlevel 1 goto method1

:method1
echo.
echo 🔧 방법 1: uvicorn 명령어 실행
echo uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
echo.
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
goto end

:method2
echo.
echo 🔧 방법 2: Python 모듈 실행
echo python -m uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
echo.
python -m uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
goto end

:method3
echo.
echo 🔧 방법 3: 직접 Python 실행
echo python -c "from app.main import app; import uvicorn; uvicorn.run(app, host='0.0.0.0', port=8002)"
echo.
python -c "from app.main import app; import uvicorn; uvicorn.run(app, host='0.0.0.0', port=8002)"
goto end

:end
echo.
echo 서버가 종료되었습니다.
pause
