@echo off
chcp 65001 > nul
echo ===============================================
echo AIRISS v5.0 - 간단한 GitHub Secret 문제 해결
echo ===============================================
echo.
echo 새로운 깨끗한 브랜치로 문제를 해결하겠습니다.
echo.
pause

echo 1단계: 현재 브랜치 확인
echo ===============================================
git branch -a
echo.
pause

echo 2단계: 문제 파일들 .gitignore에 추가
echo ===============================================
echo # Environment files > .gitignore
echo .env >> .gitignore
echo .env.* >> .gitignore
echo *.env >> .gitignore
echo.
echo # Temporary files >> .gitignore
echo *.tmp >> .gitignore
echo temp/ >> .gitignore
echo.

echo 3단계: 문제 파일들 삭제
echo ===============================================
del .env.aws.example
del start_with_cloud_db.bat
echo 문제 파일들이 삭제되었습니다.
echo.

echo 4단계: 안전한 템플릿 파일 생성
echo ===============================================
echo # AIRISS v4.0 Configuration Template > .env.template
echo PROJECT_NAME=AIRISS v4.0 > .env.template
echo VERSION=4.0.0 >> .env.template
echo DATABASE_URL=sqlite:///./airiss_v4.db >> .env.template
echo. >> .env.template
echo # OpenAI API Key - Replace with your actual key >> .env.template
echo OPENAI_API_KEY=your-openai-api-key-here >> .env.template
echo. >> .env.template
echo # AWS S3 Configuration >> .env.template
echo AWS_ACCESS_KEY_ID=your-aws-access-key >> .env.template
echo AWS_SECRET_ACCESS_KEY=your-aws-secret-key >> .env.template

echo.
echo 5단계: 새로운 브랜치 생성
echo ===============================================
git checkout -b v5-clean-release
echo.

echo 6단계: 변경사항 커밋
echo ===============================================
git add .
git commit -m "feat: Clean release for v5.0 - removed sensitive files and added templates"

echo.
echo 7단계: 새로운 브랜치 푸시
echo ===============================================
git push origin v5-clean-release

echo.
echo ===============================================
echo 완료! 
echo ===============================================
echo.
echo 새로운 브랜치 v5-clean-release가 생성되었습니다.
echo 이 브랜치는 민감한 정보가 제거된 깨끗한 상태입니다.
echo.
pause
