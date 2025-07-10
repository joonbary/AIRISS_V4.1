@echo off
REM Emergency Git Fix - Unrelated Histories Resolution
REM English Only - No Encoding Issues

echo ============================================================
echo AIRISS Emergency Git Fix - Unrelated Histories
echo ============================================================
echo.

cd /d "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

echo Step 1: Cleaning problematic files...
echo Removing elasticbeanstalk logs directory...
rmdir /s /q ".elasticbeanstalk\logs" 2>nul
echo.

echo Step 2: Force cleaning Git workspace...
git reset --hard HEAD
git clean -fd
echo.

echo Step 3: Handling unrelated histories...
echo This will merge repositories with different histories.
echo.

echo Option A: Allow unrelated histories merge
git pull origin main --allow-unrelated-histories --no-edit

if %ERRORLEVEL% EQU 0 (
    echo Merge successful! Now pushing...
    git push origin main
    if %ERRORLEVEL% EQU 0 (
        echo ============================================================
        echo SUCCESS: Repository synchronized with unrelated histories!
        echo ============================================================
        goto END
    )
)

echo.
echo Option A failed. Trying Option B: Force push local version...
echo WARNING: This overwrites remote repository completely!
echo.
set /p confirm="Type YES to overwrite remote repository: "
if not "%confirm%"=="YES" goto OPTION_C

git push origin main --force
if %ERRORLEVEL% EQU 0 (
    echo ============================================================
    echo SUCCESS: Force push completed!
    echo ============================================================
    goto END
)

:OPTION_C
echo.
echo Option C: Create new branch and merge manually...
git branch backup-current
git checkout -b temp-merge
git pull origin main --allow-unrelated-histories --strategy=ours
git checkout main
git merge temp-merge
git push origin main

:END
echo.
echo ============================================================
echo Emergency fix completed. Checking final status...
echo ============================================================
git status
echo.
echo Remote sync check:
git fetch origin
git log --oneline -3
echo.
pause
