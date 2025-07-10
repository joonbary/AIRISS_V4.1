@echo off
cd /d "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

echo GitHub Secret Scanning Fix Script
echo =================================

echo Step 1: Remove API keys from example files
echo Fixing .env.aws.example file...
(
echo # AIRISS v4.0 + AWS S3 Configuration Example
echo PROJECT_NAME=AIRISS v4.0
echo VERSION=4.0.0
echo DATABASE_URL=sqlite:///./airiss_v4.db
echo.
echo # OpenAI Configuration ^(Optional^)
echo OPENAI_API_KEY=sk-proj-YOUR_OPENAI_API_KEY_HERE
echo.
echo # AWS S3 Configuration ^(Download Optimization^)
echo AWS_ACCESS_KEY_ID=YOUR_AWS_ACCESS_KEY_HERE
echo AWS_SECRET_ACCESS_KEY=YOUR_AWS_SECRET_KEY_HERE
echo AWS_DEFAULT_REGION=ap-northeast-2
echo AWS_S3_BUCKET_NAME=airiss-downloads
echo.
echo # S3 Download Settings
echo S3_DOWNLOAD_ENABLED=true
echo S3_DOWNLOAD_EXPIRY_HOURS=24
echo S3_MAX_FILE_SIZE_MB=50
echo S3_URL_EXPIRY_MINUTES=60
echo.
echo # Railway Deployment Settings
echo PORT=8002
echo SERVER_HOST=0.0.0.0
) > .env.aws.example.fixed

move .env.aws.example.fixed .env.aws.example

echo Step 2: Fix batch file with API key
echo Fixing start_with_cloud_db.bat file...
powershell -Command "(Get-Content 'start_with_cloud_db.bat') -replace 'sk-proj-[A-Za-z0-9_-]+', 'sk-proj-YOUR_OPENAI_API_KEY_HERE' | Set-Content 'start_with_cloud_db.bat'"

echo Step 3: Remove files from git history
git filter-branch --force --index-filter "git rm --cached --ignore-unmatch .env.aws.example start_with_cloud_db.bat" --prune-empty --tag-name-filter cat -- --all

echo Step 4: Clean up git
git for-each-ref --format="delete %(refname)" refs/original | git update-ref --stdin
git reflog expire --expire=now --all
git gc --prune=now

echo Step 5: Stage fixed files
git add .env.aws.example start_with_cloud_db.bat

echo Step 6: Commit fix
git commit -m "security: Remove exposed OpenAI API keys from example files"

echo Step 7: Force push to GitHub
git push origin main --force

echo.
echo Fixed files successfully!
echo All API keys have been replaced with placeholders.
echo.
pause
