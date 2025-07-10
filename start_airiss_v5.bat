@echo off
REM ===============================================
REM AIRISS v5.0 - 인코딩 문제 해결 버전
REM ===============================================

REM UTF-8 코드페이지 설정
chcp 65001 > nul 2>&1

REM 인코딩 환경 변수 설정
set PYTHONIOENCODING=utf-8
set PYTHONPATH=%CD%
set LANG=ko_KR.UTF-8

echo ===============================================
echo AIRISS v5.0 - 인코딩 안전 시작
echo ===============================================
echo.

echo 환경 설정 완료...
echo 현재 디렉토리: %CD%
echo 인코딩: UTF-8
echo.

REM .env 파일 확인
if not exist .env (
    echo .env 파일 생성 중...
    if exist .env.template (
        copy .env.template .env > nul
        echo .env 파일 생성 완료
    )
)

echo AIRISS v5.0 시작 중...
echo 접속: http://localhost:8002
echo 종료: Ctrl+C
echo.

REM uvicorn 실행 (인코딩 안전)
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload

REM 실패 시 Python 모듈 방식으로 재시도
if errorlevel 1 (
    echo.
    echo uvicorn 직접 실행 실패. Python 모듈 방식으로 재시도...
    python -m uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
)
