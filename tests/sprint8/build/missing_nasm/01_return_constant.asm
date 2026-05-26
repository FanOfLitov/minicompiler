section .text
global main

main:
    push rbp
    mov rbp, rsp
.L_main_entry:
    mov rax, 42
    jmp .L_main_end
.L_main_end:
    mov rsp, rbp
    pop rbp
    ret
