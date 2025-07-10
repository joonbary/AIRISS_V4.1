@echo off
echo ============================================
echo GitHub Upload for Railway Deployment
echo ============================================
echo.

echo Step 1: Check Git Status
git status

echo.
echo Step 2: Add All Files
git add .

echo Step 3: Commit Changes
git commit -m "AIRISS v4 ready for Railway deployment"

echo.
echo Step 4: Push to GitHub
echo Please make sure your GitHub repository is set up
echo Then run: git push origin main
echo.

echo Step 5: Deploy via Railway Website
echo 1. Go to https://railway.app
echo 2. Login and click "New Project"
echo 3. Choose "Deploy from GitHub repo"
echo 4. Select your AIRISS repository
echo 5. Railway will auto-deploy!
echo.

echo GitHub repository URL should be:
echo https://github.com/joonbary/airiss_enterprise
echo.

pause
