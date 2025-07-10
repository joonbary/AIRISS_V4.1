@echo off
echo ===============================================
echo AIRISS GitHub-Based Deployment Options
echo ===============================================
echo.
echo Your code is already on GitHub, so we can use:
echo.
echo 1. Render (Free, GitHub integration)
echo 2. Vercel (Free, Serverless)  
echo 3. Railway (via GitHub, no CLI needed)
echo 4. Fly.io (GitHub Actions)
echo.
echo Choose option (1-4):
set /p choice=

if "%choice%"=="1" goto render
if "%choice%"=="2" goto vercel
if "%choice%"=="3" goto railway_github
if "%choice%"=="4" goto flyio
goto end

:render
echo.
echo ===============================================
echo Setting up Render Deployment
echo ===============================================
echo.
echo 1. Go to https://render.com
echo 2. Sign up with GitHub account
echo 3. Click "New +" then "Web Service"
echo 4. Connect repository: joonbary/airiss_enterprise
echo 5. Use these settings:
echo    - Name: airiss-v4
echo    - Environment: Python 3
echo    - Build Command: pip install -r requirements.txt
echo    - Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
echo    - Instance Type: Free
echo.
echo 6. Click "Create Web Service"
echo.
echo ✅ Render will auto-deploy from your GitHub repo!
pause
goto end

:vercel
echo.
echo ===============================================
echo Setting up Vercel Deployment
echo ===============================================
echo.
echo 1. Go to https://vercel.com
echo 2. Sign up with GitHub account
echo 3. Click "New Project"
echo 4. Import: joonbary/airiss_enterprise
echo 5. Framework Preset: Other
echo 6. Build Command: pip install -r requirements.txt
echo 7. Output Directory: . 
echo.
echo Create vercel.json file for FastAPI...
echo.
pause
goto end

:railway_github
echo.
echo ===============================================
echo Setting up Railway via GitHub (No CLI needed)
echo ===============================================
echo.
echo 1. Go to https://railway.app
echo 2. Sign up with GitHub account
echo 3. Click "New Project"
echo 4. Select "Deploy from GitHub repo"
echo 5. Choose: joonbary/airiss_enterprise
echo 6. Railway will auto-detect your Dockerfile
echo.
echo ✅ No Railway CLI installation needed!
pause
goto end

:flyio
echo.
echo ===============================================
echo Setting up Fly.io Deployment
echo ===============================================
echo.
echo 1. Go to https://fly.io
echo 2. Sign up with GitHub account
echo 3. Use GitHub Actions for deployment
echo.
pause
goto end

:end
echo.
echo ===============================================
echo GitHub-based deployment setup completed!
echo ===============================================
