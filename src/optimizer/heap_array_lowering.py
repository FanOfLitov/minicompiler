from src.ir.ir_instructions import IRInstruction


class HeapArrayLowering:

    def __init__(self):
        self._temp_counter = 0

    def optimize(self, program):
        for function in program.functions.values():
            for block in function.blocks:
                lowered = []

                for instr in block.instructions:
                    if instr.opcode == "ALLOCA" and len(instr.args) == 3:
                        array_name = instr.args[0]
                        element_count = instr.args[1]
                        element_size = instr.args[2]

                        size_temp = self._new_temp()

                        lowered.append(
                            IRInstruction(
                                opcode="MUL",
                                dest=size_temp,
                                args=[element_count, element_size],
                                comment="array byte size: count * element_size",
                            )
                        )

                        lowered.append(
                            IRInstruction(
                                opcode="MALLOC",
                                dest=array_name,
                                args=[size_temp],
                                comment="dynamic array allocation in heap",
                            )
                        )

                    else:
                        lowered.append(instr)

                block.instructions = lowered

        return program

    def _new_temp(self):
        self._temp_counter += 1
        return "heap_size{}".format(self._temp_counter)
