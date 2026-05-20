; Minimal runtime library for Sprint 5.
; NASM syntax, Linux x86-64.
;
; These routines are placeholders for future end-to-end linking.
; Sprint 5 tests focus on generated assembly shape, prologue/epilogue,
; stack slots, function calls, and return values.

section .text
global print_int
global exit

print_int:
    ; Placeholder.
    ret

exit:
    mov rax, 60
    syscall
