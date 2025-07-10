@echo off
chcp 65001 > nul
echo.
echo ████████████████████████████████████████████████████████████████
echo ██                                                            ██
echo ██              AIRISS v5.0 인코딩 문제 해결                  ██
echo ██                                                            ██
echo ████████████████████████████████████████████████████████████████
echo.

echo 🔧 인코딩 문제 해결 방법을 선택하세요:
echo.
echo 1. 인코딩 수정 후 즉시 실행 (권장)
echo 2. PowerShell로 실행
echo 3. 영어 경로로 이동 후 실행
echo 4. 인코딩 환경 진단만 실행
echo 5. 수동 설정 가이드 보기
echo.

choice /c 12345 /n /m "선택하세요 (1-5): "

if errorlevel 5 goto manual_guide
if errorlevel 4 goto diagnose
if errorlevel 3 goto english_path
if errorlevel 2 goto powershell
if errorlevel 1 goto encoding_fix

:encoding_fix
echo.
echo 🚀 인코딩 수정 후 즉시 실행...
call fix_encoding_and_run.bat
goto end

:powershell
echo.
echo 🚀 PowerShell로 실행...
powershell -ExecutionPolicy Bypass -File start_airiss_v5.ps1
goto end

:english_path
echo.
echo 🚀 영어 경로로 이동 후 실행...
call start_airiss_v5_english_path.bat
goto end

:diagnose
echo.
echo 🔍 인코딩 환경 진단...
python diagnose_encoding.py
pause
goto end

:manual_guide
echo.
echo 📋 수동 설정 가이드:
echo.
echo 1. CMD 창에서 다음 명령 실행:
echo    chcp 65001
echo    set PYTHONIOENCODING=utf-8
echo    set PYTHONPATH=%CD%
echo.
echo 2. AIRISS 실행:
echo    uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
echo.
echo 3. 접속:
echo    http://localhost:8002
echo.
pause
goto end

:end
echo.
echo 작업 완료
pause
