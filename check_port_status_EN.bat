@echo off
echo AIRISS Port Status Checker
echo ==========================

echo.
echo Main port usage status:
echo.

echo Port 8002 (AIRISS default):
netstat -ano | findstr :8002
if errorlevel 1 (
    echo   Status: Available
) else (
    echo   Status: In use
)

echo.
echo Port 8003 (Alternative 1):
netstat -ano | findstr :8003
if errorlevel 1 (
    echo   Status: Available
) else (
    echo   Status: In use
)

echo.
echo Port 8004 (Alternative 2):
netstat -ano | findstr :8004
if errorlevel 1 (
    echo   Status: Available
) else (
    echo   Status: In use
)

echo.
echo Port 8005 (Alternative 3):
netstat -ano | findstr :8005
if errorlevel 1 (
    echo   Status: Available
) else (
    echo   Status: In use
)

echo.
echo Python processes:
tasklist | findstr /i python.exe | findstr /v /i "Windows\System32"

echo.
echo Port resolution options:
echo   1. fix_port_conflict_EN.bat    - Resolve port 8002 conflict
echo   2. run_port_8003_EN.bat        - Run on port 8003
echo   3. run_alternative_port_EN.bat - Auto port selection

echo.
pause
