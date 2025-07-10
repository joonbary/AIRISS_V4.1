@echo off
REM AIRISS One-Click Solution
REM Automatic port conflict resolution and server start

title AIRISS v4.1 One-Click Solution

echo ========================================
echo AIRISS v4.1 One-Click Solution
echo ========================================
echo Automatic port resolution and server start
echo.

cd /d "%~dp0"

REM Step 1: Environment check
echo [1/6] Environment check...
if not exist app\main.py (
    echo ERROR: AIRISS project not found
    echo Please run from correct directory
    pause
    exit /b 1
)

REM Step 2: Virtual environment
echo [2/6] Virtual environment setup...
if exist venv_new\Scripts\activate.bat (
    call venv_new\Scripts\activate.bat
    echo Using venv_new
) else if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    echo Using venv
) else (
    echo ERROR: No virtual environment found
    echo Creating new environment...
    python -m venv venv_new
    call venv_new\Scripts\activate.bat
    pip install -r requirements.txt
)

REM Step 3: Port cleanup
echo [3/6] Port cleanup...
for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr :8002') do (
    taskkill /PID %%a /F >nul 2>&1
)

REM Step 4: Find available port
echo [4/6] Finding available port...
set "target_port=8002"
for %%p in (8002 8003 8004 8005) do (
    netstat -ano | findstr :%%p >nul
    if errorlevel 1 (
        set target_port=%%p
        goto :port_found
    )
)

:port_found
echo Selected port: %target_port%

REM Step 5: Environment variables
echo [5/6] Setting environment...
set SERVER_PORT=%target_port%
set WS_HOST=localhost

REM Step 6: Start server
echo [6/6] Starting AIRISS server...
echo.
echo ========================================
echo AIRISS v4.1 Server Starting
echo ========================================
echo URL: http://localhost:%target_port%
echo Dashboard: http://localhost:%target_port%/dashboard
echo API Docs: http://localhost:%target_port%/docs
echo Health: http://localhost:%target_port%/health
echo ========================================
echo.

python -m uvicorn app.main:app --host 0.0.0.0 --port %target_port%

if errorlevel 1 (
    echo.
    echo ERROR: Server failed to start
    echo Please check the error messages above
    pause
) else (
    echo.
    echo Server stopped normally
    pause
)
