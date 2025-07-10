@echo off
echo ===============================================
echo AIRISS v5.0 - Create Clean Orphan Branch
echo ===============================================
echo.
echo This will create a completely new branch without any commit history.
echo This is the most effective way to solve the GitHub secret issue.
echo.
pause

echo Step 1: Create orphan branch (no history)
echo ===============================================
git checkout --orphan v5-clean-final
echo Created orphan branch: v5-clean-final

echo.
echo Step 2: Remove all staged files
echo ===============================================
git rm -rf .
echo All files removed from staging

echo.
echo Step 3: Create clean .gitignore
echo ===============================================
echo # Environment files > .gitignore
echo .env >> .gitignore
echo .env.* >> .gitignore
echo *.env >> .gitignore
echo. >> .gitignore
echo # Temporary files >> .gitignore
echo *.tmp >> .gitignore
echo temp/ >> .gitignore
echo. >> .gitignore
echo # Python cache >> .gitignore
echo __pycache__/ >> .gitignore
echo *.pyc >> .gitignore
echo. >> .gitignore
echo # Node modules >> .gitignore
echo node_modules/ >> .gitignore
echo. >> .gitignore
echo # IDE files >> .gitignore
echo .vscode/ >> .gitignore
echo .idea/ >> .gitignore

echo.
echo Step 4: Copy essential files (excluding sensitive ones)
echo ===============================================
git checkout airiss-v5-clean -- app/
git checkout airiss-v5-clean -- static/
git checkout airiss-v5-clean -- templates/
git checkout airiss-v5-clean -- requirements.txt
git checkout airiss-v5-clean -- README.md
git checkout airiss-v5-clean -- main.py

echo Files copied (excluding sensitive files)

echo.
echo Step 5: Create safe configuration template
echo ===============================================
echo # AIRISS v5.0 Configuration Template > .env.template
echo # Copy this file to .env and fill in your actual values >> .env.template
echo. >> .env.template
echo PROJECT_NAME=AIRISS v5.0 >> .env.template
echo VERSION=5.0.0 >> .env.template
echo DATABASE_URL=sqlite:///./airiss_v5.db >> .env.template
echo. >> .env.template
echo # OpenAI API Key >> .env.template
echo OPENAI_API_KEY=your-openai-api-key-here >> .env.template
echo. >> .env.template
echo # AWS Configuration >> .env.template
echo AWS_ACCESS_KEY_ID=your-aws-access-key >> .env.template
echo AWS_SECRET_ACCESS_KEY=your-aws-secret-key >> .env.template

echo.
echo Step 6: Create setup instructions
echo ===============================================
echo # AIRISS v5.0 Setup Guide > SETUP.md
echo. >> SETUP.md
echo ## Environment Setup >> SETUP.md
echo 1. Copy .env.template to .env >> SETUP.md
echo 2. Update .env with your actual API keys >> SETUP.md
echo 3. Run: pip install -r requirements.txt >> SETUP.md
echo 4. Run: python main.py >> SETUP.md
echo. >> SETUP.md
echo ## API Keys Required >> SETUP.md
echo - OpenAI API Key: Get from https://platform.openai.com/api-keys >> SETUP.md
echo - AWS Keys: Optional for cloud features >> SETUP.md

echo.
echo Step 7: Add and commit clean files
echo ===============================================
git add .
git status

echo.
echo Step 8: Create first clean commit
echo ===============================================
git commit -m "Initial clean commit for AIRISS v5.0

- No sensitive information in history
- Safe configuration templates
- All essential application files
- Proper .gitignore configuration"

echo.
echo Step 9: Push clean branch to GitHub
echo ===============================================
echo Pushing clean branch without any sensitive history...
git push origin v5-clean-final

echo.
echo ===============================================
echo SUCCESS!
echo ===============================================
echo Clean branch 'v5-clean-final' has been created and pushed.
echo This branch has no commit history with sensitive information.
echo.
echo Next steps:
echo 1. Go to GitHub and create a pull request from v5-clean-final
echo 2. Or set v5-clean-final as your main branch
echo 3. Delete the old branches if needed
echo.
pause
