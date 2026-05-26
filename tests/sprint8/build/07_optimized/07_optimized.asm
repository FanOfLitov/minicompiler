section .text
global main

main:
    push rbp
    mov rbp, rsp
    sub rsp, 32
.L_main_entry:
    mov rax, 5
    mov qword [rbp-16], rax
    mov rax, qword [rbp-16]
    mov qword [rbp-8], rax
    mov rax, qword [rbp-8]
    mov qword [rbp-24], rax
    mov rax, qword [rbp-24]
    jmp .L_main_end
.L_main_end:
    mov rsp, rbp
    pop rbp
    ret
