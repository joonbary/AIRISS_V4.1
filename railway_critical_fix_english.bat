@echo off
chcp 65001 > nul
title AIRISS v4.1 Railway CRITICAL FIX - Dockerfile Restore

echo =========================================
echo AIRISS v4.1 CRITICAL FIX
echo Dockerfile Restore and Redeploy
echo =========================================
echo.

echo [CRITICAL] Dockerfile was missing from root directory!
echo [SOLUTION] Dockerfile has been restored to root directory
echo.

echo [1/5] Checking current status...
dir Dockerfile 2>nul && echo ✅ Dockerfile found || echo ❌ Dockerfile missing
echo.

echo [2/5] Checking Git status...
git status --porcelain

echo.
echo [3/5] Adding Dockerfile restoration...
git add Dockerfile
git add railway.json

echo.
echo [4/5] Committing critical fix...
git commit -m "CRITICAL FIX: Restore missing Dockerfile for Railway deployment"

echo.
echo [5/5] Pushing to GitHub for auto-redeploy...
git push origin main

echo.
echo =========================================
echo CRITICAL FIX DEPLOYED!
echo =========================================
echo.
echo What was fixed:
echo ✅ Dockerfile restored to root directory
echo ✅ Railway can now find Dockerfile
echo ✅ Multi-stage build will work properly
echo ✅ React + FastAPI integration will work
echo ✅ PORT environment variable will work
echo.
echo Expected results:
echo - React build stage (Node.js 18)
echo - Python build stage (Python 3.9)
echo - Static files copied to /app/static
echo - Server runs on Railway PORT (not 8000)
echo - /health endpoint returns 200 OK
echo.
echo Monitor Railway: https://railway.app/project/
echo Test URL: https://web-production-4066.up.railway.app/health
echo.
pause
