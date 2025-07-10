@echo off
REM Quick Git Push Fix - One Click Solution
REM English Only - No Encoding Issues

echo ============================================================
echo AIRISS Quick Git Push Fix - Automatic Resolution
echo ============================================================
echo.

cd /d "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

echo Attempting automatic fix...
echo.

REM Method 1: Standard pull and push
echo Step 1: Fetching remote updates...
git fetch origin

echo Step 2: Attempting pull with merge...
git pull origin main --no-edit

if %ERRORLEVEL% EQU 0 (
    echo Step 3: Pull successful, now pushing...
    git push origin main
    if %ERRORLEVEL% EQU 0 (
        echo ============================================================
        echo SUCCESS: Git push completed successfully!
        echo ============================================================
        goto END
    )
)

REM Method 2: Rebase approach
echo.
echo Standard method failed. Trying rebase approach...
git pull origin main --rebase

if %ERRORLEVEL% EQU 0 (
    echo Rebase successful, now pushing...
    git push origin main
    if %ERRORLEVEL% EQU 0 (
        echo ============================================================
        echo SUCCESS: Git push completed with rebase!
        echo ============================================================
        goto END
    )
)

REM Method 3: Force with lease (safer force)
echo.
echo Rebase failed. Trying force with lease...
git push origin main --force-with-lease

if %ERRORLEVEL% EQU 0 (
    echo ============================================================
    echo SUCCESS: Git push completed with force-with-lease!
    echo ============================================================
    goto END
)

REM All methods failed
echo ============================================================
echo ERROR: All automatic methods failed.
echo Please run advanced_git_fix.bat for manual resolution.
echo ============================================================

:END
echo.
echo Final repository status:
git status
echo.
echo Recent commits:
git log --oneline -3
echo.
echo Process completed. Press any key to continue...
pause
