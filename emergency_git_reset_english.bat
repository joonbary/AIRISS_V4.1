@echo off
chcp 65001 >nul 2>&1
echo ============================================================
echo AIRISS Emergency Git Reset - Nuclear Option
echo ============================================================
echo.

cd /d "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

echo WARNING: This will reset everything to clean state!
echo Press Ctrl+C to cancel, or
pause

echo Step 1: Removing git history...
rmdir /s /q ".git" 2>nul

echo Step 2: Cleaning all cache and temp files...
git clean -fxd 2>nul
rmdir /s /q "__pycache__" 2>nul
rmdir /s /q ".elasticbeanstalk" 2>nul

echo Step 3: Reinitializing git...
git init

echo Step 4: Adding remote...
git remote add origin https://github.com/joonbary/AIRISS_V4.1.git

echo Step 5: Adding all files...
git add .

echo Step 6: Initial commit...
git commit -m "Fresh Start - Neon DB Integration Complete"

echo Step 7: Creating main branch and pushing...
git branch -M main
git push -u origin main --force

echo ============================================================
echo Emergency reset completed!
echo ============================================================
pause