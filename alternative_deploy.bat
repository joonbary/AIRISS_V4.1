@echo off
echo ===============================================
echo AIRISS Alternative Platform Deploy
echo ===============================================

echo Choose deployment platform:
echo 1. Render (Free tier available)
echo 2. Fly.io (Similar to Railway)  
echo 3. Vercel (Serverless)
echo 4. Back to Railway troubleshooting

set /p choice=Enter choice (1-4): 

if "%choice%"=="1" goto render
if "%choice%"=="2" goto flyio
if "%choice%"=="3" goto vercel
if "%choice%"=="4" goto railway
goto end

:render
echo.
echo Setting up Render deployment...
echo 1. Go to https://render.com
echo 2. Connect your GitHub repository
echo 3. Create new Web Service
echo 4. Use these settings:
echo    - Build Command: pip install -r requirements.txt
echo    - Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
echo    - Environment: Python 3.9
echo.
pause
goto end

:flyio
echo.
echo Setting up Fly.io deployment...
echo 1. Install flyctl: https://fly.io/docs/getting-started/installing-flyctl/
echo 2. Run: fly auth login
echo 3. Run: fly launch
echo 4. Follow the prompts
echo.
pause
goto end

:vercel
echo.
echo Setting up Vercel deployment...
echo 1. Install Vercel CLI: npm i -g vercel
echo 2. Run: vercel login
echo 3. Run: vercel --prod
echo 4. Configure for FastAPI
echo.
pause
goto end

:railway
echo.
echo Back to Railway troubleshooting...
echo Run: railway_diagnosis.py
echo.
pause
goto end

:end
echo ===============================================
echo Alternative deployment setup completed.
echo ===============================================
