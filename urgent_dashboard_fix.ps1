# URGENT: Push Dashboard.tsx fix immediately
Write-Host "🚨 URGENT: Pushing Dashboard.tsx fix to GitHub..." -ForegroundColor Red
Write-Host ""

Set-Location "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

Write-Host "Adding changes..." -ForegroundColor Yellow
git add .

Write-Host "Committing Dashboard.tsx fix..." -ForegroundColor Yellow
git commit -m "URGENT FIX: Resolve Dashboard.tsx Git merge conflicts

- Fixed getGradeColor function conflict (removed <<<<<<< HEAD markers)
- Fixed gradeData array conflict (removed Git conflict markers)
- Dashboard.tsx now has clean TypeScript syntax
- Ready for Railway deployment"

Write-Host "Pushing to GitHub..." -ForegroundColor Yellow
git push origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ SUCCESS: Dashboard.tsx fix pushed!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🚀 Railway should automatically start redeployment" -ForegroundColor Cyan
    Write-Host "🎯 React build should succeed this time!" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Monitor Railway dashboard for build progress..." -ForegroundColor White
} else {
    Write-Host ""
    Write-Host "❌ Push failed. Check your Git credentials." -ForegroundColor Red
}

Write-Host ""
Write-Host "Press any key to continue..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")