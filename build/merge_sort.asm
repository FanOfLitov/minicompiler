section .text
global main

merge:
    push rbp
    mov rbp, rsp
    sub rsp, 32
    mov qword [rbp-8], rdi
    mov qword [rbp-16], rsi
    mov qword [rbp-24], rdx
    mov qword [rbp-32], rcx
.L_merge_entry:
    jmp .L_merge_end
.L_merge_end:
    mov rsp, rbp
    pop rbp
    ret

merge_sort:
    push rbp
    mov rbp, rsp
    sub rsp, 224
    mov qword [rbp-8], rdi
    mov qword [rbp-16], rsi
    mov qword [rbp-24], rdx
.L_merge_sort_entry:
    mov rax, qword [rbp-16]
    mov qword [rbp-40], rax
    mov rax, qword [rbp-24]
    mov qword [rbp-48], rax
    mov rax, qword [rbp-40]
    mov rbx, qword [rbp-48]
    cmp rax, rbx
    setl al
    movzx rax, al
    mov qword [rbp-56], rax
    mov rax, qword [rbp-56]
    cmp rax, 0
    je .L_merge_sort_endif2
    mov rax, qword [rbp-16]
    mov qword [rbp-64], rax
    mov rax, qword [rbp-24]
    mov qword [rbp-72], rax
    mov rax, qword [rbp-16]
    mov qword [rbp-80], rax
    mov rax, qword [rbp-72]
    mov rbx, qword [rbp-80]
    sub rax, rbx
    mov qword [rbp-88], rax
    mov rax, qword [rbp-88]
    mov rbx, 2
    cqo
    idiv rbx
    mov qword [rbp-96], rax
    mov rax, qword [rbp-64]
    mov rbx, qword [rbp-96]
    add rax, rbx
    mov qword [rbp-104], rax
    mov rax, qword [rbp-104]
    mov qword [rbp-32], rax
    mov rax, qword [rbp-8]
    mov qword [rbp-112], rax
    mov rax, qword [rbp-16]
    mov qword [rbp-120], rax
    mov rax, qword [rbp-32]
    mov qword [rbp-128], rax
    mov rdi, qword [rbp-112]
    mov rsi, qword [rbp-120]
    mov rdx, qword [rbp-128]
    call merge_sort
    mov qword [rbp-136], rax
    mov rax, qword [rbp-8]
    mov qword [rbp-144], rax
    mov rax, qword [rbp-32]
    mov qword [rbp-152], rax
    mov rax, qword [rbp-152]
    mov rbx, 1
    add rax, rbx
    mov qword [rbp-160], rax
    mov rax, qword [rbp-24]
    mov qword [rbp-168], rax
    mov rdi, qword [rbp-144]
    mov rsi, qword [rbp-160]
    mov rdx, qword [rbp-168]
    call merge_sort
    mov qword [rbp-176], rax
    mov rax, qword [rbp-8]
    mov qword [rbp-184], rax
    mov rax, qword [rbp-16]
    mov qword [rbp-192], rax
    mov rax, qword [rbp-32]
    mov qword [rbp-200], rax
    mov rax, qword [rbp-24]
    mov qword [rbp-208], rax
    mov rdi, qword [rbp-184]
    mov rsi, qword [rbp-192]
    mov rdx, qword [rbp-200]
    mov rcx, qword [rbp-208]
    call merge
    mov qword [rbp-216], rax
    jmp .L_merge_sort_endif2
.L_merge_sort_endif2:
    jmp .L_merge_sort_end
.L_merge_sort_end:
    mov rsp, rbp
    pop rbp
    ret

main:
    push rbp
    mov rbp, rsp
    sub rsp, 32
.L_main_entry:
    mov rax, 0
    mov qword [rbp-8], rax
    mov rax, qword [rbp-8]
    mov qword [rbp-16], rax
    mov rdi, qword [rbp-16]
    mov rsi, 0
    mov rdx, 7
    call merge_sort
    mov qword [rbp-24], rax
    mov rax, 0
    jmp .L_main_end
.L_main_end:
    mov rsp, rbp
    pop rbp
    ret
