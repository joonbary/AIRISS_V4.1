@echo off
echo ===============================================
echo AIRISS Railway Web Deployment Guide
echo ===============================================

echo Step 1: Check GitHub sync status...
git status 2>nul
if %errorlevel% neq 0 (
    echo [WARNING] Git not available or not a git repository
    echo Make sure code is on GitHub: https://github.com/joonbary/AIRISS_V4.1
)

echo.
echo Step 2: Verify essential files for Railway...
if exist "Dockerfile" (
    echo [OK] Dockerfile found
) else (
    echo [ERROR] Dockerfile missing
)

if exist "railway.json" (
    echo [OK] railway.json found  
) else (
    echo [ERROR] railway.json missing
)

if exist "requirements.txt" (
    echo [OK] requirements.txt found
) else (
    echo [ERROR] requirements.txt missing
)

if exist "app\main.py" (
    echo [OK] app\main.py found
) else (
    echo [ERROR] app\main.py missing
)

echo.
echo Step 3: Test app import...
python -c "import sys; sys.path.append('.'); from app.main import app; print('[OK] App imports successfully')" 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] App import failed
) else (
    echo [OK] App import successful
)

echo.
echo ===============================================
echo Pre-deployment check completed
echo ===============================================

echo.
echo GitHub Repository: https://github.com/joonbary/AIRISS_V4.1
echo.
echo Continue with Railway deployment? (Y/N)
set /p continue=
if /i "%continue%"=="Y" (
    echo.
    echo Opening Railway deployment guide...
    echo.
    echo STEP BY STEP INSTRUCTIONS:
    echo.
    echo 1. Open https://railway.app in your browser
    echo 2. Click "Login" 
    echo 3. Choose "Continue with GitHub"
    echo 4. Authorize Railway to access your GitHub
    echo 5. Click "New Project"
    echo 6. Select "Deploy from GitHub repo"
    echo 7. Choose: joonbary/AIRISS_V4.1
    echo 8. Railway will auto-detect your Dockerfile
    echo 9. Click "Deploy"
    echo 10. Monitor deployment progress
    echo.
    echo Railway will provide a live URL when deployment completes!
    
    echo.
    echo Opening Railway website...
    start https://railway.app
)

pause
