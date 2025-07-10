@echo off
chcp 65001 >nul
echo.
echo ===============================================
echo   AIRISS v4.1 빠른 배포 상태 확인
echo   (환경 문제와 무관하게 프로젝트 상태 점검)
echo ===============================================
echo.

echo [1] 프로젝트 구조 확인...
if exist app\main.py (
    echo ✅ 메인 애플리케이션 파일 존재
) else (
    echo ❌ 메인 애플리케이션 파일 없음
)

if exist app\templates\index.html (
    echo ✅ 프론트엔드 템플릿 존재
) else (
    echo ❌ 프론트엔드 템플릿 없음
)

if exist requirements.txt (
    echo ✅ 패키지 요구사항 파일 존재
) else (
    echo ❌ 패키지 요구사항 파일 없음
)

echo.
echo [2] GitHub 상태 확인...
git status
echo.

echo [3] 프론트엔드 폴더 확인...
if exist airiss-v4-frontend (
    echo ✅ 프론트엔드 폴더 존재
    cd airiss-v4-frontend
    echo 프론트엔드 패키지 설치 상태:
    if exist node_modules (
        echo ✅ node_modules 존재
    ) else (
        echo ❌ node_modules 없음 - npm install 필요
        echo npm install 실행 중...
        npm install
    )
    cd ..
) else (
    echo ❌ 프론트엔드 폴더 없음
)

echo.
echo [4] Vercel 배포 URL 찾기...
echo 다음 명령어로 Vercel 대시보드에서 URL 확인:
echo 1. https://vercel.com/dashboard 접속
echo 2. airiss-enterprise 프로젝트 클릭
echo 3. Deployments 탭에서 최신 배포 URL 확인

echo.
echo ===============================================
echo 📋 현재 배포 옵션:
echo ===============================================
echo.
echo 🟢 Option A: 백엔드 환경 문제 해결
echo    → fix_deployment_safe.bat 실행
echo.
echo 🟡 Option B: 프론트엔드만 우선 배포
echo    → Vercel에서 정적 사이트만 먼저 공개
echo.
echo 🔵 Option C: 클라우드 IDE 사용
echo    → GitHub Codespaces에서 환경 무관하게 실행
echo.
echo ===============================================
echo.
pause
