@echo off
echo AIRISS Railway Deployment - Simple Version
echo ==========================================

echo Checking files...
if exist "Dockerfile" echo [OK] Dockerfile
if exist "railway.json" echo [OK] railway.json  
if exist "requirements.txt" echo [OK] requirements.txt
if exist "app\main.py" echo [OK] main.py

echo.
echo Testing app...
python -c "from app.main import app; print('App OK')"

echo.
echo Repository: https://github.com/joonbary/AIRISS_V4.1
echo.
echo Railway Steps:
echo 1. Go to https://railway.app
echo 2. Login with GitHub
echo 3. New Project
echo 4. Deploy from GitHub repo
echo 5. Select: joonbary/AIRISS_V4.1
echo 6. Deploy

echo.
echo Open Railway? (Y/N)
set /p open=
if /i "%open%"=="Y" start https://railway.app

pause
