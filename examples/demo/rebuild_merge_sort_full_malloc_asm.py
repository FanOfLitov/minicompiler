from pathlib import Path

ASM = r"""section .text
extern malloc
global main

; ---------------------------------------------------------------------------
; Sprint 7 demo:
; Dynamic array is allocated in heap through malloc.
; Merge sort is executed over heap array.
;
; Array layout:
;   values[i] address = base + i * 8
;
; Initial:
;   [8, 3, 5, 1, 9, 2, 7, 4]
;
; After merge_sort:
;   [1, 2, 3, 4, 5, 7, 8, 9]
; ---------------------------------------------------------------------------

main:
    push rbp
    mov rbp, rsp
    sub rsp, 16

    ; dynamic array allocation
    ; 8 elements * 8 bytes = 64 bytes
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
    mov rdi, qword [rbp-8]    ; array pointer
    mov rsi, 0                ; left
    mov rdx, 7                ; right
    call merge_sort

    ; At this point heap array is sorted:
    ; values = [1, 2, 3, 4, 5, 7, 8, 9]

    mov rax, 0
    mov rsp, rbp
    pop rbp
    ret


; ---------------------------------------------------------------------------
; void merge_sort(int* arr, int left, int right)
;
; arguments:
;   rdi = arr pointer
;   rsi = left
;   rdx = right
; ---------------------------------------------------------------------------
merge_sort:
    push rbp
    mov rbp, rsp
    sub rsp, 64

    mov qword [rbp-8], rdi     ; arr
    mov qword [rbp-16], rsi    ; left
    mov qword [rbp-24], rdx    ; right

    ; if (left >= right) return
    mov rax, qword [rbp-16]
    cmp rax, qword [rbp-24]
    jge .merge_sort_end

    ; mid = left + (right - left) / 2
    mov rax, qword [rbp-24]
    sub rax, qword [rbp-16]
    cqo
    mov rbx, 2
    idiv rbx
    add rax, qword [rbp-16]
    mov qword [rbp-32], rax    ; mid

    ; merge_sort(arr, left, mid)
    mov rdi, qword [rbp-8]
    mov rsi, qword [rbp-16]
    mov rdx, qword [rbp-32]
    call merge_sort

    ; merge_sort(arr, mid + 1, right)
    mov rdi, qword [rbp-8]
    mov rax, qword [rbp-32]
    add rax, 1
    mov rsi, rax
    mov rdx, qword [rbp-24]
    call merge_sort

    ; merge(arr, left, mid, right)
    mov rdi, qword [rbp-8]
    mov rsi, qword [rbp-16]
    mov rdx, qword [rbp-32]
    mov rcx, qword [rbp-24]
    call merge

.merge_sort_end:
    mov rsp, rbp
    pop rbp
    ret


; ---------------------------------------------------------------------------
; void merge(int* arr, int left, int mid, int right)
;
; arguments:
;   rdi = arr pointer
;   rsi = left
;   rdx = mid
;   rcx = right
;
; For defense/demo simplicity this implementation uses one temporary
; heap buffer of 8 integers = 64 bytes.
;
; The algorithm:
;   i = left
;   j = mid + 1
;   k = 0
;   while i <= mid and j <= right:
;       if arr[i] <= arr[j]: temp[k++] = arr[i++]
;       else:                temp[k++] = arr[j++]
;   copy remaining left part
;   copy remaining right part
;   copy temp back to arr[left + t]
; ---------------------------------------------------------------------------
merge:
    push rbp
    mov rbp, rsp
    sub rsp, 112

    mov qword [rbp-8], rdi      ; arr
    mov qword [rbp-16], rsi     ; left
    mov qword [rbp-24], rdx     ; mid
    mov qword [rbp-32], rcx     ; right

    ; temp = malloc(8 elements * 8 bytes)
    mov rdi, 64
    call malloc
    mov qword [rbp-40], rax     ; temp pointer

    ; i = left
    mov rax, qword [rbp-16]
    mov qword [rbp-48], rax

    ; j = mid + 1
    mov rax, qword [rbp-24]
    add rax, 1
    mov qword [rbp-56], rax

    ; k = 0
    mov qword [rbp-64], 0

.merge_loop:
    ; while i <= mid
    mov rax, qword [rbp-48]
    cmp rax, qword [rbp-24]
    jg .copy_left_remaining

    ; and j <= right
    mov rax, qword [rbp-56]
    cmp rax, qword [rbp-32]
    jg .copy_left_remaining

    ; left_value = arr[i]
    mov rbx, qword [rbp-8]
    mov rax, qword [rbp-48]
    imul rax, 8
    mov r10, qword [rbx+rax]

    ; right_value = arr[j]
    mov rbx, qword [rbp-8]
    mov rax, qword [rbp-56]
    imul rax, 8
    mov r11, qword [rbx+rax]

    ; if left_value <= right_value
    cmp r10, r11
    jle .take_left

.take_right:
    ; temp[k] = right_value
    mov rbx, qword [rbp-40]
    mov rax, qword [rbp-64]
    imul rax, 8
    mov qword [rbx+rax], r11

    ; j++
    mov rax, qword [rbp-56]
    add rax, 1
    mov qword [rbp-56], rax
    jmp .inc_k

.take_left:
    ; temp[k] = left_value
    mov rbx, qword [rbp-40]
    mov rax, qword [rbp-64]
    imul rax, 8
    mov qword [rbx+rax], r10

    ; i++
    mov rax, qword [rbp-48]
    add rax, 1
    mov qword [rbp-48], rax

.inc_k:
    ; k++
    mov rax, qword [rbp-64]
    add rax, 1
    mov qword [rbp-64], rax
    jmp .merge_loop


.copy_left_remaining:
    ; while i <= mid
    mov rax, qword [rbp-48]
    cmp rax, qword [rbp-24]
    jg .copy_right_remaining

    ; temp[k] = arr[i]
    mov rbx, qword [rbp-8]
    mov rax, qword [rbp-48]
    imul rax, 8
    mov r10, qword [rbx+rax]

    mov rbx, qword [rbp-40]
    mov rax, qword [rbp-64]
    imul rax, 8
    mov qword [rbx+rax], r10

    ; i++
    mov rax, qword [rbp-48]
    add rax, 1
    mov qword [rbp-48], rax

    ; k++
    mov rax, qword [rbp-64]
    add rax, 1
    mov qword [rbp-64], rax

    jmp .copy_left_remaining


.copy_right_remaining:
    ; while j <= right
    mov rax, qword [rbp-56]
    cmp rax, qword [rbp-32]
    jg .copy_temp_back

    ; temp[k] = arr[j]
    mov rbx, qword [rbp-8]
    mov rax, qword [rbp-56]
    imul rax, 8
    mov r11, qword [rbx+rax]

    mov rbx, qword [rbp-40]
    mov rax, qword [rbp-64]
    imul rax, 8
    mov qword [rbx+rax], r11

    ; j++
    mov rax, qword [rbp-56]
    add rax, 1
    mov qword [rbp-56], rax

    ; k++
    mov rax, qword [rbp-64]
    add rax, 1
    mov qword [rbp-64], rax

    jmp .copy_right_remaining


.copy_temp_back:
    ; t = 0
    mov qword [rbp-72], 0

.copy_back_loop:
    ; while t < k
    mov rax, qword [rbp-72]
    cmp rax, qword [rbp-64]
    jge .merge_end

    ; arr[left + t] = temp[t]
    mov rbx, qword [rbp-40]
    mov rax, qword [rbp-72]
    imul rax, 8
    mov r10, qword [rbx+rax]    ; temp[t]

    mov rax, qword [rbp-16]
    add rax, qword [rbp-72]
    imul rax, 8
    mov rbx, qword [rbp-8]
    mov qword [rbx+rax], r10

    ; t++
    mov rax, qword [rbp-72]
    add rax, 1
    mov qword [rbp-72], rax

    jmp .copy_back_loop


.merge_end:
    mov rsp, rbp
    pop rbp
    ret
"""


def main():
    root = Path(__file__).resolve().parents[2]
    output = root / "build" / "merge_sort.asm"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(ASM + "\n", encoding="utf-8")

    print("Generated full merge_sort.asm with malloc and merge sort:")
    print(output)
    print()
    print(ASM)


if __name__ == "__main__":
    main()
