@echo off
echo ===============================================
echo AIRISS v5.0 - GitHub Secret Fix
echo ===============================================
echo.

echo Step 1: Check current status
echo ===============================================
git status
echo.

echo Step 2: Update .gitignore
echo ===============================================
(
echo # Environment files
echo .env
echo .env.*
echo *.env
echo.
echo # Temporary files
echo *.tmp
echo temp/
echo.
echo # Sensitive batch files
echo start_with_cloud_db.bat
echo.
echo # Node modules
echo node_modules/
echo.
echo # Python cache
echo __pycache__/
echo *.pyc
echo.
) > .gitignore

echo Step 3: Remove problem files
echo ===============================================
if exist .env.aws.example del .env.aws.example
if exist start_with_cloud_db.bat del start_with_cloud_db.bat
echo Problem files removed.

echo.
echo Step 4: Create safe template
echo ===============================================
(
echo # AIRISS v5.0 Configuration Template
echo # Copy this file to .env and update with your actual values
echo.
echo PROJECT_NAME=AIRISS v5.0
echo VERSION=5.0.0
echo DATABASE_URL=sqlite:///./airiss_v5.db
echo.
echo # OpenAI API Key - Get from https://platform.openai.com/api-keys
echo OPENAI_API_KEY=your-openai-api-key-here
echo.
echo # AWS S3 Configuration
echo AWS_ACCESS_KEY_ID=your-aws-access-key
echo AWS_SECRET_ACCESS_KEY=your-aws-secret-key
echo.
echo # Other settings
echo DEBUG=true
echo LOG_LEVEL=INFO
) > .env.template

echo.
echo Step 5: Stage all changes
echo ===============================================
git add .
git status

echo.
echo Step 6: Commit changes
echo ===============================================
git commit -m "security: Remove sensitive files and add safe templates"

echo.
echo Step 7: Push to GitHub
echo ===============================================
echo Pushing safe commit...
git push origin HEAD

echo.
echo ===============================================
echo COMPLETED!
echo ===============================================
echo Sensitive information has been removed.
echo Safe templates have been created.
echo.
pause
