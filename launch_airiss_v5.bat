@echo off
echo ===============================================
echo AIRISS v5.0 - Status Check and Launch
echo ===============================================
echo.

echo Step 1: Check current git status
echo ===============================================
git status
echo.

echo Step 2: Check if .env file exists and is configured
echo ===============================================
if exist .env (
    echo .env file exists
    echo Checking for OpenAI API key...
    findstr /C:"OPENAI_API_KEY=sk-" .env >nul
    if %errorlevel%==0 (
        echo OpenAI API key is configured
    ) else (
        echo WARNING: OpenAI API key not found or not configured
    )
) else (
    echo .env file not found, creating from template...
    copy .env.template .env
    echo Please edit .env file with your actual API keys
    notepad .env
    pause
)

echo.
echo Step 3: Check Python environment
echo ===============================================
python --version
echo.

echo Step 4: Verify app/main.py exists
echo ===============================================
if exist app\main.py (
    echo app/main.py found
) else (
    echo ERROR: app/main.py not found
    echo Current directory contents:
    dir /B
    pause
    exit /b 1
)

echo.
echo Step 5: Start AIRISS v5.0
echo ===============================================
echo Starting AIRISS v5.0...
echo Access: http://localhost:8002
echo Dashboard: http://localhost:8002/dashboard
echo API Docs: http://localhost:8002/docs
echo.
echo Press Ctrl+C to stop the application
echo.
python app/main.py
