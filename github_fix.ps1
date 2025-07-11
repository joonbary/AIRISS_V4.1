# AIRISS GitHub Upload Fix - PowerShell Script
# Author: AIRISS Team
# Purpose: Fix GitHub upload issues for Railway deployment

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "AIRISS GitHub Upload Fix - PowerShell Edition" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Set location to project directory
Set-Location "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

# Function to check if command succeeded
function Test-LastCommand {
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ SUCCESS" -ForegroundColor Green
        return $true
    } else {
        Write-Host "❌ FAILED" -ForegroundColor Red
        return $false
    }
}

Write-Host "[1/7] Backing up current .gitignore..." -ForegroundColor Yellow
$backupDate = Get-Date -Format "yyyyMMdd_HHmmss"
if (Test-Path ".gitignore") {
    Copy-Item ".gitignore" ".gitignore.backup_$backupDate"
    Write-Host "✅ Backup created: .gitignore.backup_$backupDate" -ForegroundColor Green
}

Write-Host "[2/7] Creating clean .gitignore..." -ForegroundColor Yellow
$gitignoreContent = @"
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual Environments
venv/
venv_*/
venv311/
venv_backup/
venv_new/
env/
ENV/
.venv

# Database files
*.db
*.sqlite
*.sqlite3
airiss.db
airiss_v4.db
*.backup
*_backup*
backup_*/

# Environment variables
.env
.env.local
.env.*.local

# Node.js
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Build outputs
dist/
build/
*.egg-info/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db
*.tmp
*.temp

# AWS and Cloud
.elasticbeanstalk/
.aws/
*.pem
*.key

# Logs
*.log
logs/
log/
pip-log.txt

# Testing
.pytest_cache/
.coverage
htmlcov/

# Jupyter
.ipynb_checkpoints/

# Uploads and temporary
uploads/temp*
test_data/temp*
temp/
tmp/
*.tmp

# Deployment
.vercel
.railway/

# Backup files
cleanup_backup/
"@

$gitignoreContent | Out-File -FilePath ".gitignore" -Encoding UTF8
Test-LastCommand

Write-Host "[3/7] Removing cached files from git..." -ForegroundColor Yellow
try {
    git rm -r --cached . 2>$null
    Write-Host "✅ Git cache cleared" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Some files may not have been cached" -ForegroundColor Yellow
}

Write-Host "[4/7] Adding files with new .gitignore..." -ForegroundColor Yellow
git add .
Test-LastCommand

Write-Host "[5/7] Checking git status..." -ForegroundColor Yellow
git status

Write-Host "[6/7] Committing changes..." -ForegroundColor Yellow
git commit -m "Fix: Resolve gitignore merge conflicts and update ignore rules for Railway deployment"
Test-LastCommand

Write-Host "[7/7] Pushing to GitHub..." -ForegroundColor Yellow
Write-Host "Attempting to push to origin main..." -ForegroundColor Cyan

try {
    git push origin main
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "🎉 SUCCESS: GitHub upload completed successfully!" -ForegroundColor Green
        Write-Host "Repository is now ready for Railway deployment." -ForegroundColor Green
        Write-Host ""
        Write-Host "Next steps:" -ForegroundColor Cyan
        Write-Host "1. Go to Railway.app" -ForegroundColor White
        Write-Host "2. Connect your GitHub repository: https://github.com/joonbary/AIRISS_V4.1" -ForegroundColor White
        Write-Host "3. Deploy your project" -ForegroundColor White
    } else {
        throw "Git push failed"
    }
} catch {
    Write-Host ""
    Write-Host "❌ GitHub push failed. Trying alternative methods..." -ForegroundColor Red
    Write-Host ""
    
    Write-Host "Attempting force push with lease..." -ForegroundColor Yellow
    try {
        git push origin main --force-with-lease
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Force push succeeded!" -ForegroundColor Green
        } else {
            throw "Force push also failed"
        }
    } catch {
        Write-Host ""
        Write-Host "⚠️ Manual intervention required. Possible solutions:" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "1. Check GitHub credentials:" -ForegroundColor White
        Write-Host "   git config --list" -ForegroundColor Gray
        Write-Host ""
        Write-Host "2. Use personal access token instead of password" -ForegroundColor White
        Write-Host ""
        Write-Host "3. Check network connection" -ForegroundColor White
        Write-Host ""
        Write-Host "4. Try manual push:" -ForegroundColor White
        Write-Host "   git push -u origin main" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "Press any key to continue..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")