Write-Host "=================================================="
Write-Host "🚀 Инициализация SDD Orchestrator Environment" -ForegroundColor Cyan
Write-Host "=================================================="

$projectRoot = Get-Location
$allPassed = $true

function Check-File {
    param ([string]$Path, [string]$Name, [string]$Tip)
    
    if (Test-Path $Path) {
        Write-Host "✅ $Name найден ($Path)" -ForegroundColor Green
    } else {
        Write-Host "❌ $Name НЕ НАЙДЕН. Ожидаемый путь: $Path" -ForegroundColor Red
        Write-Host "   💡 Подсказка: $Tip" -ForegroundColor Yellow
        $script:allPassed = $false
    }
}

Write-Host "`n1. Проверка глобальных правил (AGENTS.md)..."
Check-File -Path "$projectRoot\.agents\AGENTS.md" -Name "AGENTS.md" -Tip "Создайте папку .agents и файл AGENTS.md с глобальными правилами для ИИ."

Write-Host "`n2. Проверка системной архитектуры..."
Check-File -Path "$projectRoot\.openspec\system-architecture.md" -Name "system-architecture.md" -Tip "Создайте папку .openspec и опишите стек технологий в system-architecture.md до начала разработки."

Write-Host "`n3. Проверка зависимых скиллов (frontend-design)..."
Check-File -Path "$projectRoot\.agents\skills\frontend-design\SKILL.md" -Name "Скилл frontend-design" -Tip "Для работы UI-Designer установите скилл (см. README.md)."

Write-Host "`n4. Проверка локальных LLM (Ollama)..."
$ollamaOk = $false
try {
    $response = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -Method Get -TimeoutSec 3 -ErrorAction Stop
    $models = $response.models | Select-Object -ExpandProperty name
    Write-Host "✅ Ollama работает. Найдено моделей: $($models.Count)" -ForegroundColor Green
    if ($models.Count -gt 0) {
        $displayModels = $models | Select-Object -First 3
        $suffix = if ($models.Count -gt 3) { "..." } else { "" }
        Write-Host "   Доступные модели: $([string]::Join(', ', $displayModels))$suffix" -ForegroundColor Green
        $ollamaOk = $true
    } else {
        Write-Host "   ⚠️ Внимание: В Ollama нет скачанных моделей. Запустите 'ollama pull <model_name>'" -ForegroundColor Yellow
        $ollamaOk = $true # Сервер все же работает
    }
} catch {
    Write-Host "❌ Ollama НЕ ОТВЕЧАЕТ на http://localhost:11434. Проверьте, что сервер запущен." -ForegroundColor Red
}

Write-Host "`n=================================================="
if ($allPassed -and $ollamaOk) {
    Write-Host "🎉 ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ! Ваша SDD-среда готова к работе." -ForegroundColor Green
    Write-Host "   Вы можете написать Оркестратору в чат: 'Спроектируй первый модуль'." -ForegroundColor Green
} else {
    Write-Host "⚠️ ЕСТЬ ЗАМЕЧАНИЯ. Пожалуйста, исправьте ошибки выше перед началом работы, чтобы агенты не галлюцинировали." -ForegroundColor Yellow
}
Write-Host "=================================================="
