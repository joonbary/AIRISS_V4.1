@echo off
echo ========================================
echo AIRISS v4.0 - Fixed Server with Job Tracking
echo ========================================
echo.

REM Run migration to ensure jobs table exists
echo [1/3] Running database migration...
python create_jobs_table.py
if errorlevel 1 (
    echo Error: Migration failed!
    pause
    exit /b 1
)

echo.
echo [2/3] Checking environment...
if exist venv\Scripts\activate (
    echo Activating virtual environment...
    call venv\Scripts\activate
) else (
    echo Warning: Virtual environment not found
)

echo.
echo [3/3] Starting fixed server...
echo.
echo Server Features:
echo - Persistent job tracking in database
echo - Complete E2E flow support
echo - Job status always available
echo.
echo Starting on http://localhost:8006
echo API Docs: http://localhost:8006/docs
echo.

REM Start the fixed server
python -m app.main_fixed

pause