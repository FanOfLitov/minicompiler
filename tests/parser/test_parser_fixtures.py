"""
Golden-file parser tests.

Valid fixtures:
    tests/parser/valid/*.src
        -> parsed successfully
        -> AST printed by TextPrinter()
        -> compared with .expected

Invalid fixtures:
    tests/parser/invalid/*.src
        -> parser must produce diagnostics
        -> joined diagnostics compared with .expected
"""
from pathlib import Path
import pytest

from src.lexer.scanner import Scanner
from src.parser.parser import Parser
from src.parser.ast_printer import TextPrinter


BASE_DIR = Path(__file__).resolve().parent
VALID_DIR = BASE_DIR / "valid"
INVALID_DIR = BASE_DIR / "invalid"


def normalize_text(text: str) -> str:
    return text.replace("\r\n", "\n").strip()


def parse_file(src_file: Path):
    source = src_file.read_text(encoding="utf-8")
    scanner = Scanner(source, filename=src_file.name)
    tokens = scanner.scan_all()
    parser = Parser(tokens)
    program = parser.parse()
    return source, program, parser.errors


VALID_CASES = sorted(VALID_DIR.glob("*.src"))
INVALID_CASES = sorted(INVALID_DIR.glob("*.src"))


@pytest.mark.parametrize("src_file", VALID_CASES, ids=lambda p: p.stem)
def test_parser_valid_matches_expected(src_file: Path):
    expected_file = src_file.with_suffix(".expected")
    assert expected_file.exists(), f"Missing expected file: {expected_file}"

    _, program, errors = parse_file(src_file)

    assert program is not None, (
        f"Parser returned None for valid file {src_file.name}. "
        f"Errors: {[str(e) for e in errors]}"
    )
    assert len(errors) == 0, (
        f"Expected no parse errors for {src_file.name}, "
        f"but got: {[str(e) for e in errors]}"
    )

    actual = TextPrinter().print(program)
    expected = expected_file.read_text(encoding="utf-8")

    assert normalize_text(actual) == normalize_text(expected)


@pytest.mark.parametrize("src_file", INVALID_CASES, ids=lambda p: p.stem)
def test_parser_invalid_matches_expected(src_file: Path):
    expected_file = src_file.with_suffix(".expected")
    assert expected_file.exists(), f"Missing expected file: {expected_file}"

    _, program, errors = parse_file(src_file)

    assert len(errors) > 0, (
        f"Expected parse errors for invalid file {src_file.name}, "
        f"but parser reported none."
    )

    actual = "\n".join(str(e) for e in errors)
    expected = expected_file.read_text(encoding="utf-8")

    assert normalize_text(actual) == normalize_text(expected)