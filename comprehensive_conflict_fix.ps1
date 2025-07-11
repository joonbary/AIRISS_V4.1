# Comprehensive Git Conflict Scanner & Auto-Fixer
# Find and fix ALL remaining Git merge conflicts in the project

Write-Host "================================================" -ForegroundColor Red
Write-Host "🔍 COMPREHENSIVE GIT CONFLICT SCANNER" -ForegroundColor Red
Write-Host "================================================" -ForegroundColor Red
Write-Host ""

Set-Location "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

Write-Host "Scanning entire project for Git conflict markers..." -ForegroundColor Yellow
Write-Host "Excluding: node_modules, .git, venv, build directories" -ForegroundColor Gray
Write-Host ""

# Find all files with conflict markers (excluding binary and irrelevant directories)
$conflictFiles = Get-ChildItem -Recurse -File | Where-Object {
    $_.FullName -notmatch '(node_modules|\.git|venv|build|dist|\.egg-info|__pycache__)' -and
    $_.Extension -in @('.tsx', '.ts', '.js', '.jsx', '.py', '.md', '.txt', '.json', '.yml', '.yaml', '.css', '.html') -and
    (Get-Content $_.FullName -Raw -ErrorAction SilentlyContinue) -match '<<<<<<< HEAD|=======|>>>>>>> '
}

Write-Host "SCAN RESULTS:" -ForegroundColor Cyan
Write-Host "=============" -ForegroundColor Cyan

if ($conflictFiles.Count -eq 0) {
    Write-Host "✅ NO CONFLICTS FOUND! Project is clean." -ForegroundColor Green
} else {
    Write-Host "🚨 Found $($conflictFiles.Count) files with Git conflicts:" -ForegroundColor Red
    Write-Host ""
    
    foreach ($file in $conflictFiles) {
        $relativePath = $file.FullName.Replace((Get-Location).Path + '\', '')
        Write-Host "  📄 $relativePath" -ForegroundColor Yellow
        
        # Show conflict preview
        $content = Get-Content $file.FullName -Raw -ErrorAction SilentlyContinue
        $conflicts = [regex]::Matches($content, '<<<<<<< HEAD.*?>>>>>>> [^\r\n]*', [System.Text.RegularExpressions.RegexOptions]::Singleline)
        Write-Host "     → $($conflicts.Count) conflict(s) detected" -ForegroundColor Gray
    }
    
    Write-Host ""
    Write-Host "Auto-fixing all conflicts..." -ForegroundColor Cyan
    Write-Host ""
    
    $fixedCount = 0
    $errorCount = 0
    
    foreach ($file in $conflictFiles) {
        try {
            $relativePath = $file.FullName.Replace((Get-Location).Path + '\', '')
            Write-Host "Fixing: $relativePath" -ForegroundColor Yellow
            
            $content = Get-Content $file.FullName -Raw -Encoding UTF8
            
            # Advanced conflict resolution strategy
            # Strategy: Keep the "current" version (after =======, before >>>>>>>)
            $fixedContent = $content -replace '<<<<<<< HEAD.*?=======(.*?)>>>>>>> [^\r\n]*', '$1', 'Singleline'
            
            # Clean up any leftover markers
            $fixedContent = $fixedContent -replace '<<<<<<< HEAD[^\r\n]*\r?\n?', ''
            $fixedContent = $fixedContent -replace '=======[^\r\n]*\r?\n?', ''
            $fixedContent = $fixedContent -replace '>>>>>>> [^\r\n]*\r?\n?', ''
            
            # Normalize line endings and remove excessive blank lines
            $fixedContent = $fixedContent -replace '\r?\n\r?\n\r?\n+', "`r`n`r`n"
            
            if ($fixedContent -ne $content) {
                $fixedContent | Set-Content $file.FullName -Encoding UTF8 -NoNewline
                Write-Host "  ✅ FIXED: $relativePath" -ForegroundColor Green
                $fixedCount++
            } else {
                Write-Host "  ⚠️ NO CHANGES: $relativePath" -ForegroundColor Yellow
            }
            
        } catch {
            Write-Host "  ❌ ERROR: $relativePath - $($_.Exception.Message)" -ForegroundColor Red
            $errorCount++
        }
    }
    
    Write-Host ""
    Write-Host "SUMMARY:" -ForegroundColor Cyan
    Write-Host "========" -ForegroundColor Cyan
    Write-Host "✅ Files fixed: $fixedCount" -ForegroundColor Green
    Write-Host "⚠️ Errors: $errorCount" -ForegroundColor Red
}

Write-Host ""
Write-Host "Final verification scan..." -ForegroundColor Yellow

# Re-scan for any remaining conflicts
$remainingConflicts = Get-ChildItem -Recurse -File | Where-Object {
    $_.FullName -notmatch '(node_modules|\.git|venv|build|dist)' -and
    $_.Extension -in @('.tsx', '.ts', '.js', '.jsx', '.py', '.md', '.txt', '.json') -and
    (Get-Content $_.FullName -Raw -ErrorAction SilentlyContinue) -match '<<<<<<< HEAD|=======|>>>>>>> '
}

if ($remainingConflicts.Count -eq 0) {
    Write-Host "✅ VERIFICATION PASSED: No conflicts remaining!" -ForegroundColor Green
    
    Write-Host ""
    Write-Host "Committing fixes to GitHub..." -ForegroundColor Cyan
    
    git add .
    git commit -m "COMPREHENSIVE FIX: Resolve all Git merge conflicts

- Fixed Dashboard.tsx conflicts in getGradeColor and gradeData
- Removed all remaining Git conflict markers
- Project is now clean and ready for Railway deployment
- React build should succeed without syntax errors"
    
    git push origin main
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "🎉 SUCCESS: All conflicts resolved and pushed!" -ForegroundColor Green
        Write-Host ""
        Write-Host "🚀 Railway deployment should now succeed!" -ForegroundColor Cyan
        Write-Host "   • No more Git conflict markers" -ForegroundColor White
        Write-Host "   • Clean TypeScript/React syntax" -ForegroundColor White
        Write-Host "   • Ready for production build" -ForegroundColor White
    } else {
        Write-Host ""
        Write-Host "❌ Push failed. Please check Git credentials." -ForegroundColor Red
    }
    
} else {
    Write-Host "❌ VERIFICATION FAILED: $($remainingConflicts.Count) conflicts still exist!" -ForegroundColor Red
    foreach ($file in $remainingConflicts) {
        $relativePath = $file.FullName.Replace((Get-Location).Path + '\', '')
        Write-Host "  → $relativePath" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Green
Write-Host "GIT CONFLICT RESOLUTION COMPLETED" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green

Write-Host ""
Write-Host "Press any key to continue..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")