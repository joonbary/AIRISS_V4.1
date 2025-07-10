@echo off
REM AIRISS Ultimate Fix - Solves all compatibility issues
REM One-click solution for Python 3.13 + AIRISS v4.1

title AIRISS Ultimate Fix

echo ========================================
echo AIRISS v4.1 Ultimate Compatibility Fix
echo ========================================
echo This will solve Python 3.13 + pandas issues
echo and start your AIRISS server successfully
echo.

cd /d "%~dp0"

echo [1/7] System check...
python --version
if errorlevel 1 (
    echo ERROR: Python not found in PATH
    echo Please install Python 3.11+ and try again
    pause
    exit /b 1
)

echo [2/7] Backup original files...
if exist requirements.txt (
    if not exist requirements_original.txt (
        copy requirements.txt requirements_original.txt >nul
    )
)

echo [3/7] Clean problematic environments...
if exist venv_new (
    echo Removing venv_new...
    rmdir /s /q venv_new
)
if exist venv (
    echo Removing venv...
    rmdir /s /q venv
)

echo [4/7] Create compatible environment...
python -m venv venv_fixed
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

echo [5/7] Install compatible packages...
call venv_fixed\Scripts\activate.bat

echo Upgrading pip...
python -m pip install --upgrade pip

echo Installing core packages...
pip install --only-binary=all fastapi==0.104.1
pip install --only-binary=all "uvicorn[standard]==0.24.0" 
pip install --only-binary=all python-multipart==0.0.6
pip install --only-binary=all jinja2==3.1.2

echo Installing data packages...
pip install --only-binary=all "pandas>=2.2.0"
pip install --only-binary=all "numpy>=1.24.0"
pip install --only-binary=all openpyxl==3.1.2

echo Installing ML packages...
pip install --only-binary=all "scikit-learn>=1.3.0"
pip install --only-binary=all "scipy>=1.11.0"

echo Installing remaining packages...
pip install --only-binary=all aiosqlite==0.19.0
pip install --only-binary=all aiofiles==23.2.1
pip install --only-binary=all python-dotenv==1.0.0
pip install --only-binary=all "pydantic>=2.5.0"
pip install --only-binary=all websockets==12.0

echo [6/7] Testing installation...
python -c "import fastapi, uvicorn, pandas, numpy, sklearn; print('✓ All packages imported successfully')"
if errorlevel 1 (
    echo ERROR: Package import test failed
    echo Please check error messages above
    pause
    exit /b 1
)

echo [7/7] Starting AIRISS server...
echo.
echo ========================================
echo AIRISS v4.1 Server Starting
echo ========================================

REM Kill any existing processes on target ports
for %%p in (8002 8003 8004 8005) do (
    for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr :%%p') do (
        taskkill /PID %%a /F >nul 2>&1
    )
)

REM Find available port and start
for %%p in (8002 8003 8004 8005) do (
    netstat -ano | findstr :%%p >nul
    if errorlevel 1 (
        echo Starting on port %%p...
        echo.
        echo ✓ Main Interface: http://localhost:%%p/
        echo ✓ Dashboard: http://localhost:%%p/dashboard  
        echo ✓ API Docs: http://localhost:%%p/docs
        echo ✓ Health Check: http://localhost:%%p/health
        echo.
        echo ========================================
        echo.
        python -m uvicorn app.main:app --host 0.0.0.0 --port %%p
        goto :end
    )
)

echo ERROR: No available ports found
echo Please run emergency_cleanup.bat first

:end
if errorlevel 1 (
    echo.
    echo ERROR: Server failed to start
    echo Check error messages above
    pause
) else (
    echo.
    echo Server stopped normally
    pause
)
