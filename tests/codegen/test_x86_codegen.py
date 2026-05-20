from pathlib import Path

import pytest

from src.lexer.scanner import Scanner
from src.parser.parser import Parser
from src.semantic.analyzer import SemanticAnalyzer
from src.ir.ir_generator import IRGenerator
from src.codegen.x86_generator import X86Generator


CODEGEN_DIR = Path(__file__).parent
VALID_DIR = CODEGEN_DIR / "valid"


# Manual test list. Do not replace with glob().
VALID_CODEGEN_CASES = [
    "return_constant.src",
    "arithmetic_stack.src",
    "function_call.src",
    "if_else.src",
    "while_loop.src",
]


def _build_ast(source: str, filename: str):
    scanner = Scanner(source, filename=filename)
    tokens = scanner.scan_tokens() if hasattr(scanner, "scan_tokens") else scanner.scan_all()

    assert scanner.errors == [], "Lexer errors:\n" + "\n".join(map(str, scanner.errors))

    parser = Parser(tokens)
    ast = parser.parse()

    assert ast is not None, "Parser returned None"
    assert parser.errors == [], "Parser errors:\n" + "\n".join(map(str, parser.errors))

    analyzer = SemanticAnalyzer(filename=Path(filename).name, source=source)
    ok = analyzer.analyze(ast)

    assert ok is True, analyzer.format_errors()

    return ast


def _generate_asm(src_path: Path) -> str:
    source = src_path.read_text(encoding="utf-8")
    ast = _build_ast(source, str(src_path))

    ir_program = IRGenerator().generate(ast)
    asm = X86Generator().generate(ir_program)

    return asm


@pytest.mark.parametrize("case_name", VALID_CODEGEN_CASES)
def test_codegen_valid_cases_match_expected(case_name: str):
    src_path = VALID_DIR / case_name
    expected_path = src_path.with_suffix(".expected")

    assert src_path.exists(), "Missing source file: {}".format(src_path)
    assert expected_path.exists(), "Missing expected assembly file: {}".format(expected_path)

    actual = _generate_asm(src_path).strip()
    expected = expected_path.read_text(encoding="utf-8").strip()

    assert actual == expected


def test_function_prologue_and_epilogue_are_generated():
    asm = _generate_asm(VALID_DIR / "return_constant.src")

    assert "main:" in asm
    assert "push rbp" in asm
    assert "mov rbp, rsp" in asm
    assert "mov rsp, rbp" in asm
    assert "pop rbp" in asm
    assert "ret" in asm


def test_arithmetic_uses_x86_integer_instructions():
    asm = _generate_asm(VALID_DIR / "arithmetic_stack.src")

    assert "imul rax, rbx" in asm
    assert "add rax, rbx" in asm
    assert "mov qword [rbp" in asm


def test_call_uses_system_v_argument_registers():
    asm = _generate_asm(VALID_DIR / "function_call.src")

    assert "mov rdi, 2" in asm
    assert "mov rsi, 3" in asm
    assert "call add" in asm
