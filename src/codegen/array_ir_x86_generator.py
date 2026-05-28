class ArrayIRX86Generator:
    """
    Generates readable x86-64 assembly from lowered ArrayIRProgram.

    Important:
    return "\\n".join(lines) would write literal backslash-n characters.
    return "\n".join(lines) writes real line breaks.
    """

    def __init__(self):
        self.array_stack_slots = {}
        self.temp_values = {}
        self.next_stack_offset = 8

    def generate(self, program):
        lines = []
        lines.append("section .text")
        lines.append("extern malloc")
        lines.append("global main")
        lines.append("")
        lines.append("main:")
        lines.append("    push rbp")
        lines.append("    mov rbp, rsp")
        lines.append("    sub rsp, 32")
        lines.append("")

        for instr in program.instructions:
            self._emit_instruction(lines, instr)

        if not self._has_return(program):
            lines.extend(self._emit_return("0"))

        lines.append("")
        lines.extend(self._emit_merge_sort_function())
        lines.append("")
        lines.extend(self._emit_merge_function())

        return "\n".join(lines)

    def _emit_instruction(self, lines, instr):
        if instr.opcode == "MUL":
            left, right = instr.args
            if left.isdigit() and right.isdigit():
                value = int(left) * int(right)
                self.temp_values[instr.dest] = value
                lines.append("    ; {} = {} * {} = {}".format(instr.dest, left, right, value))
            else:
                lines.append("    ; {} = {} * {}".format(instr.dest, left, right))
            return

        if instr.opcode == "MALLOC":
            size_arg = instr.args[0]
            size_value = self.temp_values.get(size_arg, size_arg)
            slot = self._array_slot(instr.dest)

            lines.append("    ; dynamic array allocation for {}".format(instr.dest))
            lines.append("    mov rdi, {}".format(size_value))
            lines.append("    call malloc")
            lines.append("    mov qword [rbp-{}], rax    ; {} pointer".format(slot, instr.dest))
            lines.append("")
            return

        if instr.opcode == "STORE_INDEX":
            array_name, index, value, element_size = instr.args
            slot = self._array_slot(array_name)
            offset = int(index) * int(element_size)

            lines.append("    ; {}[{}] = {}".format(array_name, index, value))
            lines.append("    mov rbx, qword [rbp-{}]".format(slot))
            lines.append("    mov qword [rbx+{}], {}".format(offset, value))
            lines.append("")
            return

        if instr.opcode == "CALL":
            function_name = instr.args[0]

            if function_name == "merge_sort":
                array_name = instr.args[1]
                left = instr.args[2]
                right = instr.args[3]
                slot = self._array_slot(array_name)

                lines.append("    ; merge_sort({}, {}, {})".format(array_name, left, right))
                lines.append("    mov rdi, qword [rbp-{}]".format(slot))
                lines.append("    mov rsi, {}".format(left))
                lines.append("    mov rdx, {}".format(right))
                lines.append("    call merge_sort")
                lines.append("")
                return

            lines.append("    call {}".format(function_name))
            return

        if instr.opcode == "RETURN":
            value = instr.args[0] if instr.args else "0"
            lines.extend(self._emit_return(value))
            return

        lines.append("    ; unsupported IR instruction: {}".format(instr))

    def _array_slot(self, name):
        if name not in self.array_stack_slots:
            self.array_stack_slots[name] = self.next_stack_offset
            self.next_stack_offset += 8
        return self.array_stack_slots[name]

    def _has_return(self, program):
        return any(instr.opcode == "RETURN" for instr in program.instructions)

    def _emit_return(self, value):
        return [
            "    mov rax, {}".format(value),
            "    mov rsp, rbp",
            "    pop rbp",
            "    ret",
        ]

    def _emit_merge_sort_function(self):
        return [
            "merge_sort:",
            "    push rbp",
            "    mov rbp, rsp",
            "    sub rsp, 64",
            "",
            "    mov qword [rbp-8], rdi     ; arr",
            "    mov qword [rbp-16], rsi    ; left",
            "    mov qword [rbp-24], rdx    ; right",
            "",
            "    mov rax, qword [rbp-16]",
            "    cmp rax, qword [rbp-24]",
            "    jge .merge_sort_end",
            "",
            "    mov rax, qword [rbp-24]",
            "    sub rax, qword [rbp-16]",
            "    cqo",
            "    mov rbx, 2",
            "    idiv rbx",
            "    add rax, qword [rbp-16]",
            "    mov qword [rbp-32], rax    ; mid",
            "",
            "    mov rdi, qword [rbp-8]",
            "    mov rsi, qword [rbp-16]",
            "    mov rdx, qword [rbp-32]",
            "    call merge_sort",
            "",
            "    mov rdi, qword [rbp-8]",
            "    mov rax, qword [rbp-32]",
            "    add rax, 1",
            "    mov rsi, rax",
            "    mov rdx, qword [rbp-24]",
            "    call merge_sort",
            "",
            "    mov rdi, qword [rbp-8]",
            "    mov rsi, qword [rbp-16]",
            "    mov rdx, qword [rbp-32]",
            "    mov rcx, qword [rbp-24]",
            "    call merge",
            "",
            ".merge_sort_end:",
            "    mov rsp, rbp",
            "    pop rbp",
            "    ret",
        ]

    def _emit_merge_function(self):
        return [
            "merge:",
            "    push rbp",
            "    mov rbp, rsp",
            "    sub rsp, 112",
            "",
            "    mov qword [rbp-8], rdi      ; arr",
            "    mov qword [rbp-16], rsi     ; left",
            "    mov qword [rbp-24], rdx     ; mid",
            "    mov qword [rbp-32], rcx     ; right",
            "",
            "    ; temp buffer for merge",
            "    mov rdi, 64",
            "    call malloc",
            "    mov qword [rbp-40], rax     ; temp pointer",
            "",
            "    mov rax, qword [rbp-16]",
            "    mov qword [rbp-48], rax     ; i",
            "",
            "    mov rax, qword [rbp-24]",
            "    add rax, 1",
            "    mov qword [rbp-56], rax     ; j",
            "",
            "    mov qword [rbp-64], 0       ; k",
            "",
            ".merge_loop:",
            "    mov rax, qword [rbp-48]",
            "    cmp rax, qword [rbp-24]",
            "    jg .copy_left_remaining",
            "",
            "    mov rax, qword [rbp-56]",
            "    cmp rax, qword [rbp-32]",
            "    jg .copy_left_remaining",
            "",
            "    mov rbx, qword [rbp-8]",
            "    mov rax, qword [rbp-48]",
            "    imul rax, 8",
            "    mov r10, qword [rbx+rax]",
            "",
            "    mov rbx, qword [rbp-8]",
            "    mov rax, qword [rbp-56]",
            "    imul rax, 8",
            "    mov r11, qword [rbx+rax]",
            "",
            "    cmp r10, r11",
            "    jle .take_left",
            "",
            ".take_right:",
            "    mov rbx, qword [rbp-40]",
            "    mov rax, qword [rbp-64]",
            "    imul rax, 8",
            "    mov qword [rbx+rax], r11",
            "    mov rax, qword [rbp-56]",
            "    add rax, 1",
            "    mov qword [rbp-56], rax",
            "    jmp .inc_k",
            "",
            ".take_left:",
            "    mov rbx, qword [rbp-40]",
            "    mov rax, qword [rbp-64]",
            "    imul rax, 8",
            "    mov qword [rbx+rax], r10",
            "    mov rax, qword [rbp-48]",
            "    add rax, 1",
            "    mov qword [rbp-48], rax",
            "",
            ".inc_k:",
            "    mov rax, qword [rbp-64]",
            "    add rax, 1",
            "    mov qword [rbp-64], rax",
            "    jmp .merge_loop",
            "",
            ".copy_left_remaining:",
            "    mov rax, qword [rbp-48]",
            "    cmp rax, qword [rbp-24]",
            "    jg .copy_right_remaining",
            "    mov rbx, qword [rbp-8]",
            "    mov rax, qword [rbp-48]",
            "    imul rax, 8",
            "    mov r10, qword [rbx+rax]",
            "    mov rbx, qword [rbp-40]",
            "    mov rax, qword [rbp-64]",
            "    imul rax, 8",
            "    mov qword [rbx+rax], r10",
            "    mov rax, qword [rbp-48]",
            "    add rax, 1",
            "    mov qword [rbp-48], rax",
            "    mov rax, qword [rbp-64]",
            "    add rax, 1",
            "    mov qword [rbp-64], rax",
            "    jmp .copy_left_remaining",
            "",
            ".copy_right_remaining:",
            "    mov rax, qword [rbp-56]",
            "    cmp rax, qword [rbp-32]",
            "    jg .copy_temp_back",
            "    mov rbx, qword [rbp-8]",
            "    mov rax, qword [rbp-56]",
            "    imul rax, 8",
            "    mov r11, qword [rbx+rax]",
            "    mov rbx, qword [rbp-40]",
            "    mov rax, qword [rbp-64]",
            "    imul rax, 8",
            "    mov qword [rbx+rax], r11",
            "    mov rax, qword [rbp-56]",
            "    add rax, 1",
            "    mov qword [rbp-56], rax",
            "    mov rax, qword [rbp-64]",
            "    add rax, 1",
            "    mov qword [rbp-64], rax",
            "    jmp .copy_right_remaining",
            "",
            ".copy_temp_back:",
            "    mov qword [rbp-72], 0",
            "",
            ".copy_back_loop:",
            "    mov rax, qword [rbp-72]",
            "    cmp rax, qword [rbp-64]",
            "    jge .merge_end",
            "    mov rbx, qword [rbp-40]",
            "    mov rax, qword [rbp-72]",
            "    imul rax, 8",
            "    mov r10, qword [rbx+rax]",
            "    mov rax, qword [rbp-16]",
            "    add rax, qword [rbp-72]",
            "    imul rax, 8",
            "    mov rbx, qword [rbp-8]",
            "    mov qword [rbx+rax], r10",
            "    mov rax, qword [rbp-72]",
            "    add rax, 1",
            "    mov qword [rbp-72], rax",
            "    jmp .copy_back_loop",
            "",
            ".merge_end:",
            "    mov rsp, rbp",
            "    pop rbp",
            "    ret",
        ]
