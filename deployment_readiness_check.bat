@echo off
echo ===============================================
echo AIRISS Deployment Readiness Check
echo ===============================================

echo Checking essential files for deployment...

echo.
echo [1] Main application file...
if exist "app\main.py" (
    echo ✅ app\main.py exists
) else (
    echo ❌ app\main.py missing
)

echo.
echo [2] Requirements file...
if exist "requirements.txt" (
    echo ✅ requirements.txt exists
    echo Contents:
    type requirements.txt
) else (
    echo ❌ requirements.txt missing
)

echo.
echo [3] Dockerfile...
if exist "Dockerfile" (
    echo ✅ Dockerfile exists
) else (
    echo ❌ Dockerfile missing
)

echo.
echo [4] Railway config...
if exist "railway.json" (
    echo ✅ railway.json exists
) else (
    echo ❌ railway.json missing
)

echo.
echo [5] Render config...
if exist "render.yaml" (
    echo ✅ render.yaml exists
) else (
    echo ℹ️ render.yaml not found (optional)
)

echo.
echo [6] Testing app startup...
python -c "
import sys
sys.path.append('.')
try:
    from app.main import app
    print('✅ App loads successfully')
    print(f'   Title: {app.title}')
    print(f'   Version: {app.version}')
except Exception as e:
    print('❌ App load failed:', str(e))
"

echo.
echo ===============================================
echo Deployment readiness check completed!
echo ===============================================

echo.
echo All checks passed? Ready to deploy! Choose platform:
echo 1. Render (Recommended)
echo 2. Railway 
echo 3. Vercel
echo.
set /p platform=Choose (1-3): 

if "%platform%"=="1" (
    echo.
    echo 🏆 Render Deployment:
    echo 1. Go to https://render.com
    echo 2. Sign up with GitHub
    echo 3. New Web Service
    echo 4. Connect: joonbary/AIRISS_V4.1
    echo 5. Settings: pip install -r requirements.txt
    echo 6. Start: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    echo 7. Deploy!
)

if "%platform%"=="2" (
    echo.
    echo 🚀 Railway Deployment:
    echo 1. Go to https://railway.app
    echo 2. Login with GitHub
    echo 3. New Project from GitHub
    echo 4. Select: joonbary/AIRISS_V4.1
    echo 5. Auto-deploy!
)

if "%platform%"=="3" (
    echo.
    echo ⚡ Vercel Deployment:
    echo 1. Go to https://vercel.com
    echo 2. Import project
    echo 3. Select: joonbary/AIRISS_V4.1
    echo 4. Configure for FastAPI
    echo 5. Deploy!
)

pause
