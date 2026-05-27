section .text
global main

factorial:
    push rbp
    mov rbp, rsp
    sub rsp, 64
    mov qword [rbp-8], rdi
.L_factorial_entry:
    mov rax, qword [rbp-8]
    mov qword [rbp-16], rax
    mov rax, qword [rbp-16]
    mov rbx, 1
    cmp rax, rbx
    setle al
    movzx rax, al
    mov qword [rbp-24], rax
    mov rax, qword [rbp-24]
    cmp rax, 0
    je .L_factorial_endif2
    mov rax, 1
    jmp .L_factorial_end
    jmp .L_factorial_endif2
.L_factorial_endif2:
    mov rax, qword [rbp-8]
    mov qword [rbp-32], rax
    mov rax, qword [rbp-8]
    mov qword [rbp-40], rax
    mov rax, qword [rbp-40]
    mov rbx, 1
    sub rax, rbx
    mov qword [rbp-48], rax
    mov rdi, qword [rbp-48]
    call factorial
    mov qword [rbp-56], rax
    mov rax, qword [rbp-32]
    mov rbx, qword [rbp-56]
    imul rax, rbx
    mov qword [rbp-64], rax
    mov rax, qword [rbp-64]
    jmp .L_factorial_end
.L_factorial_end:
    mov rsp, rbp
    pop rbp
    ret

main:
    push rbp
    mov rbp, rsp
    sub rsp, 32
.L_main_entry:
    mov rdi, 5
    call factorial
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
