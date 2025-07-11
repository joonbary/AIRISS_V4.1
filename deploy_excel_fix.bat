@echo off
chcp 65001
echo ========================================
echo AIRISS Excel API Deploy to Railway
echo ========================================
echo.

cd /d "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

echo [1/5] Check Git Status...
git status
echo.

echo [2/5] Add All Changes...
git add .
echo.

echo [3/5] Commit Changes...
git commit -m "Add Excel export API endpoints with real file download - Fix #ExcelDownloadIssue"
echo.

echo [4/5] Push to GitHub...
git push origin main
echo.

echo [5/5] Check Railway Deployment...
echo Railway auto-deployment should start now...
echo Check: https://railway.app/dashboard
echo.

echo ========================================
echo Deployment Process Complete!
echo ========================================
echo.
echo Test URLs after deployment:
echo Excel: https://web-production-4066.up.railway.app/api/analysis-storage/export-excel
echo CSV:   https://web-production-4066.up.railway.app/api/analysis-storage/export-csv
echo.
pause
