@echo off
echo ============================================================
echo AIRISS v4.0 - Starting with Real AI Analysis
echo ============================================================
echo.

REM Check Python
echo Checking Python installation...
python --version
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.8+
    pause
    exit /b 1
)

REM Check environment
echo.
echo Checking environment configuration...
if exist .env (
    echo [OK] .env file found
) else (
    echo [WARNING] .env file not found, using defaults
)

REM Display OpenAI status
echo.
echo OpenAI Integration Status:
if defined OPENAI_API_KEY (
    echo [OK] OPENAI_API_KEY is set - Advanced AI features available
) else (
    echo [INFO] OPENAI_API_KEY not set - Using basic NLP analysis
)

REM Start server
echo.
echo Starting AIRISS v4.0 Backend Server...
echo - Port: 8006
echo - Database: SQLite (airiss.db)
echo - AI Analysis: ENABLED
echo.
echo Press Ctrl+C to stop the server
echo.
echo ============================================================

python -m app.main