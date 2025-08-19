@echo off
echo Starting FastAPI server on port 8080...
cd app
set PORT=8080
uvicorn main:app --host 0.0.0.0 --port 8080 --reload
pause