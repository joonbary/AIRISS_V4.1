@echo off
echo ===============================================
echo AIRISS GitHub Sync Check
echo ===============================================

echo Checking Git status...
git status

echo.
echo Checking remote repository...
git remote -v

echo.
echo Checking current branch...
git branch

echo.
echo Checking recent commits...
git log --oneline -5

echo.
echo ===============================================
echo GitHub repository status checked.
echo ===============================================

echo.
echo Push latest changes to GitHub? (Y/N)
set /p push=
if /i "%push%"=="Y" (
    echo Adding all changes...
    git add .
    
    echo.
    set /p message=Enter commit message: 
    git commit -m "%message%"
    
    echo.
    echo Pushing to GitHub...
    git push origin main
    
    if %errorlevel% equ 0 (
        echo [SUCCESS] Changes pushed to GitHub
        echo Ready for deployment!
    ) else (
        echo [ERROR] Push failed
        echo Try: git push origin master
    )
)

pause
