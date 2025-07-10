@echo off
chcp 65001 >nul
echo ================================
echo AIRISS PORT FIX - Critical Update
echo ================================
echo.

echo FIXED: Railway PORT environment variable
echo - Changed SERVER_PORT to support Railway PORT
echo - Added port logging for debugging
echo.

echo [1/4] Git status check...
git status

echo.
echo [2/4] Adding PORT fix...
git add .

echo.
echo [3/4] Committing PORT fix...
git commit -m "CRITICAL FIX: Railway PORT environment variable support in main.py"

echo.
echo [4/4] Pushing PORT fix...
git push origin main

echo.
echo ================================
echo PORT FIX DEPLOYED TO RAILWAY
echo This should resolve the healthcheck failure
echo ================================
echo.

echo Key Changes:
echo - SERVER_PORT now reads Railway PORT variable
echo - Added port debugging logs
echo - Fixed uvicorn port binding
echo.

pause
