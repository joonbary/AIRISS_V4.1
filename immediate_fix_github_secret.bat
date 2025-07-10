@echo off
chcp 65001 > nul
echo ===============================================
echo AIRISS v5.0 - 즉시 GitHub Secret 해결
echo ===============================================
echo.

echo 현재 상태 확인 중...
git status
echo.

echo 1단계: 즉시 .gitignore 업데이트
echo ===============================================
(
echo # Environment files
echo .env
echo .env.*
echo *.env
echo.
echo # Temporary files
echo *.tmp
echo temp/
echo.
echo # Sensitive batch files
echo start_with_cloud_db.bat
echo.
echo # Node modules
echo node_modules/
echo.
echo # Python cache
echo __pycache__/
echo *.pyc
echo.
) > .gitignore

echo 2단계: 문제 파일들 제거
echo ===============================================
if exist .env.aws.example del .env.aws.example
if exist start_with_cloud_db.bat del start_with_cloud_db.bat
echo 문제 파일들이 제거되었습니다.

echo.
echo 3단계: 안전한 템플릿 생성
echo ===============================================
(
echo # AIRISS v5.0 Configuration Template
echo # Copy this file to .env and update with your actual values
echo.
echo PROJECT_NAME=AIRISS v5.0
echo VERSION=5.0.0
echo DATABASE_URL=sqlite:///./airiss_v5.db
echo.
echo # OpenAI API Key - Get from https://platform.openai.com/api-keys
echo OPENAI_API_KEY=your-openai-api-key-here
echo.
echo # AWS S3 Configuration ^(Optional^)
echo AWS_ACCESS_KEY_ID=your-aws-access-key
echo AWS_SECRET_ACCESS_KEY=your-aws-secret-key
echo.
echo # Other settings
echo DEBUG=true
echo LOG_LEVEL=INFO
) > .env.template

echo.
echo 4단계: README 업데이트
echo ===============================================
(
echo # AIRISS v5.0 Setup Guide
echo.
echo ## Environment Setup
echo 1. Copy `.env.template` to `.env`
echo 2. Update the values in `.env` with your actual API keys
echo 3. Never commit `.env` files to version control
echo.
echo ## Required API Keys
echo - OpenAI API Key: Required for AI analysis
echo - AWS Keys: Optional, for cloud storage
echo.
) > SETUP_GUIDE.md

echo.
echo 5단계: 모든 변경사항 스테이징
echo ===============================================
git add .
git status

echo.
echo 6단계: 새로운 커밋 생성
echo ===============================================
git commit -m "security: Remove sensitive files and add safe templates

- Removed .env.aws.example and start_with_cloud_db.bat
- Added .env.template with safe placeholder values
- Updated .gitignore to prevent future issues
- Added setup guide for environment configuration"

echo.
echo 7단계: 현재 리모트 확인
echo ===============================================
git remote -v

echo.
echo 8단계: 푸시 시도
echo ===============================================
echo 안전한 커밋으로 푸시를 시도합니다...
git push origin HEAD

echo.
echo ===============================================
echo 완료!
echo ===============================================
echo 민감한 정보가 제거되고 안전한 템플릿이 생성되었습니다.
echo.
pause
