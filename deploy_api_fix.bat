@echo off
echo AIRISS v4.1 - Fix API route conflicts

echo Adding changes...
git add app/main.py

echo Committing...
git commit -m "Fix API route conflicts: Remove mount conflicts, use explicit routing"

echo Pushing to GitHub...
git push origin main

echo.
echo ✅ API route conflict fix deployed!
echo 🌐 Test URLs after deployment:
echo   https://web-production-4066.up.railway.app/health
echo   https://web-production-4066.up.railway.app/api
echo   https://web-production-4066.up.railway.app/
echo.
pause
