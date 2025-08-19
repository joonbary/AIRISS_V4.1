@echo off
echo.
echo ====================================
echo    AIRISS API Server Status Check
echo ====================================
echo.

REM Check if port 8080 is in use
netstat -an | findstr :8080 | findstr LISTENING >nul
if %errorlevel% == 0 (
    echo [OK] Port 8080 is active - API server is running
    echo.
    echo Testing API endpoints...
    echo.
    
    REM Test health endpoint
    curl -s -o nul -w "Health Check: %%{http_code}\n" http://localhost:8080/api/v1/health
    
    REM Test dashboard stats endpoint
    curl -s -o nul -w "Dashboard Stats: %%{http_code}\n" http://localhost:8080/api/v1/hr-dashboard/stats
    
    echo.
    echo If you see 200 status codes, the API is working correctly.
    echo If you see 404 or other errors, check your API routes.
) else (
    echo [ERROR] Port 8080 is not active - API server is NOT running
    echo.
    echo To start the FastAPI server, run:
    echo.
    echo    cd app
    echo    uvicorn main:app --reload --port 8080
    echo.
    echo Or use the start_fastapi.bat file
)

echo.
echo ====================================
pause