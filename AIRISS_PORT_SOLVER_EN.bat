@echo off
title AIRISS v4.1 - Port Conflict Solver
color 0A

echo.
echo ==========================================
echo      AIRISS v4.1 Port Conflict Solver     
echo                                          
echo  Automatically resolves port conflicts    
echo ==========================================
echo.

echo Diagnosing current situation...
echo.

REM Check port 8002 status
netstat -ano | findstr :8002 > nul
if errorlevel 1 (
    echo Port 8002: Available
    goto :run_default
) else (
    echo Port 8002: In use
)

echo.
echo Please choose a solution:
echo.
echo 1. Fix port 8002 conflict and run
echo 2. Run on port 8003
echo 3. Auto port selection (Python tool)
echo 4. Check port status only
echo 5. Exit
echo.

set /p CHOICE="Choice (1-5): "

if "%CHOICE%"=="1" goto :fix_port_8002
if "%CHOICE%"=="2" goto :use_port_8003
if "%CHOICE%"=="3" goto :use_python_tool
if "%CHOICE%"=="4" goto :check_status_only
if "%CHOICE%"=="5" goto :end
goto :invalid_choice

:fix_port_8002
echo.
echo Resolving port 8002 conflict...
call fix_port_conflict_EN.bat
goto :end

:use_port_8003
echo.
echo Running on port 8003...
call run_port_8003_EN.bat
goto :end

:use_python_tool
echo.
echo Running Python port management tool...
python port_manager_EN.py
goto :end

:check_status_only
echo.
echo Checking port status...
call check_port_status_EN.bat
goto :end

:run_default
echo.
echo Port 8002 is available!
echo.
set /p RUN_NOW="Start AIRISS now? (Y/n): "
if /i "%RUN_NOW%"=="n" goto :end

echo.
echo Starting AIRISS v4.1...
echo Access URL: http://localhost:8002
echo.
python -m app.main
goto :end

:invalid_choice
echo.
echo Invalid choice. Please select 1-5.
timeout /t 2 /nobreak > nul
goto :menu

:end
echo.
echo Additional help:
echo    - If problems persist, try restarting your system
echo    - Firewall or antivirus might block ports
echo    - Run as administrator for more privileges
echo.
pause
