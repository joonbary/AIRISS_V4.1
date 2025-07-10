Write-Host "AIRISS v5.0 - GitHub Secret Fix" -ForegroundColor Green
Write-Host "=======================================" -ForegroundColor Green

Write-Host "Step 1: Removing problematic files..." -ForegroundColor Yellow
Remove-Item -Path ".env.aws.example" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "start_with_cloud_db.bat" -Force -ErrorAction SilentlyContinue

Write-Host "Step 2: Creating .gitignore..." -ForegroundColor Yellow
$gitignoreContent = @"
# Environment files
.env
.env.*
*.env

# Temporary files
*.tmp
temp/

# Sensitive batch files
start_with_cloud_db.bat

# Node modules
node_modules/

# Python cache
__pycache__/
*.pyc
"@
Set-Content -Path ".gitignore" -Value $gitignoreContent

Write-Host "Step 3: Creating safe template..." -ForegroundColor Yellow
$templateContent = @"
# AIRISS v5.0 Configuration Template
# Copy this file to .env and update with your actual values

PROJECT_NAME=AIRISS v5.0
VERSION=5.0.0
DATABASE_URL=sqlite:///./airiss_v5.db

# OpenAI API Key - Get from https://platform.openai.com/api-keys
OPENAI_API_KEY=your-openai-api-key-here

# AWS S3 Configuration (Optional)
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key

# Other settings
DEBUG=true
LOG_LEVEL=INFO
"@
Set-Content -Path ".env.template" -Value $templateContent

Write-Host "Step 4: Git operations..." -ForegroundColor Yellow
git add .
git commit -m "security: Remove sensitive files and add safe templates"
git push origin HEAD

Write-Host "COMPLETED!" -ForegroundColor Green
Write-Host "Safe templates created and pushed to GitHub." -ForegroundColor Green
