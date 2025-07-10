@echo off
chcp 65001 >nul 2>&1
echo ============================================================
echo AIRISS Git Upload Fix - Complete Solution
echo ============================================================
echo.

cd /d "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

echo Step 1: Checking current git status...
git status

echo.
echo Step 2: Force removing problematic directories...
rmdir /s /q ".elasticbeanstalk\logs" 2>nul
rmdir /s /q ".elasticbeanstalk" 2>nul
echo Problematic directories removed.

echo.
echo Step 3: Adding all changes...
git add .

echo.
echo Step 4: Committing with English message only...
git commit -m "Neon DB Integration Complete - PostgreSQL Only Architecture"

echo.
echo Step 5: Pulling with unrelated histories fix...
git pull origin main --allow-unrelated-histories --no-edit

echo.
echo Step 6: Pushing to remote...
git push origin main

echo.
echo ============================================================
echo Git upload process completed!
echo ============================================================
pause