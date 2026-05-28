from src.arrays.merge_sort_ir_builder import MergeSortIRBuilder
from src.arrays.array_heap_lowering import ArrayHeapLowering
from src.codegen.array_ir_x86_generator import ArrayIRX86Generator


def _build_pipeline():
    high_ir = MergeSortIRBuilder().build([8, 3, 5, 1, 9, 2, 7, 4])
    lowered_ir = ArrayHeapLowering().lower(high_ir)
    asm = ArrayIRX86Generator().generate(lowered_ir)
    return high_ir, lowered_ir, asm


def test_high_ir_contains_abstract_array_allocation():
    high_ir, _, _ = _build_pipeline()
    text = high_ir.dump()

    assert "ALLOCA_ARRAY values, 8, 8" in text
    assert "STORE_INDEX values, 0, 8, 8" in text
    assert "CALL merge_sort, values, 0, 7" in text


def test_lowered_ir_replaces_alloca_with_malloc():
    _, lowered_ir, _ = _build_pipeline()
    text = lowered_ir.dump()

    assert "ALLOCA_ARRAY" not in text
    assert "heap_size1 = MUL 8, 8" in text
    assert "values = MALLOC heap_size1" in text


def test_asm_contains_malloc_and_exact_size():
    _, _, asm = _build_pipeline()

    assert "extern malloc" in asm
    assert "mov rdi, 64" in asm
    assert "call malloc" in asm


def test_asm_contains_merge_sort_and_merge():
    _, _, asm = _build_pipeline()

    assert "merge_sort:" in asm
    assert "merge:" in asm
    assert "call merge_sort" in asm
    assert "call merge" in asm


def test_asm_writes_initial_array_values():
    _, _, asm = _build_pipeline()

    assert "mov qword [rbx+0], 8" in asm
    assert "mov qword [rbx+8], 3" in asm
    assert "mov qword [rbx+56], 4" in asm


def test_asm_contains_copy_back_loop():
    _, _, asm = _build_pipeline()

    assert ".copy_temp_back:" in asm
    assert ".copy_back_loop:" in asm
    assert "mov qword [rbx+rax], r10" in asm
