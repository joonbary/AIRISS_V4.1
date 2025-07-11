# CRITICAL: Push core file fixes immediately
Write-Host "🚨 CRITICAL: Pushing core file fixes to GitHub..." -ForegroundColor Red
Write-Host ""

Set-Location "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

Write-Host "Adding critical file changes..." -ForegroundColor Yellow
git add airiss-v4-frontend/src/services/api.ts
git add airiss-v4-frontend/src/services/websocket.ts  
git add requirements.txt

Write-Host "Committing critical fixes..." -ForegroundColor Yellow
git commit -m "CRITICAL FIX: Resolve Git conflicts in core files

✅ Fixed api.ts:
  - Removed API_BASE_URL conflict (Railway compatibility)
  - Removed auth functions conflict
  
✅ Fixed websocket.ts:
  - Removed JSON stringify indentation conflict
  - Removed return statement conflict
  
✅ Fixed requirements.txt:
  - Removed PostgreSQL drivers conflict
  
🚀 Core frontend services and backend dependencies now clean
🎯 Railway build should succeed with React compilation"

Write-Host "Pushing to GitHub..." -ForegroundColor Yellow
git push origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "🎉 SUCCESS: Critical fixes pushed to GitHub!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🚀 Railway automatic redeployment starting..." -ForegroundColor Cyan
    Write-Host "🎯 React build should now succeed!" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Fixed the most important conflicts:" -ForegroundColor White
    Write-Host "• Frontend API services (api.ts)" -ForegroundColor Gray
    Write-Host "• WebSocket services (websocket.ts)" -ForegroundColor Gray  
    Write-Host "• Python dependencies (requirements.txt)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Monitor Railway dashboard for deployment progress..." -ForegroundColor Yellow
} else {
    Write-Host ""
    Write-Host "❌ Push failed. Check your Git credentials." -ForegroundColor Red
}

Write-Host ""
Write-Host "Press any key to continue..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")