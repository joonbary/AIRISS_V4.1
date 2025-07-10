@echo off
echo AIRISS v4.1 Complete - Railway Deployment Success Test

echo.
set /p RAILWAY_URL="Enter Railway deployment URL (e.g., https://airiss-production.up.railway.app): "

echo.
echo Running test scenarios...

echo.
echo 1. Health Check Test
curl -s "%RAILWAY_URL%/health" | findstr "healthy"
if %errorlevel%==0 (
    echo    SUCCESS: Health check passed
) else (
    echo    FAILED: Health check failed
)

echo.
echo 2. API Endpoint Test  
curl -s "%RAILWAY_URL%/api" | findstr "AIRISS"
if %errorlevel%==0 (
    echo    SUCCESS: API working normally
) else (
    echo    FAILED: API access failed
)

echo.
echo 3. Frontend Test
curl -s "%RAILWAY_URL%/" | findstr "DOCTYPE\|html"
if %errorlevel%==0 (
    echo    SUCCESS: React app serving normally
) else (
    echo    FAILED: Frontend access failed
)

echo.
echo 4. Detailed Status Test
curl -s "%RAILWAY_URL%/api/status" | findstr "react_build_exists"
if %errorlevel%==0 (
    echo    SUCCESS: React build status available
) else (
    echo    FAILED: Detailed status check failed
)

echo.
echo Final Test Results:
echo    Please verify these URLs directly in your web browser:
echo.
echo    Home Page: %RAILWAY_URL%/
echo    API Info: %RAILWAY_URL%/api
echo    Health Check: %RAILWAY_URL%/health  
echo    Detailed Status: %RAILWAY_URL%/api/status

echo.
echo If all tests pass, AIRISS v4.1 Complete deployment is successful!
echo    - React frontend and FastAPI backend fully integrated
echo    - Stable operation on Railway cloud
echo    - Next step: Restore full features and enhancement

pause
