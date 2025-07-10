@echo off
REM AIRISS v4.1 Windows 인코딩 안전 배포 스크립트
REM Windows/OneDrive 한글/특수문자 경로 대응

echo ============================================
echo AIRISS v4.1 Windows 인코딩 안전 배포 도구
echo ============================================
echo.

REM 인코딩 설정 (Windows 호환)
chcp 65001 >nul 2>&1

REM 현재 경로 확인
echo [INFO] 현재 작업 디렉토리: %CD%
echo [INFO] 프로젝트 폴더 확인...

REM AIRISS 프로젝트 폴더인지 확인
if not exist "app\main.py" (
    echo [ERROR] AIRISS 프로젝트 폴더가 아닙니다!
    echo [ERROR] app\main.py 파일이 없습니다.
    echo [INFO] 올바른 AIRISS 프로젝트 폴더에서 실행하세요.
    pause
    exit /b 1
)

if not exist "airiss-v4-frontend\package.json" (
    echo [ERROR] React 프론트엔드 폴더가 없습니다!
    echo [ERROR] airiss-v4-frontend\package.json 파일이 없습니다.
    pause
    exit /b 1
)

echo [SUCCESS] AIRISS v4.1 프로젝트 폴더 확인 완료
echo.

REM 메뉴 선택
:MENU
echo ============================================
echo 작업을 선택하세요:
echo ============================================
echo 1. 프로젝트 정리 (임시 파일 제거)
echo 2. Railway 배포 준비
echo 3. 로컬 서버 실행 (개발 모드)
echo 4. React 빌드 테스트
echo 5. 환경 변수 확인
echo 6. Git 상태 확인
echo 7. 전체 시스템 진단
echo 8. 종료
echo.
set /p choice="선택 (1-8): "

if "%choice%"=="1" goto CLEANUP
if "%choice%"=="2" goto RAILWAY_PREP
if "%choice%"=="3" goto LOCAL_SERVER
if "%choice%"=="4" goto REACT_BUILD
if "%choice%"=="5" goto ENV_CHECK
if "%choice%"=="6" goto GIT_CHECK
if "%choice%"=="7" goto SYSTEM_DIAG
if "%choice%"=="8" goto EXIT
goto MENU

REM ============================================
REM 1. 프로젝트 정리
REM ============================================
:CLEANUP
echo.
echo [INFO] 프로젝트 정리를 시작합니다...
echo [INFO] 임시 파일과 백업 파일들을 정리합니다.

REM Python 정리 스크립트가 있으면 실행
if exist "auto_cleanup_airiss.py" (
    echo [INFO] Python 정리 스크립트 실행...
    python auto_cleanup_airiss.py --dry-run
    echo.
    set /p cleanup_confirm="실제 정리를 실행하시겠습니까? (y/N): "
    if /i "%cleanup_confirm%"=="y" (
        python auto_cleanup_airiss.py --force
    )
) else (
    echo [INFO] 기본 정리 실행...
    
    REM __pycache__ 폴더들 제거
    echo [INFO] Python 캐시 폴더 정리...
    for /d /r . %%d in (__pycache__) do (
        if exist "%%d" (
            echo [REMOVE] %%d
            rmdir /s /q "%%d" 2>nul
        )
    )
    
    REM .pyc 파일들 제거
    echo [INFO] Python 바이트코드 파일 정리...
    for /r . %%f in (*.pyc) do (
        if exist "%%f" (
            echo [REMOVE] %%f
            del /q "%%f" 2>nul
        )
    )
    
    REM 임시 로그 파일들 제거
    echo [INFO] 임시 로그 파일 정리...
    if exist "*.log" del /q "*.log" 2>nul
    if exist "cleanup_log.txt" del /q "cleanup_log.txt" 2>nul
    
    echo [SUCCESS] 기본 정리 완료!
)

echo.
pause
goto MENU

REM ============================================
REM 2. Railway 배포 준비
REM ============================================
:RAILWAY_PREP
echo.
echo [INFO] Railway 배포 준비를 시작합니다...

REM 필수 파일 확인
echo [INFO] 필수 파일 확인...
set missing_files=0

if not exist "Dockerfile" (
    echo [ERROR] Dockerfile이 없습니다!
    set missing_files=1
)

if not exist "requirements.txt" (
    echo [ERROR] requirements.txt가 없습니다!
    set missing_files=1
)

if not exist "railway.json" (
    echo [ERROR] railway.json이 없습니다!
    set missing_files=1
)

if %missing_files%==1 (
    echo [ERROR] 필수 파일이 누락되었습니다!
    pause
    goto MENU
)

echo [SUCCESS] 필수 파일 확인 완료!

REM React 빌드 확인
echo [INFO] React 빌드 확인...
if not exist "airiss-v4-frontend\build\index.html" (
    echo [WARNING] React 빌드가 없습니다. 빌드를 생성합니다...
    cd airiss-v4-frontend
    call npm run build
    cd ..
    
    if not exist "airiss-v4-frontend\build\index.html" (
        echo [ERROR] React 빌드 실패!
        pause
        goto MENU
    )
)

echo [SUCCESS] React 빌드 확인 완료!

REM Git 준비
echo [INFO] Git 커밋 확인...
git add .
git status

