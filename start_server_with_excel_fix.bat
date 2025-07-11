@echo off
chcp 65001
echo ========================================
echo AIRISS Local Server Start (Excel Fix)
echo ========================================
echo.

cd /d "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

echo [1/3] Check Python and dependencies...
python --version
pip show fastapi uvicorn pandas openpyxl
echo.

echo [2/3] Starting AIRISS server...
echo Server will be available at: http://localhost:8002
echo.
echo New Excel endpoints:
echo - Excel: http://localhost:8002/api/analysis-storage/export-excel
echo - CSV:   http://localhost:8002/api/analysis-storage/export-csv
echo.

echo [3/3] Launch server...
python -m uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload

echo.
echo ========================================
echo Server Stopped
echo ========================================
pause
