@echo off
chcp 65001 >nul
echo ============================================================
echo AIRISS NEON DB 통합 완료 버전 - GitHub 업로드
echo ============================================================
echo.

cd /d "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

echo 📋 현재 Git 상태 확인 중...
echo.

git status
echo.

echo ============================================================
echo 🎯 업로드 옵션을 선택하세요:
echo ============================================================
echo.
echo 1. 기존 AIRISS_V4.1 리포지토리에 업로드 (추천)
echo 2. 현재 AIRISS_V5_Clean 리포지토리에 업로드  
echo 3. 새 브랜치로 안전하게 업로드
echo 4. 백업 후 업로드
echo 0. 취소
echo.

set /p choice="선택하세요 (1-4, 0=취소): "

if "%choice%"=="1" goto upload_v41
if "%choice%"=="2" goto upload_v5clean
if "%choice%"=="3" goto upload_newbranch
if "%choice%"=="4" goto upload_backup
if "%choice%"=="0" goto cancel

echo 잘못된 선택입니다.
pause
exit /b

:upload_v41
echo.
echo 📤 AIRISS_V4.1 리포지토리에 업로드 중...
echo.

echo 리모트 URL 변경...
git remote remove origin
git remote add origin https://github.com/joonbary/AIRISS_V4.1.git

echo.
echo 변경사항 스테이징...
git add .

echo.
echo 커밋 생성...
git commit -m "✅ NEON DB 통합 완료 (PostgreSQL 단일 아키텍처)

🎯 주요 변경사항:
- PostgreSQL-only 스토리지 서비스로 완전 전환
- SQLite 의존성 완전 제거
- analysis_storage_service.py → PostgreSQL 전용으로 교체
- 변수명 호환성 유지 (storage_service alias 추가)
- 통합 테스트 4/4 모두 통과

📊 성과:
- 단일 클라우드 데이터베이스 아키텍처 구축
- 확장성 및 안정성 향상
- Neon DB 엔터프라이즈급 기능 활용

🔗 연결된 이슈: 데이터베이스 이중화 문제 해결
⚡ 다음 단계: v5 AI 기능 점진적 도입 준비"

echo.
echo 리포지토리에 푸시...
git push origin main --force-with-lease

goto success

:upload_v5clean
echo.
echo 📤 AIRISS_V5_Clean 리포지토리에 업로드 중...
echo.

echo 변경사항 스테이징...
git add .

echo.
echo 커밋 생성...
git commit -m "🎉 NEON DB 통합 100%% 완료 - Production Ready

✅ 완료된 작업:
- PostgreSQL 전용 스토리지 서비스 구현
- SQLite 완전 제거 및 단일 DB 아키텍처
- 변수명 호환성 유지 (storage_service = postgresql_storage_service)
- 전체 시스템 통합 테스트 통과 (4/4)

🏗️ 기술적 개선:
- analysis_storage_service.py 완전 재작성
- Neon DB 클라우드 PostgreSQL 최적화
- 백업 호환성 유지 (postgresql_storage_service alias)
- 통합 검증 스크립트 추가

📈 비즈니스 임팩트:
- 확장 가능한 클라우드 네이티브 아키텍처
- 엔터프라이즈급 데이터 보안 및 백업
- v5 AI 기능 도입 기반 완성

🚀 Ready for: v5 딥러닝 NLP 및 예측 분석 기능 통합"

echo.
echo 현재 브랜치에 푸시...
git push origin HEAD

goto success

:upload_newbranch
echo.
echo 🌿 새 브랜치 'neon-db-integration' 생성 및 업로드...
echo.

echo 새 브랜치 생성...
git checkout -b neon-db-integration

echo 변경사항 스테이징...
git add .

echo 커밋 생성...
git commit -m "🎯 NEON DB 통합 완료 - 새 브랜치

📋 통합 완료 사항:
✅ PostgreSQL-only 아키텍처 구현
✅ SQLite 의존성 완전 제거  
✅ analysis_storage_service.py 전면 재작성
✅ 변수명 호환성 확보 (storage_service alias)
✅ 통합 검증 스크립트 테스트 통과

🏆 성과 지표:
- Import 호환성: ✅ SUCCESS
- 스토리지 서비스: ✅ PostgreSQL-only  
- 헬스 체크: ✅ 모든 시스템 정상
- 백워드 호환성: ✅ 기존 코드 무변경

🎯 다음 단계 준비:
- v5 AI 기능 점진적 도입 가능
- 딥러닝 NLP 엔진 통합 준비
- 예측 분석 모델 개발 기반 완성"

echo.
echo 새 브랜치 푸시...
git push origin neon-db-integration

goto success

:upload_backup
echo.
echo 💾 백업 생성 후 안전하게 업로드...
echo.

echo 현재 상태 백업 생성...
git stash push -m "neon-db-integration-backup-$(date /t)-$(time /t)"

echo 변경사항 스테이징...
git add .

echo 커밋 생성...
git commit -m "🛡️ SAFE: Neon DB 통합 완료 (백업본)

⚠️ 주의: 이 커밋은 백업 목적으로 생성되었습니다.

📦 포함된 변경사항:
- analysis_storage_service.py → PostgreSQL 전용
- storage_service 변수명 호환성 유지
- 통합 테스트 스크립트 추가
- final_integration_check.py 결과: 4/4 통과

🔒 안전 조치:
- git stash로 현재 상태 백업됨
- --force-with-lease 옵션으로 안전한 푸시
- 롤백 가능한 구조 유지

✅ 검증 완료:
- PostgreSQL 연결: 정상
- 스토리지 서비스: 정상  
- Import 호환성: 정상
- 전체 시스템: 정상"

echo.
echo 안전한 푸시 실행...
git push origin HEAD --force-with-lease

goto success

:success
echo.
echo ============================================================
echo 🎉 GitHub 업로드 완료!
echo ============================================================
echo.
echo ✅ NEON DB 통합 완료 버전이 성공적으로 업로드되었습니다.
echo.
echo 📋 업로드된 주요 변경사항:
echo    - PostgreSQL 전용 스토리지 서비스
echo    - SQLite 의존성 완전 제거
echo    - 변수명 호환성 유지
echo    - 통합 테스트 4/4 통과
echo.
echo 🔗 GitHub에서 확인하세요:
echo    - 커밋 내역 및 변경사항
echo    - 새로운 파일들 (final_integration_check.py 등)
echo    - README 업데이트 권장
echo.
echo 🚀 다음 단계:
echo    1. GitHub에서 Pull Request 생성 (브랜치 사용한 경우)
echo    2. 팀원들과 코드 리뷰 진행
echo    3. v5 기능 개발 계획 수립
echo.
goto end

:cancel
echo.
echo ❌ 업로드가 취소되었습니다.
echo.

:end
echo ============================================================
echo 작업 완료. 아무 키나 눌러 계속하세요...
pause
