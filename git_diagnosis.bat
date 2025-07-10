@echo off
REM Git Status Diagnosis Tool
REM English Only - No Encoding Issues

echo ============================================================
echo AIRISS Git Status Diagnosis
echo ============================================================
echo.

cd /d "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

echo 1. CURRENT REPOSITORY STATUS
echo ------------------------------
git status
echo.

echo 2. REMOTE REPOSITORY INFORMATION
echo ---------------------------------
git remote -v
echo.

echo 3. BRANCH INFORMATION
echo ---------------------
git branch -a
echo.

echo 4. RECENT LOCAL COMMITS
echo -----------------------
git log --oneline -5
echo.

echo 5. RECENT REMOTE COMMITS
echo ------------------------
git fetch origin 2>nul
git log --oneline origin/main -5
echo.

echo 6. DIFFERENCES BETWEEN LOCAL AND REMOTE
echo ----------------------------------------
git rev-list --left-right --count main...origin/main
echo.

echo 7. UNCOMMITTED CHANGES
echo -----------------------
git diff --name-only
echo.

echo 8. STAGED CHANGES
echo -----------------
git diff --cached --name-only
echo.

echo 9. UNTRACKED FILES
echo ------------------
git ls-files --others --exclude-standard
echo.

echo 10. GIT CONFIGURATION
echo ---------------------
git config --list | findstr user
echo.

echo ============================================================
echo DIAGNOSIS COMPLETE
echo ============================================================
echo.
echo RECOMMENDED SOLUTIONS:
echo.
echo A. If you see conflicts: Run fix_git_push_error.bat
echo B. For quick automatic fix: Run quick_git_fix.bat  
echo C. For advanced manual control: Run advanced_git_fix.bat
echo.
echo Choose the appropriate solution based on the diagnosis above.
echo.
pause
