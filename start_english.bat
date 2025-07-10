@echo off
chcp 65001 > nul
echo ===============================================
echo AIRISS v5.0 - English Version
echo ===============================================
echo.

set PYTHONIOENCODING=utf-8
set PYTHONPATH=%CD%
set LANG=ko_KR.UTF-8

echo Encoding: UTF-8
echo Path: %CD%
echo.

if not exist .env (
    if exist .env.template (
        copy .env.template .env > nul
        echo .env file created
    )
)

echo Starting AIRISS v5.0...
echo Access: http://localhost:8002
echo Stop: Ctrl+C
echo.

uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
