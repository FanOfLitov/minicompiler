from pathlib import Path

import pytest

from src.lexer.scanner import Scanner
from src.parser.parser import Parser
from src.semantic.analyzer import SemanticAnalyzer
from src.ir.ir_generator import IRGenerator
from src.ir.control_flow import function_to_dot


IR_DIR = Path(__file__).parent
VALID_DIR = IR_DIR / "valid"
INVALID_DIR = IR_DIR / "invalid"


# ВАЖНО:
# Тестовые случаи добавляются вручную.
# Мы специально НЕ используем glob("*.src"), чтобы преподаватель видел,
# какие именно тесты входят в Sprint 4.
VALID_IR_CASES = [
    "arithmetic_ir.src",
    "function_call_ir.src",
    "if_else_ir.src",
    "while_ir.src",
]

INVALID_IR_CASES = [
    "invalid_assignment_ir.src",
    "unsupported_construct.src",
]


def _scan(source: str, filename: str):
    scanner = Scanner(source, filename=filename)
    tokens = scanner.scan_tokens() if hasattr(scanner, "scan_tokens") else scanner.scan_all()

    assert scanner.errors == [], "Lexer errors:\n" + "\n".join(map(str, scanner.errors))
    return tokens


def _parse(source: str, filename: str):
    tokens = _scan(source, filename)

    parser = Parser(tokens)
    ast = parser.parse()

    assert ast is not None, "Parser returned None"
    assert parser.errors == [], "Parser errors:\n" + "\n".join(map(str, parser.errors))
    return ast


def _semantic_ok(source: str, filename: str):
    ast = _parse(source, filename)

    analyzer = SemanticAnalyzer(filename=Path(filename).name, source=source)
    ok = analyzer.analyze(ast)

    assert ok is True, analyzer.format_errors()
    assert analyzer.has_errors is False

    return ast


def _semantic_invalid(source: str, filename: str):
    ast = _parse(source, filename)

    analyzer = SemanticAnalyzer(filename=Path(filename).name, source=source)
    ok = analyzer.analyze(ast)

    assert ok is False or analyzer.has_errors
    return analyzer


def _generate_ir_from_file(src_path: Path):
    source = src_path.read_text(encoding="utf-8")
    ast = _semantic_ok(source, str(src_path))

    generator = IRGenerator()
    program = generator.generate(ast)

    return program.dump(), program


@pytest.mark.parametrize("case_name", VALID_IR_CASES)
def test_ir_valid_cases_match_expected(case_name: str):
    src_path = VALID_DIR / case_name
    expected_path = src_path.with_suffix(".expected")

    assert src_path.exists(), "Missing source file: {}".format(src_path)
    assert expected_path.exists(), "Missing expected IR file: {}".format(expected_path)

    actual, _program = _generate_ir_from_file(src_path)
    expected = expected_path.read_text(encoding="utf-8").strip()

    assert actual.strip() == expected


@pytest.mark.parametrize("case_name", INVALID_IR_CASES)
def test_ir_invalid_cases_stop_before_ir_generation(case_name: str):
    src_path = INVALID_DIR / case_name

    assert src_path.exists(), "Missing invalid source file: {}".format(src_path)

    source = src_path.read_text(encoding="utf-8")
    analyzer = _semantic_invalid(source, str(src_path))

    # IR generator must not be started for semantically invalid programs.
    assert analyzer.has_errors


def test_ir_cfg_dot_for_if_else_contains_basic_blocks():
    src_path = VALID_DIR / "if_else_ir.src"

    _actual, program = _generate_ir_from_file(src_path)
    function_ir = program.get_function("main")

    dot = function_to_dot(function_ir)

    assert "digraph" in dot
    assert "entry" in dot
    assert "else" in dot
    assert "endif" in dot
    assert "JUMP_IF_NOT" in dot


def test_ir_arithmetic_contains_three_address_operations():
    src_path = VALID_DIR / "arithmetic_ir.src"

    actual, _program = _generate_ir_from_file(src_path)

    assert "MUL" in actual
    assert "ADD" in actual
    assert "STORE x" in actual
    assert "RETURN" in actual


def test_ir_empty_program_is_allowed_and_generates_empty_ir():
    # Пустая программа не является ошибкой frontend.
    # Для IR это edge-case: генератор должен вернуть пустой IR.
    src_path = INVALID_DIR / "empty_program.src"

    assert src_path.exists(), "Missing edge source file: {}".format(src_path)

    source = src_path.read_text(encoding="utf-8")
    ast = _semantic_ok(source, str(src_path))

    generator = IRGenerator()
    program = generator.generate(ast)

    assert program.dump() == ""


def test_ir_infinite_while_program_generates_cfg_without_crash():
    # Это не invalid-кейс. while(true) может быть бесконечным,
    # но синтаксически и семантически программа корректна.
    src_path = INVALID_DIR / "malformed_cfg.src"

    assert src_path.exists(), "Missing edge source file: {}".format(src_path)

    actual, program = _generate_ir_from_file(src_path)

    assert "while" in actual
    assert "JUMP" in actual

    function_ir = program.get_function("main")
    dot = function_to_dot(function_ir)

    assert "digraph" in dot
    assert "while" in dot
