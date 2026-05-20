section .text
global main

main:
    push rbp
    mov rbp, rsp
    sub rsp, 32
.L_main_entry:
    mov rax, 3
    mov rbx, 4
    imul rax, rbx
    mov qword [rbp-16], rax
    mov rax, 2
    mov rbx, qword [rbp-16]
    add rax, rbx
    mov qword [rbp-24], rax
    mov rax, qword [rbp-24]
    mov qword [rbp-8], rax
    mov rax, qword [rbp-8]
    mov qword [rbp-32], rax
    mov rax, qword [rbp-32]
    jmp .L_main_end
.L_main_end:
    mov rsp, rbp
    pop rbp
    ret
