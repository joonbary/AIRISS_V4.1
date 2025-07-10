@echo off
echo AIRISS v4.1 Alternative Port Runner
echo ===================================

echo.
echo Finding available alternative ports for AIRISS...

set "available_ports=8003 8004 8005 8006 8007"

for %%p in (%available_ports%) do (
    echo.
    echo Checking port %%p...
    netstat -ano | findstr :%%p > nul
    if errorlevel 1 (
        echo Port %%p is available!
        echo.
        echo Starting AIRISS v4.1 on port %%p...
        echo Access URL: http://localhost:%%p
        echo.
        set PORT=%%p
        python -m app.main
        goto :end
    ) else (
        echo Port %%p is in use
    )
)

echo.
echo All alternative ports are in use.
echo Please run fix_port_conflict_EN.bat or specify a manual port.

:end
pause
