"""
Basic block and function-level IR containers.
Compatible with Python 3.8+.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from .ir_instructions import IRInstruction


@dataclass
class BasicBlock:
    label: str
    instructions: List[IRInstruction] = field(default_factory=list)

    def add(self, instruction: IRInstruction) -> None:
        self.instructions.append(instruction)

    def dump(self) -> str:
        lines = [f"  {self.label}:"]
        for instr in self.instructions:
            if instr.opcode == "LABEL":
                continue
            lines.append(f"    {instr}")
        return "\n".join(lines)


@dataclass
class IRFunction:
    name: str
    return_type: str
    params: List[str]
    blocks: List[BasicBlock] = field(default_factory=list)
    locals: Dict[str, str] = field(default_factory=dict)

    def new_block(self, label: str) -> BasicBlock:
        block = BasicBlock(label)
        self.blocks.append(block)
        return block

    def dump(self) -> str:
        params = ", ".join(self.params)
        lines = [f"function {self.name}: {self.return_type} ({params})"]
        for block in self.blocks:
            lines.append(block.dump())
        return "\n".join(lines)


@dataclass
class IRProgram:
    functions: Dict[str, IRFunction] = field(default_factory=dict)

    def add_function(self, function: IRFunction) -> None:
        self.functions[function.name] = function

    def get_function(self, name: str) -> IRFunction:
        return self.functions[name]

    def dump(self) -> str:
        return "\n\n".join(fn.dump() for fn in self.functions.values())
