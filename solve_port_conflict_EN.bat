@echo off
echo AIRISS v4.1 Complete Port Conflict Solution
echo ===========================================

echo.
echo Step 1: Current running AIRISS processes
echo.
tasklist | findstr /i python
echo.

echo Step 2: Detailed port 8002 usage check
echo.
for /f "tokens=1,2,3,4,5" %%a in ('netstat -ano ^| findstr :8002') do (
    echo Protocol: %%a, Local: %%b, Foreign: %%c, State: %%d, PID: %%e
    for /f "tokens=1" %%p in ('tasklist /fi "pid eq %%e" /fo csv /nh') do (
        echo   Process: %%p
    )
)

echo.
echo Step 3: Force release port 8002
echo.
set /p CONFIRM="Kill processes using port 8002? (Y/N): "
if /i "%CONFIRM%"=="Y" (
    echo Killing port 8002 processes...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8002') do (
        echo Killing process ID %%a...
        taskkill /PID %%a /F 2>nul
        if errorlevel 1 (
            echo   Failed to kill PID %%a
        ) else (
            echo   Successfully killed PID %%a
        )
    )
) else (
    echo Skipping process termination.
)

echo.
echo Step 4: Verify port release
timeout /t 3 /nobreak > nul
echo Port 8002 status recheck:
netstat -ano | findstr :8002
if errorlevel 1 (
    echo Port 8002 is now free!
) else (
    echo Port 8002 is still in use.
)

echo.
echo Step 5: Restart AIRISS server
echo.
set /p RESTART="Start AIRISS now? (Y/N): "
if /i "%RESTART%"=="Y" (
    echo.
    echo Starting AIRISS v4.1...
    echo Access URL: http://localhost:8002
    echo.
    python -m app.main
) else (
    echo.
    echo Manual execution:
    echo    python -m app.main
    echo.
    echo Alternative port execution:
    echo    run_port_8003_EN.bat
)

echo.
echo Port conflict resolution process complete!
pause
