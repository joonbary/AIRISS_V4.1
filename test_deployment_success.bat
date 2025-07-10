@echo off
chcp 65001 > nul
echo 🧪 AIRISS v4.1 Complete - Railway 배포 성공 테스트

echo.
set /p RAILWAY_URL="🌐 Railway 배포 URL을 입력하세요 (예: https://airiss-production.up.railway.app): "

echo.
echo 📋 테스트 시나리오 실행 중...

echo.
echo 1️⃣ 헬스체크 테스트
curl -s "%RAILWAY_URL%/health" | findstr "healthy"
if %errorlevel%==0 (
    echo    ✅ 헬스체크 통과
) else (
    echo    ❌ 헬스체크 실패
)

echo.
echo 2️⃣ API 엔드포인트 테스트  
curl -s "%RAILWAY_URL%/api" | findstr "AIRISS"
if %errorlevel%==0 (
    echo    ✅ API 정상 작동
) else (
    echo    ❌ API 접근 실패
)

echo.
echo 3️⃣ 프론트엔드 테스트
curl -s "%RAILWAY_URL%/" | findstr "DOCTYPE\|html"
if %errorlevel%==0 (
    echo    ✅ React 앱 서빙 정상
) else (
    echo    ❌ 프론트엔드 접근 실패
)

echo.
echo 4️⃣ 상세 상태 테스트
curl -s "%RAILWAY_URL%/api/status" | findstr "react_build_exists"
if %errorlevel%==0 (
    echo    ✅ React 빌드 상태 확인 가능
) else (
    echo    ❌ 상세 상태 확인 실패
)

echo.
echo 📊 최종 테스트 결과:
echo    🌐 웹 브라우저에서 다음 URL들을 직접 확인하세요:
echo.
echo    🏠 메인 페이지: %RAILWAY_URL%/
echo    📊 API 정보: %RAILWAY_URL%/api
echo    💓 헬스체크: %RAILWAY_URL%/health  
echo    📈 상세 상태: %RAILWAY_URL%/api/status

echo.
echo 🎉 모든 테스트가 통과하면 AIRISS v4.1 Complete 배포 성공!
echo    - React 프론트엔드와 FastAPI 백엔드가 완전 통합
echo    - Railway 클라우드에서 안정적 운영
echo    - 다음 단계: 전체 기능 복원 및 고도화

pause
