@echo off
echo ===============================================
echo AIRISS v5.0 - Switch to Clean Branch
echo ===============================================
echo.

echo Step 1: Switch to clean branch
echo ===============================================
git checkout v5-clean-final
echo Switched to clean branch

echo.
echo Step 2: Set as default tracking branch
echo ===============================================
git branch --set-upstream-to=origin/v5-clean-final v5-clean-final
echo Set tracking branch

echo.
echo Step 3: Check current status
echo ===============================================
git status
git log --oneline -5

echo.
echo Step 4: Create working .env file
echo ===============================================
if not exist .env (
    copy .env.template .env
    echo .env file created from template
    echo Please edit .env file and add your actual API keys
) else (
    echo .env file already exists
)

echo.
echo ===============================================
echo READY TO WORK!
echo ===============================================
echo You are now on the clean branch: v5-clean-final
echo No sensitive information in the commit history
echo.
echo Next steps:
echo 1. Edit .env file with your actual API keys
echo 2. Run: python main.py
echo 3. Continue development normally
echo.
pause
