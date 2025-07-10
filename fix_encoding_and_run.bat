@echo off
REM 즉시 인코딩 문제 해결 및 실행

REM UTF-8 코드페이지 강제 설정
chcp 65001 > nul 2>&1

REM 모든 인코딩 환경 변수 설정
set PYTHONIOENCODING=utf-8
set PYTHONPATH=%CD%
set LANG=ko_KR.UTF-8
set LC_ALL=ko_KR.UTF-8

REM 콘솔 출력 설정
mode con: cols=100 lines=30

echo.
echo    ╔════════════════════════════════════════════════════════════════╗
echo    ║                    AIRISS v5.0 인코딩 해결                     ║
echo    ╚════════════════════════════════════════════════════════════════╝
echo.

REM 환경 정보 표시
echo [INFO] 인코딩 설정: UTF-8
echo [INFO] 현재 위치: %CD%
echo [INFO] Python 경로: %PYTHONPATH%
echo.

REM 의존성 확인
echo [CHECK] 의존성 확인 중...
pip list | findstr uvicorn > nul
if errorlevel 1 (
    echo [INSTALL] uvicorn 설치 중...
    pip install uvicorn > nul
)

REM AIRISS 실행
echo.
echo [START] AIRISS v5.0 시작 중...
echo [ACCESS] http://localhost:8002
echo [STOP] Ctrl+C로 종료
echo.

REM 실행 (여러 방법으로 시도)
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload || (
    echo [RETRY] Python 모듈 방식으로 재시도...
    python -m uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
) || (
    echo [RETRY] Python 직접 실행...
    python -X utf8 -c "import sys; sys.path.insert(0, '.'); from app.main import app; import uvicorn; uvicorn.run(app, host='0.0.0.0', port=8002)"
)
