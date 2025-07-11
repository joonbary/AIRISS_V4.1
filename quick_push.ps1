# Quick GitHub Push for Railway Build Fix
Write-Host "🚀 Pushing Railway build fixes to GitHub..." -ForegroundColor Cyan
Write-Host ""

Set-Location "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

Write-Host "Adding changes..." -ForegroundColor Yellow
git add .

Write-Host "Committing..." -ForegroundColor Yellow
git commit -m "Fix: Update frontend build configuration for Railway deployment

- Move cross-env to dependencies in package.json
- Update Dockerfile with better environment variables
- Fix build scripts for Railway compatibility"

Write-Host "Pushing to GitHub..." -ForegroundColor Yellow
git push origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ SUCCESS: Changes pushed to GitHub!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🎯 Next Steps:" -ForegroundColor Cyan
    Write-Host "1. Go to Railway dashboard" -ForegroundColor White
    Write-Host "2. Your project should automatically redeploy" -ForegroundColor White
    Write-Host "3. The frontend build should now succeed!" -ForegroundColor White
} else {
    Write-Host ""
    Write-Host "❌ Push failed. Manual intervention needed." -ForegroundColor Red
}

Write-Host ""
Write-Host "Press any key to continue..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")