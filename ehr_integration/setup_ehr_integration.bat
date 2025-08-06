@echo off
echo ================================================
echo    EHR-AIRISS Integration Setup Script
echo ================================================
echo.

REM Check if EHR project path is provided
if "%1"=="" (
    echo Usage: setup_ehr_integration.bat [EHR_PROJECT_PATH]
    echo Example: setup_ehr_integration.bat C:\Projects\EHR_V1.0
    exit /b 1
)

set EHR_PATH=%1
set AIRISS_MODULE_PATH=%EHR_PATH%\src\modules\airiss

echo Target EHR Project: %EHR_PATH%
echo.

REM Check if EHR project exists
if not exist "%EHR_PATH%" (
    echo Error: EHR project path does not exist!
    exit /b 1
)

REM Create module directory
echo Creating AIRISS module directory...
if not exist "%AIRISS_MODULE_PATH%" (
    mkdir "%AIRISS_MODULE_PATH%"
    mkdir "%AIRISS_MODULE_PATH%\components"
    mkdir "%AIRISS_MODULE_PATH%\services"
    mkdir "%AIRISS_MODULE_PATH%\context"
)

REM Copy integration files
echo.
echo Copying integration files...
copy /Y "EHR_AirissIntegration.jsx" "%AIRISS_MODULE_PATH%\"
copy /Y "EHR_AirissIntegration.css" "%AIRISS_MODULE_PATH%\"
copy /Y "ehr_integration_config.js" "%AIRISS_MODULE_PATH%\"
copy /Y "INTEGRATION_GUIDE.md" "%AIRISS_MODULE_PATH%\"

REM Copy component files
copy /Y "components\*.jsx" "%AIRISS_MODULE_PATH%\components\"
copy /Y "services\*.js" "%AIRISS_MODULE_PATH%\services\"
copy /Y "context\*.jsx" "%AIRISS_MODULE_PATH%\context\"

echo.
echo ================================================
echo    Integration files copied successfully!
echo ================================================
echo.
echo Next steps:
echo 1. cd %EHR_PATH%
echo 2. npm install axios (if not already installed)
echo 3. Import EHRAirissIntegration component in your app
echo 4. Add route for /airiss path
echo 5. Test the integration
echo.
echo For detailed instructions, see:
echo %AIRISS_MODULE_PATH%\INTEGRATION_GUIDE.md
echo.
echo AIRISS MSA URL: https://web-production-4066.up.railway.app
echo API Docs: https://web-production-4066.up.railway.app/docs
echo ================================================