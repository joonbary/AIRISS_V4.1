@echo off
echo AIRISS Basic Check
echo ==================

echo 1. Check Python...
python --version

echo.
echo 2. Check if app imports...
python -c "import sys; sys.path.append('.'); from app.main import app; print('App import: OK')"

echo.
echo 3. Check requirements install...
pip list | findstr fastapi

echo.
echo 4. Check Railway CLI...
where railway

echo.
echo 5. Test basic railway command...
railway --help

echo.
echo Check completed.
pause
