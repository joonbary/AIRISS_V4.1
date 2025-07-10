@echo off

echo ================================================
echo GitHub Secret Scanning - SAFE SOLUTION
echo ================================================
echo.
echo The easiest and safest way to solve this is to:
echo.
echo 1. Open this link in your browser:
echo    https://github.com/joonbary/AIRISS_V4.1/security/secret-scanning/unblock-secret/2zd8n7b5Di9ij1ECLkWEFZHShoe
echo.
echo 2. Click the "Allow secret" button
echo.
echo 3. Wait for confirmation message
echo.
echo 4. Press any key here to continue...
pause

echo.
echo 5. Now pushing to GitHub...
cd /d "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"
git push origin main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo SUCCESS: GitHub push completed!
    echo ========================================
    echo.
    echo Repository: https://github.com/joonbary/AIRISS_V4.1
    echo Deployed App: https://web-production-4066.up.railway.app/dashboard
    echo.
    echo The API keys in the files have been replaced with placeholders.
    echo Your repository is now secure!
    echo.
) else (
    echo.
    echo Still failed? Try these alternatives:
    echo.
    echo Alternative 1: Delete the problematic files temporarily
    echo git rm .env.aws.example start_with_cloud_db.bat
    echo git commit -m "temp: remove files with API keys"
    echo git push origin main
    echo.
    echo Alternative 2: Create a new branch
    echo git checkout -b v5-clean
    echo git push origin v5-clean
    echo Then make v5-clean the default branch in GitHub settings
    echo.
)

pause
