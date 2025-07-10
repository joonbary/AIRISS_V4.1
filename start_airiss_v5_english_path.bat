@echo off
chcp 65001 > nul
echo ===============================================
echo AIRISS v5.0 - 영어 경로 이동 솔루션
echo ===============================================
echo.

REM 현재 경로 확인
echo 현재 경로: %CD%
echo.

REM 영어 경로 제안
set ENGLISH_PATH=C:\AIRISS_v5
echo 권장 영어 경로: %ENGLISH_PATH%
echo.

REM 사용자 선택
echo 옵션을 선택하세요:
echo 1. 영어 경로로 복사하여 실행
echo 2. 현재 경로에서 인코딩 수정하여 실행
echo 3. 진단만 실행
echo.

choice /c 123 /n /m "선택하세요 (1, 2, 3): "

if errorlevel 3 goto diagnose
if errorlevel 2 goto fix_encoding
if errorlevel 1 goto copy_to_english

:copy_to_english
echo.
echo 영어 경로로 복사 중...
if not exist %ENGLISH_PATH% (
    mkdir %ENGLISH_PATH%
)

echo 파일 복사 중...
xcopy /E /I /Y "%CD%\*" "%ENGLISH_PATH%\" > nul
echo 복사 완료!

echo.
echo 영어 경로로 이동 중...
cd /d %ENGLISH_PATH%
echo 현재 위치: %CD%

echo.
echo AIRISS v5.0 시작 중...
set PYTHONIOENCODING=utf-8
set PYTHONPATH=%CD%
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
goto end

:fix_encoding
echo.
echo 현재 경로에서 인코딩 수정 실행...
set PYTHONIOENCODING=utf-8
set PYTHONPATH=%CD%
set LANG=ko_KR.UTF-8
python -X utf8 -m uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
goto end

:diagnose
echo.
echo 인코딩 진단 실행...
python diagnose_encoding.py
pause
goto end

:end
echo.
echo 실행 완료
pause
