@echo off
echo ===============================================
echo AIRISS Railway Web UI Deployment Guide
echo ===============================================

echo Step 1: Check GitHub sync status...
git status
if %errorlevel% neq 0 (
    echo [WARNING] Not a git repository or git not available
    echo Make sure your code is pushed to GitHub: https://github.com/joonbary/AIRISS_V4.1
)

echo.
echo Step 2: Verify essential files for Railway...
if exist "Dockerfile" (
    echo ✅ Dockerfile found
) else (
    echo ❌ Dockerfile missing - Railway needs this!
)

if exist "railway.json" (
    echo ✅ railway.json found  
) else (
    echo ❌ railway.json missing - Railway needs this!
)

if exist "requirements.txt" (
    echo ✅ requirements.txt found
) else (
    echo ❌ requirements.txt missing
)

if exist "app\main.py" (
    echo ✅ app\main.py found
) else (
    echo ❌ app\main.py missing
)

echo.
echo Step 3: Test app import...
python -c "
import sys
sys.path.append('.')
try:
    from app.main import app
    print('✅ App imports successfully')
    print(f'Title: {app.title}')
    print(f'Version: {app.version}')
except Exception as e:
    print('❌ App import failed:', str(e))
"

echo.
echo ===============================================
echo Pre-deployment check completed!
echo ===============================================

echo.
echo Ready to deploy to Railway?
echo Your GitHub repo: https://github.com/joonbary/AIRISS_V4.1
echo.

echo Continue with Railway deployment? (Y/N)
set /p continue=
if /i "%continue%"=="Y" (
    echo.
    echo 🚀 Opening Railway deployment guide...
    echo Follow the steps below:
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
    echo ✅ Railway will provide a live URL when deployment completes!
    
    echo.
    echo Opening Railway in browser...
    start https://railway.app
)

pause
