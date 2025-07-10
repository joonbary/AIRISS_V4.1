@echo off
cd /d "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

echo GitHub Secret Fix - Simple Version
echo =================================

echo Step 1: Add fixed files to git
git add .env.aws.example
git add start_with_cloud_db.bat

echo Step 2: Commit the fix
git commit -m "security: Replace actual API keys with placeholders"

echo Step 3: Push to GitHub
git push origin main

echo.
if %ERRORLEVEL% EQU 0 (
    echo SUCCESS: API keys have been replaced with placeholders
    echo GitHub push completed successfully!
) else (
    echo FAILED: Push still blocked
    echo Try the manual method below
)

echo.
echo Manual method if automatic fix fails:
echo 1. Go to: https://github.com/joonbary/AIRISS_V4.1/security/secret-scanning/unblock-secret/2zd8n7b5Di9ij1ECLkWEFZHShoe
echo 2. Click "Allow secret" to bypass the protection
echo 3. Then run: git push origin main
echo.

pause
