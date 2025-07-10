@echo off
echo ============================================================
echo AIRISS Git Conflict Resolution - Safe Upload
echo ============================================================
echo.

cd /d "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

echo Current Git status:
git status --short
echo.

echo ============================================================
echo Choose resolution method:
echo ============================================================
echo.
echo 1. SAFE: Pull and merge (recommended)
echo 2. FORCE: Overwrite remote (use with caution) 
echo 3. BRANCH: Create new branch
echo 4. CHECK: View differences first
echo 0. Cancel
echo.

set /p choice="Select option (1-4, 0=cancel): "

if "%choice%"=="1" goto safe_merge
if "%choice%"=="2" goto force_push  
if "%choice%"=="3" goto new_branch
if "%choice%"=="4" goto check_diff
if "%choice%"=="0" goto cancel

echo Invalid choice.
pause
exit /b

:safe_merge
echo.
echo ============================================================
echo SAFE METHOD: Pull and merge
echo ============================================================
echo.

echo Step 1: Fetching latest changes...
git fetch origin

echo Step 2: Pulling with merge strategy...
git pull origin main --no-rebase

echo Step 3: Checking for conflicts...
git status

echo Step 4: Pushing merged changes...
git push origin main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo SUCCESS: Changes merged and uploaded!
    echo Check: https://github.com/joonbary/AIRISS_V4.1
) else (
    echo.
    echo Manual conflict resolution may be needed.
    echo Please check git status for conflicts.
)
goto end

:force_push
echo.
echo ============================================================
echo FORCE METHOD: Overwrite remote (CAUTION!)
echo ============================================================
echo.

echo WARNING: This will overwrite all remote changes!
set /p confirm="Are you sure? (yes/no): "

if /i "%confirm%"=="yes" (
    echo Force pushing...
    git push origin main --force
    
    if %ERRORLEVEL% EQU 0 (
        echo SUCCESS: Force push completed!
        echo Check: https://github.com/joonbary/AIRISS_V4.1
    ) else (
        echo FAILED: Force push failed.
    )
) else (
    echo Cancelled.
)
goto end

:new_branch
echo.
echo ============================================================
echo BRANCH METHOD: Create new branch
echo ============================================================
echo.

echo Creating new branch: neon-integration-%date:~10,4%%date:~4,2%%date:~7,2%
git checkout -b neon-integration-%date:~10,4%%date:~4,2%%date:~7,2%

echo Pushing to new branch...
git push origin HEAD

if %ERRORLEVEL% EQU 0 (
    echo SUCCESS: New branch created and pushed!
    echo Create PR: https://github.com/joonbary/AIRISS_V4.1/compare
) else (
    echo FAILED: Branch push failed.
)
goto end

:check_diff
echo.
echo ============================================================
echo CHECKING DIFFERENCES
echo ============================================================
echo.

echo Fetching latest...
git fetch origin

echo Local commits not in remote:
git log origin/main..HEAD --oneline

echo.
echo Remote commits not in local:
git log HEAD..origin/main --oneline

echo.
echo Files that differ:
git diff --name-only origin/main

echo.
echo Review complete. Run script again to choose resolution.
goto end

:cancel
echo Operation cancelled.

:end
echo.
echo ============================================================
pause
