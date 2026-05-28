"""
Sprint 7: assembly generator for dynamic array allocation demo.

This generator is intentionally focused on the teacher requirement:
- do not allocate arrays on stack through ALLOCA;
- calculate exact byte size: element_count * element_size;
- call malloc;
- store values into heap addresses through the returned pointer;
- show assembly that can be demonstrated like Sprint 5/6 asm output.

It generates NASM-like x86-64 assembly.
"""


class MallocArrayASMGenerator:
    def generate_int_array_demo(self, array_name, values, element_size=8):
        element_count = len(values)
        total_bytes = element_count * element_size

        lines = []
        lines.append("section .text")
        lines.append("extern malloc")
        lines.append("global main")
        lines.append("")
        lines.append("main:")
        lines.append("    push rbp")
        lines.append("    mov rbp, rsp")
        lines.append("    sub rsp, 16")
        lines.append("")
        lines.append("    ; dynamic array allocation")
        lines.append("    ; {} elements * {} bytes = {} bytes".format(element_count, element_size, total_bytes))
        lines.append("    mov rdi, {}".format(total_bytes))
        lines.append("    call malloc")
        lines.append("    mov qword [rbp-8], rax    ; {} pointer".format(array_name))
        lines.append("")

        for index, value in enumerate(values):
            offset = index * element_size
            lines.append("    ; {}[{}] = {}".format(array_name, index, value))
            lines.append("    mov rbx, qword [rbp-8]")
            lines.append("    mov qword [rbx+{}], {}".format(offset, value))
            lines.append("")

        lines.append("    ; return 0")
        lines.append("    mov rax, 0")
        lines.append("    mov rsp, rbp")
        lines.append("    pop rbp")
        lines.append("    ret")

        return "\n".join(lines)
