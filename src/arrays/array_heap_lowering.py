from src.arrays.array_ir import ArrayIRProgram


class ArrayHeapLowering:
    """
    Lowers high-level array allocation to heap allocation.

    Before:
        ALLOCA_ARRAY values, 8, 8

    After:
        heap_size1 = MUL 8, 8
        values = MALLOC heap_size1
    """

    def __init__(self):
        self.temp_counter = 0

    def lower(self, program):
        lowered = ArrayIRProgram()

        for instr in program.instructions:
            if instr.opcode == "ALLOCA_ARRAY":
                name, count, element_size = instr.args
                temp = self._temp()

                lowered.add(
                    "MUL",
                    [count, element_size],
                    dest=temp,
                    comment="exact heap size: count * element_size",
                )

                lowered.add(
                    "MALLOC",
                    [temp],
                    dest=name,
                    comment="dynamic array allocation in heap",
                )
            else:
                lowered.instructions.append(instr)

        return lowered

    def _temp(self):
        self.temp_counter += 1
        return "heap_size{}".format(self.temp_counter)
