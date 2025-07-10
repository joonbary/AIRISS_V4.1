@echo off
echo AIRISS v4.1 Port Conflict Resolver
echo ====================================

echo.
echo Step 1: Check current processes using port 8002
netstat -ano | findstr :8002
echo.

echo Step 2: Check Python processes
tasklist | findstr python.exe
echo.

echo Step 3: Kill processes using port 8002
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8002') do (
    echo Killing process ID %%a...
    taskkill /PID %%a /F 2>nul
)

echo.
echo Step 4: Wait and verify port is free
timeout /t 3 /nobreak > nul
netstat -ano | findstr :8002

echo.
echo Step 5: Start AIRISS server
echo Run: python -m app.main

echo.
echo Port conflict resolution complete!
pause
