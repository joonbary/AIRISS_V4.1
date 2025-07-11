@echo off
REM AIRISS Excel API Deployment to Railway - English Only
REM Fix encoding issues by using English-only commands

echo ========================================
echo AIRISS Excel API Deployment to Railway
echo ========================================
echo.

REM Change to project directory
cd /d "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

echo Step 1: Check Git status
git status

echo.
echo Step 2: Add all changes
git add .

echo.
echo Step 3: Commit with Excel API improvements
git commit -m "Add Excel export API endpoints with real file download"

echo.
echo Step 4: Push to GitHub (triggers Railway auto-deploy)
git push origin main

echo.
echo Step 5: Wait for Railway deployment (60 seconds)
echo Railway will automatically deploy from GitHub...
timeout /t 60 /nobreak

echo.
echo Step 6: Test the deployed Excel API
echo Testing Railway deployment...

REM Test the deployed API using curl or similar
echo Testing: https://web-production-4066.up.railway.app/health
curl -s "https://web-production-4066.up.railway.app/health" | findstr "healthy"

echo.
echo Step 7: Test Excel download endpoint
echo Testing: https://web-production-4066.up.railway.app/api/analysis-storage/export-excel
curl -I "https://web-production-4066.up.railway.app/api/analysis-storage/export-excel"

echo.
echo ========================================
echo Deployment Complete!
echo ========================================
echo.
echo Excel Download URL:
echo https://web-production-4066.up.railway.app/api/analysis-storage/export-excel
echo.
echo CSV Download URL:
echo https://web-production-4066.up.railway.app/api/analysis-storage/export-csv
echo.
pause
