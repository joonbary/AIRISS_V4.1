@echo off
chcp 65001 > nul
echo ===============================================
echo AIRISS v5.0 - Quick Start (Fixed)
echo ===============================================
echo.

echo Checking .env file...
if not exist .env (
    echo Creating .env file from template...
    copy .env.template .env
    echo.
    echo IMPORTANT: Please edit .env file with your actual API keys
    echo Opening .env file for editing...
    notepad .env
    echo.
    echo After editing, save the file and press any key to continue...
    pause
)

echo.
echo Checking Python environment...
python --version
echo.

echo Starting AIRISS v5.0...
echo Access: http://localhost:8002
echo Press Ctrl+C to stop the application
echo.

REM 올바른 방법으로 uvicorn 실행
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
