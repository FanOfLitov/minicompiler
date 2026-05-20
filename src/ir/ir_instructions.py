"""
Intermediate Representation instruction model for Sprint 4.
Compatible with Python 3.8+.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass(frozen=True)
class IROperand:
    text: str
    typ: Optional[str] = None

    def __str__(self) -> str:
        return self.text


@dataclass(frozen=True)
class Temp(IROperand):
    pass


@dataclass(frozen=True)
class Var(IROperand):
    pass


@dataclass(frozen=True)
class Const(IROperand):
    pass


@dataclass(frozen=True)
class Label(IROperand):
    pass


@dataclass
class IRInstruction:
    opcode: str
    dest: Optional[str] = None
    args: List[str] = field(default_factory=list)
    comment: str = ""

    def __str__(self) -> str:
        if self.opcode == "LABEL":
            line = f"{self.args[0]}:"
        elif self.opcode == "JUMP":
            line = f"JUMP {self.args[0]}"
        elif self.opcode in ("JUMP_IF", "JUMP_IF_NOT"):
            line = f"{self.opcode} {self.args[0]}, {self.args[1]}"
        elif self.opcode == "RETURN":
            line = "RETURN" if not self.args else f"RETURN {self.args[0]}"
        elif self.opcode == "CALL":
            call_args = ", ".join(self.args)
            line = f"{self.dest} = CALL {call_args}" if self.dest else f"CALL {call_args}"
        elif self.opcode == "STORE":
            line = f"STORE {self.args[0]}, {self.args[1]}"
        elif self.opcode == "LOAD":
            line = f"{self.dest} = LOAD {self.args[0]}"
        elif self.opcode == "MOVE":
            line = f"{self.dest} = MOVE {self.args[0]}"
        elif self.dest:
            line = f"{self.dest} = {self.opcode} " + ", ".join(self.args)
        else:
            line = self.opcode + (" " + ", ".join(self.args) if self.args else "")

        if self.comment:
            line += f"    # {self.comment}"
        return line
