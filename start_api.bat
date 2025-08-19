@echo off
echo.
echo ========================================
echo    Starting AIRISS FastAPI Server
echo ========================================
echo.

cd /d "%~dp0\app"

echo Starting FastAPI server on port 8080...
echo.
echo Server will be available at:
echo - http://localhost:8080
echo - http://localhost:8080/airiss (Main Application)
echo - http://localhost:8080/api/v1/health (Health Check)
echo.
echo Press Ctrl+C to stop the server
echo.

uvicorn main:app --reload --port 8080 --host 0.0.0.0

pause