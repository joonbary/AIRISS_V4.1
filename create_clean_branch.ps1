Write-Host "Creating clean branch without sensitive history..." -ForegroundColor Green

Write-Host "Step 1: Create orphan branch" -ForegroundColor Yellow
git checkout --orphan clean-v5-final

Write-Host "Step 2: Remove all staged files" -ForegroundColor Yellow
git rm -rf . 2>$null

Write-Host "Step 3: Create .gitignore" -ForegroundColor Yellow
@"
.env
.env.*
*.env
__pycache__/
*.pyc
*.tmp
temp/
node_modules/
.vscode/
.idea/
"@ | Out-File -FilePath ".gitignore" -Encoding UTF8

Write-Host "Step 4: Copy essential files only" -ForegroundColor Yellow
# Copy directories
if (Test-Path "../app") { Copy-Item -Path "../app" -Destination "./app" -Recurse -Force }
if (Test-Path "../static") { Copy-Item -Path "../static" -Destination "./static" -Recurse -Force }
if (Test-Path "../templates") { Copy-Item -Path "../templates" -Destination "./templates" -Recurse -Force }

# Copy files
if (Test-Path "../requirements.txt") { Copy-Item -Path "../requirements.txt" -Destination "./requirements.txt" -Force }
if (Test-Path "../README.md") { Copy-Item -Path "../README.md" -Destination "./README.md" -Force }
if (Test-Path "../main.py") { Copy-Item -Path "../main.py" -Destination "./main.py" -Force }

Write-Host "Step 5: Create safe template" -ForegroundColor Yellow
@"
# AIRISS v5.0 Configuration Template
PROJECT_NAME=AIRISS v5.0
VERSION=5.0.0
DATABASE_URL=sqlite:///./airiss_v5.db

# OpenAI API Key
OPENAI_API_KEY=your-openai-api-key-here

# AWS Configuration
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
"@ | Out-File -FilePath ".env.template" -Encoding UTF8

Write-Host "Step 6: Commit clean version" -ForegroundColor Yellow
git add .
git commit -m "Clean AIRISS v5.0 - no sensitive data in history"

Write-Host "Step 7: Push clean branch" -ForegroundColor Yellow
git push origin clean-v5-final

Write-Host "SUCCESS! Clean branch created: clean-v5-final" -ForegroundColor Green
Write-Host "This branch has no commit history with sensitive information." -ForegroundColor Green
