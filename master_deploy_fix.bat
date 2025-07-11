@echo off
chcp 65001 >nul 2>&1
cd /d "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

echo ================================================
echo AIRISS Railway Deployment - Master Fix Script
echo ================================================
echo.
echo This script will:
echo 1. Fix missing files for Railway deployment
echo 2. Check deployment readiness  
echo 3. Fix GitHub upload issues
echo 4. Upload to GitHub
echo.
echo Press any key to start the complete fix process...
pause >nul
echo.

echo ================================================
echo STEP 1: Auto-Fix Missing Files
echo ================================================
call auto_fix_missing_files.bat
echo.

echo ================================================
echo STEP 2: Check Railway Deployment Readiness
echo ================================================
call railway_deploy_check.bat
echo.

echo ================================================
echo STEP 3: Fix GitHub Upload Issues
echo ================================================
echo Starting GitHub upload fix...
call github_upload_fix.bat
echo.

echo ================================================
echo DEPLOYMENT PROCESS COMPLETED
echo ================================================
echo.
echo If all steps completed successfully:
echo 1. Your project is now uploaded to GitHub
echo 2. Go to Railway.app
echo 3. Connect your GitHub repository
echo 4. Deploy your project
echo.
echo GitHub Repository URL: https://github.com/joonbary/AIRISS_V4.1
echo.
echo Press any key to exit...
pause >nul