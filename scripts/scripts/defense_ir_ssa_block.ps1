Write-Host "============================================================"
Write-Host "[Sprint 4] IR and SSA Intermediate Representation"
Write-Host "============================================================"

Write-Host ""
Write-Host "Source:"
Get-Content examples/demo/ir_ssa_demo.src

Write-Host ""
Write-Host "Normal IR:"
py main.py ir --input examples/demo/ir_ssa_demo.src

Write-Host ""
Write-Host "SSA IR:"
py main.py ssa --input examples/demo/ir_ssa_demo.src

Write-Host ""
Write-Host "ASM only after IR/SSA:"
New-Item -ItemType Directory -Force -Path build | Out-Null
py main.py asm --input examples/demo/ir_ssa_demo.src --output build/ir_ssa_demo.asm