@echo off
echo ===============================================
echo Node.js Installation Check
echo ===============================================

echo Checking Node.js...
node --version
if %errorlevel% neq 0 (
    echo [ERROR] Node.js not installed
    echo Download from: https://nodejs.org/
    echo Install LTS version
    pause
    exit /b 1
)

echo Checking npm...
npm --version
if %errorlevel% neq 0 (
    echo [ERROR] npm not available
    pause
    exit /b 1
)

echo [SUCCESS] Node.js and npm are available
echo Ready to install Railway CLI

echo.
echo Install Railway CLI now? (Y/N)
set /p install=
if /i "%install%"=="Y" (
    echo Installing Railway CLI...
    npm install -g @railway/cli
    
    echo.
    echo Testing Railway CLI installation...
    railway --version
    
    if %errorlevel% equ 0 (
        echo [SUCCESS] Railway CLI installed successfully
        echo Next step: railway login
    ) else (
        echo [ERROR] Railway CLI installation failed
    )
)

pause
