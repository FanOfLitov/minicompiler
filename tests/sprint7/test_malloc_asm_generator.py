from src.codegen.malloc_asm_generator import MallocArrayASMGenerator


def test_malloc_asm_contains_extern_malloc():
    asm = MallocArrayASMGenerator().generate_int_array_demo("arr", [8, 3, 5])

    assert "extern malloc" in asm
    assert "call malloc" in asm


def test_malloc_asm_uses_exact_size():
    asm = MallocArrayASMGenerator().generate_int_array_demo("arr", [8, 3, 5], element_size=8)

    assert "; 3 elements * 8 bytes = 24 bytes" in asm
    assert "mov rdi, 24" in asm


def test_malloc_asm_stores_pointer_on_stack():
    asm = MallocArrayASMGenerator().generate_int_array_demo("arr", [1, 2])

    assert "mov qword [rbp-8], rax    ; arr pointer" in asm


def test_malloc_asm_writes_array_values_to_heap_offsets():
    asm = MallocArrayASMGenerator().generate_int_array_demo("arr", [8, 3, 5], element_size=8)

    assert "mov qword [rbx+0], 8" in asm
    assert "mov qword [rbx+8], 3" in asm
    assert "mov qword [rbx+16], 5" in asm


def test_malloc_asm_does_not_use_alloca():
    asm = MallocArrayASMGenerator().generate_int_array_demo("arr", [1, 2, 3])

    assert "ALLOCA" not in asm
    assert "alloca" not in asm
