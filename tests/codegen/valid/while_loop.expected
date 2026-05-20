section .text
global main

main:
    push rbp
    mov rbp, rsp
    sub rsp, 48
.L_main_entry:
    mov rax, 0
    mov qword [rbp-8], rax
    jmp .L_main_while1
.L_main_while1:
    mov rax, qword [rbp-8]
    mov qword [rbp-16], rax
    mov rax, qword [rbp-16]
    mov rbx, 3
    cmp rax, rbx
    setl al
    movzx rax, al
    mov qword [rbp-24], rax
    mov rax, qword [rbp-24]
    cmp rax, 0
    je .L_main_while_end3
.L_main_while_body2:
    mov rax, qword [rbp-8]
    mov qword [rbp-32], rax
    mov rax, qword [rbp-32]
    mov rbx, 1
    add rax, rbx
    mov qword [rbp-40], rax
    mov rax, qword [rbp-40]
    mov qword [rbp-8], rax
    jmp .L_main_while1
.L_main_while_end3:
    mov rax, qword [rbp-8]
    mov qword [rbp-48], rax
    mov rax, qword [rbp-48]
    jmp .L_main_end
.L_main_end:
    mov rsp, rbp
    pop rbp
    ret
