REM AIRISS v4.1 - 정적파일 404 해결 배포
REM React 정적파일을 루트 경로에서 직접 서빙하도록 수정

echo 🔧 Git 변경사항 커밋 및 푸시...

git add app/main.py
git commit -m "Fix React static files 404: Mount React build to root path"
git push origin main

echo ✅ Railway 재배포 시작됨!
echo 🌐 배포 확인 URL: https://web-production-4066.up.railway.app/

pause
