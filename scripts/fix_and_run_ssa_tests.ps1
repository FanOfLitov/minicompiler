Write-Host "Regenerating SSA expected files..."
py scripts/regenerate_ssa_expected.py
Write-Host "Running SSA tests..."
py -m pytest tests/ssa -v
