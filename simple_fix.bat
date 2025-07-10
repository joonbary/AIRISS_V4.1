@echo off
cd /d %~dp0

echo AIRISS Python Fix Starting...

if exist venv_new rmdir /s /q venv_new
if exist venv rmdir /s /q venv

python -m venv venv_new
call venv_new\Scripts\activate.bat

python -m pip install --upgrade pip

pip install fastapi==0.104.1
pip install uvicorn[standard]==0.24.0
pip install python-multipart==0.0.6
pip install jinja2==3.1.2
pip install aiosqlite==0.19.0
pip install pandas>=2.2.0
pip install numpy>=1.24.0
pip install scikit-learn>=1.3.0
pip install openpyxl==3.1.2
pip install aiofiles==23.2.1
pip install python-dotenv==1.0.0
pip install pydantic>=2.5.0
pip install websockets==12.0

echo Testing packages...
python -c "import fastapi, uvicorn, pandas"

if errorlevel 1 (
    echo Package test failed
    pause
    exit /b 1
)

echo Starting server on port 8003...
python -m uvicorn app.main:app --host 0.0.0.0 --port 8003

pause
