@echo off
cd /d "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

echo AIRISS v5.0 - New Repository Creation Guide
echo =============================================

echo GitHub keeps detecting API keys in git history (commit: 200407d)
echo The only way to completely solve this is to create a new repository
echo.

echo STEP 1: Create new repository on GitHub
echo ----------------------------------------
echo 1. Go to: https://github.com/new
echo 2. Repository name: AIRISS_V5_Clean
echo 3. Description: AI-powered HR Analysis System v5.0 - Clean version
echo 4. Set to Public
echo 5. Check "Add a README file"
echo 6. Click "Create repository"
echo.

echo STEP 2: Prepare local repository
echo ---------------------------------
echo Current branch: airiss-v5-clean (already created)
echo This branch has clean files without API keys
echo.

echo STEP 3: Change remote to new repository
echo ----------------------------------------
echo After creating the new repository, run these commands:
echo.
echo git remote remove origin
echo git remote add origin https://github.com/joonbary/AIRISS_V5_Clean.git
echo git push origin airiss-v5-clean
echo.

echo STEP 4: Update Railway deployment
echo ---------------------------------
echo 1. Go to: https://railway.app/dashboard
echo 2. Select your AIRISS project
echo 3. Go to Settings ^> Service
echo 4. Update Repository URL to: https://github.com/joonbary/AIRISS_V5_Clean
echo 5. Update Branch to: airiss-v5-clean
echo.

echo STEP 5: Update README and links
echo --------------------------------
echo Update all documentation links to point to new repository
echo.

echo Would you like me to execute STEP 3 now?
echo Make sure you created the new repository first!
echo.
echo Press Y to continue with remote change, N to do it manually
choice /c YN /n

if %ERRORLEVEL% EQU 1 (
    echo.
    echo Changing remote repository...
    git remote remove origin
    git remote add origin https://github.com/joonbary/AIRISS_V5_Clean.git
    
    echo.
    echo Pushing to new repository...
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
        echo Next steps:
        echo 1. Update Railway deployment settings
        echo 2. Update documentation links
        echo 3. Archive old repository if needed
        echo.
        echo Your AIRISS v5.0 is now in a clean repository!
    ) else (
        echo.
        echo Failed to push. Make sure you created the new repository first:
        echo https://github.com/new
    )
) else (
    echo.
    echo Manual setup:
    echo 1. Create new repository at https://github.com/new
    echo 2. Run: git remote remove origin
    echo 3. Run: git remote add origin https://github.com/joonbary/AIRISS_V5_Clean.git
    echo 4. Run: git push origin airiss-v5-clean
)

echo.
pause
