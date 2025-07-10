@echo off
echo Creating clean branch without commit history...

echo Step 1: Create orphan branch
git checkout --orphan clean-v5

echo Step 2: Remove all staged files
git rm -rf .

echo Step 3: Create .gitignore
echo .env > .gitignore
echo .env.* >> .gitignore
echo *.env >> .gitignore
echo __pycache__/ >> .gitignore
echo *.pyc >> .gitignore

echo Step 4: Copy essential files only
git checkout HEAD~1 -- app/
git checkout HEAD~1 -- static/
git checkout HEAD~1 -- templates/
git checkout HEAD~1 -- requirements.txt
git checkout HEAD~1 -- README.md

echo Step 5: Create safe template
echo PROJECT_NAME=AIRISS v5.0 > .env.template
echo VERSION=5.0.0 >> .env.template
echo DATABASE_URL=sqlite:///./airiss_v5.db >> .env.template
echo OPENAI_API_KEY=your-openai-api-key-here >> .env.template
echo AWS_ACCESS_KEY_ID=your-aws-access-key >> .env.template
echo AWS_SECRET_ACCESS_KEY=your-aws-secret-key >> .env.template

echo Step 6: Commit clean version
git add .
git commit -m "Clean AIRISS v5.0 - no sensitive data in history"

echo Step 7: Push clean branch
git push origin clean-v5

echo DONE! Clean branch created: clean-v5
pause
