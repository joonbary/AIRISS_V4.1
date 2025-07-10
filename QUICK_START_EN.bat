@echo off
title AIRISS v4.1 Quick Start
echo ===============================
echo AIRISS v4.1 Quick Start Helper
echo ===============================
echo.

echo Checking system status...
echo.

REM Quick port check
echo Port 8002 status:
netstat -ano | findstr :8002 > nul
if errorlevel 1 (
    echo Available - Starting AIRISS on default port...
    echo.
    echo Access URL: http://localhost:8002
    echo Press Ctrl+C to stop server
    echo.
    python -m app.main
    goto :end
) else (
    echo In use - Port conflict detected
)

echo.
echo Port 8003 status:
netstat -ano | findstr :8003 > nul
if errorlevel 1 (
    echo Available - Starting AIRISS on port 8003...
    echo.
    echo Access URL: http://localhost:8003
    echo Press Ctrl+C to stop server
    echo.
    set SERVER_PORT=8003
    python -m app.main
    goto :end
) else (
    echo In use
)

echo.
echo Both primary ports are busy.
echo Please use AIRISS_PORT_SOLVER_EN.bat for advanced options.
echo.

:end
pause
