@echo off
REM Git Upload Success Verification
REM English Only - No Encoding Issues

echo ============================================================
echo AIRISS Git Upload Success Verification
echo ============================================================
echo.

cd /d "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

echo Checking upload status...
echo.

echo 1. REMOTE REPOSITORY STATUS
echo ----------------------------
git remote show origin
echo.

echo 2. SYNC STATUS CHECK
echo ---------------------
git fetch origin
git status
echo.

echo 3. COMMIT COMPARISON
echo --------------------
echo Local commits:
git log --oneline -3
echo.
echo Remote commits:
git log --oneline origin/main -3
echo.

echo 4. VERIFICATION
echo ---------------
git rev-list --count main ^origin/main > temp_count.txt
set /p LOCAL_AHEAD=<temp_count.txt
del temp_count.txt

git rev-list --count origin/main ^main > temp_count.txt
set /p REMOTE_AHEAD=<temp_count.txt
del temp_count.txt

if %LOCAL_AHEAD%==0 if %REMOTE_AHEAD%==0 (
    echo ============================================================
    echo SUCCESS: Repository is fully synchronized!
    echo ============================================================
    echo Your Neon DB integration changes are uploaded to GitHub.
    echo Repository URL: https://github.com/joonbary/AIRISS_V4.1.git
) else (
    echo ============================================================
    echo WARNING: Repository is not synchronized
    echo ============================================================
    echo Local ahead: %LOCAL_AHEAD% commits
    echo Remote ahead: %REMOTE_AHEAD% commits
    echo.
    echo Action needed: Run git_problem_solver.bat to fix sync issues
)

echo.
echo 5. LATEST GITHUB COMMIT VERIFICATION
echo -------------------------------------
echo Visit: https://github.com/joonbary/AIRISS_V4.1/commits/main
echo Verify that your latest commit appears on GitHub
echo.

echo Verification completed. Press any key to continue...
pause
