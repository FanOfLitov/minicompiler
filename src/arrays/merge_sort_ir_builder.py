from src.arrays.array_ir import ArrayIRProgram


class MergeSortIRBuilder:
    """
    Builds high-level array IR for merge sort demo.

    This is not raw ASM. It is an intermediate representation that later
    gets lowered to heap allocation and then to x86-64 assembly.
    """

    def build(self, values):
        program = ArrayIRProgram()

        count = len(values)
        element_size = 8

        program.add(
            "ALLOCA_ARRAY",
            ["values", str(count), str(element_size)],
            comment="old abstract array allocation",
        )

        for index, value in enumerate(values):
            program.add(
                "STORE_INDEX",
                ["values", str(index), str(value), str(element_size)],
                comment="values[{}] = {}".format(index, value),
            )

        program.add(
            "CALL",
            ["merge_sort", "values", "0", str(count - 1)],
            comment="merge_sort(values, 0, {})".format(count - 1),
        )

        program.add("RETURN", ["0"])

        return program
