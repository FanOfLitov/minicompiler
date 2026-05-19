"""
Pytest tests for Sprint 3 semantic analyzer.
These tests DO NOT generate fixtures. They only read existing files from:
  tests/semantic/valid/*.src
  tests/semantic/invalid/*.src + matching *.expected
"""
from pathlib import Path
import pytest

from src.lexer.scanner import Scanner
from src.parser.parser import Parser
from src.semantic.analyzer import SemanticAnalyzer

ROOT = Path(__file__).resolve().parents[2]
SEMANTIC_DIR = ROOT / "tests" / "semantic"
VALID_DIR = SEMANTIC_DIR / "valid"
INVALID_DIR = SEMANTIC_DIR / "invalid"


def _normalise(text: str) -> str:
    return "\n".join(line.rstrip() for line in text.strip().splitlines())

def _compact_semantic_errors(analyzer) -> str:
    lines = []
    for err in analyzer.errors:
        filename = Path(err.filename).name
        line = f"semantic error at {filename}:{err.line}:{err.column}: {err.message}"
        lines.append(line)
        if getattr(err, "hint", ""):
            lines.append(f"  note: {err.hint}")
    return "\n".join(lines)


def _build_ast(source: str, filename: str):
    scanner = Scanner(source, filename=filename)
    tokens = scanner.scan_tokens() if hasattr(scanner, "scan_tokens") else scanner.scan_all()
    assert scanner.errors == [], "Lexer errors before semantic analysis:\n" + "\n".join(map(str, scanner.errors))

    parser = Parser(tokens)
    ast = parser.parse()
    assert ast is not None, "Parser returned None before semantic analysis"
    assert parser.errors == [], "Parser errors before semantic analysis:\n" + "\n".join(map(str, parser.errors))
    return ast


def _analyze_file(src_path: Path):
    source = src_path.read_text(encoding="utf-8")
    ast = _build_ast(source, str(src_path))
    analyzer = SemanticAnalyzer(filename=str(src_path), source=source)
    ok = analyzer.analyze(ast)
    return analyzer, ok


valid_cases = sorted(VALID_DIR.glob("*.src"))
invalid_cases = sorted(INVALID_DIR.glob("*.src"))


@pytest.mark.parametrize("src_path", valid_cases, ids=lambda p: p.name)
def test_valid_semantic_cases_have_no_errors(src_path: Path):
    analyzer, ok = _analyze_file(src_path)

    assert ok is True
    assert not analyzer.has_errors, "Valid semantic case produced errors:\n" + analyzer.format_errors()


@pytest.mark.parametrize("src_path", invalid_cases, ids=lambda p: p.name)
def test_invalid_semantic_cases_match_expected_errors(src_path: Path):
    expected_path = src_path.with_suffix(".expected")
    if not expected_path.exists():
        pytest.skip(f"Missing expected file: {expected_path}")

    analyzer, ok = _analyze_file(src_path)
    actual = _compact_semantic_errors(analyzer)
    expected = expected_path.read_text(encoding="utf-8")

    assert ok is False
    assert analyzer.has_errors, "Invalid semantic case did not produce semantic errors"

    # Exact match first. If your .expected contains only the key message,
    # substring match also works.
    expected_norm = _normalise(expected)
    actual_norm = _normalise(actual)
    assert actual_norm == expected_norm or expected_norm in actual_norm
