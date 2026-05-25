import pytest

from src.codegen.array_generator import ArrayGenerator, ArrayLayout, ArrayLayoutError
from src.codegen.external_calls import ExternalCallError, ExternalFunction, ExternalFunctionRegistry, default_registry
from src.ir.basic_block import IRProgram, IRFunction
from src.ir.ir_instructions import IRInstruction
from src.optimizer.advanced_passes import Sprint7Optimizer


VALID_CASES = [
    "array_1d_layout",
    "array_2d_layout",
    "array_load_emit",
    "array_store_emit",
    "extern_printf_variadic",
    "extern_strlen",
    "optimizer_constant_propagation",
]

INVALID_CASES = [
    "array_zero_size",
    "array_negative_size",
    "array_wrong_index_count",
    "array_index_out_of_bounds",
    "extern_unknown_function",
    "extern_wrong_argument_count",
    "extern_wrong_argument_type",
]


@pytest.mark.parametrize("case_name", VALID_CASES)
def test_sprint7_valid_cases(case_name):
    if case_name == "array_1d_layout":
        layout = ArrayLayout("arr", "int", [10])
        assert layout.element_size == 8
        assert layout.element_count == 10
        assert layout.total_size == 80
        assert layout.byte_offset([3]) == 24

    elif case_name == "array_2d_layout":
        layout = ArrayLayout("matrix", "int", [3, 4])
        assert layout.element_count == 12
        assert layout.byte_offset([2, 3]) == 88
        assert layout.address_expression("rbp", [2, 3]) == "[rbp+88]"

    elif case_name == "array_load_emit":
        gen = ArrayGenerator()
        layout = gen.declare_static_array("arr", "int", [5])
        assert gen.emit_load(layout, "rbp", [2], "rax") == "mov rax, qword [rbp+16]"

    elif case_name == "array_store_emit":
        gen = ArrayGenerator()
        layout = gen.declare_static_array("arr", "int", [5])
        assert gen.emit_store(layout, "rbp", [1], "rbx") == "mov qword [rbp+8], rbx"

    elif case_name == "extern_printf_variadic":
        registry = default_registry()
        fn = registry.validate_call("printf", ["string", "int", "int"])
        assert fn.name == "printf"
        assert fn.variadic is True

    elif case_name == "extern_strlen":
        registry = default_registry()
        fn = registry.validate_call("strlen", ["string"])
        assert fn.return_type == "int"

    elif case_name == "optimizer_constant_propagation":
        program = IRProgram()
        fn = IRFunction("main", "int", [])
        block = fn.new_block("entry")
        block.add(IRInstruction("STORE", args=["x", "5"]))
        block.add(IRInstruction("LOAD", dest="t1", args=["x"]))
        block.add(IRInstruction("ADD", dest="t2", args=["t1", "0"]))
        block.add(IRInstruction("RETURN", args=["t2"]))
        program.add_function(fn)

        optimized = Sprint7Optimizer().optimize(program).dump()

        assert "t1 = MOVE 5" in optimized
        assert "t2 = MOVE t1" in optimized


@pytest.mark.parametrize("case_name", INVALID_CASES)
def test_sprint7_invalid_cases(case_name):
    if case_name == "array_zero_size":
        with pytest.raises(ArrayLayoutError):
            ArrayLayout("arr", "int", [0])

    elif case_name == "array_negative_size":
        with pytest.raises(ArrayLayoutError):
            ArrayLayout("arr", "int", [-3])

    elif case_name == "array_wrong_index_count":
        layout = ArrayLayout("matrix", "int", [3, 4])
        with pytest.raises(ArrayLayoutError):
            layout.byte_offset([1])

    elif case_name == "array_index_out_of_bounds":
        layout = ArrayLayout("arr", "int", [5])
        with pytest.raises(ArrayLayoutError):
            layout.byte_offset([5])

    elif case_name == "extern_unknown_function":
        registry = default_registry()
        with pytest.raises(ExternalCallError):
            registry.validate_call("unknown", [])

    elif case_name == "extern_wrong_argument_count":
        registry = default_registry()
        with pytest.raises(ExternalCallError):
            registry.validate_call("puts", [])

    elif case_name == "extern_wrong_argument_type":
        registry = default_registry()
        with pytest.raises(ExternalCallError):
            registry.validate_call("strlen", ["int"])


def test_external_registry_rejects_duplicate_registration():
    registry = ExternalFunctionRegistry()
    registry.register(ExternalFunction("puts", "int", ["string"]))

    with pytest.raises(ExternalCallError):
        registry.register(ExternalFunction("puts", "int", ["string"]))


def test_array_bounds_check_comment():
    gen = ArrayGenerator()
    layout = gen.declare_static_array("arr", "int", [4])

    assert gen.emit_bounds_check_comment(layout, [3]) == "; bounds check ok for arr[3]"


def test_sprint7_optimizer_keeps_function_structure():
    program = IRProgram()
    fn = IRFunction("main", "int", [])
    block = fn.new_block("entry")
    block.add(IRInstruction("STORE", args=["x", "1"]))
    block.add(IRInstruction("LOAD", dest="t1", args=["x"]))
    block.add(IRInstruction("RETURN", args=["t1"]))
    program.add_function(fn)

    optimized = Sprint7Optimizer().optimize(program)

    assert list(optimized.functions.keys()) == ["main"]
    assert len(optimized.get_function("main").blocks) == 1
