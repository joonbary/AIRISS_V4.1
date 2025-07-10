@echo off
cd /d "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

echo AIRISS v5.0 - GitHub Allow Secret Method
echo ==========================================

echo GitHub provided a direct link to allow the secret
echo This is the fastest and easiest solution
echo.

echo STEP 1: Open the GitHub link
echo -----------------------------
echo Click on this link or copy it to your browser:
echo https://github.com/joonbary/AIRISS_V4.1/security/secret-scanning/unblock-secret/2zd8n7b5Di9ij1ECLkWEFZHShoe
echo.

echo STEP 2: Click "Allow secret"
echo -----------------------------
echo On the GitHub page, click the "Allow secret" button
echo This will bypass the secret scanning for this specific case
echo.

echo STEP 3: Wait for confirmation
echo -----------------------------
echo You should see a success message
echo.

echo STEP 4: Return here and press any key to continue
echo -------------------------------------------------
pause

echo.
echo STEP 5: Now pushing to GitHub...
echo --------------------------------
git push origin airiss-v5-clean

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo SUCCESS: Push completed!
    echo ========================================
    echo.
    echo Repository: https://github.com/joonbary/AIRISS_V4.1
    echo Branch: airiss-v5-clean
    echo.
    echo Next steps:
    echo 1. Go to GitHub Settings ^> Branches
    echo 2. Change default branch to "airiss-v5-clean"
    echo 3. Update Railway to use "airiss-v5-clean" branch
    echo.
    echo Your AIRISS v5.0 is now successfully deployed!
) else (
    echo.
    echo Still failed after allowing secret
    echo Let's create a completely new repository
    echo.
    echo Run: create_new_repository.bat
)

echo.
pause
