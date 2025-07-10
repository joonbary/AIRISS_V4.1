@echo off
chcp 65001 >nul 2>&1
echo ============================================================
echo AIRISS Manual Cleanup - Remove Problematic Files
echo ============================================================
echo.

cd /d "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

echo Step 1: Stopping any running processes...
taskkill /f /im "git.exe" 2>nul
taskkill /f /im "python.exe" 2>nul

echo.
echo Step 2: Taking ownership of problematic directories...
takeown /f ".elasticbeanstalk" /r /d y 2>nul
icacls ".elasticbeanstalk" /grant Everyone:F /t 2>nul

echo.
echo Step 3: Force removing directories...
rmdir /s /q ".elasticbeanstalk" 2>nul
rmdir /s /q "__pycache__" 2>nul
rmdir /s /q ".git\logs" 2>nul

echo.
echo Step 4: Cleaning git cache...
git rm -r --cached . 2>nul
git clean -fxd

echo.
echo Step 5: Reinitializing git if needed...
git init

echo.
echo ============================================================
echo Manual cleanup completed!
echo Now run: git_upload_fix_english.bat
echo ============================================================
pause