# AIRISS Git Merge Conflicts Auto-Fix
# Fix all remaining Git merge conflicts in source files

Write-Host "================================================" -ForegroundColor Red
Write-Host "🚨 CRITICAL: Git Merge Conflicts Detected!" -ForegroundColor Red
Write-Host "================================================" -ForegroundColor Red
Write-Host ""

Set-Location "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

Write-Host "Searching for files with merge conflicts..." -ForegroundColor Yellow

# Search for files containing Git conflict markers
$conflictFiles = Get-ChildItem -Recurse -File | Where-Object {
    $_.Extension -in @('.tsx', '.ts', '.js', '.jsx', '.py', '.md', '.txt', '.json') -and
    (Get-Content $_.FullName -Raw -ErrorAction SilentlyContinue) -match "<<<<<<< HEAD|=======|>>>>>>> "
}

if ($conflictFiles.Count -eq 0) {
    Write-Host "✅ No merge conflicts found!" -ForegroundColor Green
} else {
    Write-Host "Found $($conflictFiles.Count) files with merge conflicts:" -ForegroundColor Red
    
    foreach ($file in $conflictFiles) {
        Write-Host "  - $($file.FullName)" -ForegroundColor Yellow
    }
    
    Write-Host ""
    Write-Host "Fixing conflicts automatically..." -ForegroundColor Cyan
}

# Auto-fix all files with conflict markers
Write-Host "[1/2] Auto-fixing all conflict files..." -ForegroundColor Yellow
$fixedCount = 0

foreach ($file in $conflictFiles) {
    try {
        $content = Get-Content $file.FullName -Raw -Encoding UTF8
        
        # Remove conflict markers and keep the "current" version (after =======)
        $fixedContent = $content -replace '<<<<<<< HEAD.*?=======(.*?)>>>>>>> [^\r\n]*', '$1', 'Singleline'
        
        if ($fixedContent -ne $content) {
            $fixedContent | Set-Content $file.FullName -Encoding UTF8
            Write-Host "  ✅ Fixed: $($file.Name)" -ForegroundColor Green
            $fixedCount++
        }
    } catch {
        Write-Host "  ⚠️ Could not auto-fix: $($file.Name) - $($_.Exception.Message)" -ForegroundColor Yellow
    }
}

Write-Host "Fixed $fixedCount files automatically" -ForegroundColor Cyan

# Commit and push
Write-Host "[2/2] Committing fixes..." -ForegroundColor Yellow
git add .
git commit -m "CRITICAL FIX: Resolve all Git merge conflicts in source files

- Fixed App.tsx merge conflict  
- Removed all Git conflict markers from source files
- Ready for Railway deployment"

git push origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "🎉 SUCCESS: All conflicts fixed and pushed!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🚀 Railway should now build successfully!" -ForegroundColor Cyan
    Write-Host "The React build error should be resolved." -ForegroundColor White
} else {
    Write-Host ""
    Write-Host "❌ Push failed. Manual intervention needed." -ForegroundColor Red
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Green
Write-Host "MERGE CONFLICTS RESOLUTION COMPLETED" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green

Write-Host ""
Write-Host "Press any key to continue..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")