@echo off
chcp 65001 >nul 2>&1
cd /d "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

echo ========================================
echo AIRISS Railway Deployment Checker
echo ========================================
echo.

set "ERRORS=0"

echo [Checking Essential Files...]
echo.

REM Check Procfile
if exist "Procfile" (
    echo ✅ Procfile: EXISTS
    echo    Content:
    type "Procfile" | findstr /C:"web:" >nul
    if %errorlevel% equ 0 (
        echo    ✅ Contains web process definition
    ) else (
        echo    ❌ Missing web process definition
        set /a ERRORS+=1
    )
) else (
    echo ❌ Procfile: MISSING - CRITICAL
    set /a ERRORS+=1
)
echo.

REM Check requirements.txt
if exist "requirements.txt" (
    echo ✅ requirements.txt: EXISTS
    findstr /C:"fastapi" requirements.txt >nul
    if %errorlevel% equ 0 (
        echo    ✅ FastAPI dependency found
    ) else (
        echo    ❌ FastAPI dependency missing
        set /a ERRORS+=1
    )
    findstr /C:"uvicorn" requirements.txt >nul
    if %errorlevel% equ 0 (
        echo    ✅ Uvicorn dependency found
    ) else (
        echo    ❌ Uvicorn dependency missing
        set /a ERRORS+=1
    )
) else (
    echo ❌ requirements.txt: MISSING - CRITICAL
    set /a ERRORS+=1
)
echo.

REM Check main application file
if exist "main.py" (
    echo ✅ main.py: EXISTS
) else if exist "app.py" (
    echo ✅ app.py: EXISTS
) else if exist "application.py" (
    echo ✅ application.py: EXISTS
) else (
    echo ❌ Main application file (main.py/app.py): MISSING - CRITICAL
    set /a ERRORS+=1
)
echo.

REM Check frontend structure
if exist "frontend" (
    echo ✅ Frontend folder: EXISTS
    if exist "frontend\package.json" (
        echo    ✅ package.json found in frontend
    ) else (
        echo    ❌ package.json missing in frontend
        set /a ERRORS+=1
    )
) else if exist "airiss-v4-frontend" (
    echo ✅ Frontend folder: EXISTS (airiss-v4-frontend)
    if exist "airiss-v4-frontend\package.json" (
        echo    ✅ package.json found in frontend
    ) else (
        echo    ❌ package.json missing in frontend
        set /a ERRORS+=1
    )
) else (
    echo ❌ Frontend folder: NOT FOUND
    set /a ERRORS+=1
)
echo.

REM Check environment variables
if exist ".env.example" (
    echo ✅ .env.example: EXISTS
) else (
    echo ⚠️  .env.example: MISSING (recommended for Railway)
)

if exist ".env" (
    echo ⚠️  .env: EXISTS (should be in .gitignore)
)
echo.

REM Check Railway configuration
if exist "railway.json" (
    echo ✅ railway.json: EXISTS
) else (
    echo ⚠️  railway.json: MISSING (optional but recommended)
)
echo.

REM Check runtime
if exist "runtime.txt" (
    echo ✅ runtime.txt: EXISTS
    echo    Content:
    type "runtime.txt"
) else (
    echo ⚠️  runtime.txt: MISSING (Python version not specified)
)
echo.

echo [Checking Git Status...]
git status --porcelain >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Git repository: INITIALIZED
) else (
    echo ❌ Git repository: NOT INITIALIZED
    set /a ERRORS+=1
)
echo.

echo ========================================
echo DEPLOYMENT READINESS SUMMARY
echo ========================================

if %ERRORS% equ 0 (
    echo ✅ STATUS: READY FOR RAILWAY DEPLOYMENT
    echo.
    echo Next Steps:
    echo 1. Run github_upload_fix.bat to push to GitHub
    echo 2. Connect repository to Railway
    echo 3. Deploy to Railway
) else (
    echo ❌ STATUS: NOT READY - %ERRORS% ERRORS FOUND
    echo.
    echo Please fix the errors above before deploying to Railway.
    echo.
    echo Common fixes:
    echo - Ensure Procfile exists with: web: uvicorn main:app --host 0.0.0.0 --port $PORT
    echo - Add FastAPI and uvicorn to requirements.txt
    echo - Make sure main.py or app.py contains FastAPI application
)

echo.
echo Press any key to continue...
pause >nul