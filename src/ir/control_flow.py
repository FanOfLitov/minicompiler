"""
Label generation and control-flow graph DOT output.
Compatible with Python 3.8+.
"""
from __future__ import annotations

from typing import List

from .basic_block import IRFunction


class LabelManager:
    def __init__(self) -> None:
        self._counter = 0

    def new_label(self, prefix: str = "L") -> str:
        self._counter += 1
        return f"{prefix}{self._counter}"


def function_to_dot(function: IRFunction) -> str:
    lines: List[str] = [
        f'digraph "{function.name}_cfg" {{',
        '  node [shape=box fontname="Courier"];',
    ]

    for block in function.blocks:
        parts = []
        for instr in block.instructions:
            if instr.opcode == "LABEL":
                continue
            parts.append(str(instr).replace('"', '\\"'))
        body = "\\l".join(parts)
        if body:
            body += "\\l"
        lines.append(f'  "{block.label}" [label="{block.label}:\\l{body}"];')

    for idx, block in enumerate(function.blocks):
        if not block.instructions:
            if idx + 1 < len(function.blocks):
                lines.append(f'  "{block.label}" -> "{function.blocks[idx + 1].label}";')
            continue

        last = block.instructions[-1]
        if last.opcode == "JUMP":
            lines.append(f'  "{block.label}" -> "{last.args[0]}";')
        elif last.opcode in ("JUMP_IF", "JUMP_IF_NOT"):
            lines.append(f'  "{block.label}" -> "{last.args[1]}" [label="true"];')
            if idx + 1 < len(function.blocks):
                lines.append(f'  "{block.label}" -> "{function.blocks[idx + 1].label}" [label="false"];')
        elif last.opcode != "RETURN" and idx + 1 < len(function.blocks):
            lines.append(f'  "{block.label}" -> "{function.blocks[idx + 1].label}";')

    lines.append("}")
    return "\n".join(lines)
