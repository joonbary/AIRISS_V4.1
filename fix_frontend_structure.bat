@echo off
chcp 65001
echo ========================================
echo Fix Railway Frontend Build Issue
echo ========================================
echo.

cd /d "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

echo [1/5] Backup current frontend folder...
if exist frontend_backup rmdir /s /q frontend_backup
if exist frontend ren frontend frontend_backup
echo.

echo [2/5] Copy airiss-v4-frontend to frontend...
robocopy "airiss-v4-frontend" "frontend" /E /XD node_modules build .git /XF .env .env.* *.log
echo.

echo [3/5] Verify frontend structure...
if exist "frontend\package.json" (
    echo ✅ package.json found
) else (
    echo ❌ package.json missing
)

if exist "frontend\src" (
    echo ✅ src folder found
) else (
    echo ❌ src folder missing
)

if exist "frontend\public" (
    echo ✅ public folder found
) else (
    echo ❌ public folder missing
)
echo.

echo [4/5] Clean up potential issues...
if exist "frontend\.env" del "frontend\.env"
if exist "frontend\.env.production" del "frontend\.env.production"
if exist "frontend\node_modules" rmdir /s /q "frontend\node_modules"
if exist "frontend\build" rmdir /s /q "frontend\build"
echo.

echo [5/5] Check Auth component...
if exist "frontend\src\components\Auth.tsx" (
    echo ✅ Auth.tsx found - Build should work now!
) else (
    echo ❌ Auth.tsx missing - Check file structure
)
echo.

echo ========================================
echo Frontend Sync Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Run: git add .
echo 2. Run: git commit -m "Fix frontend folder structure for Railway"
echo 3. Run: git push origin main
echo 4. Check Railway deployment
echo.
pause
