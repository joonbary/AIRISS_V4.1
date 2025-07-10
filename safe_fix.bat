@echo off
REM AIRISS Safe Fix
cd /d %~dp0

echo Step 1: Clean old environment
if exist venv_new rmdir /s /q venv_new

echo Step 2: Create new environment  
python -m venv venv_new

echo Step 3: Activate environment
call venv_new\Scripts\activate.bat

echo Step 4: Upgrade pip
python -m pip install --upgrade pip

echo Step 5: Install packages
pip install --only-binary=all fastapi==0.104.1
pip install --only-binary=all uvicorn[standard]==0.24.0  
pip install --only-binary=all python-multipart==0.0.6
pip install --only-binary=all jinja2==3.1.2
pip install --only-binary=all aiosqlite==0.19.0
pip install --only-binary=all pandas>=2.2.0
pip install --only-binary=all numpy>=1.24.0
pip install --only-binary=all scikit-learn>=1.3.0
pip install --only-binary=all openpyxl==3.1.2
pip install --only-binary=all aiofiles==23.2.1
pip install --only-binary=all python-dotenv==1.0.0
pip install --only-binary=all pydantic>=2.5.0
pip install --only-binary=all websockets==12.0

echo Step 6: Test imports
python -c "import fastapi, uvicorn, pandas, numpy"
if errorlevel 1 goto error

echo Step 7: Start server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8003
goto end

:error
echo Import test failed - check packages
pause
exit /b 1

:end
pause
