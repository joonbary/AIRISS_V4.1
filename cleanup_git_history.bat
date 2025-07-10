@echo off
cd /d "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

echo GitHub Secret History Cleanup
echo ==============================

echo WARNING: This will rewrite Git history!
echo Make sure you have a backup before proceeding.
echo.
echo Press Y to continue or N to cancel
choice /c YN /n
if %ERRORLEVEL% EQU 2 goto :end

echo.
echo Step 1: Install BFG Repo Cleaner (if not installed)
echo You can download it from: https://rtyley.github.io/bfg-repo-cleaner/
echo.
echo For now, we'll use git filter-branch (built-in method)
echo.

echo Step 2: Create backup branch
git branch backup-before-cleanup

echo Step 3: Remove API keys from all commits
echo This may take a few minutes...
git filter-branch --force --index-filter "git rm --cached --ignore-unmatch .env.aws.example start_with_cloud_db.bat" --prune-empty --tag-name-filter cat -- --all

echo Step 4: Clean up Git references
git for-each-ref --format="delete %%(refname)" refs/original | git update-ref --stdin
git reflog expire --expire=now --all
git gc --prune=now

echo Step 5: Re-add the cleaned files
git add .env.aws.example start_with_cloud_db.bat .gitignore
git commit -m "security: Add example files with placeholder API keys"

echo Step 6: Force push to GitHub
echo This will overwrite the remote repository!
git push origin main --force

if %ERRORLEVEL% EQU 0 (
    echo SUCCESS: Git history cleaned and pushed!
    echo The API keys have been completely removed from history.
) else (
    echo FAILED: Force push failed
    echo Try the manual method below
)

echo.
echo If this fails, restore from backup:
echo git checkout backup-before-cleanup
echo git branch -D main
echo git checkout -b main
echo.

:end
pause
