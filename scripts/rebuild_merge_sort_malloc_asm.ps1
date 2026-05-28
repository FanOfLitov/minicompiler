Write-Host "Rebuilding merge_sort.asm with malloc-based dynamic array allocation..."
New-Item -ItemType Directory -Force -Path build | Out-Null

py examples/demo/rebuild_merge_sort_malloc_asm.py

Write-Host ""
Write-Host "Check generated ASM:"
Write-Host "build/merge_sort.asm"
Write-Host ""
Write-Host "Important lines:"
Select-String -Path build/merge_sort.asm -Pattern "extern malloc|call malloc|mov rdi|values pointer|rbx\+"
