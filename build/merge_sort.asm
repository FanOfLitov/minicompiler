section .text
extern malloc
global main

main:
    push rbp
    mov rbp, rsp
    sub rsp, 32

    ; heap_size1 = 8 * 8 = 64
    ; dynamic array allocation for values
    mov rdi, 64
    call malloc
    mov qword [rbp-8], rax    ; values pointer

    ; values[0] = 8
    mov rbx, qword [rbp-8]
    mov qword [rbx+0], 8

    ; values[1] = 3
    mov rbx, qword [rbp-8]
    mov qword [rbx+8], 3

    ; values[2] = 5
    mov rbx, qword [rbp-8]
    mov qword [rbx+16], 5

    ; values[3] = 1
    mov rbx, qword [rbp-8]
    mov qword [rbx+24], 1

    ; values[4] = 9
    mov rbx, qword [rbp-8]
    mov qword [rbx+32], 9

    ; values[5] = 2
    mov rbx, qword [rbp-8]
    mov qword [rbx+40], 2

    ; values[6] = 7
    mov rbx, qword [rbp-8]
    mov qword [rbx+48], 7

    ; values[7] = 4
    mov rbx, qword [rbp-8]
    mov qword [rbx+56], 4

    ; merge_sort(values, 0, 7)
    mov rdi, qword [rbp-8]
    mov rsi, 0
    mov rdx, 7
    call merge_sort

    mov rax, 0
    mov rsp, rbp
    pop rbp
    ret

merge_sort:
    push rbp
    mov rbp, rsp
    sub rsp, 64

    mov qword [rbp-8], rdi     ; arr
    mov qword [rbp-16], rsi    ; left
    mov qword [rbp-24], rdx    ; right

    mov rax, qword [rbp-16]
    cmp rax, qword [rbp-24]
    jge .merge_sort_end

    mov rax, qword [rbp-24]
    sub rax, qword [rbp-16]
    cqo
    mov rbx, 2
    idiv rbx
    add rax, qword [rbp-16]
    mov qword [rbp-32], rax    ; mid

    mov rdi, qword [rbp-8]
    mov rsi, qword [rbp-16]
    mov rdx, qword [rbp-32]
    call merge_sort

    mov rdi, qword [rbp-8]
    mov rax, qword [rbp-32]
    add rax, 1
    mov rsi, rax
    mov rdx, qword [rbp-24]
    call merge_sort

    mov rdi, qword [rbp-8]
    mov rsi, qword [rbp-16]
    mov rdx, qword [rbp-32]
    mov rcx, qword [rbp-24]
    call merge

.merge_sort_end:
    mov rsp, rbp
    pop rbp
    ret

merge:
    push rbp
    mov rbp, rsp
    sub rsp, 112

    mov qword [rbp-8], rdi      ; arr
    mov qword [rbp-16], rsi     ; left
    mov qword [rbp-24], rdx     ; mid
    mov qword [rbp-32], rcx     ; right

    ; temp buffer for merge
    mov rdi, 64
    call malloc
    mov qword [rbp-40], rax     ; temp pointer

    mov rax, qword [rbp-16]
    mov qword [rbp-48], rax     ; i

    mov rax, qword [rbp-24]
    add rax, 1
    mov qword [rbp-56], rax     ; j

    mov qword [rbp-64], 0       ; k

.merge_loop:
    mov rax, qword [rbp-48]
    cmp rax, qword [rbp-24]
    jg .copy_left_remaining

    mov rax, qword [rbp-56]
    cmp rax, qword [rbp-32]
    jg .copy_left_remaining

    mov rbx, qword [rbp-8]
    mov rax, qword [rbp-48]
    imul rax, 8
    mov r10, qword [rbx+rax]

    mov rbx, qword [rbp-8]
    mov rax, qword [rbp-56]
    imul rax, 8
    mov r11, qword [rbx+rax]

    cmp r10, r11
    jle .take_left

.take_right:
    mov rbx, qword [rbp-40]
    mov rax, qword [rbp-64]
    imul rax, 8
    mov qword [rbx+rax], r11
    mov rax, qword [rbp-56]
    add rax, 1
    mov qword [rbp-56], rax
    jmp .inc_k

.take_left:
    mov rbx, qword [rbp-40]
    mov rax, qword [rbp-64]
    imul rax, 8
    mov qword [rbx+rax], r10
    mov rax, qword [rbp-48]
    add rax, 1
    mov qword [rbp-48], rax

.inc_k:
    mov rax, qword [rbp-64]
    add rax, 1
    mov qword [rbp-64], rax
    jmp .merge_loop

.copy_left_remaining:
    mov rax, qword [rbp-48]
    cmp rax, qword [rbp-24]
    jg .copy_right_remaining
    mov rbx, qword [rbp-8]
    mov rax, qword [rbp-48]
    imul rax, 8
    mov r10, qword [rbx+rax]
    mov rbx, qword [rbp-40]
    mov rax, qword [rbp-64]
    imul rax, 8
    mov qword [rbx+rax], r10
    mov rax, qword [rbp-48]
    add rax, 1
    mov qword [rbp-48], rax
    mov rax, qword [rbp-64]
    add rax, 1
    mov qword [rbp-64], rax
    jmp .copy_left_remaining

.copy_right_remaining:
    mov rax, qword [rbp-56]
    cmp rax, qword [rbp-32]
    jg .copy_temp_back
    mov rbx, qword [rbp-8]
    mov rax, qword [rbp-56]
    imul rax, 8
    mov r11, qword [rbx+rax]
    mov rbx, qword [rbp-40]
    mov rax, qword [rbp-64]
    imul rax, 8
    mov qword [rbx+rax], r11
    mov rax, qword [rbp-56]
    add rax, 1
    mov qword [rbp-56], rax
    mov rax, qword [rbp-64]
    add rax, 1
    mov qword [rbp-64], rax
    jmp .copy_right_remaining

.copy_temp_back:
    mov qword [rbp-72], 0

.copy_back_loop:
    mov rax, qword [rbp-72]
    cmp rax, qword [rbp-64]
    jge .merge_end
    mov rbx, qword [rbp-40]
    mov rax, qword [rbp-72]
    imul rax, 8
    mov r10, qword [rbx+rax]
    mov rax, qword [rbp-16]
    add rax, qword [rbp-72]
    imul rax, 8
    mov rbx, qword [rbp-8]
    mov qword [rbx+rax], r10
    mov rax, qword [rbp-72]
    add rax, 1
    mov qword [rbp-72], rax
    jmp .copy_back_loop

.merge_end:
    mov rsp, rbp
    pop rbp
    ret
