@echo off
cd /d "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

echo AIRISS v5.0 - Remove Problem Files Method
echo ==========================================

echo This method removes the problematic files entirely
echo and recreates them without API keys
echo.

echo Step 1: Remove problematic files from git
git rm .env.aws.example
git rm start_with_cloud_db.bat

echo Step 2: Commit the removal
git commit -m "security: Remove files with exposed API keys"

echo Step 3: Push the removal
git push origin main

if %ERRORLEVEL% NEQ 0 (
    echo Push failed again. The files are still in history.
    echo Using force push to overwrite history...
    git push origin main --force
)

echo Step 4: Create new clean files
echo # AIRISS v4.0 Configuration Example > .env.aws.example.new
echo PROJECT_NAME=AIRISS v4.0 >> .env.aws.example.new
echo VERSION=4.0.0 >> .env.aws.example.new
echo DATABASE_URL=sqlite:///./airiss_v4.db >> .env.aws.example.new
echo. >> .env.aws.example.new
echo # OpenAI Configuration >> .env.aws.example.new
echo OPENAI_API_KEY=your-openai-api-key-here >> .env.aws.example.new

echo @echo off > start_with_cloud_db.bat.new
echo echo AIRISS v4.1 Cloud DB Setup >> start_with_cloud_db.bat.new
echo echo Please set your OPENAI_API_KEY in .env file >> start_with_cloud_db.bat.new
echo pause >> start_with_cloud_db.bat.new

echo Step 5: Rename new files
move .env.aws.example.new .env.aws.example
move start_with_cloud_db.bat.new start_with_cloud_db.bat

echo Step 6: Add clean files back
git add .env.aws.example start_with_cloud_db.bat

echo Step 7: Commit clean files
git commit -m "feat: Add clean example files without API keys"

echo Step 8: Push clean version
git push origin main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo SUCCESS: Clean files pushed successfully!
    echo Repository: https://github.com/joonbary/AIRISS_V4.1
    echo App: https://web-production-4066.up.railway.app/dashboard
) else (
    echo.
    echo Still failed. Try the clean branch method:
    echo Run: create_clean_repository.bat
)

echo.
pause
