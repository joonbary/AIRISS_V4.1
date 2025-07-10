@echo off
REM Connect to GitHub repo: joonbary/AIRISS_V4.1
REM Safe encoding - English only

title AIRISS GitHub Connect

echo ==========================================
echo AIRISS v4.1 GitHub Connection
echo Repository: joonbary/AIRISS_V4.1
echo ==========================================

cd /d "%~dp0"

echo Step 1: Prepare requirements...
copy requirements_vercel.txt requirements.txt >nul

echo Step 2: Check Git status...
git status >nul 2>&1
if errorlevel 1 (
    echo Initializing Git...
    git init
    git add .
    git commit -m "Initial commit: AIRISS v4.1"
)

echo Step 3: Connect to GitHub...
git remote remove origin >nul 2>&1
git remote add origin https://github.com/joonbary/AIRISS_V4.1.git

echo Step 4: Push to GitHub...
git branch -M main
git push -u origin main

if errorlevel 1 (
    echo.
    echo ==========================================
    echo ERROR: Push failed
    echo ==========================================
    echo.
    echo Possible solutions:
    echo 1. Check GitHub login credentials
    echo 2. Ensure repository exists and is accessible
    echo 3. Try manual push with authentication
    echo.
    echo Manual command:
    echo git push -u origin main
    echo.
    pause
    exit /b 1
)

echo.
echo ==========================================
echo SUCCESS: Code pushed to GitHub!
echo ==========================================
echo.
echo Repository: https://github.com/joonbary/AIRISS_V4.1
echo.
echo Next step: Deploy to Vercel
echo 1. Go to: https://vercel.com/new
echo 2. Connect GitHub account
echo 3. Select repository: AIRISS_V4.1
echo 4. Click Deploy
echo.

pause

echo Opening Vercel deployment...
start https://vercel.com/new

echo.
echo Ready for Vercel deployment!
