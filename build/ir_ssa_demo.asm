section .text
global main

add:
    push rbp
    mov rbp, rsp
    sub rsp, 48
    mov qword [rbp-8], rdi
    mov qword [rbp-16], rsi
.L_add_entry:
    mov rax, qword [rbp-8]
    mov qword [rbp-24], rax
    mov rax, qword [rbp-16]
    mov qword [rbp-32], rax
    mov rax, qword [rbp-24]
    mov rbx, qword [rbp-32]
    add rax, rbx
    mov qword [rbp-40], rax
    mov rax, qword [rbp-40]
    jmp .L_add_end
.L_add_end:
    mov rsp, rbp
    pop rbp
    ret

main:
    push rbp
    mov rbp, rsp
    sub rsp, 96
.L_main_entry:
    mov rax, 2
    mov qword [rbp-8], rax
    mov rax, 3
    mov qword [rbp-16], rax
    mov rax, qword [rbp-8]
    mov qword [rbp-32], rax
    mov rax, qword [rbp-16]
    mov qword [rbp-40], rax
    mov rdi, qword [rbp-32]
    mov rsi, qword [rbp-40]
    call add
    mov qword [rbp-48], rax
    mov rax, qword [rbp-48]
    mov qword [rbp-24], rax
    mov rax, qword [rbp-24]
    mov qword [rbp-56], rax
    mov rax, qword [rbp-56]
    mov rbx, 4
    cmp rax, rbx
    setg al
    movzx rax, al
    mov qword [rbp-64], rax
    mov rax, qword [rbp-64]
    cmp rax, 0
    je .L_main_endif2
    mov rax, qword [rbp-24]
    mov qword [rbp-72], rax
    mov rax, qword [rbp-72]
    mov rbx, 1
    add rax, rbx
    mov qword [rbp-80], rax
    mov rax, qword [rbp-80]
    mov qword [rbp-24], rax
    jmp .L_main_endif2
.L_main_endif2:
    mov rax, qword [rbp-24]
    mov qword [rbp-88], rax
    mov rax, qword [rbp-88]
    jmp .L_main_end
.L_main_end:
    mov rsp, rbp
    pop rbp
    ret
