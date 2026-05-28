class HeapCodegen:
    """
    Demonstrates how MALLOC IR is lowered to a malloc call.
    """

    def generate_malloc_commentary(self, array_name, element_count, element_size):
        total = int(element_count) * int(element_size)

        lines = [
            "; dynamic array allocation",
            "; {} elements * {} bytes = {} bytes".format(element_count, element_size, total),
            "mov rdi, {}".format(total),
            "call malloc",
            "; {} pointer is now in rax".format(array_name),
        ]

        return "\n".join(lines)
