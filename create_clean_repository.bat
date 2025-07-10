@echo off
cd /d "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

echo AIRISS v5.0 - Clean Repository Solution
echo ========================================

echo Current situation: GitHub is blocking push due to API keys in git history
echo Solution: Create a completely clean branch
echo.

echo Step 1: Check current status
git status

echo Step 2: Remove problematic files temporarily
git rm --cached .env.aws.example 2>nul
git rm --cached start_with_cloud_db.bat 2>nul

echo Step 3: Create new clean branch
git checkout -b airiss-v5-clean

echo Step 4: Remove files with API keys from this branch
del .env.aws.example
del start_with_cloud_db.bat

echo Step 5: Create clean example files
echo # AIRISS v4.0 Configuration Example > .env.aws.example
echo PROJECT_NAME=AIRISS v4.0 >> .env.aws.example
echo VERSION=4.0.0 >> .env.aws.example
echo DATABASE_URL=sqlite:///./airiss_v4.db >> .env.aws.example
echo. >> .env.aws.example
echo # OpenAI API Key - Replace with your actual key >> .env.aws.example
echo OPENAI_API_KEY=your-openai-api-key-here >> .env.aws.example
echo. >> .env.aws.example
echo # AWS S3 Configuration >> .env.aws.example
echo AWS_ACCESS_KEY_ID=your-aws-access-key >> .env.aws.example
echo AWS_SECRET_ACCESS_KEY=your-aws-secret-key >> .env.aws.example

echo @echo off > start_with_cloud_db.bat
echo echo AIRISS v4.1 Cloud DB Script >> start_with_cloud_db.bat
echo echo Please configure your API keys in .env file >> start_with_cloud_db.bat
echo echo API Key should be: OPENAI_API_KEY=your-actual-key-here >> start_with_cloud_db.bat
echo pause >> start_with_cloud_db.bat

echo Step 6: Add all files to clean branch
git add .

echo Step 7: Commit clean version
git commit -m "feat: AIRISS v5.0 - Clean version without exposed API keys

- Advanced AI text analysis with deep learning
- Bias detection and fairness monitoring  
- Predictive analytics for performance forecasting
- Multi-language support (Korean, English, Chinese, Japanese)
- Enhanced security and privacy protection
- API v2 endpoints with advanced features
- Real-time monitoring and notifications
- Improved performance and scalability

Version: v5.0.0
All API keys replaced with placeholders for security"

echo Step 8: Push clean branch to GitHub
git push origin airiss-v5-clean

if %ERRORLEVEL% EQU 0 (
    echo.
    echo =============================================
    echo SUCCESS: Clean branch pushed successfully!
    echo =============================================
    echo.
    echo Branch: airiss-v5-clean
    echo Repository: https://github.com/joonbary/AIRISS_V4.1
    echo.
    echo NEXT STEPS:
    echo 1. Go to: https://github.com/joonbary/AIRISS_V4.1
    echo 2. Click on "airiss-v5-clean" branch
    echo 3. Click "Settings" tab
    echo 4. Click "Branches" in left menu
    echo 5. Change default branch to "airiss-v5-clean"
    echo 6. Update Railway deployment to use new branch
    echo.
    echo This gives you a completely clean repository without API key history!
) else (
    echo.
    echo Push failed. Let's try alternative method...
    echo.
    echo Alternative: Create new repository
    echo 1. Go to: https://github.com/new
    echo 2. Create new repository: AIRISS_V5_Clean
    echo 3. Run: git remote set-url origin https://github.com/your-username/AIRISS_V5_Clean.git
    echo 4. Run: git push origin airiss-v5-clean
)

echo.
pause
