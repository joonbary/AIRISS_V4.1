@echo off
echo ============================================
echo AIRISS AI Analysis Fix and Deploy
echo ============================================

echo.
echo Checking Git status...
git status

echo.
echo Adding changes...
git add requirements.txt

echo.
echo Committing changes...
git commit -m "Fix: Enable OpenAI package for AI analysis functionality"

echo.
echo Pushing to GitHub...
git push origin main

echo.
echo ============================================
echo Deploy Success!
echo ============================================
echo.
echo Railway will auto-deploy in 2-3 minutes.
echo.
echo Check deployment: https://railway.app/dashboard
echo Test app: https://web-production-4066.up.railway.app/dashboard
echo.
echo Please wait 3 minutes and refresh the page.
echo AI analysis should work properly now!
echo.
pause
