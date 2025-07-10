@echo off
chcp 65001 > nul
echo 🎯 AIRISS v4.1 Python 3.13 호환 모드 실행
echo ====================================================
echo.
echo 📝 변경사항:
echo   - SQLAlchemy 호환성 문제 해결
echo   - 데이터베이스 기능 조건부 활성화
echo   - 핵심 분석 기능은 모두 작동
echo.

cd /d "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

echo 📍 현재 디렉토리: %CD%
echo 🐍 Python 버전 확인:
python --version
echo.

echo 🚀 AIRISS 서버 시작...
echo 📱 브라우저에서 http://localhost:8002 접속하세요
echo 🛑 서버 종료: Ctrl+C
echo.
echo ===============================================
echo 핵심 기능 (항상 작동):
echo   ✅ 파일 업로드
echo   ✅ 텍스트 분석
echo   ✅ 정량 분석
echo   ✅ 하이브리드 스코어링
echo   ✅ 편향 탐지
echo.
echo 추가 기능 (Python 3.13에서 조건부):
echo   ❓ 데이터베이스 저장 (SQLAlchemy 의존)
echo   ❓ 분석 이력 관리
echo ===============================================
echo.

python app\main.py

pause
