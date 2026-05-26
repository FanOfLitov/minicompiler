from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class SSAInstruction:
    opcode: str
    dest: Optional[str] = None
    args: List[str] = field(default_factory=list)
    comment: str = ""

    def __str__(self):
        if self.opcode == "RETURN":
            line = "RETURN " + self.args[0] if self.args else "RETURN"
        elif self.opcode == "JUMP":
            line = "JUMP " + self.args[0]
        elif self.opcode in ("JUMP_IF", "JUMP_IF_NOT"):
            line = "{} {}, {}".format(self.opcode, self.args[0], self.args[1])
        elif self.opcode == "CALL":
            line = "{} = CALL {}".format(self.dest, ", ".join(self.args)) if self.dest else "CALL " + ", ".join(self.args)
        elif self.dest:
            line = "{} = {} {}".format(self.dest, self.opcode, ", ".join(self.args))
        else:
            line = self.opcode + (" " + ", ".join(self.args) if self.args else "")
        if self.comment:
            line += "    # " + self.comment
        return line


@dataclass
class SSABlock:
    label: str
    instructions: List[SSAInstruction] = field(default_factory=list)

    def add(self, instruction):
        self.instructions.append(instruction)

    def dump(self):
        lines = ["  {}:".format(self.label)]
        for instr in self.instructions:
            lines.append("    {}".format(instr))
        return "\n".join(lines)


@dataclass
class SSAFunction:
    name: str
    return_type: str
    params: List[str]
    blocks: List[SSABlock] = field(default_factory=list)

    def new_block(self, label):
        block = SSABlock(label)
        self.blocks.append(block)
        return block

    def dump(self):
        lines = ["ssa function {}: {} ({})".format(self.name, self.return_type, ", ".join(self.params))]
        for block in self.blocks:
            lines.append(block.dump())
        return "\n".join(lines)


@dataclass
class SSAProgram:
    functions: Dict[str, SSAFunction] = field(default_factory=dict)

    def add_function(self, function):
        self.functions[function.name] = function

    def dump(self):
        return "\n\n".join(fn.dump() for fn in self.functions.values())
