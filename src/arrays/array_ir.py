from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ArrayIRInstruction:
    opcode: str
    args: List[str] = field(default_factory=list)
    dest: Optional[str] = None
    comment: str = ""

    def __str__(self):
        if self.dest:
            text = "{} = {} {}".format(self.dest, self.opcode, ", ".join(self.args))
        else:
            text = "{} {}".format(self.opcode, ", ".join(self.args)).rstrip()

        if self.comment:
            text += "    # " + self.comment

        return text


@dataclass
class ArrayIRProgram:
    instructions: List[ArrayIRInstruction] = field(default_factory=list)

    def add(self, opcode, args=None, dest=None, comment=""):
        instr = ArrayIRInstruction(
            opcode=opcode,
            args=list(args or []),
            dest=dest,
            comment=comment,
        )
        self.instructions.append(instr)
        return instr

    def dump(self):
        return "\n".join(str(instr) for instr in self.instructions)
