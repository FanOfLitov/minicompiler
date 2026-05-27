Write-Host "Sprint 8 full pipeline demo"
New-Item -ItemType Directory -Force -Path build | Out-Null

Write-Host "Input: examples/demo/sprint8_full_pipeline.src"

Write-Host ""
Write-Host "[1] Lexer"
py main.py lex --input examples/demo/sprint8_full_pipeline.src

Write-Host ""
Write-Host "[2] Parser"
py main.py parse --input examples/demo/sprint8_full_pipeline.src --format text

Write-Host ""
Write-Host "[3] Semantic"
py main.py semantic --input examples/demo/sprint8_full_pipeline.src --symbols

Write-Host ""
Write-Host "[4] IR"
py main.py ir --input examples/demo/sprint8_full_pipeline.src

Write-Host ""
Write-Host "[5] SSA"
py main.py ssa --input examples/demo/sprint8_full_pipeline.src

Write-Host ""
Write-Host "[6] ASM"
py main.py asm --input examples/demo/sprint8_full_pipeline.src --output build/sprint8_full_pipeline.asm

Write-Host ""
Write-Host "Assembly saved to build/sprint8_full_pipeline.asm"