echo.
echo [INFO] Railway 배포 준비 완료!
echo [INFO] 이제 Railway에서 자동 배포됩니다.
echo.
echo Railway 배포 확인 방법:
echo 1. Railway 대시보드에서 빌드 로그 확인
echo 2. https://your-app.up.railway.app/health 접속 테스트
echo 3. https://your-app.up.railway.app/api 접속 테스트
echo.
pause
goto MENU

REM ============================================
REM 3. 로컬 서버 실행
REM ============================================
:LOCAL_SERVER
echo.
echo [INFO] 로컬 서버를 시작합니다...
echo [INFO] 서버 주소: http://localhost:8002
echo [INFO] 종료하려면 Ctrl+C를 누르세요.
echo.

REM 환경변수 설정
set PYTHONPATH=%CD%
set SERVER_HOST=0.0.0.0
set SERVER_PORT=8002
set REACT_BUILD_PATH=%CD%\static

REM Python 가상환경 확인 (선택적)
if exist "venv\Scripts\activate.bat" (
    echo [INFO] 가상환경 활성화...
    call venv\Scripts\activate.bat
)

REM 서버 실행
python -m uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload

pause
goto MENU

REM ============================================
REM 4. React 빌드 테스트
REM ============================================
:REACT_BUILD
echo.
echo [INFO] React 빌드 테스트를 시작합니다...

cd airiss-v4-frontend

REM Node.js 버전 확인
echo [INFO] Node.js 버전:
node --version
npm --version

REM 종속성 설치 확인
echo [INFO] npm 종속성 확인...
if not exist "node_modules" (
    echo [INFO] npm 종속성 설치...
    npm install
)

REM 빌드 실행
echo [INFO] React 빌드 실행...
call npm run build

if exist "build\index.html" (
    echo [SUCCESS] React 빌드 성공!
    echo [INFO] 빌드 결과: build\index.html
) else (
    echo [ERROR] React 빌드 실패!
)

cd ..
pause
goto MENU

REM ============================================
REM 5. 환경 변수 확인
REM ============================================
:ENV_CHECK
echo.
echo [INFO] 환경 변수 확인...
echo.

echo [ENV] Python 경로: %PYTHONPATH%
echo [ENV] 서버 호스트: %SERVER_HOST%
echo [ENV] 서버 포트: %SERVER_PORT%
echo [ENV] React 빌드 경로: %REACT_BUILD_PATH%
echo [ENV] Railway PORT: %PORT%
echo.

echo [INFO] .env 파일 확인...
if exist ".env" (
    echo [SUCCESS] .env 파일 존재
) else (
    echo [WARNING] .env 파일 없음
    if exist ".env.example" (
        echo [INFO] .env.example을 복사하여 .env를 생성하세요
        echo copy .env.example .env
    )
)

echo.
echo [INFO] Python 인코딩 확인...
python -c "import sys; print('기본 인코딩:', sys.getdefaultencoding()); print('파일시스템 인코딩:', sys.getfilesystemencoding()); print('플랫폼:', sys.platform)"

pause
goto MENU

REM ============================================
REM 6. Git 상태 확인
REM ============================================
:GIT_CHECK
echo.
echo [INFO] Git 상태 확인...
echo.

git status
echo.

echo [INFO] 최근 커밋:
git log --oneline -5
echo.

echo [INFO] 원격 저장소:
git remote -v
echo.

echo [INFO] 현재 브랜치:
git branch
echo.

pause
goto MENU

REM ============================================
REM 7. 전체 시스템 진단
REM ============================================
:SYSTEM_DIAG
echo.
echo [INFO] 전체 시스템 진단을 시작합니다...
echo.

REM Python 진단 스크립트 실행
if exist "app\utils\encoding_safe.py" (
    echo [INFO] 인코딩 안전성 진단...
    python -c "from app.utils.encoding_safe import EncodingSafeUtils; EncodingSafeUtils.log_encoding_info()"
    echo.
)

REM 파일 구조 확인
echo [INFO] 프로젝트 구조 확인...
echo.
if exist "app\main.py" echo [OK] app\main.py
if exist "airiss-v4-frontend\package.json" echo [OK] airiss-v4-frontend\package.json
if exist "Dockerfile" echo [OK] Dockerfile
if exist "requirements.txt" echo [OK] requirements.txt
if exist "railway.json" echo [OK] railway.json
if not exist "app\main.py" echo [MISSING] app\main.py
if not exist "airiss-v4-frontend\package.json" echo [MISSING] airiss-v4-frontend\package.json
if not exist "Dockerfile" echo [MISSING] Dockerfile
if not exist "requirements.txt" echo [MISSING] requirements.txt
if not exist "railway.json" echo [MISSING] railway.json

echo.
echo [INFO] React 빌드 확인...
if exist "airiss-v4-frontend\build\index.html" (
    echo [OK] React 빌드 존재
) else (
    echo [WARNING] React 빌드 없음
)

echo.
echo [INFO] 진단 완료!

pause
goto MENU

REM ============================================
REM 8. 종료
REM ============================================
:EXIT
echo.
echo [INFO] AIRISS v4.1 배포 도구를 종료합니다.
echo [INFO] 배포 성공을 기원합니다! 🚀
echo.
exit /b 0
