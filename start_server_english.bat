@echo off
cls
echo ========================================
echo AIRISS v4.1 Server Start - Excel Fixed
echo ========================================
echo.

cd /d "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

echo System Information:
echo Python Version: 
python --version
echo Current Directory: %CD%
echo.

echo Starting AIRISS server...
echo Excel Download URL: http://localhost:8002/api/analysis-storage/export-excel
echo CSV Download URL:   http://localhost:8002/api/analysis-storage/export-csv
echo Health Check URL:   http://localhost:8002/health
echo.

echo Starting uvicorn server on port 8002...
python -m uvicorn app.main:app --host 0.0.0.0 --port 8002

echo.
echo Server stopped.
pause
