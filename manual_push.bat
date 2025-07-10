@echo off
REM Manual GitHub Push - Safe fallback
REM For repository: joonbary/AIRISS_V4.1

title AIRISS Manual Push

echo ==========================================
echo AIRISS v4.1 Manual GitHub Push
echo Repository: joonbary/AIRISS_V4.1
echo ==========================================

cd /d "%~dp0"

echo Preparing files...
copy requirements_vercel.txt requirements.txt >nul

echo.
echo Copy and paste these commands one by one:
echo.
echo ==========================================
echo COMMAND 1: Initialize Git
echo ==========================================
echo git init
echo.
echo ==========================================
echo COMMAND 2: Add files
echo ==========================================
echo git add .
echo.
echo ==========================================
echo COMMAND 3: Commit
echo ==========================================
echo git commit -m "Initial commit: AIRISS v4.1"
echo.
echo ==========================================
echo COMMAND 4: Connect to GitHub
echo ==========================================
echo git remote add origin https://github.com/joonbary/AIRISS_V4.1.git
echo.
echo ==========================================
echo COMMAND 5: Push to GitHub
echo ==========================================
echo git branch -M main
echo git push -u origin main
echo.
echo ==========================================

pause

echo Opening GitHub repository...
start https://github.com/joonbary/AIRISS_V4.1

echo.
echo After successful push, go to Vercel:
start https://vercel.com/new
