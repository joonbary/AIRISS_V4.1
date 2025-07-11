# AIRISS Railway Build Fix Script
# Fix frontend build issues for Railway deployment

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "AIRISS Railway Build Fix" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

Set-Location "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

Write-Host "[1/5] Backing up current package.json..." -ForegroundColor Yellow
$backupDate = Get-Date -Format "yyyyMMdd_HHmmss"
Copy-Item "airiss-v4-frontend\package.json" "airiss-v4-frontend\package.json.backup_$backupDate"
Write-Host "✅ Backup created" -ForegroundColor Green

Write-Host "[2/5] Reading current package.json..." -ForegroundColor Yellow
$packageJson = Get-Content "airiss-v4-frontend\package.json" | ConvertFrom-Json

Write-Host "[3/5] Fixing build scripts for Railway..." -ForegroundColor Yellow

# Move cross-env to dependencies and fix build scripts
$packageJson.dependencies."cross-env" = "^7.0.3"
$packageJson.scripts.build = "react-scripts build"
$packageJson.scripts."build:production" = "cross-env NODE_ENV=production DISABLE_ESLINT_PLUGIN=true react-scripts build"

Write-Host "[4/5] Writing fixed package.json..." -ForegroundColor Yellow
$packageJson | ConvertTo-Json -Depth 10 | Set-Content "airiss-v4-frontend\package.json" -Encoding UTF8
Write-Host "✅ package.json updated" -ForegroundColor Green

Write-Host "[5/5] Updating Dockerfile for better compatibility..." -ForegroundColor Yellow

$dockerfileContent = @"
# AIRISS v4.1 Railway Multi-stage Dockerfile - Fixed
# React + FastAPI Complete Integration

# Stage 1: React Frontend Build
FROM node:18-slim as frontend-builder

WORKDIR /app/frontend

# Install Node.js dependencies (production + dev for build)
COPY airiss-v4-frontend/package*.json ./
RUN npm ci

# Copy React source and build
COPY airiss-v4-frontend/ ./
RUN npm run build

# Stage 2: Python FastAPI + React Static Files  
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy React build results
COPY --from=frontend-builder /app/frontend/build ./static

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create database directory
RUN mkdir -p /app/data

# Environment variables
ENV PYTHONPATH=/app
ENV DATABASE_URL=sqlite:///data/airiss.db
ENV SERVER_HOST=0.0.0.0
ENV REACT_BUILD_PATH=/app/static
ENV NODE_ENV=production
ENV DISABLE_ESLINT_PLUGIN=true

# Health check for Railway
HEALTHCHECK --interval=30s --timeout=30s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:`${PORT:-8002}/health || exit 1

# Railway dynamic port support
CMD ["sh", "-c", "python -m uvicorn app.main:app --host 0.0.0.0 --port `${PORT:-8002}"]
"@

$dockerfileContent | Set-Content "Dockerfile" -Encoding UTF8
Write-Host "✅ Dockerfile updated" -ForegroundColor Green

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "BUILD FIX COMPLETED" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Changes made:" -ForegroundColor Green
Write-Host "✅ Moved cross-env to dependencies" -ForegroundColor White
Write-Host "✅ Fixed build scripts for Railway" -ForegroundColor White  
Write-Host "✅ Updated Dockerfile for better compatibility" -ForegroundColor White
Write-Host "✅ Added environment variables for ESLint" -ForegroundColor White
Write-Host ""

Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Commit and push changes to GitHub" -ForegroundColor White
Write-Host "2. Redeploy on Railway" -ForegroundColor White
Write-Host ""

# Commit and push automatically
Write-Host "Auto-committing changes..." -ForegroundColor Yellow
git add .
git commit -m "Fix: Update frontend build configuration for Railway deployment"
git push origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Changes pushed to GitHub successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🚀 Ready for Railway deployment!" -ForegroundColor Cyan
    Write-Host "Go to Railway and redeploy your project." -ForegroundColor White
} else {
    Write-Host "⚠️ Manual push required:" -ForegroundColor Yellow
    Write-Host "git add ." -ForegroundColor Gray
    Write-Host "git commit -m 'Fix: Update frontend build configuration for Railway'" -ForegroundColor Gray
    Write-Host "git push origin main" -ForegroundColor Gray
}

Write-Host ""
Write-Host "Press any key to continue..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")