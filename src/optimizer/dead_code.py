class DeadCodeEliminator:
    def optimize(self, program):
        for function in program.functions.values():
            for block in function.blocks:
                cleaned = []
                stop = False
                for instr in block.instructions:
                    if stop:
                        continue
                    cleaned.append(instr)
                    if instr.opcode in ("RETURN", "JUMP"):
                        stop = True
                block.instructions = cleaned
        return program
