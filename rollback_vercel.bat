@echo off
REM AIRISS v4.1 Rollback Script - Encoding Safe
REM Restore original files if deployment fails

echo ==========================================
echo    AIRISS v4.1 Deployment Rollback
echo ==========================================

echo.
echo [1/4] Restoring backup files...

if exist "vercel.json.backup" (
    copy "vercel.json.backup" "vercel.json" >nul 2>&1
    echo   - vercel.json restored
) else (
    echo   - No vercel.json backup found
)

if exist "requirements.txt.backup" (
    copy "requirements.txt.backup" "requirements.txt" >nul 2>&1
    echo   - requirements.txt restored
) else (
    echo   - No requirements.txt backup found
)

if exist "api\index.py.backup" (
    copy "api\index.py.backup" "api\index.py" >nul 2>&1
    echo   - api\index.py restored
) else (
    echo   - No api\index.py backup found
)

echo [2/4] Commit rollback changes...
git add .
git commit -m "Rollback: Restore original configuration"

echo [3/4] Push rollback to GitHub...
git push origin main

echo [4/4] Rollback complete!
echo.
echo SUCCESS: Original configuration restored
echo.
echo Vercel will auto-redeploy the rollback
echo Check deployment status at: https://vercel.com/dashboard
echo.
echo Press any key to exit...
pause >nul
