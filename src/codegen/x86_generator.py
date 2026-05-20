"""
x86-64 assembly generator for Sprint 5.
Compatible with Python 3.8+.

Input: IRProgram from Sprint 4.
Output: NASM-like Intel syntax assembly.

The generator intentionally uses a simple stack-based strategy:
- source variables and temporaries are assigned stack slots;
- arithmetic is performed through rax/rbx;
- integer return values are placed in rax;
- function parameters are copied from System V argument registers to stack slots.
"""
from __future__ import annotations

from typing import List, Set

from src.ir.basic_block import IRProgram, IRFunction, BasicBlock
from src.ir.ir_instructions import IRInstruction

from .abi import INTEGER_ARGUMENT_REGISTERS
from .stack_frame import StackFrame


class X86Generator:
    def __init__(self) -> None:
        self.lines: List[str] = []
        self.frame: StackFrame = StackFrame("<none>")

    def generate(self, program: IRProgram) -> str:
        self.lines = []
        self._emit("section .text")

        if program.functions:
            self._emit("global main")

        for function in program.functions.values():
            self._generate_function(function)

        return "\n".join(self.lines)

    def _emit(self, line: str = "") -> None:
        self.lines.append(line)

    def _comment(self, text: str) -> None:
        self._emit(f"    ; {text}")

    def _generate_function(self, function: IRFunction) -> None:
        self.frame = StackFrame(function.name)
        self._prepare_frame(function)

        self._emit("")
        self._emit(f"{function.name}:")
        self._emit("    push rbp")
        self._emit("    mov rbp, rsp")

        if self.frame.aligned_size:
            self._emit(f"    sub rsp, {self.frame.aligned_size}")

        self._store_parameters(function)

        end_label = f".L_{function.name}_end"

        for block in function.blocks:
            self._generate_block(function, block, end_label)

        self._emit(f"{end_label}:")
        self._emit("    mov rsp, rbp")
        self._emit("    pop rbp")
        self._emit("    ret")

    def _prepare_frame(self, function: IRFunction) -> None:
        # Function parameters: "name: type"
        for param in function.params:
            name = param.split(":", 1)[0].strip()
            if name:
                self.frame.allocate(name)

        for name in function.locals.keys():
            self.frame.allocate(name)

        for block in function.blocks:
            for instr in block.instructions:
                if instr.dest:
                    self.frame.allocate(instr.dest)
                for arg in instr.args:
                    if self._looks_like_temp(arg):
                        self.frame.allocate(arg)

    def _store_parameters(self, function: IRFunction) -> None:
        for idx, param in enumerate(function.params):
            name = param.split(":", 1)[0].strip()
            if not name:
                continue

            slot = self.frame.get(name)

            if idx < len(INTEGER_ARGUMENT_REGISTERS):
                self._emit(f"    mov qword {slot.asm()}, {INTEGER_ARGUMENT_REGISTERS[idx]}")
            else:
                # First stack argument after return address and old rbp is [rbp+16].
                stack_offset = 16 + (idx - len(INTEGER_ARGUMENT_REGISTERS)) * 8
                self._emit(f"    mov rax, [rbp+{stack_offset}]")
                self._emit(f"    mov qword {slot.asm()}, rax")

    def _generate_block(self, function: IRFunction, block: BasicBlock, end_label: str) -> None:
        if block.label == "entry":
            self._emit(f".L_{function.name}_entry:")
        else:
            self._emit(f".L_{function.name}_{block.label}:")

        for instr in block.instructions:
            self._generate_instruction(function, instr, end_label)

    def _label(self, function: IRFunction, label: str) -> str:
        return f".L_{function.name}_{label}"

    def _generate_instruction(self, function: IRFunction, instr: IRInstruction, end_label: str) -> None:
        op = instr.opcode

        if op == "DECLARE":
            return

        if op == "LOAD":
            self._load_operand(instr.args[0], "rax")
            self._store_dest(instr.dest, "rax")
            return

        if op == "STORE":
            target, value = instr.args[0], instr.args[1]
            self._load_operand(value, "rax")
            slot = self.frame.get(target)
            self._emit(f"    mov qword {slot.asm()}, rax")
            return

        if op == "MOVE":
            self._load_operand(instr.args[0], "rax")
            self._store_dest(instr.dest, "rax")
            return

        if op in ("ADD", "SUB", "MUL", "DIV", "MOD"):
            self._generate_arithmetic(instr)
            return

        if op in ("CMP_EQ", "CMP_NE", "CMP_LT", "CMP_LE", "CMP_GT", "CMP_GE"):
            self._generate_comparison(instr)
            return

        if op in ("AND", "OR"):
            self._load_operand(instr.args[0], "rax")
            self._load_operand(instr.args[1], "rbx")
            if op == "AND":
                self._emit("    and rax, rbx")
            else:
                self._emit("    or rax, rbx")
            self._emit("    cmp rax, 0")
            self._emit("    setne al")
            self._emit("    movzx rax, al")
            self._store_dest(instr.dest, "rax")
            return

        if op == "NOT":
            self._load_operand(instr.args[0], "rax")
            self._emit("    cmp rax, 0")
            self._emit("    sete al")
            self._emit("    movzx rax, al")
            self._store_dest(instr.dest, "rax")
            return

        if op == "NEG":
            self._load_operand(instr.args[0], "rax")
            self._emit("    neg rax")
            self._store_dest(instr.dest, "rax")
            return

        if op == "JUMP":
            self._emit(f"    jmp {self._label(function, instr.args[0])}")
            return

        if op in ("JUMP_IF", "JUMP_IF_NOT"):
            cond, label = instr.args[0], instr.args[1]
            self._load_operand(cond, "rax")
            self._emit("    cmp rax, 0")
            if op == "JUMP_IF":
                self._emit(f"    jne {self._label(function, label)}")
            else:
                self._emit(f"    je {self._label(function, label)}")
            return

        if op == "CALL":
            self._generate_call(instr)
            return

        if op == "RETURN":
            if instr.args:
                self._load_operand(instr.args[0], "rax")
            self._emit(f"    jmp {end_label}")
            return

        self._emit(f"    ; unsupported IR instruction: {instr}")

    def _generate_arithmetic(self, instr: IRInstruction) -> None:
        left, right = instr.args[0], instr.args[1]

        self._load_operand(left, "rax")
        self._load_operand(right, "rbx")

        if instr.opcode == "ADD":
            self._emit("    add rax, rbx")
        elif instr.opcode == "SUB":
            self._emit("    sub rax, rbx")
        elif instr.opcode == "MUL":
            self._emit("    imul rax, rbx")
        elif instr.opcode in ("DIV", "MOD"):
            self._emit("    cqo")
            self._emit("    idiv rbx")
            if instr.opcode == "MOD":
                self._emit("    mov rax, rdx")

        self._store_dest(instr.dest, "rax")

    def _generate_comparison(self, instr: IRInstruction) -> None:
        jumps = {
            "CMP_EQ": "sete",
            "CMP_NE": "setne",
            "CMP_LT": "setl",
            "CMP_LE": "setle",
            "CMP_GT": "setg",
            "CMP_GE": "setge",
        }

        self._load_operand(instr.args[0], "rax")
        self._load_operand(instr.args[1], "rbx")
        self._emit("    cmp rax, rbx")
        self._emit(f"    {jumps[instr.opcode]} al")
        self._emit("    movzx rax, al")
        self._store_dest(instr.dest, "rax")

    def _generate_call(self, instr: IRInstruction) -> None:
        func_name = instr.args[0]
        call_args = instr.args[1:]

        # This simple Sprint 5 version supports first six integer args.
        for idx, arg in enumerate(call_args[:len(INTEGER_ARGUMENT_REGISTERS)]):
            self._load_operand(arg, INTEGER_ARGUMENT_REGISTERS[idx])

        self._emit(f"    call {func_name}")

        if instr.dest:
            self._store_dest(instr.dest, "rax")

    def _store_dest(self, dest: str, reg: str) -> None:
        slot = self.frame.get(dest)
        self._emit(f"    mov qword {slot.asm()}, {reg}")

    def _load_operand(self, operand: str, reg: str) -> None:
        if self._is_int(operand):
            self._emit(f"    mov {reg}, {operand}")
            return

        if operand == "true":
            self._emit(f"    mov {reg}, 1")
            return

        if operand == "false":
            self._emit(f"    mov {reg}, 0")
            return

        # Strings/floats are not fully supported by Sprint 5 backend yet.
        if self._is_float(operand):
            self._emit(f"    ; float literal {operand} is not supported in integer backend")
            self._emit(f"    mov {reg}, 0")
            return

        slot = self.frame.get(operand)
        self._emit(f"    mov {reg}, qword {slot.asm()}")

    def _looks_like_temp(self, value: str) -> bool:
        return value.startswith("t") and value[1:].isdigit()

    def _is_int(self, value: str) -> bool:
        if value.startswith("-"):
            return value[1:].isdigit()
        return value.isdigit()

    def _is_float(self, value: str) -> bool:
        try:
            float(value)
            return "." in value
        except ValueError:
            return False
