@echo off
cd /d "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

echo AIRISS v5 GitHub Push Script
echo ==============================

echo Checking current git status...
git status

echo.
echo Checking for sensitive files...
if exist ".env" (
    echo WARNING: .env file found - will be ignored
)
if exist "AWS*.txt" (
    echo WARNING: AWS key files found - will be ignored
)
if exist "*.db" (
    echo WARNING: Database files found - will be ignored
)

echo.
echo Cleaning git cache...
git rm --cached .env >nul 2>&1
git rm --cached "AWS*.txt" >nul 2>&1
git rm --cached "*.db" >nul 2>&1
git rm --cached -r __pycache__ >nul 2>&1
git rm --cached -r venv >nul 2>&1
git rm --cached -r venv_* >nul 2>&1

echo.
echo Staging changes...
git add .

echo.
echo Creating commit...
git commit -m "feat: AIRISS v5.0 Advanced AI Update - Deep Learning NLP Engine - Bias Detection System - Predictive Analytics - Multi-language Support - Enhanced Security - Performance Optimization - API v2 Endpoints - Real-time Monitoring - Version: v5.0.0"

echo.
echo Pushing to GitHub...
git push origin main

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Push failed! Please check:
    echo 1. Internet connection
    echo 2. GitHub authentication
    echo 3. Repository permissions
    echo.
    pause
    exit /b 1
)

echo.
echo SUCCESS: GitHub push completed!
echo Repository: https://github.com/joonbary/AIRISS_V4.1
echo Deployed App: https://web-production-4066.up.railway.app/dashboard

echo.
echo Recent commits:
git log --oneline -5

echo.
echo AIRISS v5.0 GitHub update completed successfully!
echo.
echo Next steps:
echo 1. Check Railway auto-deployment
echo 2. Verify web app functionality
echo 3. Test new v5 features
echo.
pause
