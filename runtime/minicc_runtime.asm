; Sprint 8 minimal runtime.
; NASM x86-64, Linux System V.

section .text
global _minicc_exit

_minicc_exit:
    mov rax, 60
    syscall
