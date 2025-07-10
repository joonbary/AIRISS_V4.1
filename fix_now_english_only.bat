@echo off
echo AIRISS v4.1 Railway CRITICAL FIX - Dockerfile Restore
echo.
echo Checking Dockerfile...
dir Dockerfile
echo.
echo Adding files to git...
git add Dockerfile
git add railway.json
echo.
echo Committing critical fix...
git commit -m "CRITICAL FIX: Restore missing Dockerfile for Railway deployment"
echo.
echo Pushing to GitHub...
git push origin main
echo.
echo SUCCESS: Critical fix deployed!
echo.
echo Monitor Railway: https://railway.app/project/
echo Test URL: https://web-production-4066.up.railway.app/health
echo.
pause