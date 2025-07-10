@echo off
chcp 65001 > nul
echo ===============================================
echo AIRISS v5.0 - 즉시 실행
echo ===============================================
echo.

REM 환경 변수 설정
set PYTHONPATH=%CD%
set PYTHONIOENCODING=utf-8

echo 🚀 AIRISS v5.0 시작 중...
echo 접속: http://localhost:8002
echo 종료: Ctrl+C
echo.

REM 직접 uvicorn 실행 (가장 안전한 방법)
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
