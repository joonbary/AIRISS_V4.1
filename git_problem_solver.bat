@echo off
REM Git Problem Solver - Main Menu
REM English Only - No Encoding Issues

:MENU
cls
echo ============================================================
echo AIRISS Git Problem Solver - Main Menu
echo ============================================================
echo.
echo Current Error: "stale info" - Git push failed
echo.
echo Available Solutions:
echo.
echo 1. Quick Fix (Automatic - Recommended)
echo 2. Diagnosis Tool (Check what's wrong first)
echo 3. Standard Fix (Step by step with confirmations)
echo 4. Advanced Fix (Manual control with multiple options)
echo 5. Exit
echo.

set /p choice="Select option (1-5): "

if "%choice%"=="1" (
    echo.
    echo Running Quick Fix...
    call quick_git_fix.bat
    goto MENU
)

if "%choice%"=="2" (
    echo.
    echo Running Diagnosis...
    call git_diagnosis.bat
    goto MENU
)

if "%choice%"=="3" (
    echo.
    echo Running Standard Fix...
    call fix_git_push_error.bat
    goto MENU
)

if "%choice%"=="4" (
    echo.
    echo Running Advanced Fix...
    call advanced_git_fix.bat
    goto MENU
)

if "%choice%"=="5" (
    echo.
    echo Exiting Git Problem Solver...
    goto END
)

echo.
echo Invalid choice. Please select 1-5.
pause
goto MENU

:END
echo.
echo Git Problem Solver completed.
echo.
pause
