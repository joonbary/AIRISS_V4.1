@echo off
echo ===============================================
echo AIRISS Railway Quick Check
echo ===============================================
echo.

echo Checking Railway CLI...
railway --version
echo.

echo Checking login status...
railway whoami
echo.

echo Getting latest logs...
railway logs --tail 50
echo.

echo Checking service status...
railway status
echo.

echo Checking environment variables...
railway variables
echo.

echo Testing local app import...
python -c "
try:
    from app.main import app
    print('SUCCESS: App imports correctly')
except Exception as e:
    print('ERROR: App import failed -', str(e))
"

echo.
echo ===============================================
echo Quick check completed.
echo ===============================================
pause
