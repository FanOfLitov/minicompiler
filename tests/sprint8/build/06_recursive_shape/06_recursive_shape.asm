section .text
global main

countdown:
    push rbp
    mov rbp, rsp
    sub rsp, 48
    mov qword [rbp-8], rdi
.L_countdown_entry:
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
    je .L_countdown_endif2
    mov rax, qword [rbp-8]
    mov qword [rbp-32], rax
    mov rax, qword [rbp-32]
    mov rbx, 1
    sub rax, rbx
    mov qword [rbp-40], rax
    mov rdi, qword [rbp-40]
    call countdown
    mov qword [rbp-48], rax
    mov rax, qword [rbp-48]
    jmp .L_countdown_end
    jmp .L_countdown_endif2
.L_countdown_endif2:
    mov rax, 0
    jmp .L_countdown_end
.L_countdown_end:
    mov rsp, rbp
    pop rbp
    ret

main:
    push rbp
    mov rbp, rsp
    sub rsp, 16
.L_main_entry:
    mov rdi, 3
    call countdown
    mov qword [rbp-8], rax
    mov rax, qword [rbp-8]
    jmp .L_main_end
.L_main_end:
    mov rsp, rbp
    pop rbp
    ret
