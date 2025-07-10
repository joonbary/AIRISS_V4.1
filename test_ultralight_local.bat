@echo off
REM AIRISS v4.1 Local Test - Encoding Safe
REM Test ultra-light configuration locally before deployment

echo ==========================================
echo    AIRISS v4.1 Local Test Suite
echo ==========================================

echo.
echo [1/5] Checking Python environment...
python --version
if errorlevel 1 (
    echo ERROR: Python not found
    goto :error
)

echo [2/5] Installing ultra-light dependencies...
pip install -r requirements_vercel_ultralight.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies  
    goto :error
)

echo [3/5] Testing ultra-light API...
python -c "from api.index_ultralight import app; print('API import: SUCCESS')"
if errorlevel 1 (
    echo ERROR: API import failed
    goto :error
)

echo [4/5] Starting test server...
echo Starting server on http://localhost:8000
echo Press Ctrl+C to stop
echo.
uvicorn api.index_ultralight:app --host 0.0.0.0 --port 8000 --reload

echo [5/5] Test completed

goto :end

:error
echo.
echo TEST FAILED - Please check errors above
pause
goto :end

:end
echo.
echo Test session ended
pause
