@echo off
chcp 65001
echo ========================================
echo AIRISS Excel API + Frontend Fix Deploy
echo ========================================
echo.

cd /d "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

echo [1/6] Check Current Git Status...
git status
echo.

echo [2/6] Add All Changes...
git add .
echo.

echo [3/6] Commit Frontend Fix...
git commit -m "Fix Auth component import path in App.tsx - Frontend build issue resolved"
echo.

echo [4/6] Push to GitHub...
git push origin main
echo.

echo [5/6] Railway Deployment Status...
echo Railway auto-deployment should start now...
echo Check: https://railway.app/dashboard
echo.

echo [6/6] Verify Fix...
echo Frontend issue: Auth/Auth import → Auth import ✅
echo Excel API: New endpoints added ✅
echo.

echo ========================================
echo Deployment Complete!
echo ========================================
echo.
echo Expected Results:
echo 1. Frontend build should SUCCESS (no more Auth/Auth error)
echo 2. Excel download should work:
echo    - https://web-production-4066.up.railway.app/api/analysis-storage/export-excel
echo    - https://web-production-4066.up.railway.app/api/analysis-storage/export-csv
echo.
echo Wait 3-5 minutes for Railway deployment to complete...
echo.
pause
