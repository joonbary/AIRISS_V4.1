@echo off
cd /d "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

echo AIRISS v5.0 - Connect to New Repository
echo ==========================================

echo Step 1: Remove old remote
git remote remove origin

echo Step 2: Add new remote (UPDATE THIS URL!)
echo IMPORTANT: Update the URL below with your actual GitHub username!
echo.
echo Current command uses 'joonbary' - change it to your username if different
echo.
git remote add origin https://github.com/joonbary/AIRISS_V5_Clean.git

echo Step 3: Push to new repository
git push origin airiss-v5-clean

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo SUCCESS: New repository created!
    echo ========================================
    echo.
    echo New Repository: https://github.com/joonbary/AIRISS_V5_Clean
    echo Branch: airiss-v5-clean
    echo.
    echo NEXT STEPS:
    echo 1. Go to GitHub Settings and set airiss-v5-clean as default branch
    echo 2. Update Railway deployment to use new repository
    echo 3. Update any documentation links
    echo.
    echo Your AIRISS v5.0 is now in a clean repository without API key history!
) else (
    echo.
    echo Push failed. Possible reasons:
    echo 1. Repository not created yet - go to https://github.com/new
    echo 2. Wrong repository URL - check your GitHub username
    echo 3. Authentication issues - check GitHub login
    echo.
    echo Manual commands:
    echo git remote remove origin
    echo git remote add origin https://github.com/YOUR-USERNAME/AIRISS_V5_Clean.git
    echo git push origin airiss-v5-clean
)

echo.
pause
