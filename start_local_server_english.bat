@echo off
REM AIRISS Local Server Startup - English Only
REM Avoid encoding issues with English-only content

echo ========================================
echo AIRISS v4.1 Local Server Startup
echo ========================================
echo.

REM Change to project directory
cd /d "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

echo System Information:
echo Python Version:
python --version
echo Current Directory: %CD%
echo.

echo Starting AIRISS server...
echo.
echo Available URLs after startup:
echo - Health Check: http://localhost:8002/health
echo - Excel Download: http://localhost:8002/api/analysis-storage/export-excel
echo - CSV Download: http://localhost:8002/api/analysis-storage/export-csv
echo - API Info: http://localhost:8002/api
echo.

echo Starting server on port 8002...
python -m uvicorn app.main:app --host 0.0.0.0 --port 8002

echo.
echo Server stopped.
pause
