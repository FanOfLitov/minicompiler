from pathlib import Path

import pytest

from src.lexer.scanner import Scanner
from src.parser.parser import Parser
from src.semantic.analyzer import SemanticAnalyzer
from src.ir.ir_generator import IRGenerator
from src.ssa.ssa_builder import SSABuilder


VALID_DIR = Path(__file__).parent / "valid"

VALID_SSA_CASES = [
    "01_assignment_versions.src",
    "02_arithmetic.src",
    "03_function_call.src",
    "04_return_constant.src",
    "05_multiple_variables.src",
    "06_if_shape.src",
    "07_while_shape.src",
]


def _build_ssa(src_path: Path) -> str:
    source = src_path.read_text(encoding="utf-8")

    scanner = Scanner(source, filename=str(src_path))
    tokens = scanner.scan_tokens() if hasattr(scanner, "scan_tokens") else scanner.scan_all()
    assert scanner.errors == [], "\n".join(map(str, scanner.errors))

    parser = Parser(tokens)
    ast = parser.parse()
    assert ast is not None
    assert parser.errors == [], "\n".join(map(str, parser.errors))

    analyzer = SemanticAnalyzer(filename=src_path.name, source=source)
    assert analyzer.analyze(ast), analyzer.format_errors()

    ir = IRGenerator().generate(ast)
    ssa = SSABuilder().build(ir)
    return ssa.dump()


@pytest.mark.parametrize("case_name", VALID_SSA_CASES)
def test_ssa_cases_match_expected(case_name):
    src = VALID_DIR / case_name
    expected_path = src.with_suffix(".expected")

    assert src.exists(), "Missing SSA source: {}".format(src)
    assert expected_path.exists(), "Missing SSA expected: {}".format(expected_path)

    actual = _build_ssa(src).strip()
    expected = expected_path.read_text(encoding="utf-8").strip()

    assert actual == expected


def test_ssa_header_is_visible():
    actual = _build_ssa(VALID_DIR / "02_arithmetic.src")
    assert "ssa function main" in actual


def test_ssa_versions_are_visible():
    actual = _build_ssa(VALID_DIR / "01_assignment_versions.src")
    assert "x.1" in actual
    assert "x.2" in actual
