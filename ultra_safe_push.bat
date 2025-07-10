@echo off
cd /d "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

echo AIRISS v5 GitHub Push - Ultra Safe Version
echo ==========================================

echo Step 1: Check Git Status
git status
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Git not available or not in git repository
    pause
    exit /b 1
)

echo.
echo Step 2: Remove sensitive files from git cache
git rm --cached .env 2>nul
git rm --cached *.db 2>nul
git rm --cached -r __pycache__ 2>nul
git rm --cached -r venv 2>nul

echo.
echo Step 3: Stage all changes
git add .

echo.
echo Step 4: Create commit
git commit -m "AIRISS v5.0 Update: Advanced AI Features, Bias Detection, Predictive Analytics"

echo.
echo Step 5: Push to GitHub
git push origin main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo SUCCESS: Push completed successfully!
    echo GitHub: https://github.com/joonbary/AIRISS_V4.1
    echo App: https://web-production-4066.up.railway.app/dashboard
) else (
    echo.
    echo FAILED: Push failed - check connection and permissions
)

echo.
echo Recent commits:
git log --oneline -3

echo.
pause
