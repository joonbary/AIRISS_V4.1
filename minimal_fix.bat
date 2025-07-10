@echo off
cd %~dp0
rmdir /s /q venv_new 2>nul
python -m venv venv_new
call venv_new\Scripts\activate.bat
pip install fastapi uvicorn pandas numpy aiosqlite jinja2 python-multipart openpyxl aiofiles python-dotenv pydantic websockets scikit-learn
python -m uvicorn app.main:app --host 0.0.0.0 --port 8003
pause
