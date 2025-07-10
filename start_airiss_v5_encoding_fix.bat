@echo off
REM UTF-8 코드페이지 설정
chcp 65001 > nul 2>&1

echo ===============================================
echo AIRISS v5.0 - 인코딩 문제 해결 버전
echo ===============================================
echo.

REM 인코딩 환경 변수 설정
set PYTHONIOENCODING=utf-8
set PYTHONPATH=%CD%
set LANG=ko_KR.UTF-8
set LC_ALL=ko_KR.UTF-8

echo 인코딩 설정 완료...
echo 현재 디렉토리: %CD%
echo Python 경로: %PYTHONPATH%
echo 인코딩: %PYTHONIOENCODING%
echo.

REM 코드페이지 확인
echo 현재 코드페이지:
chcp
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

REM Python 실행 (인코딩 안전 모드)
python -X utf8 -c "
import sys
import os
sys.path.insert(0, os.getcwd())
print('Python 인코딩 설정 완료')
print('기본 인코딩:', sys.getdefaultencoding())
print('파일시스템 인코딩:', sys.getfilesystemencoding())
"

echo.
echo uvicorn 실행 중...
python -X utf8 -m uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
