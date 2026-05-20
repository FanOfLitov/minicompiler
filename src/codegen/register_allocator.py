"""
Very small fixed-register helper for Sprint 5.

This is not a real global register allocator. It provides scratch registers
used by the x86 generator while values are stored in stack slots.
"""
from __future__ import annotations


class RegisterAllocator:
    def __init__(self) -> None:
        self.registers = ["rax", "rbx", "rcx", "rdx"]
        self._index = 0

    def reset(self) -> None:
        self._index = 0

    def next(self) -> str:
        reg = self.registers[self._index % len(self.registers)]
        self._index += 1
        return reg
