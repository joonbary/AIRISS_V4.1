@echo off
chcp 65001 >nul
echo ================================
echo AIRISS Railway Fixed Deployment
echo ================================
echo.

echo [1/4] Git status check...
git status

echo.
echo [2/4] Adding all changes...
git add .

echo.
echo [3/4] Committing changes...
git commit -m "Fix Railway deployment: PORT and healthcheck issues"

echo.
echo [4/4] Pushing to GitHub...
git push origin main

echo.
echo ================================
echo Railway will auto-deploy from GitHub
echo Check Railway dashboard in 2-3 minutes
echo ================================
echo.

echo Fixed Issues:
echo - PORT environment variable support
echo - curl added for healthcheck
echo - Dynamic port configuration
echo.

pause
