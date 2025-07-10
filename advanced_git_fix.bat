@echo off
REM Advanced Git Fix - Force Push and Branch Management
REM English Only - No Encoding Issues

echo ============================================================
echo AIRISS Advanced Git Fix - Force Resolution
echo ============================================================
echo.

cd /d "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

echo Current situation analysis...
echo.

echo Option 1: Force Push (DESTRUCTIVE - overwrites remote)
echo Option 2: Create New Branch and Merge
echo Option 3: Reset and Clean Push
echo.

set /p choice="Select option (1/2/3): "

if "%choice%"=="1" goto FORCE_PUSH
if "%choice%"=="2" goto NEW_BRANCH
if "%choice%"=="3" goto RESET_CLEAN
goto END

:FORCE_PUSH
echo ============================================================
echo WARNING: This will OVERWRITE remote repository!
echo All remote changes will be LOST!
echo ============================================================
set /p confirm="Type YES to confirm: "
if not "%confirm%"=="YES" goto END

echo Forcing push to remote...
git push origin main --force
if %ERRORLEVEL% EQU 0 (
    echo SUCCESS: Force push completed!
) else (
    echo ERROR: Force push failed. Check permissions.
)
goto END

:NEW_BRANCH
echo ============================================================
echo Creating new branch and merging...
echo ============================================================

echo Creating backup branch...
git branch backup-main

echo Creating new integration branch...
git checkout -b integration-fix

echo Pulling latest remote...
git pull origin main

echo Switching back to main...
git checkout main

echo Merging integration branch...
git merge integration-fix

echo Pushing merged result...
git push origin main

goto END

:RESET_CLEAN
echo ============================================================
echo Clean reset and push...
echo ============================================================

echo Resetting to last commit...
git reset --hard HEAD

echo Cleaning untracked files...
git clean -fd

echo Pulling latest...
git pull origin main

echo Adding all changes...
git add .

echo Committing changes...
git commit -m "Neon DB Integration Complete - Clean Push"

echo Pushing to remote...
git push origin main

goto END

:END
echo.
echo ============================================================
echo Advanced Git Fix Process Completed
echo ============================================================
echo.
echo Checking final status...
git status
echo.
echo Remote sync status...
git log --oneline -3
echo.
pause
