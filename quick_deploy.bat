@echo off
REM AIRISS Quick Deploy
REM Safe encoding - English only

title AIRISS Deploy

echo ========================================
echo AIRISS v4.1 Quick Deploy
echo ========================================

cd /d "%~dp0"

echo Step 1: Prepare files...
copy requirements_vercel.txt requirements.txt >nul

echo Step 2: Git init...
if exist .git rmdir /s /q .git
git init >nul
git add . >nul
git commit -m "AIRISS v4.1 deploy" >nul

echo Step 3: Done!
echo.
echo Next steps:
echo 1. Go to: https://github.com/new
echo 2. Create repo: airiss-v4  
echo 3. Copy these commands:
echo.
echo    git remote add origin https://github.com/USERNAME/airiss-v4.git
echo    git push -u origin main
echo.
echo 4. Go to: https://vercel.com/new
echo 5. Select your GitHub repo
echo 6. Click Deploy
echo.

pause
start https://github.com/new
