"""
Stack frame management for Sprint 5.
Compatible with Python 3.8+.

This module assigns stack slots for local variables and IR temporaries.
The generated assembly follows a simple System V AMD64 style frame:

    push rbp
    mov rbp, rsp
    sub rsp, <aligned_size>
    ...
    mov rsp, rbp
    pop rbp
    ret
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict


@dataclass
class StackSlot:
    name: str
    offset: int
    size: int = 8

    def asm(self) -> str:
        if self.offset < 0:
            return f"[rbp{self.offset}]"
        return f"[rbp+{self.offset}]"


@dataclass
class StackFrame:
    function_name: str
    slots: Dict[str, StackSlot] = field(default_factory=dict)
    _next_offset: int = -8

    def allocate(self, name: str, size: int = 8) -> StackSlot:
        if name in self.slots:
            return self.slots[name]

        slot = StackSlot(name=name, offset=self._next_offset, size=size)
        self.slots[name] = slot
        self._next_offset -= size
        return slot

    def get(self, name: str) -> StackSlot:
        return self.allocate(name)

    @property
    def raw_size(self) -> int:
        if not self.slots:
            return 0
        return abs(min(slot.offset for slot in self.slots.values()))

    @property
    def aligned_size(self) -> int:
        size = self.raw_size
        if size == 0:
            return 0
        # 16-byte alignment for calls and ABI-friendly frames.
        remainder = size % 16
        if remainder:
            size += 16 - remainder
        return size

    def dump_layout(self) -> str:
        lines = [f"stack frame for {self.function_name}:"]
        for name, slot in sorted(self.slots.items(), key=lambda item: item[1].offset):
            lines.append(f"  {name}: {slot.asm()}")
        lines.append(f"  total stack size: {self.aligned_size}")
        return "\n".join(lines)
