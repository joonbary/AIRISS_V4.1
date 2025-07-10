@echo off
chcp 65001
echo =============================================
echo AIRISS AI 분석 문제 해결 완료!
echo =============================================

echo.
echo ✅ 수정 완료 사항:
echo    1. requirements.txt에 OpenAI 패키지 활성화
echo    2. AI/ML 관련 패키지 추가
echo    3. 7단계 등급 체계 이미 적용됨 (S, A+, A, B+, B, C, D)

echo.
echo 🚀 지금 바로 배포하시겠습니까?
choice /c YN /m "Y: 예 (배포 실행), N: 아니오 (취소)"

if errorlevel 2 goto :cancel
if errorlevel 1 goto :deploy

:deploy
echo.
echo [1단계] Git 상태 확인...
git status

echo.
echo [2단계] 변경사항 커밋...
git add requirements.txt
git commit -m "🔧 Fix: OpenAI 패키지 활성화로 AI 분석 기능 복원 + 7단계 등급 체계 (S~D) 적용"

echo.
echo [3단계] GitHub에 푸시...
git push origin main

echo.
echo [4단계] Railway 자동 배포 진행 중...
echo Railway에서 새 버전을 자동 배포합니다 (약 2-3분 소요).
echo.
echo 📊 배포 상태 모니터링:
echo https://railway.app/dashboard
echo.
echo 🎯 배포 완료 후 테스트:
echo https://web-production-4066.up.railway.app/dashboard

echo.
echo ⏳ 배포 완료까지 약 3분 대기 후 새로고침하세요.
echo ✨ AI 분석 기능이 정상 작동할 것입니다!
goto :end

:cancel
echo 배포가 취소되었습니다.

:end
echo.
pause
