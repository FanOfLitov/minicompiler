"""
Pytest tests for Sprint 2 parser.
These tests DO NOT generate fixtures. They only read existing files from:
  tests/parser/valid/*.src + matching *.expected
  tests/parser/invalid/*.src + matching *.expected
"""
from pathlib import Path
import pytest

from src.lexer.scanner import Scanner
from src.parser.parser import Parser
from src.parser.ast_printer import TextPrinter

ROOT = Path(__file__).resolve().parents[2]
PARSER_DIR = ROOT / "tests" / "parser"
VALID_DIR = PARSER_DIR / "valid"
INVALID_DIR = PARSER_DIR / "invalid"


def _scan(source: str, filename: str):
    scanner = Scanner(source, filename=filename)
    tokens = scanner.scan_tokens() if hasattr(scanner, "scan_tokens") else scanner.scan_all()
    assert scanner.errors == [], "Lexer errors before parser:\n" + "\n".join(map(str, scanner.errors))
    return tokens


def _parse(source: str, filename: str):
    tokens = _scan(source, filename)
    parser = Parser(tokens)
    ast = parser.parse()
    return parser, ast


def _normalise(text: str) -> str:
    return "\n".join(line.rstrip() for line in text.strip().splitlines())


def _parser_errors_text(parser: Parser) -> str:
    return "\n".join(str(e) for e in parser.errors)


valid_cases = sorted(VALID_DIR.glob("*.src"))
invalid_cases = sorted(INVALID_DIR.glob("*.src"))


@pytest.mark.parametrize("src_path", valid_cases, ids=lambda p: p.name)
def test_valid_parser_cases_match_expected_ast(src_path: Path):
    expected_path = src_path.with_suffix(".expected")
    assert expected_path.exists(), f"Missing expected file: {expected_path}"

    source = src_path.read_text(encoding="utf-8")
    expected = expected_path.read_text(encoding="utf-8")

    parser, ast = _parse(source, str(src_path))

    assert ast is not None, "Parser returned None for valid file"
    assert parser.errors == [], "Valid parser case produced errors:\n" + _parser_errors_text(parser)

    actual = TextPrinter().print(ast)
    assert _normalise(actual) == _normalise(expected)


@pytest.mark.parametrize("src_path", invalid_cases, ids=lambda p: p.name)
def test_invalid_parser_cases_match_expected_errors(src_path: Path):
    expected_path = src_path.with_suffix(".expected")
    assert expected_path.exists(), f"Missing expected file: {expected_path}"

    source = src_path.read_text(encoding="utf-8")
    expected = expected_path.read_text(encoding="utf-8")

    parser, ast = _parse(source, str(src_path))
    actual = _parser_errors_text(parser)

    assert parser.errors, "Invalid parser case did not produce parser errors"

    # Exact match first. If your .expected contains only the key message,
    # substring match also works.
    expected_norm = _normalise(expected)
    actual_norm = _normalise(actual)
    assert actual_norm == expected_norm or expected_norm in actual_norm
