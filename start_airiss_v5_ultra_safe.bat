@echo off
chcp 65001 > nul
echo ===============================================
echo AIRISS v5.0 - Ultra Safe Start
echo ===============================================
echo.

echo Setting up environment...
set PYTHONPATH=%CD%
set PYTHONIOENCODING=utf-8

echo Current directory: %CD%
echo Python path: %PYTHONPATH%
echo.

echo Checking Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python not found in PATH
    pause
    exit /b 1
)

echo.
echo Checking uvicorn installation...
uvicorn --version
if errorlevel 1 (
    echo Installing uvicorn...
    pip install uvicorn
)

echo.
echo Starting AIRISS v5.0...
echo Access: http://localhost:8002
echo Press Ctrl+C to stop the application
echo.

REM 가장 안전한 방법: 현재 디렉토리에서 uvicorn 직접 실행
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload --log-level info
