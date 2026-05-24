from src.ir.ir_instructions import IRInstruction

class ConstantFolder:
    def optimize(self, program):
        for function in program.functions.values():
            for block in function.blocks:
                result = []
                for instr in block.instructions:
                    if instr.opcode == "ADD" and all(a.lstrip("-").isdigit() for a in instr.args):
                        value = int(instr.args[0]) + int(instr.args[1])
                        instr = IRInstruction(
                            opcode="MOVE",
                            dest=instr.dest,
                            args=[str(value)],
                            comment="constant folded"
                        )
                    result.append(instr)
                block.instructions = result
        return program
