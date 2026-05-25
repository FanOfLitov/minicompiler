from pathlib import Path

import pytest

from src.lexer.scanner import Scanner
from src.parser.parser import Parser
from src.semantic.analyzer import SemanticAnalyzer
from src.ir.ir_generator import IRGenerator
from src.optimizer.optimizer import IROptimizer


BASE_DIR = Path(__file__).parent
VALID_DIR = BASE_DIR / "valid"
INVALID_DIR = BASE_DIR / "invalid"


# Тесты добавляются вручную. Автоматический glob не используется.
VALID_OPTIMIZER_CASES = [
    "01_constant_add.src",
    "02_constant_sub.src",
    "03_constant_mul.src",
    "04_constant_div_not_folded.src",
    "05_variable_expression_not_folded.src",
    "06_dead_code_after_return.src",
    "07_dead_code_after_jump.src",
]

INVALID_OPTIMIZER_CASES = [
    "01_semantic_type_error.src",
    "02_undeclared_variable.src",
    "03_bad_return_type.src",
    "04_wrong_argument_count.src",
    "05_wrong_argument_type.src",
    "06_invalid_condition_type.src",
    "07_duplicate_variable.src",
]


def _build_ast(source: str, filename: str):
    scanner = Scanner(source, filename=filename)
    tokens = scanner.scan_tokens() if hasattr(scanner, "scan_tokens") else scanner.scan_all()

    assert scanner.errors == [], "Lexer errors before optimizer test:\n" + "\n".join(map(str, scanner.errors))

    parser = Parser(tokens)
    ast = parser.parse()

    assert ast is not None, "Parser returned None before optimizer test"
    assert parser.errors == [], "Parser errors before optimizer test:\n" + "\n".join(map(str, parser.errors))

    return ast


def _generate_optimized_ir(src_path: Path) -> str:
    source = src_path.read_text(encoding="utf-8")
    ast = _build_ast(source, str(src_path))

    analyzer = SemanticAnalyzer(filename=src_path.name, source=source)
    ok = analyzer.analyze(ast)

    assert ok is True, analyzer.format_errors()

    ir = IRGenerator().generate(ast)
    optimized = IROptimizer().optimize(ir)

    return optimized.dump()


def _run_frontend_for_invalid_case(src_path: Path):
    source = src_path.read_text(encoding="utf-8")
    ast = _build_ast(source, str(src_path))

    analyzer = SemanticAnalyzer(filename=src_path.name, source=source)
    ok = analyzer.analyze(ast)

    return analyzer, ok


def _compact_errors(analyzer) -> str:
    lines = []

    for err in analyzer.errors:
        lines.append(
            "semantic error at {}:{}:{}: {}".format(
                err.filename,
                err.line,
                err.column,
                err.message,
            )
        )

        if err.hint:
            lines.append("  note: {}".format(err.hint))

    return "\n".join(lines)


@pytest.mark.parametrize("case_name", VALID_OPTIMIZER_CASES)
def test_optimizer_valid_cases_match_expected(case_name: str):
    src_path = VALID_DIR / case_name
    expected_path = src_path.with_suffix(".expected")

    assert src_path.exists(), "Missing optimizer valid source: {}".format(src_path)
    assert expected_path.exists(), "Missing optimizer expected file: {}".format(expected_path)

    actual = _generate_optimized_ir(src_path).strip()
    expected = expected_path.read_text(encoding="utf-8").strip()

    assert actual == expected


@pytest.mark.parametrize("case_name", INVALID_OPTIMIZER_CASES)
def test_optimizer_invalid_cases_stop_before_optimization(case_name: str):
    src_path = INVALID_DIR / case_name
    expected_path = src_path.with_suffix(".expected")

    assert src_path.exists(), "Missing optimizer invalid source: {}".format(src_path)
    assert expected_path.exists(), "Missing optimizer expected file: {}".format(expected_path)

    analyzer, ok = _run_frontend_for_invalid_case(src_path)
    actual = _compact_errors(analyzer)
    expected = expected_path.read_text(encoding="utf-8").strip()

    assert ok is False
    assert analyzer.has_errors
    assert expected in actual


def test_optimizer_does_not_change_function_count():
    src_path = VALID_DIR / "01_constant_add.src"
    source = src_path.read_text(encoding="utf-8")
    ast = _build_ast(source, str(src_path))

    analyzer = SemanticAnalyzer(filename=src_path.name, source=source)
    assert analyzer.analyze(ast), analyzer.format_errors()

    ir = IRGenerator().generate(ast)
    before = len(ir.functions)

    optimized = IROptimizer().optimize(ir)
    after = len(optimized.functions)

    assert before == after == 1
