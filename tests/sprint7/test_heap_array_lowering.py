from src.ir.basic_block import IRProgram, IRFunction
from src.ir.ir_instructions import IRInstruction
from src.optimizer.heap_array_lowering import HeapArrayLowering
from src.codegen.heap_codegen import HeapCodegen


def _program_with_alloca():
    program = IRProgram()
    fn = IRFunction("main", "int", [])
    block = fn.new_block("entry")
    block.add(IRInstruction("ALLOCA", args=["arr", "5", "8"], comment="old stack array allocation"))
    block.add(IRInstruction("RETURN", args=["0"]))
    program.add_function(fn)
    return program


def test_alloca_is_removed_after_heap_lowering():
    lowered = HeapArrayLowering().optimize(_program_with_alloca())
    text = lowered.dump()

    assert "ALLOCA" not in text


def test_alloca_becomes_malloc():
    lowered = HeapArrayLowering().optimize(_program_with_alloca())
    text = lowered.dump()

    assert "heap_size1 = MUL 5, 8" in text
    assert "arr = MALLOC heap_size1" in text


def test_malloc_size_is_exact_count_times_element_size():
    code = HeapCodegen().generate_malloc_commentary("arr", "5", "8")

    assert "5 elements * 8 bytes = 40 bytes" in code
    assert "mov rdi, 40" in code
    assert "call malloc" in code


def test_dynamic_array_allocation_uses_heap_not_stack():
    lowered = HeapArrayLowering().optimize(_program_with_alloca())
    text = lowered.dump()

    assert "MALLOC" in text
    assert "ALLOCA" not in text


def test_second_array_gets_second_heap_size_temp():
    program = IRProgram()
    fn = IRFunction("main", "int", [])
    block = fn.new_block("entry")
    block.add(IRInstruction("ALLOCA", args=["a", "3", "8"]))
    block.add(IRInstruction("ALLOCA", args=["b", "4", "8"]))
    block.add(IRInstruction("RETURN", args=["0"]))
    program.add_function(fn)

    lowered = HeapArrayLowering().optimize(program)
    text = lowered.dump()

    assert "heap_size1 = MUL 3, 8" in text
    assert "a = MALLOC heap_size1" in text
    assert "heap_size2 = MUL 4, 8" in text
    assert "b = MALLOC heap_size2" in text


def test_codegen_commentary_for_different_size():
    code = HeapCodegen().generate_malloc_commentary("values", "10", "8")

    assert "10 elements * 8 bytes = 80 bytes" in code
    assert "mov rdi, 80" in code
