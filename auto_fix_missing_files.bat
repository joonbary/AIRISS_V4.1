@echo off
chcp 65001 >nul 2>&1
cd /d "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

echo ========================================
echo AIRISS Auto-Fix Missing Files
echo ========================================
echo.

echo [Checking and fixing essential files...]

REM Fix Procfile
if not exist "Procfile" (
    echo Creating Procfile...
    echo web: uvicorn main:app --host 0.0.0.0 --port $PORT > Procfile
    echo ✅ Procfile created
) else (
    echo ✅ Procfile already exists
)

REM Check and fix main.py for Railway compatibility
if exist "main.py" (
    echo Checking main.py for Railway compatibility...
    findstr /C:"PORT" main.py >nul
    if %errorlevel% neq 0 (
        echo Adding PORT environment variable handling to main.py...
        echo.
        echo # Adding Railway port compatibility >> main.py
        echo import os >> main.py
        echo PORT = int(os.environ.get("PORT", 8000)) >> main.py
        echo.
        echo if __name__ == "__main__": >> main.py
        echo     import uvicorn >> main.py
        echo     uvicorn.run("main:app", host="0.0.0.0", port=PORT) >> main.py
        echo ✅ PORT handling added to main.py
    )
) else if exist "application.py" (
    echo Using application.py as main entry point...
    echo Checking application.py for Railway compatibility...
) else (
    echo ❌ No main application file found. Please check your FastAPI setup.
)

REM Create runtime.txt if missing
if not exist "runtime.txt" (
    echo Creating runtime.txt...
    echo python-3.11.9 > runtime.txt
    echo ✅ runtime.txt created (Python 3.11.9)
) else (
    echo ✅ runtime.txt already exists
)

REM Create railway.json if missing
if not exist "railway.json" (
    echo Creating railway.json...
    (
    echo {
    echo   "build": {
    echo     "builder": "nixpacks"
    echo   },
    echo   "deploy": {
    echo     "restartPolicyType": "ON_FAILURE",
    echo     "restartPolicyMaxRetries": 10
    echo   }
    echo }
    ) > railway.json
    echo ✅ railway.json created
) else (
    echo ✅ railway.json already exists
)

REM Create .env.example if missing
if not exist ".env.example" (
    echo Creating .env.example...
    (
    echo # Database Configuration
    echo DATABASE_URL=postgresql://username:password@hostname:port/database_name
    echo NEON_DATABASE_URL=postgresql://username:password@hostname:port/database_name
    echo.
    echo # Application Settings
    echo SECRET_KEY=your_secret_key_here
    echo DEBUG=False
    echo.
    echo # CORS Settings
    echo FRONTEND_URL=http://localhost:3000
    echo.
    echo # Railway Deployment
    echo PORT=8000
    ) > .env.example
    echo ✅ .env.example created
) else (
    echo ✅ .env.example already exists
)

REM Check requirements.txt for essential dependencies
echo Checking requirements.txt for Railway dependencies...
if exist "requirements.txt" (
    findstr /C:"fastapi" requirements.txt >nul || (
        echo Adding FastAPI to requirements.txt...
        echo fastapi^>=0.100.0 >> requirements.txt
    )
    findstr /C:"uvicorn" requirements.txt >nul || (
        echo Adding uvicorn to requirements.txt...
        echo uvicorn[standard]^>=0.22.0 >> requirements.txt
    )
    findstr /C:"python-multipart" requirements.txt >nul || (
        echo Adding python-multipart to requirements.txt...
        echo python-multipart^>=0.0.6 >> requirements.txt
    )
    echo ✅ Essential dependencies checked/added
) else (
    echo Creating requirements.txt with essential dependencies...
    (
    echo fastapi^>=0.100.0
    echo uvicorn[standard]^>=0.22.0
    echo python-multipart^>=0.0.6
    echo python-dotenv^>=1.0.0
    echo sqlalchemy^>=2.0.0
    echo psycopg2-binary^>=2.9.0
    ) > requirements.txt
    echo ✅ requirements.txt created with essential dependencies
)

echo.
echo ========================================
echo AUTO-FIX COMPLETED
echo ========================================
echo.
echo Files checked/created:
echo - Procfile ✅
echo - runtime.txt ✅  
echo - railway.json ✅
echo - .env.example ✅
echo - requirements.txt dependencies ✅
echo.
echo Next steps:
echo 1. Run railway_deploy_check.bat to verify readiness
echo 2. Run github_upload_fix.bat to upload to GitHub
echo 3. Deploy to Railway
echo.
echo Press any key to continue...
pause >nul