Write-Host "Rebuilding merge_sort through real array IR pipeline..."
py examples/demo/rebuild_merge_sort_real_pipeline.py

Write-Host ""
Write-Host "Key lines:"
Select-String -Path build/merge_sort.asm -Pattern "extern malloc|call malloc|merge_sort:|merge:|call merge_sort|call merge|copy_temp_back"
