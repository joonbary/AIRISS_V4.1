@echo off
chcp 65001 >nul 2>&1
cd /d "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

echo ================================
echo AIRISS GitHub Upload Auto-Fix
echo ================================
echo.

echo [1/7] Backing up current gitignore...
copy ".gitignore" ".gitignore.backup_%date:~0,4%%date:~5,2%%date:~8,2%" >nul 2>&1

echo [2/7] Cleaning gitignore merge conflicts...
(
echo # Python
echo __pycache__/
echo *.py[cod]
echo *$py.class
echo *.so
echo .Python
echo build/
echo develop-eggs/
echo dist/
echo downloads/
echo eggs/
echo .eggs/
echo lib/
echo lib64/
echo parts/
echo sdist/
echo var/
echo wheels/
echo share/python-wheels/
echo *.egg-info/
echo .installed.cfg
echo *.egg
echo MANIFEST
echo.
echo # Virtual Environments
echo venv/
echo venv_*/
echo venv311/
echo venv_backup/
echo venv_new/
echo env/
echo ENV/
echo .venv
echo.
echo # Database files
echo *.db
echo *.sqlite
echo *.sqlite3
echo airiss.db
echo airiss_v4.db
echo *.backup
echo *_backup*
echo backup_*/
echo.
echo # Environment variables
echo .env
echo .env.local
echo .env.*.local
echo.
echo # Node.js
echo node_modules/
echo npm-debug.log*
echo yarn-debug.log*
echo yarn-error.log*
echo.
echo # Build outputs
echo dist/
echo build/
echo *.egg-info/
echo.
echo # IDEs
echo .vscode/
echo .idea/
echo *.swp
echo *.swo
echo *~
echo.
echo # OS
echo .DS_Store
echo Thumbs.db
echo *.tmp
echo *.temp
echo.
echo # AWS and Cloud
echo .elasticbeanstalk/
echo .aws/
echo *.pem
echo *.key
echo.
echo # Logs
echo *.log
echo logs/
echo log/
echo pip-log.txt
echo.
echo # Testing
echo .pytest_cache/
echo .coverage
echo htmlcov/
echo.
echo # Jupyter
echo .ipynb_checkpoints/
echo.
echo # Uploads and temporary
echo uploads/temp*
echo test_data/temp*
echo temp/
echo tmp/
echo *.tmp
echo.
echo # Deployment
echo .vercel
echo .railway/
echo.
echo # Backup files
echo cleanup_backup/
) > ".gitignore"

echo [3/7] Removing cached files from git...
git rm -r --cached . >nul 2>&1

echo [4/7] Adding files with new gitignore...
git add .

echo [5/7] Checking git status...
git status

echo [6/7] Committing changes...
git commit -m "Fix: Resolve gitignore merge conflicts and update ignore rules for Railway deployment"

echo [7/7] Pushing to GitHub...
git push origin main

echo.
if %errorlevel% equ 0 (
    echo ✅ SUCCESS: GitHub upload completed successfully!
    echo Repository is now ready for Railway deployment.
) else (
    echo ❌ ERROR: GitHub push failed. Checking authentication...
    echo.
    echo Possible solutions:
    echo 1. Check GitHub credentials: git config --list
    echo 2. Use personal access token instead of password
    echo 3. Check network connection
    echo 4. Try: git push -u origin main --force-with-lease
)

echo.
echo Press any key to continue...
pause >nul