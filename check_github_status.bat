@echo off
echo ============================================================
echo AIRISS GitHub Repository Status Check
echo ============================================================
echo.

cd /d "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

echo Checking Git status...
git status

echo.
echo ============================================================
echo Checking last commit...
git log --oneline -5

echo.
echo ============================================================
echo Checking remote repository...
git remote -v

echo.
echo ============================================================
echo Repository URL: https://github.com/joonbary/AIRISS_V4.1.git
echo Deployment URL: https://web-production-4066.up.railway.app/dashboard
echo ============================================================
echo.
echo GitHub upload verification completed!
pause
