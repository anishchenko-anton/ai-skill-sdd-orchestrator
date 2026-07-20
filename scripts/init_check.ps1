Write-Host "=================================================="
Write-Host "SDD Orchestrator Environment Init Check" -ForegroundColor Cyan
Write-Host "=================================================="

$projectRoot = Get-Location
$allPassed = $true

function Check-File {
    param ([string]$Path, [string]$Name, [string]$Tip)
    if (Test-Path $Path) {
        Write-Host "[OK] $Name found ($Path)" -ForegroundColor Green
    }
    else {
        Write-Host "[ERROR] $Name NOT FOUND. Expected: $Path" -ForegroundColor Red
        Write-Host "   Hint: $Tip" -ForegroundColor Yellow
        $script:allPassed = $false
    }
}

Write-Host "`n1. Checking global rules (AGENTS.md)..."
Check-File -Path "$projectRoot\.agents\AGENTS.md" -Name "AGENTS.md" -Tip "Create .agents/AGENTS.md"

Write-Host "`n2. Checking system architecture..."
Check-File -Path "$projectRoot\.openspec\system-architecture.md" -Name "system-architecture.md" -Tip "Create .openspec/system-architecture.md"

Write-Host "`n3. Checking dependent skills..."
Check-File -Path "$projectRoot\.agents\skills\frontend-design\SKILL.md" -Name "frontend-design" -Tip "Install frontend-design skill"

Write-Host "`n4. Checking local LLM (Ollama)..."
$ollamaOk = $false
$response = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -Method Get -TimeoutSec 3 -ErrorAction SilentlyContinue
if ($null -ne $response) {
    Write-Host "[OK] Ollama is running." -ForegroundColor Green
    $ollamaOk = $true
}
else {
    Write-Host "[ERROR] Ollama is NOT responding." -ForegroundColor Red
}

Write-Host "`n5. Checking Python (Required for Execution scripts)..."
$pyCheck = python -c "import sys; print('OK')" 2>&1
if ($pyCheck -match "OK") {
    $pyVer = python --version
    Write-Host "[OK] Python is installed ($pyVer)" -ForegroundColor Green
}
else {
    Write-Host "[ERROR] Python is NOT FOUND." -ForegroundColor Red
    $script:allPassed = $false
}

Write-Host "`n=================================================="
if ($allPassed -and $ollamaOk) {
    Write-Host "[SUCCESS] All checks passed! SDD environment is ready." -ForegroundColor Green
}
else {
    Write-Host "[WARNING] Please fix the errors above." -ForegroundColor Yellow
}
Write-Host "=================================================="
