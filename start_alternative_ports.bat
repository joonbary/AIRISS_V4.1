@echo off
echo AIRISS v4.1 Alternative Port Launch
echo ===================================

echo [1] Trying different ports...
call venv_new\Scripts\activate

echo [2] Testing port 8003...
start "AIRISS-8003" python -m uvicorn app.main:app --host 0.0.0.0 --port 8003
timeout /t 2 >nul

echo [3] Testing port 8004...
start "AIRISS-8004" python -m uvicorn app.main:app --host 0.0.0.0 --port 8004  
timeout /t 2 >nul

echo [4] Testing port 8005...
start "AIRISS-8005" python -m uvicorn app.main:app --host 0.0.0.0 --port 8005
timeout /t 2 >nul

echo [5] Opening browsers for testing...
start http://localhost:8003/health
start http://localhost:8004/health  
start http://localhost:8005/health

echo.
echo Try these URLs:
echo - http://localhost:8003/
echo - http://localhost:8004/
echo - http://localhost:8005/
echo.
echo Choose the working port and bookmark it!

pause
