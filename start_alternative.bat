@echo off
REM AIRISS Alternative Port Launcher
REM Safe encoding for Windows compatibility

title AIRISS v4.1 Alternative Port Launcher

echo ========================================
echo AIRISS v4.1 Alternative Port Launcher
echo ========================================

REM Check available ports
set "available_port="

echo Checking available ports...
for %%p in (8003 8004 8005 8006 8007) do (
    netstat -ano | findstr :%%p >nul
    if errorlevel 1 (
        echo Port %%p is available
        if not defined available_port set available_port=%%p
    ) else (
        echo Port %%p is in use
    )
)

if not defined available_port (
    echo ERROR: No alternative ports available
    echo Please run fix_port_safe.bat first
    pause
    exit /b 1
)

echo.
echo Selected port: %available_port%
echo.

REM Activate virtual environment
cd /d "%~dp0"
if exist venv_new\Scripts\activate.bat (
    echo Activating venv_new...
    call venv_new\Scripts\activate.bat
) else if exist venv\Scripts\activate.bat (
    echo Activating venv...
    call venv\Scripts\activate.bat
) else (
    echo ERROR: No virtual environment found
    echo Please run setup first
    pause
    exit /b 1
)

REM Set environment variables
set SERVER_PORT=%available_port%
set WS_HOST=localhost

echo Starting AIRISS v4.1 on port %available_port%...
echo.
echo URL: http://localhost:%available_port%
echo Dashboard: http://localhost:%available_port%/dashboard
echo Health: http://localhost:%available_port%/health
echo.

python -m uvicorn app.main:app --host 0.0.0.0 --port %available_port%

pause
