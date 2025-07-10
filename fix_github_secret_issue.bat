@echo off
chcp 65001 > nul
echo ===============================================
echo AIRISS v5.0 - GitHub Secret 문제 해결
echo ===============================================
echo.
echo 단계별로 커밋 히스토리를 정리하겠습니다.
echo.
pause

echo 1단계: 현재 상태 확인
echo ===============================================
git status
echo.
pause

echo 2단계: 문제 파일들 커밋 히스토리에서 제거
echo ===============================================
echo 민감한 파일들을 git 히스토리에서 완전히 제거합니다...
echo.

git filter-branch --force --index-filter "git rm --cached --ignore-unmatch .env.aws.example" --prune-empty --tag-name-filter cat -- --all
git filter-branch --force --index-filter "git rm --cached --ignore-unmatch start_with_cloud_db.bat" --prune-empty --tag-name-filter cat -- --all

echo.
echo 3단계: .gitignore 파일 업데이트
echo ===============================================
echo # Environment files > .gitignore
echo .env >> .gitignore
echo .env.* >> .gitignore
echo *.env >> .gitignore
echo.
echo # Batch files with sensitive content >> .gitignore
echo start_with_cloud_db.bat >> .gitignore
echo.

echo 4단계: 새로운 예시 파일 생성 (안전한 버전)
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
echo 5단계: 변경사항 커밋
echo ===============================================
git add .gitignore .env.template
git commit -m "docs: Update configuration template and add gitignore rules"

echo.
echo 6단계: 강제 푸시 준비
echo ===============================================
echo 이제 강제 푸시를 시도합니다...
echo.
git push origin airiss-v5-clean --force

echo.
echo ===============================================
echo 완료! 
echo ===============================================
echo.
echo 만약 여전히 문제가 있다면:
echo 1. GitHub에서 직접 Allow secret 링크를 클릭하세요
echo 2. 또는 새로운 깨끗한 브랜치를 생성하세요
echo.
pause
