section .text
global main

main:
    push rbp
    mov rbp, rsp
    sub rsp, 32
.L_main_entry:
    mov rax, 1
    mov qword [rbp-8], rax
    mov rax, qword [rbp-8]
    mov qword [rbp-16], rax
    mov rax, qword [rbp-16]
    mov rbx, 0
    cmp rax, rbx
    setg al
    movzx rax, al
    mov qword [rbp-24], rax
    mov rax, qword [rbp-24]
    cmp rax, 0
    je .L_main_else1
    mov rax, 2
    mov qword [rbp-8], rax
    jmp .L_main_endif2
.L_main_else1:
    mov rax, 3
    mov qword [rbp-8], rax
    jmp .L_main_endif2
.L_main_endif2:
    mov rax, qword [rbp-8]
    mov qword [rbp-32], rax
    mov rax, qword [rbp-32]
    jmp .L_main_end
.L_main_end:
    mov rsp, rbp
    pop rbp
    ret
