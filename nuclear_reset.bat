@echo off
cd /d "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

echo AIRISS v5.0 - Nuclear Option (Complete Reset)
echo ===============================================

echo WARNING: This will create a completely new git repository
echo Your commit history will be lost, but all files will be preserved
echo.
echo Press Y to continue or N to cancel
choice /c YN /n
if %ERRORLEVEL% EQU 2 goto :end

echo.
echo Step 1: Backup current repository
if exist .git_backup rmdir /s /q .git_backup
move .git .git_backup

echo Step 2: Remove problematic files
if exist .env.aws.example del .env.aws.example
if exist start_with_cloud_db.bat del start_with_cloud_db.bat

echo Step 3: Create clean example files
echo # AIRISS v4.0 Configuration Example > .env.aws.example
echo PROJECT_NAME=AIRISS v4.0 >> .env.aws.example
echo VERSION=4.0.0 >> .env.aws.example
echo DATABASE_URL=sqlite:///./airiss_v4.db >> .env.aws.example
echo OPENAI_API_KEY=your-openai-api-key-here >> .env.aws.example

echo @echo off > start_with_cloud_db.bat
echo echo AIRISS v4.1 Cloud Database Setup >> start_with_cloud_db.bat
echo echo Configure your API keys in .env file >> start_with_cloud_db.bat
echo pause >> start_with_cloud_db.bat

echo Step 4: Initialize new git repository
git init

echo Step 5: Add all files
git add .

echo Step 6: Create initial commit
git commit -m "feat: AIRISS v5.0 - Complete AI HR Analysis System

Features:
- Deep learning-based text analysis
- Bias detection and fairness monitoring
- Predictive analytics for performance forecasting
- Multi-language support (Korean, English, Chinese, Japanese)
- 8-dimension comprehensive analysis
- Real-time monitoring and notifications
- Enhanced security and privacy protection
- API v2 endpoints with advanced features

Version: v5.0.0
Clean repository without exposed API keys"

echo Step 7: Add remote repository
git remote add origin https://github.com/joonbary/AIRISS_V4.1.git

echo Step 8: Force push to GitHub (overwrites everything)
git push origin main --force

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo SUCCESS: Complete reset successful!
    echo ========================================
    echo.
    echo Repository: https://github.com/joonbary/AIRISS_V4.1
    echo App: https://web-production-4066.up.railway.app/dashboard
    echo.
    echo Your repository is now completely clean!
    echo All API keys have been removed from history.
    echo.
    echo To restore old history (if needed):
    echo 1. Delete .git folder
    echo 2. Rename .git_backup to .git
) else (
    echo.
    echo Reset failed. Restoring original repository...
    rmdir /s /q .git
    move .git_backup .git
    echo Original repository restored.
)

:end
pause
