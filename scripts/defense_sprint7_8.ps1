Write-Host "============================================================"
Write-Host "MiniCompiler Sprint 7-8 Defense Demo"
Write-Host "============================================================"

New-Item -ItemType Directory -Force -Path build | Out-Null

Write-Host ""
Write-Host "[Sprint 7] Advanced Features"
Write-Host "============================================================"
Write-Host "Goal: arrays helpers, external calls, advanced optimizer passes"
Write-Host ""

Write-Host "Running Sprint 7 tests:"
py -m pytest tests/sprint7 -v

Write-Host ""
Write-Host "[Sprint 7] Optimization demo source"
Write-Host "------------------------------------------------------------"
Get-Content examples/demo/sprint7_optimization_demo.src

Write-Host ""
Write-Host "IR before backend:"
Write-Host "------------------------------------------------------------"
py main.py ir --input examples/demo/sprint7_optimization_demo.src

Write-Host ""
Write-Host "[Sprint 8] Full Pipeline Integration"
Write-Host "============================================================"
Write-Host "Goal: source -> lexer -> parser -> semantic -> IR -> SSA -> ASM"
Write-Host ""

Write-Host "Sprint 8 source:"
Write-Host "------------------------------------------------------------"
Get-Content examples/demo/sprint8_full_pipeline.src

Write-Host ""
Write-Host "Step 1: Lexer"
Write-Host "------------------------------------------------------------"
py main.py lex --input examples/demo/sprint8_full_pipeline.src

Write-Host ""
Write-Host "Step 2: Parser / AST"
Write-Host "------------------------------------------------------------"
py main.py parse --input examples/demo/sprint8_full_pipeline.src --format text

Write-Host ""
Write-Host "Step 3: Semantic Analysis"
Write-Host "------------------------------------------------------------"
py main.py semantic --input examples/demo/sprint8_full_pipeline.src --symbols

Write-Host ""
Write-Host "Step 4: IR"
Write-Host "------------------------------------------------------------"
py main.py ir --input examples/demo/sprint8_full_pipeline.src

Write-Host ""
Write-Host "Step 5: SSA IR"
Write-Host "------------------------------------------------------------"
py main.py ssa --input examples/demo/sprint8_full_pipeline.src

Write-Host ""
Write-Host "Step 6: x86-64 ASM"
Write-Host "------------------------------------------------------------"
py main.py asm --input examples/demo/sprint8_full_pipeline.src --output build/sprint8_full_pipeline.asm

if (Test-Path build/sprint8_full_pipeline.asm) {
    Write-Host ""
    Write-Host "Generated assembly preview:"
    Write-Host "------------------------------------------------------------"
    Get-Content build/sprint8_full_pipeline.asm | Select-Object -First 120
}

Write-Host ""
Write-Host "Sprint 8 tests:"
Write-Host "------------------------------------------------------------"
py -m pytest tests/sprint8 -v

Write-Host ""
Write-Host "SSA tests:"
Write-Host "------------------------------------------------------------"
py -m pytest tests/ssa -v

Write-Host ""
Write-Host "============================================================"
Write-Host "Sprint 7-8 demo completed."
Write-Host "============================================================"
