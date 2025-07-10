@echo off
echo AIRISS v4.1 Port 8003 Runner
echo =============================

echo.
echo Current port usage status:
echo Default port 8002:
netstat -ano | findstr :8002

echo.
echo Alternative port 8003:
netstat -ano | findstr :8003

echo.
echo Starting AIRISS v4.1 on port 8003...
echo Access URL: http://localhost:8003
echo.

set SERVER_PORT=8003
python -m app.main

echo.
echo AIRISS execution complete!
pause
