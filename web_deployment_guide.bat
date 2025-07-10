@echo off
echo ============================================
echo AIRISS v4 Web Deployment Guide
echo ============================================
echo.

echo Step 1: Update GitHub Repository
echo ============================================
git add .
git commit -m "AIRISS v4 ready for Railway deployment"
git push origin main

echo.
echo Step 2: Railway Web Deployment
echo ============================================
echo 1. Go to: https://railway.app
echo 2. Click "Login" or "Sign Up"
echo 3. Click "New Project"
echo 4. Select "Deploy from GitHub repo"
echo 5. Choose: joonbary/airiss_enterprise
echo 6. Railway will auto-detect Dockerfile and deploy!
echo.

echo Your GitHub repository:
echo https://github.com/joonbary/airiss_enterprise
echo.

echo Expected deployment time: 5-10 minutes
echo.

echo Opening GitHub repository...
start https://github.com/joonbary/airiss_enterprise

echo.
echo Opening Railway website...
start https://railway.app

echo.
echo Follow the steps above to deploy via web interface!
pause
