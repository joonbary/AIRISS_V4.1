# Quick fix and push for merge conflicts
Write-Host "🚨 EMERGENCY FIX: Pushing merge conflict resolution..." -ForegroundColor Red
Write-Host ""

Set-Location "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

Write-Host "Adding all changes..." -ForegroundColor Yellow
git add .

Write-Host "Committing critical fix..." -ForegroundColor Yellow
git commit -m "CRITICAL FIX: Resolve Git merge conflicts in App.tsx

- Fixed React import syntax errors
- Removed Git conflict markers (<<<<<<< HEAD, =======, >>>>>>>)
- App.tsx now has clean, valid TypeScript code
- Ready for Railway deployment"

Write-Host "Pushing to GitHub..." -ForegroundColor Yellow
git push origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ SUCCESS: Critical fix pushed to GitHub!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🎯 Railway will now rebuild automatically" -ForegroundColor Cyan
    Write-Host "🎯 React build should succeed this time!" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Monitor Railway dashboard for deployment progress..." -ForegroundColor White
} else {
    Write-Host ""
    Write-Host "❌ Push failed. Check your Git credentials." -ForegroundColor Red
}

Write-Host ""
Write-Host "Press any key to continue..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")