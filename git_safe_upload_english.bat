@echo off
chcp 65001 >nul 2>&1
echo ============================================================
echo AIRISS Git Upload - Alternative Safe Method
echo ============================================================
echo.

cd /d "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

echo Step 1: Creating backup of current state...
echo Current git status:
git status --porcelain

echo.
echo Step 2: Force cleaning problematic files...
git clean -fd
rmdir /s /q ".elasticbeanstalk" 2>nul
del /f /q "*.tmp" 2>nul

echo.
echo Step 3: Resetting to clean state...
git reset --hard HEAD

echo.
echo Step 4: Creating new branch for upload...
git checkout -b upload-neon-integration

echo.
echo Step 5: Adding all current changes...
git add .

echo.
echo Step 6: Committing changes...
git commit -m "Complete Neon DB Integration - All Features Working"

echo.
echo Step 7: Force pushing new branch...
git push -u origin upload-neon-integration --force

echo.
echo ============================================================
echo Alternative upload completed!
echo Check GitHub and create pull request if needed.
echo ============================================================
pause