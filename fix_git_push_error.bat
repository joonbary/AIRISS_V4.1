@echo off
REM Git Push Fix - Stale Info Error Resolution
REM English Only - No Encoding Issues

echo ============================================================
echo AIRISS Git Push Error Fix - Stale Info Resolution
echo ============================================================
echo.

cd /d "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

echo Step 1: Checking current Git status...
git status
echo.

echo Step 2: Fetching latest remote information...
git fetch origin
echo.

echo Step 3: Checking remote vs local differences...
git log --oneline -5
echo.
git log --oneline origin/main -5
echo.

echo Step 4: Pulling latest changes from remote...
echo WARNING: This may create merge conflicts that need resolution
pause
git pull origin main
echo.

echo Step 5: Checking if merge conflicts exist...
git status
echo.

echo If you see merge conflicts above, resolve them manually then run:
echo   git add .
echo   git commit -m "Resolve merge conflicts"
echo.
echo Otherwise, continue to push...
pause

echo Step 6: Pushing to GitHub...
git push origin main
echo.

if %ERRORLEVEL% EQU 0 (
    echo ============================================================
    echo SUCCESS: Git push completed successfully!
    echo ============================================================
) else (
    echo ============================================================
    echo ERROR: Push still failed. Running advanced fix...
    echo ============================================================
    call advanced_git_fix.bat
)

echo.
echo Process completed. Press any key to continue...
pause
