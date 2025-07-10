@echo off
echo AIRISS v4.1 - Fix React static files 404 issue

echo Adding changes to git...
git add app/main.py

echo Committing changes...
git commit -m "Fix React static files 404: Mount React build to root path"

echo Pushing to GitHub...
git push origin main

echo.
echo ✅ Deployment started!
echo 🌐 Check deployment: https://web-production-4066.up.railway.app/
echo.
pause
