@echo off
echo ========================================
echo AIRISS v4.1 Complete - Quick Success Test
echo ========================================

echo.
echo Enter your Railway deployment URL when ready:
echo Example: https://airiss-production-abc123.up.railway.app
echo.
set /p RAILWAY_URL="Railway URL: "

echo.
echo Testing deployment...
echo.

echo 1. Health Check Test:
curl -s "%RAILWAY_URL%/health"
echo.
echo.

echo 2. API Test:
curl -s "%RAILWAY_URL%/api"
echo.
echo.

echo 3. React Build Status:
curl -s "%RAILWAY_URL%/api/status"
echo.
echo.

echo ========================================
echo Manual Verification URLs:
echo ========================================
echo.
echo Open these in your browser:
echo.
echo Main App:     %RAILWAY_URL%/
echo Health Check: %RAILWAY_URL%/health
echo API Info:     %RAILWAY_URL%/api
echo Build Status: %RAILWAY_URL%/api/status
echo.
echo ========================================
echo Expected Success Indicators:
echo ========================================
echo.
echo Health: "status": "healthy"
echo React:  "react_build": "available"  
echo API:    "AIRISS v4.1 Complete API"
echo Frontend: HTML page with React app
echo.

pause
