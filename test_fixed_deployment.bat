@echo off
chcp 65001
echo ========================================
echo Test Fixed AIRISS Deployment
echo ========================================
echo.

cd /d "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

echo [1/3] Wait for Railway deployment...
echo Please wait 3-5 minutes after pushing to GitHub
echo.
pause

echo [2/3] Running deployment test...
python test_fixed_deployment.py
echo.

echo [3/3] Manual verification...
echo.
echo Open these URLs in browser to verify:
echo.
echo 1. Main App (should show login page):
echo    https://web-production-4066.up.railway.app/
echo.
echo 2. Excel Download (should download file):
echo    https://web-production-4066.up.railway.app/api/analysis-storage/export-excel
echo.
echo 3. CSV Download (should download file):
echo    https://web-production-4066.up.railway.app/api/analysis-storage/export-csv
echo.
echo ========================================
echo Verification Complete!
echo ========================================
pause
