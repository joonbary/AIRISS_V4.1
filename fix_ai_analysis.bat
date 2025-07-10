@echo off
chcp 65001
echo =============================================
echo AIRISS AI 분석 문제 해결 및 배포 스크립트
echo =============================================

echo.
echo [1단계] Git 상태 확인...
git status

echo.
echo [2단계] 변경사항 커밋...
git add requirements.txt
git commit -m "Fix: OpenAI 패키지 활성화로 AI 분석 기능 복원"

echo.
echo [3단계] GitHub에 푸시...
git push origin main

echo.
echo [4단계] Railway 자동 배포 대기 중... (약 2-3분 소요)
echo Railway가 자동으로 새 버전을 배포합니다.
echo.
echo 배포 상태 확인:
echo https://railway.app/dashboard
echo.
echo 배포된 앱 확인:
echo https://web-production-4066.up.railway.app/dashboard

echo.
echo =============================================
echo AI 분석 문제 해결 완료!
echo =============================================
echo.
echo 다음 사항들이 수정되었습니다:
echo ✅ OpenAI 패키지 활성화
echo ✅ AI/ML 패키지 추가 (선택적)
echo ✅ 7단계 등급 체계 (S, A+, A, B+, B, C, D) 이미 적용됨
echo.
echo 주의: AI 기능을 사용하려면 OpenAI API 키가 필요합니다.
echo 설정에서 API 키를 입력해주세요.
echo.
pause
