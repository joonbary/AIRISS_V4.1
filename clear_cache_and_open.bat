@echo off
echo Revolutionary 디자인 확인 스크립트
echo =====================================
echo.
echo 1. 브라우저 캐시를 비우고 새로 열기
echo.

REM Chrome 캐시 강제 새로고침
start chrome.exe --disable-application-cache --disable-cache --incognito "http://localhost:8000/airiss/"

echo.
echo Chrome 시크릿 모드로 열렸습니다.
echo.
echo 만약 여전히 변경사항이 안 보이면:
echo 1. Ctrl+Shift+R 을 눌러서 강력 새로고침
echo 2. F12 개발자도구 > Network 탭 > Disable cache 체크
echo.
pause