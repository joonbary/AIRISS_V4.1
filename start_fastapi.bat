@echo off
echo Starting FastAPI server on port 8001...
cd app
set PORT=8001
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
pause