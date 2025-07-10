@echo off
REM AIRISS Quick Fix for Python 3.13
REM Fastest solution - uses compatible requirements

title AIRISS Quick Python 3.13 Fix

echo ========================================
echo AIRISS Quick Python 3.13 Fix
echo ========================================
echo This will fix pandas compatibility issues
echo.

cd /d "%~dp0"

echo [1/4] Backup original requirements...
if exist requirements.txt (
    copy requirements.txt requirements_original_backup.txt >nul
    echo Original requirements backed up
)

echo.
echo [2/4] Update requirements file...
copy requirements_compatible.txt requirements.txt >nul
echo Requirements updated to Python 3.13 compatible versions

echo.
echo [3/4] Clean and recreate environment...
if exist venv_new (
    rmdir /s /q venv_new
)

python -m venv venv_new
call venv_new\Scripts\activate.bat

echo.
echo [4/4] Install compatible packages...
python -m pip install --upgrade pip
pip install --only-binary=all -r requirements.txt

echo.
echo Testing installation...
python -c "import fastapi, uvicorn, pandas; print('SUCCESS: All key packages working')"

if errorlevel 1 (
    echo FAILED: Please try fix_python_compatibility.bat
    pause
    exit /b 1
)

echo.
echo ========================================
echo Quick fix complete! Starting server...
echo ========================================

REM Start server on available port
for %%p in (8003 8004 8005) do (
    netstat -ano | findstr :%%p >nul
    if errorlevel 1 (
        echo Starting on port %%p...
        python -m uvicorn app.main:app --host 0.0.0.0 --port %%p
        goto :end
    )
)

:end
pause
